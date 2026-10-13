---
name: repo-cleanup-common-hidden-folders
description: 'Sub-skill of repo-cleanup: Common Hidden Folders (+2).'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Common Hidden Folders (+2)

## Common Hidden Folders


| Folder | Description | Action |
|--------|-------------|--------|
| `.agent-os/` | Legacy agent OS framework | Consolidate to `.claude/` |
| `.ai/` | Legacy AI configuration | Consolidate to `.claude/` |
| `.agent-runtime/` | Runtime symlinks (often dead) | Delete if dead links |
| `.common/` | Orphaned utility scripts | Delete or relocate to `scripts/` |
| `.specify/` | Stale specification templates | Delete if unused |
| `.drcode/` | External tool config (Dr. Code) | Keep if actively used |
| `.slash-commands/` | Command registry | Keep |

## Discovery Commands


```bash
# List all hidden directories with sizes
du -sh .*/ 2>/dev/null | grep -v "^\./\.git"

# Find dead symlinks in hidden folders
find .agent-runtime -type l ! -exec test -e {} \; -print 2>/dev/null

# Count files in each hidden directory
for dir in .claude .agent-os .ai .common .specify; do
  if [ -d "$dir" ]; then
    count=$(find "$dir" -type f | wc -l)
    echo "$dir: $count files"
  fi
done
```

## Cleanup Commands


```bash
# Remove dead symlink directories
rm -rf .agent-runtime/

# Remove stale template directories
rm -rf .specify/

# Remove orphaned utilities (after relocating useful scripts)
rm -rf .common/


*See sub-skills for full details.*
