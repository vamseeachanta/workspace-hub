"""Synthetic boundaries for #2332; no operational corpus or reports are read.

Policy basis: #2332 names ``uv run python`` and ``uv run --no-project python``.
The existing declarations in provider_session_ecosystem_audit.py are the basis
for normalization (normalize_cmd), substring counters (summarize_raw_provider),
and ratio thresholds (compute_python_hygiene_status). These tests characterize
those APIs; substring counters are not an execution-aware compliance measure.
All counts below are hand calculations from literal synthetic records.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts" / "analysis" / "provider_session_ecosystem_audit.py"
)


@pytest.fixture
def audit_module(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    spec = importlib.util.spec_from_file_location("runtime_boundary_audit", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    root = tmp_path / "repo"
    root.mkdir()
    monkeypatch.setattr(module, "REPO_ROOT", root)
    monkeypatch.setattr(module, "LOGS_ROOT", root / "logs")
    monkeypatch.setattr(module, "CLAUDE_PRECOMPUTED", root / "absent.json")
    monkeypatch.setattr(module, "load_github_issue_index", lambda _root: [])
    return module


# Columns: hook, tool, command, expected family, python3 count, uv-python count.
# Ten post records: two bare executions and three canonical executions; five
# non-executions/invalid inputs contribute no runtime counts. The pre record is
# excluded. Thus the hand-counted densities are 2/10*1000=200 and 3/10*1000=300.
RUNTIME_RECORDS = (
    ("post", "Bash", "python3 tool.py", "python3", 1, 0),
    ("post", "Bash", "MODE=test python3 tool.py", "python3", 1, 0),
    ("post", "Bash", "uv run python tool.py", "uv run", 0, 1),
    ("post", "Bash", "uv run --no-project python tool.py", "uv run", 0, 1),
    ("post", "Bash", "MODE=test uv run python tool.py", "uv run", 0, 1),
    ("post", "Read", "python3 tool.py", None, 0, 0),
    ("post", "Bash", None, "", 0, 0),
    ("post", "Bash", "", "", 0, 0),
    ("post", "Bash", "   ", "", 0, 0),
    ("post", "Bash", "printf 'unterminated", "printf", 0, 0),
    ("pre", "Bash", "python3 ignored.py", None, 0, 0),
)


def write_records(logs_dir: Path, records: list[dict]) -> None:
    logs_dir.mkdir(parents=True, exist_ok=True)
    # The production glob requires this filename shape; the date is synthetic.
    (logs_dir / "session_20000101.jsonl").write_text(
        "\n".join(json.dumps(record) for record in records) + "\n{invalid json\n",
        encoding="utf-8",
    )


@pytest.mark.parametrize("provider", ("codex", "hermes"))
def test_runtime_counts_match_literal_records(audit_module, provider: str) -> None:
    records = [
        {"hook": hook, "tool": tool, "cmd": cmd}
        for hook, tool, cmd, _prefix, _bare, _uv in RUNTIME_RECORDS
    ]
    logs_dir = audit_module.LOGS_ROOT / provider
    write_records(logs_dir, records)

    summary = audit_module.summarize_raw_provider(provider, logs_dir, audit_module.REPO_ROOT)

    assert summary["post_records"] == 10
    assert summary["python3_bash_calls"] == sum(row[4] for row in RUNTIME_RECORDS) == 2
    assert summary["uv_python_bash_calls"] == sum(row[5] for row in RUNTIME_RECORDS) == 3
    assert summary["python3_per_1k_records"] == 200.0
    assert summary["uv_python_per_1k_records"] == 300.0
    assert summary["top_tools"] == [{"tool": "Bash", "count": 9}, {"tool": "Read", "count": 1}]
    assert {row["prefix"]: row["count"] for row in summary["top_bash_command_families"]} == {
        "uv run": 3, "python3": 2, "printf": 1,
    }
    for hook, _tool, cmd, prefix, _bare, _uv in RUNTIME_RECORDS:
        if hook == "post" and prefix is not None:
            normalized = audit_module.normalize_cmd(provider, cmd)
            assert audit_module.normalize_command_to_prefix(normalized, cleanup=True) == prefix


@pytest.mark.parametrize("provider", ("codex", "hermes"))
def test_quoted_python_mention_is_not_execution(audit_module, provider: str) -> None:
    command = 'printf "%s" "python3 uv run python"'
    logs_dir = audit_module.LOGS_ROOT / provider
    write_records(logs_dir, [{"hook": "post", "tool": "Bash", "cmd": command}])

    summary = audit_module.summarize_raw_provider(provider, logs_dir, audit_module.REPO_ROOT)
    normalized = audit_module.normalize_cmd(provider, command)

    # One printf execution, zero Python executions: the command-family API
    # preserves the distinction even though both substring counters hit once.
    assert normalized == command
    assert audit_module.normalize_command_to_prefix(normalized, cleanup=True) == "printf"
    assert summary["top_bash_command_families"] == [
        {"prefix": "printf", "count": 1, "share_of_bash_calls": 100.0, "example_command": command}
    ]
    # Known limit of the existing API, not evidence of runtime compliance.
    assert summary["python3_bash_calls"] == 1
    assert summary["uv_python_bash_calls"] == 1


@pytest.mark.parametrize(
    ("raw", "expected", "prefix"),
    (
        (None, "", ""),
        ("", "", ""),
        ("   ", "", ""),
        ("python3 tool.py", "python3 tool.py", "python3"),
        (" u v   r u n   p y t h o n   t o o l . p y ", "uv run python tool.py", "uv run"),
        (" p y t h o n 3   t o o l . p y ", "python3 tool.py", "python3"),
        ("printf 'unterminated", "printf 'unterminated", "printf"),
    ),
)
def test_normalization_preserves_runtime_boundaries(audit_module, raw, expected, prefix) -> None:
    # Literal decoded strings exercise the spaced encoding declared by normalize_cmd.
    normalized = audit_module.normalize_cmd("codex", raw)
    assert normalized == expected
    assert audit_module.normalize_command_to_prefix(normalized, cleanup=True) == prefix


@pytest.mark.parametrize(
    ("bare", "canonical", "expected"),
    (
        (0, 0, "no_python_usage"),
        (0, 1, "uv_preferred"),
        (4, 0, "python3_heavy"),
        (4, 1, "python3_heavy"),
        (4, 2, "mixed"),
        (4, 7, "mixed"),
        (4, 8, "uv_preferred"),
    ),
)
def test_hygiene_threshold_boundaries(audit_module, bare, canonical, expected) -> None:
    # Existing compute_python_hygiene_status declares canonical >= 2*bare and
    # canonical < 0.5*bare. For bare=4 the boundaries are 8 and 2, inclusive
    # only at the upper bound; equal denominators cancel from these ratios.
    assert audit_module.compute_python_hygiene_status(bare, canonical) == expected


@pytest.mark.parametrize("activity", ("missing", "directory", "empty_file", "pre_only"))
def test_empty_activity_is_not_healthy_evidence(audit_module, activity: str) -> None:
    logs_dir = audit_module.LOGS_ROOT / "codex"
    if activity != "missing":
        logs_dir.mkdir(parents=True)
    if activity == "empty_file":
        (logs_dir / "session_20000101.jsonl").write_text("", encoding="utf-8")
    elif activity == "pre_only":
        write_records(logs_dir, [{"hook": "pre", "tool": "Bash", "cmd": "uv run python tool.py"}])

    audit = audit_module.build_provider_audit(
        repo_root=audit_module.REPO_ROOT, logs_root=audit_module.LOGS_ROOT
    )
    summary = audit["providers"]["codex"]

    assert summary["post_records"] == 0
    # Without a denominator, missing rates remain unknown (absent), not measured
    # zeros. The legacy interpretation label is no_python_usage, not compliance.
    assert summary.get("python3_per_1k_records") is None
    assert summary.get("uv_python_per_1k_records") is None
    rows = audit["executive_summary"]["provider_interpretation_summary"]["providers"]
    row = next(row for row in rows if row["provider"] == "codex")
    assert row["python_hygiene_status"] == "no_python_usage"
    assert row["python_hygiene_trend"] == "unavailable"
