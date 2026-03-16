---
name: file-taxonomy-gitignore-policy
description: 'Sub-skill of file-taxonomy: Gitignore Policy.'
version: 1.6.0
category: workspace
type: reference
scripts_exempt: true
---

# Gitignore Policy

## Gitignore Policy


| Category | Always gitignore | Always track |
|----------|-----------------|-------------|
| `results/` | Yes (computation output) | Never |
| `cache/` | Yes | Never |
| `data/` | Never (ground truth) | Yes (large files → LFS) |
| `tests/fixtures/` | Never | Yes |
| `htmlcov/` | Yes | Never |
| `coverage*.xml` | Yes | Never |
| `*.backup*` | Yes | Never |
| `node_modules/` | Yes | Never |
| `dist/`, `build/` | Yes | Never |
| `.venv/`, `venv/` | Yes | Never |
| `reports/` | If fully generated | If curated/reference |
