---
name: hermes-blocked-status-auto-unblocked
description: Hermes gateway auto-unblocks --initial-status blocked cards within minutes; blocked is NOT a parking spot for imported work
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 000d04a3-532a-4959-becb-59b1f1349fb3
---

Cards created with `hermes kanban create --initial-status blocked` (with no `blocked_reason` or `consecutive_failures` set) are auto-unblocked to `ready` by the gateway specifier within minutes. The Hermes runtime is designed to keep workers busy; "blocked" semantically means "needs human ops / R3 gate", and the auxiliary unblocker treats fresh-import blocked-without-reason as eligible for promotion.

**Why:** Discovered empirically 2026-05-22 while bulk-loading 1536 kanban cards across 45 boards. The patched loader switched from `--triage` to `--initial-status blocked` thinking blocked was safe; within minutes 100+ blocked cards had advanced to `ready` and workers were claiming them. Only the pre-existing 4 cards on `default` board survived as blocked indefinitely — they had been blocked BY a worker after detecting an issue, so they carried `blocked_reason` metadata.

**How to apply:** For bulk imports into Hermes that genuinely should NOT be dispatched until human review:
- Use `hermes kanban archive` after create (terminal non-dispatch state) — but then `unarchive` is needed to use them.
- OR provision the cards with a placeholder `blocked_reason` like "imported-pending-review" via `hermes kanban edit` so the unblocker recognizes them as truly blocked.
- OR don't use Hermes runtime at all; keep imports as YAML-only "planning kanban" and promote individually via `hermes kanban specify <one-card>` when ready.
- The Hermes design preference is to dispatch — fighting it requires explicit archive or reason-flag.

Related: [[hermes-triage-is-pipeline-entry]] — the sibling failure mode where `--triage` was thought safe.
