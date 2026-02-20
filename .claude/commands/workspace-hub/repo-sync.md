---
name: repo-sync
description: Smart repository synchronization — pull all repos, diagnose failures (detached HEAD, diverged, dirty), and auto-fix
category: workspace-hub
---

# Repo Sync Command

Smart pull-all with automatic diagnosis and repair for the workspace-hub multi-repo ecosystem.

## Usage

```
/repo-sync [action]
```

## Actions

| Action | Description |
|--------|-------------|
| `pull` | Pull all repos, diagnose and fix failures (default) |
| `status` | Status check only, no pulls |
| `push` | Push all repos with unpushed commits |

## Examples

```bash
# Default: pull all repos with auto-fix
/repo-sync

# Status check only
/repo-sync status

# Push all
/repo-sync push
```

## Skill Reference

@.claude/skills/workspace-hub/repo-sync/SKILL.md

## Related Commands

- `/reflect` - Cross-repository reflection
- `/work` - Work queue management
