---
name: crossprovider codex privacy-gate-verification-paths-must-bind-to-act
description: Privacy gate verification paths must bind to actual artifact, not just function existence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy-gates, verification, testing]
---

When a gate references a verification script (e.g., `check-completeness-before-close.sh 736`), the script must validate *that specific issue's* artifact, not just any artifact matching its schema. Session 2 found that the command existed but validated parent #725's completeness, not #736's. Tests should verify correctness by name/ID, not assume script-presence equals proof.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
