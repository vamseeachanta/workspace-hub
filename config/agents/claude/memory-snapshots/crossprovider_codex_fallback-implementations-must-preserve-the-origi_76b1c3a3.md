---
name: crossprovider codex fallback-implementations-must-preserve-the-origi
description: Fallback implementations must preserve the original requirement, not weaken it
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [robustness, fallback-design, requirements]
---

Plans offering 'fallback' implementations (e.g., when a primary tool is unavailable) must still satisfy the original acceptance criterion. A fallback that omits exception handling, per-item result capture, or report generation may be simpler but violates the stated requirement. Fallbacks are not alternatives; they are equivalent implementations under different constraints.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
