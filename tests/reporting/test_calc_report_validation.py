"""TDD tests: validate calc report YAML outputs against existing Python implementations.

WRK-1188 Phase 4 AC4: Each calc report validated against existing Python code.
"""

import math
import sys
import os

import yaml

# Add digitalmodel to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../digitalmodel/src"))


def load_calc_report(name):
    path = os.path.join(os.path.dirname(__file__), f"../../examples/reporting/{name}")
    with open(path) as f:
        return yaml.safe_load(f)


def get_output(report, symbol):
    for out in report["outputs"]:
        if out["symbol"] == symbol:
            return out["value"]
    raise KeyError(f"Output {symbol} not found")


def get_input(report, symbol):
    for inp in report["inputs"]:
        if inp["symbol"] == symbol:
            return inp["value"]
    raise KeyError(f"Input {symbol} not found")


# ── DNV-RP-B401 Cathodic Protection ──


class TestB401CalcReport:
    """Validate cp-anode-design-dnv-rp-b401.yaml against digitalmodel CP module."""

    def setup_method(self):
        self.report = load_calc_report("cp-anode-design-dnv-rp-b401.yaml")
        from digitalmodel.cathodic_protection.dnv_rp_b401 import (
            coating_breakdown_factor,
            current_demand,
            anode_mass_requirement,
        )
        self.coating_breakdown_factor = coating_breakdown_factor
        self.current_demand = current_demand
        self.anode_mass_requirement = anode_mass_requirement

    def test_coating_breakdown_initial(self):
        """f_ci = a + b*0 = 0.02"""
        f_ci = self.coating_breakdown_factor(a=0.02, b=0.012, t_years=0)
        assert abs(f_ci - get_input(self.report, "f_ci")) < 0.001

    def test_coating_breakdown_mean(self):
        """f_cm = a + b*(t/2) = 0.02 + 0.012*12.5 = 0.17"""
        f_cm = self.coating_breakdown_factor(a=0.02, b=0.012, t_years=12.5)
        assert abs(f_cm - get_input(self.report, "f_cm")) < 0.001

    def test_coating_breakdown_final(self):
        """f_cf = a + b*t = 0.02 + 0.012*25 = 0.32"""
        f_cf = self.coating_breakdown_factor(a=0.02, b=0.012, t_years=25)
        assert abs(f_cf - get_input(self.report, "f_cf")) < 0.001

    def test_initial_current_demand(self):
        """I_ci = A_c * i_ci * f_ci = 5000 * 0.15 * 0.02 = 15.0 A"""
        I_ci = self.current_demand(
            surface_area_m2=get_input(self.report, "A_c"),
            current_density_A_m2=get_input(self.report, "i_ci"),
            breakdown_factor=get_input(self.report, "f_ci"),
        )
        assert abs(I_ci - get_output(self.report, "I_ci")) < 0.1

    def test_mean_current_demand(self):
        """I_cm = A_c * i_cm * f_cm = 5000 * 0.07 * 0.17 = 59.5 A"""
        I_cm = self.current_demand(
            surface_area_m2=get_input(self.report, "A_c"),
            current_density_A_m2=get_input(self.report, "i_cm"),
            breakdown_factor=get_input(self.report, "f_cm"),
        )
        assert abs(I_cm - get_output(self.report, "I_cm")) < 0.1

    def test_final_current_demand(self):
        """I_cf = A_c * i_cf * f_cf = 5000 * 0.10 * 0.32 = 160.0 A"""
        I_cf = self.current_demand(
            surface_area_m2=get_input(self.report, "A_c"),
            current_density_A_m2=get_input(self.report, "i_cf"),
            breakdown_factor=get_input(self.report, "f_cf"),
        )
        assert abs(I_cf - get_output(self.report, "I_cf")) < 0.5

    def test_total_anode_mass(self):
        """M_a = (I_cm * t_f * 8760) / (u_f * epsilon) = 7239.2 kg"""
        M_a = self.anode_mass_requirement(
            I_mean_A=get_output(self.report, "I_cm"),
            T_design_years=get_input(self.report, "t_f"),
            E_capacity=get_input(self.report, "epsilon"),
            u_f=get_input(self.report, "u_f"),
        )
        assert abs(M_a - get_output(self.report, "M_a")) < 1.0


# ── DNV-RP-F109 On-Bottom Stability ──


class TestF109CalcReport:
    """Validate on-bottom-stability-dnv-rp-f109.yaml against digitalmodel module."""

    def setup_method(self):
        self.report = load_calc_report("on-bottom-stability-dnv-rp-f109.yaml")
        from digitalmodel.geotechnical.on_bottom_stability import (
            drag_force_per_meter,
            lift_force_per_meter,
            inertia_force_per_meter,
        )
        self.drag_force = drag_force_per_meter
        self.lift_force = lift_force_per_meter
        self.inertia_force = inertia_force_per_meter

    def _total_od(self):
        D_steel = get_input(self.report, "D_{steel}")
        t_coat = get_input(self.report, "t_{coat}")
        return D_steel + 2 * t_coat

    def test_drag_force(self):
        """F_D = 0.5 * rho * C_D * D * U * |U|"""
        D_total = self._total_od()
        F_D = self.drag_force(
            current_velocity_ms=get_input(self.report, "U"),
            pipe_od_m=D_total,
            water_density_kg_m3=get_input(self.report, "\\rho_{sw}"),
            drag_coeff=get_input(self.report, "C_D"),
        )
        assert abs(F_D - get_output(self.report, "F_D")) < 1.0

    def test_lift_force(self):
        """F_L = 0.5 * rho * C_L * D * U^2"""
        D_total = self._total_od()
        F_L = self.lift_force(
            current_velocity_ms=get_input(self.report, "U"),
            pipe_od_m=D_total,
            water_density_kg_m3=get_input(self.report, "\\rho_{sw}"),
            lift_coeff=get_input(self.report, "C_L"),
        )
        assert abs(F_L - get_output(self.report, "F_L")) < 1.0

    def test_inertia_force(self):
        """F_I = rho * C_M * pi/4 * D^2 * a"""
        D_total = self._total_od()
        F_I = self.inertia_force(
            acceleration_ms2=get_input(self.report, "a"),
            pipe_od_m=D_total,
            water_density_kg_m3=get_input(self.report, "\\rho_{sw}"),
            inertia_coeff=get_input(self.report, "C_M"),
        )
        assert abs(F_I - get_output(self.report, "F_I")) < 1.0


# ── DNV-RP-C203 Fatigue S-N Curves ──


class TestC203CalcReport:
    """Validate fatigue-sn-curve-dnv-rp-c203.yaml against S-N curve computation."""

    def setup_method(self):
        self.report = load_calc_report("fatigue-sn-curve-dnv-rp-c203.yaml")

    def test_allowable_cycles(self):
        """log N = log(a) - m * log(S) for S-N curve D in air"""
        loga1 = get_input(self.report, "loga_1")
        m1 = get_input(self.report, "m_1")
        stress = get_input(self.report, "delta_sigma")
        log_N = loga1 - m1 * math.log10(stress)
        N = 10 ** log_N
        expected_N = get_output(self.report, "N")
        assert abs(N - expected_N) < 1000, f"N={N}, expected={expected_N}"

    def test_unfactored_damage(self):
        """D = n / N"""
        n = get_input(self.report, "n")
        N = get_output(self.report, "N")
        D = n / N
        expected_D = get_output(self.report, "D")
        assert abs(D - expected_D) < 0.01

    def test_factored_damage(self):
        """D_factored = D * DFF"""
        D = get_output(self.report, "D")
        DFF = get_input(self.report, "DFF")
        D_factored = D * DFF
        expected = get_output(self.report, "D_factored")
        assert abs(D_factored - expected) < 0.01

    def test_fatigue_limit_curve_d(self):
        """Fatigue limit for curve D = 52.63 MPa from Table 2-1"""
        sigma_fl = get_input(self.report, "sigma_fl")
        assert abs(sigma_fl - 52.63) < 0.01

    def test_sn_table_curve_d_params(self):
        """Verify Table 2-1 extracted data matches code constants"""
        # Check the data_tables section has curve D with correct values
        tables = self.report.get("data_tables", [])
        assert len(tables) > 0
        table = tables[0]
        # Find D row
        d_row = None
        for row in table["rows"]:
            if row[0] == "D":
                d_row = row
                break
        assert d_row is not None
        assert d_row[1] == 3.0  # m1
        assert d_row[2] == 12.164  # log(a1)
        assert d_row[3] == 15.606  # log(a2)
        assert d_row[4] == 52.63  # fatigue limit
        assert d_row[5] == 0.20  # k
