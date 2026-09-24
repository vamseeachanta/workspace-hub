---
name: crossprovider gemini environment-variable-references-eliminate-machin
description: Environment-variable references eliminate machine-specific hardcoding
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [environment-management, portability, configuration, remote-resources]
---

For workstation-specific resource paths, use `mount_root_ref: env:VAR_NAME` and provide `mount_root_example` for documentation. Allows same artifact (e.g., registry.yaml) to work across multiple machines without modification; resolver code picks up the environment variable.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
