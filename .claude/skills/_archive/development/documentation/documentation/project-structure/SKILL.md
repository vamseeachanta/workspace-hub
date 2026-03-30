---
name: documentation-project-structure
description: 'Sub-skill of documentation: Project Structure (+3).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Project Structure (+3)

## Project Structure


```
docs/
├── index.md              # Home page
├── getting-started/      # Quickstart guides
│   ├── installation.md
│   └── configuration.md
├── guides/               # How-to guides
│   ├── basic-usage.md
│   └── advanced.md
├── reference/            # API reference
│   └── api.md
└── assets/               # Images, diagrams
    └── images/
```

## Frontmatter Standards


```yaml
---
title: Page Title
description: Brief description for SEO
sidebar_position: 1
tags:
  - guide
  - configuration
---
```

## Admonitions


```markdown
!!! note "Title"
    This is a note admonition.

!!! warning
    This is a warning without a custom title.

!!! tip "Pro Tip"
    Helpful tips go here.
```

## Code Blocks with Highlighting


```markdown
​```python title="example.py" hl_lines="2 3"
def hello():
    message = "Hello"  # highlighted
    print(message)     # highlighted
​```
```
