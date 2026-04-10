from __future__ import annotations

import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "analysis" / "claude_session_ecosystem_audit.py"
spec = importlib.util.spec_from_file_location("claude_session_ecosystem_audit", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_normalize_path_for_repo_file(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    target = repo_root / "docs" / "report.md"
    target.parent.mkdir(parents=True)
    target.write_text("ok", encoding="utf-8")

    normalized, exists, scope = module.normalize_path(str(target), repo_root)

    assert normalized == "docs/report.md"
    assert exists is True
    assert scope == "repo"


def test_normalize_path_for_missing_external_file(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    normalized, exists, scope = module.normalize_path("/tmp/does-not-exist/prompt.md", repo_root)

    assert normalized == "/tmp/does-not-exist/prompt.md"
    assert exists is False
    assert scope == "external"


def test_build_summary_counts_missing_repo_reads_and_prompts(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    logs_dir = repo_root / "logs"
    logs_dir.mkdir()
    existing = repo_root / "docs" / "keep.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("hi", encoding="utf-8")

    missing_prompt = str(repo_root / ".claude" / "work-queue" / "assets" / "WRK-9" / "stage-2-prompt.md")
    existing_path = str(existing)
    log_file = logs_dir / "session_20260409.jsonl"
    records = [
        {"hook": "post", "tool": "Read", "file": missing_prompt, "repo": "workspace-hub"},
        {"hook": "post", "tool": "Read", "file": existing_path, "repo": "workspace-hub"},
        {"hook": "post", "tool": "Bash", "cmd": "python3 -c \"print(1)\"", "repo": "workspace-hub"},
        {"hook": "pre", "tool": "Read", "file": missing_prompt, "repo": "workspace-hub"},
    ]
    log_file.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")

    summary = module.build_summary(logs_dir, repo_root)

    assert summary["sessions_analyzed"] == 1
    assert summary["post_records"] == 3
    assert summary["prompt_read_total"] == 1
    assert summary["missing_repo_read_total"] == 1
    assert summary["top_missing_repo_reads"][0]["path"].endswith("stage-2-prompt.md")
    assert summary["stage_prompt_distribution"][0]["stage"] == 2
    assert summary["python3_bash_calls"] == 1
