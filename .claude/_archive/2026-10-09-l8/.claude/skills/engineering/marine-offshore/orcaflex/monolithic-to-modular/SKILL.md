---
name: orcaflex-monolithic-to-modular
description: Convert monolithic OrcaFlex models (.dat/.yml) to spec-driven modular
  format with semantic validation for round-trip fidelity.
type: reference
version: 2.0.0
updated: 2026-02-10
category: engineering
triggers:
- convert monolithic to modular
- extract OrcaFlex spec
- modularize OrcaFlex model
- create OrcaFlex includes
- reverse engineer OrcaFlex YAML
- monolithic to spec.yml
- semantic validation OrcaFlex
capabilities: []
requires: []
tags: []
---

# Orcaflex Monolithic To Modular

## When to Use

- Converting `.dat` / `.yml` OrcaFlex models to portable `spec.yml` format
- Creating reusable component libraries from existing models
- Validating that modular output is semantically equivalent to monolithic source
- Preparing models for parametric studies or automated benchmarking
- Building a spec.yml foundation for any new OrcaFlex model

## Related Skills

- orcaflex-model-generator - Builder registry and generation architecture
- orcaflex-yaml-gotchas - Production OrcaFlex YAML traps
- orcaflex-environment-config - Environment configuration

## References

- Extractor: `src/digitalmodel/solvers/orcaflex/modular_generator/extractor.py`
- Schema: `src/digitalmodel/solvers/orcaflex/modular_generator/schema/generic.py`
- Semantic validator: `scripts/semantic_validate.py`
- Benchmark: `scripts/benchmark_model_library.py`
- Spec library: `docs/modules/orcaflex/library/tier2_fast/`

---

## Version History

- **2.0.0** (2026-02-10): Complete rewrite. Documents actual MonolithicExtractor pipeline, section name aliases, semantic validation, Pydantic integration, and benchmark results.
- **1.0.0** (2026-01-21): Initial release with manual splitting approach.

## Sub-Skills

- Architecture
- Step 1: Convert .dat to .yml (if needed) (+4)
- Section Mapping (+2)
- Significance Levels (+2)
- Output Structure
- Common Issues and Fixes
- Benchmark Results (2026-02-10)
