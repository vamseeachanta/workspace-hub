---
name: crossprovider codex multi-delimiter-tokenization-silent-data-loss
description: Multi-delimiter tokenization silent data loss
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [parsing, data-quality, defect]
---

When parsing upstream data with multiple delimiters (pipe + semicolon + comma), ensure split logic matches upstream contract exactly. Collapsing multi-delimited caveats into single strings due to incomplete tokenization is a silent data loss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
