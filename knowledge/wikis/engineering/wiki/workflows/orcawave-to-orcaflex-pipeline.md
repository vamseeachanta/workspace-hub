---
title: "OrcaWave-to-OrcaFlex Handoff Pipeline"
tags: [orcawave, orcaflex, pipeline, automation, rao, vessel-type, diffraction]
sources:
  - closed-issues
added: 2026-04-09
last_updated: 2026-04-26
---

# OrcaWave-to-OrcaFlex Handoff Pipeline

Automated single-command pipeline for converting OrcaWave diffraction results into OrcaFlex vessel type definitions (#1768, closed 2026-04-04). Replaces a previously manual multi-step process.

## Proof Boundary

This page documents the **handoff data flow** — extraction, conversion, and emission. Two independent proofs apply to any change here:

| Proof layer | Question answered | Where it runs | Authority |
|---|---|---|---|
| **Semantic equivalence** | Does the converted file mean what the source data said? | Any dev machine, CI | [Canonical Spec Semantic Equivalence Contract](../concepts/canonical-spec-semantic-equivalence.md) |
| **Licensed load/run** | Does OrcaFlex actually load the vessel type and produce sensible motions? | Licensed machine via [Solver Queue](../entities/solver-queue.md) | Issue #2475 protocol (in progress) |

A handoff change that passes semantic proof but fails licensed proof is a real failure — passing one is not a substitute for the other. Use the [Fixture Expansion Cookbook](../workflows/orcawave-orcaflex-fixture-expansion-cookbook.md) when adding new structure-family handoff fixtures.

## Pipeline Flow

```
.owr (OrcaWave results)
    -> RAO extraction (frequency, heading, 6DOF)
        -> Coordinate transform (convention alignment)
            -> OrcaFlex vessel type YAML
```

## Prior State

Before #1768, the handoff required manually using separate bridge pieces:
- `orcaflex_exporter.py` — partial RAO export
- BEMRosetta converters — format conversion
- `convert_to_orcaflex.py` — final assembly

Each step had its own convention assumptions (Hz vs rad/s, phase lead vs lag, array shape), making the process error-prone.

## Key Convention Conversions

| Property | OrcaWave | OrcaFlex |
|----------|----------|---------|
| Frequency | Hz, descending | Hz, ascending (for internal) |
| Phase | Orcina lag convention | Same convention |
| Rotational RAOs | radians/m | degrees/m (for reporting) |
| Array shape | (nheading, nfreq, 6) | Verified to match |

## Integration Points

- CLI entry point callable from scripts
- Integration test using committed `.owr` and `.sim` fixtures
- Documented in operator map
- Feeds into the [Solver Queue](../entities/solver-queue.md) for batch processing

## Cross-References

- **Related concept**: [Canonical Spec Semantic Equivalence Contract](../concepts/canonical-spec-semantic-equivalence.md)
- **Related workflow**: [Fixture Expansion Cookbook](../workflows/orcawave-orcaflex-fixture-expansion-cookbook.md)
- **Related entity**: [OrcaWave Solver](../entities/orcawave-solver.md)
- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Related entity**: [Diffraction Analysis System](../entities/diffraction-analysis-system.md)
- **Related entity**: [Solver Queue](../entities/solver-queue.md)
- **Related workflow**: [Solver Debugging Protocol](../workflows/solver-debugging-protocol.md)
- **Issues**: #2476, #2474, #2475
