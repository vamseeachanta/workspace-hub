---
name: mkdocs-3-abbreviations
description: 'Sub-skill of mkdocs: 3. Abbreviations (+2).'
version: 1.0.0
category: _internal
type: reference
scripts_exempt: true
---

# 3. Abbreviations (+2)

## 3. Abbreviations


```markdown
<!-- docs/includes/abbreviations.md -->
*[HTML]: Hyper Text Markup Language
*[API]: Application Programming Interface
*[CLI]: Command Line Interface
*[CSS]: Cascading Style Sheets
*[JSON]: JavaScript Object Notation
*[YAML]: YAML Ain't Markup Language
*[REST]: Representational State Transfer
*[SDK]: Software Development Kit

*See sub-skills for full details.*

## 4. SEO Optimization


```yaml
# mkdocs.yml
plugins:
  - search
  - social
  - meta

extra:
  social:
    - icon: fontawesome/brands/twitter
      link: https://twitter.com/username
  analytics:
    provider: google
    property: G-XXXXXXXXXX
```

## 5. Performance Optimization


```yaml
# mkdocs.yml - Performance settings
theme:
  features:
    - navigation.instant  # Preload pages
    - navigation.prune    # Reduce navigation size

plugins:
  - minify:
      minify_html: true
      minify_js: true
      minify_css: true
  - optimize:
      enabled: true
```
