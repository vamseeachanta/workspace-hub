---
name: crossprovider codex verify-upstream-validators-pass-not-just-issue-l
description: Verify upstream validators pass, not just issue labels
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [plan-review, dependencies, validation]
---

When a plan depends on closed issues (#66, #68, #69), don't trust the label state alone—run the upstream validators to confirm they actually pass. Session 1 found #66 labeled complete but its own validator failing on tracked code, invalidating downstream assumptions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
