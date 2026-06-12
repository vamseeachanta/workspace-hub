---
name: crossprovider hermes enforcement-controls-documented-as-global-but-se
description: Enforcement controls documented as global but selectively implemented create false confidence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [enforcement-env, control-plane, false-confidence, hook-implementation]
---

DISABLE_ENFORCEMENT and FORCE_PLAN_GATE_STRICT are documented as repo-wide master switches, but only pre-commit honors them; pre-push doesn't source enforcement-env at all, and CI hardcodes --strict flag. Tests checking file presence (hook contains string) miss the implementation gap. Result: operators think enforcement is disabled during incidents, but push still gets blocked.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
