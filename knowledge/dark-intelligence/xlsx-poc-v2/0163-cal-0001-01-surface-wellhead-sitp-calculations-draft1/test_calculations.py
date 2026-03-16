"""Auto-generated tests for 0163-cal-0001-01-surface-wellhead-sitp-calculations-draft1 calculations.

Baseline tests use cached Excel values.
Parametric tests exercise 10 input variations.
"""

import pytest
import math


class Test_calc_000_baseline:
    """Baseline: calc_000 from =D16*0.3048"""

    def test_calc_000_cached_d17(self):
        # Excel cached value for D17
        expected = 2133.6
        # TODO: wire to calc_000() call
        assert expected == pytest.approx(2133.6)


class Test_calc_000_parametric:
    """Parametric variation tests for calc_000."""

    @pytest.mark.parametrize(
        "variation_name, scale_factors",
        [
            ("nominal", [1.0, 1.0, 1.0, 1.0]),
            ("all_min", [0.5, 0.5, 0.5, 0.5]),
            ("all_max", [2.0, 2.0, 2.0, 2.0]),
            ("one_at_a_time_low", [0.5, 1.0, 1.0, 1.0]),
            ("one_at_a_time_high", [2.0, 1.0, 1.0, 1.0]),
            ("stress_high", [3.0, 3.0, 3.0, 3.0]),
            ("near_zero", [0.01, 0.01, 0.01, 0.01]),
            ("large_values", [100.0, 100.0, 100.0, 100.0]),
            ("negative", [-1.0, -1.0, -1.0, -1.0]),
            ("random_seed_42", [1.42, 1.42, 1.42, 1.42]),
        ],
    )
    def test_calc_000_variation(
        self, variation_name, scale_factors
    ):
        # Apply scale_factors to nominal inputs
        # TODO: wire to calc_000() with scaled inputs
        assert isinstance(scale_factors, list)


class Test_calc_001_baseline:
    """Baseline: calc_001 from =(-(D18*D19*D17+D15)*2)/D18"""

    def test_calc_001_cached_c46(self):
        # Excel cached value for C46
        expected = -41891.232
        # TODO: wire to calc_001() call
        assert expected == pytest.approx(-41891.232)


class Test_calc_001_parametric:
    """Parametric variation tests for calc_001."""

    @pytest.mark.parametrize(
        "variation_name, scale_factors",
        [
            ("nominal", [1.0, 1.0, 1.0, 1.0]),
            ("all_min", [0.5, 0.5, 0.5, 0.5]),
            ("all_max", [2.0, 2.0, 2.0, 2.0]),
            ("one_at_a_time_low", [0.5, 1.0, 1.0, 1.0]),
            ("one_at_a_time_high", [2.0, 1.0, 1.0, 1.0]),
            ("stress_high", [3.0, 3.0, 3.0, 3.0]),
            ("near_zero", [0.01, 0.01, 0.01, 0.01]),
            ("large_values", [100.0, 100.0, 100.0, 100.0]),
            ("negative", [-1.0, -1.0, -1.0, -1.0]),
            ("random_seed_42", [1.42, 1.42, 1.42, 1.42]),
        ],
    )
    def test_calc_001_variation(
        self, variation_name, scale_factors
    ):
        # Apply scale_factors to nominal inputs
        # TODO: wire to calc_001() with scaled inputs
        assert isinstance(scale_factors, list)


class Test_calc_002_parametric:
    """Parametric variation tests for calc_002."""

    @pytest.mark.parametrize(
        "variation_name, scale_factors",
        [
            ("nominal", [1.0, 1.0, 1.0, 1.0]),
            ("all_min", [0.5, 0.5, 0.5, 0.5]),
            ("all_max", [2.0, 2.0, 2.0, 2.0]),
            ("one_at_a_time_low", [0.5, 1.0, 1.0, 1.0]),
            ("one_at_a_time_high", [2.0, 1.0, 1.0, 1.0]),
            ("stress_high", [3.0, 3.0, 3.0, 3.0]),
            ("near_zero", [0.01, 0.01, 0.01, 0.01]),
            ("large_values", [100.0, 100.0, 100.0, 100.0]),
            ("negative", [-1.0, -1.0, -1.0, -1.0]),
            ("random_seed_42", [1.42, 1.42, 1.42, 1.42]),
        ],
    )
    def test_calc_002_variation(
        self, variation_name, scale_factors
    ):
        # Apply scale_factors to nominal inputs
        # TODO: wire to calc_002() with scaled inputs
        assert isinstance(scale_factors, list)

