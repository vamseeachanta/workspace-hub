---
title: "OrcaFlex VIV Analysis"
tags: [orcaflex, viv, riser, fatigue, wake-interference, offshore]
sources:
  - career-learnings
added: 2026-04-09
last_updated: 2026-04-09
---

# OrcaFlex VIV Analysis

OrcaFlex VIV (vortex-induced vibration) analysis is used to assess fatigue damage in steel
catenary risers and other slender offshore structures subjected to ocean currents.

## Model Build

- Start from as-built geometry: touchdown point, departure angle, wall thickness profile
- OrcaFlex line type must match actual riser wall thickness profile along the length
- Use site-specific metocean scatter diagram — not simplified uniform current
- Current profile discretisation is critical for accurate VIV predictions

## Wake Interference

Adjacent risers create wake effects that increase effective VIV amplitude:

- **Interference amplification factor** depends on spacing/diameter ratio
- Apply spacing/diameter ratio correction factor for closely spaced risers
- Wake interference is the dominant source of additional fatigue damage in riser arrays

## Fatigue Post-Processing

- S-N curve selection per DNV-RP-C203 (F1, D, or E curves depending on weld class)
- Fatigue damage integrated over all current bins weighted by probability of occurrence
- Fatigue damage accumulates per Miner's rule: sum(ni/Ni) < 1/DFF

## Design Fatigue Factors (DFF)

| Location | DFF |
|----------|-----|
| Inspectable locations | 3 |
| Non-inspectable or inaccessible | 10 |

## Follow-On References

- Orcina OrcaFlex Automation Training — official automation training for scripting workflows

## Cross-References

- **Related entity**: [[pipeline-integrity]] (riser wall thickness assessment)
- **Related entity**: [[fea-structural-analysis]] (local stress analysis at connections)
- **Cross-wiki (engineering)**: [VIV Riser Fatigue](../../../engineering/wiki/concepts/viv-riser-fatigue.md) — comprehensive VIV fatigue methodology: current discretisation, wake interference, S-N curve selection, and DFF guidelines
- **Cross-wiki (engineering)**: [OrcaFlex Solver](../../../engineering/wiki/entities/orcaflex-solver.md) — OrcFxAPI automation, frequency conventions, and unit traps when comparing solvers
- **Cross-wiki (engineering)**: [FEA Structural Analysis](../../../engineering/wiki/concepts/fea-structural-analysis.md) -- similar slugs (55%); similar titles (55%); shared tags: fatigue
- **Cross-wiki (engineering)**: [Hydrodynamic Analysis](../../../engineering/wiki/concepts/hydrodynamic-analysis.md) -- similar slugs (57%); similar titles (57%)
- **Cross-wiki (engineering)**: [Mooring Analysis System](../../../engineering/wiki/entities/mooring-analysis-system.md) -- similar slugs (55%); similar titles (55%); shared keywords: analysis, cross-references, cross-wiki, design, entity
