---
name: crossprovider codex data-gates-require-content-validation-not-just-f
description: Data gates require content validation, not just file presence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gate-design, data-integrity, requirements]
---

Gates meant to control data flow (e.g., 'only extract after taxonomy gate passes') must validate schema/row contracts, not just check file-exists or substring-contains. A gate that only confirms file presence is a no-op; enforce the actual data requirements.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
