---
name: crossprovider codex fingerprint-metadata-loss-prevents-rollback-in-t
description: Fingerprint metadata loss prevents rollback in transactional systems
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [transactional-pattern, metadata-loss, rollback]
---

Transactional cron operations (cron_apply.py, cron-audit.py) return bare fingerprint dicts while discarding catalog task IDs and sibling metadata. Post-apply rollback (cron_apply.py:188-199) cannot match rolled-back lines to their catalog sources, preventing proper deduplication and causing catalog-owned task management to fail. Metadata must be preserved through the full transaction lifecycle.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
