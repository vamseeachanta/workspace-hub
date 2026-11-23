---
name: repo-cleanup-progress-tracking-commands
description: 'Sub-skill of repo-cleanup: Progress Tracking Commands (+1).'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Progress Tracking Commands (+1)

## Progress Tracking Commands


```bash
# Count tracked files in each hidden folder
for dir in .claude .agent-os .ai; do
  count=$(git ls-files "$dir" 2>/dev/null | wc -l)
  echo "$dir: $count files"
done

# Count all files (tracked + untracked)
for dir in .claude .agent-os .ai .common .specify; do
  if [ -d "$dir" ]; then

*See sub-skills for full details.*

## Verification After Merge


```bash
# Verify no files were lost
expected_count=150  # Set to sum of source folders
actual_count=$(git ls-files .claude | wc -l)
echo "Expected: $expected_count, Actual: $actual_count"

# List any untracked files that might have been missed
git status --porcelain | grep "^??" | grep -E "^\?\? \.(claude|agent-os|ai)/"
```
