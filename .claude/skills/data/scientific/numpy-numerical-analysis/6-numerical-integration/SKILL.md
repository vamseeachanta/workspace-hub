---
name: numpy-numerical-analysis-6-numerical-integration
description: 'Sub-skill of numpy-numerical-analysis: 6. Numerical Integration.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 6. Numerical Integration

## 6. Numerical Integration


**Time-Stepping Integration:**
```python
def runge_kutta_4th_order(
    derivative_func,
    y0: np.ndarray,
    t: np.ndarray
) -> np.ndarray:
    """
    4th-order Runge-Kutta integration.

    Args:
        derivative_func: Function dy/dt = f(t, y)
        y0: Initial conditions
        t: Time array

    Returns:
        Solution array
    """
    n = len(t)
    y = np.zeros((n, len(y0)))
    y[0] = y0

    for i in range(n - 1):
        dt = t[i+1] - t[i]

        k1 = derivative_func(t[i], y[i])
        k2 = derivative_func(t[i] + dt/2, y[i] + k1*dt/2)
        k3 = derivative_func(t[i] + dt/2, y[i] + k2*dt/2)
        k4 = derivative_func(t[i] + dt, y[i] + k3*dt)

        y[i+1] = y[i] + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)

    return y

# Example: Simple harmonic oscillator
# m*x'' + k*x = 0
# y = [x, v], dy/dt = [v, -k/m*x]

def oscillator_derivatives(t, y):
    """Simple harmonic oscillator."""
    m = 1.0  # Mass
    k = 4.0  # Stiffness (omega = 2 rad/s, T = pi s)

    x, v = y
    dxdt = v
    dvdt = -k/m * x

    return np.array([dxdt, dvdt])

# Initial conditions
y0 = np.array([1.0, 0.0])  # x = 1, v = 0

# Time array
t = np.linspace(0, 10, 1000)

# Solve
solution = runge_kutta_4th_order(oscillator_derivatives, y0, t)

print(f"Final position: {solution[-1, 0]:.4f}")
print(f"Final velocity: {solution[-1, 1]:.4f}")
```

**Trapezoidal Integration:**
```python
def integrate_spectrum(
    frequencies: np.ndarray,
    spectral_density: np.ndarray
) -> float:
    """
    Integrate spectral density to get variance.

    m_0 = ∫ S(f) df

    Args:
        frequencies: Frequency array
        spectral_density: Spectral density array

    Returns:
        Integral (variance)
    """
    variance = np.trapz(spectral_density, frequencies)

    return variance

# Example: Calculate significant wave height from spectrum
freq = np.linspace(0.05, 0.5, 100)  # Hz
S = 10 * freq**(-5)  # Simplified spectrum

m0 = integrate_spectrum(freq, S)
Hs = 4 * np.sqrt(m0)

print(f"Significant wave height: {Hs:.2f} m")
```
