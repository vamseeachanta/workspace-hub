---
name: crossprovider codex quota-collector-policy-authoritative-oauth-only-
description: Quota collector policy: authoritative-oauth-only, refuse estimates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [quota-policy, oauth-pattern, statusline]
---

Quota collectors deliberately use 'authoritative OAuth snapshot only'; they have estimate helpers but refuse to use them, preferring N/A over guesses. This applies to Claude, Codex, and Gemini quota rendering. Fallbacks are local-only, never sent upstream.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
