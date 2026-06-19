---
name: crossprovider codex path-safety-requires-explicit-boundary-checks-no
description: Path safety requires explicit boundary checks, not test-time tmpdir
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [security, paths, testing]
---

Scripts accepting arbitrary I/O paths need explicit boundary enforcement (allowed parent dirs, forbidden roots), not just static token/pattern checks. Session 8: script accepted arbitrary --schema, --manifest, --json-report paths and created parent dirs; tests only used tmpdir writes, not dynamic path tracing. Write path safety is not verified by test-time tmpdir safety. Add explicit path validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
