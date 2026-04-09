---
title: "OrcaWave-to-OrcaFlex Handoff Pipeline"
tags: [orcawave, orcaflex, pipeline, automation, rao, vessel-type, diffraction]
sources:
  - closed-issues
added: 2026-04-09
last_updated: 2026-04-09
---

# OrcaWave-to-OrcaFlex Handoff Pipeline

Automated single-command pipeline for converting OrcaWave diffraction results into OrcaFlex vessel type definitions (#1768, closed 2026-04-04). Replaces a previously manual multi-step process.

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

- **Related entity**: [OrcaWave Solver](../entities/orcawave-solver.md)
- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Related entity**: [Diffraction Analysis System](../entities/diffraction-analysis-system.md)
- **Related workflow**: [Solver Debugging Protocol](../workflows/solver-debugging-protocol.md)
