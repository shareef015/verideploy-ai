"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

const gateway = process.env.NEXT_PUBLIC_GATEWAY_URL ?? "http://localhost:4000";
const tenantId = "11111111-1111-4111-8111-111111111111";
const userId = "22222222-2222-4222-8222-222222222222";

type Investigation = {
  investigation_id: string;
  correlation_id: string;
  query?: string;
  status: string;
  last_sequence_number?: number;
  cancel_requested?: boolean;
  cancel_reason?: string | null;
  updated_at?: string;
};

type InvestigationEvent = {
  event_id: string;
  event_type: string;
  investigation_id: string;
  sequence_number: number;
  occurred_at: string;
  payload: Record<string, unknown>;
};

export default function IncidentInvestigationPage() {
  const [record, setRecord] = useState<Investigation | null>(null);
  const [events, setEvents] = useState<InvestigationEvent[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const lastSequence = useRef(0);
  const abortRef = useRef<AbortController | null>(null);

  async function authoritativeSnapshot(investigationId: string, correlationId: string) {
    const response = await fetch(`${gateway}/api/v1/investigations/${investigationId}`, {
      headers: { "x-tenant-id": tenantId, "x-correlation-id": correlationId }, cache: "no-store",
    });
    if (response.status === 404) return null;
    if (!response.ok) throw new Error(`Snapshot failed with ${response.status}`);
    const current = await response.json() as Investigation;
    setRecord(current);
    return current;
  }

  function mergeEvents(incoming: InvestigationEvent[]) {
    setEvents((current) => {
      const byId = new Map(current.map((item) => [item.event_id, item]));
      for (const item of incoming) {
        byId.set(item.event_id, item);
        lastSequence.current = Math.max(lastSequence.current, item.sequence_number);
      }
      return [...byId.values()].sort((a, b) => a.sequence_number - b.sequence_number);
    });
  }

  async function replay(investigationId: string, correlationId: string) {
    const response = await fetch(`${gateway}/api/v1/investigations/${investigationId}/events?after_sequence=${lastSequence.current}`, {
      headers: { "x-tenant-id": tenantId, "x-correlation-id": correlationId }, cache: "no-store",
    });
    if (!response.ok) throw new Error(`Replay failed with ${response.status}`);
    mergeEvents(await response.json() as InvestigationEvent[]);
  }

  async function connectStream(investigationId: string, correlationId: string) {
    abortRef.current?.abort();
    const controller = new AbortController(); abortRef.current = controller;
    await replay(investigationId, correlationId);
    await authoritativeSnapshot(investigationId, correlationId);
    try {
      const response = await fetch(`${gateway}/api/v1/investigations/${investigationId}/stream`, {
        headers: { "x-tenant-id": tenantId, "x-correlation-id": correlationId, "last-event-id": String(lastSequence.current) },
        signal: controller.signal, cache: "no-store",
      });
      if (!response.ok || !response.body) throw new Error(`Live stream failed with ${response.status}`);
      const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = "";
      while (!controller.signal.aborted) {
        const { value, done } = await reader.read(); if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const frames = buffer.split("\n\n"); buffer = frames.pop() ?? "";
        for (const frame of frames) {
          const dataLine = frame.split("\n").find((line) => line.startsWith("data: "));
          if (!dataLine) continue;
          try {
            const parsed = JSON.parse(dataLine.slice(6));
            const candidates = Array.isArray(parsed) ? parsed : [parsed];
            const valid = candidates.filter((item): item is InvestigationEvent => Boolean(item?.event_id && Number.isInteger(item?.sequence_number)));
            if (valid.length) { mergeEvents(valid); await authoritativeSnapshot(investigationId, correlationId); }
          } catch { /* heartbeat or incomplete application event */ }
        }
      }
    } catch (caught) {
      if (!controller.signal.aborted) {
        setError(caught instanceof Error ? caught.message : "Live stream disconnected");
        await replay(investigationId, correlationId);
        await authoritativeSnapshot(investigationId, correlationId);
      }
    }
  }

  useEffect(() => () => abortRef.current?.abort(), []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(""); setEvents([]); lastSequence.current = 0;
    const form = new FormData(event.currentTarget);
    const correlationId = crypto.randomUUID();
    try {
      const response = await fetch(`${gateway}/api/v1/investigations`, {
        method: "POST",
        headers: { "content-type": "application/json", "x-tenant-id": tenantId, "x-user-id": userId, "x-correlation-id": correlationId, "idempotency-key": crypto.randomUUID() },
        body: JSON.stringify({ query: String(form.get("query")), incident_id: String(form.get("incident_id") || "") || undefined }),
      });
      if (!response.ok) throw new Error(`Create failed with ${response.status}`);
      const queued = await response.json() as Investigation; setRecord(queued);
      void connectStream(queued.investigation_id, correlationId);
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Investigation creation failed"); }
    finally { setBusy(false); }
  }

  async function cancel() {
    if (!record) return;
    const response = await fetch(`${gateway}/api/v1/investigations/${record.investigation_id}/cancel`, {
      method: "POST", headers: { "content-type":"application/json", "x-tenant-id":tenantId, "x-user-id":userId, "x-correlation-id":record.correlation_id },
      body: JSON.stringify({ reason: "Cancelled by incident investigator" }),
    });
    if (!response.ok) setError(`Cancellation failed with ${response.status}`);
  }

  return <main className="page">
    <section className="hero"><p className="eyebrow">Incident Intelligence</p><h1>Real-Time Incident Investigation</h1><p>Durable command processing, ordered event replay, reconnect reconciliation, and cancellation without frontend-simulated state.</p></section>
    <div className="grid">
      <form className="card form" onSubmit={submit}>
        <label>Incident ID<input name="incident_id" placeholder="INC-2026-0042" /></label>
        <label>Investigation question<textarea name="query" required minLength={10} rows={7} defaultValue="Why did checkout latency increase immediately after the latest production release?" /></label>
        <button disabled={busy}>{busy ? "Submitting…" : "Start investigation"}</button>
        {record && !["CANCELLED","COMPLETED","FAILED"].includes(record.status) && <button type="button" onClick={cancel}>Cancel investigation</button>}
        {error && <p className="error">{error}</p>}
      </form>
      <section className="card result" aria-live="polite">
        {!record && <p>No investigation active.</p>}
        {record && <><p className="eyebrow">{record.status}</p><h2>{record.investigation_id}</h2><p>Correlation: <code>{record.correlation_id}</code></p><p>Authoritative sequence: {record.last_sequence_number ?? lastSequence.current}</p></>}
        <h3>Durable event timeline</h3>
        <ol>{events.map((item) => <li key={item.event_id}><strong>#{item.sequence_number} {item.event_type}</strong><br/><small>{new Date(item.occurred_at).toLocaleString()}</small></li>)}</ol>
      </section>
    </div>
  </main>;
}
