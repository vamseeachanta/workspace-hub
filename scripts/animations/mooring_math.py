"""Mooring layout geometry and force calculations for animation pipeline.

Computes spread mooring arrangements (plan view + elevation), chain catenary
shapes, vessel excursion under environmental loading, and mooring line tensions.

Reference: API RP 2SK, DNV-OS-E301
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


@dataclass
class MooringLineConfig:
    """Configuration for a single mooring line."""

    azimuth_deg: float  # bearing from vessel centre (0 = bow, CW positive)
    length: float  # total line length in metres
    pretension: float  # pretension in kN
    mbl: float  # minimum breaking load in kN
    submerged_weight: float = 150.0  # N/m (chain weight in water)
    anchor_radius: float = 800.0  # m from vessel centre to anchor


@dataclass
class MooringConfig:
    """Full spread mooring configuration."""

    lines: list[MooringLineConfig] = field(default_factory=list)
    water_depth: float = 50.0  # metres
    vessel_length: float = 280.0  # metres (LNG carrier typical)
    vessel_beam: float = 46.0  # metres
    heading_deg: float = 0.0  # vessel heading (0 = north, CW positive)


@dataclass
class EnvironmentalLoad:
    """Environmental forces on moored vessel."""

    force_x: float  # kN (surge, positive = bow direction)
    force_y: float  # kN (sway, positive = starboard)
    moment_z: float = 0.0  # kN·m (yaw moment)
    label: str = ""


def default_spread_mooring(n_lines: int = 8) -> MooringConfig:
    """Create a representative spread mooring for an LNG carrier.

    8-point symmetric spread: 2 fore, 2 aft on each side.
    Typical of a permanent LNG terminal berth.
    """
    # Symmetric 8-line arrangement (4-2-2 pattern per side is typical,
    # but simplify to uniform 45-deg spacing for visual clarity)
    azimuths = [float(i * 360.0 / n_lines) for i in range(n_lines)]

    lines = [
        MooringLineConfig(
            azimuth_deg=az,
            length=900.0,
            pretension=200.0,  # kN
            mbl=3000.0,  # kN (typical for 76mm chain)
            submerged_weight=150.0,
            anchor_radius=800.0,
        )
        for az in azimuths
    ]

    return MooringConfig(
        lines=lines,
        water_depth=50.0,
        vessel_length=280.0,
        vessel_beam=46.0,
        heading_deg=0.0,
    )


def line_anchor_positions(config: MooringConfig) -> list[tuple[float, float]]:
    """Compute anchor positions (x, y) in metres relative to vessel centre.

    Uses vessel heading + line azimuth to find global anchor position.
    """
    anchors = []
    for line in config.lines:
        angle_rad = math.radians(config.heading_deg + line.azimuth_deg)
        ax = line.anchor_radius * math.sin(angle_rad)
        ay = line.anchor_radius * math.cos(angle_rad)
        anchors.append((ax, ay))
    return anchors


def chain_catenary_profile(
    horizontal_distance: float,
    water_depth: float,
    submerged_weight: float,
    n_points: int = 50,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute chain catenary elevation profile between fairlead and anchor.

    Returns (s_horiz, z_elev) arrays where s is horizontal distance from
    fairlead and z is elevation (0 = seabed, water_depth = surface).

    Simplified model: the chain hangs as a catenary from fairlead depth
    to the seabed, with grounded length on seabed.
    """
    if horizontal_distance <= 0:
        s = np.array([0.0])
        z = np.array([water_depth])
        return s, z

    # Catenary parameter: a = H / w where H = horizontal tension component
    # For display purposes, fit a catenary to the known endpoints
    # Fairlead at (0, water_depth), touchdown at (x_td, 0), anchor at (h_dist, 0)
    #
    # Use a parabolic approximation for visual clarity (close to catenary for
    # moderate sag)
    x_td = horizontal_distance * 0.7  # approx grounded length ratio
    suspended_length = horizontal_distance * 0.7

    s_suspended = np.linspace(0, suspended_length, n_points)
    # Parabolic approximation: z = water_depth * (1 - (s/L)^2)
    z_suspended = water_depth * (1.0 - (s_suspended / suspended_length) ** 2)
    z_suspended = np.maximum(z_suspended, 0.0)

    # Grounded portion on seabed
    s_grounded = np.linspace(suspended_length, horizontal_distance, max(n_points // 4, 5))
    z_grounded = np.zeros_like(s_grounded)

    s = np.concatenate([s_suspended, s_grounded[1:]])
    z = np.concatenate([z_suspended, z_grounded[1:]])

    return s, z


def compute_excursion(
    config: MooringConfig,
    load: EnvironmentalLoad,
    stiffness_kn_per_m: float = 50.0,
) -> tuple[float, float]:
    """Estimate vessel excursion (dx, dy) under environmental load.

    Simplified linear model: displacement = force / total_stiffness.
    Real analysis uses iterative catenary solutions (API RP 2SK).

    Returns (dx, dy) in metres.
    """
    # Total restoring stiffness from all lines (simplified uniform)
    n = len(config.lines)
    total_stiffness = stiffness_kn_per_m * n

    dx = load.force_x / total_stiffness if total_stiffness > 0 else 0.0
    dy = load.force_y / total_stiffness if total_stiffness > 0 else 0.0

    return dx, dy


def compute_line_tensions(
    config: MooringConfig,
    vessel_offset: tuple[float, float] = (0.0, 0.0),
) -> list[float]:
    """Compute mooring line tensions given vessel offset.

    Simplified model: tension increases linearly with elongation.
    Lines toward the offset direction increase in tension,
    lines away decrease.

    Returns list of tensions in kN (one per line).
    """
    dx, dy = vessel_offset
    tensions = []

    for line in config.lines:
        angle_rad = math.radians(config.heading_deg + line.azimuth_deg)
        # Project vessel offset onto line direction
        line_dir_x = math.sin(angle_rad)
        line_dir_y = math.cos(angle_rad)

        # Elongation component: positive if vessel moves away from anchor
        elongation = -(dx * line_dir_x + dy * line_dir_y)

        # Simplified stiffness: tension = pretension + k * elongation
        # k chosen so that MBL is reached at ~10% of anchor radius
        k = (line.mbl - line.pretension) / (0.10 * line.anchor_radius)
        tension = max(0.0, line.pretension + k * elongation)

        tensions.append(tension)

    return tensions


def max_utilisation(tensions: list[float], config: MooringConfig) -> float:
    """Maximum line tension utilisation (tension / MBL)."""
    if not tensions or not config.lines:
        return 0.0
    utilisations = [t / line.mbl for t, line in zip(tensions, config.lines)]
    return max(utilisations)


def excursion_envelope(
    config: MooringConfig,
    load_magnitudes: list[float],
    n_directions: int = 36,
    stiffness_kn_per_m: float = 50.0,
) -> list[list[tuple[float, float]]]:
    """Compute excursion envelopes for multiple load magnitudes.

    Returns a list of envelopes, each being a list of (x, y) points
    forming a closed curve.
    """
    envelopes = []
    angles = np.linspace(0, 2 * math.pi, n_directions, endpoint=False)

    for mag in load_magnitudes:
        points = []
        for angle in angles:
            load = EnvironmentalLoad(
                force_x=mag * math.cos(angle),
                force_y=mag * math.sin(angle),
            )
            dx, dy = compute_excursion(config, load, stiffness_kn_per_m)
            points.append((dx, dy))
        points.append(points[0])  # close the envelope
        envelopes.append(points)

    return envelopes
