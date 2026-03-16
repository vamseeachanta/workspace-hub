---
name: python-scientific-computing-pattern-1-load-and-process-engineering-data
description: 'Sub-skill of python-scientific-computing: Pattern 1: Load and Process
  Engineering Data (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Pattern 1: Load and Process Engineering Data (+2)

## Pattern 1: Load and Process Engineering Data


```python
import numpy as np

# Load CSV data
data = np.loadtxt('../data/measurements.csv', delimiter=',', skiprows=1)

# Extract columns
time = data[:, 0]
temperature = data[:, 1]
pressure = data[:, 2]

*See sub-skills for full details.*

## Pattern 2: Solve System of Equations


```python
from scipy.optimize import fsolve

def system(vars):
    x, y, z = vars
    eq1 = x + y + z - 6
    eq2 = 2*x - y + z - 1
    eq3 = x + 2*y - z - 3
    return [eq1, eq2, eq3]

solution = fsolve(system, [1, 1, 1])
```

## Pattern 3: Curve Fitting


```python
from scipy.optimize import curve_fit

def model(x, a, b, c):
    return a * np.exp(-b * x) + c

# Fit data
params, covariance = curve_fit(model, x_data, y_data)
a_fit, b_fit, c_fit = params
```
