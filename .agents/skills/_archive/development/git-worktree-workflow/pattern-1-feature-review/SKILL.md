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
# Terminal 1: Development Codex
cd /project-feature
Codex "Implement the new authentication module"

# Terminal 2: Review Codex
cd /project
Codex "Review the authentication changes in feature-auth branch"
```

## Pattern 2: Multi-Feature Development


Work on multiple features simultaneously:

```bash
# Setup worktrees
git worktree add -b feature-api ../project-api main
git worktree add -b feature-ui ../project-ui main
git worktree add -b feature-tests ../project-tests main

# Run Codex in each (separate terminals)
cd ../project-api && Codex "Build REST API endpoints"
cd ../project-ui && Codex "Create React components"
cd ../project-tests && Codex "Write integration tests"
```

## Pattern 3: Subagent Verification


Main Codex spawns verification in separate worktree:

```bash
# Main Codex working in /project
# Creates verification worktree:
git worktree add --detach ../project-verify HEAD

# Spawns subagent to verify:
cd ../project-verify && Codex -p "Verify the implementation works correctly"
```

## Pattern 4: A/B Implementation


Compare two approaches:

```bash
# Create two worktrees from same point
git worktree add -b approach-a ../project-a main
git worktree add -b approach-b ../project-b main

# Different Codex instances try different solutions
cd ../project-a && Codex "Implement caching using Redis"
cd ../project-b && Codex "Implement caching using Memcached"

# Compare results
diff -r ../project-a/src ../project-b/src
```
