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
