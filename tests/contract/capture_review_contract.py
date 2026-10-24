"""Reusable, test-only assertions for the capture review contract.

Source: issue 3874 (2026), acceptance requirements and condition counterexamples.
Adapters retain their owning schema and normalize dispositions only. This module
neither collects evidence nor authenticates a specification or qualifies a host.
"""

import subprocess
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

# These are review-case names and dispositions, not a new persistence schema.
_REQUIRED = {
    "qualified": "qualified",
    "missing": "missing",
    "empty_identity": "incomplete",
    "missing_node": "incomplete",
    "missing_repository": "incomplete",
    "missing_nested_field": "incomplete",
    "wrong_type": "incomplete",
    "absence": "failed",
    "digest": "failed",
    "metadata": "failed",
    "ignore": "failed",
    "untracked": "failed",
    "different": "different",
}


@dataclass(frozen=True)
class ComparisonCase:
    """An independently classified fixture; right=None repeats left exactly."""

    name: str
    left: Any
    right: Any
    expected: str


def _compare_without_mutation(compare, left, right, specification):
    inputs = deepcopy((left, right, specification))
    before = deepcopy(inputs)
    result = compare(*inputs)
    assert inputs == before, "comparison mutated evidence or trusted specification"
    return result


def assert_comparison_contract(
    compare: Callable, specification: Any, cases: list[ComparisonCase],
) -> None:
    """Check completeness and conditions independently of snapshot equality.

    Incomplete/failed/missing fixtures are compared both with themselves and with
    the valid control, in both argument orders. Fixture authors shall independently
    establish each mutation and expected result against their caller's schema.
    Use category:field names to enumerate every required nested field and type.
    Exceptions are not normalized to a passing disposition by this assertion.
    """
    names = [case.name for case in cases]
    assert len(names) == len(set(names)), "duplicate case inventory"
    categories = {name.partition(":")[0] for name in names}
    assert categories == set(_REQUIRED), "case inventory is incomplete or unknown"
    assert "qualified" in names, "case inventory needs a qualified control"
    valid = next(case.left for case in cases if case.name == "qualified")
    for case in cases:
        assert case.expected == _REQUIRED[case.name.partition(":")[0]], f"wrong oracle: {case.name}"
        right = case.left if case.right is None else case.right
        if case.expected == "different":
            assert case.left != right, "different case requires distinct evidence"
            for record in (case.left, right):
                status = _compare_without_mutation(compare, record, record, specification)
                assert status == "qualified", "different records must qualify individually"
        pairs = [(case.left, right), (right, case.left)]
        if case.expected in {"missing", "incomplete", "failed"}:
            pairs.extend([(case.left, case.left), (case.left, valid), (valid, case.left)])
        for left, right in pairs:
            actual = _compare_without_mutation(compare, left, right, specification)
            assert actual == case.expected, (
                f"{case.name}: expected {case.expected}, got {actual!r}"
            )


class _ForbiddenLaunch(RuntimeError):
    """An attempted subprocess launch; never valid repository rejection."""


def assert_repository_rejection(capture, root, monkeypatch, rejection) -> None:
    """Require rejection of one invalid root without launching any subprocess.

    Patch the standard subprocess entry points; caller tests shall also intercept
    any native, cached or alternate command launcher they use. Run this assertion
    separately for linked roots/ancestors and missing/redirected Git bindings.
    """
    launches = []

    def forbidden(*args, **kwargs):
        launches.append((args, kwargs))
        raise _ForbiddenLaunch("repository command before validation")

    rejected = False
    with monkeypatch.context() as patch:
        patch.setattr(subprocess, "run", forbidden)
        patch.setattr(subprocess, "Popen", forbidden)
        try:
            capture(root)
        except _ForbiddenLaunch:
            pass
        except rejection:
            rejected = True
    assert not launches, "repository command attempted before validation"
    assert rejected, "collector did not reject invalid repository"
