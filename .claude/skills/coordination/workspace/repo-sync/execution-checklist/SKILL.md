---
name: workspace-repo-sync-execution-checklist
description: 'Sub-skill of workspace-repo-sync: Execution Checklist.'
version: 1.2.0
category: coordination
type: reference
scripts_exempt: true
---

# Execution Checklist

## Execution Checklist


- [ ] Verify SSH authentication (`ssh -T git@github.com`)
- [ ] Check repository configuration (`./scripts/repository_sync list all`)
- [ ] Run status check before operations (`./scripts/repository_sync status all`)
- [ ] Review changes in repos with uncommitted work
- [ ] Execute bulk operation with appropriate scope (all/work/personal)
- [ ] Verify operation success with status check
- [ ] Resolve any conflicts or errors reported
