---
name: crossprovider gemini re-run-guards-prevent-children-list-duplication
description: Re-run guards prevent children list duplication
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [idempotency, data-corruption, work-queue]
---

Feature WRKs run new-feature.sh to scaffold children. If re-run against a WRK with existing children:, it will duplicate them and corrupt the list. Guard at start: if `children:` already contains WRK-NNN entries, exit 1 before any writes.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
