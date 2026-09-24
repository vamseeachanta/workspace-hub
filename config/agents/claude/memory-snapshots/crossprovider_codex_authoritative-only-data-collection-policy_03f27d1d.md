---
name: crossprovider codex authoritative-only-data-collection-policy
description: Authoritative-only data collection policy
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, data-policy, quota-tracking]
---

Shared quota/status collectors should enforce authoritative-only data (e.g., OAuth snapshots); keep fallback estimates local to display layers, not in shared collectors. This prevents stale or estimated data from becoming canonical upstream.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
