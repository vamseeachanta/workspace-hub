---
name: crossprovider codex cdn-dependencies-in-engineering-reports-break-of
description: CDN dependencies in engineering reports break offline and archival use
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [dependencies, engineering-reporting, deliverability]
---

Reports depending on KaTeX and Chart.js via CDN are non-self-contained, fragile in air-gapped environments, and subject to version nondeterminism unless pinned with integrity attributes. For engineering reports, make asset bundling the default with `--offline` mode optional or mandatory.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
