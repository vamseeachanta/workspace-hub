---
name: crossprovider gemini environment-variable-indirection-in-configuratio
description: Environment-variable indirection in configuration
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [config, portability, environment, yaml]
---

Store environment variable names in YAML (`mount_root_env_var: VAR_NAME`) rather than resolved paths, so the same config works across workstations with different mount layouts. Resolve variables at runtime, not at config write time.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
