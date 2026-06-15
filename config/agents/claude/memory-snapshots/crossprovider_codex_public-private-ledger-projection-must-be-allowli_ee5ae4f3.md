---
name: crossprovider codex public-private-ledger-projection-must-be-allowli
description: Public/private ledger projection must be allowlist-only
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [privacy, ledger-design, data-projection]
---

Deny-list-only approach to filtering private data from ledgers will miss unknown client names and unanticipated field leaks. Use allowlist-only schema for public projection with explicit rules for each ledger field. Test fixtures should include leak-through paths: ledger fields, citation sidecars, wiki-target metadata, nested objects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
