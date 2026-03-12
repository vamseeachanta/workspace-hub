YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
Here are the complete pytest modules for the calculations files to fill the test coverage gaps. I have strictly followed your instructions to cover happy paths, edge cases, and error cases for all public functions, and skipped the devtools CLI files as they require complex filesystem mocking and do not contain simple numeric computations.

### `tests/calculations/test_casing_pipe.py`
```python
import pytest
import math
from assetutilities.calculations.casing_pipe import (
    CasingPipeProperties,
    PipeGrade,
    CasingPipeRatings,
    burst_pressure_rating,
    collapse_pressure_rating,
    axial_tensile_yield_strength,
    wall_thickness_for_design_pressure,
    temperature_derating_factor,
    rate_casing_pipe,
)

class TestCasingPipeCalculations:
    @pytest.fixture
    def sample_pipe(self):
        return CasingPipeProperties(od_in=9.625, wall_thickness_in=0.472, grade=PipeGrade.N80)

    def test_burst_pressure_rating_happy_path(self, sample_pipe):
        # Barlow: 0.875 * 2 * 80000 * 0.472 / 9.625 = 6865.4545
        result = burst_pressure_rating(sample_pipe)
        assert result == pytest.approx(6865.4545, rel=1e-4)

    def test_burst_pressure_rating_zero_thickness_returns_zero(self):
        pipe = CasingPipeProperties(od_in=9.625, wall_thickness_in=0.0, grade=PipeGrade.N80)
        result = burst_pressure_rating(pipe)
        assert result == 0.0

    def test_burst_pressure_rating_zero_od_raises_zero_division(self):
        pipe = CasingPipeProperties(od_in=0.0, wall_thickness_in=0.472, grade=PipeGrade.N80)
        with pytest.raises(ZeroDivisionError):
            burst_pressure_rating(pipe)

    def test_axial_tensile_yield_strength_happy_path(self, sample_pipe):
        # Area = pi/4 * (OD^2 - ID^2) = pi/4 * (9.625^2 - 8.681^2) = 13.57 in2
        # Yield force = 80000 * 13.57 = 1085600 lbf
        result = axial_tensile_yield_strength(sample_pipe)
        assert result == pytest.approx(1085606.3, rel=1e-4)

    def test_collapse_pressure_rating_happy_path(self, sample_pipe):
        # N80, D/t = 20.39 falls into Transitional or Plastic regime
        result = collapse_pressure_rating(sample_pipe)
        assert result > 0.0

    def test_wall_thickness_for_design_pressure_happy_path(self):
        result = wall_thickness_for_design_pressure(od_in=9.625, design_pressure_psi=6865.0, grade=PipeGrade.N80)
        assert result == pytest.approx(0.472, rel=1e-3)

    def test_temperature_derating_factor_ambient_returns_one(self):
        assert temperature_derating_factor(70.0) == 1.0
        assert temperature_derating_factor(200.0) == 1.0

    def test_temperature_derating_factor_elevated_linearly_interpolates(self):
        assert temperature_derating_factor(300.0) == pytest.approx(0.97)

    def test_temperature_derating_factor_extreme_capped_at_minimum(self):
        assert temperature_derating_factor(5000.0) == 0.01

    def test_rate_casing_pipe_happy_path_applies_derating(self, sample_pipe):
        ratings = rate_casing_pipe(sample_pipe, temperature_f=300.0)
        assert isinstance(ratings, CasingPipeRatings)
        assert ratings.temperature_f == 300.0
        assert ratings.derating_factor == pytest.approx(0.97)
        assert ratings.burst_psi == pytest.approx(6865.4545 * 0.97, rel=1e-4)
```

### `tests/calculations/test_drilling_riser_integrity.py`
```python
import pytest
from assetutilities.calculations.drilling_riser_integrity import (
    riser_effective_tension,
    riser_collapse_pressure,
    minimum_top_tension,
    tensile_utilization,
    bending_moment_from_offset,
    combined_loading_utilization,
    annual_fatigue_damage,
)

class TestDrillingRiserIntegrity:
    def test_riser_effective_tension_happy_path(self):
        result = riser_effective_tension(t_top=1000.0, w_sub=10.0, z=50.0)
        assert result == 500.0

    def test_riser_effective_tension_zero_depth(self):
        result = riser_effective_tension(t_top=1000.0, w_sub=10.0, z=0.0)
        assert result == 1000.0

    def test_riser_collapse_pressure_happy_path(self):
        result = riser_collapse_pressure(E=2e11, t=0.02, D=0.5, nu=0.3)
        assert result == pytest.approx(28131868.13, rel=1e-4)

    def test_riser_collapse_pressure_zero_diameter_raises_error(self):
        with pytest.raises(ZeroDivisionError):
            riser_collapse_pressure(E=2e11, t=0.02, D=0.0, nu=0.3)

    def test_minimum_top_tension_happy_path(self):
        result = minimum_top_tension(w_sub=10.0, L=100.0, bop_weight=500.0, safety_factor=1.2)
        assert result == 1800.0

    def test_tensile_utilization_happy_path(self):
        result = tensile_utilization(t_eff=500.0, a_steel=0.1, f_y=2e8)
        assert result == 2.5e-5

    def test_tensile_utilization_zero_area_raises_error(self):
        with pytest.raises(ZeroDivisionError):
            tensile_utilization(t_eff=500.0, a_steel=0.0, f_y=2e8)

    def test_bending_moment_from_offset_happy_path(self):
        result = bending_moment_from_offset(t_eff=1000.0, delta=2.0)
        assert result == 2000.0

    def test_combined_loading_utilization_happy_path(self):
        result = combined_loading_utilization(t_eff=500.0, t_allow=1000.0, M=200.0, M_allow=1000.0)
        assert result == 0.7

    def test_annual_fatigue_damage_happy_path(self):
        sea_states = [{"n_cycles": 1000, "N_f": 10000}, {"n_cycles": 500, "N_f": 5000}]
        result = annual_fatigue_damage(sea_states)
        assert result == 0.2
        
    def test_annual_fatigue_damage_empty_list_returns_zero(self):
        result = annual_fatigue_damage([])
        assert result == 0.0
```

### `tests/calculations/test_drilling_riser.py`
```python
import pytest
from assetutilities.calculations.drilling_riser import (
    gardner_bottom_tension,
    gardner_top_tension,
    kim_natural_frequency_with_pressure,
    grant_faired_drag_coefficient,
    jacobsen_suppression_damage_ratio,
    dsouza_flex_riser_effective_weight,
    vandiver_lock_in_velocity,
    miller_mud_column_pressure,
    imas_scr_response_amplification,
    berner_riser_effective_tension,
)

class TestDrillingRiser:
    def test_gardner_bottom_tension_happy_path(self):
        result = gardner_bottom_tension(w_air_lbf_per_ft=100.0, w_buoyancy_lbf_per_ft=40.0, length_ft=1000.0, bop_weight_lbf=10000.0)
        assert result == 50000.0

    def test_gardner_top_tension_happy_path(self):
        result = gardner_top_tension(bottom_tension_lbf=50000.0, segment_weights_lbf=[10000.0, 20000.0])
        assert result == 80000.0

    def test_kim_natural_frequency_with_pressure_happy_path(self):
        result = kim_natural_frequency_with_pressure(
            fn_vacuum_hz=0.5, internal_pressure_psi=1000.0, external_pressure_psi=2000.0,
            pipe_cross_section_in2=10.0, riser_length_ft=1000.0, riser_weight_lbf=100000.0
        )
        assert result > 0.5

    def test_kim_natural_frequency_zero_weight_returns_vacuum_freq(self):
        result = kim_natural_frequency_with_pressure(
            fn_vacuum_hz=0.5, internal_pressure_psi=1000.0, external_pressure_psi=2000.0,
            pipe_cross_section_in2=10.0, riser_length_ft=1000.0, riser_weight_lbf=0.0
        )
        assert result == 0.5

    def test_grant_faired_drag_coefficient_happy_path(self):
        result = grant_faired_drag_coefficient(cd_bare=1.2, reduction_factor=0.7)
        assert result == pytest.approx(0.84)

    def test_grant_faired_drag_coefficient_invalid_cd_raises_error(self):
        with pytest.raises(ValueError, match="must be non-negative"):
            grant_faired_drag_coefficient(cd_bare=-1.0)

    def test_jacobsen_suppression_damage_ratio_happy_path(self):
        result = jacobsen_suppression_damage_ratio(unsuppressed_damage=0.5, suppression_effectiveness=0.8)
        assert result == pytest.approx(0.1)

    def test_dsouza_flex_riser_effective_weight_happy_path(self):
        result = dsouza_flex_riser_effective_weight(weight_in_air_lbf_per_ft=100.0, displaced_fluid_weight_lbf_per_ft=40.0)
        assert result == 60.0

    def test_vandiver_lock_in_velocity_happy_path(self):
        result = vandiver_lock_in_velocity(natural_frequency_hz=0.2, diameter_ft=2.0, strouhal_number=0.2)
        assert result == 2.0

    def test_vandiver_lock_in_velocity_invalid_strouhal_raises_error(self):
        with pytest.raises(ValueError, match="must be positive"):
            vandiver_lock_in_velocity(natural_frequency_hz=0.2, diameter_ft=2.0, strouhal_number=0.0)

    def test_miller_mud_column_pressure_happy_path(self):
        result = miller_mud_column_pressure(mud_weight_ppg=10.0, depth_ft=1000.0)
        assert result == pytest.approx(520.0)

    def test_miller_mud_column_pressure_negative_depth_raises_error(self):
        with pytest.raises(ValueError, match="must be non-negative"):
            miller_mud_column_pressure(mud_weight_ppg=10.0, depth_ft=-1000.0)

    def test_imas_scr_response_amplification_happy_path(self):
        result = imas_scr_response_amplification(current_velocity=2.0, A=1.5, B=2.0)
        assert result == 6.0

    def test_berner_riser_effective_tension_happy_path(self):
        result = berner_riser_effective_tension(
            top_tension_lbf=100000.0, submerged_weight_lbf_per_ft=50.0,
            riser_length_ft=1000.0, vessel_offset_tension_delta_lbf=5000.0
        )
        assert result == 55000.0
```

### `tests/calculations/test_lifecycle_cost.py`
```python
import pytest
from assetutilities.calculations.lifecycle_cost import (
    net_present_value,
    levelized_cost,
    annual_equivalent_cost,
    maintenance_cost_mtbf,
    marine_transport_cost,
    effective_transit_days,
    total_installed_cost,
)

class TestLifecycleCost:
    def test_net_present_value_happy_path(self):
        result = net_present_value(costs=[100.0, 110.0, 121.0], discount_rate=0.1)
        assert result == pytest.approx(300.0)

    def test_net_present_value_empty_list_returns_zero(self):
        result = net_present_value(costs=[], discount_rate=0.1)
        assert result == 0.0

    def test_levelized_cost_happy_path(self):
        result = levelized_cost(costs=[100.0, 110.0], outputs=[10.0, 11.0], discount_rate=0.1)
        assert result == pytest.approx(10.0)

    def test_levelized_cost_zero_output_raises_error(self):
        with pytest.raises(ZeroDivisionError):
            levelized_cost(costs=[100.0, 110.0], outputs=[0.0, 0.0], discount_rate=0.1)

    def test_annual_equivalent_cost_happy_path(self):
        result = annual_equivalent_cost(npv=1000.0, discount_rate=0.1, life_years=10)
        assert result == pytest.approx(162.745, rel=1e-3)

    def test_annual_equivalent_cost_zero_discount_raises_error(self):
        with pytest.raises(ZeroDivisionError):
            annual_equivalent_cost(npv=1000.0, discount_rate=0.0, life_years=10)

    def test_maintenance_cost_mtbf_happy_path(self):
        result = maintenance_cost_mtbf(cost_per_event=5000.0, mtbf_years=5.0, years=20.0)
        assert result == 20000.0

    def test_marine_transport_cost_happy_path(self):
        result = marine_transport_cost(mobilization=10000.0, transit_day_rate=5000.0, transit_days=10.0, demobilization=5000.0)
        assert result == 65000.0

    def test_effective_transit_days_happy_path(self):
        result = effective_transit_days(nominal_days=10.0, downtime_fraction=0.2)
        assert result == 12.5

    def test_effective_transit_days_invalid_fraction_raises_error(self):
        with pytest.raises(ValueError, match="must be in \\[0, 1\\)"):
            effective_transit_days(nominal_days=10.0, downtime_fraction=1.0)

    def test_total_installed_cost_happy_path(self):
        result = total_installed_cost(equipment=1000.0, transport=200.0, installation=300.0, commissioning=100.0, contingency=50.0)
        assert result == 1650.0
```

### `tests/calculations/test_pipeline_dnv.py`
```python
import pytest
from assetutilities.calculations.pipeline_dnv import (
    burst_pressure_capacity,
    pressure_containment_check,
    local_buckling_combined_loading,
    von_mises_equivalent_stress,
    buckle_arrest_capacity,
)

class TestPipelineDnv:
    def test_burst_pressure_capacity_happy_path(self):
        result = burst_pressure_capacity(D=0.5, t=0.02, f_y=450e6, f_u=535e6)
        assert result > 0.0

    def test_burst_pressure_capacity_zero_diameter_raises_error(self):
        with pytest.raises(ZeroDivisionError):
            burst_pressure_capacity(D=0.0, t=0.02, f_y=450e6, f_u=535e6)

    def test_pressure_containment_check_happy_path(self):
        result = pressure_containment_check(P_li=1e7, D=0.5, t=0.02, f_y=450e6, f_u=535e6)
        assert result > 0.0

    def test_pressure_containment_check_zero_capacity_raises_error(self):
        with pytest.raises(ZeroDivisionError):
            pressure_containment_check(P_li=1e7, D=0.5, t=0.0, f_y=450e6, f_u=535e6)

    def test_local_buckling_combined_loading_happy_path(self):
        result = local_buckling_combined_loading(D=0.5, t=0.02, f_y=450e6, M=1e5, S=1e6, delta_p=1e6)
        assert result > 0.0

    def test_von_mises_equivalent_stress_happy_path(self):
        result = von_mises_equivalent_stress(sigma_l=100.0, sigma_h=50.0, tau=25.0)
        assert result == pytest.approx(96.82, rel=1e-3)

    def test_buckle_arrest_capacity_happy_path(self):
        result = buckle_arrest_capacity(D=0.5, t=0.02, f_y=450e6)
        assert result > 0.0

    def test_buckle_arrest_capacity_zero_diameter_raises_error(self):
        with pytest.raises(ZeroDivisionError):
            buckle_arrest_capacity(D=0.0, t=0.02, f_y=450e6)
```

### `tests/calculations/test_polynomial.py`
```python
import pytest
from assetutilities.calculations.polynomial import Polynomial

class TestPolynomial:
    def test_evaluate_polynomial_valid_inputs_returns_none_as_stub(self):
        poly = Polynomial()
        # Since the function is a stub with 'pass', it implicitly returns None.
        result = poly.evaluate_polynomial(2.0)
        assert result is None

    def test_evaluate_polynomial_with_different_types_returns_none(self):
        poly = Polynomial()
        result = poly.evaluate_polynomial("some_var")
        assert result is None

    def test_evaluate_polynomial_missing_argument_raises_type_error(self):
        poly = Polynomial()
        with pytest.raises(TypeError):
            poly.evaluate_polynomial()
```

### `tests/calculations/test_riser_array.py`
```python
import pytest
from assetutilities.calculations.riser_array import (
    equivalent_diameter,
    de_equivalencing_factor,
    hydrodynamic_shadow_factor,
    check_minimum_spacing,
)

class TestRiserArray:
    def test_equivalent_diameter_happy_path(self):
        result = equivalent_diameter(n=4, diameter=0.5)
        assert result == 1.0

    def test_equivalent_diameter_invalid_n_raises_error(self):
        with pytest.raises(ValueError, match="n must be a positive integer"):
            equivalent_diameter(n=0, diameter=0.5)

    def test_equivalent_diameter_invalid_diameter_raises_error(self):
        with pytest.raises(ValueError, match="diameter must be positive"):
            equivalent_diameter(n=4, diameter=-0.5)

    def test_de_equivalencing_factor_happy_path(self):
        result = de_equivalencing_factor(n=4)
        assert result == 0.5

    def test_de_equivalencing_factor_invalid_n_raises_error(self):
        with pytest.raises(ValueError, match="n must be a positive integer"):
            de_equivalencing_factor(n=0)

    def test_hydrodynamic_shadow_factor_happy_path(self):
        result = hydrodynamic_shadow_factor(spacing_ratio=2.0)
        assert result == pytest.approx(0.4230, rel=1e-3)

    def test_hydrodynamic_shadow_factor_large_spacing(self):
        result = hydrodynamic_shadow_factor(spacing_ratio=100.0)
        assert result == 1.0

    def test_hydrodynamic_shadow_factor_invalid_spacing_raises_error(self):
        with pytest.raises(ValueError, match="spacing_ratio must be positive"):
            hydrodynamic_shadow_factor(spacing_ratio=-1.0)

    def test_check_minimum_spacing_happy_path_is_true(self):
        result = check_minimum_spacing(centre_to_centre=2.0, diameter=0.5)
        assert result is True

    def test_check_minimum_spacing_fails_is_false(self):
        result = check_minimum_spacing(centre_to_centre=1.0, diameter=0.5)
        assert result is False

    def test_check_minimum_spacing_invalid_diameter_raises_error(self):
        with pytest.raises(ValueError, match="diameter must be positive"):
            check_minimum_spacing(centre_to_centre=2.0, diameter=-0.5)
```

### `tests/calculations/test_riser_dynamics.py`
```python
import pytest
from assetutilities.calculations.riser_dynamics import (
    tow_out_catenary_tension,
    hydrodynamic_damping_ratio,
    viv_fatigue_correction_factor,
    norton_drag_coefficient,
    vandiver_added_mass_coefficient,
    smith_residual_collapse_factor,
    crossflow_psd_amplitude,
)

class TestRiserDynamics:
    def test_tow_out_catenary_tension_happy_path(self):
        result = tow_out_catenary_tension(submerged_weight=1000.0, water_depth=100.0, angle_from_horizontal_deg=45.0)
        assert result == pytest.approx(100000.0)

    def test_tow_out_catenary_tension_vertical_angle_returns_zero(self):
        result = tow_out_catenary_tension(submerged_weight=1000.0, water_depth=100.0, angle_from_horizontal_deg=90.0)
        # Check that it returns approximately zero 
        assert result == pytest.approx(0.0, abs=1e-5)

    def test_tow_out_catenary_tension_invalid_angle_raises_error(self):
        with pytest.raises(ValueError, match="angle_from_horizontal_deg must be in range"):
            tow_out_catenary_tension(submerged_weight=1000.0, water_depth=100.0, angle_from_horizontal_deg=0.0)

    def test_hydrodynamic_damping_ratio_happy_path(self):
        result = hydrodynamic_damping_ratio(drag_coefficient=1.2, fluid_density=1025.0, diameter=0.5, current_velocity=1.0, mass_per_unit_length=200.0, natural_frequency=0.5)
        assert result > 0.0

    def test_hydrodynamic_damping_ratio_invalid_mass_raises_error(self):
        with pytest.raises(ValueError, match="mass_per_unit_length must be positive"):
            hydrodynamic_damping_ratio(drag_coefficient=1.2, fluid_density=1025.0, diameter=0.5, current_velocity=1.0, mass_per_unit_length=0.0, natural_frequency=0.5)

    def test_viv_fatigue_correction_factor_happy_path(self):
        result = viv_fatigue_correction_factor(correlation_length=10.0, span_length=20.0)
        assert result == 0.5

    def test_viv_fatigue_correction_factor_long_correlation_capped(self):
        result = viv_fatigue_correction_factor(correlation_length=30.0, span_length=20.0)
        assert result == 1.0

    def test_viv_fatigue_correction_factor_invalid_length_raises_error(self):
        with pytest.raises(ValueError, match="correlation_length must be positive"):
            viv_fatigue_correction_factor(correlation_length=-10.0, span_length=20.0)

    def test_norton_drag_coefficient_happy_path(self):
        assert norton_drag_coefficient(reynolds_number=1e5) == 1.2
        assert norton_drag_coefficient(reynolds_number=6e5) == 0.5

    def test_norton_drag_coefficient_invalid_re_raises_error(self):
        with pytest.raises(ValueError, match="reynolds_number must be positive"):
            norton_drag_coefficient(reynolds_number=-1e5)

    def test_vandiver_added_mass_coefficient_happy_path(self):
        assert vandiver_added_mass_coefficient() == 1.0

    def test_smith_residual_collapse_factor_happy_path(self):
        assert smith_residual_collapse_factor(ovality=0.1) == 0.8
        assert smith_residual_collapse_factor(ovality=0.6) == 0.0

    def test_smith_residual_collapse_factor_invalid_ovality_raises_error(self):
        with pytest.raises(ValueError, match="ovality must be non-negative"):
            smith_residual_collapse_factor(ovality=-0.1)

    def test_crossflow_psd_amplitude_happy_path(self):
        result = crossflow_psd_amplitude(lift_coefficient=0.5, fluid_density=1025.0, diameter=0.5, current_velocity=1.0, total_mass_per_unit_length=500.0, natural_frequency=0.5)
        assert result > 0.0

    def test_crossflow_psd_amplitude_invalid_frequency_raises_error(self):
        with pytest.raises(ValueError, match="natural_frequency must be positive"):
            crossflow_psd_amplitude(lift_coefficient=0.5, fluid_density=1025.0, diameter=0.5, current_velocity=1.0, total_mass_per_unit_length=500.0, natural_frequency=0.0)
```

### `tests/calculations/test_riser_viv.py`
```python
import pytest
from assetutilities.calculations.riser_viv import (
    drag_coefficient_smooth_cylinder,
    drag_coefficient_bundle,
    strouhal_frequency,
    reduced_velocity,
    viv_lock_in,
    viv_amplitude_response,
    viv_fatigue_damage,
    effective_tension,
    riser_natural_frequency,
)

class TestRiserViv:
    def test_drag_coefficient_smooth_cylinder_subcritical(self):
        assert drag_coefficient_smooth_cylinder(Re=1e5) == 1.2

    def test_drag_coefficient_smooth_cylinder_supercritical(self):
        assert drag_coefficient_smooth_cylinder(Re=1e7) == 0.6

    def test_drag_coefficient_smooth_cylinder_invalid_re_raises_error(self):
        with pytest.raises(ValueError, match="Reynolds number must be positive"):
            drag_coefficient_smooth_cylinder(Re=-1e5)

    def test_drag_coefficient_bundle_single_riser(self):
        assert drag_coefficient_bundle(Re=1e5, n_risers=1, pitch_diameter_ratio=2.0) == 1.2

    def test_drag_coefficient_bundle_multiple_risers(self):
        result = drag_coefficient_bundle(Re=1e5, n_risers=3, pitch_diameter_ratio=2.0)
        assert result == pytest.approx(1.8)

    def test_drag_coefficient_bundle_invalid_risers_raises_error(self):
        with pytest.raises(ValueError, match="n_risers must be >= 1"):
            drag_coefficient_bundle(Re=1e5, n_risers=0, pitch_diameter_ratio=2.0)

    def test_strouhal_frequency_happy_path(self):
        assert strouhal_frequency(U=2.0, D=0.5) == 0.8

    def test_strouhal_frequency_invalid_diameter_raises_error(self):
        with pytest.raises(ValueError, match="Diameter must be positive"):
            strouhal_frequency(U=2.0, D=0.0)

    def test_reduced_velocity_happy_path(self):
        assert reduced_velocity(U=2.0, f_n=0.5, D=0.5) == 8.0

    def test_reduced_velocity_invalid_frequency_raises_error(self):
        with pytest.raises(ValueError, match="Natural frequency must be positive"):
            reduced_velocity(U=2.0, f_n=0.0, D=0.5)

    def test_viv_lock_in_inside_range(self):
        assert viv_lock_in(Vr=5.0) is True

    def test_viv_lock_in_outside_range(self):
        assert viv_lock_in(Vr=3.0) is False

    def test_viv_amplitude_response_inside_lock_in(self):
        result = viv_amplitude_response(Vr=6.0, Ks=0.1)
        assert result > 0.0

    def test_viv_amplitude_response_outside_lock_in(self):
        result = viv_amplitude_response(Vr=3.0, Ks=0.1)
        assert result == 0.0

    def test_viv_fatigue_damage_happy_path(self):
        result = viv_fatigue_damage(stress_ranges=[1e6, 2e6], cycle_counts=[100, 50])
        assert result > 0.0

    def test_viv_fatigue_damage_mismatched_lengths_raises_error(self):
        with pytest.raises(ValueError, match="must equal cycle_counts length"):
            viv_fatigue_damage(stress_ranges=[1e6], cycle_counts=[100, 50, 10])

    def test_effective_tension_happy_path(self):
        result = effective_tension(T_wall=1e6, pi=1e7, pe=2e7, D=0.5, t=0.02)
        assert result > 0.0

    def test_riser_natural_frequency_happy_path(self):
        result = riser_natural_frequency(n=1, L=100.0, EI=1e8, m=200.0)
        assert result > 0.0

    def test_riser_natural_frequency_invalid_mode_raises_error(self):
        with pytest.raises(ValueError, match="Mode number n must be >= 1"):
            riser_natural_frequency(n=0, L=100.0, EI=1e8, m=200.0)
```

### `tests/calculations/test_scr_fatigue.py`
```python
import pytest
from assetutilities.calculations.scr_fatigue import (
    keulegan_carpenter_number,
    soil_interaction_fatigue_factor,
    fatigue_damage_tdz,
    scr_sn_fatigue_life,
    allen_viv_amplitude_ratio,
    brooks_viv_screening,
)

class TestScrFatigue:
    def test_keulegan_carpenter_number_valid_inputs_computes_correctly(self):
        result = keulegan_carpenter_number(u_m=2.0, period=10.0, diameter=0.5)
        assert result == pytest.approx(40.0)

    def test_keulegan_carpenter_number_zero_velocity_returns_zero(self):
        result = keulegan_carpenter_number(u_m=0.0, period=10.0, diameter=0.5)
        assert result == pytest.approx(0.0)

    def test_keulegan_carpenter_number_negative_diameter_raises_value_error(self):
        with pytest.raises(ValueError, match="diameter must be positive"):
            keulegan_carpenter_number(u_m=2.0, period=10.0, diameter=-0.5)

    def test_keulegan_carpenter_number_negative_period_raises_value_error(self):
        with pytest.raises(ValueError, match="period must be positive"):
            keulegan_carpenter_number(u_m=2.0, period=-10.0, diameter=0.5)

    def test_keulegan_carpenter_number_negative_velocity_raises_value_error(self):
        with pytest.raises(ValueError, match="u_m must be non-negative"):
            keulegan_carpenter_number(u_m=-2.0, period=10.0, diameter=0.5)


    def test_soil_interaction_fatigue_factor_high_kc_returns_one(self):
        result = soil_interaction_fatigue_factor(kc=15.0)
        assert result == pytest.approx(1.0)

    def test_soil_interaction_fatigue_factor_low_kc_returns_amplified_factor(self):
        result = soil_interaction_fatigue_factor(kc=5.0)
        assert result == pytest.approx(1.125)

    def test_soil_interaction_fatigue_factor_threshold_kc_returns_one(self):
        result = soil_interaction_fatigue_factor(kc=10.0)
        assert result == pytest.approx(1.0)

    def test_soil_interaction_fatigue_factor_negative_kc_raises_value_error(self):
        with pytest.raises(ValueError, match="kc must be non-negative"):
            soil_interaction_fatigue_factor(kc=-1.0)


    def test_fatigue_damage_tdz_valid_inputs_computes_correctly(self):
        stress_ranges = [100.0, 200.0]
        cycle_counts = [1e4, 1e3]
        kc_numbers = [15.0, 5.0]
        a_param = 1e12
        m_param = 3.0
        
        result = fatigue_damage_tdz(stress_ranges, cycle_counts, kc_numbers, a_param, m_param)
        assert result == pytest.approx(0.019)

    def test_fatigue_damage_tdz_empty_lists_returns_zero(self):
        result = fatigue_damage_tdz([], [], [], 1e12, 3.0)
        assert result == 0.0

    def test_fatigue_damage_tdz_mismatched_lists_raises_value_error(self):
        with pytest.raises(ValueError, match="must have the same length"):
            fatigue_damage_tdz([100.0], [1e4, 1e3], [15.0], 1e12, 3.0)


    def test_scr_sn_fatigue_life_valid_inputs_computes_correctly(self):
        result = scr_sn_fatigue_life(sigma_a=50.0, a_param=1e12, m_param=3.0)
        assert result == pytest.approx(1e6)

    def test_scr_sn_fatigue_life_small_stress_returns_large_life(self):
        result = scr_sn_fatigue_life(sigma_a=1e-3, a_param=1e12, m_param=3.0)
        assert result > 1e12

    def test_scr_sn_fatigue_life_non_positive_stress_raises_value_error(self):
        with pytest.raises(ValueError, match="sigma_a must be positive"):
            scr_sn_fatigue_life(sigma_a=0.0, a_param=1e12, m_param=3.0)

    def test_scr_sn_fatigue_life_non_positive_a_param_raises_value_error(self):
        with pytest.raises(ValueError, match="a_param must be positive"):
            scr_sn_fatigue_life(sigma_a=50.0, a_param=-1e12, m_param=3.0)


    def test_allen_viv_amplitude_ratio_low_vr_returns_zero(self):
        result = allen_viv_amplitude_ratio(vr=3.0)
        assert result == 0.0

    def test_allen_viv_amplitude_ratio_mid_vr_returns_linear_interpolation(self):
        result = allen_viv_amplitude_ratio(vr=6.0)
        assert result == pytest.approx(0.4)

    def test_allen_viv_amplitude_ratio_high_vr_returns_max(self):
        result = allen_viv_amplitude_ratio(vr=10.0)
        assert result == pytest.approx(0.8)

    def test_allen_viv_amplitude_ratio_negative_vr_raises_value_error(self):
        with pytest.raises(ValueError, match="vr must be non-negative"):
            allen_viv_amplitude_ratio(vr=-1.0)


    def test_brooks_viv_screening_low_vr_returns_false_and_zero(self):
        viv_risk, a_over_d = brooks_viv_screening(vr=3.0)
        assert viv_risk is False
        assert a_over_d == 0.0

    def test_brooks_viv_screening_high_vr_returns_true_and_lock_in_ratio(self):
        viv_risk, a_over_d = brooks_viv_screening(vr=5.0)
        assert viv_risk is True
        assert a_over_d == pytest.approx(0.9)

    def test_brooks_viv_screening_negative_vr_raises_value_error(self):
        with pytest.raises(ValueError, match="vr must be non-negative"):
            brooks_viv_screening(vr=-1.0)
```

### `tests/calculations/test_tlp_well_system.py`
```python
import pytest
from assetutilities.calculations.tlp_well_system import (
    tendon_effective_tension,
    riser_tensioner_stroke,
    wellhead_fatigue_accumulation,
    riser_interference_check,
    critical_damping_ratio,
    platform_set_down,
)

class TestTlpWellSystem:
    def test_tendon_effective_tension_happy_path(self):
        result = tendon_effective_tension(t_pretension=1e6, delta_t_hull=1e5)
        assert result == 9e5

    def test_tendon_effective_tension_non_positive_raises_error(self):
        with pytest.raises(ValueError, match="effective tension must be positive"):
            tendon_effective_tension(t_pretension=1e5, delta_t_hull=1e6)

    def test_riser_tensioner_stroke_happy_path(self):
        result = riser_tensioner_stroke(length=100.0, delta_vert=2.0, delta_horiz=10.0)
        assert result > 0.0

    def test_riser_tensioner_stroke_invalid_length_raises_error(self):
        with pytest.raises(ValueError, match="length must be positive"):
            riser_tensioner_stroke(length=0.0, delta_vert=2.0, delta_horiz=10.0)

    def test_wellhead_fatigue_accumulation_happy_path(self):
        result = wellhead_fatigue_accumulation(stress_ranges=[1e6], annual_cycles=[100], service_years=20, a_param=1e12, m_param=3.0)
        assert result > 0.0

    def test_wellhead_fatigue_accumulation_mismatched_lists_raises_error(self):
        with pytest.raises(ValueError, match="must have the same length"):
            wellhead_fatigue_accumulation(stress_ranges=[1e6], annual_cycles=[100, 200], service_years=20, a_param=1e12, m_param=3.0)

    def test_riser_interference_check_clear(self):
        is_clear, gap = riser_interference_check(tensioned_riser_od=0.5, drilling_riser_od=0.6, centre_to_centre=2.0)
        assert is_clear is True
        assert gap == 1.45

    def test_riser_interference_check_invalid_od_raises_error(self):
        with pytest.raises(ValueError, match="outer diameter must be positive"):
            riser_interference_check(tensioned_riser_od=-0.5, drilling_riser_od=0.6, centre_to_centre=2.0)

    def test_critical_damping_ratio_happy_path(self):
        result = critical_damping_ratio(C=100.0, K=1000.0, M=10.0)
        assert result == 0.5

    def test_critical_damping_ratio_invalid_mass_raises_error(self):
        with pytest.raises(ValueError, match="must be positive"):
            critical_damping_ratio(C=100.0, K=1000.0, M=0.0)

    def test_platform_set_down_happy_path(self):
        result = platform_set_down(length=1000.0, delta_horiz=100.0)
        assert result > 0.0

    def test_platform_set_down_invalid_offset_raises_error(self):
        with pytest.raises(ValueError, match="must be less than length"):
            platform_set_down(length=100.0, delta_horiz=100.0)
```

### `tests/calculations/test_wellhead_fatigue.py`
```python
import pytest
from assetutilities.calculations.wellhead_fatigue import (
    sn_cycles_to_failure,
    fatigue_life_years,
    annual_fatigue_damage,
    accumulate_fatigue_damage,
    sweeney_effective_stress,
    viv_wellhead_fatigue_damage,
    denison_conductor_tensioner_load,
    britton_fatigue_life_multiplier,
)

class TestWellheadFatigue:
    def test_sn_cycles_to_failure_happy_path(self):
        result = sn_cycles_to_failure(delta_sigma=100.0, A=1e12, m=3.0)
        assert result == 1e6

    def test_sn_cycles_to_failure_invalid_stress_raises_error(self):
        with pytest.raises(ValueError, match="delta_sigma must be positive"):
            sn_cycles_to_failure(delta_sigma=0.0, A=1e12, m=3.0)

    def test_fatigue_life_years_happy_path(self):
        result = fatigue_life_years(n_f=1e6, cycles_per_year=1e5)
        assert result == 10.0

    def test_fatigue_life_years_invalid_cycles_raises_error(self):
        with pytest.raises(ValueError, match="cycles_per_year must be positive"):
            fatigue_life_years(n_f=1e6, cycles_per_year=0.0)

    def test_annual_fatigue_damage_happy_path(self):
        result = annual_fatigue_damage(n_applied=1e5, n_f=1e6)
        assert result == 0.1

    def test_annual_fatigue_damage_invalid_nf_raises_error(self):
        with pytest.raises(ValueError, match="n_f must be positive"):
            annual_fatigue_damage(n_applied=1e5, n_f=-1e6)

    def test_accumulate_fatigue_damage_happy_path(self):
        result = accumulate_fatigue_damage(blocks=[(1e5, 1e6), (2e5, 2e6)])
        assert result == 0.2

    def test_sweeney_effective_stress_happy_path(self):
        result = sweeney_effective_stress(sigma_hoop=100.0, sigma_axial=50.0)
        assert result > 0.0

    def test_viv_wellhead_fatigue_damage_happy_path(self):
        result = viv_wellhead_fatigue_damage(viv_stress_range_psi=100.0, viv_frequency_hz=0.5, exposure_years=1.0, A=1e12, m=3.0)
        assert result > 0.0

    def test_viv_wellhead_fatigue_damage_zero_exposure(self):
        result = viv_wellhead_fatigue_damage(viv_stress_range_psi=100.0, viv_frequency_hz=0.5, exposure_years=0.0, A=1e12, m=3.0)
        assert result == 0.0

    def test_denison_conductor_tensioner_load_happy_path(self):
        result = denison_conductor_tensioner_load(pretension_kips=100.0, viv_amplification=1.5, hydrodynamic_load_kips=50.0)
        assert result == 175.0

    def test_britton_fatigue_life_multiplier_happy_path(self):
        result = britton_fatigue_life_multiplier(baseline_stiffness=2.0, reduced_stiffness=1.0, m=3.0)
        assert result == 8.0

    def test_britton_fatigue_life_multiplier_invalid_stiffness_raises_error(self):
        with pytest.raises(ValueError, match="reduced_stiffness must be positive"):
            britton_fatigue_life_multiplier(baseline_stiffness=2.0, reduced_stiffness=-1.0, m=3.0)
```
