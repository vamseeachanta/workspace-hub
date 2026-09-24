---
name: crossprovider codex path-documentation-can-diverge-from-implementati
description: Path documentation can diverge from implementation; catalog paths need explicit tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [path-handling, testing, documentation]
---

Code may append a path segment that documentation already includes, breaking catalog-friendly direct usage (e.g., docs say `/mnt/ace/.../raw/production/pdq` but code appends that again). Test the documented path as a first-class input, not just happy-path overrides.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
