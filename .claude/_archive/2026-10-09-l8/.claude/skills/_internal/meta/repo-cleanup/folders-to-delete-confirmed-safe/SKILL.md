---
name: repo-cleanup-folders-to-delete-confirmed-safe
description: 'Sub-skill of repo-cleanup: Folders to DELETE (Confirmed Safe) (+3).'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Folders to DELETE (Confirmed Safe) (+3)

## Folders to DELETE (Confirmed Safe)


| Folder | Reason | Verification |
|--------|--------|--------------|
| `.drcode/` | Legacy AI config (Dr. Code) | Not referenced in any scripts or CI |
| `.benchmarks/` | Empty benchmark folder | `ls .benchmarks/` returns empty or missing |
| `.agent-runtime/` | Dead symlinks only | `find .agent-runtime -type l ! -exec test -e {} \;` |
| `.common/` | Orphaned utilities | No imports reference this folder |
| `.specify/` | Stale specification templates | Specs moved to `specs/templates/` |

## Folders to CONSOLIDATE


| Source | Destination | Command |
|--------|-------------|---------|
| `.slash-commands/` | `.claude/docs/commands/` | `git mv .slash-commands/* .claude/docs/commands/` |
| `.git-commands/` | `scripts/git/` | `git mv .git-commands/* scripts/git/` |
| `.agent-os/` | `.claude/` | See module-based-refactor skill |
| `.ai/` | `.claude/` | See module-based-refactor skill |

## Folders to KEEP


| Folder | Reason |
|--------|--------|
| `.githooks/` | Standard location for git hooks |
| `.github/` | GitHub workflows and templates |
| `.claude/` | Authoritative AI configuration |
| `.vscode/` | Team VS Code settings (if tracked) |

## Cleanup Commands


```bash
# Delete legacy config folders
rm -rf .drcode/
rm -rf .benchmarks/

# Consolidate slash-commands to docs
mkdir -p .claude/docs/commands
git mv .slash-commands/* .claude/docs/commands/ 2>/dev/null
rm -rf .slash-commands/


*See sub-skills for full details.*
