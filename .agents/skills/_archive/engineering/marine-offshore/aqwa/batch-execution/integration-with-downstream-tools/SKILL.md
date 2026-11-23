---
name: aqwa-batch-execution-integration-with-downstream-tools
description: 'Sub-skill of aqwa-batch-execution: Integration with Downstream Tools.'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Integration with Downstream Tools

## Integration with Downstream Tools


| Target | File | Skill |
|--------|------|-------|
| OrcaFlex vessel type | `.AH1` (ASCII hydro) or `.LIS` parsed | `orcawave-to-orcaflex`, `aqwa-analysis` |
| OrcaWave benchmark | `.LIS` RAOs + coefficients | `orcawave-aqwa-benchmark` |
| BEMRosetta converter | `.HYD` binary | `bemrosetta` |
| Python post-processing | `.LIS` text parsing | `aqwa-analysis` Python API |
