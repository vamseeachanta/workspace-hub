---
name: crossprovider codex exact-label-scans-must-be-section-diff-scoped-on
description: Exact-label scans must be section/diff-scoped on pages with historical metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy-scanning, page-updates, regression-risk]
---

When adding sanitized generated sections to existing pages containing historical exact-label metadata, whole-file scans false-positive on the historical data. Scans must be bounded to newly added lines, generated sections only, or diff-scoped to separate implementation leakage from pre-existing page metadata.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
