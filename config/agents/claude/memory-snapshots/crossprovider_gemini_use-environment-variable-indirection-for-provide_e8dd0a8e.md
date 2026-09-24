---
name: crossprovider gemini use-environment-variable-indirection-for-provide
description: Use environment variable indirection for provider selection
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [configuration, portability, provider-neutral]
---

Use ${WRK_PROVIDER:-default} in config YAML for runtime provider/model selection without code changes. Maintain model registry as single source of truth; don't duplicate model IDs across config files.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
