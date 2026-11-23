---
name: github-issue-tracker-3-automated-progress-updates
description: 'Sub-skill of github-issue-tracker: 3. Automated Progress Updates (+5).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 3. Automated Progress Updates (+5)

## 3. Automated Progress Updates


```javascript
// Update issue with progress from swarm memory
    action: "retrieve",
    key: "issue/54/progress"
})

// Store progress
    action: "store",
    key: "issue/54/latest_update",
    value: JSON.stringify({

*See sub-skills for full details.*

## Completed Tasks


- Architecture review completed
- Dependency analysis finished
- Integration testing verified

## Current Status


- Documentation review in progress
- Integration score: 89% (Excellent)

## Next Steps


- Final validation and merge preparation"
```

## 4. Search and Coordinate Related Issues


```bash
# Search related issues
gh issue list --repo owner/repo --label "integration" --state open --json number,title,labels

# Update issue with milestone
gh issue edit 54 --milestone "v1.0.0"

# Add labels
gh issue edit 54 --add-label "in-progress"

# Transfer issue
gh issue transfer 54 owner/new-repo
```

## 5. Batch Issue Operations


```javascript
[Single Message - Issue Lifecycle Management]:
    // Initialize issue coordination swarm

    // Create multiple related issues
    Bash(`gh issue create --repo owner/repo \
      --title "Feature: Advanced GitHub Integration" \
      --body "Implement comprehensive GitHub workflow automation..." \
      --label "feature,github,high-priority"`)


*See sub-skills for full details.*
