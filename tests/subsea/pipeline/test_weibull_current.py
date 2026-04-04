"""
Tests for Weibull current profile fitting (DNV-RP-F105 Sec 3.3).

Verifies the piecewise Weibull extrapolation for current speed vs
exceedance probability, used to derive design current speeds at
arbitrary return periods.
"""
import math
import pytest
import numpy as np

from digitalmodel.subsea.pipeline.free_span.weibull_current import (
    fit_weibull_current,
    extrapolate_current,
    WeibullFitResult,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_current_data():
    """Standard 5-bin current distribution (GOM-typical)."""
    speeds = [0.04, 0.20, 0.40, 0.60, 1.00]
    occurrence = [0.80, 0.10, 0.05, 0.04, 0.01]
    cum = np.cumsum(occurrence)
    exceedance = list(np.round(1e8 * (1 - cum)) / 1e8)
    return speeds, exceedance


@pytest.fixture
def two_point_data():
    """Minimal 2-point dataset for edge case testing."""
    return [0.5, 1.0], [0.10, 0.01]


# ---------------------------------------------------------------------------
# fit_weibull_current tests
# ---------------------------------------------------------------------------

class TestFitWeibullCurrent:

    def test_returns_weibull_result(self, sample_current_data):
        speeds, exc = sample_current_data
        result = fit_weibull_current(exc, speeds)
        assert isinstance(result, WeibullFitResult)

    def test_k_upper_positive(self, sample_current_data):
        speeds, exc = sample_current_data
        result = fit_weibull_current(exc, speeds)
        assert result.k_upper > 0

    def test_k_lower_positive(self, sample_current_data):
        speeds, exc = sample_current_data
        result = fit_weibull_current(exc, speeds)
        assert result.k_lower > 0

    def test_stores_filtered_data(self, sample_current_data):
        """Fit stores only valid (P > 0) data points."""
        speeds, exc = sample_current_data
        result = fit_weibull_current(exc, speeds)
        # Zero-exceedance entries are filtered out
        valid_speeds = [s for s, p in zip(speeds, exc) if p > 0]
        valid_exc = [p for p in exc if p > 0]
        assert result.current_speeds == valid_speeds
        assert result.exceedance_probs == valid_exc

    def test_two_points_works(self, two_point_data):
        speeds, exc = two_point_data
        result = fit_weibull_current(exc, speeds)
        assert result.k_upper != 0
        assert result.k_lower != 0

    def test_raises_single_point(self):
        with pytest.raises(ValueError, match="At least 2"):
            fit_weibull_current([0.1], [0.5])

    def test_raises_length_mismatch(self):
        with pytest.raises(ValueError, match="Length mismatch"):
            fit_weibull_current([0.1, 0.01], [0.5])

    def test_raises_empty_input(self):
        with pytest.raises(ValueError):
            fit_weibull_current([], [])


# ---------------------------------------------------------------------------
# extrapolate_current tests
# ---------------------------------------------------------------------------

class TestExtrapolateCurrent:

    def test_scalar_output(self, sample_current_data):
        speeds, exc = sample_current_data
        result = extrapolate_current(exc, speeds, 0.005)
        assert isinstance(result, float)

    def test_list_output(self, sample_current_data):
        speeds, exc = sample_current_data
        result = extrapolate_current(exc, speeds, [0.01, 0.005])
        assert isinstance(result, list)
        assert len(result) == 2

    def test_100yr_exceeds_observed_max(self, sample_current_data):
        """100-year current should exceed the maximum observed speed."""
        speeds, exc = sample_current_data
        p_100yr = 24 / (24 * 365.25 * 100)
        u_100yr = extrapolate_current(exc, speeds, p_100yr)
        assert u_100yr > max(speeds)

    def test_1yr_less_than_100yr(self, sample_current_data):
        speeds, exc = sample_current_data
        p_1yr = 24 / (24 * 365.25 * 1)
        p_100yr = 24 / (24 * 365.25 * 100)
        u_1yr = extrapolate_current(exc, speeds, p_1yr)
        u_100yr = extrapolate_current(exc, speeds, p_100yr)
        assert u_1yr < u_100yr

    def test_monotonic_extrapolation(self, sample_current_data):
        """Current must increase as exceedance probability decreases."""
        speeds, exc = sample_current_data
        probs = [0.15, 0.10, 0.05, 0.01, 0.005, 0.001, 0.0001]
        results = extrapolate_current(exc, speeds, probs)
        for i in range(len(results) - 1):
            assert results[i] <= results[i + 1] + 1e-10

    def test_physical_range(self, sample_current_data):
        """Extrapolated currents should be physically reasonable (< 5 m/s)."""
        speeds, exc = sample_current_data
        p_1000yr = 24 / (24 * 365.25 * 1000)
        u_1000yr = extrapolate_current(exc, speeds, p_1000yr)
        assert 0 < u_1000yr < 5.0, f"1000-yr current {u_1000yr:.2f} m/s unreasonable"

    def test_two_point_extrapolation(self, two_point_data):
        speeds, exc = two_point_data
        u = extrapolate_current(exc, speeds, 0.001)
        assert u > max(speeds)

    def test_raises_on_prob_zero(self, sample_current_data):
        speeds, exc = sample_current_data
        with pytest.raises(ValueError, match="must be in"):
            extrapolate_current(exc, speeds, 0.0)

    def test_raises_on_prob_one(self, sample_current_data):
        speeds, exc = sample_current_data
        with pytest.raises(ValueError, match="must be in"):
            extrapolate_current(exc, speeds, 1.0)


# ---------------------------------------------------------------------------
# Return period convenience tests
# ---------------------------------------------------------------------------

class TestReturnPeriods:
    """Tests using standard return period conversions."""

    @pytest.mark.parametrize("return_years", [1, 10, 100])
    def test_return_period_positive_current(self, sample_current_data, return_years):
        speeds, exc = sample_current_data
        T_hours = 24
        p_exc = T_hours / (24 * 365.25 * return_years)
        u = extrapolate_current(exc, speeds, p_exc)
        assert u > 0

    def test_longer_return_gives_higher_current(self, sample_current_data):
        speeds, exc = sample_current_data
        T_hours = 24
        u_values = []
        for years in [1, 10, 50, 100, 500]:
            p = T_hours / (24 * 365.25 * years)
            u_values.append(extrapolate_current(exc, speeds, p))
        for i in range(len(u_values) - 1):
            assert u_values[i] <= u_values[i + 1]
