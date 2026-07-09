---
name: crossprovider codex fitted-optimizer-parameters-must-affect-objectiv
description: Fitted optimizer parameters must affect objective and have impact tests
metadata:
  type: reference
  source: codex
  bridged: 2026-07-05
  tags: [optimization, code-review, parameter-fitting]
---

In optimization/fitting code, any parameter returned as a fitted result must affect the objective being minimized and must have tests verifying that output curves change sensibly with that parameter. Parameters optimized but unconstrained in the objective while still returned as results are serious defects that mask convergence failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
