---
name: crossprovider hermes private-data-redaction-family-hash-id-pattern
description: Private data redaction: family-hash ID pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, redaction, metadata-scanning]
---

Metadata-only scanning of private archives (/mnt/ace style) redacts family labels into stable family-<sha256> IDs by default. Supports --reveal-labels local-only mode for internal use. Does not read file contents, only counts dirs/files/bytes/extensions. Safe to publish scans without leaking private structure.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
