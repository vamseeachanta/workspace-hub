# Next-session prompt — workspace-hub self-improvement epic #3248

Paste this to start the next session.

---

Continue the self-improvement epic #3248 on workspace-hub.

**Preflight:**
```
cd $WORKSPACE_HUB && git checkout main && git pull --ff-only
gh issue view 3248 --comments | tail -40
```
Read `docs/session-handoffs/2026-06-27-self-improvement-epic-3248-and-matrix-line-items.md` first.

**Where it stands:** 4 matrix line items + a drift detector shipped (session_curation, skill_currency,
memory_freshness, skill_link_health; the matrix has 8 groups). 4 children are **deferred, no plans yet**:
- #3252 auto-graduate high-confidence correction candidates → skills
- #3253 Hermes pattern auto-promotion → canonical skills
- #3254 recurring drift patterns → skill-update candidates
- #3256 adaptive correction-confidence threshold + Gemini-specific skill detection

**Do next — use parallel agents + dynamic workflows (the proven pattern this epic used):**
1. Draft **and** adversarially review (2 rounds each) implementation plans for the 4 deferred children
   **in parallel**; commit each plan to `docs/plans/`, post to its issue, set `status:plan-review`.
   **Stop there — do NOT implement until I approve each.**
2. On my approval: implement TDD-first, both adversarial gates, **one reviewed PR per child**.

**Hard rules (cost us bugs this epic — don't relearn):**
- Never self-apply `status:plan-approved` or `status:completeness-verified` — those are my gates.
- Wire every new audit into **both** `curate-session-memory.sh` AND `.ps1`; reuse `machine_label()` and
  the audit→state-JSON→collect-equality→verdict substrate; don't rebuild it.
- A new matrix dimension touches ~11 places; every new OK verdict must be added to
  `reconcile-ecosystem.sh`'s OK-skip list (or healthy cells fire spurious reconcile actions).
- Don't overload script exit codes (non-zero aborts the Windows cron under `$ErrorActionPreference='Stop'`).
- The state-ref `git push` hangs (operator issue) — bound any cross-machine publish with a timeout.

Reconcile any box to equivalence anytime: `bash scripts/curation/curate-session-memory.sh` (in the matrix HTML).
