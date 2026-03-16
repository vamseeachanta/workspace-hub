---
name: orcaflex-monolithic-to-modular-step-1-convert-dat-to-yml-if-needed
description: 'Sub-skill of orcaflex-monolithic-to-modular: Step 1: Convert .dat to
  .yml (if needed) (+4).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Step 1: Convert .dat to .yml (if needed) (+4)

## Step 1: Convert .dat to .yml (if needed)


```python
import OrcFxAPI

model = OrcFxAPI.Model("model.dat")
model.SaveData("model.yml")  # OrcaFlex YAML export
```


## Step 2: Extract spec from monolithic YAML


```python
from digitalmodel.solvers.orcaflex.modular_generator.extractor import MonolithicExtractor

ext = MonolithicExtractor(Path("model.yml"))
spec_dict = ext.extract()
# Returns: {"metadata": {...}, "environment": {...}, "simulation": {...}, "generic": {...}}
```

The extractor:
- Reads multi-document YAML (handles `---` separators)
- Maps OrcaFlex keys to spec schema (typed fields + properties bag)
- Handles section name aliases (Groups/BrowserGroups, FrictionCoefficients/SolidFrictionCoefficients)
- Extracts current profiles from multi-column keys
- Captures `raw_properties` for diagnostic use


## Step 3: Validate and create spec


```python
from digitalmodel.solvers.orcaflex.modular_generator.schema.root import ProjectInputSpec

spec = ProjectInputSpec(**spec_dict)
# Pydantic validates all fields, applies defaults
```


## Step 4: Generate modular output


```python
from digitalmodel.solvers.orcaflex.modular_generator import ModularModelGenerator

gen = ModularModelGenerator.from_spec(spec)
gen.generate(Path("output/modular"))
```


## Step 5: Semantic validation


```python
from scripts.semantic_validate import load_monolithic, load_modular, validate, summarize

mono = load_monolithic(Path("model.yml"))
mod = load_modular(Path("output/modular"))
results = validate(mono, mod)
summary = summarize(results)

print(f"Match: {summary['total_sections'] - summary['sections_with_diffs']}/{summary['total_sections']}")
print(f"Significant diffs: {summary['significant_diffs']}")
```
