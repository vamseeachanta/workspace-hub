---
name: github-release-swarm-hotfix-process
description: 'Sub-skill of github-release-swarm: Hotfix Process (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Hotfix Process (+1)

## Hotfix Process


```bash
# Emergency hotfix
npx ruv-swarm github emergency-release \
  --severity critical \
  --bypass-checks security-only \
  --fast-track \
  --notify-all
```

## Rollback Procedure


```bash
# Immediate rollback
npx ruv-swarm github rollback \
  --to-version v1.9.9 \
  --reason "Critical bug in v2.0.0" \
  --preserve-data \
  --notify-users
```
