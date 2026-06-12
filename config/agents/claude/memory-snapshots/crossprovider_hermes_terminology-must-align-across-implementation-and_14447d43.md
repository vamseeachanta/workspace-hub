---
name: crossprovider hermes terminology-must-align-across-implementation-and
description: Terminology must align across implementation and user-facing docs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [terminology-consistency, scoping, documentation]
---

Engineering reports use precise terminology; mismatches mislead consumers. B1528: code comment said `psi` is "local downstream axis rotation" but report text said "current heading offset"—different meanings for naval engineers. Define terms once in architecture doc; reference consistently across implementation, tests, and generated output.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
