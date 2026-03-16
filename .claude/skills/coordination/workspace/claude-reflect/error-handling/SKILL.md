---
name: claude-reflect-error-handling
description: 'Sub-skill of claude-reflect: Error Handling.'
version: 2.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Submodule Access Issues

```bash
# Check submodule status
git submodule status

# Update submodules
git submodule update --init --recursive
```

### Empty History

If no commits found in window, reflection completes with warning:
```
Warning: No commits found in the last 30 days
Consider running with --days 90 for a larger window
```

### Pattern Scoring Issues

If pattern scores seem incorrect:
1. Check evidence commit counts
2. Verify cross-repo detection
3. Review pattern categorization
