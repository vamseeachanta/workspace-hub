---
name: technology-stack-modernization-workspace-hub-compliance
description: 'Sub-skill of technology-stack-modernization: Workspace-Hub Compliance
  (+2).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Workspace-Hub Compliance (+2)

## Workspace-Hub Compliance


1. **Always use UV, never Conda/Poetry**
2. **Always use Plotly, never Matplotlib/Seaborn**
3. **Always use relative paths for CSV data**
4. **Always organize files in directories, never root**
5. **Always use modern Python (3.11+)**

## Migration Safety


1. **Create feature branch for updates:**
   ```bash
   git checkout -b tech-stack-modernization
   ```

2. **Commit frequently with clear messages:**
   ```bash
   git commit -m "Update pandas 1.5 → 2.0 (breaking changes addressed)"
   git commit -m "Replace matplotlib with plotly (workspace-hub compliance)"
   ```

*See sub-skills for full details.*

## Performance Considerations


1. **Python 3.11+ gives 10-25% speed boost** (no code changes)
2. **UV is 10-100x faster** than pip for environment setup
3. **Plotly HTML can be large** - use CDN mode: `include_plotlyjs='cdn'`
4. **Ruff is 10-100x faster** than Black+isort+flake8 combined
