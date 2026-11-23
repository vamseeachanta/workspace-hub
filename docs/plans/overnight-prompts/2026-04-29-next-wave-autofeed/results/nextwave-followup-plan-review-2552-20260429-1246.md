# Plan-only adversarial review — issue [#2552](https://github.com/vamseeachanta/workspace-hub/issues/2552)

> **Lane:** `2026-04-29-next-wave-autofeed` — single-author plan review (no GitHub mutation, no plan edits, no fanout).
> **Reviewer:** Claude Opus 4.7 (1M context), `ace-linux-1` autofeed worker.
> **Stance:** Adversarial per `feedback_adversarial_review_stance.md` — actively hunt for defects, default to non-approval, demand evidence per finding.
> **Plan under review:** `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` @ commit `2734c103b`.
> **Date:** 2026-04-29 12:46 CDT (17:46 UTC).
> **Scope ceiling:** documentation/runbook-only — implementation forbidden in this lane.

---

## Executive verdict

**MINOR_PATCH_NEEDED.**

The plan is internally consistent, scope-appropriate for a T1 documentation issue, and the public/security wording is defensible. No MAJOR defects: scope stays inside `docs/security/` + a one-line cross-reference in `docs/governance/TRUST-ARCHITECTURE.md`, no PII exposure, no implementation surface beyond markdown.

Six MINOR consistency/coverage fixes should land **before** the user moves `status:plan-review` → `status:plan-approved`. None are blockers — all are mechanical edits to the plan file itself, not redesigns. After F1–F6 are patched, the plan is approval-ready under either the T1 deferred-review path or a full cross-review fanout (operator's choice).

The plan's own "Risks and Open Questions" already flags two of the substantive trade-offs (hide-vs-reply default, runbook location). One of those (location) should be **decided up-front** rather than deferred to user approval, because it changes the path in `Files to Change` and the AC test target.

---

## Live issue state (read-only)

`gh issue view 2552 --json number,title,state,labels,updatedAt` at 2026-04-29T17:46Z (live):

| Field | Value |
|---|---|
| Number | 2552 |
| Title | `docs(security): external contributor and unsolicited paid-help response runbook` |
| State | OPEN |
| `updatedAt` | `2026-04-29T13:15:57Z` |
| Labels | `documentation`, `priority:medium`, `cat:documentation`, `domain:security`, **`status:plan-review`** |

Plan SHA on `main`: `2734c103b docs(plans): draft plans for #2550 interaction-limit renewal and #2552 external contributor runbook` (single commit covering this plan and sibling [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550)).

Approval marker existence (`ls .planning/plan-approved/2552.md`): not present — correct, since the issue is at `status:plan-review`, not `status:plan-approved`.

Confirms: plan is currently in the user-approval queue and has not been self-promoted. Aligns with `feedback_never_offer_to_self_label_plan_approved.md`.

---

## Findings table

| ID | Severity | Category | Finding | Evidence (file:line) | Patch (recommendation) |
|---|---|---|---|---|---|
| F1 | MINOR | AC correctness | AC #7 says `uv run pytest workspace-hub/tests/` but **the repo itself IS `workspace-hub`** — that path resolves to `/mnt/local-analysis/workspace-hub/workspace-hub/tests/` which does not exist. The intended invocation is `uv run pytest tests/` (or `uv run pytest tests/security/`) from repo root. | `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md:139` | Replace `workspace-hub/tests/` with `tests/` (or `tests/security/`). |
| F2 | MINOR | Plan completeness | The plan's `Files to Change` table has no `Create` row for `tests/security/test_runbook_external_contributor.py`, yet AC #6 requires that file to exist and pass 4 named tests. The implementation step has no anchor for creating the test file. | `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md:91-96` (table); `:122-125` (TDD list); `:138` (AC) | Add a `Create` row: `tests/security/test_runbook_external_contributor.py — structural lint tests for runbook + cross-reference`. |
| F3 | MINOR | AC ↔ body mismatch | The runbook outline (line 114) requires three templates: `DECLINE_TEMPLATE`, `CONTRIBUTOR_INTEREST_TEMPLATE`, `HIDE_CHECKLIST`. AC #2 only checks for the first two, and `test_runbook_contains_templates` (line 124) only greps for the first two. `HIDE_CHECKLIST` could be silently omitted and still pass. | plan body line 114 vs AC line 134 + TDD test line 124 | Add `HIDE_CHECKLIST` to both AC #2 and the `test_runbook_contains_templates` expected-output column. |
| F4 | MINOR | Cross-issue coherence | The plan cites #2546 and #2401 as triggering examples but does **not** reference sibling issue [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) (`chore(security): codify public repo interaction-limit renewal in scheduled tasks`), which was committed in the **same SHA** (`2734c103b`) and is the durability mechanism for the lockdown the runbook describes. The runbook will tell readers "interaction limits are in place" without telling them where renewal is scheduled. | live `gh issue view 2550` shows `status:plan-review`, plan path `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md`; this plan's "Documents consulted" (lines 31-33) omits #2550 | Add #2550 to "Documents consulted" and to AC #3 ("Runbook references #2546, #2401, **and #2550** as triggering / sibling-enforcement issues"). |
| F5 | MINOR | Runbook accuracy | Scenario 3 ("Legitimate external contributor") tells the operator to "route through fork-and-PR path." But the active `collaborators_only` interaction limit (per `docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md`, expiring 2026-10-29) means non-collaborators cannot comment, open issues, or open PRs — the fork-and-PR path is **closed** until expiry or a temporary lift. The runbook would mislead an operator following Scenario 3 today. | plan line 107 vs lockdown handoff (`docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md`); cross-checked against [#2546](https://github.com/vamseeachanta/workspace-hub/issues/2546) closeout | Add a one-line runbook caveat: "While `collaborators_only` interaction limits are active (currently through 2026-10-29 — see [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550)), Scenario 3 actions require either temporary lift of the limit or invitation as a collaborator first." Reflect this caveat as an AC item. |
| F6 | MINOR | Open question should be resolved before approval | "Open: Should the runbook live under `docs/security/` or `docs/ops/runbooks/`?" — this is not actually open. `docs/security/` already exists and contains one prior security artifact; the issue title says `docs(security):`; the plan's `Files to Change` already commits to `docs/security/`. The "Open" framing creates ambiguity that downstream batch agents could read as latitude to relocate. | plan lines 160-161 | Resolve in the plan: pick `docs/security/external-contributor-runbook.md` and remove the open-question framing. Reasoning: discoverability under existing `docs/security/` taxonomy, alignment with issue title, and one-line policy artifacts are not a runbook backlog warranting `docs/ops/runbooks/`. |
| L1 | LOW | Wording (defensive) | The plan's Section §1.3 cites the external account's GitHub username verbatim. The username is public, not PII, but the **runbook** itself should describe the pattern abstractly ("an external GitHub account, not a current collaborator, offered paid implementation help on a public issue") and reference the **issue number** for traceability rather than name the individual. | plan lines 31, 103 | Add an AC item: "Runbook references #2401 by issue number for the example scenario; does not name the individual external commenter inline." |
| L2 | LOW | TDD over-engineering for T1 | Four grep-level structural tests for a static markdown file is borderline overkill for a T1 documentation artifact whose `test_runbook_file_exists` and `test_runbook_covers_four_scenarios` are essentially tautological at file-creation time. The plan itself notes "trivially passable on file creation." | plan lines 122-127 | Either accept as-is (no harm) OR collapse to two tests: one existence + cross-ref check (`test_trust_architecture_crossref`) and one content-coverage check that combines scenarios + templates. Operator preference. |
| L3 | LOW | Files-to-Change completeness | `docs/plans/README.md` update is listed in Files to Change but has no AC. The index update is a process artifact; consistency with prior plans suggests adding a single AC bullet ("Plan listed in `docs/plans/README.md`"). | plan line 95 vs AC lines 132-139 | Add AC bullet for index update, or omit the index row from Files to Change if it is implicitly handled by another process. |

**Severity legend**

| Severity | Definition |
|---|---|
| MAJOR | Plan cannot be approved without rewrite — structural defect, scope drift, or safety violation |
| MINOR | Plan is structurally sound; small fixes required before approval |
| LOW | Improvement / nice-to-have; not blocking even at MINOR threshold |

---

## Required patches before approval

In order of importance (apply F1–F6; consider L1–L3):

1. **F1** — fix AC #7 pytest path: `workspace-hub/tests/` → `tests/` (one-character class fix).
2. **F2** — add `Create` row for `tests/security/test_runbook_external_contributor.py` in Files to Change.
3. **F3** — add `HIDE_CHECKLIST` to AC #2 and to `test_runbook_contains_templates` expected-output cell.
4. **F4** — add #2550 to "Documents consulted" and to AC #3.
5. **F5** — add one-line caveat in Scenario 3 about active `collaborators_only` limit and reflect as AC item; reference #2550 + lockdown handoff.
6. **F6** — resolve the "Open: docs/security vs docs/ops/runbooks" question to `docs/security/` in the plan.
7. **L1** *(recommended)* — add AC item disallowing inline naming of the external commenter; runbook references #2401 by number only.
8. **L2** *(optional)* — leave TDD list as-is unless the operator wants a leaner T1.
9. **L3** *(optional)* — add AC item for `docs/plans/README.md` index entry, or remove the row.

After F1–F6 are applied, the plan is **APPROVE_FOR_USER_REVIEW** under either:

- **T1 deferred-review path** (faster): operator posts one-line approval comment + writes `.planning/plan-approved/2552.md` marker citing this artifact's path and the F1–F6 patch SHA. Path is supported by `feedback_codex_cli_0_124_upstream_regression.md` (codex-cli 0.124.0 stdin-hang regression makes full fanout fragile until pinned to 0.123.0); `approval-synthesis-10.md` row #2552 explicitly accepts T1 deferred-review for this issue.
- **Full cross-review fanout** (slower, higher confidence): operator runs `scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` from a terminal session (this autofeed lane is permission-gated per `feedback_permission_gate_blocks_cross_review.md` and cannot dispatch fanout). After Codex+Gemini return MINOR-or-better, operator approves.

This review is **not** a substitute for cross-AI fanout; it is the Claude-authored single-author lane permitted under the deferred-review path. Operator picks the path.

---

## Evidence checked

**Inputs read in full:**

- `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` (the plan under review).
- `docs/plans/_template-issue-plan.md` (plan template — Resource Intel contract, Evidence sub-section, Adversarial Review table conventions).
- `docs/governance/TRUST-ARCHITECTURE.md` (verified existence; verified the plan's "Category B/C decision point" claim corresponds to lines 23, 48, 84 of TRUST-ARCHITECTURE.md — the plan's framing is accurate).
- `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/approval-synthesis-10.md` (independent synthesis row #9 = #2552 with NEEDS_MINOR verdict pending review fanout — this artifact IS that review).
- `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/autofeed-policy-and-next-queue.md` (queue row P0 #2 lists this lane as "feed1" review; expected result file matches the path this artifact writes to).

**Memory files consulted:**

- `feedback_never_offer_to_self_label_plan_approved.md` — review must not offer/imply self-approval; verdict explicitly defers label flip to user.
- `feedback_adversarial_review_stance.md` — defect-hunting stance enforced; no praise, evidence per finding.
- `feedback_permission_gate_blocks_cross_review.md` — accounts for why this is single-author rather than dispatched fanout; recommendation is honest about the constraint.
- `feedback_codex_cli_0_124_upstream_regression.md` — informs the T1 deferred-review path recommendation (codex-cli regression makes fanout-blocking until 0.123.0 pin).

**Live state queries:**

- `gh issue view 2552 --json number,title,state,labels,updatedAt` (timestamp 2026-04-29T13:15:57Z, recorded above).
- `git log --oneline -1 docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` → `2734c103b` (committed; plan is git-tracked per `feedback_queue_git_tracked.md`).
- `ls -la docs/security/` → confirms `aceengineer-website-orphan-path-verification-2026-04-20.md` is the only existing file; runbook path is unoccupied; plan's gap claim verified.
- `ls .planning/plan-approved/2552.md` → file does not exist; correct for `status:plan-review`.

**Sources audited:** 7 distinct (plan, template, TRUST-ARCHITECTURE, approval-synthesis, autofeed-policy, live `gh` issue state, git log). Exceeds plan template's ≥3 source minimum.

---

## Boundary compliance

- Did **NOT** mutate GitHub: no `gh issue edit`, `gh issue comment`, `gh issue close`, `gh pr *`. Live state read-only via `gh issue view --json`.
- Did **NOT** apply `status:plan-approved` or change any label.
- Did **NOT** create or edit `.planning/plan-approved/*` markers.
- Did **NOT** edit the plan file `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md`. All patches recommended in this artifact only.
- Did **NOT** run `scripts/review/plan-review-fanout.sh`, `submit-to-codex.sh`, `submit-to-gemini.sh`, `codex`, or `gemini`.
- Did **NOT** modify production code, tests, or configuration.
- Did **NOT** overwrite any other lane's result file (verified `nextwave-followup-plan-review-2552-20260429-1246.md` did not exist before write; sibling files in `results/` are untouched).
- Wrote **exactly one** primary result artifact: this file at `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2552-20260429-1246.md`.

Single-author provenance disclosure: this is a Claude-authored plan-only review. It is not a substitute for cross-AI fanout. Operator must decide whether F1–F6 patches plus this artifact are sufficient (T1 deferred-review path) or whether to dispatch a full Codex+Gemini fanout from an unsandboxed terminal session.

---

## Lane classification

**COMPLETED_WITH_RESULT**
