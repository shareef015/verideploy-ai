"use client";

import { useEffect, useMemo, useState } from "react";

const gateway = process.env.NEXT_PUBLIC_GATEWAY_URL ?? "http://localhost:4000";
const tenantId = "11111111-1111-4111-8111-111111111111";

type Team = { team_id:string; name:string; slug:string; mission:string };
type Owner = { owner_id:string; team_id:string; display_name:string; role:string; oncall_alias:string };
type Service = { service_id:string; team_id:string; name:string; slug:string; domain:string; tier:string; runtime:string; repository:string; description:string };
type Dependency = { dependency_id:string; source_service_id:string; target_service_id:string; kind:string; criticality:string; description:string };
type Environment = { environment_id:string; name:string; region:string; criticality:string };
type SLO = { slo_id:string; service_id:string; environment_id:string; metric:string; target:number; window_days:number };
type Deployment = { deployment_id:string; service_id:string; environment_id:string; version:string; commit_sha:string; cluster:string; namespace:string; replicas:number; deployed_at:string };
type Snapshot = { seed_version:string; seed_sha256:string; company:{name:string}; teams:Team[]; owners:Owner[]; services:Service[]; dependencies:Dependency[]; environments:Environment[]; slos:SLO[]; deployments:Deployment[] };

export default function TopologyPage(){
  const [data,setData]=useState<Snapshot|null>(null); const [error,setError]=useState("");
  useEffect(()=>{const controller=new AbortController(); void (async()=>{try{const response=await fetch(`${gateway}/api/v1/topology/nexuspay`,{headers:{"x-tenant-id":tenantId,"x-correlation-id":crypto.randomUUID()},cache:"no-store",signal:controller.signal}); if(!response.ok) throw new Error(`Topology request failed with ${response.status}`); setData(await response.json() as Snapshot);}catch(e){if(!controller.signal.aborted)setError(e instanceof Error?e.message:"Topology request failed");}})(); return()=>controller.abort();},[]);
  const teamById=useMemo(()=>new Map((data?.teams??[]).map(t=>[t.team_id,t])),[data]);
  const serviceById=useMemo(()=>new Map((data?.services??[]).map(s=>[s.service_id,s])),[data]);
  const ownerByTeam=useMemo(()=>new Map((data?.owners??[]).map(o=>[o.team_id,o])),[data]);
  const production=useMemo(()=>data?.environments.find(e=>e.name==="production"),[data]);
  if(error)return <main className="page"><section className="hero"><p className="eyebrow">NexusPay topology</p><h1>Topology unavailable</h1><p className="error">{error}</p></section></main>;
  if(!data)return <main className="page"><section className="hero"><p className="eyebrow">NexusPay topology</p><h1>Loading service graph…</h1></section></main>;
  return <main className="page topologyPage">
    <section className="hero"><p className="eyebrow">Synthetic company model · {data.seed_version}</p><h1>{data.company.name} Service Topology</h1><p>Stable ownership, dependencies, production SLOs, environments, and deployed versions. Seed <code>{data.seed_sha256.slice(0,12)}</code>.</p></section>
    <section className="topologyStats">
      <article><strong>{data.teams.length}</strong><span>Teams</span></article><article><strong>{data.services.length}</strong><span>Services</span></article><article><strong>{data.dependencies.length}</strong><span>Dependencies</span></article><article><strong>{data.deployments.length}</strong><span>Deployments</span></article>
    </section>
    <section className="serviceGrid">{data.services.map(service=>{const team=teamById.get(service.team_id); const owner=ownerByTeam.get(service.team_id); const prodDeploy=data.deployments.find(d=>d.service_id===service.service_id&&d.environment_id===production?.environment_id); const availability=data.slos.find(s=>s.service_id===service.service_id&&s.metric==="availability"); return <article className={`serviceCard ${service.tier}`} key={service.service_id}><div className="serviceHeader"><span>{service.domain}</span><b>{service.tier.replace("_"," ")}</b></div><h2>{service.name}</h2><p>{service.description}</p><dl><dt>Team</dt><dd>{team?.name}</dd><dt>Owner</dt><dd>{owner?.display_name}</dd><dt>Runtime</dt><dd>{service.runtime}</dd><dt>Prod SLO</dt><dd>{availability?.target}%</dd><dt>Deployment</dt><dd>{prodDeploy?.version}</dd></dl></article>})}</section>
    <section className="card dependencyPanel"><p className="eyebrow">Directed dependency graph</p><h2>Critical service relationships</h2><div className="dependencyList">{data.dependencies.map(dep=><div key={dep.dependency_id}><strong>{serviceById.get(dep.source_service_id)?.name}</strong><span>→ {dep.kind.replace("_"," ")} · {dep.criticality} →</span><strong>{serviceById.get(dep.target_service_id)?.name}</strong></div>)}</div></section>
  </main>;
}
