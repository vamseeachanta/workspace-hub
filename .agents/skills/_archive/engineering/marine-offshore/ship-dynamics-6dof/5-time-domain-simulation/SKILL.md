---
name: ship-dynamics-6dof-5-time-domain-simulation
description: 'Sub-skill of ship-dynamics-6dof: 5. Time-Domain Simulation.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 5. Time-Domain Simulation

## 5. Time-Domain Simulation


**Newmark-Beta Integration:**
```python
def newmark_beta_integration(
    M: np.ndarray,
    C: np.ndarray,
    K: np.ndarray,
    F_t: np.ndarray,
    x0: np.ndarray,
    v0: np.ndarray,
    t: np.ndarray,
    beta: float = 0.25,
    gamma: float = 0.5
) -> dict:
    """
    Newmark-Beta time integration for 6DOF dynamics.

    Args:
        M: Mass matrix (6x6)
        C: Damping matrix (6x6)
        K: Stiffness matrix (6x6)
        F_t: Force time series (n_steps x 6)
        x0: Initial displacement (6,)
        v0: Initial velocity (6,)
        t: Time array
        beta: Newmark beta parameter (0.25 = const accel)
        gamma: Newmark gamma parameter (0.5)

    Returns:
        Dictionary with motion time series
    """
    n_steps = len(t)
    dt = t[1] - t[0]

    # Initialize
    x = np.zeros((n_steps, 6))
    v = np.zeros((n_steps, 6))
    a = np.zeros((n_steps, 6))

    x[0] = x0
    v[0] = v0

    # Initial acceleration
    a[0] = np.linalg.solve(M, F_t[0] - C @ v[0] - K @ x[0])

    # Effective stiffness
    K_eff = K + gamma/(beta*dt) * C + 1/(beta*dt**2) * M

    # Time stepping
    for i in range(n_steps - 1):
        # Effective force
        F_eff = (
            F_t[i+1] +
            M @ (x[i]/(beta*dt**2) + v[i]/(beta*dt) + (0.5/beta - 1)*a[i]) +
            C @ (gamma/(beta*dt)*x[i] + (gamma/beta - 1)*v[i] + dt*(gamma/(2*beta) - 1)*a[i])
        )

        # Solve for displacement
        x[i+1] = np.linalg.solve(K_eff, F_eff)

        # Update velocity and acceleration
        a[i+1] = (x[i+1] - x[i])/(beta*dt**2) - v[i]/(beta*dt) - (0.5/beta - 1)*a[i]
        v[i+1] = v[i] + dt*((1-gamma)*a[i] + gamma*a[i+1])

    return {
        'time': t,
        'displacement': x,
        'velocity': v,
        'acceleration': a
    }

# Example: Simulate heave response to wave force
t = np.linspace(0, 100, 10000)
dt = t[1] - t[0]

# Simplified system (heave only)
M_simple = np.diag([0, 0, 200e6, 0, 0, 0])  # Heave mass
C_simple = np.diag([0, 0, 100e6, 0, 0, 0])  # Heave damping
K_simple = np.diag([0, 0, 150e6, 0, 0, 0])  # Heave stiffness

# Wave force (10s period, 1 MN amplitude)
F = np.zeros((len(t), 6))
F[:, 2] = 1e6 * np.sin(2*np.pi*t / 10)

# Simulate
result = newmark_beta_integration(
    M_simple, C_simple, K_simple, F,
    x0=np.zeros(6), v0=np.zeros(6), t=t
)

print(f"Max heave: {np.max(np.abs(result['displacement'][:, 2])):.2f} m")
```
