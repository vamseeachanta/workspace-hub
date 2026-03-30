---
name: github-modes-8-sync-coordinator
description: 'Sub-skill of github-modes: 8. sync-coordinator (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 8. sync-coordinator (+2)

## 8. sync-coordinator


**Multi-package synchronization**

```bash
# Sync files across repos
gh api repos/:owner/:repo/contents/file.md --jq '.content' | base64 -d

# Create sync PR
gh pr create \
  --title "Sync: Update shared configurations" \
  --head sync/config-update \
  --base main
```

## 9. ci-orchestrator


**CI/CD pipeline coordination**

```bash
# Trigger workflow
gh workflow run ci.yml --ref main

# Check workflow status
gh run list --workflow=ci.yml --limit=5

# View run details
gh run view $RUN_ID

# Download artifacts
gh run download $RUN_ID
```

## 10. security-guardian


**Security and compliance management**

```bash
# List secret scanning alerts
gh api repos/:owner/:repo/secret-scanning/alerts

# List code scanning alerts
gh api repos/:owner/:repo/code-scanning/alerts

# Check Dependabot alerts
gh api repos/:owner/:repo/dependabot/alerts
```
