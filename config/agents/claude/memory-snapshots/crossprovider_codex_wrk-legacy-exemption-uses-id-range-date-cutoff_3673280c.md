---
name: crossprovider codex wrk-legacy-exemption-uses-id-range-date-cutoff
description: WRK legacy exemption uses ID range + date cutoff
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [gates, wrk-orchestration, backward-compatibility]
---

New WRKs (≥658) created before 2026-03-09 cutoff auto-pass legacy gates; older WRKs (ID<658) always pass. Two-tier check (int suffix + created_at timestamp) enables backward compatibility when enforcing new logging requirements.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
