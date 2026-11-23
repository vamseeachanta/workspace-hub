"""Pile axial capacity in clay — alpha method per API RP 2GEO Sec 7.3.

Extracted from dark intelligence archive:
  knowledge/dark-intelligence/geotechnical/pile_capacity/
  dark-intelligence-api-rp-2geo-alpha-method.yaml
"""

import math


def compute_alpha(su_kpa: float, sigma_v_eff_kpa: float) -> float:
    """Alpha adhesion factor: alpha = 0.5 * (Su / sigma_v')^(-0.5).

    Valid for Su/sigma_v' <= 1.0 per API RP 2GEO Sec 7.3.
    """
    psi = su_kpa / sigma_v_eff_kpa
    return 0.5 * psi ** (-0.5)


def compute_unit_skin_friction(su_kpa: float, sigma_v_eff_kpa: float) -> float:
    """Unit skin friction: f = alpha * Su."""
    alpha = compute_alpha(su_kpa, sigma_v_eff_kpa)
    return alpha * su_kpa


def compute_skin_friction_capacity(
    pile_diameter_m: float,
    pile_length_m: float,
    su_kpa: float,
    sigma_v_eff_kpa: float,
) -> float:
    """Total skin friction: Qf = pi * D * f * L (kN)."""
    f = compute_unit_skin_friction(su_kpa, sigma_v_eff_kpa)
    return math.pi * pile_diameter_m * f * pile_length_m


def compute_end_bearing_capacity(
    pile_diameter_m: float,
    su_kpa: float,
    nc: float = 9.0,
) -> float:
    """End bearing: Qp = Nc * Su * Ap (kN), where Ap = pi/4 * D^2."""
    ap = math.pi / 4.0 * pile_diameter_m ** 2
    return nc * su_kpa * ap


def compute_total_axial_capacity(
    pile_diameter_m: float,
    pile_length_m: float,
    su_kpa: float,
    sigma_v_eff_kpa: float,
    nc: float = 9.0,
) -> float:
    """Total axial capacity: Q = Qf + Qp (kN)."""
    qf = compute_skin_friction_capacity(pile_diameter_m, pile_length_m, su_kpa, sigma_v_eff_kpa)
    qp = compute_end_bearing_capacity(pile_diameter_m, su_kpa, nc)
    return qf + qp
