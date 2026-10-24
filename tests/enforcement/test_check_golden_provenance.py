"""Golden provenance policy, with expected outcomes derived from issue 3844.

Independent truth table: a missing/unknown class is an error; archived-run and
none warn; closed-form, measured, cross-solver and conservation pass. These are
policy cases, not numerical engineering acceptance limits. Source (2026):
.claude/rules/reproducibility-is-not-correctness.md, How to apply, comparator table.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/enforcement/check-golden-provenance.py"


@pytest.fixture
def checker():
    spec = importlib.util.spec_from_file_location("golden_provenance", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scan(checker, payload=None, *, mode="100644", extra=None):
    entries = {"tests/golden/answer.txt": ("100644", "answer")}
    if payload is not None:
        entries["tests/golden/provenance.json"] = (mode, "record")
    entries.update(extra or {})
    return checker.audit(entries, lambda oid: payload)


def test_absent_record_fails(checker):
    assert scan(checker) == [("ERROR", "tests/golden", "missing provenance.json")]


@pytest.mark.parametrize("value", ["closed-form", "measured", "cross-solver", "conservation"])
def test_independent_classes_pass(checker, value):
    assert scan(checker, json.dumps({"comparator": {"class": value}}).encode()) == []


@pytest.mark.parametrize("value", ["archived-run", "none"])
def test_regression_only_classes_warn(checker, value):
    assert scan(checker, json.dumps({"comparator": {"class": value}}).encode()) == [
        ("WARNING", "tests/golden", "comparator does not establish correctness")
    ]


@pytest.mark.parametrize("payload", [
    b"{}", b'{"comparator": {}}', b'{"comparator": null}', b"[]", b"null",
    b'{"comparator": {"class": ""}}', b'{"comparator": {"class": "invented"}}',
    b'{"comparator": {"class": []}}', b'{"comparator": {"class": true}}',
    b'{"comparator": {"class": " conservation "}}',
])
def test_absent_or_invalid_class_fails(checker, payload):
    assert scan(checker, payload)[0][0] == "ERROR"


@pytest.mark.parametrize("payload", [
    b"not json", b"\xff", b'{"comparator": {"class": "conservation"}, "x": NaN}',
    b'{"comparator": {"class": "none", "class": "conservation"}}',
    b'{"comparator": {"class": "none"}, "comparator": {"class": "conservation"}}',
])
def test_malformed_or_ambiguous_json_fails_without_echoing_payload(checker, payload):
    assert scan(checker, payload) == [("ERROR", "tests/golden", "invalid provenance JSON")]


def test_symlink_record_fails_without_reading_target(checker):
    assert scan(checker, b"outside", mode="120000") == [
        ("ERROR", "tests/golden", "provenance.json must be a regular Git blob")
    ]


def test_each_named_directory_requires_its_own_record(checker):
    entries = {
        "tests/goldens/a.txt": ("100644", "a"),
        "tests/goldens/nested/golden/b.txt": ("100644", "b"),
        "tests/baseline/a.txt": ("100644", "c"),
        "tests/baselines/nested/b.txt": ("100644", "d"),
        "docs/baseline.md": ("100644", "e"),
        "tests/not_golden/a.txt": ("100644", "f"),
    }
    assert [finding[1] for finding in checker.audit(entries, lambda oid: b"")] == [
        "tests/baseline", "tests/baselines", "tests/goldens", "tests/goldens/nested/golden",
    ]


def test_parent_record_cannot_cover_nested_golden(checker):
    result = scan(checker, b'{"comparator": {"class": "conservation"}}', extra={
        "tests/golden/case/golden/value.txt": ("100644", "nested"),
    })
    assert result == [("ERROR", "tests/golden/case/golden", "missing provenance.json")]


def test_no_matching_directories_is_empty(checker):
    assert checker.audit({"tests/golden.txt": ("100644", "value")}, lambda oid: b"") == []


def test_git_snapshot_uses_nul_paths_and_pinned_tree(checker, monkeypatch, tmp_path):
    calls = []

    def fake_git(repo, *args):
        calls.append((repo, args))
        if args[0] == "rev-parse":
            return b"pinned-tree\n"
        return b"100644 blob digest\ttests/golden/line\nbreak.txt\0"

    monkeypatch.setattr(checker, "git", fake_git)
    assert checker.snapshot(tmp_path, "HEAD") == {
        "tests/golden/line\nbreak.txt": ("100644", "digest"),
    }
    assert calls == [
        (tmp_path, ("rev-parse", "--verify", "--end-of-options", "HEAD^{tree}")),
        (tmp_path, ("ls-tree", "-r", "-z", "pinned-tree")),
    ]


def test_git_binding_environment_is_removed(checker, monkeypatch, tmp_path):
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
        monkeypatch.setenv(name, "unrelated-checkout")

    def fake_run(args, **kwargs):
        assert args[:3] == ["git", "-C", str(tmp_path)]
        assert not any(key.startswith("GIT_") for key in kwargs["env"])
        return subprocess.CompletedProcess(args, 0, stdout=b"result", stderr=b"")

    monkeypatch.setattr(checker.subprocess, "run", fake_run)
    assert checker.git(tmp_path, "ls-tree") == b"result"


@pytest.mark.parametrize("severity, expected", [("ERROR", 1), ("WARNING", 0)])
def test_cli_status_and_summary(checker, monkeypatch, capsys, severity, expected):
    monkeypatch.setattr(checker, "snapshot", lambda *args: {})
    monkeypatch.setattr(checker, "audit", lambda *args: [(severity, "tests/golden", "finding")])
    assert checker.main([]) == expected
    output = capsys.readouterr().out
    assert severity in output
    assert "error(s)" in output and "warning(s)" in output


def test_git_failure_is_distinct_and_does_not_print_stderr(checker, monkeypatch, capsys):
    def fail(*args):
        raise subprocess.CalledProcessError(128, "git", stderr=b"private diagnostic")

    monkeypatch.setattr(checker, "snapshot", fail)
    assert checker.main([]) == 2
    assert capsys.readouterr().err == "ERROR: unable to read the requested Git tree\n"


def test_read_only_integration_sees_base_goldens(checker):
    """Read the existing commit; never create or mutate fixture Git metadata."""
    entries = checker.snapshot(SCRIPT.parents[2], "HEAD")
    assert "tests/ecosystem-sync/golden/empty.md" in entries
    assert checker.audit(entries, lambda oid: checker.git(SCRIPT.parents[2], "cat-file", "blob", oid))


def test_cli_from_other_directory_ignores_inherited_git_binding(tmp_path):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env["GIT_DIR"] = str(tmp_path / "absent-git-dir")
    result = subprocess.run(
        ["python", str(SCRIPT), "--repo", str(SCRIPT.parents[2])],
        cwd=tmp_path, env=env, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 1
    assert "tests/ecosystem-sync/golden" in result.stdout
    assert "unable to read" not in result.stderr


def test_submodule_payload_still_requires_directory_provenance(checker, monkeypatch, tmp_path):
    def fake_git(repo, *args):
        if args[0] == "rev-parse":
            return b"pinned-tree\n"
        return b"160000 commit digest\ttests/baseline/linked-data\0"

    monkeypatch.setattr(checker, "git", fake_git)
    entries = checker.snapshot(tmp_path, "HEAD")
    assert checker.audit(entries, lambda oid: b"") == [
        ("ERROR", "tests/baseline", "missing provenance.json"),
    ]


def test_blob_read_failure_is_operational_error(checker, monkeypatch, capsys):
    monkeypatch.setattr(checker, "snapshot", lambda *args: {
        "golden/provenance.json": ("100644", "unreadable"),
    })

    def fail(*args):
        raise OSError("private diagnostic")

    monkeypatch.setattr(checker, "git", fail)
    assert checker.main([]) == 2
    assert capsys.readouterr().err == "ERROR: unable to read the requested Git tree\n"


def test_worked_policy_example(checker):
    """Hand trace: conservation is in the published class table and is independent.

    Input is the JSON record printed in docs/standards/golden-provenance.md.
    There is one matching directory and its immediate provenance file exists.
    Conservation belongs to the independent set, so there are no errors or
    warnings and the CLI's success result is zero. No code-generated expected
    value, engineering coefficient or measured acceptance limit is used.
    """
    text = (SCRIPT.parents[2] / "docs/standards/golden-provenance.md").read_text()
    payload = text.split("```json\n", 1)[1].split("```", 1)[0].encode()
    assert scan(checker, payload) == []


def test_structural_read_counterexample():
    """Independent hand check for the generic example documented beside the rule.

    Enum value 4 is an arbitrary synthetic identifier, not an engineering
    constant. For an IntEnum, str(State.READY) is decimal text on Python 3.11+;
    decimal text cannot equal the alphabetic member name. Direct member equality
    does match. The expected booleans follow from those different representations.
    Source: issue 3844 (2026), instance 3; repository Python requirement >=3.11.
    """
    from enum import IntEnum

    class State(IntEnum):
        READY = 4

    state = State.READY
    assert (str(state) in {"READY"}) is False
    assert (state in {State.READY}) is True


def test_cli_passes_explicit_repository_and_revision_to_snapshot(checker, monkeypatch, tmp_path, capsys):
    calls = []

    def fake_snapshot(repo, ref):
        calls.append((repo, ref))
        return {"golden/provenance.json": ("100644", "record-digest")}

    def fake_git(repo, *args):
        assert repo == tmp_path
        assert args == ("cat-file", "blob", "record-digest")
        return b'{"comparator": {"class": "measured"}}'

    monkeypatch.setattr(checker, "snapshot", fake_snapshot)
    monkeypatch.setattr(checker, "git", fake_git)
    assert checker.main(["--repo", str(tmp_path), "--ref", "selected-revision"]) == 0
    assert calls == [(tmp_path, "selected-revision")]
    assert capsys.readouterr().out == "Golden provenance: 0 error(s), 0 warning(s)\n"


def test_unusual_path_diagnostics_remain_on_one_line(checker, monkeypatch, capsys):
    monkeypatch.setattr(checker, "snapshot", lambda *args: {
        "tests/line\nbreak/golden/value.txt": ("100644", "payload"),
    })
    assert checker.main([]) == 1
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 2  # One diagnostic plus one summary, by CLI contract.
    assert json.loads(lines[0].split(": ")[1]) == "tests/line\nbreak/golden"
