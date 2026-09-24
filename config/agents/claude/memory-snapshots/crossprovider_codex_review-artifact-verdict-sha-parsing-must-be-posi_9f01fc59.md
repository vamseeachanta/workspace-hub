---
name: crossprovider codex review-artifact-verdict-sha-parsing-must-be-posi
description: Review artifact verdict/SHA parsing must be position-constrained
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-cd, review-automation, parser-safety]
---

The continuous-planning pipeline's acceptance of the first APPROVE/MINOR/MAJOR token anywhere in a file (and Plan-SHA256 on any matching line) creates false negatives when review text quotes examples or contains phrases like 'No MAJOR blockers'. Parser must enforce structured metadata headers or clearly delimited sections.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
