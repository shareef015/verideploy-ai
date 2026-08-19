from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text())
def main():
 p53=load('evals/reports/phase53-retrieval-metrics.json'); p54=load('evals/reports/phase54-rag-metrics.json'); p55=load('evals/reports/phase55-agent-metrics.json'); p56=load('evals/reports/phase56-llm-quality-metrics.json'); p57=load('evals/reports/phase57-safety-hallucination-metrics.json'); p58=load('evals/reports/phase58-visual-multimodal-metrics.json'); p60=load('evals/reports/phase60-regression-gates.json'); p62=load('evals/reports/phase62-security.json'); p72=load('evals/reports/phase72-testing-strategy.json'); p76=load('evals/reports/phase76-rag-performance.json'); p77=load('evals/reports/phase77-agentic-orchestration.json'); p78=load('evals/reports/phase78-multimodal-integration.json'); p79=load('evals/reports/phase79-production-operations.json'); reg=load('artifacts/release-candidate/pytest-summary.json')
 out={
  'phase':80,'release':'0.80.0','evidence_kind':'actual_local_execution_plus_ci_enforced_browser',
  'regression':reg,
  'coverage':p72['coverage'],
  'mutation_tests':{'killed':sum(1 for m in p72['mutations'] if m['killed']),'total':len(p72['mutations'])},
  'evaluation':{
    'retrieval_gate':bool(p53.get('passed')),
    'rag_gate':bool(p54.get('passed')),
    'agent_gate':bool(p55.get('gate_passed')),
    'llm_quality_gate':bool(p56.get('passed')),
    'safety_gate':bool(p57.get('passed')),
    'multimodal_gate':bool(p58.get('passed')),
    'regression_gate':p60.get('gate',{}).get('status')=='pass',
  },
  'security':{'critical_findings':p62.get('critical_findings',0),'gate':p62.get('gate')},
  'rag_checkpoint':{'gate':p76['gate'],'latency_ms':p76['latency_ms'],'cache':p76['cache'],'metrics':p76['metrics']},
  'agent_checkpoint':{'gate':p77['gate'],'aggregate_score':p77['metrics']['summary']['aggregate_score'],'scenario_count':p77['scenario_count']},
  'multimodal_checkpoint':{'passed':p78['passed'],'clean_traceability':p78['clean']['traceability'],'partial_traceability':p78['partial']['traceability']},
  'operations':{'passed':p79['passed'],'critical_gaps':p79['critical_gaps'],'high_gaps':p79['high_gaps']},
  'browser':{'executed_locally':False,'ci_enforced':True,'reason':'Playwright/node_modules unavailable in local execution container'},
  'accessibility':{'static_semantic_gate':True,'browser_keyboard_assertions_in_ci':True},
 }
 out['local_critical_gates_passed']=all(out['evaluation'].values()) and out['security']['critical_findings']==0 and out['coverage']['passed'] and out['mutation_tests']['killed']==out['mutation_tests']['total'] and out['operations']['critical_gaps']==0 and reg['failed']==0
 path=ROOT/'evals/reports/phase80-release-candidate-benchmarks.json';path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2)); return 0 if out['local_critical_gates_passed'] else 1
if __name__=='__main__': raise SystemExit(main())
