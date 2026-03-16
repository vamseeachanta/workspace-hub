---
name: fatigue-analysis-4-spectral-fatigue-analysis
description: 'Sub-skill of fatigue-analysis: 4. Spectral Fatigue Analysis (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 4. Spectral Fatigue Analysis (+1)

## 4. Spectral Fatigue Analysis


**Narrow-Band Spectral Method:**
```python
def spectral_fatigue_narrow_band(
    spectrum: np.ndarray,
    frequencies: np.ndarray,
    sn_curve: dict,
    duration: float,
    design_factor: float = 10.0
) -> dict:
    """
    Calculate fatigue damage using narrow-band spectral method.

    Assumes Rayleigh distribution of stress ranges.

    Args:
        spectrum: Stress response spectrum S(f)
        frequencies: Frequency array (Hz)
        sn_curve: S-N curve parameters
        duration: Duration of analysis (seconds)
        design_factor: Safety factor

    Returns:
        Fatigue damage
    """
    # Spectral moments
    m0 = np.trapz(spectrum, frequencies)
    m2 = np.trapz(spectrum * frequencies**2, frequencies)
    m4 = np.trapz(spectrum * frequencies**4, frequencies)

    # Zero-crossing frequency
    f0 = np.sqrt(m2 / m0)

    # Number of zero crossings in duration
    N0 = f0 * duration

    # Standard deviation of stress
    sigma = np.sqrt(m0)

    # Damage integral for Rayleigh distribution
    # D = N0 * (2*sigma)^m * Γ(1 + m/2) / a

    m = sn_curve['m1']  # Use first slope
    a = sn_curve['a1']

    from scipy.special import gamma

    damage = N0 * (2 * sigma)**m * gamma(1 + m/2) / a

    # Apply design factor
    damage_with_df = damage * design_factor

    # Fatigue life
    if damage > 0:
        fatigue_life = duration / damage
    else:
        fatigue_life = np.inf

    return {
        'total_damage': damage,
        'damage_with_design_factor': damage_with_df,
        'fatigue_life_seconds': fatigue_life,
        'fatigue_life_years': fatigue_life / (365.25 * 24 * 3600),
        'sigma_stress': sigma,
        'zero_crossing_freq': f0
    }

# Example
freq_hz = np.linspace(0.01, 0.5, 500)
S_stress = 100 * freq_hz**(-2)  # Simplified stress spectrum

fatigue_spectral = spectral_fatigue_narrow_band(
    S_stress,
    freq_hz,
    sn_f3,
    duration=3600,  # 1 hour
    design_factor=10.0
)

# Scale to 25 years
fatigue_spectral['damage_25yr'] = fatigue_spectral['total_damage'] * 8760 * 25

print(f"Spectral Fatigue (25 years):")
print(f"  Damage: {fatigue_spectral['damage_25yr']:.4f}")
print(f"  Utilization: {fatigue_spectral['damage_25yr'] * 10:.1f}%")
```


## 5. Mooring Line Fatigue


**Chain Fatigue at Fairlead:**
```python
def mooring_chain_fatigue_analysis(
    tension_time_series: np.ndarray,
    chain_diameter: float,
    chain_grade: str = 'R4',
    design_life_years: float = 25,
    time_step: float = 0.1
) -> dict:
    """
    Complete mooring chain fatigue analysis.

    Args:
        tension_time_series: Tension time series (kN)
        chain_diameter: Chain diameter (mm)
        chain_grade: Chain grade (R3, R4, R5)
        design_life_years: Design life (years)
        time_step: Time step (seconds)

    Returns:
        Fatigue results
    """
    # Chain properties
    grade_factors = {'R3': 0.0219, 'R4': 0.0246, 'R5': 0.0273}
    MBL = grade_factors[chain_grade] * chain_diameter**2  # tonnes

    # Cross-sectional area (nominal)
    d_mm = chain_diameter
    A = np.pi * (d_mm/2)**2  # mm²

    # Convert tension to stress
    stress_time_series = tension_time_series * 1000 / A  # MPa

    # Rainflow counting
    stress_ranges, cycle_counts = rainflow_counting(stress_time_series)

    # Duration of time series
    duration_hours = len(tension_time_series) * time_step / 3600

    # Scale to design life
    hours_total = 8760 * design_life_years
    scale_factor = hours_total / duration_hours

    cycle_counts_scaled = cycle_counts * scale_factor

    # Select S-N curve (DNV: F3 for chain at connector)
    sn_curve = get_dnv_sn_curve('F3', thickness=chain_diameter)

    # Calculate damage
    fatigue_result = calculate_fatigue_damage_miners_rule(
        stress_ranges,
        cycle_counts_scaled,
        sn_curve,
        design_factor=10.0  # DNV-OS-E301
    )

    return {
        'chain_diameter_mm': chain_diameter,
        'chain_grade': chain_grade,
        'MBL_tonnes': MBL,
        'design_life_years': design_life_years,
        'fatigue_damage': fatigue_result['total_damage'],
        'utilization': fatigue_result['utilization'],
        'passed': fatigue_result['passed'],
        'fatigue_life_years': fatigue_result['fatigue_life'],
        'stress_ranges': stress_ranges,
        'cycle_counts': cycle_counts_scaled
    }

# Example
tension = 2000 + 400 * np.sin(2*np.pi*np.arange(36000)/100)  # 1 hour, varied tension

chain_fatigue = mooring_chain_fatigue_analysis(
    tension,
    chain_diameter=127,  # mm
    chain_grade='R4',
    design_life_years=25,
    time_step=0.1
)

print(f"Mooring Chain Fatigue:")
print(f"  Diameter: {chain_fatigue['chain_diameter_mm']} mm {chain_fatigue['chain_grade']}")
print(f"  MBL: {chain_fatigue['MBL_tonnes']:.1f} tonnes")
print(f"  Damage (25 years): {chain_fatigue['fatigue_damage']:.4f}")
print(f"  Utilization: {chain_fatigue['utilization']*100:.1f}%")
print(f"  Status: {'PASS' if chain_fatigue['passed'] else 'FAIL'}")
```
