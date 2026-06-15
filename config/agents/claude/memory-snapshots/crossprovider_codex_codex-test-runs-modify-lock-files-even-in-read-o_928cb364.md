---
name: crossprovider codex codex-test-runs-modify-lock-files-even-in-read-o
description: Codex test runs modify lock files even in read-only review; isolate cache and restore
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [codex, tooling-quirk, uv, testing]
---

Running `uv run` under Codex review context modifies uv.lock despite read-only intent. Workaround: set UV_CACHE_DIR=/tmp/uv-cache before tests, then explicitly restore with `git show HEAD:uv.lock > uv.lock` post-test to keep worktree clean and avoid accidental dependency changes in commits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
