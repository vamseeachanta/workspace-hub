---
name: gmsh-openfoam-orcaflex-agent-usage-pattern
description: 'Sub-skill of gmsh-openfoam-orcaflex: Agent Usage Pattern.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Agent Usage Pattern

## Agent Usage Pattern


An agent can invoke the full pipeline with a single structured call:

```python
# Agent invocation (WRK item execution pattern)
import subprocess, json, sys

result = subprocess.run(
    [
        sys.executable,
        "scripts/pipelines/gmsh_openfoam_orcaflex.py",
        "--diameter", "1.0",
        "--length", "5.0",
        "--velocity", "1.5",
        "--work-dir", "/tmp/wrk_run",
        "--stub-mode",    # remove when solvers are installed
        "--json",
    ],
    capture_output=True, text=True
)

data = json.loads(result.stdout.split("\n{")[1])  # strip pipeline print
# OR: read /tmp/wrk_run/pipeline_results.json

assert data["passed"], f"Pipeline failed: {data['issues']}"
drag = data["summary"]["drag_force_N"]
deflection = data["summary"]["max_deflection_m"]
```
