"use client";
import { useEffect,useMemo,useState } from "react";
const gateway=process.env.NEXT_PUBLIC_GATEWAY_URL??"http://localhost:4000";
const tenantId="11111111-1111-4111-8111-111111111111";
type Entity={entity_id:string;entity_type:string;label:string;reference_uri:string;observed_at:string|null};
type Edge={edge_id:string;source_entity_id:string;target_entity_id:string;relationship:string;confidence:number;occurred_at:string|null};
type Snapshot={snapshot_sha256:string;entities:Entity[];edges:Edge[]};
const order=["pull_request","service","incident","root_cause","evidence"];
export default function EvidenceGraphPage(){
 const [data,setData]=useState<Snapshot|null>(null);const [error,setError]=useState("");
 useEffect(()=>{const c=new AbortController();void(async()=>{try{const r=await fetch(`${gateway}/api/v1/evidence-graph/snapshot`,{headers:{"x-tenant-id":tenantId,"x-correlation-id":crypto.randomUUID()},cache:"no-store",signal:c.signal});if(!r.ok)throw new Error(`Evidence graph request failed with ${r.status}`);setData(await r.json() as Snapshot);}catch(e){if(!c.signal.aborted)setError(e instanceof Error?e.message:"Evidence graph unavailable");}})();return()=>c.abort();},[]);
 const byId=useMemo(()=>new Map((data?.entities??[]).map(e=>[e.entity_id,e])),[data]);
 if(error)return <main className="page"><section className="hero"><p className="eyebrow">Evidence graph</p><h1>Graph unavailable</h1><p className="error">{error}</p></section></main>;
 if(!data)return <main className="page"><section className="hero"><p className="eyebrow">Evidence graph</p><h1>Loading lineage…</h1></section></main>;
 const lanes=[...data.entities].sort((a,b)=>order.indexOf(a.entity_type)-order.indexOf(b.entity_type));
 return <main className="page graphPage"><section className="hero"><p className="eyebrow">Tenant-isolated relational graph</p><h1>Evidence Graph & Lineage</h1><p>Typed entities, temporal relationships, immutable evidence references, and queryable cause paths. Snapshot <code>{data.snapshot_sha256.slice(0,12)}</code>.</p></section>
 <section className="graphStats"><article><strong>{data.entities.length}</strong><span>Entities</span></article><article><strong>{data.edges.length}</strong><span>Relationships</span></article></section>
 <section className="graphFlow">{lanes.map((e,index)=><div className="graphNode" key={e.entity_id}><span>{e.entity_type.replaceAll("_"," ")}</span><strong>{e.label}</strong><small>{e.observed_at?new Date(e.observed_at).toLocaleString():"reference entity"}</small>{index<lanes.length-1&&<i>→</i>}</div>)}</section>
 <section className="card graphEdges"><p className="eyebrow">Typed temporal edges</p><h2>Lineage and causal relationships</h2>{data.edges.map(e=><div key={e.edge_id}><strong>{byId.get(e.source_entity_id)?.label}</strong><span>{e.relationship.replaceAll("_"," ")} · {(e.confidence*100).toFixed(0)}%</span><strong>{byId.get(e.target_entity_id)?.label}</strong></div>)}</section></main>;
}
