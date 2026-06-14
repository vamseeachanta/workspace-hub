from pathlib import Path


REPO = Path(__file__).resolve().parents[2]


def test_parity_sentinel_sources_default_model_from_registry():
    script = (REPO / "scripts" / "ai" / "parity-sentinel.sh").read_text()

    assert "source \"$ROOT/scripts/lib/model-registry.sh\"" in script
    assert "registry_model claude_strong" in script
    assert "# Usage: parity-sentinel.sh [--model <model-id>] [--days 14]" in script
    assert 'MODEL="claude-opus-4-8"' not in script


def test_scheduled_parity_sentinel_does_not_hardcode_model_id():
    schedule = (REPO / "config" / "scheduled-tasks" / "schedule-tasks.yaml").read_text()

    assert "bash scripts/ai/parity-sentinel.sh --model claude-opus-4-8" not in schedule
    assert "bash scripts/ai/parity-sentinel.sh --days 14" in schedule
