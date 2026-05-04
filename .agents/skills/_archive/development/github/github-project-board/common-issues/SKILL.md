---
name: github-project-board-common-issues
description: 'Sub-skill of github-project-board: Common Issues.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: Cards not syncing**
```bash
# Check project permissions
gh project view $PROJECT_NUM --owner @me

# Verify webhook configuration
gh api repos/:owner/:repo/hooks
```

**Issue: Field values not updating**
```bash
# List available fields
gh project field-list $PROJECT_NUM --owner @me

# Check field IDs
gh api graphql -f query='
  query { viewer { projectV2(number: 1) { fields(first: 20) { nodes { ... on ProjectV2SingleSelectField { id name options { id name } } } } } } }
'
```
