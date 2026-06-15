---
name: crossprovider codex metadata-loss-in-cron-audit-fingerprints-breaks-
description: Metadata loss in cron audit fingerprints breaks reliable rollback logic
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, metadata-loss, rollback, workspace-hub#3057]
---

cron_apply.py and cron-audit.py return bare fingerprint dicts, discarding task IDs and state-class metadata. Post-apply preservation checks (cron_apply.py:188-199) use a different classifier, causing mismatches. Audit/rollback requires metadata-preserving classification throughout the cutover pipeline.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
