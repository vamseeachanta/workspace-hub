---
name: python-scicomp-1-numpy-arrays-linear-algebra
description: 'Sub-skill of python-scientific-computing: 1. NumPy - Numerical Arrays
  and Linear Algebra (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. NumPy - Numerical Arrays and Linear Algebra (+2)

## 1. NumPy - Numerical Arrays and Linear Algebra


**Array Operations:**
```python
import numpy as np

# Create arrays
array_1d = np.array([1, 2, 3, 4, 5])
array_2d = np.array([[1, 2, 3], [4, 5, 6]])

# Special arrays
zeros = np.zeros((3, 3))
ones = np.ones((2, 4))
identity = np.eye(3)
linspace = np.linspace(0, 10, 100)  # 100 points from 0 to 10

# Array operations (vectorized - fast!)
x = np.linspace(0, 2*np.pi, 1000)
y = np.sin(x) * np.exp(-x/10)
```

**Linear Algebra:**
```python
# Matrix operations
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# Matrix multiplication
C = A @ B  # or np.dot(A, B)

# Inverse
A_inv = np.linalg.inv(A)

# Eigenvalues and eigenvectors
eigenvalues, eigenvectors = np.linalg.eig(A)

# Solve linear system Ax = b
b = np.array([1, 2])
x = np.linalg.solve(A, b)

# Determinant
det_A = np.linalg.det(A)
```


## 2. SciPy - Scientific Computing


**Optimization:**
```python
from scipy import optimize

# Minimize function
def rosenbrock(x):
    return (1 - x[0])**2 + 100*(x[1] - x[0]**2)**2

result = optimize.minimize(rosenbrock, x0=[0, 0], method='BFGS')
print(f"Minimum at: {result.x}")

# Root finding
def equations(vars):
    x, y = vars
    eq1 = x**2 + y**2 - 4
    eq2 = x - y - 1
    return [eq1, eq2]

solution = optimize.fsolve(equations, [1, 1])
```

**Integration:**
```python
from scipy import integrate

# Numerical integration
def integrand(x):
    return x**2

result, error = integrate.quad(integrand, 0, 1)  # Integrate from 0 to 1
print(f"Result: {result}, Error: {error}")

# ODE solver
def ode_system(t, y):
    # dy/dt = -2y
    return -2 * y

solution = integrate.solve_ivp(
    ode_system,
    t_span=[0, 10],
    y0=[1],
    t_eval=np.linspace(0, 10, 100)
)
```

**Interpolation:**
```python
from scipy import interpolate

# 1D interpolation
x = np.array([0, 1, 2, 3, 4])
y = np.array([0, 0.5, 1.0, 1.5, 2.0])

f_linear = interpolate.interp1d(x, y, kind='linear')
f_cubic = interpolate.interp1d(x, y, kind='cubic')

x_new = np.linspace(0, 4, 100)
y_linear = f_linear(x_new)
y_cubic = f_cubic(x_new)

# 2D interpolation
from scipy.interpolate import griddata
points = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
values = np.array([0, 1, 1, 2])
grid_x, grid_y = np.mgrid[0:1:100j, 0:1:100j]
grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')
```


## 3. SymPy - Symbolic Mathematics


**Symbolic Expressions:**
```python
from sympy import symbols, diff, integrate, solve, simplify, expand
from sympy import sin, cos, exp, log, sqrt, pi

# Define symbols
x, y, z = symbols('x y z')
t = symbols('t', real=True, positive=True)

# Create expressions
expr = x**2 + 2*x + 1
simplified = simplify(expr)
expanded = expand((x + 1)**3)

# Differentiation
f = x**3 + 2*x**2 + x
df_dx = diff(f, x)  # 3*x**2 + 4*x + 1
d2f_dx2 = diff(f, x, 2)  # 6*x + 4

# Integration
indefinite = integrate(x**2, x)  # x**3/3
definite = integrate(x**2, (x, 0, 1))  # 1/3

# Solve equations
equation = x**2 - 4
solutions = solve(equation, x)  # [-2, 2]

# System of equations
eq1 = x + y - 5
eq2 = x - y - 1
sol = solve([eq1, eq2], [x, y])  # {x: 3, y: 2}
```
