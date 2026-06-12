---
name: crossprovider codex plan-safety-claims-must-be-verified-against-live
description: Plan safety claims must be verified against live code, not narrative consistency
metadata:
  type: reference
  source: codex
  bridged: 2026-05-27
  tags: [plan-review, adversarial-review, live-code-verification]
---

Plans describing existing behavior as 'triage' when live code uses `--initial-status blocked` conceal actual safety surface. Safe: artifact reviews must spot-check critical claims against HEAD source.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
