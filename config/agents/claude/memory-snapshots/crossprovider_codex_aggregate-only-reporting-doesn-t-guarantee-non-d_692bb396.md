---
name: crossprovider codex aggregate-only-reporting-doesn-t-guarantee-non-d
description: Aggregate-only reporting doesn't guarantee non-derivable public data
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy, de-identification, public-interface, data-leakage]
---

Emitting aggregate bucket names or group identifiers as public JSON keys can leak identity if those names are derived from private sources or can be joined back through manifest order or structural keys. True de-identification requires opaque/hashed identifiers, not just aggregation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
