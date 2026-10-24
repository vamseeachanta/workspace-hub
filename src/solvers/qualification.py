"""Offline numerical evidence checks; no solver execution or implicit limits.

Comparison method: PEP 485 (2015), Implementation and Handling of non-finite
numbers, https://peps.python.org/pep-0485/ . Limits and reference values are
required caller inputs, each accompanied by a declared basis.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from math import isfinite
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import SolverResult


class Status(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_EVALUATED = "NOT_EVALUATED"


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _finite(value: object) -> bool:
    # JSON numeric scalars only; booleans must not become engineering values.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return isfinite(value)
    except OverflowError:
        return False


@dataclass(frozen=True)
class Criterion:
    """One required output, its declared reference and its acceptance basis.

    Units must match literally. No aliases, conversions or physical validity
    of the supplied criteria are inferred from this metadata.
    """

    quantity: str
    expected: float
    units: str
    relative_tolerance: float
    absolute_tolerance: float
    reference: str
    tolerance_basis: str

    def __post_init__(self):
        for name in ("quantity", "units", "reference", "tolerance_basis"):
            if not _text(getattr(self, name)):
                raise ValueError(f"Criterion requires {name}")
        for name in ("expected", "relative_tolerance", "absolute_tolerance"):
            if not _finite(getattr(self, name)):
                raise ValueError(f"Criterion requires finite numeric {name}")
        # Zero permits an exact comparison; negative allowances cannot bound
        # an absolute difference in the PEP 485 (2015) comparison formula.
        if self.relative_tolerance < 0 or self.absolute_tolerance < 0:
            raise ValueError("Criterion tolerances must be non-negative")


@dataclass(frozen=True)
class Assumption:
    """Declared input evidence; None explicitly means unresolved."""

    name: str
    value: str | None
    basis: str

    def __post_init__(self):
        if not _text(self.name) or not _text(self.basis):
            raise ValueError("Assumption requires name and basis")
        if self.value is not None and not _text(self.value):
            raise ValueError("Assumption value must be nonempty or unresolved")


@dataclass(frozen=True)
class CheckResult:
    criterion: Criterion
    status: Status
    reason: str
    observed: float | None
    observed_units: str | None


@dataclass(frozen=True)
class QualificationReport:
    """Acceptance of declared checks only, not engineering certification."""

    solver_name: str
    status: Status
    checks: tuple[CheckResult, ...]
    assumptions: tuple[Assumption, ...]
    reasons: tuple[str, ...]
    method_reference: str = "PEP 485 (2015), Implementation; https://peps.python.org/pep-0485/"

    @property
    def accepted(self) -> bool:
        return self.status == Status.PASS


def compare_value(
    criterion: Criterion, observed: object, observed_units: str | None,
) -> CheckResult:
    """Compare with the symmetric PEP 485 (2015) bound, inclusive at equality.

    |observed-expected| <= max(relative_tolerance * max(|observed|, |expected|),
                               absolute_tolerance).
    Non-finite output always fails, including matching infinities.
    """
    # Omit invalid scalars from the JSON evidence rather than emit NaN/Infinity.
    numeric = observed if _finite(observed) else None
    units = observed_units if _text(observed_units) else None
    if numeric is None:
        status, reason = Status.FAIL, "Output is not a finite numeric scalar"
    elif units is None:
        status, reason = Status.NOT_EVALUATED, "Output unit evidence is missing"
    elif units != criterion.units:
        status, reason = Status.FAIL, "Output units differ from criterion units"
    else:
        # Evaluate the PEP 485 (2015) equation as exact ratios of the supplied
        # scalars. This preserves integer differences and avoids intermediate
        # binary64 overflow; it does not restore precision lost before input.
        actual, expected = Fraction(numeric), Fraction(criterion.expected)
        allowance = max(
            Fraction(criterion.relative_tolerance) * max(abs(actual), abs(expected)),
            Fraction(criterion.absolute_tolerance),
        )
        passed = abs(actual - expected) <= allowance
        status = Status.PASS if passed else Status.FAIL
        reason = "Within declared tolerance" if passed else "Outside declared tolerance"
    return CheckResult(criterion, status, reason, numeric, units)


def qualify_result(
    result: "SolverResult", criteria: Sequence[Criterion], *,
    output_units: Mapping[str, str], assumptions: Sequence[Assumption] = (),
) -> QualificationReport:
    """Inspect an existing result without changing it or executing its solver.

    A failed execution or failed comparison dominates missing evidence.
    Empty criteria, missing outputs/units and unresolved assumptions deny PASS.
    Sources are caller declarations, not authenticated external evidence.
    """
    criteria = tuple(criteria)
    assumptions = tuple(assumptions)
    names = [item.quantity for item in criteria]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate criterion quantity")
    if not isinstance(output_units, Mapping):
        raise TypeError("Output units must be a mapping")
    if result.result_data is not None and not isinstance(result.result_data, Mapping):
        raise TypeError("Result data must be a mapping or absent")
    if type(result.success) is not bool:
        raise TypeError("Execution success must be boolean")
    if not _text(result.solver_name):
        raise ValueError("Result requires solver name")
    reasons = []
    if not result.success:
        reasons.append("Solver execution failed")
    if not criteria:
        reasons.append("No acceptance criteria supplied")
    if any(item.value is None for item in assumptions):
        reasons.append("Assumption evidence is unresolved")
    checks = []
    outputs = result.result_data or {}
    for item in criteria:
        if not result.success or item.quantity not in outputs:
            reason = "Execution failed" if not result.success else "Required output is missing"
            checks.append(CheckResult(item, Status.NOT_EVALUATED, reason, None, None))
        else:
            checks.append(compare_value(item, outputs[item.quantity], output_units.get(item.quantity)))
    if not result.success or any(item.status == Status.FAIL for item in checks):
        status = Status.FAIL
    elif reasons or any(item.status == Status.NOT_EVALUATED for item in checks):
        status = Status.NOT_EVALUATED
    else:
        status = Status.PASS
    return QualificationReport(result.solver_name, status, tuple(checks), assumptions, tuple(reasons))
