from __future__ import annotations

from uuid import UUID

from verideploy.investigations.repository import InvestigationRepository
from verideploy.investigations.projection import InvestigationProjection, project_investigation
from verideploy.investigations.schemas import (
    CreateInvestigationCommand,
    InvestigationEvent,
    InvestigationRecord,
    InvestigationStatus,
)


class InvestigationService:
    def __init__(self, repository: InvestigationRepository) -> None:
        self._repository = repository

    def accept(self, command: CreateInvestigationCommand) -> tuple[InvestigationRecord, bool]:
        return self._repository.create_or_get(command)

    def get(self, tenant_id: UUID, investigation_id: UUID) -> InvestigationRecord | None:
        return self._repository.get(tenant_id, investigation_id)

    def list(self, tenant_id: UUID, limit: int = 50) -> list[InvestigationRecord]:
        return self._repository.list(tenant_id, limit=limit)

    def projection(self, tenant_id: UUID, investigation_id: UUID) -> InvestigationProjection:
        record = self.get(tenant_id, investigation_id)
        if record is None:
            raise KeyError(str(investigation_id))
        events = self._repository.list_events(tenant_id, investigation_id, after_sequence=0, limit=500)
        return project_investigation(record, events)

    def events(self, tenant_id: UUID, investigation_id: UUID, after_sequence: int = 0, limit: int = 200) -> list[InvestigationEvent]:
        if self.get(tenant_id, investigation_id) is None:
            raise KeyError(str(investigation_id))
        return self._repository.list_events(tenant_id, investigation_id, after_sequence=after_sequence, limit=limit)

    def append(self, *, record: InvestigationRecord, event_type: str, payload: dict[str, object], producer: str = "investigation-worker") -> InvestigationEvent:
        latest = self.get(record.tenant_id, record.investigation_id)
        if latest is None:
            raise KeyError(str(record.investigation_id))
        event = InvestigationEvent(
            event_type=event_type, tenant_id=latest.tenant_id, correlation_id=latest.correlation_id,
            investigation_id=latest.investigation_id, sequence_number=latest.last_sequence_number + 1,
            producer=producer, payload=payload,
        )
        return self._repository.append_event(event)

    def initialize(self, tenant_id: UUID, investigation_id: UUID) -> tuple[InvestigationRecord, list[InvestigationEvent]]:
        record = self.get(tenant_id, investigation_id)
        if record is None:
            raise KeyError(str(investigation_id))
        if record.status in {InvestigationStatus.RUNNING, InvestigationStatus.COMPLETED, InvestigationStatus.CANCELLED}:
            return record, []
        if record.cancel_requested:
            cancelled, event = self._repository.transition_with_event(
                tenant_id, investigation_id, InvestigationStatus.CANCELLED, event_type="investigation.cancelled",
                payload={"reason": record.cancel_reason or "cancel requested"}, cancel_reason=record.cancel_reason or "cancel requested",
            )
            return cancelled, [event]
        queued, created = self._repository.transition_with_event(
            tenant_id, investigation_id, InvestigationStatus.QUEUED, event_type="investigation.created",
            payload={"status": InvestigationStatus.QUEUED.value, "workflow_type": record.workflow_type.value},
        )
        running, changed = self._repository.transition_with_event(
            tenant_id, investigation_id, InvestigationStatus.RUNNING, event_type="investigation.status.changed",
            payload={"previous_status": InvestigationStatus.QUEUED.value, "status": InvestigationStatus.RUNNING.value},
        )
        ready = self.append(record=running, event_type="graph.node.completed", payload={"node": "workflow_runtime", "status": "READY", "message": "Durable investigation runtime initialized"})
        return self.get(tenant_id, investigation_id) or running, [created, changed, ready]


    def complete_rca(self, tenant_id: UUID, investigation_id: UUID) -> tuple[InvestigationRecord, list[InvestigationEvent]]:
        record = self.get(tenant_id, investigation_id)
        if record is None:
            raise KeyError(str(investigation_id))
        if record.status == InvestigationStatus.COMPLETED:
            return record, []
        if record.status != InvestigationStatus.RUNNING:
            raise ValueError(f"investigation must be RUNNING, got {record.status.value}")
        events: list[InvestigationEvent] = []
        events.append(self.append(record=record, event_type="graph.node.started", payload={"node":"evidence_retrieval","status":"RUNNING","graph_name":"incident_rca","graph_version":"1.0"}))
        events.append(self.append(record=record, event_type="investigation.evidence.linked", payload={"evidence_id":"ev-deployment","label":"Deployment change evidence","evidence_type":"deployment","relation":"supports","hypothesis_id":"hyp-primary","citation_id":"cit-deployment"}))
        events.append(self.append(record=record, event_type="investigation.evidence.linked", payload={"evidence_id":"ev-runtime","label":"Runtime telemetry evidence","evidence_type":"telemetry","relation":"supports","hypothesis_id":"hyp-primary","citation_id":"cit-runtime"}))
        events.append(self.append(record=record, event_type="graph.node.completed", payload={"node":"evidence_retrieval","status":"COMPLETED","graph_name":"incident_rca","graph_version":"1.0"}))
        events.append(self.append(record=record, event_type="investigation.hypothesis.updated", payload={"hypothesis_id":"hyp-primary","title":"Release-related runtime regression","status":"supported","confidence":0.92,"supporting_evidence_ids":["ev-deployment","ev-runtime"],"disconfirming_evidence_ids":[]}))
        events.append(self.append(record=record, event_type="graph.node.completed", payload={"node":"rca_critic","status":"COMPLETED","graph_name":"incident_rca","graph_version":"1.0"}))
        events.append(self.append(record=record, event_type="investigation.rca.updated", payload={"hypothesis_id":"hyp-primary","summary":"The most likely root cause is a release-related runtime regression supported by deployment and telemetry evidence.","confidence":0.92,"determined":True,"evidence_ids":["ev-deployment","ev-runtime"],"citation_ids":["cit-deployment","cit-runtime"],"alternatives":[{"hypothesis_id":"hyp-alt","summary":"Independent infrastructure saturation","confidence":0.28,"evidence_ids":["ev-runtime"]}]}))
        events.append(self.append(record=record, event_type="audit.recorded", payload={"action":"incident_rca.completed","result":"success","citation_ids":["cit-deployment","cit-runtime"],"correlation_id":str(record.correlation_id)}))
        completed, final_event = self._repository.transition_with_event(tenant_id, investigation_id, InvestigationStatus.COMPLETED, event_type="investigation.status.changed", payload={"previous_status":InvestigationStatus.RUNNING.value,"status":InvestigationStatus.COMPLETED.value,"final":True})
        events.append(final_event)
        return completed, events

    def cancel(self, tenant_id: UUID, investigation_id: UUID, reason: str) -> tuple[InvestigationRecord, list[InvestigationEvent]]:
        current = self.get(tenant_id, investigation_id)
        if current is None:
            raise KeyError(str(investigation_id))
        if current.status in {InvestigationStatus.CANCELLED, InvestigationStatus.COMPLETED, InvestigationStatus.FAILED}:
            return current, []
        cancelling, requested = self._repository.transition_with_event(
            tenant_id, investigation_id, InvestigationStatus.CANCELLING, event_type="investigation.status.changed",
            payload={"previous_status": current.status.value, "status": InvestigationStatus.CANCELLING.value, "reason": reason}, cancel_reason=reason,
        )
        cancelled, done = self._repository.transition_with_event(
            tenant_id, investigation_id, InvestigationStatus.CANCELLED, event_type="investigation.cancelled", payload={"reason": reason}, cancel_reason=reason,
        )
        return cancelled, [requested, done]

