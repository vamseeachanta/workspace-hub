---
name: crossprovider codex readiness-matrix-false-completion-masks-underlyi
description: Readiness matrix false-completion masks underlying blockers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [readiness-matrix, test-coverage, coordination]
---

When a readiness matrix marks a lane `implemented` while the actual disposition/routing artifact is still `blocked` or `needs-human-input`, reviewers trust the matrix row. Test the matrix row AND the generated artifact together to catch false-completion states.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
