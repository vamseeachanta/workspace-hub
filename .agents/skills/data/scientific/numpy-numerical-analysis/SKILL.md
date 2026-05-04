---
name: numpy-numerical-analysis
version: 1.0.0
description: NumPy for matrix operations, FFT, linear algebra, and numerical computations
  in marine engineering
type: reference
author: workspace-hub
category: data
tags:
- numpy
- numerical-analysis
- matrix-operations
- fft
- linear-algebra
- engineering
platforms:
- python
capabilities: []
requires: []
---

# Numpy Numerical Analysis

## When to Use This Skill

Use NumPy numerical analysis when you need:
- **Matrix operations** - 6DOF equations of motion, mass matrices, stiffness matrices
- **FFT analysis** - Frequency domain analysis, spectral density, response spectra
- **Linear algebra** - Solve linear systems, eigenvalue analysis, matrix decomposition
- **Array operations** - Efficient computations on large datasets
- **Numerical integration** - Time-stepping, ODE solvers
- **Signal processing** - Filtering, windowing, convolution

**Avoid when:**
- Symbolic mathematics needed (use SymPy)
- Sparse matrices dominate (use SciPy sparse)
- GPU acceleration required (use CuPy or JAX)
- Distributed computing needed (use Dask)

## Complete Examples

### Example 1: 6DOF Time-Domain Simulation

```python
import numpy as np
import plotly.graph_objects as go

def simulate_6dof_vessel_motion(
    mass_matrix: np.ndarray,
    damping_matrix: np.ndarray,
    stiffness_matrix: np.ndarray,
    force_time_series: np.ndarray,
    time: np.ndarray

*See sub-skills for full details.*
### Example 2: RAO Calculation from FFT

```python
def calculate_rao_from_time_series(
    wave_elevation: np.ndarray,
    vessel_response: np.ndarray,
    dt: float
) -> tuple[np.ndarray, np.ndarray]:
    """
    Calculate Response Amplitude Operator (RAO) from time series.

    RAO(ω) = |Response(ω)| / |Wave(ω)|

*See sub-skills for full details.*
### Example 3: Mooring Stiffness Matrix

```python
def calculate_mooring_stiffness_matrix(
    num_lines: int,
    pretension: float,
    fairlead_radius: float,
    fairlead_depth: float,
    line_azimuth: np.ndarray,
    weight_per_length: float
) -> np.ndarray:
    """

*See sub-skills for full details.*
### Example 4: Statistical Analysis of Extremes

```python
def extreme_value_statistics(
    data: np.ndarray,
    method: str = '3hr_max'
) -> dict:
    """
    Perform extreme value statistical analysis.

    Args:
        data: Time series data

*See sub-skills for full details.*
### Example 5: Convolution for Impulse Response

```python
def convolve_impulse_response(
    impulse_response: np.ndarray,
    force_time_series: np.ndarray,
    dt: float
) -> np.ndarray:
    """
    Convolve impulse response with force time series.

    Response(t) = ∫ h(τ) * F(t-τ) dτ

*See sub-skills for full details.*

## Resources

- **NumPy Documentation**: https://numpy.org/doc/
- **NumPy for MATLAB Users**: https://numpy.org/doc/stable/user/numpy-for-matlab-users.html
- **Linear Algebra**: https://numpy.org/doc/stable/reference/routines.linalg.html
- **FFT Module**: https://numpy.org/doc/stable/reference/routines.fft.html
- **SciPy (extends NumPy)**: https://scipy.org/

---

**Use this skill for all numerical computations in DigitalModel!**

## Sub-Skills

- [1. Array Creation and Operations (+1)](1-array-creation-and-operations/SKILL.md)
- [3. 6DOF Equations of Motion](3-6dof-equations-of-motion/SKILL.md)
- [4. FFT and Frequency Analysis](4-fft-and-frequency-analysis/SKILL.md)
- [5. Linear Algebra Operations](5-linear-algebra-operations/SKILL.md)
- [6. Numerical Integration](6-numerical-integration/SKILL.md)
- [1. Use Vectorization (+3)](1-use-vectorization/SKILL.md)
