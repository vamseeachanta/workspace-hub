---
name: github-modes-batch-operations
description: 'Sub-skill of github-modes: Batch Operations.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Batch Operations

## Batch Operations


All GitHub modes support batch operations for maximum efficiency:

```bash
# Parallel issue creation
gh issue create --title "Task 1" --body "..." &
gh issue create --title "Task 2" --body "..." &
gh issue create --title "Task 3" --body "..." &
wait

# Batch label management
for issue in 1 2 3 4 5; do
  gh issue edit $issue --add-label "sprint-24" &
done
wait

# Parallel PR reviews
for pr in 10 11 12; do
  gh pr review $pr --approve --body "Automated approval" &
done
wait
```
