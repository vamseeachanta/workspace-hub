---
name: crossprovider codex path-canonicalization-before-containment-checks-
description: Path canonicalization before containment checks: explicit algorithm required
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [security, plan-review]
---

When validating relative paths (e.g., `fields/page.html`), explicitly canonicalize them against a known base directory before checking containment. Plan text must specify the base resolution algorithm, not leave it implicit—this prevents path-traversal oversights.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
