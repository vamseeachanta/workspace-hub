---
name: crossprovider codex session-signal-files-require-rotation-weekly-hea
description: Session-signal files require rotation + weekly health trends, not just hard limits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [state-management, archival, observability, automation]
---

Tracked JSONL files like `cost-tracking.jsonl` grow unbounded; pair size-blocking hooks with monthly rotation (date-suffixed archive + gzip) and weekly size-trend reports. Real data point: 45 MB cost-tracking file + 58 MB total state directory → 6–8 week TTL to 100 MB GitHub hard limit without rotation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
