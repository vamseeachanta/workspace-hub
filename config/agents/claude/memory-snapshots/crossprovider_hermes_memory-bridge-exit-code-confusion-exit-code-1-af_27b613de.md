---
name: crossprovider hermes memory-bridge-exit-code-confusion-exit-code-1-af
description: Memory bridge exit-code confusion: __EXIT_CODE__=1 after stash phase doesn't signal failure
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-bridge, git-workflow, signal-interpretation]
---

When `scripts/memory/pre-bridge-quality.sh --fix` runs, it may emit `__EXIT_CODE__=1` after reaching the 'stashing before pull' phase, but this doesn't indicate failure if the memory files are actually committed, pushed to `origin/main`, the repo is clean, and drift check passes afterward. Verify completion by checking commit/push success and final drift state, not the exit code alone.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
