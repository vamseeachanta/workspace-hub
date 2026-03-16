---
name: orcaflex-monolithic-to-modular
description: Convert monolithic OrcaFlex models (.dat/.yml) to spec-driven modular
  format with semantic validation for round-trip fidelity.
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
see_also:
- orcaflex-monolithic-to-modular-architecture
- orcaflex-monolithic-to-modular-step-1-convert-dat-to-yml-if-needed
- orcaflex-monolithic-to-modular-section-mapping
- orcaflex-monolithic-to-modular-significance-levels
- orcaflex-monolithic-to-modular-output-structure
- orcaflex-monolithic-to-modular-common-issues-and-fixes
- orcaflex-monolithic-to-modular-benchmark-results-2026-02-10
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

- [orcaflex-model-generator](../orcaflex-model-generator/SKILL.md) - Builder registry and generation architecture
- [orcaflex-yaml-gotchas](../orcaflex-yaml-gotchas/SKILL.md) - Production OrcaFlex YAML traps
- [orcaflex-environment-config](../orcaflex-environment-config/SKILL.md) - Environment configuration

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

- [Architecture](architecture/SKILL.md)
- [Step 1: Convert .dat to .yml (if needed) (+4)](step-1-convert-dat-to-yml-if-needed/SKILL.md)
- [Section Mapping (+2)](section-mapping/SKILL.md)
- [Significance Levels (+2)](significance-levels/SKILL.md)
- [Output Structure](output-structure/SKILL.md)
- [Common Issues and Fixes](common-issues-and-fixes/SKILL.md)
- [Benchmark Results (2026-02-10)](benchmark-results-2026-02-10/SKILL.md)
