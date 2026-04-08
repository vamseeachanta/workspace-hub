"""Catenary riser geometry calculations for animation pipeline.

Computes steel catenary riser (SCR) shapes using the catenary equation
for different vessel offsets, identifying the touchdown zone (TDZ).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class RiserConfig:
    """Configuration for a steel catenary riser."""

    water_depth: float  # metres
    outer_diameter: float  # mm
    wall_thickness: float  # mm
    submerged_weight: float  # N/m (weight per unit length in water)
    horizontal_tension: float  # N (top tension horizontal component)
    hangoff_height: float = 20.0  # metres above waterline

    @property
    def catenary_parameter(self) -> float:
        """a = H / w — the catenary shape parameter."""
        return self.horizontal_tension / self.submerged_weight


def catenary_profile(
    config: RiserConfig,
    vessel_offset: float = 0.0,
    n_points: int = 200,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Compute the catenary riser profile.

    Returns (x_coords, y_coords, tdz_x) where:
    - x is horizontal distance from hangoff point
    - y is elevation (seabed = 0, upward positive)
    - tdz_x is the horizontal position of the touchdown zone
    """
    a = config.catenary_parameter
    total_depth = config.water_depth + config.hangoff_height

    # The catenary: y = a * cosh(x/a) - a
    # At hangoff: y_top = total_depth → solve for x_top
    # cosh(x_top/a) = (total_depth + a) / a
    cosh_val = (total_depth + a) / a
    if cosh_val < 1.0:
        raise ValueError("Invalid configuration: tension too high for water depth")
    x_top = a * math.acosh(cosh_val) + vessel_offset

    # TDZ is where catenary meets seabed (y=0), i.e., x=0 in catenary coords
    tdz_x = 0.0

    # Generate points from TDZ to hangoff
    x_cat = np.linspace(0, x_top, n_points)
    y_cat = a * np.cosh(x_cat / a) - a

    # Shift x so TDZ is at the correct horizontal position
    # The riser goes from hangoff (left) to TDZ (right on seabed)
    # Flip convention: x increases rightward from vessel
    return x_cat, y_cat, tdz_x


def offset_profiles(
    config: RiserConfig,
    offsets: list[float],
    n_points: int = 200,
) -> list[tuple[np.ndarray, np.ndarray, float]]:
    """Generate catenary profiles for multiple vessel offsets.

    Each offset shifts the top attachment point horizontally,
    resulting in different catenary shapes and TDZ positions.
    """
    profiles = []
    for offset in offsets:
        # Adjust horizontal tension for offset (simplified model)
        # Near offset: tension increases; far offset: tension decreases
        adjusted_config = RiserConfig(
            water_depth=config.water_depth,
            outer_diameter=config.outer_diameter,
            wall_thickness=config.wall_thickness,
            submerged_weight=config.submerged_weight,
            horizontal_tension=config.horizontal_tension * (1.0 + offset / 1000.0),
            hangoff_height=config.hangoff_height,
        )
        x, y, tdz = catenary_profile(adjusted_config, vessel_offset=0.0, n_points=n_points)
        profiles.append((x, y, tdz))
    return profiles


def default_scr_config() -> RiserConfig:
    """Representative SCR configuration based on fatigue-scr-touchdown.yaml.

    10.75" OD, 1" WT, 1500m water depth.
    """
    return RiserConfig(
        water_depth=1500.0,
        outer_diameter=273.1,
        wall_thickness=25.4,
        submerged_weight=1200.0,  # typical for 10.75" SCR
        horizontal_tension=800_000.0,  # ~800 kN
        hangoff_height=20.0,
    )
