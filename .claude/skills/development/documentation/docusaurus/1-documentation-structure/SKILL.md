---
name: docusaurus-1-documentation-structure
description: 'Sub-skill of docusaurus: 1. Documentation Structure (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Documentation Structure (+2)

## 1. Documentation Structure


```
docs/
├── intro.md
├── getting-started/
│   ├── _category_.json
│   ├── installation.md
│   └── quick-start.md
├── guides/
│   ├── _category_.json
│   ├── index.md
│   └── advanced.md
├── api/
│   └── reference.md
├── faq.md
└── changelog.md
```

```json
// docs/getting-started/_category_.json
{
  "label": "Getting Started",
  "position": 1,
  "collapsible": true,
  "collapsed": false
}
```


## 2. SEO Optimization


```markdown
---
title: My Page | Brand Name
description: Description for search engines (150-160 chars)
keywords: [keyword1, keyword2]
image: /img/og/my-page.png
---
```


## 3. Content Guidelines


```markdown
---
id: unique-id
title: Clear Title
sidebar_label: Short Label
description: SEO description
---

# Page Title (H1 - only one)
