---
name: mkdocs-8-plugin-configuration
description: 'Sub-skill of mkdocs: 8. Plugin Configuration (+4).'
version: 1.0.0
category: _internal
type: reference
scripts_exempt: true
---

# 8. Plugin Configuration (+4)

## 8. Plugin Configuration


```yaml
# mkdocs.yml - Comprehensive plugin setup
plugins:
  # Built-in search
  - search:
      lang: en
      separator: '[\s\-,:!=\[\]()"/]+|(?!\b)(?=[A-Z][a-z])|\.(?!\d)|&[lg]t;'
      pipeline:
        - stemmer
        - stopWordFilter

*See sub-skills for full details.*

## 9. Versioning with Mike


```bash
# Install mike
pip install mike

# Initialize versioning
mike deploy --push --update-aliases 1.0 latest

# Deploy a new version
mike deploy --push --update-aliases 2.0 latest


*See sub-skills for full details.*

## 10. Custom CSS and JavaScript


```yaml
# mkdocs.yml
extra_css:
  - stylesheets/extra.css
extra_javascript:
  - javascripts/extra.js
  - javascripts/mathjax.js
  - https://polyfill.io/v3/polyfill.min.js?features=es6
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
```

*See sub-skills for full details.*

## 11. GitHub Pages Deployment


```yaml
# .github/workflows/docs.yml
name: Deploy Documentation

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'

*See sub-skills for full details.*

## 12. Versioned Deployment with Mike


```yaml
# .github/workflows/docs-versioned.yml
name: Deploy Versioned Docs

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:

*See sub-skills for full details.*
