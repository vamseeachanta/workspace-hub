---
name: github-sync-sync-quality-metrics
description: 'Sub-skill of github-sync: Sync Quality Metrics (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Sync Quality Metrics (+1)

## Sync Quality Metrics


- Package version alignment percentage
- Documentation consistency score
- Integration test success rate
- Synchronization completion time

## Automated Reporting


```bash
# Generate sync status report
gh api repos/:owner/:repo/pulls \
  --jq '[.[] | select(.head.ref | startswith("sync/"))] | length'

# Check CI status for sync PRs
gh pr list --search "head:sync/" --json number,statusCheckRollup
```
