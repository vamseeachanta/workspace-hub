---
name: crossprovider codex explicit-out-of-scope-boundaries-prevent-silent-
description: Explicit out-of-scope boundaries prevent silent assumptions
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [spec-clarity, scope-definition, ambiguity-resolution]
---

Rather than implying scope, explicitly enumerate what's excluded (Unicode normalization handling, symlink policy, mode/timestamp variance tolerance). WRK-188 evolved from implicit to explicit scope statements, which prevented misaligned expectations during execution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
