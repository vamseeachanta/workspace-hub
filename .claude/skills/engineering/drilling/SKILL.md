---
name: drilling
version: "1.0.0"
category: engineering
description: "Drilling engineering domain expertise — well planning, hydraulics, well control"
---
# Drilling Expert

> Domain expertise for drilling engineering, well planning, and drilling operations. Use this skill when working on drilling analysis, well design, hydraulics, well control, or any drilling-related problems in the worldenergydata or engineering context.

## Domain Knowledge

### Well Planning and Design
- **Well Architecture**: Vertical, deviated, horizontal, multilateral wells
- **Trajectory Design**: Build/hold/drop sections, dogleg severity, torque and drag
- **Casing Design**: Casing string selection, burst/collapse calculations, cement programs
- **Wellbore Stability**: Geomechanical modeling, mud weight windows, breakout analysis
- **Anti-Collision**: Well spacing, separation factor, collision avoidance
- **Drilling Programs**: AFE preparation, time/depth curves, operational procedures

### Drilling Operations
- **Drilling Parameters**: WOB, RPM, ROP optimization, MSE calculations
- **Hydraulics**: ECD management, hole cleaning, cuttings transport
- **Drilling Fluids**: Mud properties, rheology, filtration control, lost circulation
- **Directional Drilling**: MWD/LWD, RSS, mud motors, geosteering
- **Managed Pressure Drilling**: MPD, UBD, dual gradient drilling
- **Drilling Automation**: Auto-driller, closed-loop systems, real-time optimization

### Drilling Equipment and Technology
- **Rig Systems**: Drawworks, rotary systems, mud pumps, BOPs
- **Drill String Components**: Drill pipe, collars, HWDP, stabilizers, jars
- **Bits**: PDC, roller cone, hybrid bits, bit selection, dull grading
- **Downhole Tools**: MWD/LWD tools, motors, RSS, drilling jars
- **Surface Equipment**: Shale shakers, centrifuges, mud tanks, degassers
- **Rig Instrumentation**: EDR, WITS, real-time data acquisition

### Well Control and Safety
- **Kick Detection**: Flow checks, pit gain, drilling breaks, gas shows
- **Well Control Methods**: Driller's method, wait and weight, volumetric
- **BOP Systems**: Stack configuration, testing procedures, shear calculations
- **Formation Pressures**: Pore pressure prediction, fracture gradients, LOT/FIT
- **H2S Operations**: Sour gas procedures, safety equipment, emergency response
- **Barrier Management**: Primary and secondary barriers, barrier verification

### Drilling Fluids Engineering
- **Water-Based Muds**: Bentonite, polymer, KCl systems
- **Oil-Based Muds**: Invert emulsion, synthetic-based muds
- **Specialty Fluids**: Foam, air/gas drilling, formate brines
- **Mud Properties**: Density, viscosity, gel strength, fluid loss
- **Additives**: Viscosifiers, thinners, LCM, shale inhibitors
- **Solids Control**: Particle size distribution, centrifuge operations

### Specialized Drilling Operations
- **Deepwater Drilling**: Riser management, shallow hazards, hydrates
- **HPHT Wells**: Equipment ratings, well control, mud stability
- **ERD Wells**: Torque/drag limitations, ECD management, hole cleaning
- **Geothermal Drilling**: High temperature tools, lost circulation, scaling
- **Coiled Tubing Drilling**: CTD operations, limitations, applications
- **Casing While Drilling**: CwD systems, level 1-3 operations

## Industry Standards and Regulations

### API Standards
- **API RP 7G**: Drill stem design and operation
- **API RP 13B**: Drilling fluid testing procedures
- **API RP 13D**: Rheology and hydraulics of drilling fluids
- **API RP 53**: BOP equipment systems
- **API RP 59**: Well control operations
- **API RP 65**: Cementing shallow water flow zones
- **API RP 92U**: Underbalanced drilling operations

### International Standards
- **ISO 10400 Series**: Petroleum and natural gas industries — drilling and production equipment
- **ISO 13533**: Drilling and production equipment — drill-through equipment
- **ISO 16530**: Well integrity — life cycle governance
- **IADC Standards**: Drilling contractor guidelines
- **NORSOK D-010**: Well integrity in drilling and well operations

### Regulatory Bodies
- **BSEE (US)**: Bureau of Safety and Environmental Enforcement
- **HSE (UK)**: Health and Safety Executive
- **PSA (Norway)**: Petroleum Safety Authority
- **NOPSEMA (Australia)**: National Offshore Petroleum Safety
- **ANP (Brazil)**: National Agency of Petroleum

## Key Analysis Methods

### Drilling Optimization
- **ROP Modeling**: Bourgoyne-Young, Bingham models
- **MSE Analysis**: Mechanical specific energy optimization
- **Torque and Drag**: Soft string, stiff string models
- **Hydraulics Optimization**: Bit hydraulics, ECD calculations
- **Vibration Analysis**: Stick-slip, whirl, bit bounce mitigation

### Well Planning
- **Trajectory Planning**: Minimum curvature, spline methods
- **Casing Design**: Biaxial stress, triaxial design
- **Cement Design**: Slurry design, placement techniques
- **Risk Assessment**: Probability analysis, decision trees
- **Cost Estimation**: Time-depth-cost curves, AFE preparation

### Formation Evaluation
- **Pore Pressure**: Eaton, Bowers methods, seismic velocity
- **Fracture Gradient**: Matthews-Kelly, Eaton methods
- **Wellbore Stability**: Mohr-Coulomb, Mogi-Coulomb criteria
- **Rock Mechanics**: UCS, Young's modulus, Poisson's ratio

## Common Calculations

### Drilling Hydraulics
```python
# Equivalent Circulating Density (ECD)
ECD = MW + (delta_P_annular / (0.052 * TVD))

# Pressure Loss in Annulus
delta_P = (L * rho * v**2) / (25.8 * (Dh - Dp))

# Bit Hydraulics
HHP = (Q * delta_P_bit) / 1714
HSI = HHP / area_bit
```

### Rate of Penetration
```python
# Bourgoyne-Young Model
ROP = K * exp(a1 + sum(ai * xi))

# Mechanical Specific Energy
MSE = (WOB / area_bit) + (2 * pi * RPM * T) / (60 * area_bit * ROP)
```

### Torque and Drag (Soft String Model)
```python
T = T0 + mu * N * L   # Torque
F = F0 + mu * N * L   # Drag (+ for pulling, - for slack off)
# N is normal force, mu is friction factor
```

### Well Control
```python
# Kill Mud Weight
KMW = original_MW + (SIDPP / (0.052 * TVD))

# Maximum Allowable Annular Surface Pressure
MAASP = (fracture_gradient - MW) * 0.052 * shoe_TVD

# Kick Tolerance
KT = (FG - MW_current) * shoe_TVD / depth_total
```

### Example: ECD Calculation
```python
def calculate_ecd(
    mud_weight_ppg: float,
    annular_pressure_loss_psi: float,
    tvd_ft: float
) -> float:
    """
    Calculate Equivalent Circulating Density.

    Args:
        mud_weight_ppg: Static mud weight in ppg
        annular_pressure_loss_psi: Annular pressure loss in psi
        tvd_ft: True vertical depth in feet

    Returns:
        ECD in ppg
    """
    return mud_weight_ppg + annular_pressure_loss_psi / (0.052 * tvd_ft)
```

### Example: Parameter Validation
```python
def validate_drilling_parameters(params: dict) -> None:
    """Validate drilling parameters are within safe ranges."""
    if params['mud_weight'] < params['pore_pressure']:
        raise ValueError("Mud weight below pore pressure — kick risk!")
    if params['mud_weight'] > params['fracture_gradient']:
        raise ValueError("Mud weight above fracture gradient — losses risk!")
    if params['wob'] > params['bit_rating']:
        raise ValueError("WOB exceeds bit rating")
```

## Drilling Challenges and Solutions

### Common Problems
- **Stuck Pipe**: Differential, mechanical, keyseating
- **Lost Circulation**: Seepage, partial, total losses
- **Wellbore Instability**: Shale problems, salt sections
- **Drilling Vibrations**: Stick-slip, whirl, BHA resonance
- **Hole Cleaning**: Cuttings beds, pack-offs
- **Cement Failures**: Channeling, poor bond, gas migration

### Mitigation Strategies
- **Preventive Measures**: Proper planning, parameter selection
- **Early Detection**: Real-time monitoring, trend analysis
- **Corrective Actions**: Standard procedures, decision trees
- **Technology Application**: MPD, RSS, casing drilling
- **Team Expertise**: Experienced personnel, expert support

## Best Practices

### Planning Phase
1. Offset Well Analysis: study nearby wells for lessons learned
2. Risk Assessment: identify and mitigate drilling hazards
3. Contingency Planning: prepare for potential problems
4. Equipment Selection: match tools to well requirements
5. Team Alignment: ensure all parties understand objectives

### Execution Phase
1. Parameter Optimization: continuously optimize WOB, RPM, flow rate
2. Real-Time Monitoring: track drilling parameters and trends
3. Dysfunction Mitigation: quickly identify and resolve issues
4. Data Quality: ensure accurate data collection and transmission
5. Communication: maintain clear communication with all stakeholders

### Safety and Environment
1. Well Control Readiness: regular drills and equipment checks
2. Environmental Protection: prevent spills and emissions
3. Personnel Safety: follow JSA, permit systems, stop work authority
4. Equipment Integrity: regular inspection and maintenance
5. Emergency Response: clear procedures and regular training

### Safety Priorities
- Always maintain primary well control
- Monitor for kick indicators; maintain proper mud properties
- Never compromise well control for speed
- Always verify barrier integrity — maintain two-barrier philosophy
- Follow MOC procedures for changes

## Integration with WorldEnergyData

### BSEE Drilling Data
- Well spud reports and drilling permits
- Drilling incident analysis and statistics
- Rig utilization and performance metrics
- Regulatory compliance tracking
- Safety performance indicators

### Cost Analysis
- AFE vs actual cost tracking
- Cost per foot benchmarking
- NPT cost impact analysis
- Technology ROI evaluation
- Contract optimization

### Performance Analytics
- ROP improvement tracking
- Learning curve analysis
- Best practices identification
- Offset well comparisons
- Technology effectiveness

## References

1. Applied Drilling Engineering — Bourgoyne, Millheim, Chenevert, Young
2. Drilling Engineering — J.J. Azar and G. Robello Samuel
3. Advanced Drilling and Well Technology — SPE
4. Casing and Liners for Drilling and Completion — Ted G. Byrom
5. Composition and Properties of Drilling and Completion Fluids — Caenn, Darley, Gray
6. Formulas and Calculations for Drilling Operations — Robello Samuel

## Usage

Invoke this skill when:
- Designing or reviewing a well plan (trajectory, casing, cement, mud program)
- Performing drilling hydraulics calculations (ECD, pressure loss, hole cleaning)
- Analyzing or troubleshooting drilling problems (stuck pipe, lost circulation, vibrations)
- Conducting well control analysis (kick tolerance, kill mud weight, MAASP)
- Evaluating torque and drag for directional or ERD wells
- Assessing deepwater, HPHT, or extended-reach drilling challenges
- Generating Python code for drilling engineering calculations
- Interpreting BSEE drilling permit data or incident statistics
- Benchmarking drilling KPIs (ROP, NPT, cost per foot)
