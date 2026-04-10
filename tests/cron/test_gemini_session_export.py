from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "gemini-session-export.sh"
NIGHTLY = REPO_ROOT / "scripts" / "cron" / "comprehensive-learning-nightly.sh"
README = REPO_ROOT / "logs" / "orchestrator" / "README.md"


def test_gemini_export_script_exists_and_targets_session_jsonl() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

    assert "logs/orchestrator/gemini" in text
    assert "session_" in text and ".jsonl" in text
    assert "projectHash" in text
    assert "tool_call_id" in text
    assert "exported_tool_call_ids" in text


def test_gemini_export_scans_project_name_and_project_hash_directories() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

    assert 'gemini_tmp / repo_name / "chats"' in text
    assert 'gemini_tmp / repo_hash / "chats"' in text
    assert 'hashlib.sha256(str(workspace_hub).encode("utf-8")).hexdigest()' in text


def test_nightly_workflow_invokes_gemini_export() -> None:
    text = NIGHTLY.read_text(encoding="utf-8")

    assert "Gemini session export" in text
    assert "bash scripts/cron/gemini-session-export.sh" in text


def test_orchestrator_readme_mentions_gemini_session_jsonl_requirement() -> None:
    text = README.read_text(encoding="utf-8")

    assert "logs/orchestrator/gemini/session_*.jsonl" in text
