---
name: orcaflex-model-generator-builder-registry-pattern
description: 'Sub-skill of orcaflex-model-generator: Builder Registry Pattern (+3).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Builder Registry Pattern (+3)

## Builder Registry Pattern


```python
@BuilderRegistry.register("03_environment.yml", order=30)
class EnvironmentBuilder(BaseBuilder):
    def should_generate(self) -> bool:
        return True  # Always needed

    def build(self) -> dict[str, Any]:
        return {"Environment": {...}}
```

Builders self-register via the `@register` decorator. The orchestrator iterates them in order without maintaining a hardcoded list.


## Core Classes


| Class | Location | Purpose |
|-------|----------|---------|
| `ModularModelGenerator` | `__init__.py` | Orchestrator: loads spec, runs builders, writes output |
| `BuilderRegistry` | `builders/registry.py` | Auto-discovery registry with ordered execution |
| `BaseBuilder` | `builders/base.py` | ABC with `build()`, `should_generate()`, entity sharing |
| `BuilderContext` | `builders/context.py` | Typed dataclass for cross-builder data sharing |
| `ProjectInputSpec` | `schema/root.py` | Pydantic root model (metadata + environment + simulation + generic/pipeline/riser) |


## Builder Execution Flow


```
1. ModularModelGenerator.generate(output_dir)
2.   for (filename, builder_class) in BuilderRegistry.get_ordered_builders():
3.     builder = builder_class(spec, context)
4.     if not builder.should_generate(): continue
5.     data = builder.build()
6.     context.update_from_dict(builder.get_generated_entities())
7.     yaml.dump(data, includes_dir / filename)
8.   write master.yml with include directives
```


## Cross-Builder Entity Sharing


Builders register entities via `_register_entity(key, value)` for downstream builders:

```python
# VesselBuilder registers vessel name
self._register_entity("main_vessel_name", vessel.name)

# LinesBuilder reads it from context
vessel_name = self.context.main_vessel_name
```
