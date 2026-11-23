---
name: gitbook-1-structure-content-properly
description: 'Sub-skill of gitbook: 1. Structure Content Properly (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Structure Content Properly (+3)

## 1. Structure Content Properly


```markdown
# Good structure
docs/
├── README.md           # Landing page
├── SUMMARY.md          # Navigation
├── getting-started/
│   ├── README.md       # Section intro
│   ├── installation.md
│   └── quickstart.md
└── guides/
    ├── README.md
    └── ...
```


## 2. Use Meaningful Slugs


```markdown
# SUMMARY.md - Good slugs
* [Installation Guide](getting-started/installation.md)
* [API Reference](api/reference.md)

# Avoid
* [Page 1](page1.md)
* [Untitled](untitled-1.md)
```


## 3. Maintain Version Consistency


```python
# Use consistent version naming
versions = [
    {"title": "v1.0", "slug": "v1"},
    {"title": "v2.0", "slug": "v2"},
    {"title": "Latest", "slug": "latest"}
]
```


## 4. Validate Before Publish


```python
def validate_docs(docs_path):
    """Validate docs before publishing."""
    issues = []

    # Check SUMMARY.md exists
    if not (docs_path / "SUMMARY.md").exists():
        issues.append("Missing SUMMARY.md")

    # Check all linked files exist
    # Check for broken internal links
    # Check image paths

    return issues
```
