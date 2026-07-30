---
name: crossprovider codex pattern-based-ci-coverage-must-be-explicitly-inv
description: Pattern-based CI coverage must be explicitly invoked, not left implicit
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [ci, coverage]
---

GitHub Actions enumerated specific paths for scanning but had pattern-selector modes (review artifacts, sidecars) available but not invoked. CI coverage must either enumerate all artifacts or explicitly invoke selectors; implicit gaps hide behind the appearance of coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
