# Recommended Skills for DigitalModel Repository

> Based on analysis of the digitalmodel repository - a Python library for offshore/marine engineering digital models

## Repository Overview

**DigitalModel** is a Python library focused on lifecycle analysis in offshore/marine engineering, providing:
- Single ASCII data source of truth
- YAML-driven configuration for analysis workflows
- Finite element models, analytical calculations, 3D CAD models
- Integration with OrcaFlex, OrcaWave, AQWA, WAMIT, FreeCAD, GMSH

**Key Engineering Domains:**
- Offshore structures (risers, moorings, umbilicals)
- Marine vessel design and analysis
- Pipeline engineering and pressure calculations
- Fatigue and structural analysis
- Hydrodynamic analysis and wave loading
- Installation analysis and rigging

---

## 1. Programming Skills

### 1.1 Python Scientific Computing ⭐⭐⭐⭐⭐
**Priority**: CRITICAL

**Description**: Python for engineering analysis, numerical computing, and scientific workflows

**Use Cases**:
- Numerical analysis and simulations
- Data processing and transformation
- Engineering calculations
- Integration with scientific libraries

**Key Libraries**:
- **NumPy**: Numerical arrays and linear algebra
- **SciPy**: Scientific computing (optimization, integration, interpolation)
- **Pandas**: Data manipulation and analysis
- **SymPy**: Symbolic mathematics
- **Matplotlib/Plotly**: Visualization

**Skill Coverage**:
```python
# Example: Marine engineering calculations
import numpy as np
from scipy import interpolate, optimize

def calculate_mooring_tension(
    water_depth: float,
    chain_weight: float,
    horizontal_load: float
) -> dict:
    """
    Calculate mooring line tension using catenary equations.

    Parameters:
        water_depth: Water depth (m)
        chain_weight: Chain weight per unit length (kg/m)
        horizontal_load: Horizontal load (kN)

    Returns:
        Dictionary with tension results
    """
    # Catenary calculations
    g = 9.81  # Gravity
    w = chain_weight * g / 1000  # Weight in kN/m

    # Tension at bottom
    T_h = horizontal_load

    # Tension at surface
    T_surface = np.sqrt(T_h**2 + (w * water_depth)**2)

    return {
        'horizontal_tension': T_h,
        'surface_tension': T_surface,
        'vertical_load': w * water_depth
    }
```

---

### 1.2 YAML Configuration Management ⭐⭐⭐⭐⭐
**Priority**: CRITICAL

**Description**: YAML for configuration-driven engineering workflows

**Use Cases**:
- OrcaFlex model configuration
- Analysis parameters and settings
- Vessel specifications
- Environmental conditions
- Result processing configuration

**Skill Coverage**:
```yaml
# Example: Mooring analysis configuration
analysis:
  name: "FPSO Mooring System"
  type: "dynamic_mooring"

environment:
  water_depth: 1500  # meters
  wave_spectrum:
    type: "JONSWAP"
    Hs: 8.5  # meters
    Tp: 12.0  # seconds
  current:
    surface_speed: 1.2  # m/s
    profile: "linear"

vessel:
  name: "FPSO_Model"
  mass: 150000  # tonnes
  length: 320  # meters
  beam: 58  # meters
  draft: 22  # meters

mooring:
  lines: 12
  configuration: "spread"
  chain_diameter: 127  # mm
  pretension: 2000  # kN

analysis_parameters:
  duration: 10800  # seconds (3 hours)
  time_step: 0.05  # seconds
  ramp_time: 300  # seconds

output:
  format: "html"
  include_time_series: true
  statistics: ["max", "min", "mean", "std"]
```

```python
# Python code to process YAML configs
import yaml
from pathlib import Path

def load_analysis_config(config_file: Path) -> dict:
    """Load and validate analysis configuration."""
    with open(config_file) as f:
        config = yaml.safe_load(f)

    # Validate required fields
    required = ['analysis', 'environment', 'vessel']
    for field in required:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")

    return config
```

---

### 1.3 Pandas Data Processing ⭐⭐⭐⭐⭐
**Priority**: CRITICAL

**Description**: Data manipulation, time series analysis, and CSV processing for engineering results

**Use Cases**:
- Process OrcaFlex simulation results
- Time series analysis of vessel motions
- Fatigue damage calculations
- Statistical analysis of loads
- RAO (Response Amplitude Operator) processing

**Skill Coverage**:
```python
import pandas as pd
import numpy as np

def process_orcaflex_results(csv_file: str) -> pd.DataFrame:
    """
    Process OrcaFlex time series results.

    Args:
        csv_file: Path to OrcaFlex results CSV

    Returns:
        Processed DataFrame with statistics
    """
    # Read CSV with relative path
    df = pd.read_csv(csv_file, parse_dates=['Time'])

    # Calculate statistics
    stats = df.groupby('Component').agg({
        'Tension': ['max', 'min', 'mean', 'std'],
        'Angle': ['max', 'min', 'mean']
    }).round(2)

    # Calculate fatigue damage
    df['Stress_Range'] = df['Tension'] / 1000  # Convert to MPa
    df['Cycles'] = 1  # Count cycles

    return df, stats

def calculate_rao(motion_data: pd.DataFrame, wave_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Response Amplitude Operators.

    Args:
        motion_data: Vessel motion time series
        wave_data: Wave elevation time series

    Returns:
        RAO values for each DOF
    """
    from scipy import signal

    # Calculate transfer functions
    raos = {}
    for dof in ['surge', 'sway', 'heave', 'roll', 'pitch', 'yaw']:
        # Cross-spectral density
        f, Pxy = signal.csd(
            wave_data['elevation'],
            motion_data[dof],
            fs=1/motion_data['Time'].diff().mean()
        )

        # Auto-spectral density of wave
        f, Pxx = signal.welch(
            wave_data['elevation'],
            fs=1/wave_data['Time'].diff().mean()
        )

        # RAO = |Pxy| / Pxx
        raos[dof] = np.abs(Pxy) / Pxx

    return pd.DataFrame(raos, index=f)
```

---

### 1.4 NumPy Numerical Analysis ⭐⭐⭐⭐⭐
**Priority**: HIGH

**Description**: Numerical computing for engineering calculations

**Use Cases**:
- Linear algebra for structural analysis
- FFT for frequency domain analysis
- Matrix operations for 6DOF dynamics
- Interpolation and curve fitting

**Skill Coverage**:
```python
import numpy as np
from scipy.interpolate import interp1d
from scipy.fft import fft, fftfreq

def calculate_6dof_motion(
    force_vector: np.ndarray,
    mass_matrix: np.ndarray,
    damping_matrix: np.ndarray
) -> np.ndarray:
    """
    Solve 6DOF motion equation.

    Args:
        force_vector: External forces [6x1]
        mass_matrix: Mass and inertia [6x6]
        damping_matrix: Damping coefficients [6x6]

    Returns:
        Acceleration vector [6x1]
    """
    # Solve: M*a + C*v = F
    # Assuming v = 0 for simplification
    acceleration = np.linalg.solve(mass_matrix, force_vector)
    return acceleration

def perform_spectral_analysis(time_series: np.ndarray, dt: float) -> tuple:
    """
    Perform FFT spectral analysis.

    Args:
        time_series: Time series data
        dt: Time step

    Returns:
        (frequencies, power_spectral_density)
    """
    N = len(time_series)

    # Perform FFT
    yf = fft(time_series)
    xf = fftfreq(N, dt)[:N//2]

    # Calculate PSD
    psd = 2.0/N * np.abs(yf[0:N//2])**2

    return xf, psd
```

---

### 1.5 Plotly Interactive Visualization ✅
**Priority**: HIGH
**Status**: ALREADY CREATED - `skills/charts/plotly/SKILL.md`

**Use Cases**:
- Interactive HTML reports for analysis results
- 3D vessel motion visualizations
- Time series plots of tensions/loads
- Statistical distributions

---

### 1.6 CAD and Mesh Generation (FreeCAD/GMSH) ⭐⭐⭐⭐
**Priority**: MEDIUM

**Description**: Programmatic CAD modeling and mesh generation for FEA

**Use Cases**:
- Automated 3D model generation from YAML configs
- Mesh generation for structural analysis
- Geometry export to various formats
- Integration with FEM solvers

**Skill Coverage**:
```python
# FreeCAD scripting
import FreeCAD as App
import Part

def create_pipeline_model(length: float, diameter: float, thickness: float) -> Part.Shape:
    """
    Create pipeline 3D model.

    Args:
        length: Pipeline length (m)
        diameter: Outer diameter (mm)
        thickness: Wall thickness (mm)

    Returns:
        FreeCAD Part.Shape
    """
    # Create outer cylinder
    outer = Part.makeCylinder(
        diameter/2,
        length * 1000,  # Convert to mm
        App.Vector(0, 0, 0),
        App.Vector(1, 0, 0)
    )

    # Create inner cylinder
    inner = Part.makeCylinder(
        (diameter - 2*thickness)/2,
        length * 1000,
        App.Vector(0, 0, 0),
        App.Vector(1, 0, 0)
    )

    # Subtract to create pipe
    pipe = outer.cut(inner)

    return pipe

# GMSH mesh generation
import gmsh

def generate_mesh(geometry_file: str, element_size: float) -> str:
    """
    Generate FEM mesh with GMSH.

    Args:
        geometry_file: Input geometry file
        element_size: Target element size

    Returns:
        Path to generated mesh file
    """
    gmsh.initialize()
    gmsh.open(geometry_file)

    # Set mesh size
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", element_size)

    # Generate 3D mesh
    gmsh.model.mesh.generate(3)

    # Write mesh
    output_file = geometry_file.replace('.step', '.msh')
    gmsh.write(output_file)

    gmsh.finalize()
    return output_file
```

---

### 1.7 API Integration and Testing (OrcaFlex/AQWA) ⭐⭐⭐⭐
**Priority**: HIGH

**Description**: Integration with licensed engineering software APIs

**Use Cases**:
- OrcaFlex Python API for model creation/analysis
- AQWA integration for hydrodynamic analysis
- Mock APIs for testing without licenses
- Automated simulation workflows

**Skill Coverage**:
```python
# OrcaFlex API integration
try:
    import OrcFxAPI
    ORCAFLEX_AVAILABLE = True
except ImportError:
    ORCAFLEX_AVAILABLE = False

class OrcaFlexWrapper:
    """Wrapper for OrcaFlex API with mock support."""

    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock or not ORCAFLEX_AVAILABLE

        if not self.use_mock:
            self.model = OrcFxAPI.Model()
        else:
            self.model = MockOrcaFlexModel()

    def create_vessel(self, config: dict) -> None:
        """Create vessel from configuration."""
        if not self.use_mock:
            vessel = self.model.CreateObject(OrcFxAPI.otVessel)
            vessel.Length = config['length']
            vessel.Breadth = config['beam']
            vessel.Draught = config['draft']
            vessel.Mass = config['mass']
        else:
            self.model.create_vessel(config)

    def run_analysis(self, duration: float) -> dict:
        """Run dynamic analysis."""
        if not self.use_mock:
            self.model.CalculateStatics()
            self.model.RunSimulation()
            return self._extract_results()
        else:
            return self.model.run_simulation(duration)

# Mock for testing
class MockOrcaFlexModel:
    """Mock OrcaFlex model for testing without license."""

    def __init__(self):
        self.objects = []

    def create_vessel(self, config: dict):
        self.objects.append({'type': 'vessel', 'config': config})

    def run_simulation(self, duration: float) -> dict:
        # Return mock results
        import numpy as np
        time = np.linspace(0, duration, 1000)
        return {
            'time': time,
            'surge': np.random.randn(1000) * 2,
            'heave': np.random.randn(1000) * 1,
            'pitch': np.random.randn(1000) * 0.5
        }
```

---

## 2. Subject Matter Expert (SME) Skills

### 2.1 Marine and Offshore Engineering ⭐⭐⭐⭐⭐
**Priority**: CRITICAL

**Description**: Comprehensive marine/offshore engineering expertise

**Topics**:
- Offshore platform design (fixed, floating)
- FPSO (Floating Production Storage Offloading)
- Subsea systems and pipelines
- Marine operations and installation
- Regulatory standards (DNV, API, ISO)

**Knowledge Areas**:
```markdown
### Platform Types
- **Fixed Platforms**: Jackets, jack-ups
- **Floating Platforms**: Semi-submersibles, TLPs, SPARs, FPSOs
- **Subsea**: Templates, manifolds, umbilicals

### Design Considerations
- Environmental loads (wind, wave, current)
- Structural integrity
- Fatigue life
- Station-keeping (mooring, DP)
- Stability and seakeeping

### Standards
- DNV-RP-H103: Modelling and Analysis of Marine Operations
- API RP 2SK: Stationkeeping Systems
- API RP 2SM: Mooring System Design
- ISO 19901: Offshore structures
```

---

### 2.2 Hydrodynamic Analysis ⭐⭐⭐⭐⭐
**Priority**: CRITICAL

**Description**: Wave-structure interaction and hydrodynamic coefficients

**Topics**:
- Potential flow theory
- Boundary Element Method (BEM)
- Added mass and damping
- RAOs (Response Amplitude Operators)
- Wave drift forces

**Analysis Methods**:
```markdown
### Frequency Domain Analysis
- **Panel Methods**: WAMIT, AQWA, OrcaWave
- **Radiation/Diffraction**: First-order wave forces
- **Added Mass Matrix**: Frequency-dependent coefficients
- **Damping Matrix**: Wave radiation damping

### Time Domain Analysis
- **Cummins Equation**: Convolution integral
- **Retardation Functions**: Time-domain hydrodynamics
- **Second-order Forces**: Slow-drift, sum-frequency

### Key Outputs
- RAOs for 6 DOFs (surge, sway, heave, roll, pitch, yaw)
- Hydrodynamic coefficients (A, B matrices)
- Wave excitation forces
- QTFs (Quadratic Transfer Functions)
```

**Skill Example**:
```python
def process_wamit_output(wamit_file: str) -> dict:
    """
    Process WAMIT hydrodynamic analysis output.

    Args:
        wamit_file: Path to WAMIT .out file

    Returns:
        Dictionary with hydrodynamic coefficients
    """
    # Parse added mass and damping
    added_mass = np.zeros((6, 6, num_frequencies))
    damping = np.zeros((6, 6, num_frequencies))

    # Parse RAOs
    raos = {}
    for dof in range(6):
        raos[dof] = {
            'amplitude': [],
            'phase': [],
            'frequency': []
        }

    return {
        'added_mass': added_mass,
        'damping': damping,
        'raos': raos
    }
```

---

### 2.3 Mooring Analysis ⭐⭐⭐⭐⭐
**Priority**: CRITICAL

**Description**: Mooring system design and analysis

**Topics**:
- Catenary moorings
- Taut moorings
- Dynamic analysis
- Tension calculations
- Fatigue assessment

**Design Considerations**:
```markdown
### Mooring Types
- **Catenary**: Chain, wire, combination
- **Taut**: Polyester, steel wire
- **Semi-taut**: Hybrid configurations

### Analysis Types
- **Static**: Initial configuration, pretension
- **Quasi-static**: Slow-drift motions
- **Dynamic**: Wave-frequency response

### Failure Modes
- Line breakage (ULS)
- Fatigue (FLS)
- Clashing (ALS)
- Anchor capacity

### Standards
- API RP 2SK
- DNV-OS-E301
- ISO 19901-7
```

---

### 2.4 Ship Dynamics and 6DOF Motion ⭐⭐⭐⭐⭐
**Priority**: HIGH

**Description**: Vessel motion analysis and seakeeping

**Topics**:
- 6 Degrees of Freedom (surge, sway, heave, roll, pitch, yaw)
- Motion equations
- Natural periods
- Seakeeping performance

**Equations of Motion**:
```python
def solve_6dof_motion(
    mass_matrix: np.ndarray,  # [6x6]
    added_mass: np.ndarray,   # [6x6]
    damping: np.ndarray,       # [6x6]
    stiffness: np.ndarray,     # [6x6]
    force: np.ndarray,         # [6x1]
    omega: float               # Wave frequency
) -> np.ndarray:
    """
    Solve 6DOF motion in frequency domain.

    Equation: (-ω²[M+A(ω)] + iω[B(ω)] + [C])X = F

    Args:
        mass_matrix: Vessel mass and inertia
        added_mass: Frequency-dependent added mass
        damping: Frequency-dependent damping
        stiffness: Restoring stiffness
        force: Wave excitation force
        omega: Wave frequency (rad/s)

    Returns:
        Motion response vector [6x1]
    """
    # Dynamic stiffness matrix
    Z = (-omega**2 * (mass_matrix + added_mass) +
         1j * omega * damping +
         stiffness)

    # Solve for motion
    X = np.linalg.solve(Z, force)

    return X

# Calculate RAO
rao_amplitude = np.abs(X) / wave_amplitude
rao_phase = np.angle(X, deg=True)
```

---

### 2.5 Fatigue Analysis ⭐⭐⭐⭐
**Priority**: HIGH

**Description**: Fatigue life assessment using S-N curves

**Topics**:
- Palmgren-Miner rule
- Rainflow counting
- S-N curves
- Stress concentration factors

**Skill Coverage**:
```python
from scipy import stats
import rainflow

def calculate_fatigue_damage(
    stress_history: np.ndarray,
    sn_curve: dict,
    scf: float = 1.0
) -> float:
    """
    Calculate cumulative fatigue damage.

    Args:
        stress_history: Time series of stress (MPa)
        sn_curve: S-N curve parameters {'m': slope, 'a': intercept}
        scf: Stress concentration factor

    Returns:
        Cumulative damage ratio
    """
    # Apply SCF
    stress_history = stress_history * scf

    # Rainflow count cycles
    cycles = rainflow.count_cycles(stress_history)

    # Calculate damage using Palmgren-Miner
    damage = 0.0
    m = sn_curve['m']
    a = sn_curve['a']

    for stress_range, count in cycles:
        # N = a * S^(-m)
        N = a * (stress_range ** (-m))
        damage += count / N

    return damage

def estimate_fatigue_life(
    damage_per_year: float,
    design_life: float = 25
) -> dict:
    """
    Estimate fatigue life.

    Args:
        damage_per_year: Annual damage
        design_life: Design life (years)

    Returns:
        Fatigue assessment results
    """
    total_damage = damage_per_year * design_life

    return {
        'annual_damage': damage_per_year,
        'design_life_damage': total_damage,
        'utilization': total_damage / 1.0,  # Limit = 1.0
        'remaining_life': (1.0 - total_damage) / damage_per_year if total_damage < 1.0 else 0
    }
```

---

### 2.6 Wave Theory and Spectra ⭐⭐⭐⭐
**Priority**: HIGH

**Description**: Ocean wave modeling and spectral analysis

**Topics**:
- Wave theories (Airy, Stokes, Stream function)
- Wave spectra (JONSWAP, Pierson-Moskowitz)
- Wave statistics
- Irregular waves

**Wave Spectra**:
```python
def jonswap_spectrum(
    frequencies: np.ndarray,
    Hs: float,
    Tp: float,
    gamma: float = 3.3
) -> np.ndarray:
    """
    Calculate JONSWAP wave spectrum.

    Args:
        frequencies: Frequency array (Hz)
        Hs: Significant wave height (m)
        Tp: Peak period (s)
        gamma: Peak enhancement factor

    Returns:
        Spectral density S(f)
    """
    fp = 1 / Tp  # Peak frequency
    omega_p = 2 * np.pi * fp
    omega = 2 * np.pi * frequencies

    # Pierson-Moskowitz spectrum
    alpha = 0.0081
    beta = 0.74
    S_PM = (alpha * 9.81**2 / omega**5) * \
           np.exp(-beta * (omega_p / omega)**4)

    # Peak enhancement
    sigma = np.where(omega <= omega_p, 0.07, 0.09)
    r = np.exp(-(omega - omega_p)**2 / (2 * sigma**2 * omega_p**2))

    S_JONSWAP = S_PM * gamma**r

    return S_JONSWAP

def calculate_wave_statistics(spectrum: np.ndarray, df: float) -> dict:
    """
    Calculate wave statistics from spectrum.

    Args:
        spectrum: Spectral density array
        df: Frequency step

    Returns:
        Wave statistics
    """
    # Spectral moments
    m0 = np.sum(spectrum) * df
    m2 = np.sum(spectrum * frequencies**2) * df

    # Characteristic wave heights
    Hm0 = 4 * np.sqrt(m0)  # Spectral significant wave height
    Tz = np.sqrt(m0 / m2)   # Zero-crossing period

    return {
        'Hm0': Hm0,
        'Tz': Tz,
        'H_max': 1.86 * Hm0  # Expected maximum (3hr storm)
    }
```

---

### 2.7 Structural Analysis ⭐⭐⭐⭐
**Priority**: MEDIUM

**Description**: Structural integrity and stress analysis

**Topics**:
- Beam theory
- Buckling analysis
- Ultimate limit state
- Accidental limit state

---

### 2.8 OrcaFlex/OrcaWave Specialist ⭐⭐⭐⭐⭐
**Priority**: CRITICAL

**Description**: Expert knowledge of Orcina software suite

**Topics**:
- Model building and configuration
- Analysis setup and execution
- Results post-processing
- Best practices and workflows

---

### 2.9 Risk Assessment ⭐⭐⭐
**Priority**: MEDIUM

**Description**: Probabilistic risk analysis

**Topics**:
- Reliability analysis
- Monte Carlo simulation
- Extreme value statistics
- Safety factors

---

## 3. Recommended Skill Priority Matrix

| Skill | Type | Priority | Difficulty | Time to Create |
|-------|------|----------|------------|----------------|
| Python Scientific Computing | Programming | ⭐⭐⭐⭐⭐ | Medium | 4-6 hours |
| YAML Configuration | Programming | ⭐⭐⭐⭐⭐ | Easy | 2-3 hours |
| Pandas Data Processing | Programming | ⭐⭐⭐⭐⭐ | Medium | 3-4 hours |
| NumPy Numerical Analysis | Programming | ⭐⭐⭐⭐⭐ | Medium | 3-4 hours |
| Plotly Visualization | Programming | ⭐⭐⭐⭐⭐ | Easy | ✅ DONE |
| CAD/Mesh (FreeCAD/GMSH) | Programming | ⭐⭐⭐⭐ | Hard | 6-8 hours |
| API Integration (OrcaFlex) | Programming | ⭐⭐⭐⭐ | Hard | 5-6 hours |
| Marine/Offshore Engineering | SME | ⭐⭐⭐⭐⭐ | Expert | 8-10 hours |
| Hydrodynamic Analysis | SME | ⭐⭐⭐⭐⭐ | Expert | 8-10 hours |
| Mooring Analysis | SME | ⭐⭐⭐⭐⭐ | Expert | 6-8 hours |
| Ship Dynamics (6DOF) | SME | ⭐⭐⭐⭐⭐ | Expert | 6-8 hours |
| Fatigue Analysis | SME | ⭐⭐⭐⭐ | Advanced | 4-6 hours |
| Wave Theory | SME | ⭐⭐⭐⭐ | Advanced | 5-6 hours |
| Structural Analysis | SME | ⭐⭐⭐⭐ | Advanced | 5-6 hours |
| OrcaFlex Specialist | SME | ⭐⭐⭐⭐⭐ | Expert | 6-8 hours |
| Risk Assessment | SME | ⭐⭐⭐ | Advanced | 4-5 hours |

---

## 4. Implementation Roadmap

### Phase 1: Critical Programming Skills (Week 1-2)
1. ✅ Plotly Visualization (COMPLETED)
2. Python Scientific Computing
3. YAML Configuration Management
4. Pandas Data Processing
5. NumPy Numerical Analysis

### Phase 2: Software Integration (Week 3)
6. OrcaFlex API Integration
7. CAD and Mesh Generation

### Phase 3: Core SME Skills (Week 4-5)
8. Marine and Offshore Engineering
9. Hydrodynamic Analysis
10. Mooring Analysis
11. Ship Dynamics and 6DOF

### Phase 4: Specialized SME Skills (Week 6)
12. Fatigue Analysis
13. Wave Theory and Spectra
14. OrcaFlex/OrcaWave Specialist

### Phase 5: Advanced Topics (Week 7)
15. Structural Analysis
16. Risk Assessment

---

## 5. Skill Integration Examples

### Example 1: Complete Mooring Analysis Workflow

```yaml
# config/mooring_analysis.yaml
analysis:
  name: "FPSO Mooring System"
  vessel:
    length: 320
    beam: 58
    draft: 22
    mass: 150000
  mooring:
    lines: 12
    configuration: "spread"
  environment:
    Hs: 8.5
    Tp: 12.0
```

```python
# Workflow using multiple skills
from skills.yaml_config import load_config
from skills.orcaflex_api import OrcaFlexWrapper
from skills.pandas_processing import process_results
from skills.fatigue_analysis import calculate_fatigue
from skills.plotly_viz import create_interactive_report

# Load config (YAML skill)
config = load_config('config/mooring_analysis.yaml')

# Run analysis (OrcaFlex API skill)
model = OrcaFlexWrapper()
model.create_from_config(config)
results = model.run_analysis()

# Process results (Pandas skill)
stats = process_results(results)

# Fatigue assessment (Fatigue Analysis SME skill)
fatigue = calculate_fatigue(results['tension_history'])

# Generate report (Plotly skill)
create_interactive_report(stats, fatigue, output='reports/mooring_analysis.html')
```

---

## 6. Next Steps

1. **Review and prioritize** skills based on current digitalmodel needs
2. **Create skills** following Anthropic skills format (YAML frontmatter + markdown)
3. **Organize in** `skills/` directory with subdirectories:
   - `skills/programming/` - Programming skills
   - `skills/sme/` - Subject matter expert skills
4. **Test skills** with real digitalmodel use cases
5. **Iterate** based on feedback and usage

---

**Total Recommended Skills**: 16 (1 completed, 15 to create)
**Estimated Total Time**: 80-100 hours
**Priority Focus**: Python ecosystem + Marine engineering fundamentals
