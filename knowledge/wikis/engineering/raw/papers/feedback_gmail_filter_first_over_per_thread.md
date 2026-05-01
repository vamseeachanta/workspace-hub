> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_gmail_filter_first_over_per_thread.md

---
name: Gmail filter-first beats per-thread state machine 80/20
description: For Gmail inbox hygiene, ingestion-time filters handle ~80% of mail in one pass; reserve per-thread state machines for the actionable ~20% residue
type: feedback
originSessionId: aff40e1f-c80c-4f6d-9797-cba4ecc59a84
---
For Gmail inbox hygiene automation, filters at ingestion beat per-thread state-machine mutation by roughly 80/20. One filter with **"Apply to matching conversations"** handles hundreds of historical plus all future mail; per-thread logic needs a trigger per message and a durable state store.

**Why:** Issue #2017 originally proposed per-thread Gmail mutation for everything. The 2026-04-24 ace-sweep session proved the asymmetry: 4 filters caught 763 historical emails in one pass via "Apply to existing matching conversations," plus every future match automatically. The follow-on #2026 state-machine scope then shrunk — it only tracks the ~20% of actionable threads (client, tenant, tax) that legitimately escape the filter mesh.

**How to apply:** When asked to automate mail processing, design **filter-first (at ingestion), state-machine-second (for the residue).** Skip Inbox + Label + "Apply to existing matching conversations" is a 3-action combo that obsoletes most per-thread logic. Only reach for per-thread state when threads need multi-stage lifecycle tracking (e.g., "awaiting reply → replied → closed"). Classify the traffic first; most mail is fire-and-forget.
