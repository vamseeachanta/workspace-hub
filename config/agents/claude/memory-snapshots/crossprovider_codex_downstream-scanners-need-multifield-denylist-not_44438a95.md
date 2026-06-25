---
name: crossprovider codex downstream-scanners-need-multifield-denylist-not
description: Downstream scanners need multifield denylist, not single-field checks
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [dnv, scanner, denylist-design, multi-field]
---

A comment scanner that only forbids exact source-label strings still leaks via adjacent fields (filenames, relative paths, raw hashes). Identity can travel through semantic clusters. Build denylist over all identity-bearing fields, not just the primary one.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
