---
name: crossprovider codex generated-artifacts-with-off-repo-data-need-live
description: Generated artifacts with off-repo data need live validation, not just test fixtures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, artifacts, data-validation, external-dependencies]
---

If CSV/dataset outputs depend on external PDFs or off-repo data, tests using only synthetic fixtures won't detect drift. When regenerating from real sources, normalization or parsing changes are silent. Validation must include live-source regeneration or fixture accuracy verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
