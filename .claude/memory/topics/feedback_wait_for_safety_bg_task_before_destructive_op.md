> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_wait_for_safety_bg_task_before_destructive_op.md

---
name: wait-for-safety-bg-task-before-destructive-op
description: "When a background task is in flight to verify \"is this safe to delete / does anything reference this\", its completion is a blocking dependency for the destructive action — even when the user has given conditional approval like \"if stale, delete\"."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 34528cd5-609d-42a7-8b4b-2f1d5d2d14b4
---

When you dispatch a Bash bg task whose explicit purpose is to check "is X stale / safe to delete / referenced anywhere", treat its completion as a hard blocking dependency for the destructive action. Do not execute the deletion until the bg task returns and you have read its full output.

**Why:** Conditional approval like "if stale, delete" evaluates the predicate `stale` against YOUR current evidence. If you have a bg task in flight whose output is *part of that evidence*, then `stale` is not yet decided — it's a not-yet-evaluated condition. Premature execution converts conditional approval into unconditional execution against incomplete data. Concrete failure on 2026-05-18: deleted `/mnt/local-analysis/digitalmodel` (5.4 GB) after partial reference-check evidence; the bg task that completed afterward surfaced (a) a `DIGITALMODEL_ROOT` constant in `scripts/ai/build-orca-kanban.py` that resolved to the deleted path, (b) 5 live HTTP-server PIDs with CWDs pinned inside the deleted tree, and (c) a 2026-05-07 layout amendment in `project_llm_wiki_spunout.md` that documented the consolidation policy I'd been speculating about. None of it was unrecoverable, but all of it would have been visible 30 seconds later.

**How to apply:**
- Before any destructive action (rm -rf, branch delete, force-push, reset --hard, stash drop), call TaskList and scan in-flight Bash bg tasks.
- If any bg task description matches "verify / reference check / safety scan / impact / dependency", wait for it. Read its output file before proceeding.
- The user saying "if stale, delete" is NOT a blanket approval — it's conditioned on your verdict, and your verdict depends on complete evidence.
- Related cousin: [[feedback_subagent_write_phantom]] (subagent claims success while output didn't land — verify before trusting) and [[feedback_attestation_enables_contradiction_detection]] (cross-check before claiming).
- The defensive default when uncertain: kick the destructive op to the next turn after all in-flight verification returns.
