---
name: numpy-numerical-analysis-5-linear-algebra-operations
description: 'Sub-skill of numpy-numerical-analysis: 5. Linear Algebra Operations.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 5. Linear Algebra Operations

## 5. Linear Algebra Operations


**Eigenvalue Analysis:**
```python
def natural_frequency_analysis(
    mass_matrix: np.ndarray,
    stiffness_matrix: np.ndarray
) -> dict:
    """
    Perform eigenvalue analysis to find natural frequencies and mode shapes.

    [K]{ϕ} = ω²[M]{ϕ}

    Args:
        mass_matrix: Mass matrix [M]
        stiffness_matrix: Stiffness matrix [K]

    Returns:
        Dictionary with natural frequencies and mode shapes
    """
    # Solve generalized eigenvalue problem
    eigenvalues, eigenvectors = np.linalg.eig(
        np.linalg.solve(mass_matrix, stiffness_matrix)
    )

    # Natural frequencies (rad/s)
    natural_frequencies_rad = np.sqrt(eigenvalues)

    # Natural frequencies (Hz)
    natural_frequencies_hz = natural_frequencies_rad / (2 * np.pi)

    # Sort by frequency
    sort_indices = np.argsort(natural_frequencies_hz)
    natural_frequencies_hz = natural_frequencies_hz[sort_indices]
    eigenvectors = eigenvectors[:, sort_indices]

    # Periods
    periods = 1 / natural_frequencies_hz

    return {
        'frequencies_hz': natural_frequencies_hz,
        'frequencies_rad_s': natural_frequencies_rad[sort_indices],
        'periods_s': periods,
        'mode_shapes': eigenvectors
    }

# Example: FPSO natural frequencies
# 6DOF system
M = np.diag([150000, 150000, 150000, 1e7, 1e7, 5e6])  # Mass matrix (tonnes, tonne-m²)
K = np.diag([500, 500, 3000, 5e5, 5e5, 1e5])          # Stiffness (kN/m, kN-m/rad)

results = natural_frequency_analysis(M, K)

print("Natural Frequencies:")
for i, (freq, period) in enumerate(zip(results['frequencies_hz'], results['periods_s'])):
    dof_names = ['Surge', 'Sway', 'Heave', 'Roll', 'Pitch', 'Yaw']
    print(f"  Mode {i+1} ({dof_names[i]}): f = {freq:.4f} Hz, T = {period:.2f} s")
```

**Matrix Decomposition:**
```python
def lu_decomposition_solve(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Solve linear system using LU decomposition.

    Args:
        A: Coefficient matrix
        b: Right-hand side vector

    Returns:
        Solution vector x
    """
    from scipy.linalg import lu

    # LU decomposition
    P, L, U = lu(A)

    # Solve Ly = Pb
    y = np.linalg.solve(L, P @ b)

    # Solve Ux = y
    x = np.linalg.solve(U, y)

    return x

# Example
A = np.array([[4, -1, 0],
              [-1, 4, -1],
              [0, -1, 3]])
b = np.array([15, 10, 10])

x = lu_decomposition_solve(A, b)
print(f"Solution: {x}")
```
