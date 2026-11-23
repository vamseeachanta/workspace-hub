---
name: hidden-folder-audit-step-1-inventory-all-hidden-folders
description: 'Sub-skill of hidden-folder-audit: Step 1: Inventory All Hidden Folders
  (+4).'
version: 1.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Step 1: Inventory All Hidden Folders (+4)

## Step 1: Inventory All Hidden Folders


List all hidden directories at the repository root.

```bash
# List all hidden directories (excluding .git)
find . -maxdepth 1 -type d -name ".*" ! -name ".git" | sort

# With sizes
du -sh .*/ 2>/dev/null | grep -v "^0" | sort -hr

# Include symlinks
find . -maxdepth 1 \( -type d -o -type l \) -name ".*" ! -name ".git" | sort
```

## Step 2: Check Git Tracking Status


Determine which hidden folders are tracked, ignored, or untracked.

```bash
# Check if folder is tracked
git ls-files --error-unmatch .folder/ 2>/dev/null && echo "TRACKED" || echo "NOT TRACKED"

# Check if folder is ignored
git check-ignore -v .folder/ 2>/dev/null && echo "IGNORED" || echo "NOT IGNORED"

# List all tracked hidden files
git ls-files | grep "^\." | cut -d'/' -f1 | sort -u

# List all gitignored hidden folders
git status --porcelain --ignored | grep "^!!" | grep "^\./\." | cut -d'/' -f2 | sort -u
```

## Step 3: Analyze Content Overlap


Check for duplicate or overlapping content between hidden folders.

```bash
# Compare agent configurations
diff -rq .agent-os/agents/ .claude/agents/ 2>/dev/null

# Find duplicate files by name
find .agent-os .ai .claude -name "*.md" -type f 2>/dev/null | xargs -I {} basename {} | sort | uniq -d

# Find duplicate files by content (MD5)

*See sub-skills for full details.*

## Step 4: Identify Authoritative Source


Determine which folder should be the single source of truth.

**Criteria for Authoritative Source:**
1. **Git tracking** - Tracked folders are more likely authoritative
2. **Recency** - Check last modification dates
3. **Completeness** - More complete configuration wins
4. **Active use** - Referenced in CI/CD, scripts, documentation
5. **Tool requirements** - Some tools require specific folder names

```bash

*See sub-skills for full details.*

## Step 5: Plan Consolidation


Create a migration plan based on analysis.

**Migration Checklist:**
- [ ] Identify target folder structure
- [ ] List files to migrate
- [ ] Identify files to delete
- [ ] Update references in code/scripts
- [ ] Update .gitignore
- [ ] Test after migration
