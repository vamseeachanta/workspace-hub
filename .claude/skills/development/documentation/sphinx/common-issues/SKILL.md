---
name: sphinx-common-issues
description: 'Sub-skill of sphinx: Common Issues (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Common Issues (+1)

## Common Issues


#### Autodoc Cannot Find Module

```python
# conf.py - Add source to path
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / 'src'))
```

#### Intersphinx Inventory Not Loading

```python
# conf.py - Use local inventory file
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', 'python-objects.inv'),
}

# Download inventory manually
# curl -O https://docs.python.org/3/objects.inv
```

#### Build Warnings as Errors

```bash
# Build without -W flag for debugging
sphinx-build -b html docs/source docs/build/html

# Then fix warnings before re-enabling
sphinx-build -b html docs/source docs/build/html -W
```

#### Napoleon Not Parsing Docstrings

```python
# conf.py - Ensure napoleon is configured
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# Check docstring format - must have proper indentation
def func():
    """
    Summary line.

    Args:
        param: Description.  # Note: proper indentation
    """
```

#### PDF Build Fails

```bash
# Install full LaTeX distribution
# Ubuntu
sudo apt-get install texlive-full

# macOS
brew install --cask mactex

# Check LaTeX installation
pdflatex --version
latexmk --version
```


## Debug Mode


```bash
# Verbose build
sphinx-build -b html docs/source docs/build/html -v

# Very verbose
sphinx-build -b html docs/source docs/build/html -vvv

# Show traceback on errors
sphinx-build -b html docs/source docs/build/html -T

# Keep going on errors
sphinx-build -b html docs/source docs/build/html --keep-going
```
