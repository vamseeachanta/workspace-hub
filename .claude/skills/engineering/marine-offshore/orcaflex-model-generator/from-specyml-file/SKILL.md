---
name: orcaflex-model-generator-from-specyml-file
description: 'Sub-skill of orcaflex-model-generator: From spec.yml file (+3).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# From spec.yml file (+3)

## From spec.yml file


```python
from digitalmodel.solvers.orcaflex.modular_generator import ModularModelGenerator

gen = ModularModelGenerator(Path("spec.yml"))
gen.generate(Path("output/"))
```


## From in-memory spec


```python
spec = ProjectInputSpec(**spec_dict)
gen = ModularModelGenerator.from_spec(spec)
gen.generate(Path("output/"))
```


## From monolithic (extract + generate)


```python
from digitalmodel.solvers.orcaflex.modular_generator.extractor import MonolithicExtractor

ext = MonolithicExtractor(Path("model.yml"))
spec = ProjectInputSpec(**ext.extract())
gen = ModularModelGenerator.from_spec(spec)
gen.generate(Path("output/"))
```


## With section overrides


```python
result = gen.generate_with_overrides(
    output_dir=Path("output/"),
    sections=[override_section],
    variables={"water_depth": 500},
)
```
