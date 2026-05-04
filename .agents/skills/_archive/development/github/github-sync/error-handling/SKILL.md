---
name: github-sync-error-handling
description: 'Sub-skill of github-sync: Error Handling.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Recovery Procedures


```bash
# Check sync status
gh api repos/:owner/:repo/git/refs/heads/sync/package-alignment || echo "Branch not found"

# Rollback failed sync
git fetch origin
git checkout main
git branch -D sync/package-alignment
git push origin --delete sync/package-alignment

# Retry with fresh branch
gh api repos/:owner/:repo/git/refs \
  -f ref='refs/heads/sync/package-alignment-v2' \
  -f sha=$(gh api repos/:owner/:repo/git/refs/heads/main --jq '.object.sha')
```

### Common Issues


| Issue | Cause | Solution |
|-------|-------|----------|
| Version conflict | Incompatible dependencies | Use highest_common strategy |
| Merge conflict | Divergent changes | Manual resolution with sync coordinator |
| Test failures | Breaking changes | Run integration tests before merge |
