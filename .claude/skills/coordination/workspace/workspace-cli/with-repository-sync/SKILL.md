---
name: workspace-cli-with-repository-sync
description: 'Sub-skill of workspace-cli: With Repository Sync (+3).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# With Repository Sync (+3)

## With Repository Sync


The CLI wraps repository_sync for menu access:

```bash
# Menu access
./scripts/workspace -> 1 -> 1

# Direct access
./scripts/repository_sync <command>
```


## With Compliance System


```bash
# Menu access
./scripts/workspace -> 2 -> 3

# Direct access
./scripts/compliance/verify_compliance.sh
```


## With AI Agents


AI agents can use CLI scripts:

```python
# Run status check
subprocess.run(['./scripts/repository_sync', 'status', 'all'])

# Verify compliance
subprocess.run(['./scripts/compliance/verify_compliance.sh'])
```


## Related Skills


- [repo-sync](../repo-sync/SKILL.md) - Repository synchronization
- [compliance-check](../compliance-check/SKILL.md) - Compliance verification
- [sparc-workflow](../sparc-workflow/SKILL.md) - Development methodology
