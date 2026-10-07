---
name: repo-cleanup-conflict-resolution-patterns
description: 'Sub-skill of repo-cleanup: Conflict Resolution Patterns (+2).'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Conflict Resolution Patterns (+2)

## Conflict Resolution Patterns


| Conflict Type | Strategy | Example |
|--------------|----------|---------|
| Same filename | Rename with suffix | `README.md` -> `README-legacy.md` |
| Similar content | Use subdirectory | `commands/` -> `commands/legacy-scripts/` |
| Unique content | Preserve in dedicated folder | Keep `implementation-history/` |
| Clear duplicates | Delete after verification | Remove exact copies |

## Merge Commands


```bash
# Rename conflicting files before merge
mv .agent-os/README.md .agent-os/README-legacy.md

# Create legacy subdirectory for scripts
mkdir -p .claude/commands/legacy-scripts
git mv .agent-os/commands/* .claude/commands/legacy-scripts/

# Preserve unique historical content
git mv .agent-os/implementation-history/ .claude/docs/implementation-history/

# Find and remove exact duplicates (verify first)
md5sum .claude/agents/*.md .agent-os/agents/*.md | sort | uniq -w32 -d
```

## Pre-Merge Checklist


- [ ] Compare file lists between source and target
- [ ] Identify naming conflicts
- [ ] Decide rename vs. subdirectory strategy
- [ ] Document unique content to preserve
- [ ] Verify duplicates before deletion
