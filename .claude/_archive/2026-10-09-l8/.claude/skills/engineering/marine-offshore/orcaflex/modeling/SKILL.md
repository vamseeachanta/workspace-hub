---
name: orcaflex-modeling
description: Setup, configure, and run OrcaFlex hydrodynamic simulations using the
  universal runner. Use for marine/offshore analysis including static analysis, dynamic
  simulations, mooring analysis, and batch processing of OrcaFlex models.
type: reference
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
tags:
- marine
- offshore
- orcaflex
- hydrodynamic
- mooring
- simulation
related_skills:
- orcaflex-post-processing
- orcaflex-batch-manager
- orcaflex-environment-config
- orcaflex-vessel-setup
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

- orcaflex-post-processing - Post-process simulation results
- orcawave/analysis - Diffraction/radiation analysis
- mooring-design - Mooring system design
- structural-analysis - Structural verification
- aqwa-analysis - AQWA benchmark validation

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

- Project Setup (+2)

## Sub-Skills

- Version Metadata
- [2.0.0] - 2026-01-07
- Domain Expertise (+3)
- Standardized Folder Structure
- Basic Analysis Configuration (+1)
- Command Line Interface (+1)
- Batch Processing
- Static Analysis (+3)
- Vessel Loading (+1)
- License Check (+2)
- Common Issues
- Swarm Coordination (+1)
- External Documentation
