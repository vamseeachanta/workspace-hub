---
name: orcaflex-static-debug
description: Troubleshoot and resolve OrcaFlex static analysis convergence issues.
  Diagnose common problems including line connectivity, tensions, environmental conditions,
  and numerical instabilities.
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- static convergence
- static analysis failed
- convergence issues
- static not converging
- OrcaFlex statics
- model not converging
- catenary convergence
- unstable statics
capabilities: []
requires: []
see_also:
- orcaflex-static-debug-version-metadata
- orcaflex-static-debug-100-2026-01-17
- orcaflex-static-debug-common-error-messages
- orcaflex-static-debug-diagnostic-workflow
- orcaflex-static-debug-basic-static-diagnosis
- orcaflex-static-debug-incremental-static-testing
- orcaflex-static-debug-1-line-catenary-diverged
- orcaflex-static-debug-damping-settings
- orcaflex-static-debug-quick-checks
- orcaflex-static-debug-minimal-reproducible-model
- orcaflex-static-debug-execution-for-debugging
tags: []
scripts_exempt: true
---

# Orcaflex Static Debug

## When to Use

- OrcaFlex static analysis fails to converge
- Model returns "Statics not converged" error
- Static results show unrealistic values
- Troubleshooting new model configurations
- Debugging catenary line issues
- Investigating vessel connection problems
- Resolving numerical instabilities

## Related Skills

- [orcaflex-modeling](../orcaflex-modeling/SKILL.md) - Run OrcaFlex simulations
- [orcaflex-line-wizard](../orcaflex-line-wizard/SKILL.md) - Configure line properties
- [orcaflex-mooring-iteration](../orcaflex-mooring-iteration/SKILL.md) - Optimize tensions
- [catenary-riser](../catenary-riser/SKILL.md) - Catenary analysis

## References

- OrcaFlex Theory: Static Analysis
- OrcaFlex Help: Troubleshooting
- Orcina Support: Common Statics Issues

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-17](100-2026-01-17/SKILL.md)
- [Common Error Messages](common-error-messages/SKILL.md)
- [Diagnostic Workflow](diagnostic-workflow/SKILL.md)
- [Basic Static Diagnosis](basic-static-diagnosis/SKILL.md)
- [Incremental Static Testing (+1)](incremental-static-testing/SKILL.md)
- [1. Line Catenary Diverged (+4)](1-line-catenary-diverged/SKILL.md)
- [Damping Settings (+2)](damping-settings/SKILL.md)
- [Quick Checks (+3)](quick-checks/SKILL.md)
- [Minimal Reproducible Model (+1)](minimal-reproducible-model/SKILL.md)
- [Execution for Debugging](execution-for-debugging/SKILL.md)
