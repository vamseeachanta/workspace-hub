---
name: numpy-numerical-analysis-1-array-creation-and-operations
description: 'Sub-skill of numpy-numerical-analysis: 1. Array Creation and Operations
  (+1).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Array Creation and Operations (+1)

## 1. Array Creation and Operations


**Array Creation:**
```python
import numpy as np

# Create arrays
zeros = np.zeros((3, 3))
ones = np.ones((3, 3))
identity = np.eye(3)
arange = np.arange(0, 10, 0.1)  # 0 to 10 with step 0.1
linspace = np.linspace(0, 10, 100)  # 100 points from 0 to 10

# From list
arr = np.array([1, 2, 3, 4, 5])

# Multi-dimensional
matrix = np.array([[1, 2, 3],
                   [4, 5, 6],
                   [7, 8, 9]])

# Random arrays
random_uniform = np.random.rand(3, 3)  # Uniform [0, 1)
random_normal = np.random.randn(3, 3)  # Standard normal
random_int = np.random.randint(0, 100, size=(3, 3))
```

**Array Operations:**
```python
# Element-wise operations
a = np.array([1, 2, 3, 4, 5])
b = np.array([10, 20, 30, 40, 50])

c = a + b  # [11, 22, 33, 44, 55]
d = a * b  # [10, 40, 90, 160, 250]
e = a ** 2  # [1, 4, 9, 16, 25]

# Mathematical functions
sin_a = np.sin(a)
cos_a = np.cos(a)
exp_a = np.exp(a)
log_a = np.log(a)
sqrt_a = np.sqrt(a)

# Statistical operations
mean = np.mean(a)
std = np.std(a)
var = np.var(a)
min_val = np.min(a)
max_val = np.max(a)
```


## 2. Matrix Operations


**Matrix Multiplication:**
```python
def compute_force_response(
    mass_matrix: np.ndarray,
    stiffness_matrix: np.ndarray,
    force_vector: np.ndarray
) -> np.ndarray:
    """
    Compute structural response: F = K * x
    Solve for displacement: x = K^-1 * F

    Args:
        mass_matrix: Mass matrix [M]
        stiffness_matrix: Stiffness matrix [K]
        force_vector: Applied force vector {F}

    Returns:
        Displacement vector {x}
    """
    # Static response (ignoring mass for now)
    displacement = np.linalg.solve(stiffness_matrix, force_vector)

    return displacement

# Example: 3DOF spring-mass system
K = np.array([
    [200, -100, 0],
    [-100, 200, -100],
    [0, -100, 100]
])  # Stiffness matrix (N/m)

F = np.array([1000, 0, 0])  # Force at first node (N)

x = compute_force_response(None, K, F)
print(f"Displacements: {x} m")
```

**Matrix Properties:**
```python
def analyze_matrix_properties(matrix: np.ndarray) -> dict:
    """
    Analyze matrix properties for structural analysis.

    Args:
        matrix: Input matrix (mass or stiffness)

    Returns:
        Dictionary with matrix properties
    """
    properties = {}

    # Determinant
    properties['determinant'] = np.linalg.det(matrix)

    # Condition number (numerical stability indicator)
    properties['condition_number'] = np.linalg.cond(matrix)

    # Rank
    properties['rank'] = np.linalg.matrix_rank(matrix)

    # Eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    properties['eigenvalues'] = eigenvalues
    properties['eigenvectors'] = eigenvectors

    # Is symmetric?
    properties['is_symmetric'] = np.allclose(matrix, matrix.T)

    # Is positive definite? (all eigenvalues > 0)
    properties['is_positive_definite'] = np.all(eigenvalues > 0)

    return properties

# Example: Check stiffness matrix properties
K = np.array([
    [200, -100, 0],
    [-100, 200, -100],
    [0, -100, 100]
])

props = analyze_matrix_properties(K)
print(f"Determinant: {props['determinant']:.2f}")
print(f"Condition number: {props['condition_number']:.2f}")
print(f"Eigenvalues: {props['eigenvalues']}")
print(f"Positive definite: {props['is_positive_definite']}")
```
