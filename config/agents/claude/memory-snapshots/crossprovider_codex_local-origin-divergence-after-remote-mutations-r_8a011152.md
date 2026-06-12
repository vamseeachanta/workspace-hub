---
name: crossprovider codex local-origin-divergence-after-remote-mutations-r
description: Local-origin divergence after remote mutations requires explicit reconciliation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git, remote-mutations, local-state]
---

When a remote repository is mutated (archive, branch delete, force-push), local clones diverge. Document this explicitly in operational artifacts (e.g., STATUS-FROZEN.md) or force-sync with `git fetch && git reset --hard origin/main`. #2745 execution diverged local HEAD after remote archive, creating future confusion; reversal procedure must include explicit reconciliation step.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
