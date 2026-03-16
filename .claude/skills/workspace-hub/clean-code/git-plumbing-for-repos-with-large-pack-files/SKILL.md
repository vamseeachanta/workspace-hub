---
name: clean-code-git-plumbing-for-repos-with-large-pack-files
description: 'Sub-skill of clean-code: Git Plumbing for Repos with Large Pack Files
  (+1).'
version: 2.1.0
category: workspace
type: reference
scripts_exempt: true
---

# Git Plumbing for Repos with Large Pack Files (+1)

## Git Plumbing for Repos with Large Pack Files


`git commit` hangs indefinitely on repos with pack files ≥4GB (e.g., digitalmodel). Use
plumbing commands instead:

```bash
# Standard commit — HANGS on repos with large pack files
git commit -m "message"   # ← do NOT use

# Plumbing workflow — always safe regardless of repo size
TREE=$(git write-tree)
PARENT=$(git rev-parse HEAD)
COMMIT=$(git commit-tree "$TREE" -p "$PARENT" -m "your message here")
git update-ref HEAD "$COMMIT"
```

After this, update the hub-level submodule pointer:

```bash
# From workspace-hub root
git add <submodule-dir>
git commit -m "chore: update <submodule> pointer"
```


## Parallel Execution for Multi-Repo God Object Sprints


When splitting files across multiple repos simultaneously:

```
TeamCreate → spawn agent-repo-A + agent-repo-B in parallel
  agent-repo-A: handles one repo (worldenergydata)
  agent-repo-B: handles other repo (digitalmodel)

Rules:
  - Never run two agents on the SAME repo concurrently (index.lock contention)
  - Update hub submodule pointer AFTER each repo agent completes
  - agent-repo-B should not start WRK-592 until WRK-591 is committed
    (same __init__.py in same repo — sequential within a repo, parallel across repos)
```

---
