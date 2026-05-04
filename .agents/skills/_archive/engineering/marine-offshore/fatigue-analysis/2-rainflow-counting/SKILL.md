---
name: fatigue-analysis-2-rainflow-counting
description: 'Sub-skill of fatigue-analysis: 2. Rainflow Counting (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 2. Rainflow Counting (+1)

## 2. Rainflow Counting


**Rainflow Algorithm:**
```python
def rainflow_counting(
    time_series: np.ndarray,
    bin_width: float = None
) -> tuple[np.ndarray, np.ndarray]:
    """
    Rainflow cycle counting algorithm.

    ASTM E1049-85 standard implementation.

    Args:
        time_series: Stress or load time series
        bin_width: Bin width for histogram (None = auto)

    Returns:
        (ranges, counts) - Stress ranges and cycle counts
    """
    # Simple peak-valley extraction
    peaks_valleys = []
    for i in range(1, len(time_series) - 1):
        if (time_series[i] > time_series[i-1] and time_series[i] > time_series[i+1]) or \
           (time_series[i] < time_series[i-1] and time_series[i] < time_series[i+1]):
            peaks_valleys.append(time_series[i])

    # Rainflow counting
    stack = []
    ranges = []

    for value in peaks_valleys:
        stack.append(value)

        while len(stack) >= 3:
            # Check for cycle
            X = abs(stack[-2] - stack[-3])
            Y = abs(stack[-1] - stack[-2])

            if len(stack) == 3:
                if Y >= X:
                    # Extract cycle
                    ranges.append(X)
                    stack.pop(-2)
                    stack.pop(-2)
                else:
                    break
            else:
                Z = abs(stack[-3] - stack[-4])
                if Y >= X and X >= Z:
                    # Extract cycle
                    ranges.append(X)
                    stack.pop(-2)
                    stack.pop(-2)
                else:
                    break

    # Create histogram
    ranges = np.array(ranges)

    if bin_width is None:
        bin_width = (np.max(ranges) - np.min(ranges)) / 20

    bins = np.arange(0, np.max(ranges) + bin_width, bin_width)
    counts, bin_edges = np.histogram(ranges, bins=bins)

    # Use bin centers
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    return bin_centers, counts

# Example: Mooring tension time series
t = np.linspace(0, 3600, 36000)  # 1 hour
tension = 2000 + 300 * np.sin(2*np.pi*t/10) + 100 * np.sin(2*np.pi*t/3) + 50*np.random.randn(len(t))

ranges, counts = rainflow_counting(tension, bin_width=10)

print(f"Rainflow cycles:")
print(f"  Total cycles: {np.sum(counts)}")
print(f"  Max range: {np.max(ranges):.1f} kN")
```


## 3. Miner's Rule (Cumulative Damage)


**Palmgren-Miner Damage:**
```python
def calculate_fatigue_damage_miners_rule(
    stress_ranges: np.ndarray,
    cycle_counts: np.ndarray,
    sn_curve: dict,
    design_factor: float = 10.0
) -> dict:
    """
    Calculate fatigue damage using Miner's rule.

    D = Σ(n_i / N_i)

    Where:
    - n_i = number of cycles at stress range i
    - N_i = cycles to failure at stress range i

    Args:
        stress_ranges: Array of stress ranges (MPa)
        cycle_counts: Array of cycle counts for each range
        sn_curve: S-N curve parameters
        design_factor: Safety factor (DNV: 10 for mooring)

    Returns:
        Fatigue damage and life prediction
    """
    total_damage = 0.0
    damage_breakdown = []

    for stress_range, n_cycles in zip(stress_ranges, cycle_counts):
        if stress_range > 0:
            # Cycles to failure
            N = calculate_cycles_to_failure(stress_range, sn_curve)

            # Damage contribution
            damage = n_cycles / N

            total_damage += damage

            damage_breakdown.append({
                'stress_range': stress_range,
                'cycles': n_cycles,
                'N_failure': N,
                'damage': damage,
                'damage_percent': 0  # Will be filled later
            })

    # Calculate percentage contributions
    for item in damage_breakdown:
        item['damage_percent'] = (item['damage'] / total_damage * 100) if total_damage > 0 else 0

    # Apply design factor
    total_damage_with_df = total_damage * design_factor

    # Fatigue life
    if total_damage > 0:
        fatigue_life = 1.0 / total_damage  # In units of analysis duration
    else:
        fatigue_life = np.inf

    return {
        'total_damage': total_damage,
        'damage_with_design_factor': total_damage_with_df,
        'fatigue_life': fatigue_life,
        'utilization': total_damage_with_df,
        'passed': total_damage_with_df <= 1.0,
        'breakdown': damage_breakdown
    }

# Example: Calculate fatigue damage
# Assume 1 hour of data, scale to 25 years
hours_per_year = 8760
design_life_years = 25
scale_factor = hours_per_year * design_life_years

# Convert tension ranges to stress (simplified)
stress_ranges = ranges / 100  # kN to MPa (simplified)
cycle_counts_scaled = counts * scale_factor

fatigue_result = calculate_fatigue_damage_miners_rule(
    stress_ranges,
    cycle_counts_scaled,
    sn_f3,
    design_factor=10.0
)

print(f"Fatigue Analysis Results:")
print(f"  Total damage: {fatigue_result['total_damage']:.4f}")
print(f"  With DF=10: {fatigue_result['damage_with_design_factor']:.4f}")
print(f"  Utilization: {fatigue_result['utilization']*100:.1f}%")
print(f"  Passed: {fatigue_result['passed']}")
print(f"  Fatigue life: {fatigue_result['fatigue_life']:.1f} years")
```
