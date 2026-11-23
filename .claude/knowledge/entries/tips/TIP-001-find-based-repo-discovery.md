---
id: TIP-001
type: tip
title: "Use find-based repo discovery instead of submodule foreach"
category: tooling
tags: [git, submodules, find, repo-discovery, performance]
repos: [workspace-hub]
confidence: 0.85
created: "2026-01-30"
last_validated: "2026-01-30"
source_type: manual
related: []
status: active
access_count: 0
---

# Use Find-based Repo Discovery Instead of Submodule Foreach

## Tip

When iterating over repositories in workspace-hub, use `find` to discover directories with `.git` instead of `git submodule foreach`. This handles repos that are plain clones (not registered submodules) and avoids failures when submodule state is inconsistent.

```bash
# Preferred: find-based discovery
find "$WORKSPACE_ROOT" -maxdepth 2 -name ".git" -type d | while read gitdir; do
    repo_dir="$(dirname "$gitdir")"
    # process repo_dir
done

# Avoid: submodule foreach (misses non-submodule repos)
git submodule foreach --recursive 'echo $sm_path'
```

## Why It Works

workspace-hub contains a mix of git submodules and plain git clones. `git submodule foreach` only iterates registered submodules and fails silently or errors when submodule state is out of sync. `find`-based discovery catches all repos regardless of registration status.
