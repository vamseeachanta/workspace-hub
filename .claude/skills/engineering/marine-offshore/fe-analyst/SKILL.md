---
name: fe-analyst
version: "1.0.0"
category: engineering
description: "Finite Element Analysis Analyst — slender structure FEA for marine and offshore systems"
tags: [fea, orcaflex, pipeline, riser, mooring, jumper, installation, boundary-conditions, mesh, design-checks, html-report, dnv, api]
created: 2026-02-17
author: Claude
type: skill
trigger: manual
auto_execute: false
tools: [Read, Write, Edit, Bash, Grep, Glob, Task]
related_skills: [orcaflex-specialist, structural-analysis, mooring-analysis, hydrodynamic-analysis]
---

# FE Analyst Skill — Slender Structure Analysis

> Expert knowledge for setting up, reviewing, and reporting finite element analyses of
> slender marine structures using OrcaFlex (beam/pipe elements). Covers the complete
> FEA workflow: Geometry → Materials → Boundary Conditions → Mesh → Other Structures →
> Loads → Analysis → Results → Design Checks → Report.

## When to Use This Skill

- Setting up or reviewing OrcaFlex FE models for pipelines, risers, jumpers, moorings, or installation analyses
- Designing the HTML report layout for an analysis type
- Assessing mesh quality and discretization adequacy
- Applying boundary conditions correctly for a structural scenario
- Performing code checks (DNV, API, ISO) on results
- Generating standardized analysis reports with Plotly interactive plots

---

## 1. FEA Fundamentals for Slender Structures

OrcaFlex models slender structures (pipes, lines, cables) as **Euler-Bernoulli beam elements** with:

| DOF per node | Description |
|---|---|
| u, v, w | Translational (surge, sway, heave) |
| θx, θy, θz | Rotational (roll, pitch, yaw) |

**Element stiffness contributions**:
- Axial stiffness: `EA` (axial force vs. extension)
- Bending stiffness: `EI` (moment vs. curvature)
- Torsional stiffness: `GJ` (torque vs. twist)
- Shear stiffness: optional (Timoshenko)

**Key non-linearities** in slender structure FEA:
- Geometric non-linearity (large displacements, catenary shape)
- Contact non-linearity (seabed, bend stiffeners, clamps)
- Material non-linearity (yield — typically not modelled for fatigue)
- Hydrodynamic drag non-linearity (Morison equation, velocity-squared)

---

## 2. Geometry Section

### What to Document

Every FE report geometry section must describe:

```
├── Coordinate System
│   ├── Origin (global XYZ convention)
│   ├── Z-axis direction (up/down, depth sign convention)
│   └── Reference datum (LAT, MSL, seabed)
│
├── Structure Envelope
│   ├── Total unstretched length
│   ├── Top attachment point (x, y, z) or fairlead coordinates
│   ├── Bottom termination point (x, y, z) or anchor coordinates
│   └── Plan view shape (straight, curved, lazy-S, steep-S)
│
├── Cross-Section (per segment group)
│   ├── Outer diameter (OD) [m or mm]
│   ├── Wall thickness (WT) [m or mm]
│   ├── Inner diameter (ID) = OD − 2×WT
│   └── Bend radius limit (for flexibles: MBR)
│
└── Key Points
    ├── Hang-off / Top End (risers, moorings)
    ├── Touch-Down Point (TDP) for SCRs — static and dynamic range
    ├── Arch crest (jumpers)
    ├── Midspan sag (catenaries)
    └── Clamp, buoyancy module, and fitting positions
```

### Geometry Quality Checks

```python
# OrcaFlex geometry validation checks
checks = {
    "end_separation": abs(end_A_pos - end_B_pos),          # matches design intent
    "static_tdp_clearance": tdp_z - seabed_z,              # TDP should be near 0
    "arch_height": max(z_profile) - end_A_z,                # jumpers: adequate clearance
    "plan_radius": min(horizontal_bend_radii),              # >= 20×OD for rigid pipes
    "total_length_vs_straight": total_length / straight_dist,  # layback ratio
}
```

### Per Structure Type — Geometry Checklist

| Structure | Key Geometry Items |
|---|---|
| Pipeline | Lay route, KP (kilometre point), inline fittings, PLETS, end terminations |
| SCR | Hang-off angle, catenary shape, TDP position, sag-bend curvature |
| Flexible Riser | Riser shape (lazy-S/steep-S), buoy depth, pipe-in-pipe offset |
| Jumper (rigid) | Span, arch height, spool geometry, flange positions |
| Mooring | Fairlead position, anchor position, catenary profile, suspended length |
| Installation (S-lay) | Stinger exit angle, layback, abandonment head height |
| Installation (J-lay) | Tower angle, overboarding position, layback |

---

## 3. Materials Section

### What to Document

```
Materials (per line type / section type):
├── Steel Properties
│   ├── Grade: API 5L X65, X70, etc.
│   ├── Young's Modulus E [Pa or N/m²]
│   ├── Shear Modulus G = E / (2(1+ν))
│   ├── Poisson's ratio ν
│   ├── Density ρ_steel [kg/m³]
│   └── Yield strength SMYS, UTS [MPa]
│
├── Wall Thickness Groups
│   ├── Nominal WT
│   ├── Corrosion allowance CA
│   └── Manufacturing tolerance (typically -12.5%)
│
├── Content Density
│   ├── Operating: ρ_content [kg/m³]
│   ├── Flooded: ρ_water (1025 kg/m³)
│   └── Empty (hydrotest / installation)
│
├── Coatings and Insulation
│   ├── Fusion Bonded Epoxy (FBE), 3LPE, concrete weight coat
│   ├── Thermal insulation (GSPU, foam): thickness, density
│   └── Anti-corrosion: CWC density ~3040 kg/m³
│
└── Buoyancy Modules (if used)
    ├── Module length, OD, density
    ├── Spacing and clamp contribution
    └── Net buoyancy per unit length
```

### Computed Properties (OrcaFlex Inputs)

```python
import math

def pipe_section_properties(OD, WT, rho_steel=7850):
    """Compute OrcaFlex line type inputs from pipe dimensions."""
    ID = OD - 2 * WT
    A_steel = math.pi / 4 * (OD**2 - ID**2)

    E = 207e9          # [Pa] API 5L typical
    nu = 0.3
    G = E / (2 * (1 + nu))

    # Second moments of area
    I = math.pi / 64 * (OD**4 - ID**4)  # [m⁴]
    J = 2 * I                             # circular section

    # Mass per unit length (steel only)
    mass_per_m = rho_steel * A_steel      # [kg/m]

    # Axial/bending/torsional stiffness
    EA = E * A_steel      # [N]
    EI = E * I            # [N·m²]
    GJ = G * J            # [N·m²]

    return {
        "OD_m": OD, "ID_m": ID, "WT_m": WT,
        "EA_N": EA, "EI_Nm2": EI, "GJ_Nm2": GJ,
        "mass_per_m_kg": mass_per_m,
        "A_steel_m2": A_steel, "I_m4": I,
    }
```

---

## 4. Boundary Conditions Section

### BC Types in OrcaFlex

| BC Type | OrcaFlex Setting | Engineering Scenario |
|---|---|---|
| Fixed (clamped) | End A/B: Fixed | Flowline tie-in, rigid flange |
| Free | End A/B: Free | Anchor chain free end |
| Vessel-attached | End A/B: Connected to vessel | Riser top, mooring fairlead |
| Anchored (pinned) | End B: Fixed position, free rotation | Drag embedment anchor |
| Seabed contact | Seabed model active | Pipeline touchdown, mooring chain |
| Mid-line constraint | Constraint object | Clamp, bend stiffener tip |
| Coupled structure | Linked to another line | Pipeline-riser junction, in-line tee |

### BC Documentation Template

```
Boundary Conditions:
├── Top End (End A)
│   ├── Connection: Vessel "FPSO" / anchor point / fixed
│   ├── Position (x, y, z): [m, global]
│   ├── Degrees of freedom: Translational [fixed/free], Rotational [fixed/free]
│   └── Effective stiffness (if flexible connection): kx, ky, kz [kN/m]
│
├── Bottom End (End B)
│   ├── Connection: Seabed / anchor / fixed point
│   ├── Position (x, y, z): [m, global]
│   └── Chain/wire burial — effective anchor point
│
├── Seabed Model
│   ├── Type: Linear elastic / non-linear / PONDUS
│   ├── Normal stiffness: kn [kN/m/m]
│   ├── Friction coefficient: μ (axial and lateral)
│   └── Slope: θ_seabed [°]
│
└── Intermediate Constraints (if any)
    ├── Bend stiffener / bell mouth: position along line, stiffness curve
    ├── Clamps: position, gap, friction
    └── Buoyancy modules: start/end KP, spacing
```

### Common BC Mistakes to Flag

```python
bc_checks = {
    "anchor_drag_not_modelled": "End B fixed XYZ — ensure drag embedment verified separately",
    "vessel_motion_missing": "End A connected to vessel but no RAOs imported — static only",
    "seabed_stiffness_too_high": kn > 500,   # [kN/m/m] — causes numerical issues
    "friction_coeff_zero": mu_axial == 0.0,  # Under-conservative for walking
    "free_end_tension_check": end_tension < 0,  # Negative = compression — flag
}
```

---

## 5. Mesh Section

### OrcaFlex Discretization

OrcaFlex segments are the mesh elements. Each segment has:
- **Length**: controls resolution along the structure
- **Bend stiffness**: `EI` of the element
- **Mass**: lumped at nodes

### Mesh Quality Criteria

```python
def assess_mesh_quality(segment_lengths, OD, min_radius_of_curvature):
    """
    Assess FE mesh quality for a slender structure.

    Returns a dict of quality flags.
    """
    L_max = max(segment_lengths)
    L_min = min(segment_lengths)
    ratio = L_max / L_min

    # Rule 1: Segments should not be longer than ~5×OD in regions of high curvature
    max_seg_high_curve = min_radius_of_curvature * 0.1  # ~10 segs per 90° arc

    # Rule 2: Adjacent segment length ratio (gradual variation)
    from itertools import pairwise
    adjacent_ratios = [max(a, b) / min(a, b) for a, b in pairwise(segment_lengths)]
    max_adj_ratio = max(adjacent_ratios)

    # Rule 3: Minimum segment — avoid < OD/2 (over-discretized)
    over_refined = any(L < OD / 2 for L in segment_lengths)

    return {
        "total_segments": len(segment_lengths),
        "L_min_m": L_min,
        "L_max_m": L_max,
        "global_ratio": ratio,
        "max_adjacent_ratio": max_adj_ratio,   # flag if > 3.0
        "over_refined_segments": over_refined,
        "high_curvature_adequate": L_max <= max_seg_high_curve,
        "pass": max_adj_ratio <= 3.0 and not over_refined and L_min > 0.01,
    }
```

### Mesh Report Table Format

```
Mesh Summary:
┌─────────────────────┬──────────┬──────────┬──────────┬──────────┐
│ Region              │ N segs   │ L_min [m]│ L_max [m]│ Ratio    │
├─────────────────────┼──────────┼──────────┼──────────┼──────────┤
│ Top section         │ 20       │ 0.50     │ 1.00     │ 2.0  ✓  │
│ Mid catenary        │ 150      │ 1.00     │ 2.00     │ 2.0  ✓  │
│ TDP zone            │ 30       │ 0.25     │ 1.00     │ 4.0  ✗  │
│ Seabed section      │ 50       │ 1.00     │ 2.00     │ 2.0  ✓  │
└─────────────────────┴──────────┴──────────┴──────────┴──────────┘
TOTAL: 250 segments | PASS: 3/4 regions
```

### Refinement Guidelines by Region

| Region | Guideline | Reason |
|---|---|---|
| TDP zone | ≤ 0.5 × D | Highest curvature, most critical for fatigue |
| Sag bend | ≤ 1.0 × D | Second-highest curvature |
| Free catenary | ≤ 5.0 × D | Low curvature — efficiency |
| Seabed (laid) | ≤ 3.0 × D | Axial walking, upheaval |
| Near clamp/BSJ | ≤ 0.2 × D | Local stress concentration |
| Mooring at fairlead | ≤ 2.0 × D | Curvature under vessel offset |
| Stinger (S-lay) | ≤ 0.5 × D | Bending control critical |

---

## 6. Other Structures Section

### What to Document

"Other structures" are components that interact with the primary structure but are not the primary line:

```
Other Structures:
├── Attached Buoyancy / Arch Buoys
│   ├── Object name, position (KP or z-coordinate)
│   ├── Mass [Te], displaced volume [m³], net buoyancy [kN]
│   └── Hydrodynamic coefficients (Cd, Ca)
│
├── Bend Stiffeners / Bell Mouths
│   ├── Location (top of riser, PLEM connection)
│   ├── Length, OD, stiffness curve (M-κ relationship)
│   └── Tip constraint (fixed/pinned)
│
├── I-Tubes / J-Tubes (pull-in)
│   ├── Geometry (curved section, exit angle)
│   ├── Friction coefficient
│   └── Guide centraliser positions
│
├── Clamps and Supports
│   ├── Position (KP or global z)
│   ├── Clamp mass, gap, friction coefficient
│   └── Stiffness (restrained DOFs)
│
├── Adjacent Structures (passing ship, jacket, platform)
│   ├── Proximity distance [m]
│   ├── Clearance envelope (min approach)
│   └── Interaction modelling (constraint or hydrodynamic)
│
└── Vessel (FPSO, semi, ship)
    ├── Vessel type, draught, displacement
    ├── RAO origin, heading convention
    └── Relevant motions for analysis (heave, surge, pitch for risers)
```

---

## 7. Loads Section

### Environmental Load Summary

```
Loads:
├── Gravity
│   └── g = 9.81 m/s²; direction: −Z (downward)
│
├── Hydrodynamic (Morison Equation)
│   ├── Drag coefficient Cd (normal) — API RP 2RD typical: 1.0−1.2
│   ├── Inertia coefficient Cm = 1 + Ca — typical Ca = 1.0
│   ├── Lift coefficient Cl (VIV suppression: 0.0 without analysis)
│   └── Added mass coefficient Ca (transverse and axial)
│
├── Wave Loading
│   ├── Wave theory: Airy (linear), Stokes 5th, Dean Stream
│   ├── Sea state: Hs [m], Tp [s], γ (JONSWAP peak factor)
│   ├── Heading: θ_wave [° from North or from vessel heading]
│   └── Direction spread: long-crested or short-crested
│
├── Current
│   ├── Profile: u(z) vs. depth [m/s at each depth]
│   ├── Heading: θ_current [°]
│   └── Type: Gulf Stream, tidal, mean loop current
│
├── Wind (for surface-piercing structures)
│   ├── Speed: U10 [m/s] (10-min mean at 10m elevation)
│   ├── Heading: θ_wind [°]
│   └── Applicable: turret mooring, topsides drag
│
└── Functional Loads
    ├── Internal pressure: Pi [MPa] (operating vs. design)
    ├── Temperature: T [°C] (thermal expansion driving force)
    ├── Lay tension: Th [kN] (installation)
    └── Pre-tension: T_initial [kN] (mooring chains)
```

### Load Combinations (Design Cases)

| Case | Wave | Current | Wind | Notes |
|---|---|---|---|---|
| Operating | 100-yr Hs, Tp | 10-yr | 10-yr | Strength check |
| Extreme | 100-yr Hs, Tp | 100-yr | 100-yr | Combined extreme |
| Fatigue | Scatter diagram | Long-term | N/A | Fatigue damage |
| Survival | 10,000-yr | — | — | Mooring intact check |
| Installation | Workability Hs | — | — | Operability window |

---

## 8. Analysis Types

### Static Analysis
- Purpose: Establish equilibrium position under static loads (gravity, current, pretension)
- OrcaFlex: `CalculateStatics()`
- Outputs: Static position, static tensions, static bending moments
- Convergence criteria: max residual force < 1e-3 kN

### Dynamic Analysis
- Purpose: Time-domain simulation under wave + current
- OrcaFlex: `RunSimulation()`, stage duration, ramp time
- Minimum ramp: 1× Tp to settle hydrodynamic transients
- Minimum simulation duration: 3 hours (10,800 s) for statistical convergence
- Output extraction: Every 0.1–0.2 s (Nyquist for 5×Tp minimum)

### Modal Analysis
- Purpose: Natural frequencies and mode shapes (VIV susceptibility)
- Key output: Fundamental period T1 [s] vs. wave/vortex shedding period
- Strouhal criterion: `f_vs = St × U / D` where St ≈ 0.2 (subcritical)
- Flag if `|T1 - T_wave| / T_wave < 0.10` (resonance proximity)

### Fatigue Analysis
- Purpose: Accumulated damage over service life
- Method: Time-domain rainflow counting OR frequency-domain spectral
- S-N curve: DNV-OS-F101 D-curve for girth welds
- SCF: DNVGL-RP-C203 hot spot or notch stress
- Target: D < 1.0 (design life ≥ 20 yr with factor of 10)

---

## 9. Results Extraction

### Key Results to Extract and Plot

```python
RESULT_TYPES = {
    # Tension / Axial
    "effective_tension": {
        "unit": "kN",
        "positive": "tension",
        "check": "Te > 0 (no compression except upheaval buckling design)",
    },
    "wall_tension": {
        "unit": "kN",
        "note": "True wall tension = Te - Pi*Ai + Pe*Ae",
    },

    # Bending
    "x_bending_moment": {"unit": "kN·m"},
    "y_bending_moment": {"unit": "kN·m"},
    "resultant_bending_moment": {
        "unit": "kN·m",
        "computed": "sqrt(Mx² + My²)",
    },
    "curvature": {
        "unit": "1/m",
        "check": "κ < κ_allowable = 1 / (20×OD) typical",
    },

    # Stress
    "von_mises_stress": {"unit": "MPa", "check": "σ_vm < SMYS / γ_m"},
    "combined_utilization": {
        "unit": "−",
        "check": "UC < 1.0 per DNV-OS-F101 or API RP 2RD",
    },

    # Position
    "x_position": {"unit": "m"},
    "z_position": {"unit": "m"},
    "arc_length": {"unit": "m"},

    # Fatigue (if applicable)
    "fatigue_damage": {"unit": "−", "check": "D < 0.1 (factor 10 on 20-yr life)"},
}
```

### Statistical Summary Table

For each result variable, report:

| Statistic | Symbol | Description |
|---|---|---|
| Mean | μ | Time-average |
| Std Dev | σ | Dynamic variation |
| Maximum | max | Most extreme tensile / positive |
| Minimum | min | Most extreme compressive / negative |
| Max Absolute | |max| | Governing amplitude |
| MPM (Most Probable Maximum) | MPM = μ + √(2 ln N) × σ | Storm peak estimate |

---

## 10. Design Checks

### DNV-OS-F101 Pipeline Code Checks

```python
def check_pipeline_utilization(Te, Mx, My, Pi, Pe, D, t, SMYS, SMTS, alpha_fab=0.96):
    """
    DNV-OS-F101 combined loading utilization check for pipelines.
    Sec.5 D400 — system collapse check (simplified).
    """
    # Pressure containment
    p_b = (2 * t * SMYS) / (D - t)  # Burst pressure
    UC_pressure = (Pi - Pe) / p_b

    # Bending + tension utilization (DNV Eq. D-5)
    M_resultant = (Mx**2 + My**2)**0.5
    M_p = SMYS * (D - t)**2 * t    # Plastic moment capacity
    T_yield = SMYS * math.pi * (D - t) * t   # Yield tension

    UC_combined = (M_resultant / M_p)**2 + (Te / T_yield)**2

    return {
        "UC_pressure": UC_pressure,
        "UC_combined": UC_combined,
        "PASS_pressure": UC_pressure < 1.0,
        "PASS_combined": UC_combined < 1.0,
    }
```

### API RP 2RD Riser Code Checks

```
UC_axial = |Te| / (SMYS × A_steel)                          # ≤ 0.67 (ASD)
UC_bending = |M_resultant| × (OD/2) / (SMYS × I / (OD/2))  # ≤ 0.75
UC_combined = UC_axial + UC_bending                         # ≤ 1.0
```

### Design Check Summary Table (Report Format)

| Check | Value | Allowable | UC | Status |
|---|---|---|---|---|
| Effective tension (min) | > 0 kN | > 0 kN | — | ✅ PASS |
| Burst pressure | 15.2 MPa | 20.1 MPa | 0.76 | ✅ PASS |
| Combined bending + tension | — | — | 0.82 | ✅ PASS |
| Curvature at TDP | 0.08 1/m | 0.10 1/m | 0.80 | ✅ PASS |
| Fatigue damage | 0.07 | 0.10 | 0.70 | ✅ PASS |

---

## 11. FEA HTML Report Layout

Reports follow this canonical section order (FE causal chain):

```
1. Report Header & Metadata
2. Executive Summary          ← PASS/FAIL, key findings, worst case
3. Model Overview             ← structure type, analysis type, design codes
4. Geometry                   ← spatial layout, envelope, key points
5. Materials                  ← steel grade, content, coatings, section props
6. Boundary Conditions        ← top/bottom ends, seabed, intermediate constraints
7. Mesh                       ← segment table, quality plots, adjacent ratio map
8. Other Structures           ← buoys, clamps, adjacent members, vessel
9. Loads                      ← environmental load table, design cases
10. Analysis Setup            ← solver settings, ramp time, duration, convergence
11. Results
    ├── Static Results        ← static tensions, shape, position
    ├── Dynamic Results       ← time histories, statistics tables, envelopes
    └── Extreme Results       ← MPM values, governing load case
12. Design Checks             ← utilization ratios, pass/fail summary table
13. Fatigue (if applicable)   ← damage accumulation, SCF, hot-spot locations
14. Summary & Recommendations ← key findings, gaps, next steps
15. Appendices                ← formulas, reference data, solver settings dump
```

### Plot Types Per Section

| Section | Plot Type | Plotly Trace |
|---|---|---|
| Geometry | 3D line profile (x,y,z) | `go.Scatter3d` |
| Geometry | 2D vertical profile (arc length vs. z) | `go.Scatter` |
| Mesh | Segment length distribution | `go.Bar` |
| Mesh | Adjacent ratio heatmap along arc | `go.Scatter` with color |
| Materials | Section property table | `go.Table` |
| BC | 3D model with BC markers | `go.Scatter3d` + annotations |
| Results | Time history (Te, M, z) | `go.Scatter` (time on x) |
| Results | Envelope (max/min vs. arc length) | `go.Scatter` with fill |
| Results | Statistical summary table | `go.Table` |
| Design Checks | Utilization bar chart | `go.Bar` with threshold line |
| Fatigue | Damage vs. arc length | `go.Scatter` |

---

## 12. Standards Reference

| Standard | Scope | Key Sections |
|---|---|---|
| DNV-OS-F101 | Submarine pipeline systems | Sec.5 (loads), Sec.7 (design checks) |
| DNV-OS-F201 | Dynamic risers | Sec.3 (design criteria), App.A (SCR) |
| API RP 2RD | Risers for floating structures | Sec.5 (design), Sec.8 (fatigue) |
| DNV-RP-C203 | Fatigue design | S-N curves, SCF |
| DNV-RP-F105 | Free-spanning pipelines | VIV, fatigue, soil interaction |
| ISO 13628-7 | Flexible pipe systems | MBR, armour, service factors |
| API RP 2SK | Mooring systems | Intact + damaged criteria |
| DNV-OS-E301 | Mooring chains | Material, safety factors |

---

## 13. Common FEA Mistakes and Remedies

| Mistake | Symptom | Remedy |
|---|---|---|
| Too-coarse mesh at TDP | Curvature under-predicted | Refine to ≤ 0.5×OD near TDP |
| Adjacent segment ratio > 3 | Spurious oscillations | Grade mesh gradually |
| Missing ramp in dynamics | Non-physical transients in results | Add 1–2×Tp ramp; exclude from stats |
| Seabed stiffness too high | Divergence / oscillation at TDP | Use kn = 50–200 kN/m/m typically |
| Missing Cm (added mass) | Under-estimated natural period | Ca = 1.0 for circular sections |
| Static only (no dynamics) | Misses resonance effects | Always run dynamic for wave analysis |
| Compression not checked | Upheaval buckling risk missed | Check min(Te) > 0 at all nodes |
| No content weight | Unconservative sag bend tension | Include internal fluid density |
| Wrong sign convention for z | Results appear inverted | Confirm OrcaFlex z-positive-up convention |
