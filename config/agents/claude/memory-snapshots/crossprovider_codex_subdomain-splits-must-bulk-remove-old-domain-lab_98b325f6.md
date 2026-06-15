---
name: crossprovider codex subdomain-splits-must-bulk-remove-old-domain-lab
description: Subdomain splits must bulk-remove old domain labels
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [migration, relabeling, invariants, ordering]
---

Splitting `domain:subsea` into `domain:subsea-risers` leaves old label on cards. If both labels exist, `target_board()` uses the first it finds, creating order-dependent placement. Bulk migration must remove obsolete labels.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
