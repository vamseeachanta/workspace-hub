# OpenFOAM v13 Marine Engineering Use Cases

> Comprehensive analysis of marine engineering applications in OpenFOAM v13
>
> Focus: Ship hydrodynamics, offshore structures, wave modeling, sloshing
> Solver: incompressibleVoF (Volume of Fluid for free surface flows)

## Overview

OpenFOAM v13 includes extensive marine engineering capabilities through the **incompressibleVoF** solver, which handles two-phase (air-water) flows with free surfaces using the Volume of Fluid (VoF) method.

## Marine Engineering Categories

### 1. Ship Hydrodynamics 🚢

**Application:** Container ships, tankers, naval vessels, high-speed craft

#### DTCHull (Duisburg Test Case)
**Description:** Post-Panamax container ship hull resistance and wave pattern
**Use Case:**
- Ship resistance prediction
- Wave-making resistance
- Hull optimization
- Full-scale ship performance

**Parameters:**
- Simulation time: 4000s (long duration)
- Typical mesh: 1-5M cells
- Computing time: Hours to days
- **Complexity:** ⭐⭐⭐⭐⭐ (Very High)

**Real-World Application:**
- Container ship design
- Fuel efficiency optimization
- Seakeeping performance
- ITTC benchmarking

**Reference:**
```
el Moctar, O., Shigunov, V., Zorn, T.,
Duisburg Test Case: Post-Panamax Container Ship for Benchmarking,
Journal of Ship Technology Research, Vol.59, No.3, pp. 50-65, 2012
```

---

#### DTCHullMoving
**Description:** Moving ship hull with dynamic mesh
**Use Case:**
- Ship maneuvering simulation
- Dynamic positioning
- Course stability analysis

**Parameters:**
- Dynamic mesh motion
- 6 DOF (Degrees of Freedom)
- Computing time: Very high
- **Complexity:** ⭐⭐⭐⭐⭐ (Very High)

**Real-World Application:**
- Ship handling trials
- Autopilot system design
- Harbor navigation

---

#### DTCHullWave
**Description:** DTC hull with wave generation
**Use Case:**
- Ship-wave interaction
- Added resistance in waves
- Seakeeping analysis

**Parameters:**
- Combined hull + waves
- Wave generation boundary
- **Complexity:** ⭐⭐⭐⭐⭐ (Very High)

**Real-World Application:**
- Seakeeping prediction
- Motion sickness analysis
- Structural loads in waves

---

#### planingHullW3
**Description:** High-speed planing hull (W3 competition case)
**Use Case:**
- Fast patrol boats
- Racing boats
- High-speed ferries

**Parameters:**
- Froude number > 0.5
- Dynamic trim and sinkage
- **Complexity:** ⭐⭐⭐⭐ (High)

**Real-World Application:**
- High-speed craft design
- Racing yacht optimization
- Coast guard vessels

---

#### propeller
**Description:** Marine propeller in open water
**Use Case:**
- Propeller design
- Thrust and torque prediction
- Cavitation analysis

**Parameters:**
- Simulation time: 0.1s
- Time step: 1e-5 (very small!)
- Rotating mesh
- **Complexity:** ⭐⭐⭐⭐⭐ (Very High)

**Real-World Application:**
- Propeller efficiency
- Vibration prediction
- Cavitation erosion prevention

---

### 2. Floating Structures ⚓

**Application:** Oil platforms, FPSOs, wind turbines, floating solar

#### floatingObject
**Description:** Simple floating rectangular object
**Use Case:**
- Basic buoyancy and stability
- Heave, pitch, roll motion
- Introduction to floating bodies

**Parameters:**
- Simulation time: 6s
- Time step: 0.01s
- **Complexity:** ⭐⭐ (Low)
- **Runtime:** ~5 minutes

**Real-World Application:**
- Floating pontoon design
- Buoy dynamics
- Basic stability calculations

**Recommended:** ✅ **Excellent for quick demonstration**

---

#### floatingObjectWaves
**Description:** Floating object in regular waves
**Use Case:**
- Wave-induced motions (heave, pitch, roll)
- Response Amplitude Operators (RAOs)
- Mooring loads

**Parameters:**
- Simulation time: Moderate
- Wave forcing included
- **Complexity:** ⭐⭐⭐ (Medium)
- **Runtime:** ~30 minutes

**Real-World Application:**
- Offshore platform design
- Floating wind turbine foundations
- FPSO motion prediction
- Wave energy converters

**Recommended:** ✅ **Good marine engineering demo**

---

### 3. Wave Modeling 🌊

**Application:** Coastal engineering, offshore design, harbor operations

#### wave (2D)
**Description:** 2D wave flume with wave generation
**Use Case:**
- Wave propagation
- Wave breaking
- Coastal structures

**Parameters:**
- Simulation time: 200s
- Time step: 0.05s
- **Complexity:** ⭐⭐⭐ (Medium)
- **Runtime:** ~20 minutes

**Real-World Application:**
- Breakwater design
- Wave energy assessment
- Beach erosion studies

**Recommended:** ✅ **Good for wave dynamics**

---

#### wave3D
**Description:** 3D wave tank simulation
**Use Case:**
- 3D wave effects
- Directional waves
- Wave diffraction

**Parameters:**
- 3D mesh (larger)
- **Complexity:** ⭐⭐⭐⭐ (High)
- **Runtime:** Hours

**Real-World Application:**
- Offshore structure design
- Wave basin experiments
- Multi-directional sea states

---

#### forcedUpstreamWave
**Description:** Forced wave generation at inlet
**Use Case:**
- Active wave maker
- Absorbing boundaries
- Wave tank simulation

**Parameters:**
- Wave generation techniques
- **Complexity:** ⭐⭐⭐ (Medium)

**Real-World Application:**
- Wave tank modeling
- Harbor resonance studies

---

#### waveSubSurface
**Description:** Wave with subsurface object interaction
**Use Case:**
- Underwater structures
- Submarine behavior
- Submerged breakwaters

**Parameters:**
- Wave-structure interaction
- **Complexity:** ⭐⭐⭐ (Medium)

**Real-World Application:**
- Subsea pipeline design
- Submarine stability
- Artificial reefs

---

### 4. Sloshing Analysis 🥁

**Application:** LNG tanks, oil tankers, fuel tanks, water ballast

#### sloshingTank2D
**Description:** 2D rectangular tank with prescribed motion
**Use Case:**
- Cargo tank sloshing
- Impact loads on tank walls
- Liquid motion in ships

**Parameters:**
- Simulation time: 40s
- Time step: 0.01s
- Prescribed motion (sinusoidal)
- **Complexity:** ⭐⭐ (Low)
- **Runtime:** ~10 minutes

**Real-World Application:**
- LNG carrier design
- Crude oil tanker safety
- Fuel tank baffles
- Sloshing loads on structures

**Recommended:** ✅ **Excellent for sloshing demo**

---

#### sloshingTank3D
**Description:** 3D tank with sloshing
**Use Case:**
- 3D sloshing patterns
- Corner effects
- Realistic tank geometry

**Parameters:**
- 3D mesh (larger)
- **Complexity:** ⭐⭐⭐ (Medium)
- **Runtime:** 30-60 minutes

**Real-World Application:**
- Full-scale LNG tank analysis
- Impact pressure prediction

---

#### sloshingTank3D3DoF
**Description:** 3D tank with 3 degrees of freedom motion
**Use Case:**
- Heave, sway, surge motions
- Coupled tank-ship motion

**Parameters:**
- 3 DOF dynamics
- **Complexity:** ⭐⭐⭐⭐ (High)

**Real-World Application:**
- Ship stability with partially filled tanks
- Free surface effect on ship motion

---

#### sloshingTank3D6DoF
**Description:** 3D tank with full 6 DOF motion
**Use Case:**
- Complete ship motion (3 translations + 3 rotations)
- Sloshing-ship coupling
- Extreme sea states

**Parameters:**
- 6 DOF dynamics
- **Complexity:** ⭐⭐⭐⭐⭐ (Very High)

**Real-World Application:**
- LNG carrier in rough seas
- Tank design for extreme conditions
- Roll damping analysis

---

#### sloshingCylinder
**Description:** Cylindrical tank sloshing
**Use Case:**
- Cylindrical fuel tanks
- Storage tanks
- Process vessels

**Parameters:**
- Cylindrical geometry
- **Complexity:** ⭐⭐⭐ (Medium)

**Real-World Application:**
- Process industry tanks
- Cylindrical fuel storage
- Chemical tankers

---

### 5. Free Surface Flows 💧

**Application:** Hydraulic engineering, coastal structures

#### damBreak
**Description:** Classic dam break problem
**Use Case:**
- Wave impact forces
- Tsunami simulation
- Green water on deck

**Parameters:**
- Simulation time: ~2s
- Very fast dynamics
- **Complexity:** ⭐⭐ (Low)
- **Runtime:** ~2 minutes

**Real-World Application:**
- Tsunami impact on structures
- Wave impact on platforms
- Deck wetness prediction
- Flood modeling

**Recommended:** ✅ **Quick, dramatic visualization**

---

#### damBreak3D
**Description:** 3D dam break with obstacle
**Use Case:**
- 3D impact effects
- Wave run-up
- Structural loading

**Parameters:**
- 3D mesh
- **Complexity:** ⭐⭐⭐ (Medium)
- **Runtime:** ~15 minutes

**Real-World Application:**
- Offshore platform design
- Structural impact assessment

---

#### waterChannel
**Description:** Open channel flow
**Use Case:**
- Free surface flow in channels
- Hydraulic jumps
- Channel design

**Parameters:**
- Steady flow
- **Complexity:** ⭐⭐ (Low)

**Real-World Application:**
- Harbor channel design
- Lock systems
- River engineering

---

### 6. Other Marine Applications

#### cavitatingBullet
**Description:** Supercavitating projectile underwater
**Use Case:**
- Underwater projectiles
- Torpedo design
- Cavitation phenomena

**Parameters:**
- High-speed underwater flow
- **Complexity:** ⭐⭐⭐ (Medium)

**Real-World Application:**
- Naval weapons
- Supercavitating vehicles
- High-speed underwater objects

---

#### mixerVessel (Marine variant)
**Description:** Mixing vessel with free surface
**Use Case:**
- Process vessels on ships
- Ballast water treatment
- Mixing efficiency

**Parameters:**
- Rotating impeller
- **Complexity:** ⭐⭐⭐ (Medium)

**Real-World Application:**
- Chemical process on ships
- Ballast water systems

---

## Recommended Cases for Marine Engineers

### Quick Demonstrations (5-15 minutes)

| Case | Runtime | Marine Application | Difficulty |
|------|---------|-------------------|------------|
| **damBreak** | ~2 min | Wave impact, tsunami | ⭐⭐ |
| **floatingObject** | ~5 min | Buoyancy, stability | ⭐⭐ |
| **sloshingTank2D** | ~10 min | LNG/oil tank sloshing | ⭐⭐ |
| **waterChannel** | ~10 min | Channel flow | ⭐⭐ |

### Medium Complexity (30-60 minutes)

| Case | Runtime | Marine Application | Difficulty |
|------|---------|-------------------|------------|
| **floatingObjectWaves** | ~30 min | Offshore platforms | ⭐⭐⭐ |
| **wave** | ~20 min | Wave propagation | ⭐⭐⭐ |
| **damBreak3D** | ~15 min | 3D wave impact | ⭐⭐⭐ |
| **sloshingTank3D** | ~45 min | 3D tank sloshing | ⭐⭐⭐ |

### Advanced (Hours to Days)

| Case | Runtime | Marine Application | Difficulty |
|------|---------|-------------------|------------|
| **DTCHull** | Hours-Days | Ship resistance | ⭐⭐⭐⭐⭐ |
| **DTCHullWave** | Days | Ship seakeeping | ⭐⭐⭐⭐⭐ |
| **propeller** | Hours | Propeller design | ⭐⭐⭐⭐⭐ |
| **planingHullW3** | Hours | High-speed craft | ⭐⭐⭐⭐ |

---

## Marine Engineering Workflow

### Typical Analysis Steps

1. **Geometry Creation**
   - CAD model (ship hull, platform, tank)
   - Mesh generation (snappyHexMesh, blockMesh)
   - Domain size selection

2. **Physical Setup**
   - Water/air properties
   - Wave conditions (period, height, direction)
   - Motion prescription (RAOs, time series)

3. **Simulation**
   - Initial conditions (setFields)
   - Boundary conditions (wave generation, pressure outlets)
   - Solver execution (foamRun -solver incompressibleVoF)

4. **Post-Processing**
   - Forces and moments (drag, lift, pitch, roll)
   - Pressure distributions
   - Free surface elevation
   - ParaView visualization

5. **Analysis**
   - Compare with model tests
   - Extract engineering parameters
   - Design optimization

---

## Quick Start - Recommended First Case

### Case: sloshingTank2D (LNG Tank Sloshing)

**Why this case:**
- Quick runtime (~10 minutes)
- Highly relevant to marine engineering
- Dramatic visualization
- Easy to understand physics
- Common in LNG/oil tanker design

**Real-World Context:**
- LNG carriers transport liquefied natural gas at -162°C
- Partially filled tanks create sloshing during ship motion
- Sloshing loads can damage tank insulation
- Critical for ship safety and cargo integrity

**Quick Run:**
```bash
cd ~/openfoam-test
cp -r /opt/openfoam13/tutorials/incompressibleVoF/sloshingTank2D .
cd sloshingTank2D
of13  # Load OpenFOAM

# Setup and run
blockMesh
setFields
foamRun

# Visualize
foamToVTK
paraview VTK/sloshingTank2D_*.vtk
```

**What to observe:**
- Liquid sloshing back and forth
- Wave formation on free surface
- Impact pressures on tank walls
- Resonance at natural frequency

---

## Marine Engineering Parameters

### Dimensionless Numbers

**Froude Number (Fr):**
```
Fr = V / sqrt(g * L)
```
- Fr < 0.3: Displacement regime (ships)
- Fr 0.3-0.5: Transition regime
- Fr > 0.5: Planing regime (fast boats)

**Reynolds Number (Re):**
```
Re = V * L / ν
```
- Full-scale ships: Re ~ 10^9
- Model scale: Re ~ 10^6-10^7
- Scaling laws for model tests

**Wave Period (T) and Length (λ):**
```
λ = g * T^2 / (2π)
```
- Typical ocean waves: T = 5-15s, λ = 40-350m
- Ship response depends on λ/L ratio

---

## Validation and Benchmarking

### Standard Test Cases

1. **DTC Hull:** ITTC benchmark for container ships
2. **KVLCC2:** Tanker hull benchmark
3. **5415 Hull:** Naval combatant (David Taylor Model Basin)
4. **Wigley Hull:** Simple mathematical hull form

### Model Test Comparison

OpenFOAM results should be compared with:
- Towing tank experiments
- Wave basin tests
- Full-scale trials
- Industry standards (ITTC, SNAME)

---

## OpenFOAM vs Commercial CFD

**Advantages of OpenFOAM:**
- ✅ Free and open-source
- ✅ Customizable solvers
- ✅ Extensive wave modeling
- ✅ 6-DOF motion capability
- ✅ Active marine engineering community

**Challenges:**
- Steeper learning curve
- Requires more manual setup
- Limited GUI compared to commercial tools
- Documentation scattered

**When to use OpenFOAM:**
- Research projects
- Custom solver development
- Large parametric studies
- Budget constraints
- Need for transparency

---

## Additional Resources

### OpenFOAM Marine Tutorials
- Location: `/opt/openfoam13/tutorials/incompressibleVoF/`
- Documentation: https://doc.cfd.direct/openfoam/user-guide-v13/incompressibleVoF

### Marine CFD References
1. **ITTC Procedures:** https://ittc.info/
2. **SIMMAN Workshop:** Ship maneuvering benchmarks
3. **OpenFOAM Marine SIG:** Special Interest Group

### Books
- "Marine Hydrodynamics" - Newman
- "Ship Resistance and Propulsion" - Molland et al.
- "OpenFOAM User Guide" - OpenFOAM Foundation

### Online Communities
- CFD Online Forums: https://www.cfd-online.com/Forums/openfoam/
- OpenFOAM Discord: Marine engineering channel
- ResearchGate: Marine CFD group

---

## Summary: Best Cases to Run

### For Quick Demo (Now):
1. **sloshingTank2D** - LNG tank analysis (10 min) ⭐⭐
2. **damBreak** - Wave impact (2 min) ⭐⭐
3. **floatingObject** - Basic stability (5 min) ⭐⭐

### For Detailed Analysis (Later):
4. **floatingObjectWaves** - Offshore platforms (30 min) ⭐⭐⭐
5. **wave** - Wave modeling (20 min) ⭐⭐⭐
6. **DTCHull** - Ship resistance (hours-days) ⭐⭐⭐⭐⭐

**Recommendation:** Start with **sloshingTank2D** for a quick, relevant marine engineering demonstration!
