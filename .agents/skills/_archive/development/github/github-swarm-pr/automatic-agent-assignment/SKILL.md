---
name: github-swarm-pr-automatic-agent-assignment
description: 'Sub-skill of github-swarm-pr: Automatic Agent Assignment (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Automatic Agent Assignment (+1)

## Automatic Agent Assignment


```json
{
  "label-mapping": {
    "bug": ["debugger", "tester"],
    "feature": ["architect", "coder", "tester"],
    "refactor": ["analyst", "coder"],
    "docs": ["researcher", "writer"],
    "performance": ["analyst", "optimizer"],
    "security": ["security", "reviewer"]
  }
}
```

## Label-Based Topology Selection


```bash
# Determine topology from PR labels
get_topology() {
  local PR_NUM=$1
  LABELS=$(gh pr view $PR_NUM --json labels --jq '.labels[].name')

  if echo "$LABELS" | grep -q "critical"; then
    echo "hierarchical"  # Most structured for critical changes
  elif echo "$LABELS" | grep -q "feature"; then
    echo "mesh"  # Collaborative for features
  else
    echo "ring"  # Simple for routine changes
  fi
}
```
