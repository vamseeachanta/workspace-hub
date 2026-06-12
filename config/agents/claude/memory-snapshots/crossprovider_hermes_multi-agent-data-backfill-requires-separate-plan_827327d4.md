---
name: crossprovider hermes multi-agent-data-backfill-requires-separate-plan
description: Multi-agent data backfill requires separate plan-only session with explicit non-self-approval rule
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-migration, planning-gate, agent-handoff]
---

Data migrations benefit from schema-aware planning (Claude over Codex). Use dedicated planning-only session: plan to file, post as comment, stop—do not implement. User reviews morning; separate implementation session begins after approval. Hard rule: no self-approval flip. Prevents rework and keeps design review gate intact.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
