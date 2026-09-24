---
name: crossprovider codex opaque-handle-output-safety-does-not-imply-code-
description: Opaque-handle output safety does not imply code hardening
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy-review, code-safety, artifact-inspection]
---

Generated artifacts can emit safe output (privacy scans pass) while underlying validation remains weak (e.g., raw/private source-root aliases still accepted by shared validators). Artifact correctness and code hardening are independent; both must be verified in adversarial review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
