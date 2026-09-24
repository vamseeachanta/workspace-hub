---
name: crossprovider codex git-auto-sync-races-on-ntfs-fuse-verify-with-ls-
description: Git auto-sync races on NTFS-FUSE; verify with ls-remote
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, ci-cd, ntfs-fuse, automation-hazard]
---

Auto-sync can push commits before local sequence completes. If feature branch stays checked out, subsequent auto-syncs target it and sweep unrelated files into the PR. Verify remote state with `git ls-remote origin <branch>`, not push output. Checkout main after work to prevent auto-sync pollution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
