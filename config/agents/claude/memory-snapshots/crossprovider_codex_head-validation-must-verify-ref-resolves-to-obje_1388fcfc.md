---
name: crossprovider codex head-validation-must-verify-ref-resolves-to-obje
description: HEAD validation must verify ref resolves to object
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, validation, spec-compliance]
---

Dangling/unborn state requires explicit distinction: "authorized unborn main" (OK for CAS creation) vs "corrupt dangling HEAD" (fail-closed). Symbolic-ref text match alone is insufficient; verify the ref resolves to an actual commit object.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
