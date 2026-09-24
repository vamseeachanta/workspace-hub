---
name: crossprovider codex safety-gates-must-validate-before-traversal-not-
description: Safety gates must validate before traversal, not after
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, control-flow, gate-placement]
---

Content-value filters, policy checks, and similar gates should validate their artifacts in the control-flow path BEFORE corpus enumeration/traversal begins, not as post-processing. Early validation ensures rejections prevent any corpus access; late validation creates transient exposure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
