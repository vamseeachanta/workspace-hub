---
title: "Cathodic Protection Design"
tags: [cathodic-protection, cp, dnv-rp-b401, dnv-rp-f103, anode, iccp]
sources:
  - career-learnings-seed
added: 2026-04-08
last_updated: 2026-04-08
---

# Cathodic Protection Design

Cathodic protection (CP) prevents corrosion of subsea metallic structures by making the structure the cathode in an electrochemical cell. Two systems: **sacrificial anode** (galvanic — passive, reliable, no power required) and **ICCP** (impressed current — active, adjustable, requires power supply). Offshore pipelines and structures overwhelmingly use sacrificial anodes; ICCP is more common for ships and port structures.

## Governing Standards

| Standard | Scope | Key Content |
|----------|-------|-------------|
| **DNV-RP-B401** | Offshore structures (jackets, FPSOs, subsea equipment) | Anode design, current density tables, coating breakdown factors |
| **DNV-RP-F103** | Offshore pipelines and risers | Pipeline-specific CP, coating breakdown, anode spacing |
| **ABS Rules** | Ships and mobile offshore units | Ship hull CP requirements |
| **NACE SP0169** | Onshore buried pipelines | -850 mV CSE criterion, interference, CIPS |
| **ISO 15589-2** | Offshore pipeline CP | Aligned with DNV-RP-F103 |

## Design Routes

DNV-RP-B401 defines four design routes depending on the level of detail available:

| Route | When to Use | Inputs |
|-------|-------------|--------|
| **I — Simplified** | Small structures, early screening | Standard current densities, conservative anode mass |
| **II — Detailed** | Final design for most structures | Site-specific current densities, coating data, explicit anode sizing |
| **III — Numerical modeling** | Complex geometries, interference | FEM/BEM potential distribution modeling |
| **IV — Performance-based** | In-service verification, life extension | Measured potentials, adjusted remaining life |

Most offshore designs use **Route II** for final engineering.

## Key Parameters

### Current Density

The current required to polarise the steel surface to the protective potential (-800 to -1100 mV Ag/AgCl):

| Phase | Meaning | Typical Values (bare steel, temperate seawater) |
|-------|---------|------------------------------------------------|
| **Initial** (i_c,init) | High current to first polarise the surface | 150-200 mA/m2 |
| **Mean** (i_c,mean) | Average over the design life | 70-100 mA/m2 |
| **Final** (i_c,final) | End-of-life demand after coating degradation | 90-120 mA/m2 |

Values increase in **warm tropical waters** (higher biological activity, higher corrosion rate) and decrease in **cold deep water** (lower temperature, lower oxygen content).

### Coating Breakdown Factor

Coatings reduce the area of bare steel exposed to seawater. The **coating breakdown factor** (f_c) represents the fraction of the surface that has lost coating protection:

| Time | Typical f_c (pipeline FBE coating) | Source |
|------|---------------------------------------|--------|
| Initial (t=0) | 0.01 - 0.05 | DNV-RP-F103 Table A-4 |
| Mean (t=life/2) | 0.02 - 0.10 | Interpolation |
| Final (t=life) | 0.05 - 0.20 | DNV-RP-F103 Table A-4 |

**Coating breakdown factors increase with time** — this is the fundamental driver of increasing CP demand over the design life. The initial anode output must be sized for the initial demand, but the total anode mass must cover the cumulative demand over the entire life.

### Seawater Resistivity

Seawater resistivity affects the anode output (higher resistivity = lower current output per anode):

| Environment | Resistivity (ohm-cm) |
|-------------|----------------------|
| Tropical surface water | 15-20 |
| Temperate seawater | 20-30 |
| Deep water (>1000m) | 30-40 |
| Brackish water | 50-200 |

## Anode Sizing

The fundamental sizing equation:

```
Anode mass = (Current demand x Design life) / (Electrochemical efficiency x Utilisation factor)
```

Where:
- **Current demand** = current_density x exposed_area (for each phase: initial, mean, final)
- **Design life** in hours (typically 25 years = 219,000 hours)
- **Electrochemical efficiency**: Al-Zn-In alloy ~ 2500 A-h/kg; Zn alloy ~ 780 A-h/kg
- **Utilisation factor**: 0.80-0.90 (fraction of anode consumed before it becomes ineffective)

### Anode Material Selection

| Material | Efficiency (A-h/kg) | Driving Voltage (V) | Best For |
|----------|---------------------|---------------------|----------|
| **Aluminium alloy** (Al-Zn-In) | 2500 | 0.25 | Deep water, long design life, weight-sensitive |
| **Zinc alloy** | 780 | 0.25 | Shallow water, ship hulls, short design life |
| **Magnesium** | 1100 | 0.70 | Onshore buried pipelines (higher driving voltage needed in soil) |

**Aluminium anodes are preferred over zinc for deepwater** — they have 3x the electrochemical efficiency per kg, which is critical when every kilogram of subsea weight matters.

## Anode Geometry and Placement

- **Bracelet anodes** on pipelines: spaced every 150-300m (varies by coating quality and design life)
- **Stand-off anodes** on jackets: bolted or welded to nodes and members
- **Sled anodes** for subsea equipment: large anode sleds connected by cable

The anode resistance (and therefore current output) depends on geometry. DNV-RP-B401 provides resistance formulas for standard shapes (long slender, short, flush-mounted).

## In-Service Verification

### CIPS — Close-Interval Potential Survey

For pipelines, CIPS measures the pipe-to-soil (or pipe-to-seawater) potential at close intervals (1-3m) along the pipeline route. This is the primary method for verifying CP effectiveness in service.

| Criterion | Potential (Ag/AgCl) | Meaning |
|-----------|---------------------|---------|
| Fully protected | -800 to -1050 mV | Steel is cathodically protected |
| Under-protected | > -800 mV | Corrosion occurring — remedial action needed |
| Over-protected | < -1050 mV | Risk of hydrogen embrittlement (high-strength steels) or coating disbondment |

### ROV Survey (Subsea Structures)

For subsea structures, ROV-mounted reference electrodes measure anode and structure potentials. Anode condition (remaining cross-section) is assessed visually.

## Key Patterns

1. **Coating breakdown factors increase with time (DNV-RP-F103 Table A-4)** — never assume constant coating performance
2. **Aluminium anodes preferred over zinc for deepwater** — 3x efficiency per kg
3. **CIPS for in-service verification** — the only way to confirm a pipeline CP system is working along its length
4. **Over-protection is also a failure mode** — potentials more negative than -1050 mV can cause hydrogen embrittlement in high-strength steels (X70, X80)

## Practical Guidance

- During design, **size anodes for the final (end-of-life) current demand** to ensure protection throughout the design life. The initial phase is usually less demanding.
- For **life extension** beyond original design life, calculate remaining anode mass from ROV/CIPS surveys and compare against projected demand for the extended period. Retrofit anodes (bolt-on or diver-installed) are common.
- **Electrical continuity** is essential — every structural member must be electrically bonded. A single unbonded spool or flange can leave a section unprotected.
- For **pipeline crossings and proximity to other structures**, check for CP interference — one structure's CP system can drain current from another.

## Cross-References

- **Related concept**: [[pipeline-integrity-assessment]] — corrosion rate depends on CP effectiveness
- **Related concept**: [[cfd-offshore-hydrodynamics]] — current flow affects CP current distribution
- **Related concept**: [[energy-field-economics]] — CP system cost is a significant opex item over field life
- **Cross-wiki (marine-engineering)**: [Cathodic Protection System](../../../marine-engineering/wiki/concepts/cathodic-protection-system.md) — complementary coverage of galvanic vs ICCP design per DNV-RP-B401
- **Cross-wiki (marine-engineering)**: [Corrosion Control](../../../marine-engineering/wiki/concepts/corrosion-control.md) — CP as one of five corrosion control strategies
- **Cross-wiki (marine-engineering)**: [Coating Breakdown Factor](../../../marine-engineering/wiki/concepts/coating-breakdown.md) — zone-specific breakdown tables driving CP current demand
- **Cross-wiki (marine-engineering)**: [Anode](../../../marine-engineering/wiki/entities/anode.md) — sacrificial anode materials, design parameters, and design life
- **Source**: [Career Learnings Seed](../sources/career-learnings-seed.md)
