---
name: git-worktree-workflow-pattern-1-feature-review
description: 'Sub-skill of git-worktree-workflow: Pattern 1: Feature + Review (+3).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Pattern 1: Feature + Review (+3)

## Pattern 1: Feature + Review


Run development and review in parallel:

```bash
# Terminal 1: Development Claude
cd /project-feature
claude "Implement the new authentication module"

# Terminal 2: Review Claude
cd /project
claude "Review the authentication changes in feature-auth branch"
```

## Pattern 2: Multi-Feature Development


Work on multiple features simultaneously:

```bash
# Setup worktrees
git worktree add -b feature-api ../project-api main
git worktree add -b feature-ui ../project-ui main
git worktree add -b feature-tests ../project-tests main

# Run Claude in each (separate terminals)
cd ../project-api && claude "Build REST API endpoints"
cd ../project-ui && claude "Create React components"
cd ../project-tests && claude "Write integration tests"
```

## Pattern 3: Subagent Verification


Main Claude spawns verification in separate worktree:

```bash
# Main Claude working in /project
# Creates verification worktree:
git worktree add --detach ../project-verify HEAD

# Spawns subagent to verify:
cd ../project-verify && claude -p "Verify the implementation works correctly"
```

## Pattern 4: A/B Implementation


Compare two approaches:

```bash
# Create two worktrees from same point
git worktree add -b approach-a ../project-a main
git worktree add -b approach-b ../project-b main

# Different Claude instances try different solutions
cd ../project-a && claude "Implement caching using Redis"
cd ../project-b && claude "Implement caching using Memcached"

# Compare results
diff -r ../project-a/src ../project-b/src
```
