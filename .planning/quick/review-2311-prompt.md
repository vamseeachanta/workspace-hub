# Adversarial Plan Review Request: Issue #2311

You are an independent adversarial reviewer. Be skeptical and concrete. Do NOT rubber-stamp.

Review this local draft implementation plan for correctness, completeness, feasibility, TDD adequacy, scope discipline, risk handling, future-issue separation, and verification readiness.

Required output schema:
- Verdict: APPROVE | MINOR | MAJOR
- Strengths
- Gaps
- Risks
- Missing tests
- Scope creep concerns
- Weakest assumption and what breaks if it is false
- Most likely implementation failure mode
- Most likely test gap
- Future issues suggested
- Review confidence

Important review questions:
1. Does the plan use adequate repo evidence and correctly separate current live surfaces from intentional historical/legacy artifacts?
2. Are the proposed file changes and tests sufficient and correctly scoped?
3. Are there missing current files/tests/docs that should be in scope?
4. Is the acceptance criteria measurable and enough to block false success?
5. Is any part of the plan too broad, too vague, or mis-bounded?

Artifact under review:
Path: docs/plans/2026-04-17-issue-2311-stage-transition-stale-reference-cleanup.md

Plan text follows:

# Plan for #2311: Stage-transition stale reference cleanup

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2311
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2311-claude.md | scripts/review/results/2026-04-17-plan-2311-codex.md | scripts/review/results/2026-04-17-plan-2311-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `tests/helpers/stale_reference_docs.py` — already bans deleted stage-transition script references via the `deleted work-queue gate scripts` regex (`start_stage.py`, `exit_stage.py`, `verify_checklist.py`, plus adjacent removed files).
- Found: `tests/docs/test_banned_stale_references.py` — enforces strict stale-reference blocking for a curated set of live docs/templates, but it does not yet prove that the stage-transition cluster is confined to intentional legacy/report surfaces only.
- Found: `tests/docs/test_legacy_reference_allowlist.py` — keeps stale references confined to two intentional legacy docs (`docs/ops/legacy-claude-reference-map.md` and `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md`) for the currently scanned set.
- Gap: there is no targeted regression test proving that removed stage-transition script names stay out of current instructional surfaces while still allowing historical audit/legacy-report artifacts to exist.

### Standards
| Standard | Status | Source |
|---|---|---|
| Not applicable | n/a | Documentation / harness issue; no engineering standard governs the cleanup | 

### LLM Wiki pages consulted
- No relevant wiki pages — issue scope is repo workflow governance, not domain knowledge.

### Documents consulted
- Issue #2311 — defines the target stale-read cluster (318 mapped Claude reads) and the canonical redirect targets.
- `docs/reports/provider-session-ecosystem-audit.md` — latest audit confirms the top stale cluster is `scripts/work-queue/start_stage.py` (138), `scripts/work-queue/exit_stage.py` (137), and `scripts/work-queue/verify_checklist.py` (43), with current redirect guidance already documented.
- `docs/ops/legacy-claude-reference-map.md` — canonical legacy redirect surface explicitly mapping the removed stage-transition scripts to `docs/governance/SESSION-GOVERNANCE.md`, `docs/governance/TRUST-ARCHITECTURE.md`, `scripts/workflow/governance-checkpoints.yaml`, `.claude/hooks/plan-approval-gate.sh`, `.claude/hooks/session-governor-check.sh`, and `scripts/review/cross-review.sh`.
- `docs/work-queue-workflow.md` — current GitHub issue -> `.planning/` workflow already exists and marks local work-queue surfaces as legacy compatibility only.
- Issue #2213 — existing follow-up for expanding strict stale-reference enforcement across more current docs.
- Issue #2214 — existing follow-up for separating current architecture guidance from legacy redirect content.

### Gaps identified
- No issue-specific plan yet describing how to distinguish intentional historical/report mentions of the stage-transition scripts from forbidden live instructional mentions.
- No targeted test currently checks confinement for the stage-transition script-name cluster specifically; current tests are broader and intentionally skip many generated/report surfaces.
- The repo still needs an explicit bounded rule for where these script names may remain (legacy maps and historical reports) versus where they must never reappear (live docs/templates/instructions).

<!-- Verification: count distinct sources above (across all sub-sections).
     Minimum 3 required (issue body + 2 others). Current count: 6 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2311-stage-transition-stale-reference-cleanup.md` |
| Targeted confinement test | `tests/docs/test_stage_transition_reference_confinement.py` |
| Shared stale-reference helper updates (if needed) | `tests/helpers/stale_reference_docs.py` |
| Strict curated docs test updates (if needed) | `tests/docs/test_banned_stale_references.py` |
| Legacy/reference doc clarification (if needed) | `docs/ops/legacy-claude-reference-map.md` |
| Review artifact — Claude | `scripts/review/results/2026-04-17-plan-2311-claude.md` |
| Review artifact — Codex | `scripts/review/results/2026-04-17-plan-2311-codex.md` |
| Review artifact — Gemini | `scripts/review/results/2026-04-17-plan-2311-gemini.md` |

---

## Deliverable

A bounded stale-reference confinement rule and regression-test suite that ensures removed stage-transition scripts only appear in intentional historical/legacy surfaces and not in current instructional workflow surfaces.

---

## Pseudocode

```text
collect stage-transition stale-reference patterns
scan current instructional surfaces and classify each hit as live, legacy, or generated-history
if any live instructional hit exists:
    patch the file to remove the deleted script reference
    replace it with current governance/hook/review targets
create a targeted regression test:
    allow hits only in explicit legacy/reference or historical-report buckets
    fail if current docs/templates/instructions mention the deleted scripts
run targeted docs tests
refresh provider-session audit after cleanup to measure whether the cluster remains only as historical evidence
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/docs/test_stage_transition_reference_confinement.py` | encode a targeted rule for where removed stage-transition script names may and may not appear |
| Modify | `tests/helpers/stale_reference_docs.py` | expose reusable pattern/helper logic for the stage-transition subset if needed by the new confinement test |
| Modify | `tests/docs/test_banned_stale_references.py` | optionally expand strict coverage if newly cleaned current docs become eligible |
| Modify | `docs/ops/legacy-claude-reference-map.md` | clarify intentional legacy-only status if the plan review finds ambiguous wording |
| Update | `docs/plans/README.md` | add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_stage_transition_refs_confined_to_legacy_or_history_surfaces` | deleted stage-transition scripts only appear in intentional legacy/report files | repo text scan for `start_stage.py`, `exit_stage.py`, `verify_checklist.py` | only allowlisted paths remain |
| `test_curated_current_docs_do_not_reference_stage_transition_scripts` | current docs/templates/instructions stay clean even if historical reports contain the names | curated current-file list | zero matches |
| `test_legacy_reference_map_points_to_current_redirect_targets` | the intentional legacy map keeps the replacement targets discoverable | `docs/ops/legacy-claude-reference-map.md` | all required redirect anchors present |
| `test_provider_audit_report_still_lists_cluster_without_becoming_instructional_surface` | the generated audit can remain historical evidence without being mistaken for a current workflow doc | `docs/reports/provider-session-ecosystem-audit.md` classification helper | classified as allowed report/history surface |

---

## Acceptance Criteria

- [ ] Removed stage-transition script references are classified into explicit buckets: forbidden live instructional surfaces vs allowed historical/legacy surfaces
- [ ] Any live instructional surface discovered during implementation is rewritten to current governance/hook/review targets
- [ ] A targeted regression test fails if `scripts/work-queue/start_stage.py`, `scripts/work-queue/exit_stage.py`, or `scripts/work-queue/verify_checklist.py` reappear in protected current docs/templates/instructions
- [ ] `docs/ops/legacy-claude-reference-map.md` remains the discoverable redirect surface for intentional legacy references
- [ ] Targeted docs test suite passes via `uv run pytest tests/docs/test_stage_transition_reference_confinement.py tests/docs/test_banned_stale_references.py tests/docs/test_legacy_reference_allowlist.py -q`
- [ ] Post-implementation audit refresh is run and linked from the issue

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Not yet reviewed |
| Codex | PENDING | Not yet reviewed |
| Gemini | PENDING | Not yet reviewed |

**Overall result:** PENDING

Revisions made based on review:
- None yet

---

## Risks and Open Questions

- **Risk:** Most remaining references may be intentional historical evidence rather than live workflow guidance, so the plan must avoid deleting useful audit/report artifacts blindly.
- **Risk:** If current tests treat generated historical reports the same as live docs, the new confinement rule could become too noisy or too permissive.
- **Open:** Should historical audit/report files be explicitly enumerated in the new confinement test, or should they be recognized by directory/type classification to reduce maintenance churn?
- **Open:** If no live instructional hits remain after deeper scan, should this issue resolve as “guardrails only” while leaving actual legacy report content untouched?

---

## Complexity: T2

**T2** — bounded multi-file governance/documentation/test hardening work: it requires repo scanning, explicit scope separation between live and historical surfaces, and new regression coverage, but no architecture-scale code redesign.

