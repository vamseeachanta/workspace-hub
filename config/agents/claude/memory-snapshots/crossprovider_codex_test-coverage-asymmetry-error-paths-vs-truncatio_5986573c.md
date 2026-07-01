---
name: crossprovider codex test-coverage-asymmetry-error-paths-vs-truncatio
description: Test coverage asymmetry: error paths vs. truncation in streaming
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [testing, streaming, edge-cases, qa]
---

Test suites for download/streaming often cover HTTP errors and HTML responses thoroughly but omit truncation/short-read scenarios. Truncation is equally critical in production. Test coverage should explicitly include partial/truncated responses, not just exception types.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
