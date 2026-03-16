---
name: orcaflex-model-generator
description: Generate OrcaFlex modular models from spec.yml using builder registry
  pattern with conditional generation and cross-builder context sharing.
version: 2.0.0
updated: 2026-02-10
category: engineering
triggers:
- generate OrcaFlex model
- create riser model
- modular model generation
- spec.yml to OrcaFlex
- builder registry
- component assembly
- parametric model generation
capabilities: []
requires: []
see_also:
- orcaflex-model-generator-builder-registry-pattern
- orcaflex-model-generator-pipeline-builders-order-10-50
- orcaflex-model-generator-spec-variants
- orcaflex-model-generator-from-specyml-file
- orcaflex-model-generator-mergeobject
- orcaflex-model-generator-3-way-benchmark
tags: []
---

# Orcaflex Model Generator

## Related Skills

- [orcaflex-monolithic-to-modular](../orcaflex-monolithic-to-modular/SKILL.md) - Extraction pipeline
- [orcaflex-yaml-gotchas](../orcaflex-yaml-gotchas/SKILL.md) - Production YAML traps
- [orcaflex-environment-config](../orcaflex-environment-config/SKILL.md) - Environment builder details

## References

- Generator: `src/digitalmodel/solvers/orcaflex/modular_generator/__init__.py`
- Registry: `src/digitalmodel/solvers/orcaflex/modular_generator/builders/registry.py`
- Base: `src/digitalmodel/solvers/orcaflex/modular_generator/builders/base.py`
- Generic builder: `src/digitalmodel/solvers/orcaflex/modular_generator/builders/generic_builder.py`
- Schema: `src/digitalmodel/solvers/orcaflex/modular_generator/schema/`
- Spec library: `docs/modules/orcaflex/library/tier2_fast/`
- Benchmark: `scripts/benchmark_model_library.py`

---

## Version History

- **2.0.0** (2026-02-10): Complete rewrite. Documents actual ModularModelGenerator, builder registry, generic builder internals, _merge_object() with model_fields_set, section ordering, 3-way benchmark.
- **1.0.0** (2026-01-07): Initial release describing theoretical component lookup approach.

## Sub-Skills

- [Builder Registry Pattern (+3)](builder-registry-pattern/SKILL.md)
- [Pipeline Builders (order 10-50) (+2)](pipeline-builders-order-10-50/SKILL.md)
- [Spec Variants](spec-variants/SKILL.md)
- [From spec.yml file (+3)](from-specyml-file/SKILL.md)
- [_merge_object() (+2)](mergeobject/SKILL.md)
- [3-Way Benchmark](3-way-benchmark/SKILL.md)
