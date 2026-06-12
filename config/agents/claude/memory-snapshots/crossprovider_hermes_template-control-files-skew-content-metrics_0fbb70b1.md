---
name: crossprovider hermes template-control-files-skew-content-metrics
description: Template/control files skew content metrics
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [content-scanning, metrics, templates, noise-reduction]
---

When computing freshness, broken-link, or metric statistics on markdown/wiki corpus, template files (_template.md) and control files create false positives. Explicitly skip them during iteration and track skipped items separately to avoid noisy recommendations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
