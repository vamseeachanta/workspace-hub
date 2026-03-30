---
name: risk-assessment-1-sample-size-selection
description: 'Sub-skill of risk-assessment: 1. Sample Size Selection (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Sample Size Selection (+1)

## 1. Sample Size Selection


```python
def determine_sample_size(
    target_pf: float,
    confidence_level: float = 0.95
) -> int:
    """
    Determine required sample size for target failure probability.

    Rule of thumb: N ≈ 10/Pf for reasonable confidence

    Args:
        target_pf: Target probability of failure
        confidence_level: Confidence level

    Returns:
        Recommended sample size

    Example:
        >>> n = determine_sample_size(target_pf=1e-4, confidence_level=0.95)
        >>> print(f"Recommended samples: {n}")
    """
    # Basic rule: need at least 10 failures
    # So N * Pf ≥ 10
    # N ≥ 10 / Pf

    n_basic = int(10 / target_pf)

    # For higher confidence, increase further
    if confidence_level >= 0.99:
        n_recommended = n_basic * 5
    elif confidence_level >= 0.95:
        n_recommended = n_basic * 3
    else:
        n_recommended = n_basic * 2

    return max(n_recommended, 1000)  # Minimum 1000 samples
```


## 2. Convergence Checking


```python
def check_monte_carlo_convergence(
    data: np.ndarray,
    window_size: int = 1000
) -> dict:
    """
    Check if Monte Carlo simulation has converged.

    Args:
        data: Simulation output data
        window_size: Window size for moving average

    Returns:
        Dictionary with convergence metrics
    """
    n = len(data)

    # Calculate cumulative mean
    cumulative_mean = np.cumsum(data) / np.arange(1, n + 1)

    # Calculate moving coefficient of variation
    if n > window_size:
        moving_std = np.std(data[-window_size:])
        moving_mean = np.mean(data[-window_size:])
        cov = moving_std / moving_mean if moving_mean != 0 else 0
    else:
        cov = np.std(data) / np.mean(data) if np.mean(data) != 0 else 0

    # Convergence criterion: COV < 5%
    converged = cov < 0.05

    return {
        'converged': converged,
        'cov': cov,
        'final_mean': cumulative_mean[-1],
        'samples_used': n
    }
```
