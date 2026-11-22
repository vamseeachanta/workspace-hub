"""Solver-independent precision evidence and conservative linear error bounds.

No representation, text format or supplied evidence string authenticates native
accuracy. Callers qualify each bound and retain the source evidence themselves.
Equations and scope: docs/engineering/result-precision.html, Method section.
"""
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from typing import Literal


@dataclass(frozen=True)
class Stage:
    """Description, evidence locator and absolute error in the quantity's unit.

    Native: storage representation; recovery: averaging/extrapolation/integration;
    serialization: text format; accumulation: upstream numerical algorithm.
    A known exact operation requires explicit '0' plus supporting evidence.
    """

    description: str
    evidence: str
    absolute_error: str | None


@dataclass(frozen=True)
class Quantity:
    """A serialized value with per-quantity, release-specific provenance.

    Value and bounds must be finite decimal strings, never binary floats. Bounds
    cover separate additive contributions to the same recovered quantity. Native
    errors requiring sensitivity scaling must be propagated before this record.
    """

    name: str
    unit: str
    value: str
    release: str
    location: str
    source: str
    native: Stage | None
    recovery: Stage | None
    serialization: Stage | None
    accumulation: Stage | None


@dataclass(frozen=True)
class Criterion:
    """Caller-supplied inclusive limit, units and governing criterion evidence."""

    limit: str
    unit: str
    comparator: Literal["<=", ">="]
    evidence: str


@dataclass(frozen=True)
class LinearResult:
    """Exact accumulation of decimal inputs, preserving every contributing record."""

    value: Fraction
    unit: str
    absolute_error: Fraction | None
    reasons: tuple[str, ...]
    terms: tuple[tuple[str, Quantity], ...]


@dataclass(frozen=True)
class Assessment:
    """Disposition applies only to the supplied bound scope, not physical validity."""

    disposition: Literal["PASS", "FAIL", "INDETERMINATE", "NOT_EVALUATED"]
    value: Fraction
    lower: Fraction | None
    upper: Fraction | None
    display: str
    rounding_sensitive: bool
    reasons: tuple[str, ...]
    result: LinearResult
    criterion: Criterion


def _number(text: str) -> Fraction:
    if not isinstance(text, str):
        raise TypeError("numeric inputs must be decimal strings")
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError("invalid decimal input") from exc
    if not value.is_finite():
        raise ValueError("numeric inputs must be finite")
    return Fraction(value)


def _present(text: str) -> bool:
    return isinstance(text, str) and bool(text.strip())


def _bound(quantity: Quantity) -> tuple[Fraction | None, tuple[str, ...]]:
    reasons = []
    for field in ("name", "unit", "release", "location", "source"):
        if not _present(getattr(quantity, field)):
            reasons.append(f"missing quantity {field}")
    total = Fraction(0)
    for field in ("native", "recovery", "serialization", "accumulation"):
        stage = getattr(quantity, field)
        if stage is None:
            reasons.append(f"missing {field} metadata")
            continue
        if not _present(stage.description) or not _present(stage.evidence):
            reasons.append(f"missing {field} description or evidence")
        if stage.absolute_error is None:
            reasons.append(f"missing {field} absolute error bound")
            continue
        error = _number(stage.absolute_error)
        if error < 0:
            raise ValueError("absolute error bounds must be nonnegative")
        total += error
    return (None if reasons else total), tuple(reasons)


def linear_combination(terms: Sequence[tuple[str, Quantity]]) -> LinearResult:
    """Compute y=sum(w*x), B=sum(abs(w)*B_x), without correlation credit.

    Derivation: triangle inequality applied to sum(w*delta_x), with
    abs(delta_x)<=B_x. See Method in result-precision.html. This exact linear
    bound is not NIST TN 1297 (1994), section 5's statistical standard uncertainty.
    Weights are exact, dimensionless decimal inputs; coefficient uncertainty and
    nonlinear recovery require separate qualification. No float accumulation is
    used here, so this operation adds zero arithmetic error to the input bounds.
    """
    terms = tuple(terms)
    if not terms:
        raise ValueError("empty linear combination")
    unit = terms[0][1].unit
    value, total = Fraction(0), Fraction(0)
    reasons = []
    for index, (weight_text, quantity) in enumerate(terms):
        if quantity.unit != unit:
            raise ValueError("linear combination unit mismatch")
        weight = _number(weight_text)
        value += weight * _number(quantity.value)
        bound, gaps = _bound(quantity)
        reasons.extend(f"term {index}: {gap}" for gap in gaps)
        if bound is not None:
            total += abs(weight) * bound
    return LinearResult(value, unit, None if reasons else total, tuple(reasons), terms)


def render_fixed(value: Fraction, places: int) -> str:
    """Round exact rationals to nearest-even; display never changes a bound.

    Python 3.11 decimal documentation, ROUND_HALF_EVEN: ties to nearest even.
    Decimal scaling uses radix ten by definition; the factor two below compares
    a remainder with exactly half the denominator, without intermediate rounding.
    """
    if type(places) is not int:
        raise TypeError("places must be an integer")
    if places < 0:
        raise ValueError("places must be nonnegative")
    scale = 10 ** places
    rounded, remainder = divmod(abs(value.numerator) * scale, value.denominator)
    if remainder * 2 > value.denominator or (
        remainder * 2 == value.denominator and rounded % 2
    ):
        rounded += 1
    sign = "-" if value < 0 and rounded else ""
    whole, fraction = divmod(rounded, scale)
    if not places:
        return f"{sign}{whole}"
    return f"{sign}{whole}.{fraction:0{places}d}"


def assess(
    quantity: Quantity | LinearResult, criterion: Criterion, *, places: int
) -> Assessment:
    """Compare the full interval against an inclusive, caller-qualified limit.

    Upper limit: PASS if y+B<=L; FAIL if y-B>L; otherwise INDETERMINATE.
    Lower limit reverses inequalities. These follow directly from interval
    containment (Method in result-precision.html); no tolerance is assumed.
    Rounding sensitivity compares nominal decisions before and after display;
    it is independent of interval disposition and is not a readiness claim.
    """
    if isinstance(quantity, Quantity):
        result = linear_combination([("1", quantity)])
    elif isinstance(quantity, LinearResult):
        result = linear_combination(quantity.terms)
        if result != quantity:
            raise ValueError("linear result differs from retained terms")
    else:
        raise TypeError("expected a quantity or linear result")
    if criterion.comparator not in ("<=", ">="):
        raise ValueError("unsupported comparator")
    if _present(result.unit) and _present(criterion.unit) and criterion.unit != result.unit:
        raise ValueError("criterion unit mismatch")
    limit = _number(criterion.limit)
    display = render_fixed(result.value, places)
    upper_limit = criterion.comparator == "<="

    def meets(value):
        return value <= limit if upper_limit else value >= limit

    rounding_sensitive = meets(_number(display)) != meets(result.value)
    reasons = list(result.reasons)
    if not _present(criterion.unit):
        reasons.append("missing criterion unit")
    if not _present(criterion.evidence):
        reasons.append("missing criterion evidence")
    if result.absolute_error is None or reasons:
        return Assessment("NOT_EVALUATED", result.value, None, None, display,
                          rounding_sensitive, tuple(reasons), result, criterion)
    lower = result.value - result.absolute_error
    upper = result.value + result.absolute_error
    best, worst = (lower, upper) if upper_limit else (upper, lower)
    if meets(worst):
        disposition = "PASS"
    elif not meets(best):
        disposition = "FAIL"
    else:
        disposition = "INDETERMINATE"
    return Assessment(disposition, result.value, lower, upper, display,
                      rounding_sensitive, (), result, criterion)
