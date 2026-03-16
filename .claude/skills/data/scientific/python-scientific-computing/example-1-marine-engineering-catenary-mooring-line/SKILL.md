---
name: python-scientific-computing-example-1-marine-engineering-catenary-mooring-line
description: 'Sub-skill of python-scientific-computing: Example 1: Marine Engineering
  - Catenary Mooring Line (+5).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Example 1: Marine Engineering - Catenary Mooring Line (+5)

## Example 1: Marine Engineering - Catenary Mooring Line


```python
import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt

def catenary_mooring_analysis(
    water_depth: float,
    horizontal_distance: float,
    chain_weight: float,  # kg/m
    required_tension: float  # kN

*See sub-skills for full details.*

## Example 2: Structural Dynamics - Natural Frequency


```python
import numpy as np
from scipy.linalg import eig

def calculate_natural_frequencies(
    mass_matrix: np.ndarray,
    stiffness_matrix: np.ndarray,
    num_modes: int = 5
) -> dict:
    """

*See sub-skills for full details.*

## Example 3: Hydrodynamic Analysis - Wave Spectrum


```python
import numpy as np
from scipy.integrate import trapz

def jonswap_spectrum(
    frequencies: np.ndarray,
    Hs: float,
    Tp: float,
    gamma: float = 3.3
) -> np.ndarray:

*See sub-skills for full details.*

## Example 4: Numerical Integration - Velocity to Displacement


```python
import numpy as np
from scipy.integrate import cumtrapz

def integrate_motion_time_history(
    time: np.ndarray,
    acceleration: np.ndarray
) -> dict:
    """
    Integrate acceleration to get velocity and displacement.

*See sub-skills for full details.*

## Example 5: Optimization - Mooring Pretension


```python
from scipy.optimize import minimize
import numpy as np

def optimize_mooring_pretension(
    num_lines: int,
    water_depth: float,
    target_offset: float,
    max_tension: float
) -> dict:

*See sub-skills for full details.*

## Example 6: Symbolic Mathematics - Beam Deflection


```python
from sympy import symbols, diff, integrate, simplify, lambdify
from sympy import Function, Eq, dsolve
import numpy as np
import matplotlib.pyplot as plt

def beam_deflection_symbolic():
    """
    Solve beam deflection equation symbolically.


*See sub-skills for full details.*
