---
name: crossprovider gemini byte-boundary-truncation-corrupts-utf-8-multi-by
description: Byte-boundary truncation corrupts UTF-8 multi-byte characters
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [text-encoding, payload-handling, shell-scripting]
---

Using `head -c 5000000` to limit payload size cuts arbitrary bytes, leaving partial UTF-8 sequences that produce invalid encoding. Line-based (`head -n`) or encoding-aware truncation required to avoid garbled text downstream.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
