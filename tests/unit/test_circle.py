"""WRK-1002 gatepass TDD — calculate_circle correctness tests (written before implementation)."""
import math
import pytest
from src.geometry.circle import calculate_circle


def test_calculate_circle_area():
    result = calculate_circle(5)
    assert math.isclose(result["area"], math.pi * 25, rel_tol=1e-9)


def test_calculate_circle_circumference():
    result = calculate_circle(5)
    assert math.isclose(result["circumference"], 2 * math.pi * 5, rel_tol=1e-9)


def test_calculate_circle_zero_radius():
    result = calculate_circle(0)
    assert result["area"] == 0.0
    assert result["circumference"] == 0.0


def test_calculate_circle_returns_dict():
    result = calculate_circle(1)
    assert isinstance(result, dict)
    assert "area" in result
    assert "circumference" in result


def test_calculate_circle_unit_radius():
    result = calculate_circle(1)
    assert math.isclose(result["area"], math.pi, rel_tol=1e-9)
    assert math.isclose(result["circumference"], 2 * math.pi, rel_tol=1e-9)
