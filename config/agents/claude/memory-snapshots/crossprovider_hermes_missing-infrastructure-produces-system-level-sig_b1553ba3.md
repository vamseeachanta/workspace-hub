---
name: crossprovider hermes missing-infrastructure-produces-system-level-sig
description: Missing infrastructure produces system-level signal, not per-item blockers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [system-design, observability, planning-pipeline]
---

When global resources (e.g., dispatch ledger) are missing, report as one observability warning, not per-issue blockers. Avoid cascading per-item consequences for system-level infrastructure gaps.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
