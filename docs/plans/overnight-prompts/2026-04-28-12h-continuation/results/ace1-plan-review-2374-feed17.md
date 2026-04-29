# Feed17 Result — Adversarial Review for #2374 Plan

> **Classification:** COMPLETED_WITH_RESULT
> **Machine:** ace-linux-1
> **Provider:** Claude Opus 4.6 (Feed17 — bounded adversarial review)
> **Date:** 2026-04-29
> **Feed chain:** feed13 (draft #2375) → feed14 (review #2375) → feed15 (patch #2375) → feed16 (patch #2374) → **feed17 (review #2374)**

---

## Outcome

Cold-context adversarial review of `docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md` completed. **Verdict: MINOR.** Three MINOR findings and four LOW findings identified. No MAJOR or blocking defects. Feed16's stale-path patch verified clean.

---

## Verdict Summary

| Severity | Count | Details |
|----------|-------|---------|
| MAJOR | 0 | — |
| MINOR | 3 | F1 (DURABLE_CATEGORIES divergence), F2 (wrong script paths), F3 (route_domain divergence) |
| LOW | 4 | F4 (stale self-reference slug), F5 (stale file counts), F6 (review artifact date prefix), F7 (artifact map redundancy) |

**Overall: MINOR** — plan is structurally sound and correctly scoped. MINOR findings should be patched before `status:plan-approved` but none block planning advancement.

---

## Key Findings

### F1 (MINOR): DURABLE_CATEGORIES diverges from #2375 sibling

The plan claims merge compatibility with #2375 ("shared scoring rubric"). Both use 0..3 binary-increment scoring, but the DURABLE_CATEGORIES sets are almost disjoint:

- **#2374:** `{engineering, ai-orchestration, ci, data-pipeline, automation, knowledge-management, documentation}` (7 members)
- **#2375:** `{engineering, data, harness, standards}` (4 members)
- **Overlap:** only `engineering`

This means the `durable-category` scoring dimension produces different results for the same category across siblings. The plan's claim that merge is "mechanical" (line 35) is an overclaim — it's structurally mechanical but semantically divergent.

**Remediation:** Align sets, or add explicit caveat that scores are not directly comparable without re-scoring against a unified DURABLE_CATEGORIES.

### F2 (MINOR): Resource-intelligence cites wrong script paths

Three operations scripts are cited at `scripts/operations/` but actually live at `scripts/cron/`:
- `comprehensive-learning-nightly.sh`
- `harvest-workflow-tips.sh`
- `queue-refresh-weekly.sh`

Verified: all three exist at `scripts/cron/`, not `scripts/operations/`.

**Remediation:** Update path prefix from `scripts/operations/` to `scripts/cron/`.

### F3 (MINOR): route_domain process-category set diverges from #2375

- **#2374:** routes `(ai-orchestration, ci, automation, data-pipeline)` → `process`
- **#2375:** routes `(ai-orchestration, ci, automation)` → `process` (no `data-pipeline`)

A `data-pipeline`-category candidate routes to `process` in #2374 but `general` in #2375.

**Remediation:** Align or document the intentional divergence in the merge contract.

### F4–F7 (LOW): Cosmetic / stale evidence

- **F4:** Self-reference slug parenthetical references a `2026-04-26` path that was never used; the plan is already at its final `2026-04-27` path.
- **F5:** File counts stale by 2 days: handoffs 82→88 (+6), review results 1,111→1,195 (+84), reports 150→154 (+4). Not load-bearing.
- **F6:** Review artifact paths in artifact map use `2026-04-26` date prefix; convention uses review date (should be `2026-04-29`).
- **F7:** Artifact map "This plan" row has redundant "(final-slug = ...)" parenthetical with a different date.

---

## Cross-Plan Compatibility Assessment

### What's actually shared between #2374 and #2375 candidate schemas

| Shared fields (5) | #2374-only fields (~7) | #2375-only fields (~3) |
|---|---|---|
| wiki_target_domain, extend_or_create, score, reasons, status | source_kind, source_sha, issue_ref, finding_summary, section, additional_refs, severity | source_wrk, title, patterns (on candidate) |

The two candidate records share 5 of ~15 total unique fields. "Mechanical merge" requires a union schema with many nullable fields. Accurate, but the plan should downgrade from "mechanical" to "structurally compatible with union-schema reconciliation."

### Scoring-architecture comparison (all three siblings)

| Dimension | #2374 | #2375 | #2370 |
|-----------|-------|-------|-------|
| Scale | 0..3 binary | 0..3 binary | 4-dim × 0-5 weighted |
| DURABLE_CATEGORIES | 7 members | 4 members | N/A (uses keyword heuristics) |
| route_domain process set | 4 categories | 3 categories | N/A |
| Score threshold (min to keep) | ≥1 | ≥2 | composite ranking, no min |
| Status vocabulary | {candidate,reviewed,promoted,rejected} | {candidate,reviewed,promoted,rejected} | {already_ingested: bool} |

**Score threshold divergence** (#2374 keeps ≥1, #2375 keeps ≥2) means #2374 is more permissive — this is appropriate given its noisier source material (freeform Markdown vs. structured JSONL) but should be documented in the merge contract.

---

## Feed16 Patch Verification

All 4 remaining `knowledge-base/wiki-candidates.yaml` occurrences are in backward-reference or changelog context:
- Line 19: parenthetical "(prior draft used...)"
- Line 35: parenthetical "(prior draft used...)"
- Line 428: feed16 changelog text
- Line 443: feed16 coordination note

**Zero active forward-references to the superseded path remain.** Feed16 patch verified clean.

---

## Resource-Intelligence Citation Verification

| Category | Verified | Failing |
|----------|----------|---------|
| scripts/knowledge/*.py / *.sh | 7/7 ✅ | — |
| scripts/operations/*.sh (cited) | 0/3 ❌ | F2: actual path is scripts/cron/ |
| knowledge-base/ files | 3/3 ✅ | — |
| docs/plans/ sibling | 1/1 ✅ | — |
| docs/handoffs/ dir | ✅ (exists, count stale) | F5 |
| scripts/review/results/ dir | ✅ (exists, count stale) | F5 |
| docs/reports/ dir | ✅ (exists, count stale) | F5 |

---

## Files Written

| File | Content |
|------|---------|
| `scripts/review/results/2026-04-29-plan-2374-claude-feed17.md` | Full adversarial review with findings table |
| `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-review-2374-feed17.md` | This lane result |

---

## Next Safe Action

1. **Patch the 3 MINOR findings** (F1, F2, F3) in a feed18 patch lane or interactive session.
2. **Dispatch Codex/Gemini review** once feed17 MINORs are patched:
   ```bash
   bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md
   ```
3. **Wait for user approval** — do not implement until `status:plan-approved` is applied by the operator.

---

## Boundary Compliance Statement

- ✅ Did NOT implement code
- ✅ Did NOT edit the plan under review
- ✅ Did NOT create approval markers
- ✅ Did NOT add or remove GitHub labels
- ✅ Did NOT post issue comments, create PRs, merge, close, push, force-push, hard reset, or mutate GitHub
- ✅ Did NOT launch additional agents (external CLI fanout blocked by unattended permissions — noted transparently)
- ✅ Wrote exactly two files: the review artifact and this lane result
- ✅ All reads were read-only; no repo state mutation
- ✅ Plan status remains `draft` — not marked approved
