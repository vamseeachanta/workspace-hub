---
name: crossprovider codex deferred-correctness-checks-remain-accepted-risk
description: Deferred correctness checks remain accepted risk and should be explicitly named
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, scope, risk-management]
---

When deferring checks that affect CI integrity (e.g., workflow schema validation), the plan must explicitly acknowledge this as residual risk and justify why the deferral doesn't leave CI in a broken state. Generic arbitrary thresholds ('until >3 workflows per repo') are insufficient rationale. #2443 deferred workflow validation without naming the risk.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
