from pathlib import Path


def test_langgraph_runtime_migration_has_run_event_tables_and_forced_rls():
    text = Path("src/verideploy/database/migrations/versions/0006_phase18_langgraph_runtime.py").read_text()
    assert 'revision = "0006_phase18_langgraph_runtime"' in text
    assert 'down_revision = "0005_phase17_video_evidence"' in text
    assert '"graph_runs_phase18"' in text
    assert '"graph_runtime_events_phase18"' in text
    assert "ENABLE ROW LEVEL SECURITY" in text
    assert "FORCE ROW LEVEL SECURITY" in text
    assert "uq_graph_event_sequence" in text
