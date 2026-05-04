---
name: ship-dynamics-6dof-6-seakeeping-analysis
description: 'Sub-skill of ship-dynamics-6dof: 6. Seakeeping Analysis.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 6. Seakeeping Analysis

## 6. Seakeeping Analysis


**Motion Statistics:**
```python
def calculate_seakeeping_statistics(
    motion_time_series: np.ndarray,
    dt: float,
    dof_name: str = "Motion"
) -> dict:
    """
    Calculate seakeeping statistics from motion time series.

    Args:
        motion_time_series: Time series of motion
        dt: Time step
        dof_name: Name of DOF

    Returns:
        Statistical parameters
    """
    # Basic statistics
    mean = np.mean(motion_time_series)
    std = np.std(motion_time_series)

    # Significant amplitude (1/3 highest)
    sorted_amplitudes = np.sort(np.abs(motion_time_series))
    n_third = len(sorted_amplitudes) // 3
    significant_amplitude = np.mean(sorted_amplitudes[-n_third:])

    # Maximum
    max_amplitude = np.max(np.abs(motion_time_series))

    # Zero crossing period
    zero_crossings = np.where(np.diff(np.sign(motion_time_series)))[0]
    if len(zero_crossings) > 1:
        Tz = np.mean(np.diff(zero_crossings)) * dt * 2  # Up and down
    else:
        Tz = np.nan

    # RMS
    rms = np.sqrt(np.mean(motion_time_series**2))

    return {
        'dof': dof_name,
        'mean': mean,
        'std_dev': std,
        'rms': rms,
        'significant_amplitude': significant_amplitude,
        'max_amplitude': max_amplitude,
        'zero_crossing_period': Tz
    }

# Example
heave_motion = result['displacement'][:, 2]
heave_stats = calculate_seakeeping_statistics(heave_motion, dt, 'Heave')

print(f"Heave Statistics:")
print(f"  Significant amplitude: {heave_stats['significant_amplitude']:.2f} m")
print(f"  Max amplitude: {heave_stats['max_amplitude']:.2f} m")
print(f"  Zero-crossing period: {heave_stats['zero_crossing_period']:.2f} s")
```

**Motion Sickness Incidence (MSI):**
```python
def calculate_motion_sickness_incidence(
    acceleration_rms: float,
    frequency_hz: float,
    duration_hours: float = 2
) -> float:
    """
    Calculate Motion Sickness Incidence (MSI) using ISO 2631-1.

    MSI = % of people experiencing motion sickness

    Args:
        acceleration_rms: RMS vertical acceleration (m/s²)
        frequency_hz: Dominant frequency (Hz)
        duration_hours: Exposure duration (hours)

    Returns:
        MSI percentage
    """
    # Weighting factor (ISO 2631-1)
    # Peak sensitivity at 0.16 Hz
    if 0.1 <= frequency_hz <= 0.5:
        weighting = 1.0
    else:
        weighting = 0.5

    # Weighted acceleration
    a_w = acceleration_rms * weighting

    # Time factor
    time_factor = (duration_hours / 2) ** 0.5

    # MSI calculation (simplified O'Hanlon-McCauley)
    msdv = a_w * time_factor  # Motion Sickness Dose Value

    # Convert to percentage (empirical correlation)
    MSI = 100 * (1 / (1 + np.exp(-(msdv - 3.5) / 0.7)))

    return MSI

# Example: Calculate MSI for heave acceleration
a_heave = np.std(np.diff(result['velocity'][:, 2]) / dt)
freq_heave = 1 / heave_stats['zero_crossing_period']

msi = calculate_motion_sickness_incidence(a_heave, freq_heave, duration_hours=2)
print(f"Motion Sickness Incidence (2 hours): {msi:.1f}%")
```
