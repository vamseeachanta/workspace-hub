---
name: resource-intelligence-first-pass-routing-rule
description: 'Sub-skill of resource-intelligence: First-Pass Routing Rule.'
version: 1.1.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# First-Pass Routing Rule

## First-Pass Routing Rule


- `agent-router` is advisory for agent fit only
- `agent-usage-optimizer` is advisory for quota and capacity only
- the orchestrator retains final routing authority
- quota/capacity risk from `agent-usage-optimizer` takes precedence over fit preference from `agent-router` when they conflict
- overrides must be recorded in `resources.yaml` under `routing_overrides[]` with `decision`, `reason`, `recorded_at`, `recorded_by`

---
