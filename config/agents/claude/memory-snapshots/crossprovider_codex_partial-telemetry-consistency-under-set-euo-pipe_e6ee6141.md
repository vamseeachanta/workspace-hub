---
name: crossprovider codex partial-telemetry-consistency-under-set-euo-pipe
description: Partial telemetry consistency under set -euo pipefail
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [shell-scripting, telemetry-consistency, error-handling]
---

When merging data from multiple sources (session JSON + fallback files) in systems with set -euo pipefail, verify consistency at merge points. Mixing session reset_at with quota-file percentage produces invalid intermediate states like C:-%·Nd. Test these hybrid paths explicitly to catch consistency defects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
