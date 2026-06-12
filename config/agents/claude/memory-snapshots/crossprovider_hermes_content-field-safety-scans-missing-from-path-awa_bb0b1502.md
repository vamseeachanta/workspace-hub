---
name: crossprovider hermes content-field-safety-scans-missing-from-path-awa
description: Content-field safety scans missing from path-aware validators
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [safety-scan-gap, content-validation, public-safety]
---

Validators checking node/edge `path` fields for leakage miss titles, tags, content, and metadata fields that copy directly from source frontmatter. A public wiki page's title containing `/mnt/ace/private` or secrets can leak through unscanned fields.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
