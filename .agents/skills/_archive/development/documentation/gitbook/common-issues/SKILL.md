---
name: gitbook-common-issues
description: 'Sub-skill of gitbook: Common Issues.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: 401 Unauthorized**
```bash
# Verify token
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "https://api.gitbook.com/v1/user"

# Regenerate token at:
# https://app.gitbook.com/account/developer
```

**Issue: Git sync not updating**
```bash
# Check Git connection in GitBook space settings
# Verify branch name matches
# Check for merge conflicts

# Force resync via API
curl -s -X POST -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "https://api.gitbook.com/v1/spaces/SPACE_ID/git/sync"
```

**Issue: Broken links after migration**
```python
# Fix relative links
import re

content = path.read_text()
# Add .md extension to links
content = re.sub(
    r'\[([^\]]+)\]\((?!http)([^)]+)(?<!\.md)\)',
    r'[\1](\2.md)',
    content
)
```

**Issue: Images not displaying**
```markdown
<!-- Use absolute paths from root -->
![Image](/assets/image.png)

<!-- Or relative from current file -->
![Image](./images/image.png)
```
