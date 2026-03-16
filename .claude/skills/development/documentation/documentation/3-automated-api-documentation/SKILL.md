---
name: documentation-3-automated-api-documentation
description: 'Sub-skill of documentation: 3. Automated API Documentation (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 3. Automated API Documentation (+2)

## 3. Automated API Documentation


```python
# Generate API docs from docstrings
"""
Module description.

Example:
    >>> import mymodule
    >>> mymodule.function()
    'result'
"""

*See sub-skills for full details.*

## 4. Version Documentation


```bash
# Version docs with releases
version_docs() {
    local version="$1"

    # MkDocs with mike
    mike deploy "$version" latest -u
    mike set-default latest

    # Docusaurus
    npm run docusaurus docs:version "$version"
}
```

## 5. Link Validation


```bash
# Check for broken links
check_links() {
    local docs_dir="${1:-docs}"

    # Using markdown-link-check
    find "$docs_dir" -name '*.md' -exec markdown-link-check {} \;

    # Using linkchecker on built site
    linkchecker ./site/index.html
}
```
