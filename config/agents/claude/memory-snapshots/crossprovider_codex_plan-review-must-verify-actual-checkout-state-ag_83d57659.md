---
name: crossprovider codex plan-review-must-verify-actual-checkout-state-ag
description: Plan review must verify actual checkout state against claimed baseline
metadata:
  type: reference
  source: codex
  bridged: 2026-08-13
  tags: [plan-review, verification, git-state]
---

When measuring pytest/gating behavior for a plan, verify the target checkout is at the claimed state (branch, clean tree). In this case, the branch was on a feature branch with modified `pytest.ini`, `uv.lock`, and root `conftest.py`, not the claimed clean `origin/main@1dcc59c9`. Dirty state can mask or alter the behavior being measured; separate worktree-dependent measurements from source-file evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
