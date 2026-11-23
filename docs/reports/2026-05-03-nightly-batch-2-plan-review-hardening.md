# Nightly batch 2/5 — plan-review hardening report

> Worktree: `/mnt/local-analysis/worktrees/nightly-batch-2-20260503T054930Z`  
> Scope: planning/review only; no plan approvals and no implementation.

## Live status-review inventory

Open issues labeled `status:plan-review` at the start of the audited pass: 24 total.

Highest-leverage stale/blocked review-artifact cluster selected for this pass:

| Issue | URL | Reason selected | Result this pass |
|---|---|---|---|
| #2601 | https://github.com/vamseeachanta/workspace-hub/issues/2601 | High-priority marine-engineering audit plan had stale live-count/directory evidence and incomplete post-patch provider review chain. | Hardened to approval-candidate evidence: Claude r4 APPROVE + Codex r4 APPROVE; Gemini unavailable. |
| #2600 | https://github.com/vamseeachanta/workspace-hub/issues/2600 | BSI standards plan has only earlier internal review evidence; needs fresh post-revision external review. | Not patched in this pass; remains blocked pending rerun. |
| #2599 | https://github.com/vamseeachanta/workspace-hub/issues/2599 | NACE/AMPP standards plan has only earlier internal review evidence; needs fresh post-revision external review. | Not patched in this pass; remains blocked pending rerun. |
| #2597 | https://github.com/vamseeachanta/workspace-hub/issues/2597 | Riser topical expansion plan has only earlier internal review evidence; needs fresh post-revision external review. | Not patched in this pass; remains blocked pending rerun. |
| #2596 | https://github.com/vamseeachanta/workspace-hub/issues/2596 | #2471 erratum plan has only earlier internal review evidence; needs fresh post-revision external review. | Not patched in this pass; remains blocked pending rerun. |

## #2601 changes made

Plan patched: `docs/plans/2026-05-03-issue-2601-llm-wiki-W4C-marine-engineering-audit.md`

Concrete findings fixed:

1. Replaced stale marine wiki counts/directory assertions with live worktree evidence:
   - wiki total: 19,193 markdown files
   - concepts: 13
   - entities: 13
   - sources: 19,164
   - `comparisons/`, `visualizations/`, and `standards/`: missing directories, represented as explicit missing/count-0 rows
   - raw files: 5 PDFs under `raw/papers/` plus root `.gitkeep`; missing `raw/articles/`, `raw/assets/`, and `raw/standards/`
2. Removed phantom concept/entity filenames from enumerations.
3. De-duplicated missing-directory clauses in pseudocode/TDD rows.
4. Replaced invalid `grep ... registry.py 2>/dev/null -> 0` proof with an existence-gated citation-registry availability check; missing registry now means `unavailable`, not zero citations.
5. Fixed stale review-artifact paths (`plan-W4C-*`) to actual `plan-2601-*` artifacts.
6. Added `follow_up_issue_placeholder` to the priority-entry schema/test contract so the acceptance criterion is enforceable.
7. Updated the plan's adversarial review summary through Claude r4 and Codex r4 without changing live issue labels or approval state.

## Review artifacts created

| Artifact | Verdict / purpose |
|---|---|
| `scripts/review/results/2026-05-03-nightly-batch-2-rereview-prompt-2601.md` | Rerun prompt artifact for #2601. |
| `scripts/review/results/2026-05-03-plan-2601-claude-r2.md` | Claude rerun; MINOR -> revised. |
| `scripts/review/results/2026-05-03-plan-2601-claude-r3.md` | Claude rerun; MINOR -> revised. |
| `scripts/review/results/2026-05-03-plan-2601-claude-r4.md` | Claude rerun; APPROVE. |
| `scripts/review/results/2026-05-03-plan-2601-codex-r1.md` | Codex rerun; MAJOR -> revised. |
| `scripts/review/results/2026-05-03-plan-2601-codex-r2.md` | Codex rerun; MAJOR -> revised. |
| `scripts/review/results/2026-05-03-plan-2601-codex-r3.md` | Codex rerun; MINOR -> revised. |
| `scripts/review/results/2026-05-03-plan-2601-codex-r4.md` | Codex rerun; APPROVE. |

All new review outputs validated with `scripts/review/validate-review-output.sh`.

## Approval-readiness classification

| Issue | Candidate? | Evidence |
|---|---:|---|
| #2601 | Yes, with Gemini unavailable caveat | Plan patched; Claude r4 APPROVE; Codex r4 APPROVE; no user approval marker added. |
| #2600 | No | Needs fresh post-revision review artifacts. |
| #2599 | No | Needs fresh post-revision review artifacts. |
| #2597 | No | Needs fresh post-revision review artifacts. |
| #2596 | No | Needs fresh post-revision review artifacts. |

## User decision needed

- User may approve #2601 if satisfied with Claude+Codex approval evidence and explicit Gemini-unavailable caveat.
- Do not implement #2601 until the user applies `status:plan-approved` and creates `.planning/plan-approved/2601.md`.
- Next hardening wave should rerun post-revision reviews for #2600, #2599, #2597, and #2596 before surfacing them as approval candidates.
