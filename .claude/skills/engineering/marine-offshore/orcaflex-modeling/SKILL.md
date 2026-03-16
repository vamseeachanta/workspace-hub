---
name: orcaflex-modeling
description: Setup, configure, and run OrcaFlex hydrodynamic simulations using the
  universal runner. Use for marine/offshore analysis including static analysis, dynamic
  simulations, mooring analysis, and batch processing of OrcaFlex models.
version: 2.0.0
updated: 2025-01-02
category: engineering
triggers:
- OrcaFlex model setup
- hydrodynamic simulation
- mooring analysis
- riser analysis
- installation analysis
- batch OrcaFlex processing
- .yml model files
- .dat model files
- .sim simulation files
capabilities: []
requires: []
see_also:
- orcaflex-modeling-version-metadata
- orcaflex-modeling-200-2026-01-07
- orcaflex-modeling-domain-expertise
- orcaflex-modeling-standardized-folder-structure
- orcaflex-modeling-basic-analysis-configuration
- orcaflex-modeling-command-line-interface
- orcaflex-modeling-batch-processing
- orcaflex-modeling-static-analysis
- orcaflex-modeling-vessel-loading
- orcaflex-modeling-license-check
- orcaflex-modeling-common-issues
- orcaflex-modeling-swarm-coordination
- orcaflex-modeling-external-documentation
tags: []
scripts_exempt: true
---

# Orcaflex Modeling

## When to Use

- Setting up OrcaFlex analysis projects with standardized folder structure
- Running static or dynamic hydrodynamic simulations
- Batch processing multiple OrcaFlex models (.yml, .dat files)
- Configuring mooring analysis or iterative simulations
- Using the universal runner for pattern-based batch execution
- Preprocessing vessel data and checking model configurations
- Hydrodynamic analysis and mooring system design
- Riser analysis and installation sequence planning
- Fatigue assessment of offshore structures

## Prerequisites

- OrcaFlex license (checked via `OrcFxAPI`)
- Python environment with `digitalmodel` package installed
- YAML configuration files for analysis parameters

## Related Skills

- [orcaflex-post-processing](../orcaflex-post-processing/SKILL.md) - Post-process simulation results
- [orcawave-analysis](../orcawave-analysis/SKILL.md) - Diffraction/radiation analysis
- [mooring-design](../mooring-design/SKILL.md) - Mooring system design
- [structural-analysis](../structural-analysis/SKILL.md) - Structural verification
- [aqwa-analysis](../aqwa-analysis/SKILL.md) - AQWA benchmark validation

## References

- OrcaFlex Documentation: [Orcina OrcaFlex](https://www.orcina.com/orcaflex/)
- OrcFxAPI Python Guide
- Universal Runner: `src/digitalmodel/modules/orcaflex/universal/README.md`
- Agent Configuration: `agents/orcaflex/agent.yaml`

---

## Version History

- **2.0.0** (2025-01-02): Merged agent capabilities from agents/orcaflex/, added MCP integration, critical production rules, external documentation refresh
- **1.0.0** (2024-12-01): Initial release with universal runner and batch processing

## Sub-Skills

- [Project Setup (+2)](project-setup/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[2.0.0] - 2026-01-07](200-2026-01-07/SKILL.md)
- [Domain Expertise (+3)](domain-expertise/SKILL.md)
- [Standardized Folder Structure](standardized-folder-structure/SKILL.md)
- [Basic Analysis Configuration (+1)](basic-analysis-configuration/SKILL.md)
- [Command Line Interface (+1)](command-line-interface/SKILL.md)
- [Batch Processing](batch-processing/SKILL.md)
- [Static Analysis (+3)](static-analysis/SKILL.md)
- [Vessel Loading (+1)](vessel-loading/SKILL.md)
- [License Check (+2)](license-check/SKILL.md)
- [Common Issues](common-issues/SKILL.md)
- [Swarm Coordination (+1)](swarm-coordination/SKILL.md)
- [External Documentation](external-documentation/SKILL.md)
