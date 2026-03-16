---
name: ecosystem-health-integration-with-repo-sync
description: 'Sub-skill of ecosystem-health: Integration with /repo-sync.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Integration with /repo-sync

## Integration with /repo-sync


The `/repo-sync` skill Phase 5 should spawn this as a background agent:

```
After Phase 4 (encoding check), spawn ecosystem-health as a parallel agent.
Report its findings in the Phase 5 summary table.
```
