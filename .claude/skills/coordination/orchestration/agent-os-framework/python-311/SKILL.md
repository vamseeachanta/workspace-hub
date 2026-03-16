---
name: agent-os-framework-python-311
description: 'Sub-skill of agent-os-framework: Python 3.11+ (+4).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Python 3.11+ (+4)

## Python 3.11+


**Why**: Modern async support, performance improvements, type hints
**Usage**: All source code in `src/`

## UV Package Manager


**Why**: 10-100x faster than pip, reliable lockfiles
**Usage**: `uv venv`, `uv pip install`

## pytest


**Why**: Industry standard, excellent fixtures, plugins
**Usage**: All tests in `tests/`

## Plotly


**Why**: Interactive plots, HTML export, professional appearance
**Usage**: All visualizations must be interactive (no static matplotlib)

## Pandas


**Why**: Data manipulation, time series, CSV handling
**Usage**: Data loading and transformation
