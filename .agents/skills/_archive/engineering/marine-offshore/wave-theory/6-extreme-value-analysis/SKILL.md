---
name: wave-theory-6-extreme-value-analysis
description: 'Sub-skill of wave-theory: 6. Extreme Value Analysis.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 6. Extreme Value Analysis

## 6. Extreme Value Analysis


**Design Wave from Return Period:**
```python
def calculate_extreme_wave_height(
    return_period_years: float,
    Hs_annual_max: np.ndarray = None,
    distribution: str = 'weibull'
) -> dict:
    """
    Calculate design wave height for given return period.

    Args:
        return_period_years: Return period (years)
        Hs_annual_max: Array of annual maximum Hs values
        distribution: 'weibull' or 'gumbel'

    Returns:
        Extreme wave height statistics
    """
    from scipy.stats import weibull_min, gumbel_r

    if Hs_annual_max is None:
        # Example data: 25 years of annual maxima
        np.random.seed(42)
        Hs_annual_max = weibull_min.rvs(c=2, scale=10, size=25)

    # Fit distribution
    if distribution == 'weibull':
        params = weibull_min.fit(Hs_annual_max)
        c, loc, scale = params
        dist = weibull_min(c, loc, scale)
    elif distribution == 'gumbel':
        loc, scale = gumbel_r.fit(Hs_annual_max)
        dist = gumbel_r(loc, scale)
    else:
        raise ValueError("Unknown distribution")

    # Exceedance probability for return period
    exceedance_prob = 1 / return_period_years

    # Extreme value
    Hs_extreme = dist.ppf(1 - exceedance_prob)

    # Confidence intervals (simplified)
    Hs_lower = dist.ppf(1 - exceedance_prob - 0.1)
    Hs_upper = dist.ppf(1 - exceedance_prob + 0.1)

    return {
        'return_period_years': return_period_years,
        'Hs_extreme': Hs_extreme,
        'Hs_lower_bound': Hs_lower,
        'Hs_upper_bound': Hs_upper,
        'distribution': distribution,
        'exceedance_probability': exceedance_prob
    }

# Example: 100-year return period
extreme_100yr = calculate_extreme_wave_height(
    return_period_years=100,
    distribution='weibull'
)

print(f"100-Year Wave:")
print(f"  Hs: {extreme_100yr['Hs_extreme']:.2f} m")
print(f"  Range: {extreme_100yr['Hs_lower_bound']:.2f} - {extreme_100yr['Hs_upper_bound']:.2f} m")
```
