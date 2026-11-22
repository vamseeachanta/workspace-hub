"""Synthetic comparison checks; no audit collection or operational input.

Numeric basis (independent hand calculation, in millionths): previous =
1_000_000 and tolerance = 10_001. The six boundary rows have signed differences
+10_000, +10_001, +10_002, -10_000, -10_001, -10_002, respectively. Absolute
values at most 10_001 are stable; otherwise the sign and preference determine
the literal expected direction. The unchanged row has difference zero.

Context settings are synthetic stress inputs, not acceptance thresholds:
precision 2 discards boundary digits; precision 12 retains them. Bounds -9..9
admit the differences, while -1..0 makes them subnormal. Rounding up and down
can move a boundary outward or inward; half-even adds a third rounding mode.
All traps are either disabled or enabled, including Inexact and Subnormal.

Plan-lite
---------
Scope: comparison-only checks in
tests/analysis/test_compare_direction_decimal_context.py. Validation will use
synthetic operands, literal expected directions and restored Decimal contexts.

Offline validation (supply --basetemp with an external temporary directory):
uv run --offline --no-project --with pytest --with pyyaml python -m pytest \
tests/analysis/test_compare_direction_decimal_context.py -q -rA -p no:cacheprovider

Acceptance: all 240 cases will pass without skips, both context fixtures will
restore caller state, and production code and acceptance thresholds will remain
unchanged. Existing-suite failures will be reported separately with their basis.
"""

from __future__ import annotations

from decimal import (
    ROUND_DOWN,
    ROUND_HALF_EVEN,
    ROUND_UP,
    Context,
    Decimal,
    DefaultContext,
    getcontext,
    localcontext,
    setcontext,
)

import pytest

from scripts.analysis.provider_session_ecosystem_audit import compare_direction


# All expected classifications follow the integer calculation above, not Decimal
# arithmetic or another call to the function under test. Missing operands have no
# difference and must return unavailable, including when both are missing.
CASES = [
    pytest.param("1.010000", "1.000000", "stable", "stable", id="positive-below"),
    pytest.param("1.010001", "1.000000", "stable", "stable", id="positive-boundary"),
    pytest.param("1.010002", "1.000000", "worsening", "improving", id="positive-above"),
    pytest.param("0.990000", "1.000000", "stable", "stable", id="negative-below"),
    pytest.param("0.989999", "1.000000", "stable", "stable", id="negative-boundary"),
    pytest.param("0.989998", "1.000000", "improving", "worsening", id="negative-above"),
    pytest.param("1.000000", "1.000000", "stable", "stable", id="unchanged"),
    pytest.param(None, "1.000000", "unavailable", "unavailable", id="current-missing"),
    pytest.param("1.000000", None, "unavailable", "unavailable", id="previous-missing"),
    pytest.param(None, None, "unavailable", "unavailable", id="both-missing"),
]

CONTEXTS = [
    pytest.param((12, ROUND_HALF_EVEN, -9, 9, False), id="exact"),
    pytest.param((2, ROUND_DOWN, -9, 9, False), id="round-inward"),
    pytest.param((2, ROUND_UP, -9, 9, False), id="round-outward"),
    pytest.param((2, ROUND_HALF_EVEN, -1, 0, False), id="narrow-bounds"),
    pytest.param((2, ROUND_UP, -9, 9, True), id="trapped-rounding"),
    pytest.param((12, ROUND_DOWN, -1, 0, True), id="trapped-subnormal"),
]

# These are every writable scalar Context attribute. Flags and traps are copied
# separately so finalizers also preserve pre-existing sticky signals.
CONTEXT_ATTRIBUTES = ("prec", "rounding", "Emin", "Emax", "capitals", "clamp")


def _copy_context_settings(target: Context, source: Context) -> None:
    for attribute in CONTEXT_ATTRIBUTES:
        setattr(target, attribute, getattr(source, attribute))
    target.flags = source.flags.copy()
    target.traps = source.traps.copy()


@pytest.fixture(params=CONTEXTS)
def hostile_context(request):
    # Explicitly set all fields rather than inheriting ambient or default traps.
    # capitals=1 and clamp=0 select the ordinary representation for these cases;
    # neither changes the hand-derived differences.
    precision, rounding, emin, emax, trap_all = request.param
    context = Context(
        prec=precision,
        rounding=rounding,
        Emin=emin,
        Emax=emax,
        capitals=1,
        clamp=0,
        flags=[],
        traps=[],
    )
    for signal in context.traps:
        context.traps[signal] = trap_all
    return context


@pytest.fixture
def ambient_context(hostile_context):
    original = getcontext()
    try:
        # Install a copy: the original context and the fixture remain untouched.
        setcontext(hostile_context.copy())
        yield getcontext()
    finally:
        setcontext(original)


@pytest.fixture
def changed_default_context(hostile_context):
    original = getcontext()
    saved_default = DefaultContext.copy()
    try:
        _copy_context_settings(DefaultContext, hostile_context)
        # Copy the mutated default into a fresh active context. Mutating defaults
        # alone would leave an already-created active context unchanged.
        with localcontext(DefaultContext.copy()) as active:
            yield active
    finally:
        _copy_context_settings(DefaultContext, saved_default)
        setcontext(original)


@pytest.mark.parametrize("better_when_lower", [True, False], ids=["lower", "higher"])
@pytest.mark.parametrize("current,previous,lower_expected,higher_expected", CASES)
def test_decimal_boundary_comparison_is_context_independent(
    ambient_context, current, previous, lower_expected, higher_expected, better_when_lower
):
    # String construction is exact even inside the hostile active context.
    expected = lower_expected if better_when_lower else higher_expected
    assert compare_direction(
        Decimal(current) if current is not None else None,
        Decimal(previous) if previous is not None else None,
        better_when_lower=better_when_lower,
        tolerance=Decimal("0.010001"),
    ) == expected
    # Exact rational comparison should not set even an untrapped Decimal flag.
    assert not any(ambient_context.flags.values())


@pytest.mark.parametrize("better_when_lower", [True, False], ids=["lower", "higher"])
@pytest.mark.parametrize("current,previous,lower_expected,higher_expected", CASES)
def test_default_context_mutation_cannot_change_direction(
    changed_default_context, current, previous, lower_expected, higher_expected, better_when_lower
):
    expected = lower_expected if better_when_lower else higher_expected
    assert compare_direction(
        Decimal(current) if current is not None else None,
        Decimal(previous) if previous is not None else None,
        better_when_lower=better_when_lower,
        tolerance=Decimal("0.010001"),
    ) == expected
    assert not any(changed_default_context.flags.values())
