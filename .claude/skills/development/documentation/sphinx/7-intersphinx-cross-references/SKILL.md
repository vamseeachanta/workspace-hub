---
name: sphinx-7-intersphinx-cross-references
description: 'Sub-skill of sphinx: 7. Intersphinx Cross-References (+5).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 7. Intersphinx Cross-References (+5)

## 7. Intersphinx Cross-References


```python
# conf.py
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'sklearn': ('https://scikit-learn.org/stable/', None),
}

*See sub-skills for full details.*

## 8. Multiple Output Formats


```bash
# Build HTML
sphinx-build -b html docs/source docs/build/html

# Build PDF (requires LaTeX)
sphinx-build -b latex docs/source docs/build/latex
cd docs/build/latex && make

# Build ePub
sphinx-build -b epub docs/source docs/build/epub

*See sub-skills for full details.*

## 9. Read the Docs Configuration


```yaml
# .readthedocs.yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.11"
  jobs:
    pre_build:

*See sub-skills for full details.*

## 10. Custom Extensions


```python
# docs/source/_extensions/custom_directive.py

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx


class VersionAddedDirective(Directive):
    """

*See sub-skills for full details.*

## 11. GitHub Actions Deployment


```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'src/**/*.py'

*See sub-skills for full details.*

## 12. API Documentation with sphinx-autoapi


```python
# conf.py - Using sphinx-autoapi (alternative to autodoc)
extensions = [
    'autoapi.extension',
]

# AutoAPI configuration
autoapi_type = 'python'
autoapi_dirs = ['../../src/mypackage']
autoapi_template_dir = '_templates/autoapi'

*See sub-skills for full details.*
