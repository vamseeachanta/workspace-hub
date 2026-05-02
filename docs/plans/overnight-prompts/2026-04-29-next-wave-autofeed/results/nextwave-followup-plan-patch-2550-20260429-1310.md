# Plan Patch — #2550 interaction-limit renewal (post review-1246)

> **Lane:** next-wave-autofeed follow-up plan-patch (single plan-file edit; no code, config, label, or marker mutation)
> **Worker:** ace-linux-1 control plane (Claude Opus 4.7, 1M ctx)
> **Date:** 2026-04-29 13:10 CDT (18:10 UTC)
> **Plan patched:** `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md`
> **Review consumed:** `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md`
> **Issue:** [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) — remains `status:plan-review`, awaiting user approval (no GitHub mutation by this lane)

---

## 1. Summary of plan edits

The patch lands the F1–F8 fixes prescribed in the §3 patch set of the upstream review without expanding scope, without implementing scripts/tests/config, and without self-approving. Six discrete sections of the plan file were modified:

1. **Front-matter** — `Status` flipped from `draft` to `plan-review` to match live GitHub label state (verified by the upstream review at 2026-04-29T17:46Z); `Review artifacts` line now points to the actual single-author Claude review file path with explicit "Codex/Gemini fanout NOT run" disclosure.
2. **Pseudocode** — three changes: (a) dropped the orphan `[--output FILE]` flag (F5); (b) replaced `gh repo list ... --limit 100` with `gh repo list ... --paginate` (F8 future-proofing); (c) inserted a fail-closed empty-list guard between repo-list extraction and the mutation loop (F3 silent-failure fix). The new guard explicitly cites the review file path so future readers can trace the rationale.
3. **Files to Change** — added two rows: a `Create` row for `tests/security/test_renew_interaction_limits.bats` (F2 — bats integration test alongside the pytest suite), and a `Decommission` row for the existing Hermes cron `d9b2d1c2270d` (F1 — eliminates dual renewal-path race). Also pinned the schedule-tasks.yaml row's commentary to `machines: [ace-linux-1]` for the F6 single-runner contract.
4. **TDD Test List** — split into two tables: "Pytest unit tests" (the original 4 mocked-subprocess rows) and "Bats integration tests" (3 new live-invocation rows: `test_dry_run_live_call_pattern`, `test_set_minus_e_propagates_jq_failure`, `test_empty_repo_list_fails_closed`). The split makes the F2 mock-vs-live divergence remediation visible at a glance.
5. **Acceptance Criteria** — six material changes: added empty-list-fail AC (F3); added bats integration AC (F2); enumerated the full `schedule-tasks.yaml` schema including `id`, `label`, `log`, `is_claude_task: false`, and `machines: [ace-linux-1]` (F4 + F6); replaced `0 2 1 */5 *` cadence with `0 2 1 1,6,11 *` and documented max gap 153 days < 183-day expiry, min gap 61 days from month-boundary spacing (F7); added Hermes cron decommission AC with sequenced cutover gate (F1).
6. **Adversarial Review Summary + Risks/Open Questions** — populated the previously-empty review-summary table truthfully: Claude verdict (`MINOR_PATCH_NEEDED → patches applied`), Codex/Gemini explicitly marked `NOT RUN` with linked memory-feedback citations explaining why (codex-cli 0.124.0 stdin-hang regression #2479; Gemini interactive-permission gate). Added a provider-coverage honesty note that the plan does NOT self-approve. Added a revision log enumerating every change. In Risks: marked F8 pagination as Resolved; added the Hermes cron cutover sequence (F1); added an Open question (F9) on `notify.sh` failure escalation vs log-only audit trail with a recommended-yes flag for user decision.

The patch is plan-text-only. No script, test file, schedule config, ops doc, source code, GitHub label, or `.planning/plan-approved/*` marker was created or modified.

---

## 2. Findings resolved

| ID | Severity | Status after patch | Plan section that carries the fix |
|--:|:--:|---|---|
| F1 | MAJOR | **Resolved** | Files-to-Change Decommission row + Acceptance Criteria new bullet (post-cutover Hermes removal gate) + Risks Operational gap entry (sequenced cutover) |
| F2 | MAJOR | **Resolved** | Files-to-Change new bats row + TDD Test List split with 3 new integration rows + Acceptance Criteria new bats AC |
| F3 | MAJOR | **Resolved** | Pseudocode empty-list guard + TDD `test_empty_repo_list_fails_closed` + Acceptance Criteria new bullet |
| F4 | MINOR | **Resolved** | Acceptance Criteria #6 enumerates full schema (`id`, `label`, `log`, `is_claude_task: false`) |
| F5 | MINOR | **Resolved** | Pseudocode signature now reads `[--dry-run]` only |
| F6 | MINOR | **Resolved** | `machines: [ace-linux-1]` pinned in Files-to-Change row + Acceptance Criteria #6 + provenance note "single runner — avoids double-PUT race" |
| F7 | MINOR | **Resolved** | Acceptance Criteria #7 specifies `0 2 1 1,6,11 *` with documented max/min gaps |
| F8 | LOW | **Resolved (trivial plan-text)** | Pseudocode `--paginate`; Risks entry flipped to "Resolved" |
| F9 | LOW | **Recorded as Open question for user** | Risks/Open Questions new entry recommending `notify.sh` integration; explicit "Decision pending user approval" |
| F10 | LOW | **Resolved** | Adversarial Review Summary populated with truthful single-author Claude verdict + Codex/Gemini NOT RUN entries |
| F11 | LOW | **Resolved** | Front-matter `Review artifacts` line now reflects actual single-author state (real path; explicit fanout-pending note) |

---

## 3. Residual blockers

**None blocking the patch lane.** The patch lane completed its scope: every MAJOR finding (F1, F2, F3) plus every MINOR finding (F4–F7) plus the trivial LOW finding F8 are now expressed in plan text. F9 was deliberately preserved as an Open question because the prompt forbids implementation/config decisions — the user is the correct decider on whether the script wires `notify.sh` or relies on log audit only.

**Pending (out of scope for this lane, surfaced for handoff):**

- **Codex / Gemini cross-review fanout has not been run on the patched plan.** Per `feedback_permission_gate_blocks_cross_review.md`, the user has two acceptable paths to approval:
  1. Accept the single-author Claude review + this patch as sufficient (transparent provenance is preserved — every claim cites the upstream review file path or a memory rule).
  2. Run `scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md` from a terminal session with codex-cli pinned at 0.123.0 (per `feedback_codex_cli_0_124_upstream_regression.md`, #2479) and `GEMINI_CLI_TRUST_WORKSPACE=true` (per `feedback_gemini_trust_env_blocks_reviews.md`) before flipping `status:plan-review` → `status:plan-approved`.
- **F9 decision** — user must choose `notify.sh` wiring vs log-only audit at approval time. Recommendation embedded in plan: yes, wire `notify.sh`.
- **Approval marker (`.planning/plan-approved/2550.md`)** — not written by this lane (forbidden by the prompt). Per `project_issue_2460_approval_binding.md`, when the user does approve, the marker should cite the post-patch plan SHA AND the review artifact path AND the storage surface (revision-bound markers, not mutable file-path refs).

No new defects were introduced by the patch (validated by §4).

---

## 4. Validation commands and output summary

All checks were read-only against the patched plan file. No GitHub call, no script execution, no test invocation, no codex/gemini call.

**Check 1 — git diffstat (proves only the plan file changed):**

```bash
git diff --stat docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md
# Output:
#  ...550-interaction-limit-renewal-scheduled-task.md | 68 ++++++++++++++++------
#  1 file changed, 51 insertions(+), 17 deletions(-)
```

**Check 2 — git numstat (precise insertion/deletion counts on plan file only):**

```bash
git diff --numstat docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md
# Output:
#  51  17  docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md
```

Verified: only one file modified (the plan), +51/-17 lines.

**Check 3 — guardrails landed (Grep for new spec markers):**

The following patched-in tokens all appear at expected line numbers in the plan:

| Token | Line(s) | Section |
|---|--:|---|
| `--paginate` | 108, 207, 218 | Pseudocode + revision log + Risks |
| `if PUBLIC_REPOS is empty or null:` | 115 | Pseudocode (F3 guard) |
| `0 2 1 1,6,11` | 186 | Acceptance Criteria #7 (F7) |
| `machines: [ace-linux-1]` | 148, 185 | Files to Change + AC #6 (F6) |
| `is_claude_task: false` | 185 | AC #6 schema completeness (F4) |
| `test_renew_interaction_limits.bats` | 147, 166, 183 | Files to Change + TDD heading + AC bats invocation (F2) |
| `d9b2d1c2270d` | 150, 188, 208 | Files to Change Decommission row + AC + revision log (F1) |
| `test_empty_repo_list_fails_closed` | 172, 181, 209 | TDD bats row + AC + revision log (F3) |
| `notify.sh` | 220 (Risks Open question, F9) | Risks/Open Questions |

**Check 4 — orphan removal (Grep proves F5 cleanup):**

```bash
# search for live-spec instances of `--output FILE` and `--limit 100`:
grep -n "\\-\\-output FILE\\|\\-\\-limit 100" docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md
# Output (3 lines, all in Adversarial Review Summary citation cells, not active spec):
# 198 (key-findings cell naming F5 historical finding)
# 207 (revision log: "dropped `[--output FILE]` flag (F5); switched `--limit 100` → `--paginate` (F8)")
# 218 (Risks resolution note: "now uses `--paginate` instead of `--limit 100`")
```

The Pseudocode signature now reads exactly `renew-interaction-limits.sh [--dry-run]` — the orphan is gone from active spec; remaining mentions are appropriate citations of the historical state.

**Check 5 — Pseudocode block read end-to-end:**

Read lines 102–137. Confirmed:
- Signature: `renew-interaction-limits.sh [--dry-run]` (no `--output FILE`).
- Repo extraction: `--paginate` (not `--limit 100`).
- Empty-list guard: explicit fail-closed branch with `exit 1` and an audit-trail message.
- Mutate loop, verify loop, and exit-code logic preserved unchanged from the original draft (no scope creep).

**Check 6 — Adversarial Review Summary table populated:**

Read lines 196–200. Confirmed:
- `Claude` row: verdict `MINOR_PATCH_NEEDED → patches applied`, full F1–F11 enumeration with severity tags, link to upstream review file path.
- `Codex` row: verdict `NOT RUN` with cited memory rule (`feedback_codex_cli_0_124_upstream_regression.md`, #2479) explaining why fanout was deferred.
- `Gemini` row: verdict `NOT RUN` with cited memory rule (`feedback_gemini_trust_env_blocks_reviews.md`) explaining the interactive-permission gate.
- Provider-coverage honesty note: explicit "this plan does NOT self-approve; the `status:plan-review` GitHub label remains until the user explicitly flips it" (cites `feedback_never_offer_to_self_label_plan_approved.md`).

No implementation tests were run (forbidden by prompt). All validation is plan-text inspection only.

---

## 5. Git diffstat — plan file only

```
 docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md | 68 ++++++++++++++++------
 1 file changed, 51 insertions(+), 17 deletions(-)
```

Single-file patch. No scripts, tests, config, source, ops doc, marker, label, or workflow file touched. No untracked artifact created by this lane other than this result file at the prescribed path.

---

## 6. Boundary compliance

| Rule from prompt | Verification |
|---|---|
| Workspace = `/mnt/local-analysis/workspace-hub` | All operations relative to this path. |
| Treat ace-linux-1 as control plane; ace-linux-2 overflow only | Lane ran on ace-linux-1 only. |
| No outreach, no private contact details, no secrets | None present in this artifact. |
| No `status:plan-approved` application | No label mutation. The patch sets the plan file's internal `Status:` field to `plan-review` (the live GitHub label state); does NOT advance to `plan-approved`. |
| No `gh issue edit / close / comment / pr *`, no `plan-review-fanout.sh`, no `codex`, no `gemini` | None invoked. The `gh issue view` reference in §4 of the upstream review is read-only; this patch lane invoked nothing. |
| No `.planning/plan-approved/*` marker | Not created or modified. Verified post-write — only this artifact and the plan-file edit are this lane's outputs. |
| No production / code / config / ops-doc changes | Only the plan markdown file was edited. |
| Re-check stale context with read-only local/live state | Re-read the upstream review, the plan, the handoff doc, the schedule-tasks.yaml, and the plan template before editing. |
| Write exactly one primary result artifact at the prescribed path | This file is the ONLY result artifact written by this lane. |
| Do not overwrite other lanes' results | Verified prescribed path is unique to this lane (timestamp `1310` differentiates from sibling lane timestamps `1246` review and `1310` patch — same minute as the #2552 patch lane but different issue ID in the filename). |
| If evidence insufficient, write BLOCKED and stop | Evidence sufficient. Lane completed normally. |

---

## 7. Provenance

- **Inputs read end-to-end:** plan file (196 lines pre-patch), review file (291 lines), handoff doc (71 lines), schedule-tasks.yaml (top 643 lines with full schema confirmation), plan template.
- **Memory rules applied:**
  - `feedback_never_offer_to_self_label_plan_approved.md` — patch does NOT self-approve.
  - `feedback_permission_gate_blocks_cross_review.md` — single-author transparent provenance preserved; Codex/Gemini fanout explicitly marked NOT RUN.
  - `feedback_mock_vs_live_invocation_divergence.md` — basis for F2 patch (bats integration test alongside pytest mocks).
  - `feedback_codex_cli_0_124_upstream_regression.md` (#2479) — cited in Adversarial Review Summary Codex row.
  - `feedback_gemini_trust_env_blocks_reviews.md` — cited in Adversarial Review Summary Gemini row.
  - `feedback_plan_past_tense_artifact_claims.md` — patch keeps plan in future tense; e.g., "the Hermes cron `d9b2d1c2270d` is removed [after the new task fires]" not "was removed".
  - `feedback_adversarial_review_stance.md` — review consumed in defect-hunting mode; patch addresses every finding rather than dismissing them charitably.
  - `project_issue_2460_approval_binding.md` — referenced in §3 residual-blocker handoff for future approval-marker writing.
- **Read-only validation:** 6 distinct checks (diffstat, numstat, two greps, two reads). No script execution, no GitHub mutation, no test invocation, no third-party CLI call.
- **No subagent dispatched.** This lane is a focused single-file plan-text edit; subagent overhead would not benefit it.

---

## 8. Lane classification

**COMPLETED_WITH_RESULT**

Patch landed cleanly: all three MAJOR findings (F1, F2, F3), all four MINOR findings (F4–F7), and the trivial LOW finding F8 are now reflected in plan text. F9 retained as an explicit Open question for user decision. F10/F11 (review-summary placeholder + front-matter artifact line) resolved by populating the table and updating the line truthfully. Issue remains `status:plan-review`; no GitHub mutation, no label change, no `.planning/plan-approved/*` write, no implementation, no fanout. Plan file diffstat: +51/-17 lines, single file. Exactly one result artifact written at the prescribed path. Single-author provider-coverage honesty preserved per memory contract; Codex/Gemini fanout remains a user-discretion gate before approval.
