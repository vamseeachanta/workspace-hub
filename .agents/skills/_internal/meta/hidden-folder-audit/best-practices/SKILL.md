---
name: hidden-folder-audit-best-practices
description: 'Sub-skill of hidden-folder-audit: Best Practices.'
version: 1.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


1. **Always backup before deleting** - Create a backup branch or copy
2. **Use git rm for tracked folders** - Preserves history
3. **Check symlink targets before deleting** - May need to update references
4. **Update .gitignore first** - Prevents accidental re-tracking
5. **Test after consolidation** - Ensure nothing broke
6. **Commit in logical chunks** - Separate migration from cleanup
7. **Document the changes** - Future maintainers will thank you
