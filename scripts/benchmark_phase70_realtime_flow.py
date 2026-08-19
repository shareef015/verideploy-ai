from __future__ import annotations
import json
from pathlib import Path
from verideploy.realtime.flow import reconcile_event_stream, validate_terminal_flow
ROOT=Path(__file__).resolve().parents[1]
release=["browser.command","nestjs.validation","kafka.command","worker.consume","langgraph.release_risk","persistence","kafka.event","redis.websocket","browser.reconcile"]
incident=["browser.command","nestjs.validation","kafka.command","worker.consume","langgraph.incident_rca","citations","audit","persistence","kafka.event","redis.websocket","browser.reconcile"]
r=reconcile_event_stream([{"sequence_number":n} for n in [4,1,2,2,5,3]],authoritative_high_watermark=5)
report={"phase":70,"passed":r.converged and not validate_terminal_flow(workflow="release_risk",stages=release,status="COMPLETED",citations=["cit-risk"],audit_events=1,ui_status="COMPLETED") and not validate_terminal_flow(workflow="incident_rca",stages=incident,status="COMPLETED",citations=["cit-deployment","cit-runtime"],audit_events=1,ui_status="COMPLETED"),"reconciliation":{"high_watermark":r.high_watermark,"duplicates":list(r.duplicate_sequences),"missing":list(r.missing_sequences),"converged":r.converged},"flows":{"release_risk":release,"incident_rca":incident},"assertions":["state","event_order","citations","audit","final_ui"]}
out=ROOT/'evals/reports/phase70-complete-realtime-api-flow.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report,indent=2));raise SystemExit(0 if report["passed"] else 1)
