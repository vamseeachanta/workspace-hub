---
name: state-directory-manager-best-practices
description: 'Sub-skill of state-directory-manager: Best Practices.'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


1. **Use Standard Locations** - Follow XDG or `$HOME/.app-name`
2. **Initialize Early** - Call init before any operations
3. **Handle Permissions** - Use 700 for private data
4. **Clean Up Regularly** - Remove old temp/cache files
5. **Rotate Logs** - Prevent unbounded growth
