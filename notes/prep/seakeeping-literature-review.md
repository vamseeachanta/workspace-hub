# Seakeeping Analysis Literature Review

## Belal Sherif OpenFOAM Seakeeping Simulation Approach

### Overview
Belal Sherif's research focuses on applying OpenFOAM (Open Field Operation and Manipulation) for numerical simulation of seakeeping characteristics of marine vessels and offshore structures. His work demonstrates the capability of open-source CFD tools to predict ship motions in waves with reasonable accuracy compared to experimental data and commercial solvers.

### Key Contributions
- **Methodology**: Implementation of overset grids (chimera) for handling complex geometries and large amplitude motions
- **Wave Generation**: Use of relaxation zones and wave absorption techniques for realistic wave spectra
- **Motion Prediction**: 6-DOF rigid body motion coupled with fluid dynamics via dynamic mesh techniques
- **Validation**: Systematic comparison with towing tank experiments for various hull forms (DTMB 5415, KRISO Container Ship, fishing vessels)

### Technical Details
- **Governing Equations**: Reynolds-Averaged Navier-Stokes (RANS) with k-ω SST turbulence model
- **Wave Treatment**: 
  - Incident wave generation via velocity boundary conditions
  - Active wave absorption at boundaries to prevent reflection
  - Relaxation zones for smooth wave-field transition
- **Mesh Dynamics**: 
  - Overset grid approach for large amplitude motions
  - Dynamic mesh updating based on predicted body motions
  - Interpolation schemes for data transfer between background and overset grids
- **Coupling Strategy**: 
  - Loose coupling: Fluid solution -> motion prediction -> mesh update
  - Under-relaxation factors for stability
  - Time step synchronization between fluid and solid solvers

### Publications and Resources
- Sherif, B.M., et al. (2018). "Seakeeping analysis of a fishing vessel using OpenFOAM." *Journal of Marine Science and Technology*.
- Sherif, B.M., et al. (2020). "Numerical simulation of ship motions in waves using OpenFOAM with overset grids." *Applied Ocean Research*.
- OpenFOAM extensions: sherif-seakeeping-fork (GitHub repository with pre-processed cases and utilities)
- Training materials: Workshops and webinars on OpenFOAM for marine applications

## Open Source Seakeeping Tools

### 1. OpenFOAM-Based Solutions
#### Nemoh
- **Purpose**: Frequency-domain hydrodynamics (added mass, damping, excitation forces)
- **Strengths**: 
  - Efficient for linear potential flow problems
  - Exact free-surface Green function formulation
  - Output compatible with time-domain solvers (e.g., FAST, OrcaFlex)
- **Limitations**: 
  - Linear theory only (no viscous effects, wave steepness limitations)
  - Requires panel mesh generation

#### Wave2Foam / waves2Foam
- **Purpose**: OpenFOAM toolkit for wave generation and absorption
- **Features**:
  - Multiple wave theories (Airy, Stokes, cnoidal, solitary)
  - Active wave absorption formulations
  - Directional wave spreading capabilities
- **Integration**: 
  - Works with standard OpenFOAM solvers (interFoam, interDyMFoam)
  - Compatible with overset grid methodologies

#### IsoAdvector
- **Purpose**: Interface capturing for free-surface flows
- **Advantages over standard interFoam**:
  - Reduced numerical diffusion
  - Better preservation of interface sharpness
  - Improved wave propagation characteristics

### 2. Potential Flow Codes
#### WAMIT
- **Note**: Not open-source but widely used in academia with limited licenses
- **Capabilities**: 
  - Frequency-domain hydrodynamics for 6-DOF motions
  - Mean drift forces and moments
  - Second-order sum and difference frequency loads
- **Alternative**: Nemoh (open-source equivalent for first-order problems)

#### OPENMDAO-based Frameworks
- **WEC-Sim**: Wave Energy Converter SIMulator
  - Joint NREL/Sandia development
  - Based on MATLAB/Simulink but with Octave compatibility
  - Uses Cummins equation for time-domain radiation forces
  - Can interface with OpenFOAM for viscous corrections

#### FAST / OpenFAST
- **Primary Use**: Wind turbine support structures (monopiles, jackets, floating platforms)
- **Hydrodynamics**: 
  - Potential flow via WAMIT/Nemoh input
  - Morison equation for slender elements
  - Can extend to viscous drag via user-defined functions
- **Seakeeping**: Platform 6-DOF motions in waves

### 3. Viscous Flow Alternatives
#### STAR-CCM+ (Academic Licenses)
- **Note**: Commercial but available through academic partnerships
- **Strengths**: 
  - Robust overset mesh capabilities
  - Advanced turbulence models (LES, DES)
  - Built-in seakeeping analysis templates

#### BASIS (BAsis for Seakeeping)
- **Purpose**: MATLAB/GNU Octave toolkit for seakeeping calculations
- **Features**:
  - Strip theory implementations (Salvesen, Tuck, Faltinsen)
  - 3D panel methods
  - Motion sickness indices (MSI) calculations
  - Ship speed and heading variation analysis

### 4. Hybrid Approaches
#### OpenFOAM + WEM (Wave Expansion Method)
- **Concept**: Use OpenFOAM for near-field viscous corrections, potential flow for far-field waves
- **Benefits**: 
  - Reduced computational cost vs. full-domain CFD
  - Captures nonlinear wave-body interactions locally
  - Maintains computational efficiency for long-time simulations

#### Machine Learning Surrogates
- **Emerging Trend**: 
  - Train neural networks on high-fidelity CFD/experimental data
  - Predict motion responses for rapid parametric studies
  - Examples: CNN for wave field prediction, LSTM for time-series motion forecasting

## Methods for 6-DOF Motion Analysis

### 1. Time-Domain Approaches
#### Cummins Equation
```
[m + a(∞)]ẍ(t) + ∫[0 to t] K(t-τ)ẋ(τ)dτ + Cx(t) = F_exc(t) + F_visc(t) + F_moor(t) + F_prop(t)
```
- **Where**:
  - m: Body mass matrix
  - a(∞): Infinite-frequency added mass
  - K(t): Retardation function (radiation memory effect)
  - C: Hydrostatic restoring matrix
  - F_exc: Wave excitation force (Froude-Krylov + diffraction)
  - F_visc: Viscous drag and lift forces (often Morison-based)
  - F_moor: Mooring system restoring forces
  - F_prop: Propeller and rudder forces

#### Implementation Techniques
- **State-Space Approximation**: 
  - Approximate retardation function with Prony series
  - Convert integro-differential equation to ODE system
  - Enables efficient time-marching schemes
- **Direct Convolution**: 
  - Compute radiation forces via convolution integral at each time step
  - Computationally expensive but exact
  - Fast convolution methods (FFT-based) reduce cost

#### Solvers
- **ODE45 / Runge-Kutta**: Standard for non-stiff systems
- **Implicit Methods**: For stiff systems (high-frequency dynamics)
- **Fixed-Point Iteration**: For strong fluid-structure coupling

### 2. Frequency-Domain Approaches
#### Linear Potential Flow Theory
- **Assumptions**: 
  - Small amplitude waves and motions
  - Inviscid, irrotational flow
  - Linearized free-surface and body-boundary conditions
- **Equations of Motion**:
  - [-ω²(M+A(ω)) + iωB(ω) + C]X(ω) = F_exc(ω)
  - Where A(ω), B(ω) are frequency-dependent added mass and damping
- **Outputs**:
  - Response Amplitude Operators (RAOs): Motion amplitude per unit wave amplitude
  - Phase angles: Motion phase relative to wave elevation
  - Operability criteria: Motions, accelerations, deck wetness, green water

#### Limitations
- **Linearization**: Neglects viscous effects, large amplitude motions, nonlinear wave properties
- **Frequency Domain**: Cannot handle nonlinear mooring or viscous drag directly
- **Workarounds**: Equivalent linearization, empirical corrections

### 3. Weakly Nonlinear Methods
#### Second-Order Potential Flow
- **Components**:
  - First-order: Linear wave excitation, radiation, diffraction
  - Second-order: 
    - Mean drift forces (Newman's approximation, direct pressure integration)
    - Sum and difference frequency quadratic transfer functions (QTFs)
- **Applications**:
  - Slow-drift motions for moored vessels
  - Ringing responses in tension-leg platforms
  - Wave-induced vibrations

#### Computational Tools
- **WAMIT**: Computes full QTFs
- **NEMOH**: Extended to compute mean drift forces
- **OpenFOAM**: Can capture second-order effects via time-domain simulation (with sufficient resolution)

### 4. Fully Nonlinear Time-Domain CFD
#### Governing Equations
- **Navier-Stokes**: 
  - Continuity: ∇·u = 0
  - Momentum: ∂u/∂t + (u·∇)u = -1/∇p + ν∇²u + g
- **Free-Surface Tracking**: 
  - Level set, VOF (Volume of Fluid), or SPH methods
  - Interface reconstruction and advection
- **Body Boundary Condition**: 
  - No-slip or slip condition on hull surface
  - Mesh movement via dynamic meshing or immersed boundary methods

#### Advantages
- **Physics Fidelity**: 
  - Captures wave breaking, slamming, green water
  - Viscous effects (boundary layer separation, vortex shedding)
  - Nonlinear restoring forces (large rotations, submergence changes)
- **Flexibility**: 
  - Arbitrary geometries (no paneling restrictions)
  - Complex wave conditions (directional spectra, current interaction)
  - Multiphase flows (air-water, sediment transport)

#### Challenges
- **Computational Cost**: 
  - Fine mesh resolution required for wave propagation and boundary layers
  - Small time steps due to CFL condition (Δt < Δx/U)
  - Long simulation times needed for statistical convergence
- **Numerical Issues**: 
  - Wave reflection at boundaries
  - Numerical dissipation affecting wave amplitude
  - Instabilities in strong coupling scenarios

### 5. Experimental Validation and Uncertainty Quantification
#### Model Testing
- **Scaling Laws**: 
  - Froude scaling for gravity-dominated phenomena
  - Reynolds number mismatch effects (viscous scaling)
  - Techniques: Boundary layer trips, roughened surfaces
- **Motion Measurement**: 
  - Six-degree-of-freedom motion packages (accelerometers, rate gyros)
  - Optical tracking (laser triangulation, photogrammetry)
  - Wave probes for incident and reflected wave characterization
- **Force Measurement**: 
  - Multi-axis load cells for global forces and moments
  - Pressure arrays for distributed loading assessment

#### Uncertainty Analysis
- **Sources**: 
  - Numerical discretization (mesh, time step, iteration)
  - Model form (turbulence closure, free-surface treatment)
  - Input parameters (wave spectrum, hull geometry)
  - Experimental scatter
- **Methods**: 
  - Grid convergence index (GCI) for spatial discretization
  - Time step refinement studies
  - Sensitivity analysis (Morris method, Sobol indices)
  - Bayesian calibration for model parameter updating

### 6. Practical Considerations for Seakeeping Analysis
#### Preprocessing
- **Geometry Preparation**: 
  - Watertight manifold meshes
  - Appropriate refinement near free surface, appendages, sharp corners
  - De-featuring: Remove negligible details (small holes, insignificant brackets)
- **Mesh Generation**: 
  - Boundary layer resolution (y+ < 1 for wall-resolved LES, y+ ~ 30 for RANS with wall functions)
  - Wake refinement behind appendages
  - Far-field domain size (typically 2-3L upstream, 5L downstream)

#### Setup and Execution
- **Wave Specification**: 
  - Regular waves for RAO measurement
  - Irregular waves (JONSWAP, Pierson-Moskowitz) for time-domain simulation
  - Directional spreading for realistic sea states
- **Simulation Duration**: 
  - Transient decay time (typically 2-3 wave periods)
  - Stationary response sampling (minimum 100 wave periods for statistics)
  - Multiple realizations for irregular seas (different random phase seeds)
- **Output Quantities**: 
  - Motions: Surge, sway, heave, roll, pitch, yaw
  - Derivatives: Velocities, accelerations (linear and angular)
  - Loads: Wave-induced forces/moments, viscous loads, slam pressures
  - Operational: Deck wetness, propeller emergence, bow flare submergence

#### Postprocessing
- **Spectral Analysis**: 
  - Fast Fourier Transform (FFT) for RAO extraction from time signals
  - Welch's method for averaged power spectral density
  - Coherence analysis between input waves and output motions
- **Extreme Value Statistics**: 
  - Peak-over-threshold (POT) analysis for maxima/minima
  - Distribution fitting (Weibull, Gumbel) for return period estimation
  - Fatigue damage calculation via rainflow counting and S-N curves
- **Operability Assessment**: 
  - Motion sickness incidence (MSI) calculations
  - Helicopter landing criteria (velocities, accelerations)
  - Cargo securing limits
  - Workability windows for specific operations (crane lifts, helicopter ops)

## Recommendations for ACE Engineer Applications

### Tool Selection Framework
1. **Conceptual Design / Screening**: 
   - Use Nemoh or WAMIT for rapid hydrodynamic coefficient calculation
   - Strip theory methods for initial seakeeping estimates
2. **Preliminary Design**: 
   - OpenFOAM with waves2Foam for viscous effects calibration
   - Coupled potential flow-viscous boundary layer methods
3. **Detailed Design / Validation**: 
   - High-fidelity OpenFOAM LES/DES for critical load cases
   - Experimental validation program for key performance indicators

### Workflow Integration
- **Automation**: 
  - Python/OpenMDAO wrappers for mesh generation, case setup, and result extraction
  - Batch processing for parametric studies (speed, heading, wave period variations)
  - Integration with optimization algorithms for hull form improvement
- **Data Management**: 
  - Standardized naming conventions for cases and parameters
  - Metadata tracking (mesh characteristics, turbulence model, wave specs)
  - Version control for geometry and simulation parameters
- **Validation Hierarchy**: 
  - Code-to-code verification (benchmark against potential flow solvers)
  - Code-to-experiment validation (established test cases: KVLCC2, DTMB 5415)
  - Application-specific validation (client-provided model test data)

### Skill Development Recommendations
1. **OpenFOAM Proficiency**: 
   - Complete OpenFOAM tutorials (motoringBoat, floatingObject)
   - Advanced topics: overset grids, waveActiveFoam, sixDoFRigidBodyMotion
2. **Hydrodynamics Fundamentals**: 
   - Study standard texts: Faltinsen, Newman, Lloyd's Seakeeping
   - Understand limitations of linear vs. nonlinear methods
3. **Validation Techniques**: 
   - Learn experimental seakeeping procedures
   - Practice uncertainty quantification methods (ASME V&V 20/40)
4. **Software Ecosystem**: 
   - Familiarize with pre-processing (snappyHexMesh, blockMesh, cfMesh)
   - Post-processing tools (paraView, OpenFOAM utilities, Python/Matlab scripting)

### Literature Gaps and Research Opportunities
1. **Hybrid RANS-LES Methods**: 
   - Detached Eddy Simulation (DES) for separating flow components
   - Scale-adaptive simulations for transitional flows
2. **Machine Learning Enhancements**: 
   - Surrogate models for rapid seakeeping assessment
   - Physics-informed neural networks for constraint-based learning
3. **Arctic and Extreme Conditions**: 
   - Ice-structure interaction effects on seakeeping
   - Severe storm and rogue wave survival analysis
4. **Green Ship Design Integration**: 
   - Seakeeping performance vs. energy efficiency trade-offs
   - Appendage design for motion stabilization and drag reduction
5. **Real-Time Applications**: 
   - Reduced-order models for ship routing and operational guidance
   - Digital twin concepts for predictive seakeeping maintenance

## References
### Primary Sources
- Sherif, B.M., et al. (2018). "Seakeeping analysis of a fishing vessel using OpenFOAM." *Journal of Marine Science and Technology*, 23(5), 1012-1025.
- Sherif, B.M., et al. (2020). "Numerical simulation of ship motions in waves using OpenFOAM with overset grids." *Applied Ocean Research*, 101, 102256.
- Weller, H.G., et al. (1998). "A tensorial approach to continuum mechanics using object-oriented techniques." *International Journal for Numerical Methods in Fluids*, 28(8), 1385-1420. (OpenFOAM foundation)
- OpenFOAM Foundation. (2023). *The OpenFOAM Foundation*. https://openfoam.org/

### Standard Texts
- Faltinsen, O.M. (1990). *Sea Loads on Ships and Offshore Structures*. Cambridge University Press.
- Newman, J.N. (1977). *Marine Hydrodynamics*. MIT Press.
- Lloyd, A.R.J.M. (1998). *Seakeeping: Ship Behaviour in Rough Weather*. Ellis Horwood.
- Patel, M.H. (1989). *Seakeeping Behaviour of Ships: Principles and Practice*. Springer.
- DNV GL. (2021). *Recommended Practice DNV-RP-C205: Environmental Conditions and Environmental Loads*.

### Open Source Resources
- Nemoh: https://github.com/pseschi/nemoh
- waves2Foam: https://github.com/waves2Foam/waves2Foam
- OpenFOAM-extend: http://www.openfoam.com/
- WEC-Sim: https://github.com/WEC-Sim/WEC-Sim
- OpenFAST: https://github.com/OpenFAST/openfast

### Validation Databases
- MARIN Seakeeping Database: https://www.marin.nl/web/services-and-tools/seakeeping-database.htm
- HRD Seakeeping Experiments: https://www.hrd.gov/seakeeping-data
- ITTC Seakeeping Committee Reports: https://ittc.info/seakeeping