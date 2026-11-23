---
name: mkdocs-1-documentation-structure
description: 'Sub-skill of mkdocs: 1. Documentation Structure (+1).'
version: 1.0.0
category: _internal
type: reference
scripts_exempt: true
---

# 1. Documentation Structure (+1)

## 1. Documentation Structure


```
docs/
├── index.md                    # Landing page
├── getting-started/
│   ├── index.md               # Section overview
│   ├── installation.md
│   ├── quickstart.md
│   └── configuration.md
├── user-guide/
│   ├── index.md
│   ├── concepts.md
│   ├── tutorials/
│   │   ├── basic.md
│   │   └── advanced.md
│   └── best-practices.md
├── api/
│   ├── index.md
│   └── reference.md
├── contributing/
│   ├── index.md
│   ├── development.md
│   └── style-guide.md
├── changelog.md
├── assets/
│   ├── images/
│   ├── stylesheets/
│   └── javascripts/
└── includes/                   # Reusable snippets
    └── abbreviations.md
```


## 2. Page Template


```markdown
---
title: Page Title
description: Brief description for SEO and social sharing
---

# Page Title

Brief introduction explaining what this page covers.
