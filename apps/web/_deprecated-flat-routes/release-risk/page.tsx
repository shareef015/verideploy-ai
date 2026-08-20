"use client";

import { FormEvent, useState } from "react";

type Assessment = {
  assessment_id: string;
  status: string;
  repository: string;
  release_id: string;
  result?: { score: number; level: string; decision: string; confidence: number; requires_human_review: boolean; primary_risks: string[]; recommended_actions: string[] };
};

const gateway = process.env.NEXT_PUBLIC_GATEWAY_URL ?? "http://localhost:4000";

export default function ReleaseRiskPage() {
  const [result, setResult] = useState<Assessment | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setLoading(true); setError("");
    const data = new FormData(event.currentTarget);
    const payload = {
      repository: String(data.get("repository")), release_id: String(data.get("release_id")), commit_sha: String(data.get("commit_sha")), target_environment: "production",
      policy: { changed_files: Number(data.get("changed_files")), changed_services: Number(data.get("changed_services")), failed_workflows: Number(data.get("failed_workflows")), database_migration_changed: data.get("database_migration_changed") === "on", rollback_plan_verified: data.get("rollback_plan_verified") === "on", security_scan_critical_findings: Number(data.get("security_scan_critical_findings")) },
    };
    try {
      const response = await fetch(`${gateway}/api/v1/releases/risk-assessments`, { method: "POST", headers: { "content-type": "application/json", "x-tenant-id": "11111111-1111-4111-8111-111111111111", "x-user-id": "22222222-2222-4222-8222-222222222222", "idempotency-key": crypto.randomUUID() }, body: JSON.stringify(payload) });
      if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
      const queued = await response.json();
      setResult(queued);
      for (let attempt = 0; attempt < 20; attempt += 1) {
        await new Promise((resolve) => setTimeout(resolve, 750));
        const statusResponse = await fetch(`${gateway}/api/v1/releases/risk-assessments/${queued.assessment_id}`, { headers: { "x-tenant-id": "11111111-1111-4111-8111-111111111111" } });
        if (statusResponse.status === 404) continue;
        if (!statusResponse.ok) throw new Error(`Status request failed with ${statusResponse.status}`);
        const current = await statusResponse.json();
        setResult(current);
        if (["COMPLETED", "FAILED", "CANCELLED"].includes(current.status)) break;
      }
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Release risk request failed"); }
    finally { setLoading(false); }
  }

  return <main className="page"><section className="hero"><p className="eyebrow">Release Assurance</p><h1>Release Risk</h1><p>Submit release evidence signals to the auditable release-risk policy engine.</p></section><div className="grid"><form className="card form" onSubmit={submit}><label>Repository<input name="repository" required defaultValue="nexuspay/payment-service" /></label><label>Release ID<input name="release_id" required defaultValue="v4.8.2" /></label><label>Commit SHA<input name="commit_sha" required defaultValue="a1b2c3d4e5f6a7b8" /></label><label>Changed files<input name="changed_files" type="number" min="0" required defaultValue="84" /></label><label>Changed services<input name="changed_services" type="number" min="0" required defaultValue="2" /></label><label>Failed workflows<input name="failed_workflows" type="number" min="0" defaultValue="1" /></label><label>Critical security findings<input name="security_scan_critical_findings" type="number" min="0" defaultValue="0" /></label><label className="check"><input name="database_migration_changed" type="checkbox" /> Database migration changed</label><label className="check"><input name="rollback_plan_verified" type="checkbox" defaultChecked /> Rollback plan verified</label><button disabled={loading}>{loading ? "Assessing…" : "Assess release"}</button>{error && <p className="error">{error}</p>}</form><section className="card result" aria-live="polite">{!result && <p>No assessment submitted.</p>}{result && <><p className="eyebrow">{result.status}</p><h2>{result.release_id}</h2>{result.result && <><div className="score">{result.result.score}<small>/100</small></div><p><strong>{result.result.level}</strong> · {result.result.decision}</p><p>Calibrated policy confidence: {(result.result.confidence * 100).toFixed(0)}%</p><p>Human review: {result.result.requires_human_review ? "required" : "not required"}</p><h3>Primary risks</h3><ul>{result.result.primary_risks.map((item) => <li key={item}>{item}</li>)}</ul><h3>Recommended actions</h3><ul>{result.result.recommended_actions.map((item) => <li key={item}>{item}</li>)}</ul></>}</>}</section></div></main>;
}
