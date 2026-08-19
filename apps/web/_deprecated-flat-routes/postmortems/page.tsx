"use client";

import { FormEvent, useState } from "react";

const gateway = process.env.NEXT_PUBLIC_GATEWAY_URL ?? "http://localhost:4000";
const tenantId = "11111111-1111-4111-8111-111111111111";
const userId = "22222222-2222-4222-8222-222222222222";

type Postmortem = { postmortem_id: string; status: string; title?: string; root_cause?: string; impact?: string; version?: number; };

export default function PostmortemsPage() {
  const [record, setRecord] = useState<Postmortem | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError("");
    const form = new FormData(event.currentTarget); const correlationId = crypto.randomUUID();
    try {
      const reviewedEvidence = JSON.parse(String(form.get("reviewed_evidence")));
      const response = await fetch(`${gateway}/api/v1/postmortems`, {
        method: "POST",
        headers: { "content-type": "application/json", "x-tenant-id": tenantId, "x-user-id": userId, "x-correlation-id": correlationId, "idempotency-key": crypto.randomUUID() },
        body: JSON.stringify({ investigation_id: String(form.get("investigation_id")), title: String(form.get("title")), reviewed_evidence: reviewedEvidence }),
      });
      if (!response.ok) throw new Error(`Queue failed with ${response.status}`);
      const queued = await response.json() as Postmortem; setRecord(queued);
      for (let attempt = 0; attempt < 20; attempt += 1) {
        await new Promise((resolve) => setTimeout(resolve, 750));
        const current = await fetch(`${gateway}/api/v1/postmortems/${queued.postmortem_id}`, { headers: { "x-tenant-id": tenantId, "x-correlation-id": correlationId }, cache: "no-store" });
        if (current.status === 404) continue;
        if (!current.ok) throw new Error(`Status failed with ${current.status}`);
        setRecord(await current.json() as Postmortem); break;
      }
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Postmortem submission failed"); }
    finally { setBusy(false); }
  }

  return <main className="page">
    <section className="hero"><p className="eyebrow">Incident Learning</p><h1>Automated Postmortem</h1><p>Queues a postmortem only from a completed investigation and an explicitly reviewed evidence bundle.</p></section>
    <div className="grid">
      <form className="card form" onSubmit={submit}>
        <label>Completed investigation ID<input name="investigation_id" required /></label>
        <label>Postmortem title<input name="title" required minLength={5} /></label>
        <label>Reviewed evidence JSON<textarea name="reviewed_evidence" required rows={16} /></label>
        <button disabled={busy}>{busy ? "Submitting…" : "Generate postmortem"}</button>
        {error && <p className="error">{error}</p>}
      </form>
      <section className="card result" aria-live="polite">
        {!record && <p>No postmortem submitted.</p>}
        {record && <><p className="eyebrow">{record.status}</p><h2>{record.title ?? record.postmortem_id}</h2><p><code>{record.postmortem_id}</code></p>{record.root_cause && <><h3>Root cause</h3><p>{record.root_cause}</p></>}{record.impact && <><h3>Impact</h3><p>{record.impact}</p></>}</>}
      </section>
    </div>
  </main>;
}
