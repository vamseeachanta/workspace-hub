---
name: aqwa-reference
description: AQWA solver stages (RESTART), OPTIONS keywords, FIDP/FISK external
  damping/stiffness cards, backend bugs, and MCP tool integration patterns.
type: reference
version: 2.0.0
updated: 2026-03-16
category: engineering
triggers:
- AQWA solver stages
- AQWA OPTIONS keywords
- AQWA RESTART
- AQWA FIDP cards
- AQWA FISK cards
- AQWA MCP integration
capabilities: []
requires: []
see_also:
- aqwa-analysis
tags: []
scripts_exempt: true
---
# AQWA Reference Skill

Solver internals, OPTIONS keywords, external damping/stiffness cards, and MCP integration for ANSYS AQWA. See [aqwa](../SKILL.md) for Python API.

## RESTART Stage Reference

| RESTART | Stages Run | Purpose | Typical Use |
|---|---|---|---|
| `1 2` | Geometry + radiation | Added mass & damping matrices only | Quick coefficient extraction |
| `1 5` | Full diffraction | First-order RAOs + added mass + damping | Standard frequency-domain analysis |
| `1 8` | Full + QTF | Everything in 1-5 plus second-order QTF forces | Mooring design, slow drift |

## OPTIONS Keyword Reference

| Keyword | Purpose | When to Use |
|---|---|---|
| `GOON` | Continue past non-fatal mesh errors | Always (recommended) |
| `LHFR` | Remove irregular frequency effects (lid method) | When `remove_irregular_frequencies: true` |
| `MQTF` | Enable QTF computation | When `qtf_calculation: true` and RESTART includes stages 6-8 |
| `AHD1` | Generate .AH1 ASCII hydrodynamic database | When `output_ah1: true` |
| `REST END` | End OPTIONS block (RESTART must follow immediately) | Always (required) |

### Card Ordering in .dat File

```
OPTIONS GOON              <- Always first (error tolerance)
OPTIONS LHFR MQTF REST END  <- Feature options + terminator
OPTIONS AHD1              <- Optional output format (BEFORE REST END line)
RESTART  1  5             <- Must immediately follow REST END
```

## FIDP External Damping Cards (Deck 7)

FIDP (Frequency Independent DamPing) cards in Deck 7 WFS1:
- Format: `{6sp}FIDP{5sp}{row_idx 5-wide}{6 x 10-char scientific notation values}`
- Generated when `vessel.external_damping` has non-zero entries in spec.yml
- **Critical:** FIDP has **ZERO effect** on frequency-domain RAOs (stages 1-5)
- FIDP only affects time-domain response analysis (stages 6+, AQWA-DRIFT/NAUT)
- OrcaWave DOES include external damping in frequency-domain RAOs — this creates an asymmetry

## FISK External Stiffness Cards (Deck 7)

FISK (Frequency Independent Stiffness) cards — same format as FIDP but for `vessel.external_stiffness`.

## Backend Bug: RESTART Always 1-5

`aqwa_backend.py:412` hardcodes `RESTART 1 5` regardless of `qtf_calculation`. When `qtf_calculation: true`, should use `RESTART 1 8` to actually compute QTF. The `OPTIONS MQTF` flag is correctly generated but QTF stages never execute with RESTART 1 5.

## MCP Tool Integration

### Swarm Coordination

```javascript
mcp__claude-flow__swarm_init { topology: "mesh", maxAgents: 4 }
mcp__claude-flow__agent_spawn { type: "analyst", name: "aqwa-processor" }
mcp__claude-flow__agent_spawn { type: "code-analyzer", name: "coefficient-extractor" }
```

### Memory Coordination

```javascript
mcp__claude-flow__memory_usage {
  action: "store",
  key: "aqwa/raos/vessel",
  namespace: "hydrodynamics",
  value: JSON.stringify({ vessel: "FPSO", directions: [0, 45, 90, 135, 180], frequencies: 50 })
}
```

### Phased Processing Workflow

1. **Discovery**: Identify AQWA output files
2. **Quality**: Validate file integrity
3. **Extraction**: Extract RAOs and coefficients
4. **Synthesis**: Combine multi-body results
5. **Validation**: Check physical consistency
6. **Integration**: Export to OrcaFlex format

## Related Skills

- [aqwa](../SKILL.md) — Hub skill with Python API
- [aqwa/input](../input/SKILL.md) — Input formats and configurations
- [aqwa/output](../output/SKILL.md) — Output formats and validation
