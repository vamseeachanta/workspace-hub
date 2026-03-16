"""Tests for formula_to_python — Excel formula → Python expression translator."""

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from scripts.data.doc_intelligence.formula_to_python import (
    can_translate,
    formula_to_function,
    formula_to_python,
    translate_simple_formulas,
)


class TestCanTranslate:
    def test_simple_arithmetic(self):
        assert can_translate("=A1+B1") is True

    def test_with_pi(self):
        assert can_translate("=PI()/4*A1^2") is True

    def test_with_sqrt(self):
        assert can_translate("=SQRT(A1)") is True

    def test_vlookup_blocked(self):
        assert can_translate("=VLOOKUP(A1,B:C,2,FALSE)") is False

    def test_if_blocked(self):
        assert can_translate("=IF(A1>0,B1,C1)") is False

    def test_concatenate_blocked(self):
        assert can_translate('=A1&" text"') is False

    def test_empty_formula(self):
        assert can_translate("") is False

    def test_no_equals(self):
        assert can_translate("just text") is False

    def test_lookup_blocked(self):
        assert can_translate("=LOOKUP(A1,B1:B10)") is False


class TestFormulaToPython:
    def test_simple_multiply(self):
        result = formula_to_python("=A1*B1")
        assert result == "a1*b1"

    def test_unit_conversion(self):
        # =E42 * 25.4/1000
        result = formula_to_python("=E42*25.4/1000")
        assert result == "e42*25.4/1000"

    def test_power_operator(self):
        # =A1^2 → a1**2
        result = formula_to_python("=A1^2")
        assert result == "a1**2"

    def test_pi_function(self):
        result = formula_to_python("=PI()/4*A1^2")
        assert "math.pi" in result
        assert "**2" in result

    def test_sqrt_function(self):
        result = formula_to_python("=SQRT(A1)")
        assert result == "math.sqrt(a1)"

    def test_complex_engineering(self):
        # =PI()/4 * ($G$42^2 - E44^2) * $E$36
        result = formula_to_python("=PI()/4*($G$42^2-E44^2)*$E$36")
        assert "math.pi" in result
        assert "g42" in result
        assert "e44" in result
        assert "e36" in result
        assert "**2" in result

    def test_dollar_signs_stripped(self):
        result = formula_to_python("=$A$1+$B$2")
        assert "$" not in result
        assert "a1" in result
        assert "b2" in result

    def test_var_map_substitution(self):
        result = formula_to_python(
            "=B2*B3",
            var_map={"B2": "diameter", "B3": "thickness"},
        )
        assert result == "diameter*thickness"

    def test_subtraction_with_parens(self):
        result = formula_to_python("=$G$42-(2*G43/1000)")
        assert "g42" in result
        assert "g43" in result

    def test_returns_none_for_complex(self):
        assert formula_to_python("=VLOOKUP(A1,B:C,2)") is None
        assert formula_to_python('=A1&" text"') is None

    def test_trig_functions(self):
        assert "math.sin" in formula_to_python("=SIN(A1)")
        assert "math.cos" in formula_to_python("=COS(A1)")

    def test_abs_function(self):
        assert formula_to_python("=ABS(A1-B1)") == "abs(a1-b1)"

    def test_nested_functions(self):
        result = formula_to_python("=SQRT(ABS(A1))")
        assert result == "math.sqrt(abs(a1))"


class TestFormulaToFunction:
    def test_simple_function(self):
        result = formula_to_function(
            name="calc_od_meters",
            formula="=E42*25.4/1000",
            input_refs=["E42"],
            var_map={"E42": "od_inches"},
            cached_value=0.9144,
        )
        assert "def calc_od_meters(od_inches: float) -> float:" in result
        assert "od_inches*25.4/1000" in result
        assert "pytest.approx(0.9144)" in result

    def test_returns_none_for_complex(self):
        result = formula_to_function(
            name="x", formula="=VLOOKUP(A1,B:C,2)", input_refs=["A1"]
        )
        assert result is None

    def test_multi_param(self):
        result = formula_to_function(
            name="inner_dia",
            formula="=$G$42-(2*G43/1000)",
            input_refs=["G42", "G43"],
            var_map={"G42": "od_m", "G43": "wt_mm"},
        )
        assert "od_m: float" in result
        assert "wt_mm: float" in result


class TestTranslateSimpleFormulas:
    def test_mixed_formulas(self):
        data = {
            "formulas": [
                {"cell_ref": "A1", "sheet": "S1", "formula": "=B1*2", "cached_value": 10},
                {"cell_ref": "A2", "sheet": "S1", "formula": "=VLOOKUP(B2,C:D,2)", "cached_value": "x"},
                {"cell_ref": "A3", "sheet": "S1", "formula": "=SQRT(B3)", "cached_value": 3.0},
            ]
        }
        result = translate_simple_formulas(data)
        assert result["stats"]["total"] == 3
        assert result["stats"]["translated"] == 2
        assert result["stats"]["skipped"] == 1
        assert result["stats"]["pct_translated"] == 66.7

    def test_empty(self):
        result = translate_simple_formulas({"formulas": []})
        assert result["stats"]["total"] == 0


class TestEvalTranslated:
    """Verify translated Python expressions produce correct numeric results."""

    def test_unit_conversion_eval(self):
        expr = formula_to_python("=E42*25.4/1000", {"E42": "od"})
        od = 36  # inches
        result = eval(expr)  # noqa: S307 — test-only
        assert result == pytest.approx(0.9144, rel=1e-6)

    def test_inner_diameter_eval(self):
        expr = formula_to_python("=$G$42-(2*G43/1000)", {"G42": "od_m", "G43": "wt_mm"})
        od_m = 0.9144
        wt_mm = 50.8
        result = eval(expr)  # noqa: S307
        assert result == pytest.approx(0.8128, rel=1e-6)

    def test_mass_per_length_eval(self):
        expr = formula_to_python(
            "=PI()/4*($G$42^2-E44^2)*$E$36",
            {"G42": "od_m", "E44": "id_m", "E36": "density"},
        )
        od_m = 0.9144
        id_m = 0.8128
        density = 7850
        result = eval(expr)  # noqa: S307
        assert result == pytest.approx(1081.9218093689772, rel=1e-4)
