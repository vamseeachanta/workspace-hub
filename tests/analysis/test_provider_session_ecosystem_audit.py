from __future__ import annotations

import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "analysis" / "provider_session_ecosystem_audit.py"
spec = importlib.util.spec_from_file_location("provider_session_ecosystem_audit", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_classify_read_target_for_symbolic_skill_name(tmp_path: Path) -> None:
    normalized, scope, exists = module.classify_read_target("github-issues", tmp_path)

    assert normalized == "github-issues"
    assert scope == "symbolic"
    assert exists is False


def test_classify_read_target_for_repo_relative_path(tmp_path: Path) -> None:
    target = tmp_path / "docs" / "report.md"
    target.parent.mkdir(parents=True)
    target.write_text("ok", encoding="utf-8")

    normalized, scope, exists = module.classify_read_target("docs/report.md", tmp_path)

    assert normalized == "docs/report.md"
    assert scope == "repo"
    assert exists is True


def test_classify_read_target_expands_tilde_to_external() -> None:
    normalized, scope, exists = module.classify_read_target("~/.hermes/config.yaml", Path("/tmp/repo"))

    assert normalized.endswith("/.hermes/config.yaml")
    assert scope == "external"
    assert exists in {True, False}


def test_classify_read_target_for_slash_symbolic_skill_name(tmp_path: Path) -> None:
    normalized, scope, exists = module.classify_read_target(
        "coordination/workspace/repo-capability-map", tmp_path
    )

    assert normalized == "coordination/workspace/repo-capability-map"
    assert scope == "symbolic"
    assert exists is False


def test_classify_read_target_uses_repo_alias_for_absolute_workspace_path(tmp_path: Path) -> None:
    target = tmp_path / "docs" / "report.md"
    target.parent.mkdir(parents=True)
    target.write_text("ok", encoding="utf-8")

    normalized, scope, exists = module.classify_read_target(
        "/mnt/workspace-hub/docs/report.md", tmp_path
    )

    assert normalized == "docs/report.md"
    assert scope == "repo"
    assert exists is True


def test_normalize_cmd_decodes_codex_spaced_command() -> None:
    raw = " p y t h o n 3   - c   \" p r i n t ( 1 ) \" "

    assert module.normalize_cmd("codex", raw) == 'python3 -c "print(1)"'


def test_normalize_cmd_preserves_shell_separators_for_codex() -> None:
    raw = " g i t   s t a t u s   & &   p w d   |   s e d   - n   ' 1 p '   2 > / d e v / n u l l "

    assert module.normalize_cmd("codex", raw) == "git status && pwd | sed -n '1p' 2>/dev/null"


def test_cleanup_bash_command_drops_comments_and_cd_wrapper() -> None:
    raw = "# comment\ncd /tmp/repo && uv run --no-project python tool.py\n"

    assert module.cleanup_bash_command(raw) == "uv run --no-project python tool.py"


def test_normalize_command_to_prefix_uses_multiword_prefix() -> None:
    assert module.normalize_command_to_prefix("cd /tmp/repo && uv run --no-project python tool.py") == "uv run"


def test_summarize_raw_provider_tracks_symbolic_and_python3(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    logs_dir = repo_root / "logs" / "orchestrator" / "hermes"
    logs_dir.mkdir(parents=True)
    existing = repo_root / "docs" / "keep.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("hi", encoding="utf-8")

    records = [
        {"hook": "post", "tool": "Read", "file": "github-issues", "repo": "workspace-hub"},
        {"hook": "post", "tool": "Read", "file": "docs/keep.md", "repo": "workspace-hub"},
        {"hook": "post", "tool": "Read", "file": "docs/missing.md", "repo": "workspace-hub"},
        {"hook": "post", "tool": "Bash", "cmd": "python3 -c \"print(1)\"", "repo": "workspace-hub"},
        {"hook": "pre", "tool": "Read", "file": "docs/missing.md", "repo": "workspace-hub"},
    ]
    (logs_dir / "session_20260410.jsonl").write_text(
        "\n".join(json.dumps(r) for r in records), encoding="utf-8"
    )

    summary = module.summarize_raw_provider("hermes", logs_dir, repo_root)

    assert summary["sessions"] == 1
    assert summary["post_records"] == 4
    assert summary["python3_bash_calls"] == 1
    assert summary["top_symbolic_reads"][0]["name"] == "github-issues"
    assert summary["top_missing_repo_reads"][0]["path"] == "docs/missing.md"
    assert summary["top_reads"][0]["path"] == "docs/keep.md"


def test_summarize_raw_provider_treats_skill_view_reads_as_symbolic(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    logs_dir = repo_root / "logs" / "orchestrator" / "hermes"
    logs_dir.mkdir(parents=True)
    records = [
        {
            "hook": "post",
            "tool": "Read",
            "file": "gh-work-planning",
            "repo": "workspace-hub",
            "hermes_tool": "skill_view",
        }
    ]
    (logs_dir / "session_20260410.jsonl").write_text(
        "\n".join(json.dumps(r) for r in records), encoding="utf-8"
    )

    summary = module.summarize_raw_provider("hermes", logs_dir, repo_root)

    assert summary["top_symbolic_reads"][0]["name"] == "gh-work-planning"
    assert summary["top_missing_repo_reads"] == []


def test_build_provider_audit_handles_missing_provider_dirs(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    logs_root = repo_root / "logs" / "orchestrator"
    logs_root.mkdir(parents=True)

    audit = module.build_provider_audit(repo_root=repo_root, logs_root=logs_root)

    assert audit["providers"]["codex"]["source"] == "missing_log_directory"
    assert audit["providers"]["gemini"]["source"] == "missing_log_directory"


def test_build_provider_audit_prefers_raw_claude_logs_when_present(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    logs_root = repo_root / "logs" / "orchestrator"
    claude_dir = logs_root / "claude"
    claude_dir.mkdir(parents=True)
    records = [{"hook": "post", "tool": "Bash", "cmd": "python3 -c \"print(1)\"", "repo": "workspace-hub"}]
    (claude_dir / "session_20260410.jsonl").write_text(
        "\n".join(json.dumps(r) for r in records), encoding="utf-8"
    )

    audit = module.build_provider_audit(repo_root=repo_root, logs_root=logs_root)

    assert audit["providers"]["claude"]["source"] == "raw_logs"
    assert audit["providers"]["claude"]["post_records"] == 1


def test_build_provider_audit_consumes_gemini_export_jsonl(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    logs_root = repo_root / "logs" / "orchestrator"
    gemini_dir = logs_root / "gemini"
    gemini_dir.mkdir(parents=True)
    records = [
        {
            "hook": "post",
            "tool": "Bash",
            "gemini_tool": "run_shell_command",
            "cmd": 'python3 -c "print(1)"',
            "repo": "workspace-hub",
            "session_id": "gem-1",
        },
        {
            "hook": "post",
            "tool": "Read",
            "gemini_tool": "read_file",
            "file": "docs/keep.md",
            "repo": "workspace-hub",
            "session_id": "gem-1",
        },
    ]
    target = repo_root / "docs" / "keep.md"
    target.parent.mkdir(parents=True)
    target.write_text("ok", encoding="utf-8")
    (gemini_dir / "session_20260410.jsonl").write_text(
        "\n".join(json.dumps(r) for r in records), encoding="utf-8"
    )

    audit = module.build_provider_audit(repo_root=repo_root, logs_root=logs_root)

    assert audit["providers"]["gemini"]["source"] == "raw_logs"
    assert audit["providers"]["gemini"]["sessions"] == 1
    assert audit["providers"]["gemini"]["post_records"] == 2
    assert audit["providers"]["gemini"]["python3_bash_calls"] == 1
    assert audit["providers"]["gemini"]["unique_runtime_sessions"] == 1
    assert audit["providers"]["gemini"]["top_reads"][0]["path"] == "docs/keep.md"
    assert audit["providers"]["gemini"]["top_bash_command_families"][0]["prefix"] == "python3"


def test_render_markdown_mentions_symbolic_reads() -> None:
    audit = {
        "generated_at": "2026-04-10T00:00:00Z",
        "logs_root": "/tmp/logs/orchestrator",
        "providers": {
            "hermes": {
                "source": "raw_logs",
                "sessions": 1,
                "post_records": 10,
                "correction_sessions": 1,
                "unique_runtime_sessions": 0,
                "prompt_reads": 0,
                "blank_reads": 0,
                "python3_bash_calls": 1,
                "uv_python_bash_calls": 2,
                "top_tools": [],
                "top_repos": [],
                "top_reads": [],
                "top_symbolic_reads": [{"name": "github-issues", "count": 3}],
                "top_missing_repo_reads": [],
                "top_missing_external_reads": [],
                "special_counts": {},
            }
        },
    }

    markdown = module.render_markdown(audit)

    assert "top symbolic reads" in markdown.lower()
    assert "github-issues" in markdown
