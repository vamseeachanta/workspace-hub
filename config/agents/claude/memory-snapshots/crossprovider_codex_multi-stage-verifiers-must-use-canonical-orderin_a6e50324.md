---
name: crossprovider codex multi-stage-verifiers-must-use-canonical-orderin
description: Multi-stage verifiers must use canonical ordering logic
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verification-consistency, multi-gate-architecture]
---

When the same rule is verified at multiple gates (e.g., plan-stage + close-stage verifiers), they must implement identical logic. Disagreement on semantic ordering causes divergence; establish one canonical rule and update both verification points together.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
