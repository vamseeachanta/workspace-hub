---
name: hidden-folder-audit-verify-hidden-folder-state
description: 'Sub-skill of hidden-folder-audit: Verify Hidden Folder State (+3).'
version: 1.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Verify Hidden Folder State (+3)

## Verify Hidden Folder State


```bash
# List remaining hidden folders (should be minimal)
echo "=== Remaining Hidden Folders ==="
find . -maxdepth 1 -type d -name ".*" ! -name ".git" | sort

# Expected remaining folders:
# .claude/       - AI configuration (authoritative)
# .github/       - GitHub workflows
# .githooks/     - Git hooks
# .vscode/       - VS Code settings (if tracked)

*See sub-skills for full details.*

## Verify Consolidation Targets


```bash
# Verify .claude/ structure
echo "=== .claude/ Structure ==="
ls -la .claude/

# Verify scripts/git/ exists if .git-commands was consolidated
echo "=== scripts/git/ ==="
ls -la scripts/git/ 2>/dev/null || echo "scripts/git/ does not exist"

# Verify .claude/docs/commands/ if .slash-commands was consolidated

*See sub-skills for full details.*

## Verify Git Status


```bash
# Check for untracked hidden folders
echo "=== Untracked Hidden Folders ==="
git status --porcelain | grep "^??" | grep "^\./\." || echo "None found"

# Verify .gitignore includes runtime folders
echo "=== .gitignore Hidden Folder Entries ==="

# Count tracked files in .claude/
echo "=== .claude/ Tracked Files ==="
git ls-files .claude/ | wc -l
```

## Final State Checklist


```bash
# Run all verification checks
echo "=== Final State Verification ==="

# 1. Only expected hidden folders exist
if [ "$hidden_count" -eq 0 ]; then
  echo "[OK] No unexpected hidden folders"
else
  echo "[WARN] $hidden_count unexpected hidden folders found"
fi

*See sub-skills for full details.*
