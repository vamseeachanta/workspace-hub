from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "analysis" / "stage_prompt_drift_check.py"
sys.path.insert(0, str(SCRIPT_PATH.parent))
spec = importlib.util.spec_from_file_location("stage_prompt_drift_check", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_find_drift_issues_flags_missing_prompt_without_evidence() -> None:
    packages = [
        {
            "work_item": "WRK-9",
            "stages": [2],
            "prompt_files": [{"path": ".claude/work-queue/assets/WRK-9/stage-2-prompt.md", "exists": False, "reads": 1}],
            "evidence_files": [],
        },
        {
            "work_item": "WRK-10",
            "stages": [2],
            "prompt_files": [{"path": ".claude/work-queue/assets/WRK-10/stage-2-prompt.md", "exists": False, "reads": 1}],
            "evidence_files": [".claude/work-queue/assets/WRK-10/evidence/gate-evidence-summary.md"],
        },
    ]

    issues = module.find_drift_issues(packages)

    assert len(issues) == 1
    assert issues[0]["work_item"] == "WRK-9"
    assert issues[0]["has_replacement"] is False


def test_render_markdown_lists_drift_issue() -> None:
    report = {
        "generated_at": "2026-04-10T00:00:00Z",
        "packages_scanned": 2,
        "issues_found": 1,
        "issues": [
            {
                "work_item": "WRK-9",
                "stages": [2, 4],
                "missing_prompt_files": [
                    {"path": ".claude/work-queue/assets/WRK-9/stage-2-prompt.md", "reads": 3}
                ],
                "evidence_files": [],
                "index_replacements": [],
                "has_replacement": False,
            }
        ],
    }

    markdown = module.render_markdown(report)

    assert "## Drift issues" in markdown
    assert "`WRK-9` — stages: 2, 4" in markdown
    assert "replacement evidence: none" in markdown
    assert ".claude/work-queue/assets/WRK-9/evidence/" in markdown


def test_render_markdown_lists_generated_stub_when_present() -> None:
    report = {
        "generated_at": "2026-04-10T00:00:00Z",
        "packages_scanned": 1,
        "issues_found": 1,
        "write_evidence_stubs": True,
        "issues": [
            {
                "work_item": "WRK-9",
                "stages": [2],
                "missing_prompt_files": [
                    {"path": ".claude/work-queue/assets/WRK-9/stage-2-prompt.md", "reads": 3}
                ],
                "evidence_files": [],
                "index_replacements": [],
                "has_replacement": False,
                "evidence_stub": {
                    "path": ".claude/work-queue/assets/WRK-9/evidence/stage-prompt-drift-summary.stub.md",
                    "created": True,
                },
            }
        ],
    }

    markdown = module.render_markdown(report)

    assert "write_evidence_stubs: true" in markdown
    assert "evidence stub: created" in markdown
    assert "stage-prompt-drift-summary.stub.md" in markdown


def test_filter_newly_introduced_drift_uses_deleted_paths_and_replacements() -> None:
    issues = [
        {
            "work_item": "WRK-9",
            "stages": [2],
            "missing_prompt_files": [
                {"path": ".claude/work-queue/assets/WRK-9/stage-2-prompt.md", "reads": 1}
            ],
            "evidence_files": [],
            "index_replacements": [],
            "has_replacement": False,
        },
        {
            "work_item": "WRK-10",
            "stages": [2],
            "missing_prompt_files": [
                {"path": ".claude/work-queue/assets/WRK-10/stage-2-prompt.md", "reads": 1}
            ],
            "evidence_files": [],
            "index_replacements": [],
            "has_replacement": False,
        },
    ]
    changed_paths = {
        "deleted": {
            ".claude/work-queue/assets/WRK-9/stage-2-prompt.md",
            ".claude/work-queue/assets/WRK-10/stage-2-prompt.md",
        },
        "added": {".claude/work-queue/assets/WRK-10/evidence/gate-evidence-summary.md"},
        "modified": set(),
    }

    filtered = module.filter_newly_introduced_drift(issues, changed_paths)

    assert len(filtered) == 1
    assert filtered[0]["work_item"] == "WRK-9"


def test_build_report_uses_audit_stage_prompt_packages(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    logs_dir = repo_root / "logs"
    logs_dir.mkdir()
    log_file = logs_dir / "session_20260410.jsonl"
    missing_prompt = repo_root / ".claude" / "work-queue" / "assets" / "WRK-9" / "stage-2-prompt.md"
    log_file.write_text(
        json.dumps({"hook": "post", "tool": "Read", "file": str(missing_prompt), "repo": "workspace-hub"}),
        encoding="utf-8",
    )

    report = module.build_report(logs_dir, repo_root)

    assert report["packages_scanned"] == 1
    assert report["issues_found"] == 1
    assert report["issues"][0]["work_item"] == "WRK-9"


def test_build_report_with_base_ref_filters_to_new_drift(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    logs_dir = repo_root / "logs"
    logs_dir.mkdir()
    log_file = logs_dir / "session_20260410.jsonl"
    missing_prompt = repo_root / ".claude" / "work-queue" / "assets" / "WRK-9" / "stage-2-prompt.md"
    log_file.write_text(
        json.dumps({"hook": "post", "tool": "Read", "file": str(missing_prompt), "repo": "workspace-hub"}),
        encoding="utf-8",
    )

    original = module.get_changed_paths
    module.get_changed_paths = lambda *_args, **_kwargs: {
        "deleted": {".claude/work-queue/assets/WRK-9/stage-2-prompt.md"},
        "added": set(),
        "modified": set(),
    }
    try:
        report = module.build_report(logs_dir, repo_root, base_ref="origin/main")
    finally:
        module.get_changed_paths = original

    assert report["base_ref"] == "origin/main"
    assert report["issues_found"] == 1
    assert report["changed_paths"]["deleted"] == [".claude/work-queue/assets/WRK-9/stage-2-prompt.md"]


def test_build_report_writes_blocked_work_item_stub_without_overwriting_existing_stub(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    logs_dir = repo_root / "logs"
    logs_dir.mkdir()
    log_file = logs_dir / "session_20260410.jsonl"
    missing_prompt = repo_root / ".claude" / "work-queue" / "assets" / "WRK-5015" / "stage-0-prompt.md"
    log_file.write_text(
        json.dumps({"hook": "post", "tool": "Read", "file": str(missing_prompt), "repo": "workspace-hub"}),
        encoding="utf-8",
    )
    work_item_record = repo_root / ".claude" / "work-queue" / "pending" / "WRK-5015.md"
    work_item_record.parent.mkdir(parents=True, exist_ok=True)
    work_item_record.write_text(
        "---\n"
        "id: WRK-5015\n"
        "status: pending\n"
        "---\n\n"
        "## Session State\n"
        "- Stage 0 blocked pending external approval\n",
        encoding="utf-8",
    )

    report = module.build_report(logs_dir, repo_root, write_evidence_stubs=True)

    stub_path = repo_root / ".claude" / "work-queue" / "assets" / "WRK-5015" / "evidence" / "stage-prompt-drift-summary.stub.md"
    issue = {
        "work_item": "WRK-5015",
        "stages": [0],
        "missing_prompt_files": [
            {"path": ".claude/work-queue/assets/WRK-5015/stage-0-prompt.md", "reads": 1}
        ],
    }
    assert report["issues_found"] == 1
    assert report["issues"][0]["evidence_stub"]["created"] is True
    assert report["issues"][0]["evidence_stub"]["path"] == ".claude/work-queue/assets/WRK-5015/evidence/stage-prompt-drift-summary.stub.md"
    assert stub_path.exists()
    assert "blocked work item" in stub_path.read_text(encoding="utf-8")

    stub_path.write_text("existing stub\n", encoding="utf-8")

    stub_info = module.create_evidence_stub_for_issue(issue, repo_root, "2026-04-10T00:00:00Z")

    assert stub_info is not None
    assert stub_info["created"] is False
    assert stub_path.read_text(encoding="utf-8") == "existing stub\n"


def test_cli_fail_on_issues_returns_nonzero(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    logs_dir = repo_root / "logs"
    logs_dir.mkdir()
    log_file = logs_dir / "session_20260410.jsonl"
    missing_prompt = repo_root / ".claude" / "work-queue" / "assets" / "WRK-9" / "stage-2-prompt.md"
    log_file.write_text(
        json.dumps({"hook": "post", "tool": "Read", "file": str(missing_prompt), "repo": "workspace-hub"}),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo-root",
            str(repo_root),
            "--logs-dir",
            str(logs_dir),
            "--fail-on-issues",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "WRK-9" in result.stdout
