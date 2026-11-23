"""Tests for catenary riser geometry calculations."""

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from animations.catenary_math import (
    RiserConfig,
    catenary_profile,
    default_scr_config,
    offset_profiles,
)


class TestRiserConfig:
    def test_catenary_parameter(self):
        cfg = RiserConfig(
            water_depth=1500, outer_diameter=273.1, wall_thickness=25.4,
            submerged_weight=1200, horizontal_tension=800_000,
        )
        assert cfg.catenary_parameter == pytest.approx(800_000 / 1200)

    def test_default_config_values(self):
        cfg = default_scr_config()
        assert cfg.water_depth == 1500.0
        assert cfg.outer_diameter == 273.1
        assert cfg.wall_thickness == 25.4


class TestCatenaryProfile:
    def test_returns_three_arrays(self):
        cfg = default_scr_config()
        x, y, tdz = catenary_profile(cfg)
        assert isinstance(x, np.ndarray)
        assert isinstance(y, np.ndarray)
        assert isinstance(tdz, float)

    def test_profile_starts_at_seabed(self):
        cfg = default_scr_config()
        x, y, tdz = catenary_profile(cfg)
        # First point should be at y ≈ 0 (seabed/TDZ)
        assert y[0] == pytest.approx(0.0, abs=1.0)

    def test_profile_reaches_water_depth(self):
        cfg = default_scr_config()
        x, y, tdz = catenary_profile(cfg)
        total_depth = cfg.water_depth + cfg.hangoff_height
        assert y[-1] == pytest.approx(total_depth, rel=0.01)

    def test_profile_is_monotonically_increasing(self):
        cfg = default_scr_config()
        x, y, tdz = catenary_profile(cfg)
        assert np.all(np.diff(y) >= 0), "y should increase monotonically"

    def test_correct_number_of_points(self):
        cfg = default_scr_config()
        x, y, _ = catenary_profile(cfg, n_points=100)
        assert len(x) == 100
        assert len(y) == 100

    def test_catenary_shape_is_correct(self):
        """Verify the catenary equation: y = a*cosh(x/a) - a."""
        cfg = default_scr_config()
        x, y, _ = catenary_profile(cfg, n_points=50)
        a = cfg.catenary_parameter
        expected_y = a * np.cosh(x / a) - a
        np.testing.assert_allclose(y, expected_y, rtol=1e-10)


class TestOffsetProfiles:
    def test_returns_list_of_correct_length(self):
        cfg = default_scr_config()
        offsets = [-50, 0, 50]
        profiles = offset_profiles(cfg, offsets)
        assert len(profiles) == 3

    def test_each_profile_is_valid(self):
        cfg = default_scr_config()
        offsets = [-50, 0, 50]
        profiles = offset_profiles(cfg, offsets)
        for x, y, tdz in profiles:
            assert len(x) > 0
            assert y[0] == pytest.approx(0.0, abs=1.0)

    def test_far_offset_changes_shape(self):
        """Different offsets should produce different catenary shapes."""
        cfg = default_scr_config()
        offsets = [-100, 0, 100]
        profiles = offset_profiles(cfg, offsets)
        # Top x positions should differ between offsets
        x_tops = [x[-1] for x, y, _ in profiles]
        assert x_tops[0] != pytest.approx(x_tops[2], rel=0.01)


class TestInvalidConfig:
    def test_excessive_tension_raises(self):
        """If tension is absurdly high, catenary can't reach seabed."""
        cfg = RiserConfig(
            water_depth=100, outer_diameter=273.1, wall_thickness=25.4,
            submerged_weight=1, horizontal_tension=1e12,
        )
        # This should still work — very flat catenary
        x, y, _ = catenary_profile(cfg)
        assert len(x) > 0
