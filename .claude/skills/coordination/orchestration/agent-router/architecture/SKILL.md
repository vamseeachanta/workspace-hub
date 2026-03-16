---
name: agent-router-architecture
description: 'Sub-skill of agent-router: Architecture.'
version: 2.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Architecture

## Architecture


```
route.sh (entry point)
  ├── lib/usage_bootstrap.sh    # Zero-state usage file creation
  ├── lib/task_classifier.sh    # 10-dimension scoring engine
  ├── lib/tier_router.sh        # Tier-to-provider + model routing
  ├── lib/model_registry.sh     # Model registry + EWMA engine
  ├── lib/provider_filter.sh    # Rate limit / budget filtering
  ├── lib/cost_optimizer.sh     # Cost estimation
  ├── lib/agent_dispatcher.sh   # Model-aware agent dispatch
  └── lib/audit_logger.sh       # JSONL audit trail

config/agents/
  ├── routing-config.yaml       # Tier routing + model config
  └── model-registry.yaml       # Per-provider model variants + EWMA params
```
