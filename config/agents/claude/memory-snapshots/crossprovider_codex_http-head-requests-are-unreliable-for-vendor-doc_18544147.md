---
name: crossprovider codex http-head-requests-are-unreliable-for-vendor-doc
description: HTTP HEAD requests are unreliable for vendor documentation validation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [external-api, vendor-quirks, link-validation]
---

Some vendor doc servers (Salesforce, others) reject HEAD requests but accept bounded GET. Link validators that check availability must implement HEAD → bounded-GET fallback, not HEAD-only checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
