---
name: crossprovider gemini bootstrap-path-probing-must-target-the-execution
description: Bootstrap-path probing must target the execution machine, not assumed in policy
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [environment-assumptions, deployment, machine-specific]
---

Environment-specific paths (e.g., OpenFOAM bashrc at `/usr/lib/openfoam/...` vs `/opt/openfoam/...`) cannot be frozen in workflow policy without verification on the actual deployment machine. Live probe on the target host is a prerequisite of implementation, not an assumption that can be baked into the plan.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
