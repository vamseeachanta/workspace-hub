"""Precision examples use synthetic inputs and independent hand arithmetic.

No fixture is native solver evidence. All error bounds and limits are explicit
example assumptions, not material constants or engineering acceptance criteria.
"""
from dataclasses import replace
from fractions import Fraction

import pytest
from reporting.result_precision import (
    Criterion,
    Quantity,
    Stage,
    assess,
    linear_combination,
    render_fixed,
)


def quantity(value="9.96", error="0.01", **overrides):
    """Assume four separate records, with no correlation credit taken."""
    fields = {
        "name": "response", "unit": "N", "value": value, "release": "synthetic example",
        "location": "section resultant", "source": "synthetic hand calculation",
        "native": Stage("declared storage", "example assumption", error),
        "recovery": Stage("identity", "exact identity by definition", "0"),
        "serialization": Stage("decimal text", "example assumes exact retention", "0"),
        "accumulation": Stage("none", "single example value", "0"),
    }
    fields.update(overrides)
    return Quantity(**fields)


def criterion(limit="10", comparator="<=", **overrides):
    fields = {"limit": limit, "unit": "N", "comparator": comparator,
              "evidence": "synthetic example limit, supplied as input"}
    fields.update(overrides)
    return Criterion(**fields)


def test_rounding_does_not_decide_acceptance():
    """10.04 > 10, although nearest-even to one place gives 10.0 <= 10."""
    result = assess(quantity("10.04", "0"), criterion(), places=1)
    assert result.disposition == "FAIL"
    assert result.display == "10.0"
    assert result.rounding_sensitive is True
    assert result.lower == result.upper == Fraction(251, 25)


@pytest.mark.parametrize("value,error,expected", [
    ("9.96", "0.01", "PASS"),  # [9.95, 9.97] <= 10
    ("10.04", "0.01", "FAIL"),  # [10.03, 10.05] > 10
    ("9.96", "0.05", "INDETERMINATE"),  # [9.91, 10.01] straddles 10
    ("10", "0", "PASS"),  # inclusive equality is required by <=
])
def test_upper_limit_interval(value, error, expected):
    """Endpoints are value +/- the supplied absolute bound (hand arithmetic)."""
    assert assess(quantity(value, error), criterion(), places=1).disposition == expected


@pytest.mark.parametrize("value,error,expected", [
    ("10.04", "0.01", "PASS"),
    ("9.96", "0.01", "FAIL"),
    ("10.04", "0.05", "INDETERMINATE"),
    ("10", "0", "PASS"),
])
def test_lower_limit_interval(value, error, expected):
    """Same hand intervals as upper-limit test, with >= 10 comparison."""
    result = assess(quantity(value, error), criterion(comparator=">="), places=1)
    assert result.disposition == expected


@pytest.mark.parametrize("stage", ["native", "recovery", "serialization", "accumulation"])
@pytest.mark.parametrize("missing", [None, Stage("", "", None),
                                    Stage("known", "source", None),
                                    Stage("known", "", "0")])
def test_each_missing_stage_denies_acceptance(stage, missing):
    """An arbitrary number of printed digits cannot fill an evidence gap."""
    q = quantity("9.9600000000000000", **{stage: missing})
    result = assess(q, criterion(), places=16)
    assert result.disposition == "NOT_EVALUATED"
    assert result.lower is None and result.upper is None
    assert any(stage in reason for reason in result.reasons)


@pytest.mark.parametrize("field", ["release", "location", "source", "name", "unit"])
def test_missing_identity_metadata_denies_acceptance(field):
    assert assess(quantity(**{field: ""}), criterion(), places=1).disposition == "NOT_EVALUATED"


def test_missing_criterion_evidence_denies_acceptance():
    result = assess(quantity(), criterion(evidence=""), places=1)
    assert result.disposition == "NOT_EVALUATED"


def test_linear_bound_negative_weights_and_correlation():
    """y=2*3-4=2; B=|2|*.1+|-1|*.2=.4; interval=[1.6,2.4].

    This follows by the triangle inequality, without assuming independence.
    Reusing the same quantity twice deliberately takes no cancellation credit.
    """
    a, b = quantity("3", ".1"), quantity("4", ".2")
    combined = linear_combination([("2", a), ("-1", b)])
    result = assess(combined, criterion("2.2"), places=1)
    assert combined.value == 2
    assert result.lower == Fraction(8, 5)
    assert result.upper == Fraction(12, 5)
    assert result.disposition == "INDETERMINATE"
    cancelled = linear_combination([("1", a), ("-1", a)])
    assert cancelled.value == 0 and cancelled.absolute_error == Fraction(1, 5)
    assert combined.terms == (("2", a), ("-1", b))


def test_all_four_bounds_are_retained():
    """B=.01+.02+.03+.04=.10, so 9.96 lies in [9.86,10.06]."""
    q = quantity(recovery=Stage("average", "example assumption", ".02"),
                 serialization=Stage("export", "example assumption", ".03"),
                 accumulation=Stage("sum", "example assumption", ".04"))
    result = assess(q, criterion(), places=1)
    assert result.lower == Fraction(493, 50)
    assert result.upper == Fraction(503, 50)
    assert result.disposition == "INDETERMINATE"


def test_exact_decimal_accumulation_under_cancellation():
    """10**16 + 1 - 10**16 = 1 exactly; decimal text is parsed as rationals."""
    result = linear_combination([("1", quantity("10000000000000000", "0")),
                                 ("1", quantity("1", "0")),
                                 ("-1", quantity("10000000000000000", "0"))])
    assert result.value == 1
    assert result.absolute_error == 0


def test_unknown_error_survives_linear_combination():
    result = linear_combination([("1", quantity(native=None))])
    assert result.absolute_error is None
    assert assess(result, criterion(), places=1).disposition == "NOT_EVALUATED"


@pytest.mark.parametrize("value,places,expected", [
    ("1.25", 1, "1.2"), ("1.35", 1, "1.4"),
    ("-1.25", 1, "-1.2"), ("-1.35", 1, "-1.4"),
    ("0", 2, "0.00"), ("9.96", 1, "10.0"),
])
def test_nearest_even_display(value, places, expected):
    """Python 3.11 decimal ROUND_HALF_EVEN: nearest; ties to even."""
    assert render_fixed(Fraction(value), places) == expected


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity", 1.2, True, "1/3"])
def test_invalid_quantity_value(value):
    with pytest.raises((ValueError, TypeError)):
        assess(quantity(value), criterion(), places=1)


@pytest.mark.parametrize("error", ["-.1", "NaN", "Infinity", 0.1])
def test_invalid_bound(error):
    with pytest.raises((ValueError, TypeError)):
        assess(quantity(error=error), criterion(), places=1)


def test_invalid_comparison_and_mixed_units():
    with pytest.raises(ValueError, match="comparator"):
        assess(quantity(), criterion(comparator="<"), places=1)
    with pytest.raises(ValueError, match="unit"):
        assess(quantity(), criterion(unit="Pa"), places=1)
    with pytest.raises(ValueError, match="unit"):
        linear_combination([("1", quantity()), ("1", quantity(unit="Pa"))])
    with pytest.raises(ValueError, match="empty"):
        linear_combination([])


@pytest.mark.parametrize("places", [-1, True, 1.5])
def test_invalid_places(places):
    with pytest.raises((ValueError, TypeError)):
        assess(quantity(), criterion(), places=places)


def test_stage_bound_cannot_be_relabelled_as_accuracy():
    """Metadata retains a supplied representation without inferring a bound."""
    q = quantity(native=Stage("binary storage", "format description only", None))
    more_digits = replace(q, value="9.960000000000000000000000")
    assert assess(q, criterion(), places=1).disposition == "NOT_EVALUATED"
    assert assess(more_digits, criterion(), places=20).disposition == "NOT_EVALUATED"


def test_altered_linear_result_cannot_bypass_evidence():
    result = linear_combination([("1", quantity())])
    with pytest.raises(ValueError, match="retained terms"):
        assess(replace(result, absolute_error=Fraction(0)), criterion(), places=1)


def test_missing_criterion_unit_denies_acceptance():
    result = assess(quantity(), criterion(unit=""), places=1)
    assert result.disposition == "NOT_EVALUATED"
    assert "missing criterion unit" in result.reasons


def test_worked_example():
    """Independent expected values: 2*3-4=2; B=.2+.2=.4; bounds=8/5,12/5.

    The second example has 10.04>10 but nearest-even display 10.0, so FAIL.
    """
    import runpy
    from pathlib import Path

    example = Path(__file__).resolve().parents[1] / "examples/reporting/result_precision.py"
    module = runpy.run_path(str(example))
    result = module["worked_examples"]()
    assert result["linear"]["answer"] == {
        "value": "2", "lower": "8/5", "upper": "12/5", "display": "2.0",
        "disposition": "INDETERMINATE",
    }
    assert result["rounding"]["answer"] == {
        "display": "10.0", "disposition": "FAIL", "rounding_sensitive": True,
    }


def test_export_format_does_not_promote_native_storage():
    """Issue 3850's E25.16 counterexample: text width supplies no native bound."""
    q = quantity(native=Stage("declared native representation", "format only", None),
                 serialization=Stage("E25.16", "synthetic export declaration", "0"))
    result = assess(q, criterion(), places=16)
    assert result.disposition == "NOT_EVALUATED"
    assert result.result.terms[0][1].serialization.description == "E25.16"
    assert result.result.terms[0][1].native.absolute_error is None


def test_decimal_context_does_not_round_accumulation():
    """9.96 - 9.95 = .01 exactly, even with a one-digit Decimal context."""
    from decimal import localcontext

    with localcontext() as context:
        context.prec = 1
        result = linear_combination([("1", quantity("9.96", "0")),
                                     ("-1", quantity("9.95", "0"))])
        assert result.value == Fraction(1, 100)


def test_render_does_not_double_round():
    """1.249999 is below 1.25, hence nearest tenth is 1.2, never 1.3."""
    assert render_fixed(Fraction(1249999, 1000000), 1) == "1.2"


@pytest.mark.parametrize("field", ["value", "absolute_error"])
def test_linear_result_uses_recomputed_exact_types(field):
    """Float 10 equals rational 10; a manually rebuilt record cannot introduce floats."""
    result = linear_combination([("1", quantity("10", "0"))])
    replacement = 10.0 if field == "value" else 0.0
    assessment = assess(replace(result, **{field: replacement}), criterion(), places=1)
    assert isinstance(assessment.value, Fraction)
    assert isinstance(assessment.lower, Fraction)


@pytest.mark.parametrize("text", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_limits_and_weights_are_rejected(text):
    """A finite interval cannot qualify a non-finite threshold or weight."""
    with pytest.raises(ValueError, match="finite"):
        assess(quantity(), criterion(limit=text), places=1)
    with pytest.raises(ValueError, match="finite"):
        linear_combination([(text, quantity())])


def test_lower_limit_rounding_sensitivity():
    """9.96 < 10 fails a lower limit, though its one-place display is 10.0."""
    result = assess(quantity("9.96", "0"), criterion(comparator=">="), places=1)
    assert result.disposition == "FAIL"
    assert result.display == "10.0" and result.rounding_sensitive
