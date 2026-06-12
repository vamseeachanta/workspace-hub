---
name: crossprovider hermes manual-csv-field-edits-introduce-embedded-newlin
description: Manual CSV field edits introduce embedded newlines that break parsing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [csv-data, batch-processing, data-corruption]
---

Editing CSV fields by hand (e.g., 'frontmatter:sources\n,public-wiki') embeds newlines that corrupt rows. Per-line editing is fragile; use sed/regex batch fixes with post-fix verification.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
