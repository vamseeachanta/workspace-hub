---
name: crossprovider codex test-full-pre-push-hook-surface-not-just-happy-p
description: Test full pre-push hook surface, not just happy paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-hooks, testing, regression]
---

Pre-push hooks invoke multiple code paths (per-repo loops, coverage flags, etc.); fixture-copy tests like test_check_all.sh catch refactoring regressions that happy-path coverage misses.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
