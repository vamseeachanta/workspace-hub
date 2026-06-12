---
name: crossprovider gemini provider-neutral-config-model-registry-over-hard
description: Provider-neutral config: model registry over hardcoded IDs
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [configuration, provider-neutral, models]
---

Store model IDs in central registry (config/agents/model-registry.yaml). Workflow YAML uses env var substitution: `model: "${WRK_PROVIDER_MODEL:-claude-sonnet-4-5-20250929}"`. Allows runtime provider swapping via WRK_PROVIDER env var. (commit d372a88)

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
