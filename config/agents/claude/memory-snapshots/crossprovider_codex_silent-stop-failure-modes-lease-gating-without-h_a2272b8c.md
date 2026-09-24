---
name: crossprovider codex silent-stop-failure-modes-lease-gating-without-h
description: Silent-stop failure modes (lease gating without holder detection) require independent absence monitoring
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [monitoring, silent-failure, coordination]
---

Gating an existing cron behind 'holds_venue()' creates a new failure mode: if no holder exists or acquisition fails, nothing runs but no alert fires. Requires separate monitor for 'stale SLA marker + no active lease holder' to detect fleet-wide silent stops.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
