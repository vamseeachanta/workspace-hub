"""Contract meta-tests; all expectations follow issue 3874 (2026).

The synthetic record has identity='fixture', one node 'config' with digest
'expected', and one repository 'repo' with ignored=['cache'] and untracked=[].
By inspection, removing any required key is incomplete; changing the digest,
ignore membership, absence claim, metadata, or untracked selection violates the
trusted specification. Equality of two such records cannot repair that failure.
No expected disposition is calculated by the code being tested.
"""

import subprocess
from copy import deepcopy
from pathlib import Path

import pytest
from capture_review_contract import (
    ComparisonCase,
    assert_comparison_contract,
    assert_repository_rejection,
)

SPEC = {"identity": "fixture", "digest": "expected", "ignored": "cache"}
VALID = {
    "identity": "fixture",
    "nodes": {"config": {"digest": "expected", "mode": "regular", "absent": False}},
    "repositories": {"repo": {"ignored": ["cache"], "untracked": []}},
}


def _changed(path, value):
    record = deepcopy(VALID)
    parent = record
    for key in path[:-1]:
        parent = parent[key]
    parent[path[-1]] = value
    return record


def _omitted(path):
    record = deepcopy(VALID)
    parent = record
    for key in path[:-1]:
        parent = parent[key]
    del parent[path[-1]]
    return record


def cases():
    """Each expected value is the hand classification in the module docstring."""
    result = [
        ComparisonCase("qualified", VALID, VALID, "qualified"),
        ComparisonCase("missing", None, None, "missing"),
        ComparisonCase("empty_identity", _changed(("identity",), ""), None, "incomplete"),
        ComparisonCase("missing_node", _changed(("nodes",), {}), None, "incomplete"),
        ComparisonCase("missing_repository", _changed(("repositories",), {}), None, "incomplete"),
        ComparisonCase("missing_nested_field", _omitted(("nodes", "config", "digest")), None, "incomplete"),
        ComparisonCase("wrong_type", _changed(("nodes",), []), None, "incomplete"),
        ComparisonCase("absence", _changed(("nodes", "config", "absent"), True), None, "failed"),
        ComparisonCase("digest", _changed(("nodes", "config", "digest"), "other"), None, "failed"),
        ComparisonCase("metadata", _changed(("nodes", "config", "mode"), "link"), None, "failed"),
        ComparisonCase("ignore", _changed(("repositories", "repo", "ignored"), []), None, "failed"),
        ComparisonCase("untracked", _changed(("repositories", "repo", "untracked"), ["extra"]), None, "failed"),
        ComparisonCase("different", VALID, {**VALID, "observation": "later"}, "different"),
    ]
    for path, wrong in [
        (("nodes", "config", "digest"), []),
        (("nodes", "config", "mode"), False),
        (("nodes", "config", "absent"), "false"),
        (("repositories", "repo", "ignored"), {}),
        (("repositories", "repo", "untracked"), ""),
    ]:
        suffix = ".".join(path)
        result.append(ComparisonCase(
            f"missing_nested_field:{suffix}", _omitted(path), None, "incomplete",
        ))
        result.append(ComparisonCase(
            f"wrong_type:{suffix}", _changed(path, wrong), None, "incomplete",
        ))
    result.extend([
        ComparisonCase("missing_node:record", _changed(("nodes", "config"), {}), None, "incomplete"),
        ComparisonCase("missing_repository:record", _changed(("repositories", "repo"), {}), None, "incomplete"),
    ])
    return result


def reference_compare(left, right, spec):
    """Test-only adapter; production record formats are deliberately not defined."""
    def state(record):
        if record is None:
            return "missing"
        try:
            if not isinstance(record["identity"], str) or not record["identity"]:
                return "incomplete"
            node = record["nodes"]["config"]
            repo = record["repositories"]["repo"]
            types = [(node["digest"], str), (node["mode"], str),
                     (node["absent"], bool), (repo["ignored"], list),
                     (repo["untracked"], list)]
            if any(type(value) is not kind for value, kind in types):
                return "incomplete"
        except (KeyError, TypeError):
            return "incomplete"
        if (record["identity"] != spec["identity"] or node["absent"]
                or node["digest"] != spec["digest"] or node["mode"] != "regular"
                or spec["ignored"] not in repo["ignored"] or repo["untracked"]):
            return "failed"
        return "qualified"

    states = (state(left), state(right))
    for status in ("missing", "incomplete", "failed"):
        if status in states:
            return status
    return "qualified" if left == right else "different"


def test_complete_fixture_contract_passes():
    assert_comparison_contract(reference_compare, SPEC, cases())


@pytest.mark.parametrize("name", [case.name for case in cases() if ":" not in case.name])
def test_case_inventory_cannot_be_silently_reduced(name):
    with pytest.raises(AssertionError, match="case inventory"):
        assert_comparison_contract(reference_compare, SPEC, [c for c in cases() if c.name.partition(":")[0] != name])


@pytest.mark.parametrize("bug", ["equality", "shallow", "conditions", "left_only", "mutates"])
def test_contract_catches_known_defect_classes(bug):
    def broken(left, right, spec):
        if bug == "equality":
            return "qualified" if left == right else "different"
        if bug == "shallow" and isinstance(left, dict) and left == right:
            return "qualified"
        if bug == "conditions":
            return reference_compare(left, right, SPEC) if left != right else "qualified"
        if bug == "left_only":
            return reference_compare(left, left, spec)
        if bug == "mutates":
            spec["identity"] = "changed"
        return reference_compare(left, right, spec)

    with pytest.raises(AssertionError):
        assert_comparison_contract(broken, SPEC, cases())


@pytest.mark.parametrize("kind", ["linked_root", "linked_ancestor", "missing_git", "linked_git", "redirected_git_file"])
def test_repository_rejection_precedes_every_subprocess(tmp_path, monkeypatch, kind):
    root = tmp_path / "repo"
    root.mkdir()
    if kind == "linked_root":
        link = tmp_path / "alias"
        link.symlink_to(root, target_is_directory=True)
        root = link
    elif kind == "linked_ancestor":
        link = tmp_path / "alias"
        link.symlink_to(tmp_path, target_is_directory=True)
        root = link / "repo"
    elif kind == "redirected_git_file":
        (root / ".git").write_text("gitdir: ../unexpected\n", encoding="utf-8")
    elif kind == "linked_git":
        (root / ".git").symlink_to(tmp_path, target_is_directory=True)

    def reject(path):
        # Minimal fake collector: no Git is needed to reject fixture bindings.
        if path.is_symlink() or any(p.is_symlink() for p in path.parents):
            raise ValueError("linked root")
        if not (path / ".git").is_dir() or (path / ".git").is_symlink():
            raise ValueError("invalid binding")
        raise AssertionError("fixture did not trigger rejection")

    assert_repository_rejection(reject, root, monkeypatch, ValueError)


@pytest.mark.parametrize("launch", ["run", "Popen"])
def test_root_contract_detects_attempt_even_when_collector_swallows_error(tmp_path, monkeypatch, launch):
    def unsafe(_root):
        try:
            getattr(subprocess, launch)(["git", "--version"])
        except RuntimeError:
            raise ValueError("rejected too late") from None

    with pytest.raises(AssertionError, match="before validation"):
        assert_repository_rejection(unsafe, tmp_path, monkeypatch, ValueError)


def test_root_contract_requires_explicit_rejection(tmp_path, monkeypatch):
    with pytest.raises(AssertionError, match="did not reject"):
        assert_repository_rejection(lambda root: None, tmp_path, monkeypatch, ValueError)


def test_unexpected_exception_is_not_valid_rejection(tmp_path, monkeypatch):
    def crash(root):
        raise RuntimeError("unrelated failure")

    with pytest.raises(RuntimeError, match="unrelated"):
        assert_repository_rejection(crash, Path(tmp_path), monkeypatch, ValueError)


@pytest.mark.parametrize("defect", ["duplicate", "unknown", "wrong_oracle"])
def test_contract_rejects_invalid_case_metadata(defect):
    fixtures = cases()
    if defect == "duplicate":
        fixtures.append(fixtures[0])
    elif defect == "unknown":
        fixtures.append(ComparisonCase("unknown", VALID, VALID, "qualified"))
    else:
        fixtures[1] = ComparisonCase("missing", None, None, "qualified")
    with pytest.raises(AssertionError):
        assert_comparison_contract(reference_compare, SPEC, fixtures)


def test_comparator_crash_does_not_count_as_rejection():
    def crash(*args):
        raise RuntimeError("comparison crashed")

    with pytest.raises(RuntimeError, match="comparison crashed"):
        assert_comparison_contract(crash, SPEC, cases())


@pytest.mark.parametrize("name", ["absence", "digest", "metadata", "ignore", "untracked"])
def test_each_condition_counterexample_detects_its_own_bypass(name):
    target = next(c.left for c in cases() if c.name == name)

    def bypass(left, right, spec):
        if left == right == target:
            return "qualified"
        return reference_compare(left, right, spec)

    with pytest.raises(AssertionError, match=name):
        assert_comparison_contract(bypass, SPEC, cases())


def test_different_case_requires_both_records_to_qualify_individually():
    different = next(c.right for c in cases() if c.name == "different")

    def broken(left, right, spec):
        if left == right == different:
            return "failed"
        return reference_compare(left, right, spec)

    with pytest.raises(AssertionError, match="individually"):
        assert_comparison_contract(broken, SPEC, cases())


def test_different_case_requires_distinct_evidence():
    fixtures = [
        ComparisonCase("different", VALID, VALID, "different") if c.name == "different" else c
        for c in cases()
    ]

    with pytest.raises(AssertionError, match="distinct"):
        assert_comparison_contract(reference_compare, SPEC, fixtures)
