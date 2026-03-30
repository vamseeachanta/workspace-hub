---
name: python-project-template-example-1-create-basic-project
description: 'Sub-skill of python-project-template: Example 1: Create Basic Project
  (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Example 1: Create Basic Project (+2)

## Example 1: Create Basic Project


```bash
# Invoke skill
/python-project-template my-analysis-tool

# Result: Complete project structure created
# - pyproject.toml configured
# - src/my_analysis_tool/ with core module
# - tests/ with conftest.py and example test
# - UV environment ready
```


## Example 2: Create Library Project


```bash
# Create library project
/python-project-template my-library --type library

# Additional features:
# - Package publishing configuration
# - Documentation with Sphinx
# - API reference structure
```


## Example 3: Create Data Pipeline Project


```bash
# Create data pipeline project
/python-project-template data-pipeline --type pipeline

# Additional features:
# - data/raw/ and data/processed/ directories
# - reports/ for output
# - scripts/ with execution templates
```
