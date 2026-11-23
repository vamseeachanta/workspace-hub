---
name: github-swarm-pr-merge-status
description: 'Sub-skill of github-swarm-pr: Merge Status (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Merge Status (+2)

## Merge Status


- Mergeable: $MERGEABLE
- CI Status: $CI_STATUS
- Approvals: $APPROVALS

## Recommendations


$([ "$MERGEABLE" == "MERGEABLE" ] && echo "- Ready for merge" || echo "- Resolve conflicts first")
$([ "$CI_STATUS" == "SUCCESS" ] && echo "- CI passing" || echo "- Wait for CI to complete")
$([ $APPROVALS -ge 2 ] && echo "- Sufficient approvals" || echo "- Need more reviews")
EOF
}

validate_pr 123
```

## 5. Intelligent Merge Coordination


```bash
# Check if PR is ready to merge
check_merge_readiness() {
  local PR_NUM=$1

  # Get all checks
  CHECKS=$(gh pr checks $PR_NUM --json name,state,conclusion)

  # Count passed/failed/pending
  PASSED=$(echo "$CHECKS" | jq '[.[] | select(.conclusion == "success")] | length')

*See sub-skills for full details.*
