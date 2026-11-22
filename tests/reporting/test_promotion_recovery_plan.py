"""Synthetic recovery oracles, derived by equality comparisons by hand.

Basis: issue 2183 acceptance, interrupted promotion and no-op recovery.
P denotes the retained prior bundle; N denotes the distinct staged bundle;
X denotes an unrelated bundle. The proposed schema's v1 is a format label.
No identifier is a digest, path, physical constant or external dataset.

Literal truth table (staged=N, prior=P, recovery target=P throughout):
    journal state   current   action       target
    prepared        P         recover      P
    prepared        N         finalize     N
    swapped         P         unresolved   none
    swapped         N         finalize     N
    finalized       P         unresolved   none
    finalized       N         no-op        N
    recovered       P         no-op        P
    recovered       N         unresolved   none
Any missing identifier, staged!=N, prior!=P, current=X or unknown state is
unresolved. Each oracle below is literal, independent of the planner.
"""

import copy
import itertools
import json
import os
import stat
from pathlib import Path

import pytest

from scripts.reporting import promotion_recovery_plan
from scripts.reporting.promotion_recovery_plan import plan_recovery


TRUTH_TABLE = [
    ("prepared", "P", "recover", "P"),
    ("prepared", "N", "finalize", "N"),
    ("swapped", "P", "unresolved", None),
    ("swapped", "N", "finalize", "N"),
    ("finalized", "P", "unresolved", None),
    ("finalized", "N", "no-op", "N"),
    ("recovered", "P", "no-op", "P"),
    ("recovered", "N", "unresolved", None),
]


def journal(state="prepared"):
    """Proposed versioned example; P and N are synthetic identity symbols."""
    return {
        "schema": "publication-rollback-journal-v1",
        "promotion_id": "synthetic-promotion",
        "state": state,
        "staged_id": "N",
        "prior_id": "P",
        "recovery_target_id": "P",
        "evidence": {"ref": "synthetic-observation", "notes": ["retain"]},
    }


def observed(current="P"):
    return {"current_id": current, "staged_id": "N", "prior_id": "P"}


def evaluate(state="prepared", current="P"):
    return plan_recovery(json.dumps(journal(state)), observed(current))


def test_before_swap_plan():
    """Hand check: current=P, so preserve P and abandon unfinished promotion."""
    result = evaluate()
    assert result["action"] == "recover"
    assert result["target_id"] == "P"
    assert result["reason"] == "prior-still-current"


@pytest.mark.parametrize("state", ["prepared", "swapped"])
def test_after_swap_plan(state):
    """current=N proves the swap even if the journal still says prepared."""
    result = evaluate(state, "N")
    assert result["action"] == "finalize"
    assert result["target_id"] == "N"
    assert result["reason"] == "staged-now-current"


def test_finalized_noop():
    """Finalized with current=N needs no further recovery step."""
    result = evaluate("finalized", "N")
    assert result["action"] == "no-op"
    assert result["target_id"] == "N"
    assert result["reason"] == "already-finalized"


def test_contradictory_observation_is_unresolved():
    """Swapped claims N became current, but observed P contradicts that."""
    result = evaluate("swapped", "P")
    assert result["action"] == "unresolved"
    assert result["target_id"] is None
    assert result["reason"] == "state-observation-conflict"


@pytest.mark.parametrize("state,current,action,target", TRUTH_TABLE)
def test_literal_truth_table(state, current, action, target):
    result = evaluate(state, current)
    assert (result["action"], result["target_id"]) == (action, target)


@pytest.mark.parametrize("state", ["prepared", "swapped", "finalized", "recovered"])
@pytest.mark.parametrize("current,staged,prior", [
    values for values in itertools.product(("P", "N", "X"), repeat=3)
    if values[0] == "X" or values[1:] != ("N", "P")
])
def test_unrecognized_observation_combinations(state, current, staged, prior):
    """By hand: current outside {P,N}, staged!=N or prior!=P denies action.

    Three observed positions give the Cartesian product of these symbols;
    repeat=3 is its arity, not an engineering constant.
    """
    result = plan_recovery(json.dumps(journal(state)), {
        "current_id": current, "staged_id": staged, "prior_id": prior,
    })
    assert result["action"] == "unresolved"
    assert result["target_id"] is None


@pytest.mark.parametrize("key", [
    "promotion_id", "staged_id", "prior_id", "recovery_target_id",
])
@pytest.mark.parametrize("invalid", [None, "", " ", False, [], {}])
def test_invalid_journal_identifiers(key, invalid):
    value = journal()
    value[key] = invalid
    result = plan_recovery(json.dumps(value), observed())
    assert result["action"] == "unresolved"
    assert result["reason"] == "invalid-journal-identifier"


@pytest.mark.parametrize("key", [
    "schema", "state", "promotion_id", "staged_id", "prior_id", "recovery_target_id",
])
def test_missing_journal_fields(key):
    value = journal()
    del value[key]
    assert plan_recovery(json.dumps(value), observed())["action"] == "unresolved"


@pytest.mark.parametrize("key", ["current_id", "staged_id", "prior_id"])
@pytest.mark.parametrize("invalid", [None, "", " ", False, [], {}])
def test_invalid_observed_identifiers(key, invalid):
    value = observed()
    value[key] = invalid
    result = plan_recovery(json.dumps(journal()), value)
    assert result["action"] == "unresolved"
    assert result["reason"] == "invalid-observed-identifier"


@pytest.mark.parametrize("key", ["current_id", "staged_id", "prior_id"])
def test_missing_observed_identifiers(key):
    value = observed()
    del value[key]
    assert plan_recovery(json.dumps(journal()), value)["action"] == "unresolved"


@pytest.mark.parametrize("key,value", [
    ("schema", "publication-rollback-journal-next"),
    ("schema", []), ("state", "pending"), ("state", []),
    ("recovery_target_id", "X"), ("staged_id", "P"),
])
def test_unknown_or_inconsistent_journal(key, value):
    packet = journal()
    packet[key] = value
    result = plan_recovery(json.dumps(packet), observed())
    assert result["action"] == "unresolved"
    assert result["target_id"] is None


@pytest.mark.parametrize("raw", [
    '{"state":"prepared","state":"swapped"}',
    '{"evidence":{"ref":"P","ref":"N"}}',
    '{"evidence":NaN}', '{"evidence":Infinity}', '{"evidence":-Infinity}',
    '{"evidence":1e999}', '{', '[]', 'null', '"journal"',
    None, {}, False, b"\xff",
])
def test_ambiguous_or_invalid_json_is_unresolved_and_retained(raw):
    result = plan_recovery(raw, observed())
    assert result["action"] == "unresolved"
    assert result["target_id"] is None
    assert result["evidence"]["journal_json"] == raw


@pytest.mark.parametrize("original,replacement", [
    ('"state": "prepared"', '"state": "prepared", "state": "prepared"'),
    ('"state": "prepared"', '"state": "prepared", "state": "swapped"'),
    ('"ref": "synthetic-observation"', '"ref": "P", "ref": "N"'),
])
def test_duplicate_keys_in_otherwise_valid_journal(original, replacement):
    """Duplicate rejection must deny an otherwise actionable complete journal."""
    raw = json.dumps(journal()).replace(original, replacement)
    result = plan_recovery(raw, observed())
    assert result["action"] == "unresolved"
    assert result["reason"] == "invalid-journal-json"
    assert result["evidence"]["journal_json"] == raw
    assert result["evidence"]["journal"] is None


def test_documented_example_matches_independent_synthetic_fixture():
    example = promotion_recovery_plan.__doc__.split("    {", maxsplit=1)[1]
    value, _ = json.JSONDecoder().raw_decode("{" + example)
    assert value == journal()
    result = plan_recovery(json.dumps(value).encode("utf-8"), observed())
    assert result["action"] == "recover"
    assert result["target_id"] == "P"


def test_identifiers_are_compared_exactly_without_normalization():
    """An extra space changes an opaque identity, so it cannot select P."""
    assert plan_recovery(json.dumps(journal()), observed("P "))["action"] == "unresolved"


@pytest.mark.parametrize("value", [None, [], "P"])
def test_observations_require_an_explicit_object(value):
    result = plan_recovery(json.dumps(journal()), value)
    assert result["action"] == "unresolved"
    assert result["evidence"]["observations"] == value


@pytest.mark.parametrize("state,current,action,target", TRUTH_TABLE)
def test_repeated_evaluation_retains_independent_evidence(state, current, action, target):
    raw = json.dumps(journal(state), indent=True)
    value = observed(current)
    value["extra_evidence"] = {"notes": ["preserve"]}
    before = copy.deepcopy(value)
    first = plan_recovery(raw, value)
    second = plan_recovery(raw, value)
    assert first == second
    assert first["evidence"] == {
        "journal_json": raw, "journal": journal(state), "observations": before,
    }
    first["evidence"]["observations"]["extra_evidence"]["notes"].append("changed")
    first["evidence"]["journal"]["evidence"]["notes"].append("changed")
    assert value == before
    assert plan_recovery(raw, value) == second


def metadata_snapshot(root, paths):
    """Include root and subdirectories, nanosecond times and file identities."""
    return {
        str(path.relative_to(root)): (
            info.st_mode, info.st_ino, info.st_dev, info.st_nlink,
            info.st_uid, info.st_gid, info.st_size,
            info.st_atime_ns, info.st_mtime_ns, info.st_ctime_ns,
        )
        for path in paths
        for info in (path.stat(),)
    }


def snapshot(root):
    """Record content and stable metadata; reads precede metadata snapshots."""
    paths = (root, *sorted(root.rglob("*")))
    contents = {str(path.relative_to(root)): path.read_bytes()
                for path in paths if path.is_file()}
    return contents, metadata_snapshot(root, paths), paths


@pytest.mark.parametrize("state,current,action,target", TRUTH_TABLE)
def test_caller_files_and_metadata_preserved(tmp_path, monkeypatch, state, current,
                                            action, target):
    """All writes stay in tmp_path; bundle IDs are deliberately path-shaped.

    Permissions use Python stat's named POSIX flags. Metadata is captured
    after reading fixture bytes, so the check includes access time changes.
    """
    current_path = tmp_path / "current"
    staged_path = tmp_path / "staged"
    prior_path = tmp_path / "prior"
    packet = journal(state)
    packet["staged_id"] = str(staged_path)
    packet["prior_id"] = packet["recovery_target_id"] = str(prior_path)
    raw = json.dumps(packet)
    for path in (current_path, staged_path, prior_path):
        path.write_text("synthetic bytes", encoding="utf-8")
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    journal_path = tmp_path / "journal.json"
    journal_path.write_text(raw, encoding="utf-8")
    metadata = tmp_path / ".git"
    metadata.mkdir()
    (metadata / "HEAD").write_text("synthetic metadata", encoding="utf-8")
    values = {"P": str(prior_path), "N": str(staged_path)}
    observations = {
        "current_id": values[current], "staged_id": str(staged_path),
        "prior_id": str(prior_path),
    }
    before = snapshot(tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("planner attempted filesystem access")

    # A planner receives evidence, never locators to open or swap.
    with monkeypatch.context() as patch:
        for name in ("open", "stat", "lstat", "rename", "replace", "unlink"):
            patch.setattr(os, name, forbidden)
        patch.setattr("builtins.open", forbidden)
        patch.setattr(Path, "open", forbidden)
        result = plan_recovery(raw, observations)
        assert result == plan_recovery(raw, observations)
    assert (result["action"], result["target_id"]) == (action, values.get(target))
    # Check metadata before reading contents again, including retained .git bytes.
    # Reusing known paths avoids changing directory access times in the probe.
    assert metadata_snapshot(tmp_path, before[2]) == before[1]
    assert snapshot(tmp_path)[0] == before[0]
