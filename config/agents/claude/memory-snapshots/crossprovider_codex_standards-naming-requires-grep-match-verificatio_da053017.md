---
name: crossprovider codex standards-naming-requires-grep-match-verificatio
description: Standards naming requires grep-match verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [standards, verification, governance, digitalmodel]
---

Every standard named in entry metadata (API, DNV, ASME) must be grep-matchable to an implementation file in the codebase. Overclaim precedent shows this discipline prevents standards being cited without corresponding code or documentation. Use grep-match audits at PR/review time.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
