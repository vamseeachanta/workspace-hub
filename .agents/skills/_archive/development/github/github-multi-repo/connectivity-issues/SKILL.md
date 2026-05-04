---
name: github-multi-repo-connectivity-issues
description: 'Sub-skill of github-multi-repo: Connectivity Issues (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Connectivity Issues (+1)

## Connectivity Issues


```bash
npx ruv-swarm github diagnose-connectivity \
  --test-all-repos \
  --check-permissions \
  --verify-webhooks
```


## Memory Synchronization


```bash
npx ruv-swarm github debug-memory \
  --check-consistency \
  --identify-conflicts \
  --repair-state
```

---
