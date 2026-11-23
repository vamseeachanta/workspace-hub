"""Offline snapshot accounting; expected values are hand calculations below."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


# Two parents reach the repository root from this test directory.
SCRIPT = Path(__file__).resolve().parents[2] / "scripts/analysis/context_budget.py"


@pytest.fixture
def budget_module():
    spec = importlib.util.spec_from_file_location("context_budget", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manifest(tmp_path, components, budget=6):
    # Six is an explicit example budget, independent of the implementation.
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({
        "budget_lexical_units": budget, "components": components,
    }), encoding="utf-8")
    return path


def snapshots(tmp_path, budget=6):
    # Hand count: alpha(5) + space(1) + beta(4) + LF(1) = 11 bytes;
    # tab(1) + gamma(5) + spaces(2) + delta(5) + CRLF(2) = 15 bytes.
    # Each snapshot contains two maximal non-whitespace runs: 2 + 2 = 4.
    (tmp_path / "first.txt").write_bytes(b"alpha beta\n")
    (tmp_path / "second.txt").write_bytes(b"\tgamma  delta\r\n")
    return manifest(tmp_path, [
        {"id": "first", "path": "first.txt"},
        {"id": "second", "path": "second.txt"},
    ], budget)


def run_cli(path, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path)],
        cwd=cwd, capture_output=True, text=True, check=False,
    )


def test_component_counts_and_totals(tmp_path, budget_module):
    report = budget_module.audit_manifest(snapshots(tmp_path))
    assert report["complete"] is True
    assert report["components"] == [
        {"id": "first", "bytes": 11, "lexical_units": 2},
        {"id": "second", "bytes": 15, "lexical_units": 2},
    ]
    assert report["totals"] == {"bytes": 11 + 15, "lexical_units": 2 + 2}


def test_multibyte_accounting(tmp_path, budget_module):
    # UTF-8 hand count: c/a/f(3) + é(2) + space(1) + 猫(3) + LF(1) = 10;
    # 🙂(4) + tab(1) = 5. Lexical units: café/猫 (2), 🙂 (1).
    (tmp_path / "accent.txt").write_bytes("café 猫\n".encode("utf-8"))
    (tmp_path / "symbol.txt").write_bytes("🙂\t".encode("utf-8"))
    path = manifest(tmp_path, [
        {"id": "accent", "path": "accent.txt"},
        {"id": "symbol", "path": "symbol.txt"},
    ])
    report = budget_module.audit_manifest(path)
    assert report["components"] == [
        {"id": "accent", "bytes": 10, "lexical_units": 2},
        {"id": "symbol", "bytes": 5, "lexical_units": 1},
    ]
    assert report["totals"] == {"bytes": 10 + 5, "lexical_units": 2 + 1}


# Four units in snapshots(): budgets 6/4/3 leave 2/0/-1 respectively.
@pytest.mark.parametrize("budget, remaining, over", [
    (6, 6 - 4, False), (4, 4 - 4, False), (3, 3 - 4, True),
])
def test_budget_subtraction(tmp_path, budget_module, budget, remaining, over):
    report = budget_module.audit_manifest(snapshots(tmp_path, budget))
    assert report["budget"] == {
        "lexical_units": budget,
        "remaining_lexical_units": remaining,
        "over_budget": over,
    }


def test_duplicate_component_refused(tmp_path, budget_module):
    path = manifest(tmp_path, [
        {"id": "same", "path": "missing.txt"},
        {"id": "same", "path": "also-missing.txt"},
    ])
    with pytest.raises(budget_module.ContextBudgetError, match="duplicate component"):
        budget_module.audit_manifest(path)


def test_unreadable_component_is_incomplete(tmp_path):
    path = snapshots(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["components"].append({"id": "missing", "path": "absent.txt"})
    path.write_text(json.dumps(data), encoding="utf-8")
    result = run_cli(path, tmp_path)
    # CLI convention: zero succeeds; one reports an input/accounting failure.
    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "complete": False, "error": "component cannot be read as UTF-8",
    }
    assert result.stderr == ""


def test_cli_json_report(tmp_path):
    path = snapshots(tmp_path)
    # A different cwd proves relative paths are anchored to the manifest.
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    result = run_cli(path, elsewhere)
    assert result.returncode == 0
    assert result.stderr == ""
    report = json.loads(result.stdout)
    assert report["complete"] is True
    assert report["method"] == "lexical-unit estimate: maximal non-whitespace runs"
    assert report["limitations"] == "Not provider tokens or live context usage."
    assert report["totals"] == {"bytes": 11 + 15, "lexical_units": 2 + 2}


@pytest.mark.parametrize("value", [
    None, [], {},
    {"budget_lexical_units": True, "components": []},
    {"budget_lexical_units": -1, "components": []},
    {"budget_lexical_units": 1.5, "components": []},
    {"budget_lexical_units": "6", "components": []},
    {"budget_lexical_units": 6, "components": {}},
    {"budget_lexical_units": 6, "components": [None]},
    {"budget_lexical_units": 6, "components": [{"id": "a"}]},
    {"budget_lexical_units": 6, "components": [{"id": " ", "path": "a"}]},
    {"budget_lexical_units": 6, "components": [{"id": "a", "path": ""}]},
    {"budget_lexical_units": 6, "components": [{"id": "a", "path": 1}]},
    {"budget_lexical_units": 6, "components": [], "discover": True},
    {"budget_lexical_units": 6, "components": [
        {"id": "a", "path": "a", "extra": True},
    ]},
])
def test_malformed_manifest_refused(tmp_path, budget_module, value):
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(budget_module.ContextBudgetError):
        budget_module.audit_manifest(path)


@pytest.mark.parametrize("raw", [
    b"not json", b"\xff", b'{"budget_lexical_units": NaN, "components": []}',
    b'{"budget_lexical_units": 6, "budget_lexical_units": 7, "components": []}',
    b'{"budget_lexical_units": 6, "components": '
    b'[{"id": "a", "id": "b", "path": "a"}]}',
])
def test_invalid_json_refused(tmp_path, budget_module, raw):
    path = tmp_path / "invalid.json"
    path.write_bytes(raw)
    with pytest.raises(budget_module.ContextBudgetError):
        budget_module.audit_manifest(path)


@pytest.mark.parametrize("kind", ["invalid-utf8", "directory", "nul-path"])
def test_invalid_component_refused(tmp_path, budget_module, kind):
    component = tmp_path / "component"
    if kind == "directory":
        component.mkdir()
    else:
        component.write_bytes(b"\xff")
    path = manifest(tmp_path, [{
        "id": "invalid", "path": "bad\x00path" if kind == "nul-path" else component.name,
    }])
    with pytest.raises(budget_module.ContextBudgetError):
        budget_module.audit_manifest(path)


def test_missing_manifest_is_incomplete(tmp_path):
    result = run_cli(tmp_path / "missing.json", tmp_path)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "complete": False, "error": "manifest cannot be read as UTF-8 JSON",
    }


def test_empty_selection(tmp_path, budget_module):
    # Empty sums and the minimum permitted budget are zero by definition.
    report = budget_module.audit_manifest(manifest(tmp_path, [], budget=0))
    assert report["components"] == []
    assert report["totals"] == {"bytes": 0, "lexical_units": 0}
    assert report["budget"]["remaining_lexical_units"] == 0
    assert report["budget"]["over_budget"] is False


def test_only_explicit_snapshots_are_counted(tmp_path, budget_module):
    path = snapshots(tmp_path)
    # Unlisted content is deliberately invalid UTF-8 and must never be read.
    (tmp_path / "unlisted.txt").write_bytes(b"\xff")
    report = budget_module.audit_manifest(path)
    assert [item["id"] for item in report["components"]] == ["first", "second"]
