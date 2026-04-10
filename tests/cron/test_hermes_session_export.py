"""Checks for Hermes session export correction tracking (#1745)."""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "hermes-session-export.sh"


def test_hermes_export_mentions_corrections_log_output():
    text = SCRIPT.read_text()
    assert 'logs/orchestrator/hermes/corrections' in text or 'CORRECTIONS_DIR' in text


def test_hermes_export_tracks_repeated_file_edits_as_corrections():
    text = SCRIPT.read_text()
    assert 'correction_gap_seconds' in text
    assert 'type' in text and 'correction' in text


def test_hermes_export_reclassifies_session_search_and_skills_list() -> None:
    text = SCRIPT.read_text()
    assert "'skills_list': 'ToolSearch'" in text
    assert "'session_search': 'Grep'" in text
    assert "entry['search_query']" in text
    assert "entry['skill_category']" in text


def test_hermes_export_includes_session_id() -> None:
    text = SCRIPT.read_text()
    assert "session_id = session.get('session_id', '')" in text
    assert "'session_id': session_id" in text


def test_hermes_export_all_clears_previous_jsonl_outputs() -> None:
    text = SCRIPT.read_text()
    assert 'if [[ "$EXPORT_ALL" == "true" && "$DRY_RUN" == "false" ]]; then' in text
    assert 'rm -f "$OUTPUT_DIR"/session_*.jsonl "$CORRECTIONS_DIR"/session_*.jsonl "$STATE_FILE"' in text
