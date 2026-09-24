---
name: crossprovider gemini utf-8-byte-truncation-corrupts-multibyte-charact
description: UTF-8 byte-truncation corrupts multibyte characters
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [text-processing, encoding-hazard, utf8]
---

Truncating text payloads with `head -c <bytes>` can split multibyte UTF-8 sequences mid-character, producing invalid encoding. Safer alternatives include line-based truncation (`head -n`) or validating character boundaries before truncation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
