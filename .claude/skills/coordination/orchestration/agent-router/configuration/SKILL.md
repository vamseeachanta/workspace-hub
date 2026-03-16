---
name: agent-router-configuration
description: 'Sub-skill of agent-router: Configuration.'
version: 2.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Configuration

## Configuration


Config file: `config/agents/routing-config.yaml`
Model registry: `config/agents/model-registry.yaml`

```yaml
# routing-config.yaml
tiers:
  SIMPLE:
    primary: codex
    fallbacks: [gemini, claude]
  COMPLEX:
    primary: claude
    fallbacks: [gemini, codex]

models:
  registry: model-registry.yaml
  adaptive_routing:
    enabled: true

confidence:
  auto_route_threshold: 0.70
  suggest_threshold: 0.50

session_pinning:
  enabled: true
  ttl_minutes: 30
```

Provider profiles: `config/{claude,codex,gemini}_profile.json`
