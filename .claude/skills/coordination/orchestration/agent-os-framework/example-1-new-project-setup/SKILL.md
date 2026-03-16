---
name: agent-os-framework-example-1-new-project-setup
description: 'Sub-skill of agent-os-framework: Example 1: New Project Setup (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Example 1: New Project Setup (+1)

## Example 1: New Project Setup


```bash
# Generate complete .agent-os
/agent-os-framework

# Creates:
# - .agent-os/product/mission.md
# - .agent-os/product/tech-stack.md
# - .agent-os/product/roadmap.md
# - .agent-os/product/decisions.md
# - .agent-os/specs/README.md
# - .agent-os/standards/code-style.md
# - .agent-os/instructions/create-spec.md
```


## Example 2: Update Existing


```bash
# Add missing components
/agent-os-framework --update

# Only creates files that don't exist
```
