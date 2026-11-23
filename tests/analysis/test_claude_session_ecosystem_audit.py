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


def test_normalize_path_for_windows_workspace_file(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    target = repo_root / "docs" / "report.md"
    target.parent.mkdir(parents=True)
    target.write_text("ok", encoding="utf-8")

    normalized, exists, scope = module.normalize_path(r"D:\workspace-hub\docs\report.md", repo_root)

    assert normalized == "docs/report.md"
    assert exists is True
    assert scope == "repo"


def test_normalize_path_for_uppercase_msys_windows_workspace_file(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    target = repo_root / "docs" / "report.md"
    target.parent.mkdir(parents=True)
    target.write_text("ok", encoding="utf-8")

    normalized, exists, scope = module.normalize_path("/D/workspace-hub/docs/report.md", repo_root)

    assert normalized == "docs/report.md"
    assert exists is True
    assert scope == "repo"


def test_build_summary_counts_missing_repo_reads_and_prompts(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    logs_dir = repo_root / "logs"
    logs_dir.mkdir()
    existing = repo_root / "docs" / "keep.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("hi", encoding="utf-8")

    asset_dir = repo_root / ".claude" / "work-queue" / "assets" / "WRK-9"
    evidence_dir = asset_dir / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "gate-evidence-summary.md").write_text("ok", encoding="utf-8")
    missing_prompt = str(asset_dir / "stage-2-prompt.md")
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
    assert summary["stage_prompt_packages"][0]["work_item"] == "WRK-9"
    assert summary["stage_prompt_packages"][0]["stages"] == [2]
    assert summary["stage_prompt_packages"][0]["prompt_files"][0]["exists"] is False
    assert summary["stage_prompt_packages"][0]["evidence_files"] == [
        ".claude/work-queue/assets/WRK-9/evidence/gate-evidence-summary.md"
    ]


def test_render_markdown_includes_stage_prompt_package_index() -> None:
    summary = {
        "generated_at": "2026-04-09T18:00:00Z",
        "sessions_analyzed": 1,
        "post_records": 3,
        "prompt_read_total": 1,
        "prompt_read_unique": 1,
        "missing_repo_read_total": 1,
        "missing_external_read_total": 0,
        "python3_bash_calls": 1,
        "uv_python_bash_calls": 0,
        "tool_distribution": [],
        "repo_distribution": [],
        "top_reads": [],
        "top_missing_repo_reads": [],
        "top_missing_external_reads": [],
        "top_prompt_reads": [],
        "top_missing_prompt_reads": [],
        "stage_prompt_distribution": [],
        "stage_prompt_work_items": [],
        "stage_prompt_packages": [
            {
                "work_item": "WRK-9",
                "stages": [2, 4],
                "prompt_files": [
                    {
                        "path": ".claude/work-queue/assets/WRK-9/stage-2-prompt.md",
                        "exists": False,
                        "reads": 3,
                    }
                ],
                "evidence_files": [
                    ".claude/work-queue/assets/WRK-9/evidence/gate-evidence-summary.md"
                ],
            }
        ],
    }

    markdown = module.render_markdown(summary)

    assert "## Stage prompt package index" in markdown
    assert "`WRK-9` — stages: 2, 4" in markdown
    assert "missing prompt artifacts: 1" in markdown
    assert "gate-evidence-summary.md" in markdown
