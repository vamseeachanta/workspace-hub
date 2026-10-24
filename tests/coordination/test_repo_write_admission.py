"""Repository write admission cases derived from issue 3829's exclusion rule.

Independent truth table: for the same repository and two writers, conflict =
(candidate provider is Codex) OR (active provider is Codex). A reader or a
separate repository makes conflict false. No measured or empirical constants
are used; expected decisions below enumerate this Boolean expression directly.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts/coordination/repo_write_admission.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("repo_write_admission", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def task(provider="codex", access="write", repository="example/repository"):
    return {
        "task": "change-a",
        "repository": repository,
        "provider": provider,
        "access": access,
    }


def roster(*active, complete=True):
    return {"complete": complete, "active": list(active)}


@pytest.mark.parametrize(
    "candidate,active,allowed",
    [
        ("codex", "codex", False),
        ("codex", "claude", False),
        ("claude", "codex", False),
        ("claude", "claude", True),
        ("codex", "other", False),
        ("other", "codex", False),
    ],
)
def test_writer_truth_table(candidate, active, allowed):
    result = load_module().evaluate(task(candidate), roster(task(active)))
    assert result["allowed"] is allowed
    assert result["status"] == ("ALLOWED" if allowed else "BLOCKED")


@pytest.mark.parametrize(
    "candidate_access,active_access",
    [
        ("read", "write"),
        ("write", "read"),
        ("read", "read"),
    ],
)
def test_readers_do_not_conflict(candidate_access, active_access):
    assert load_module().evaluate(
        task(access=candidate_access), roster(task("claude", active_access))
    )["allowed"]


def test_separate_repository_does_not_conflict():
    assert load_module().evaluate(
        task(), roster(task("claude", repository="example/another"))
    )["allowed"]


def test_empty_complete_roster_allows_first_writer():
    assert load_module().evaluate(task(), roster())["allowed"]


def test_incomplete_roster_never_allows_even_a_reader():
    result = load_module().evaluate(task(access="read"), roster(complete=False))
    assert result == {"allowed": False, "status": "NOT_EVALUATED", "blockers": []}


def test_every_conflicting_writer_is_reported_in_input_order():
    first, second = task("claude"), task()
    second["task"] = "change-b"
    assert load_module().evaluate(task(), roster(first, second))["blockers"] == [
        "change-a",
        "change-b",
    ]


@pytest.mark.parametrize(
    "field,value",
    [
        ("access", "unknown"),
        ("provider", ""),
        ("task", ""),
        ("repository", "Example/repository"),
        ("repository", "../repository"),
        ("repository", "example/repository.git"),
        ("repository", "repository"),
        ("repository", "example/repository\n"),
        ("provider", "Codex"),
    ],
)
def test_invalid_candidate_is_rejected(field, value):
    candidate = task()
    candidate[field] = value
    with pytest.raises(ValueError):
        load_module().evaluate(candidate, roster())


@pytest.mark.parametrize(
    "snapshot",
    [
        {},
        {"complete": "yes", "active": []},
        {"complete": True},
        {"complete": True, "active": {}},
        roster({}),
        roster(None),
        {"complete": True, "active": [], "extra": True},
    ],
)
def test_invalid_roster_is_rejected(snapshot):
    with pytest.raises(ValueError):
        load_module().evaluate(task(), snapshot)


def run_cli(tmp_path, candidate, snapshot):
    candidate_file, roster_file = tmp_path / "candidate.json", tmp_path / "roster.json"
    candidate_file.write_text(json.dumps(candidate))
    roster_file.write_text(json.dumps(snapshot))
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--candidate",
            str(candidate_file),
            "--roster",
            str(roster_file),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    "snapshot,code,status",
    [
        (roster(), 0, "ALLOWED"),
        (roster(task("claude")), 1, "BLOCKED"),
        (roster(complete=False), 2, "NOT_EVALUATED"),
    ],
)
def test_cli_decisions(tmp_path, snapshot, code, status):
    result = run_cli(tmp_path, task(), snapshot)
    assert result.returncode == code
    assert json.loads(result.stdout)["status"] == status


def test_cli_missing_file_fails_without_disclosing_path(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--candidate",
            str(tmp_path / "missing"),
            "--roster",
            str(tmp_path / "missing"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "NOT_EVALUATED"
    assert str(tmp_path) not in result.stdout + result.stderr


def test_cli_rejects_duplicate_json_keys(tmp_path):
    source = tmp_path / "duplicate.json"
    source.write_text('{"complete": false, "complete": true, "active": []}')
    candidate = tmp_path / "candidate.json"
    candidate.write_text(json.dumps(task()))
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--candidate",
            str(candidate),
            "--roster",
            str(source),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("provider", ["codex-worker", "unknown", "codex_exec"])
def test_provider_aliases_cannot_bypass_exclusion(provider):
    with pytest.raises(ValueError):
        load_module().evaluate(task(provider), roster(task("claude")))


def test_worked_example_matches_documented_decision(tmp_path):
    """Both writers + same repository + Codex candidate => blocked by change-a."""
    import re

    document = (
        SCRIPT.parents[2] / "docs/examples/repository-writer-admission.html"
    ).read_text()
    objects = [
        json.loads(block)
        for block in re.findall(
            r"<pre>(\{.*?\})</pre>",
            document,
            re.DOTALL,
        )
    ]
    candidate, snapshot, expected = objects
    result = run_cli(tmp_path, candidate, snapshot)
    assert result.returncode == 1
    assert json.loads(result.stdout) == expected
