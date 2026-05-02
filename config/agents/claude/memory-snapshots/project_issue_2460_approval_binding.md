---
name: Issue #2460 — approval bindings must be immutable, not file-path references
description: Approval markers that point to plan file paths without SHA/hash binding silently drift when plans are rewritten; approval state must name the exact revision and the authoritative storage surface
type: project
originSessionId: 09693115-06e6-4965-9924-25d9487dae36
---

Approval markers that record plan approval must be **revision-bound** to an immutable artifact set, not a mutable file-path reference. Specifically, a valid approval record must name all four of:

1. **Exact plan file path + exact plan git commit SHA or SHA256 hash** (mutable file paths alone allow silent drift when plans are rewritten)
2. **Exact approved review-artifact paths + per-provider verdicts** (not just "reviews passed")
3. **Exact approval-storage surface** (which file/label/row holds the approval bit)
4. **Revision cleanup protocol** — if the plan is later revised, the binding must be either removed or re-bound to the new revision; a stale-approved state must not persist silently.

**Why:** Issue #2460 (CLOSED, 2026-04-23, tier-1 indexing and code-placement contract) went through r1→r16 adversarial-review iterations because the plan's approval-drift remediation was "still too weak" — Codex MAJOR×8 across revisions all surfaced variants of the same root cause: the plan kept citing file paths (`docs/plans/README.md` row, plan markdown file) without immutable binding. A mutable file-path-only reference can drift when review artifacts or plan files are replaced in place, so the stale-approval-reuse hazard stayed open even after each round of "fixes". This matches the existing `feedback_never_offer_to_self_label_plan_approved.md` rationale at the enforcement level.

**How to apply:**
- When drafting or reviewing a plan that touches approval-gate semantics, demand all four bindings before marking anything approvable.
- When asked to mark a plan `status:plan-approved`, the approval record must cite the plan commit SHA at minimum — just the label on the issue is not sufficient.
- Treat approval-binding gaps as APPROVAL-BLOCKING (MAJOR), not MINOR — the user validated this bar across #2460's r1 through r15 review cycle.
- Related follow-ups from the #2460 scope cleanup: #2467 (flake8 pathological blocker), #2468 (flake8 safe-rule first wave), #2469 (flake8 final green-gate) — these are the worldenergydata CI debt lane, separate from the indexing contract.
