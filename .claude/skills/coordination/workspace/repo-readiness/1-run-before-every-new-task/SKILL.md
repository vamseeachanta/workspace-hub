---
name: repo-readiness-1-run-before-every-new-task
description: 'Sub-skill of repo-readiness: 1. Run Before Every New Task (+4).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# 1. Run Before Every New Task (+4)

## 1. Run Before Every New Task


```bash
# Always start with readiness check
/repo-readiness

# Then proceed with work
/create-spec "new feature"
```


## 2. Keep Configuration Updated


```bash
# Update CLAUDE.md when rules change
# Update mission.md when objectives change
# Update roadmap.md when priorities shift
```


## 3. Address Issues Promptly


```bash
# Don't ignore warnings
# Fix structural issues immediately
# Keep environment synchronized
```


## 4. Use Cache Wisely


```bash
# Cache valid for 1 hour by default
# Force refresh when configuration changes
/repo-readiness --force-refresh
```


## 5. Monitor Across All Repos


```bash
# Weekly bulk check
./scripts/bulk_readiness_check.sh > reports/readiness-$(date +%Y-%m-%d).txt

# Track trends
# Maintain >95% readiness across all repos
```
