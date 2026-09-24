---
name: crossprovider codex validator-gate-placement-risk
description: Validator gate placement risk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, control-flow, defect-class]
---

Early returns in validators bypass downstream constraints. Placing acceptance gates only inside conditional branches (e.g., scheduler-backed) allows invalid states through when the condition is false. Consolidate constraints before early returns or move gates outside conditionals.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
