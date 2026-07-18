---
name: crossprovider codex handovers-explicitly-state-current-branch-state-
description: Handovers: explicitly state current branch state when work spans merge gates
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [handover, async-work, branch-state, merge-gates]
---

When describing work across approval loops or merge gates, explicitly pin which branch/state is current (e.g., 'main still at E2; #1037 not merged yet; main is still at the $177bn draft state'). Avoid silent assumptions that pre-merge branches have already merged, which sends downstream agents chasing false discrepancies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
