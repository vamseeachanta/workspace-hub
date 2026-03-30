---
name: numpy-numerical-analysis-3-6dof-equations-of-motion
description: 'Sub-skill of numpy-numerical-analysis: 3. 6DOF Equations of Motion.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 3. 6DOF Equations of Motion

## 3. 6DOF Equations of Motion


**6DOF Dynamics:**
```python
def solve_6dof_equation_of_motion(
    mass_matrix: np.ndarray,
    damping_matrix: np.ndarray,
    stiffness_matrix: np.ndarray,
    force_vector: np.ndarray,
    displacement: np.ndarray,
    velocity: np.ndarray,
    dt: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Solve 6DOF equation of motion using Newmark-Beta method.

    [M]{ẍ} + [C]{ẋ} + [K]{x} = {F}

    Args:
        mass_matrix: 6x6 mass matrix [M]
        damping_matrix: 6x6 damping matrix [C]
        stiffness_matrix: 6x6 stiffness matrix [K]
        force_vector: 6x1 force vector {F}
        displacement: Current displacement {x_n}
        velocity: Current velocity {ẋ_n}
        dt: Time step

    Returns:
        (acceleration, velocity, displacement) at next time step
    """
    # Newmark-Beta parameters
    beta = 0.25  # Constant average acceleration
    gamma = 0.5

    # Effective stiffness
    K_eff = (
        mass_matrix / (beta * dt**2) +
        damping_matrix * gamma / (beta * dt) +
        stiffness_matrix
    )

    # Effective force at next time step
    F_eff = (
        force_vector +
        mass_matrix @ (
            displacement / (beta * dt**2) +
            velocity / (beta * dt)
        ) +
        damping_matrix @ (
            displacement * gamma / (beta * dt) -
            velocity * (1 - gamma / beta)
        )
    )

    # Solve for displacement at next time step
    displacement_next = np.linalg.solve(K_eff, F_eff)

    # Calculate velocity at next time step
    velocity_next = (
        gamma / (beta * dt) * (displacement_next - displacement) +
        (1 - gamma / beta) * velocity
    )

    # Calculate acceleration at next time step
    acceleration_next = (
        (displacement_next - displacement) / (beta * dt**2) -
        velocity / (beta * dt)
    )

    return acceleration_next, velocity_next, displacement_next

# Example: Single time step for floating vessel
M = np.diag([100000, 100000, 100000, 5e6, 5e6, 5e6])  # Mass matrix
C = np.diag([50000, 50000, 50000, 2e5, 2e5, 2e5])    # Damping
K = np.diag([1000, 1000, 2000, 5e4, 5e4, 1e4])       # Restoring

F = np.array([1e6, 0, 0, 0, 0, 0])  # Surge force 1 MN
x = np.zeros(6)  # Initial displacement
v = np.zeros(6)  # Initial velocity

a, v_new, x_new = solve_6dof_equation_of_motion(M, C, K, F, x, v, dt=0.01)

print(f"Acceleration: {a}")
print(f"Velocity: {v_new}")
print(f"Displacement: {x_new}")
```
