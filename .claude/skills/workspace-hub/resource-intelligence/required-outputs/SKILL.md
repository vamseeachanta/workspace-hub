---
name: resource-intelligence-required-outputs
description: 'Sub-skill of resource-intelligence: Required Outputs (+1).'
version: 1.1.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Required Outputs (+1)

## Required Outputs


Record incremental additions discovered during execution:

**Gate-passing:**
- `evidence/resource-intelligence-update.yaml`

**Also update:**
- `evidence/stage-evidence.yaml` — stage 16 entry


## evidence/resource-intelligence-update.yaml Schema


```yaml
wrk_id: WRK-NNN
stage: 16
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_by: claude

additions:                    # new sources, constraints, or findings discovered during execution
  - type: source              # source | constraint | finding | skill
    description: "what was discovered"
    path: optional/file/path
no_additions_rationale: ""    # populate if additions is empty — explain why nothing new was found
```
