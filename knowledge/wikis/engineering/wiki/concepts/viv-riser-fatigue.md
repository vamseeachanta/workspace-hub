---
title: "VIV Riser Fatigue Analysis"
tags: [viv, riser, fatigue, orcaflex, sn-curve, dnv-rp-c203]
sources:
  - career-learnings-seed
added: 2026-04-08
last_updated: 2026-04-08
---

# VIV Riser Fatigue Analysis

Vortex-Induced Vibration (VIV) is the dominant fatigue driver for steel catenary risers (SCRs) and free-spanning pipelines. Current flowing past a cylindrical structure sheds vortices that induce oscillatory cross-flow and in-line motion. Over thousands of cycles, this causes fatigue cracking — often at girth welds near the touchdown point (TDP) or hang-off location.

## Analysis Workflow

### 1. Model Build

Start from **as-built geometry**, not design drawings. Key inputs:

- **Departure angle** at the hang-off point
- **Touchdown point** location and seabed profile
- **Wall thickness profile** — varies along the riser (thicker at TDP and hang-off for fatigue allowance)
- **Hydrodynamic coefficients** — Cd and Ca (added mass) for the riser cross-section
- **Structural damping** — typically 0.3% of critical for steel risers
- **Marine growth** profile — increases effective diameter and mass

The line type definition in OrcaFlex must match the **actual wall thickness profile** section by section. Using a single average wall thickness is non-conservative at the TDP (where the thinnest section sees the highest curvature).

### 2. Current Profile Discretisation

VIV fatigue is extremely sensitive to the current profile shape, not just the magnitude. A uniform current produces a fundamentally different mode response than a sheared profile.

**Critical requirement**: use the **site-specific metocean scatter diagram** — a matrix of current speed, direction, and profile shape binned by probability of occurrence. Do not use simplified uniform or power-law profiles as shortcuts.

| Parameter | Source | Why It Matters |
|-----------|--------|---------------|
| Current speed bins | Metocean hindcast (10+ years) | Drives VIV amplitude |
| Profile shape | ADCP measurements or hindcast model | Determines which VIV modes are excited |
| Direction bins | Directional scatter | Wake interference depends on relative angle |
| Probability of occurrence | Statistical analysis | Weights fatigue damage per bin |

### 3. Wake Interference

Adjacent risers in a riser porch create **wake interference** effects. The upstream riser sheds a wake that increases the VIV amplitude on the downstream riser. This can increase fatigue damage by a factor of 2 to 5 depending on spacing.

The correction is applied as a spacing/diameter ratio factor:

- **S/D < 3**: severe amplification — avoid this configuration in design
- **3 < S/D < 8**: moderate amplification — apply DNV-RP-F204 interference factors
- **S/D > 8**: minimal interference — can often be neglected

### 4. Fatigue Calculation

Post-processing follows the S-N curve approach per **DNV-RP-C203**:

1. For each current bin, compute stress ranges at every node along the riser
2. Count cycles using rainflow counting (or direct modal analysis output)
3. Look up allowable cycles N from the applicable S-N curve (typically D or E curve for girth welds)
4. Apply **Miner's rule**: cumulative damage D = sum(n_i / N_i) for each current bin, weighted by probability
5. Fatigue life = 1 / D (in years)
6. Apply **Design Fatigue Factor** (DFF): allowable life = fatigue_life / DFF

### S-N Curve Selection

| Weld Quality | DNV S-N Curve | Typical Application |
|-------------|---------------|---------------------|
| Ground flush | C1 or C | High-fatigue locations, TDP |
| As-welded, full penetration | D | Standard girth welds |
| Partial penetration | E or F | Should be avoided for fatigue-critical joints |
| With cathodic protection | "in seawater with CP" variant | Offshore — always use the CP curve, not in-air |

### Design Fatigue Factors

| Access Category | DFF |
|----------------|-----|
| Inspectable, above splash zone | 3 |
| Inspectable, below water | 3 |
| Not inspectable, not accessible | 10 |

The TDP and buried sections of an SCR are typically classified as not inspectable (DFF = 10), which drives the design.

## Key Patterns

1. **Line type must match actual wall thickness profile** — a single average thickness underestimates stress at thin sections and overestimates at thick sections. Build the OrcaFlex model with discrete line types per joint.

2. **Wake interference: spacing/diameter correction factor** — always check riser porch layout and apply interference amplification for closely spaced risers.

3. **Miner's rule: sum(n_i/N_i) < 1/DFF** — the acceptance criterion is not damage < 1.0 but damage < 1/DFF. A common error is to forget the DFF in the Miner's sum check.

4. **DFF = 3 for inspectable, DFF = 10 for inaccessible** — this single parameter often determines whether a riser design is fatigue-feasible.

## Practical Guidance

- Run a **sensitivity study on current discretisation** early — halving the number of current bins can change the fatigue life by an order of magnitude. Converge the result by increasing bins until the fatigue life stabilizes.
- **Touchdown point migration** under different vessel offsets changes the fatigue hot spot location. Run multiple vessel offset cases (near, far, cross) to capture this.
- VIV suppression devices (strakes, fairings) reduce VIV amplitude but add drag, weight, and installation complexity. Their effectiveness depends on coverage length — partial straking can shift the problem rather than solve it.
- For screening, SHEAR7 or VIVANA are faster than full CFD-based VIV. Use CFD (e.g., OpenFOAM) only for validation of unusual geometries or when standard tools do not cover the configuration.

## Cross-References

- **Related concept**: [[fea-structural-analysis]] — local stress analysis at hot-spot weld details
- **Related concept**: [[cfd-offshore-hydrodynamics]] — CFD validation of VIV loads and Morison coefficients
- **Related concept**: [[pipeline-integrity-assessment]] — fatigue-corrosion interaction at girth welds
- **Cross-wiki (marine-engineering)**: [Mooring Line Failure](../../../marine-engineering/wiki/concepts/mooring-line-failure.md) — wire rope mooring lines also subject to fatigue from cyclic loading
- **Source**: [Career Learnings Seed](../sources/career-learnings-seed.md)
