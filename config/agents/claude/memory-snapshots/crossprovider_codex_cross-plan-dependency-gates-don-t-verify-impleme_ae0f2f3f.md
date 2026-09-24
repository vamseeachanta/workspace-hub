---
name: crossprovider codex cross-plan-dependency-gates-don-t-verify-impleme
description: Cross-plan dependency gates don't verify implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, dependencies, gate-design]
---

Plans that depend on APIs from other open issues can pass review when gated only on 'plan-approved' status. These gates must verify that the dependency's implementation is actually landed and importable, not just that its plan is approved. Multiple plans in this batch reference `OrcaWaveAssetResolver` and other future APIs that exist only in sibling plans, not in source.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
