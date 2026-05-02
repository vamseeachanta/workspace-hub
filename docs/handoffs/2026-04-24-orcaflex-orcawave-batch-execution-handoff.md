# Execution Handoff — OrcaFlex/OrcaWave 2026-04-24 Batch

> **Purpose:** Hand off 10 user-approved plans to the next Claude Code session for implementation.
> **Source batch:** `docs/reports/2026-04-24-overnight-orcaflex-orcawave-planning-batch.md`
> **Repo (target):** `vamseeachanta/digitalmodel` (issues) + `vamseeachanta/workspace-hub` (plans/reviews)

---

## Handoff Prompt (copy-paste into a fresh session)

```
You are the execution-phase operator for the 2026-04-24 OrcaFlex/OrcaWave planning batch.
10 issues in vamseeachanta/digitalmodel are user-approved at status:plan-approved.
Your job is to implement them, one at a time or in safe parallel waves, per the approved plans.

Context to read FIRST (in order):
1. docs/reports/2026-04-24-overnight-orcaflex-orcawave-planning-batch.md — full batch context
2. docs/plans/2026-04-24-orcaflex-orcawave-overnight-batch-design.md — design principles
3. For each issue you work: its plan + r2-adversarial review (if present) + r1-adversarial review

Approved issues (all at status:plan-approved):
- #510 — Fix 20 OrcaFlex test failures (T1; simplest — cleanest starting point)
- #515 — OrcaFlex YAML semantic-equivalence (T2; PARENT of deferred #517/#518/#519 cluster)
- #511 — OrcaFlex campaign spec generation (T2; extend existing CampaignMatrix, NOT greenfield)
- #501 — OrcaWave QTF/fieldpoints/irreg-freq (T2, r2-MINOR; irreg-freq enum first, then QTF, then field points)
- #500 — OrcaWave mesh preflight + auto-copy (T2, 2nd-pass-MAJOR; extend existing _copy_mesh_files)
- #504 — OrcaFlex buoys builder refactor (T2; use BuoysOrchestrator approach B, not distinct-slots A)
- #279 — OrcaFlex reporting standardization (T2-large, r2-MINOR; extend existing 2823-LOC reporting)
- #282 — OrcaWave reporting standardization (T3; Strategy pattern with WRK-115 stub adapter default)
- #503 — OrcaFlex/OrcaWave help ingestion (T3; user decided on licensing — consult r1 adversarial for tradeoffs)
- #486 — Subsea connectors/jumpers (T3; user decided Path A vs B — consult plan for condition-ality)

DEFERRED TRADEOFFS needing user confirmation at each issue's kickoff:
- #279: $EXAMPLES_DIR binding — docs/modules/orcaflex/reporting/examples/ vs docs/domains/… — ask user before writing fixtures.
- #486: Confirm which path the user's plan-approved marker implied (Path A procure 17R vs Path B pivot to 17B/17J/F101/B31.8).
- #503: Confirm the licensing/ToS decision the user made. The r1 adversarial review lists all 6 tradeoffs; user's approval implies resolved but the plan should be consulted.

RECOMMENDED EXECUTION ORDER (safe-first):
Wave A (independent, low-risk, quick feedback):
  #510 (T1 test-drift) — start here; validates the execution workflow
  #511 (T2 extend CampaignMatrix)
  #504 (T2 buoys refactor; isolated file)

Wave B (feature adds with low cross-coupling):
  #515 (T2 semantic-equivalence parent — UNBLOCKS #517/#518/#519 for a follow-up batch)
  #500 (T2 mesh preflight — disjoint from #501)
  #501 (T2 QTF config — disjoint from #500)

Wave C (larger, may benefit from earlier waves' learnings):
  #282 (T3 OrcaWave reporting; depends on WRK-115 stub if not completed)
  #279 (T2-large OrcaFlex reporting; extends existing 2823-LOC infra)
  #486 (T3 subsea connectors; gated by user standard-path decision)
  #503 (T3 help ingestion; licensing-gate resolved)

Wave C MAY NOT be strict serialization — #279 and #282 share no files and can run in parallel after Wave A+B are verified.

PROTOCOLS:
1. TDD MANDATORY for each issue: write failing tests first, then implementation.
   Follow digitalmodel/tests/ conventions and uv run pytest for validation.
2. Read r2-adversarial AND r1-adversarial reviews for #279 and #501 before implementing —
   they document r2-introduced one-line-fix defects that should be addressed during implementation
   (don't re-introduce them).
3. For each issue: commit atomically with message referencing issue number and status
   transition (status:plan-approved → status:done once tests pass).
4. NEVER self-label status:done without passing tests — that's the user-gated verification step.
   Per feedback_never_offer_to_self_label_plan_approved, completion claims need evidence.
5. If implementation reveals the plan is wrong (new defect found during coding), STOP —
   create a status:plan-review transition to surface for user re-approval. Don't silently re-plan.
6. Push each completed issue's branch to origin (workspace-hub) before transitioning status.

GITHUB-SURFACE RULES:
- Comments on digitalmodel issues: post implementation-kickoff comment + completion comment.
- Labels: status:plan-approved → status:working → (tests pass) → status:done.
  Only promote to status:done after uv run pytest passes for the issue's test surface AND user sign-off.
- If Hermes orchestrator is auto-promoting labels, leave a "human-verified" marker in the comment
  to distinguish intentional approval from automation drift.

KNOWN ENVIRONMENTAL HAZARDS (observed during planning batch):
- Multi-session git-lock contention is frequent on this workstation. Use `set -o pipefail` on commits.
- `scripts/review/plan-review-fanout.sh` has Codex (`--no-interactive` flag stale) and Gemini
  (trust-workspace not set) issues — fanout will not produce Codex/Gemini verdicts until fixed.
  This is a repo-maintenance task separate from this batch.
- There's a stash at `foreign-changes-during-orca-push-*` and a feature branch
  `plan/issue-2103-aqwa-bemrosetta-ingestion` with duplicate batch commits — these belong to
  another session; do not disturb.
- Cross-session plans exist for #2103/#2124/#2125/#2227 from a parallel session. Do not touch
  those issues.

YOUR FIRST ACTION:
Confirm you've read the batch report. State which issue you're starting with (recommended: #510).
Then commence TDD implementation per the plan. Post a kickoff comment on the issue with
status:plan-approved → status:working label transition.
```

---

## Notes for the handoff operator (metadata — do NOT paste into prompt)

**Batch provenance:**
- Commits in sequence on `vamseeachanta/workspace-hub` origin/main:
  1. `ab7b96867` — design spec
  2. `2eb216b4b` — 10 plans + 10 adversarial reviews + design amendment
  3. `3a73d3018` — morning report
  4. `7f54958a3` — 3-provider fanout outputs
  5. `edf41ff48` — fanout outcome appended to morning report
  6. `ff6ae54ff` — r2 plans + r2 reviews for #279 and #501

**Total artifacts:** 10 approved plans + 10 r1-adversarial reviews + 2 r2-adversarial reviews + 30 fanout outputs (6 real Claude 2nd-pass, 24 failure stubs) + morning report + batch design spec + approval/handoff comments on all 10 issues.

**Cross-batch dependencies worth knowing:**
- `#515 → {#517, #518, #519}`: semantic-equivalence children deferred pending #515's approach being in-code.
- `#503 ↔ {#2124, #2125}`: parallel-session plans on thematically-adjacent Orcina ingestion; reconcile before execution to avoid third-parallel-implementation.

**If the operator hits a sustained-MAJOR loop (repeated r3 with no progress):**
Per `feedback_codex_sustained_major_loop`, surface as consensus-vs-minority decision to user instead of auto-cycling. This batch did not trigger that on any issue.
