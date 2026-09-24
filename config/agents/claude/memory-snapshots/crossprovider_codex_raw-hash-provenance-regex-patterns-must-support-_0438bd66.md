---
name: crossprovider codex raw-hash-provenance-regex-patterns-must-support-
description: Raw-hash/provenance regex patterns must support JSON quoted-key syntax
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pattern-matching, json, security-scanning]
---

Scanners looking for private source assignments must handle both unquoted (`source_hash = value`) and JSON-quoted (`"source_hash": "value"`) formats. Session 6 finding #2: the existing scanner pattern failed on quoted JSON assignments, leaving private hashes undetected in JSON artifacts. Pattern should support `"[field_name]": "[32hex]"` syntax.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
