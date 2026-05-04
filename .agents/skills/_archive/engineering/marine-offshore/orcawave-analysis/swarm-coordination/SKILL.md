---
name: orcawave-analysis-swarm-coordination
description: 'Sub-skill of orcawave-analysis: Swarm Coordination (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Swarm Coordination (+2)

## Swarm Coordination


```javascript
// Initialize panel method analysis swarm
mcp__claude-flow__swarm_init { topology: "star", maxAgents: 3 }

// Spawn specialized agents
mcp__claude-flow__agent_spawn { type: "analyst", name: "orcawave-processor" }
mcp__claude-flow__agent_spawn { type: "code-analyzer", name: "mesh-validator" }
```

## Memory Coordination


```javascript
// Store analysis configuration
mcp__claude-flow__memory_usage {
  action: "store",
  key: "orcawave/analysis/config",
  namespace: "hydrodynamics",
  value: JSON.stringify({
    vessel: "FPSO",
    mesh_panels: 5000,
    frequencies: 50,

*See sub-skills for full details.*

## Benchmark Validation vs AQWA


Compare OrcaWave results with AQWA for validation at peak/significant values.

```python
from digitalmodel.diffraction.comparison_framework import PeakRAOComparator
from digitalmodel.diffraction.aqwa_converter import AQWAConverter
from digitalmodel.diffraction.orcawave_converter import OrcaWaveConverter

# Extract both datasets
aqwa_results = AQWAConverter(...).convert_to_unified_schema(...)
orcawave_results = OrcaWaveConverter(vessel).convert()

*See sub-skills for full details.*
