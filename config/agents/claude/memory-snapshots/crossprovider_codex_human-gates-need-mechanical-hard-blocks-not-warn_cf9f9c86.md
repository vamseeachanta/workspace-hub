---
name: crossprovider codex human-gates-need-mechanical-hard-blocks-not-warn
description: Human gates need mechanical hard blocks, not warnings; WARN-only is fail-open by default
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [gate-enforcement, user-intent, determinism]
---

Conditional pause gates must exit with code 1 on missing decision/confirmation, not just emit WARN logs. WARN-only looks optional at runtime unless you also track a dated follow-up and explicitly block advancement. Mechanical gates must prevent passage until the condition is met.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
