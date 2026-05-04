---
name: mkdocs-integration-with-python-package
description: 'Sub-skill of mkdocs: Integration with Python Package (+2).'
version: 1.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Integration with Python Package (+2)

## Integration with Python Package


```
my-python-package/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       └── core.py
├── docs/
│   ├── index.md
│   ├── getting-started/
│   ├── api/
│   └── assets/
├── tests/
├── mkdocs.yml
├── pyproject.toml
└── README.md
```

```yaml
# mkdocs.yml for Python package
site_name: MyPackage
site_url: https://username.github.io/mypackage/

theme:
  name: material
  features:
    - content.code.copy

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          options:
            docstring_style: google
            show_source: true

nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - API Reference:
      - api/index.md
      - Core Module: api/core.md
  - Changelog: changelog.md
```


## Integration with Monorepo


```yaml
# mkdocs.yml for monorepo
site_name: Monorepo Documentation

nav:
  - Home: index.md
  - Packages:
      - Package A: packages/package-a/README.md
      - Package B: packages/package-b/README.md
  - Shared:
      - Contributing: CONTRIBUTING.md
      - Code of Conduct: CODE_OF_CONDUCT.md

plugins:
  - search
  - monorepo

# Reference files outside docs/
docs_dir: .
```


## Integration with CI Testing


```yaml
# .github/workflows/test-docs.yml
name: Test Documentation

on:
  pull_request:
    paths:
      - 'docs/**'
      - 'mkdocs.yml'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements-docs.txt

      - name: Build documentation (strict mode)
        run: mkdocs build --strict

      - name: Check links
        run: |
          pip install linkchecker
          mkdocs serve &
          sleep 5
          linkchecker http://127.0.0.1:8000 --check-extern

      - name: Lint Markdown
        run: |
          npm install -g markdownlint-cli
          markdownlint docs/**/*.md
```
