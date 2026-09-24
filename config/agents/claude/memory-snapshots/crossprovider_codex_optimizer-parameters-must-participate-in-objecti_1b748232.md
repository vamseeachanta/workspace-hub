---
name: crossprovider codex optimizer-parameters-must-participate-in-objecti
description: Optimizer parameters must participate in objective
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [optimization, parameter-coupling, correctness]
---

Fitted parameters returned by optimization (especially physical/domain outputs like permeability, initial reserves) must actually affect the objective function being minimized. Parameters that only affect bounds/initialization but not the residual create meaningless fits where returned physical values depend on arbitrary optimizer guesses. Defect pattern: uncoupled `reD` parameter in type-curve matching.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
