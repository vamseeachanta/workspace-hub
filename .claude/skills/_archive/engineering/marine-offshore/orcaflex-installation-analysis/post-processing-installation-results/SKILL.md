---
name: orcaflex-installation-analysis-postproc-results
description: 'Sub-skill of orcaflex-installation-analysis: Post-Processing Installation
  Results.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Post-Processing Installation Results

## Post-Processing Installation Results


```python
from digitalmodel.orcaflex.opp import OrcaFlexPostProcess

opp = OrcaFlexPostProcess()

# Extract crane wire tensions at each depth
cfg = {
    "orcaflex": {
        "postprocess": {
            "summary": {
                "flag": True,
                "variables": [
                    {"object": "Crane_Wire", "variable_name": "Effective Tension"},
                    {"object": "Structure", "variable_name": "Z"}
                ]
            }
        }
    }
}

# Process all simulation files
sim_files = list(Path("results/installation/.sim/").glob("*.sim"))
for sim_file in sim_files:
    results = opp.process_single_file(sim_file, cfg)
    depth = extract_depth_from_filename(sim_file.stem)
    print(f"Depth {depth}m: Max tension = {results['max_tension']:.1f} kN")
```
