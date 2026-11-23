---
id: PAT-002
type: pattern
title: "Extend OrcaWave frequency grid via *_input.yml without touching binary .owd"
category: data
tags: [orcawave, orcfxapi, frequency-grid, yaml, diffraction, benchmark]
repos: [digitalmodel]
confidence: 0.9
created: "2026-02-22"
last_validated: "2026-02-22"
source_type: manual
related: []
status: active
access_count: 0
---

# Extend OrcaWave Frequency Grid via *_input.yml

## Context

OrcaWave validation cases need extended frequency grids (e.g., to 10–11 rad/s) to match WAMIT reference data. Modifying the binary `.owd` file directly is error-prone and can corrupt the model.

## Pattern

```python
import OrcFxAPI

# 1. Export current model to YAML (creates *_input.yml with relative mesh paths)
diff = OrcFxAPI.Diffraction("model.owd")
diff.SaveData("model_input.yml")

# 2. Fix mesh paths (SaveData writes relative paths; script runs from different dir)
_fix_mesh_paths_in_yml("model_input.yml", base_dir=model_dir)

# 3. Modify PeriodOrFrequency list in the YAML
import yaml
with open("model_input.yml") as f:
    data = yaml.safe_load(f)
data["PeriodOrFrequency"] = [new_freq_list]
with open("model_input.yml", "w") as f:
    yaml.dump(data, f)

# 4. Load modified YAML — runs full analysis with new grid
diff2 = OrcFxAPI.Diffraction("model_input.yml")
diff2.Calculate()
diff2.SaveResults("extended.owr")
```

## Key Pitfall

`diff.SaveData(path)` writes **relative** mesh paths. If you load the YAML from a different working directory, mesh files won't be found. Always call `_fix_mesh_paths_in_yml()` to resolve to absolute paths before loading.

## Source

Implemented in WRK-204 Phase 4 (QTF freq extension), Feb 2026. See `specs/modules/piped-splashing-peacock.md` and `validate_owd_vs_spec.py`.
