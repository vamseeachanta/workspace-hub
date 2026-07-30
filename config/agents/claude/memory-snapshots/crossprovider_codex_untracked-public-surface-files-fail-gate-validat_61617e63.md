---
name: crossprovider codex untracked-public-surface-files-fail-gate-validat
description: Untracked public-surface files fail gate validation regardless of content
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [ci-gates, public-surface-scan, git-state-coupling]
---

When `--diff-only` scans hit untracked files in public-surface paths, the gate returns fail-closed (`rc=1`) even if the file content passes the legal/public-surface criteria. This is design-intentional: the gate validates git-tracked state, not just content. Implication: CI gates that couple public-surface validation to git tracking will silently reject legitimate untracked changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
