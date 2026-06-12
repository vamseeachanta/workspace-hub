---
name: crossprovider hermes path-validation-without-identifier-filtering-cre
description: Path validation without identifier filtering creates false positives
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, false-positives, cross-platform]
---

Treating all backticked tokens as filesystem paths catches non-path identifiers (CamelCase classes, ALL_CAPS constants) and invalid .git references in worktrees. Tighten to require filesystem-like patterns (/, ./, ../, extensions) and filter symbols.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
