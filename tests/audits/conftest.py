"""Conftest for tests/audits/ — opt-in semantics for `@pytest.mark.audit`.

Per W2-D plan AC: audit-marked tests should be SKIPPED in default pytest runs
(both `uv run pytest tests/audits/` and `uv run pytest`) and execute ONLY when
`-m audit` is passed explicitly.

Pytest's default mark behavior runs all tests regardless of marker. This
conftest inverts that for the `audit` marker by reading `-m` from the active
config: if the user did NOT pass `-m audit` (or a compatible expression),
audit-marked tests are auto-skipped.
"""

from __future__ import annotations

import pytest


def pytest_collection_modifyitems(config, items):
    """Auto-skip audit-marked tests unless `-m` selector explicitly opts in."""
    markexpr = config.getoption("-m", default="") or ""
    # If user passed `-m audit` (or any expression containing `audit` as a
    # positive selector), let the tests run. Otherwise skip them.
    # Heuristic: presence of "audit" without a leading "not " before it.
    explicit_opt_in = "audit" in markexpr and "not audit" not in markexpr
    if explicit_opt_in:
        return
    skip_audit = pytest.mark.skip(reason="audit-marked: opt-in only via `pytest -m audit`")
    for item in items:
        if "audit" in item.keywords:
            item.add_marker(skip_audit)
