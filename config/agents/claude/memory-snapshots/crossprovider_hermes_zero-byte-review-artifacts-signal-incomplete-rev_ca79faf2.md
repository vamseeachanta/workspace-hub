---
name: crossprovider hermes zero-byte-review-artifacts-signal-incomplete-rev
description: Zero-byte review artifacts signal incomplete reviews
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-artifacts, validation, file-state]
---

Review artifact files (e.g., `2026-05-20-plan-2754-codex-r3.md`) may exist but be 0 bytes when the review process didn't complete or output wasn't saved. File presence alone is insufficient; must verify file size > 0 and content richness before accepting review artifact trail as valid.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
