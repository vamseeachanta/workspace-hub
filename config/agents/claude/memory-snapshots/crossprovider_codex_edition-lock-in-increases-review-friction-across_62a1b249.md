---
name: crossprovider codex edition-lock-in-increases-review-friction-across
description: Edition lock-in increases review friction across standards updates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [standards-implementation, versioning, maintainability]
---

Hardcoding a standard's edition in code, tests, docs, and resolver pages (e.g., F106 2003 vs 2021-09) makes scope changes expensive and creates multi-round reviews if the edition shifts. Consider parameterizing edition at the point of use or making it explicit in the public API so callers know which edition they're citing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
