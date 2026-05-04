---
name: repo-cleanup-gitignore-updates
description: 'Sub-skill of repo-cleanup: Gitignore Updates.'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Gitignore Updates

## Gitignore Updates


Add these entries to `.gitignore` after cleanup:

```gitignore
# Build artifacts
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
*.egg
build/
dist/
.eggs/

# Test artifacts
.pytest_cache/
.coverage
.coverage.*
htmlcov/
coverage.xml
*.cover

# IDE
.idea/
.vscode/
*.code-workspace

*See sub-skills for full details.*
