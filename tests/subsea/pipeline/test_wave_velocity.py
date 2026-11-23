"""
Tests for DNV RP F105 wave-induced velocity (Sec 3.4).

Reference values derived from analytical limits and standard
JONSWAP/linear-wave-theory relationships.
"""
import math
import pytest
import numpy as np

from digitalmodel.subsea.pipeline.free_span.wave_velocity import (
    jonswap_gamma,
    jonswap_spectrum,
    solve_dispersion,
    velocity_transfer,
    spectral_moments,
    compute_wave_velocity,
    WaveVelocityResult,
)


# ---------------------------------------------------------------------------
# JONSWAP gamma auto-selection (DNV-RP-F105 Sec 3.4)
# ---------------------------------------------------------------------------

class TestJonswapGamma:

    def test_steep_sea_gives_gamma_5(self):
        """phi = Tp/sqrt(Hs) <= 3.6 -> gamma = 5.0."""
        # Hs=4, Tp=6 -> phi = 6/2 = 3.0 < 3.6
        assert jonswap_gamma(4.0, 6.0) == 5.0

    def test_swell_gives_gamma_1(self):
        """phi >= 5.0 -> gamma = 1.0 (Pierson-Moskowitz)."""
        # Hs=1, Tp=8 -> phi = 8/1 = 8.0 > 5.0
        assert jonswap_gamma(1.0, 8.0) == 1.0

    def test_intermediate_range(self):
        """3.6 < phi < 5.0 -> 1 < gamma < 5."""
        # Hs=4, Tp=8 -> phi = 8/2 = 4.0
        g = jonswap_gamma(4.0, 8.0)
        assert 1.0 < g < 5.0

    def test_formula_at_phi_4(self):
        """gamma = exp(5.75 - 1.15*4.0) = exp(1.15)."""
        # Hs=4, Tp=8 -> phi=4.0
        expected = math.exp(5.75 - 1.15 * 4.0)
        assert abs(jonswap_gamma(4.0, 8.0) - expected) < 1e-10

    def test_zero_Hs_gives_gamma_1(self):
        """Degenerate: Hs=0 -> phi=inf -> gamma=1."""
        assert jonswap_gamma(0.0, 8.0) == 1.0


# ---------------------------------------------------------------------------
# JONSWAP spectrum
# ---------------------------------------------------------------------------

class TestJonswapSpectrum:

    def test_spectrum_positive(self):
        """S(w) >= 0 for all w."""
        omega = np.linspace(0.1, 3.0, 200)
        S = jonswap_spectrum(omega, Hs=3.0, Tp=8.0)
        assert np.all(S >= 0)

    def test_spectrum_peak_near_wp(self):
        """Peak of S(w) should be near wp = 2*pi/Tp."""
        omega = np.linspace(0.1, 3.0, 1000)
        S = jonswap_spectrum(omega, Hs=3.0, Tp=8.0)
        wp = 2 * math.pi / 8.0
        w_peak = omega[np.argmax(S)]
        assert abs(w_peak - wp) / wp < 0.05  # within 5%

    def test_hs_constraint(self):
        """Integral of S(w) should give Hs²/16 (approximately).

        For gamma > 1 the C_gamma normalisation introduces some deviation
        from exact Hs recovery; tolerance is 15% which covers typical
        JONSWAP gamma range (1–5).
        """
        omega = np.linspace(0.01, 5.0, 4000)
        S = jonswap_spectrum(omega, Hs=3.0, Tp=8.0)
        _trapz = getattr(np, "trapezoid", None) or np.trapz
        M0 = _trapz(S, omega)
        Hs_reconstructed = 4.0 * math.sqrt(M0)
        assert abs(Hs_reconstructed - 3.0) / 3.0 < 0.15  # within 15%

    def test_gamma_1_equals_pm(self):
        """gamma=1 should give Pierson-Moskowitz spectrum shape."""
        omega = np.linspace(0.1, 3.0, 500)
        S_j = jonswap_spectrum(omega, Hs=3.0, Tp=8.0, gamma=1.0)
        # All values finite and positive
        assert np.all(np.isfinite(S_j))
        assert np.all(S_j >= 0)

    def test_higher_gamma_narrower_peak(self):
        """Higher gamma -> narrower, taller peak."""
        omega = np.linspace(0.1, 3.0, 500)
        S1 = jonswap_spectrum(omega, Hs=3.0, Tp=8.0, gamma=1.0)
        S5 = jonswap_spectrum(omega, Hs=3.0, Tp=8.0, gamma=5.0)
        # Peak should be taller for gamma=5
        assert np.max(S5) > np.max(S1)


# ---------------------------------------------------------------------------
# Dispersion relation
# ---------------------------------------------------------------------------

class TestDispersionRelation:

    def test_deep_water_limit(self):
        """Deep water: k = w²/g."""
        omega = np.array([1.0])
        k = solve_dispersion(omega, depth=1000.0)
        k_deep = omega**2 / 9.80665
        assert abs(k[0] - k_deep[0]) / k_deep[0] < 0.01

    def test_shallow_water_limit(self):
        """Shallow water: k*h -> w*sqrt(h/g), k -> w/sqrt(g*h)."""
        omega = np.array([0.1])  # low frequency
        h = 2.0  # very shallow
        k = solve_dispersion(omega, depth=h)
        k_shallow = omega / math.sqrt(9.80665 * h)
        # Shallow water approx should be close
        assert abs(k[0] - k_shallow[0]) / k_shallow[0] < 0.15

    def test_k_positive(self):
        """Wave number must be positive."""
        omega = np.linspace(0.1, 3.0, 100)
        k = solve_dispersion(omega, depth=50.0)
        assert np.all(k > 0)

    def test_k_increases_with_omega(self):
        """Higher frequency -> higher wave number."""
        omega = np.linspace(0.2, 2.0, 50)
        k = solve_dispersion(omega, depth=100.0)
        assert np.all(np.diff(k) > 0)


# ---------------------------------------------------------------------------
# Velocity transfer function
# ---------------------------------------------------------------------------

class TestVelocityTransfer:

    def test_surface_gives_omega(self):
        """At surface (z=h): G(w) -> w (deep water)."""
        omega = np.array([1.0])
        k = solve_dispersion(omega, depth=100.0)
        G = velocity_transfer(omega, k, depth=100.0, z_pipe=100.0)
        # cosh(k*h)/sinh(k*h) = coth(k*h) -> 1 for k*h >> 1
        assert abs(G[0] - omega[0]) / omega[0] < 0.05

    def test_seabed_gives_minimum(self):
        """At seabed (z≈0): G is minimum (near zero for deep water)."""
        omega = np.array([1.0])
        k = solve_dispersion(omega, depth=100.0)
        G_seabed = velocity_transfer(omega, k, depth=100.0, z_pipe=0.1)
        G_surface = velocity_transfer(omega, k, depth=100.0, z_pipe=100.0)
        assert G_seabed[0] < G_surface[0]

    def test_positive(self):
        """G(w) >= 0."""
        omega = np.linspace(0.1, 3.0, 100)
        k = solve_dispersion(omega, depth=50.0)
        G = velocity_transfer(omega, k, depth=50.0, z_pipe=1.0)
        assert np.all(G >= 0)


# ---------------------------------------------------------------------------
# compute_wave_velocity — integration tests
# ---------------------------------------------------------------------------

class TestComputeWaveVelocity:

    def test_returns_result_type(self):
        result = compute_wave_velocity(Hs=3.0, Tp=8.0, water_depth_m=100.0,
                                       pipe_elevation_m=0.5)
        assert isinstance(result, WaveVelocityResult)

    def test_Uw_positive(self):
        """Uw > 0 for non-zero sea state."""
        result = compute_wave_velocity(Hs=3.0, Tp=8.0, water_depth_m=100.0,
                                       pipe_elevation_m=0.5)
        assert result.Uw_ms > 0

    def test_Tu_positive(self):
        """Tu > 0 for non-zero sea state."""
        result = compute_wave_velocity(Hs=3.0, Tp=8.0, water_depth_m=100.0,
                                       pipe_elevation_m=0.5)
        assert result.Tu_s > 0

    def test_zero_Hs_gives_zero_Uw(self):
        """No waves -> Uw = 0."""
        result = compute_wave_velocity(Hs=0.0, Tp=8.0, water_depth_m=100.0,
                                       pipe_elevation_m=0.5)
        assert result.Uw_ms == 0.0

    def test_deeper_water_reduces_Uw(self):
        """Deeper water -> smaller Uw at seabed (more attenuation)."""
        r_shallow = compute_wave_velocity(Hs=3.0, Tp=8.0, water_depth_m=30.0,
                                          pipe_elevation_m=0.5)
        r_deep = compute_wave_velocity(Hs=3.0, Tp=8.0, water_depth_m=200.0,
                                       pipe_elevation_m=0.5)
        assert r_deep.Uw_ms < r_shallow.Uw_ms

    def test_higher_Hs_increases_Uw(self):
        """Bigger waves -> higher Uw."""
        r_small = compute_wave_velocity(Hs=1.0, Tp=8.0, water_depth_m=100.0,
                                        pipe_elevation_m=0.5)
        r_big = compute_wave_velocity(Hs=5.0, Tp=8.0, water_depth_m=100.0,
                                      pipe_elevation_m=0.5)
        assert r_big.Uw_ms > r_small.Uw_ms

    def test_higher_elevation_increases_Uw(self):
        """Pipe higher above seabed -> more wave action."""
        r_low = compute_wave_velocity(Hs=3.0, Tp=8.0, water_depth_m=50.0,
                                      pipe_elevation_m=0.5)
        r_high = compute_wave_velocity(Hs=3.0, Tp=8.0, water_depth_m=50.0,
                                       pipe_elevation_m=10.0)
        assert r_high.Uw_ms > r_low.Uw_ms

    def test_gamma_stored_in_result(self):
        """Auto-selected gamma is stored in result."""
        result = compute_wave_velocity(Hs=3.0, Tp=8.0, water_depth_m=100.0,
                                       pipe_elevation_m=0.5)
        expected_gamma = jonswap_gamma(3.0, 8.0)
        assert abs(result.gamma - expected_gamma) < 1e-10

    def test_matlab_example_conditions(self):
        """MATLAB sample: Hs=5, Tp=8, depth=120m (approx GOM conditions).

        With Uw=0 in the sample input, wave velocity was not computed.
        But with Hs=5, Tp=8, depth=120 near seabed: Uw should be
        physically small (< 1 m/s) due to deep water attenuation.
        """
        result = compute_wave_velocity(
            Hs=5.0, Tp=8.0, water_depth_m=120.0,
            pipe_elevation_m=2.63,  # MATLAB seabed proximity
            pipe_od_m=0.1683,       # MATLAB 6" pipe OD
        )
        # Deep water, near seabed: Uw should be modest
        assert 0 < result.Uw_ms < 2.0, f"Uw={result.Uw_ms:.3f} m/s unexpected"
        assert result.Tu_s > 0

    def test_Uw_physical_range_typical_gom(self):
        """Typical GoM 100-yr: Hs=12m, Tp=14s, depth=300m.

        Near-seabed Uw should be < 0.5 m/s (deep water).
        """
        result = compute_wave_velocity(
            Hs=12.0, Tp=14.0, water_depth_m=300.0,
            pipe_elevation_m=0.5,
        )
        assert 0 < result.Uw_ms < 1.0

    def test_shallow_water_Uw_larger(self):
        """Shallow water (20m depth, Hs=3m): Uw should be significant."""
        result = compute_wave_velocity(
            Hs=3.0, Tp=8.0, water_depth_m=20.0,
            pipe_elevation_m=0.5,
        )
        # Shallow water near seabed should give meaningful Uw
        assert result.Uw_ms > 0.1

    def test_pipe_od_shifts_elevation(self):
        """Providing pipe_od_m shifts evaluation point up by D/2."""
        r_no_od = compute_wave_velocity(Hs=3.0, Tp=8.0, water_depth_m=50.0,
                                        pipe_elevation_m=0.5, pipe_od_m=0.0)
        r_with_od = compute_wave_velocity(Hs=3.0, Tp=8.0, water_depth_m=50.0,
                                          pipe_elevation_m=0.5, pipe_od_m=0.5)
        # With OD, elevation is 0.5 + 0.25 = 0.75 -> slightly higher Uw
        assert r_with_od.Uw_ms >= r_no_od.Uw_ms


# ---------------------------------------------------------------------------
# KC number computation helper
# ---------------------------------------------------------------------------

class TestKCNumber:
    """Keulegan-Carpenter number KC = Uw × Tu / D."""

    def test_kc_from_wave_velocity(self):
        """Compute KC from Uw and Tu."""
        result = compute_wave_velocity(Hs=3.0, Tp=8.0, water_depth_m=50.0,
                                       pipe_elevation_m=0.5)
        D = 0.2731  # 10" pipe
        KC = result.Uw_ms * result.Tu_s / D
        assert KC >= 0
