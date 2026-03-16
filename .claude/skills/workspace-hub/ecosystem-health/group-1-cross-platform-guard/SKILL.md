---
name: ecosystem-health-group-1-cross-platform-guard
description: 'Sub-skill of ecosystem-health: Group 1: Cross-Platform Guard (+3).'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Group 1: Cross-Platform Guard (+3)

## Group 1: Cross-Platform Guard


| # | Check | Command | Pass |
|---|-------|---------|------|
| 1 | Hook wired | `git config core.hooksPath` | `.claude/hooks` |
| 2 | pre-commit executable | `test -x .claude/hooks/pre-commit` | exit 0 |
| 3 | post-merge executable | `test -x .claude/hooks/post-merge` | exit 0 |
| 4 | uv available | `command -v uv` | found |
| 5 | .gitattributes rules | `grep -c working-tree-encoding .gitattributes` | >= 4 |
| 6 | Encoding clean | `.claude/hooks/check-encoding.sh` | exit 0 |

**Auto-fix**: If check 1-3 fail, run `bash scripts/operations/setup-hooks.sh`.
If check 6 fails, convert flagged files with iconv or uv Python.


## Group 2: Work Queue Integrity


| # | Check | Command | Pass |
|---|-------|---------|------|
| 7 | Index generates | `uv run --no-project python .claude/work-queue/scripts/generate-index.py` | exit 0 |
| 8 | No orphan WRK items | All `working/` items have `plan_approved: true` | 0 violations |
| 9 | No gate violations | `working/` items have `plan_reviewed: true` (Route B/C only) | 0 violations |


## Group 3: Skill Frontmatter Quality


| # | Check | Pass |
|---|-------|------|
| 10 | All SKILL.md have `name:`, `version:`, `tags:` | 0 missing |
| 11 | No SKILL.md > 400 lines | 0 violations |
| 12 | Bidirectional links | For any A→B in `related_skills`, B→A also present | 0 asymmetric |


## Group 4: Signal Backlog


| # | Check | Pass |
|---|-------|------|
| 13 | Pending signals | `.claude/state/pending-reviews/` file count | < 50 |
| 14 | Improve changelog recent | `improve-changelog.yaml` updated within 7 days | pass |
