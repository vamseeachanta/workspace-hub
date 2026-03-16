---
name: github-multi-repo-multi-repo-dashboard
description: 'Sub-skill of github-multi-repo: Multi-Repo Dashboard (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Multi-Repo Dashboard (+2)

## Multi-Repo Dashboard


```bash
npx ruv-swarm github multi-repo-dashboard \
  --port 3000 \
  --metrics "agent-activity,task-progress,memory-usage" \
  --real-time
```

## Dependency Graph


```bash
npx ruv-swarm github dep-graph \
  --format mermaid \
  --include-agents \
  --show-data-flow
```

## Health Monitoring


```bash
npx ruv-swarm github health-check \
  --repos "org/*" \
  --check "connectivity,memory,agents" \
  --alert-on-issues
```
