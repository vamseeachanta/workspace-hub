---
name: interoperability-health-check-items
description: 'Sub-skill of interoperability: Health Check Items.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Health Check Items

## Health Check Items


Run these checks after every `git pull` or when diagnosing unexpected failures:

| # | Check | Command | Expected |
|---|-------|---------|----------|
| 1 | Hook wired | `git config core.hooksPath` | `.claude/hooks` |
| 2 | pre-commit executable | `test -x .claude/hooks/pre-commit && echo OK` | `OK` |
| 3 | uv available | `command -v uv && uv --version` | version string |
| 4 | .gitattributes rules | `grep working-tree-encoding .gitattributes` | 4 lines |
| 5 | Encoding clean | `.claude/hooks/check-encoding.sh` | exit 0, no output |
| 6 | Work queue index | `uv run --no-project python scripts/work-queue/generate-index.py` | exit 0 |

These six checks are the minimum to confirm the cross-platform guard is active.
The `/ecosystem-health` skill runs all of these automatically.
