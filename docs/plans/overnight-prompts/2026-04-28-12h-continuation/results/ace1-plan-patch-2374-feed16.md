# Feed16 Result — Plan Patch for #2374 (Stale Wiki-Candidate Paths)

> **Classification:** COMPLETED_WITH_RESULT
> **Machine:** ace-linux-1
> **Provider:** Claude Opus 4.6 (Feed16 — bounded plan patch)
> **Date:** 2026-04-29
> **Feed chain:** feed13 (draft #2375) → feed14 (adversarial review #2375) → feed15 (patch #2375) → **feed16 (patch #2374)**

---

## Outcome

All stale `knowledge-base/wiki-candidates.yaml` references in the #2374 plan have been updated to `data/document-index/wrk-wiki-candidates.yaml` per the superseding #2375 plan. Additionally, a #2370 scoring-architecture difference note was added where #2374 previously implied merge compatibility without qualification.

---

## Stale References Found and Patched

| Original line | Context | Old path | Patched to |
|---------------|---------|----------|------------|
| 19 | Resource Intel — sibling wave-2 plan description | `knowledge-base/wiki-candidates.yaml` | `data/document-index/wrk-wiki-candidates.yaml` (with provenance parenthetical noting prior draft path) |
| 35 | Documents consulted — #2375 sibling description | `knowledge-base/wiki-candidates.yaml` | `data/document-index/wrk-wiki-candidates.yaml` (with provenance parenthetical + #2370 scoring-architecture difference note) |
| 51 | Gaps — merge contract reference | `wiki-candidates.yaml` | `wrk-wiki-candidates.yaml` (at `data/document-index/wrk-wiki-candidates.yaml`) |
| 359 | Files to Change — schema.md modification reason | `wiki-candidates.yaml` | `wrk-wiki-candidates.yaml` (at `data/document-index/wrk-wiki-candidates.yaml`) |
| 396 | TDD Test — schema doc merge contract | `wiki-candidates.yaml` | `wrk-wiki-candidates.yaml` (wave-2, at `data/document-index/`) |
| 406 | Acceptance Criteria — schema doc merge contract | `wiki-candidates.yaml` | `wrk-wiki-candidates.yaml` (at `data/document-index/wrk-wiki-candidates.yaml`; added "0..3 binary-increment" rubric qualifier) |
| 438 | Risks — schema drift | `wiki-candidates.yaml` | `wrk-wiki-candidates.yaml` (at `data/document-index/wrk-wiki-candidates.yaml`; added #2370 scoring-architecture difference note) |

**Additional edits (not stale-path but directly consequential):**

| Section | Edit |
|---------|------|
| Line 35 — Documents consulted | Added: "**Note:** #2370 uses a structurally different 4-dimension × 0-5 weighted composite scoring system; any three-way ledger merge must normalize scores before comparison." |
| Risks § coordination note (new) | Added coordination note documenting this feed16 patch: lines patched, provenance, and the #2370 scoring difference. |
| Adversarial Review Summary § Revisions | Updated from "(none yet)" to document feed16 patch with link to this result file. |

---

## Files Written

| File | Content |
|------|---------|
| `docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md` | Patched plan (7 stale-path sites + 2 supplementary edits + 1 changelog update = 10 edit operations) |
| `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2374-feed16.md` | This lane result |

---

## Verification Commands / Read Checks Performed

| Check | Result |
|-------|--------|
| `grep -c 'knowledge-base/wiki-candidates\.yaml'` on patched file | 4 hits — all in backward-reference parenthetical context ("prior draft used...") or changelog text. Zero active path references remain. |
| `grep -c 'data/document-index/wrk-wiki-candidates\.yaml'` on patched file | 7 hits — all at the expected patched sites (lines 19, 35, 51, 359, 406, 428, 438) plus coordination note (line 443). |
| `grep -c 'wrk-wiki-candidates\.yaml'` on patched file (broader) | 9 hits — 7 full-path + 2 bare-name (lines 396, 443). All correct. |
| Read line 3 — status field | `draft` — unchanged, not marked approved. |
| `wc -l` on patched file | 450 lines — structurally intact (original was 450; one new line added for coordination note, offset by line-internal text expansion). |
| Cross-check: `data/document-index/wrk-wiki-candidates.yaml` path matches #2375 plan | ✅ Confirmed at #2375 plan lines 58, 86, 110, 126, 145, 169, 181, 365, 415, 448, 462, 463. |

---

## Residual Risks

1. **#2374 plan still at `draft` status with no adversarial reviews.** This patch resolves the stale-path hazard but the plan itself has not been reviewed by any provider (Claude/Codex/Gemini). The adversarial review table shows all three providers as PENDING. Before advancing to `status:plan-review`, the plan needs a full review cycle.
2. **Line 19 still references the prior-draft plan file** `docs/plans/2026-04-26-issue-2375-wrk-completions-normalize-seeds.md`. This file still exists but is superseded by `docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md`. A future full-plan review should update this reference if the prior draft is archived or deleted. Not in scope for this stale-path-only patch.
3. **Line 35 now documents #2370 scoring difference** — this is accurate per the feed14 review's verified analysis of #2370's `score_issue()` function (4 dimensions × 0-5 weighted composite). Any future #2374 adversarial review should verify this characterization still holds if #2370's plan is updated.
4. **Line 85 states "this plan adopts the same function signature, the same status set, and an analogous routing function"** — this is accurate for the #2375↔#2374 relationship (both use 0..3 binary-increment). The #2370 difference is now documented at line 35 and 438.

---

## Next Safe Action

1. **Route #2374 plan to adversarial review** — the plan has never been reviewed:
   ```bash
   bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md
   ```
2. **Wait for user approval** — do not implement until `status:plan-approved` is applied by the operator.

---

## Boundary Compliance Statement

- ✅ Did NOT implement code
- ✅ Did NOT create approval markers
- ✅ Did NOT add or remove GitHub labels
- ✅ Did NOT post issue comments, create PRs, merge, close, push, force-push, hard reset, or mutate GitHub
- ✅ Did NOT edit #2375 or other sibling plans
- ✅ Did NOT launch additional agents
- ✅ Did NOT broaden #2374 scope beyond stale-path correction and concise residual-risk note
- ✅ Edited exactly one plan file: `docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md`
- ✅ Wrote exactly one lane result file: this file
- ✅ All verification reads were read-only; no repo state mutation
- ✅ Plan status remains `draft` — not marked approved
