# Adversarial Plan Review — #2550 interaction-limit renewal scheduled task

> **Lane:** next-wave-autofeed follow-up plan review (single-author, plan-only, read-only)
> **Author:** ace-linux-1 control plane (Claude Opus 4.7, 1M ctx)
> **Date:** 2026-04-29 12:46 CDT (17:46 UTC)
> **Plan under review:** `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md` (committed in `2734c103b`)
> **Issue:** [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550)
> **Provider count:** single-author (Claude only) — Codex/Gemini cross-review NOT performed by this lane (sandbox / permission-gate constraints; see Boundary Compliance §5)

---

## 1. Executive verdict

**Verdict:** `MINOR_PATCH_NEEDED`

The plan is **structurally sound** — resource intelligence is grounded, T2 complexity is correct, evidence count meets the ≥3 sources threshold (counted: 5 distinct sources), every cited file existence claim verifies on disk, and the GitHub API shape matches the prior emergency-lockdown handoff. The pseudocode covers dry-run, mutate, and verify phases; the acceptance criteria are mostly testable; and the safety posture (fail-closed exit code, public-only filter, 405 handling) is correct.

However, **three substantive defects** block this from `APPROVE_FOR_USER_REVIEW`. Each is patchable inside the plan file without redrawing the deliverable. None are MAJOR (the plan is not internally contradictory, no unsafe automation is proposed, no public-claim drift). All three should be patched before the user is asked to flip `status:plan-review` → `status:plan-approved`:

1. **Hermes cron decommission gap.** Plan replaces the existing Hermes-local cron `d9b2d1c2270d` (verified live in `docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md`) but never specifies a removal/disable step. If the new task lands and the Hermes cron stays, two renewal paths race every ~150 days. This is the highest-impact missing step.
2. **pytest-on-bash mock-divergence risk.** TDD targets a Python pytest suite (`tests/security/test_renew_interaction_limits.py`) that mocks `gh` subprocess calls — but the unit-under-test is a Bash script. The user's own memory rule `feedback_mock_vs_live_invocation_divergence.md` documents this as a recurrent failure mode: *"for external-CLI fixes, mock tests pass what live CLIs reject; always do a live repro before close."* For a security control with 6-month exposure if it silently breaks, mock-only coverage is insufficient.
3. **Silent-failure surface in `gh repo list`.** Plan does not specify behavior when `gh repo list` returns an empty set (auth failure, network, account suspended). Current pseudocode would loop zero times and exit 0 — a security-control "everything passed" claim against zero verifications. Needs a fail-on-empty-list guard.

After these three patches plus the four MINOR refinements in §3, the plan is ready for user approval.

---

## 2. Findings table

| # | Severity | Finding | Plan location | Why it matters |
|--:|:-:|---|---|---|
| F1 | MAJOR | **Hermes cron `d9b2d1c2270d` decommission step missing.** The handoff doc (`docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md` lines 16, 64) confirms a live Hermes cron is performing renewal today. The plan's Deliverable claims the new task runs "without Hermes-local cron dependency" but no Files-to-Change row, no Acceptance Criterion, and no operational note specifies removal of the Hermes job. | Deliverable (L97-99); Files to Change (L134-143); Acceptance Criteria (L157-167) | Two concurrent renewal paths is a textbook cron race: both writing the same `interaction-limits` PUT every ~150 days. Worst case: one runs first and resets a 6-month expiry; the other runs hours later, races with a temporary GitHub API failure, and falsely reports a non-compliant repo, exiting 1 and triggering false alerts. Even without races, "two sources of truth" is exactly the anti-pattern this plan's existence is supposed to retire. |
| F2 | MAJOR | **pytest mocks a Bash script — recurrent mock-vs-live divergence pattern.** Test framework chosen (`pytest`, `mock` subprocess) is the same combination flagged by `feedback_mock_vs_live_invocation_divergence.md`. The four named tests all assert script behavior via mocked `gh` returns. None executes the actual `bash renew-interaction-limits.sh --dry-run` against a stubbed `gh` in `$PATH`. | Files to Change row 2 (L139); TDD Test List (L146-154); Acceptance Criteria #4 (L162) | Python mocks of subprocess calls cannot catch (a) `set -euo pipefail` interactions with grep/jq exit codes, (b) shell quoting of repo names containing special chars, (c) actual `gh` CLI flag-parsing changes between versions, (d) PATH/env contamination. For a script that touches a security control with 6-month silent-failure horizon, every one of these is a realistic break path. |
| F3 | MAJOR | **No fail-on-empty-`gh-repo-list` guard.** Pseudocode (L107-110) extracts `PUBLIC_REPOS` from `gh repo list`. If `gh` is rate-limited, auth-expired, or the account is suspended, output is empty/null. Current logic: zero iterations of mutate loop + zero iterations of verify loop + `FAIL_COUNT=0` + `exit 0` = "everything passed" with no work done. | Pseudocode (L107-110, L120-128) | Silent-failure in a security control is the worst class of bug: alerts say green; reality is undefended. Standard defense is a fail-on-zero-repos assertion (`if [ ${#PUBLIC_REPOS[@]} -eq 0 ]; then echo "FAIL: empty repo list — auth or API failure"; exit 1; fi`). The plan's #2546 context confirms 10 repos exist; any zero-result is by definition an error. |
| F4 | MINOR | **`schedule-tasks.yaml` schema fields incomplete.** Plan AC #6 lists `schedule`, `machines`, `requires`, `command`, `description` — but every existing entry in the file (verified at `config/scheduled-tasks/schedule-tasks.yaml:14-44`) also requires `log:` and `is_claude_task:`. AC will pass with a non-conforming entry. | Acceptance Criteria (L164) | Schema drift propagates: `setup-cron.sh` and `validate-schedule.py` may key off `is_claude_task` for routing decisions; missing `log:` breaks the canonical "Log" column in `docs/ops/scheduled-tasks.md` (the same table this plan also updates). |
| F5 | MINOR | **`--output FILE` flag orphan.** Pseudocode (L105) declares the flag in the signature; nothing else in the plan tests it, populates it, or specifies its format. | Pseudocode (L105); TDD Test List (L146-154); Acceptance Criteria | Either the flag is real (and needs at least one test row + one AC) or it's leftover thinking. Reviewers downstream will burn time arguing about its semantics. Cleanest: drop it; a verification report can be redirected via `> file.txt` from the cron command. |
| F6 | MINOR | **Single-machine vs `schedule_by_machine` not addressed.** The harness-update entry at `config/scheduled-tasks/schedule-tasks.yaml:73-86` uses `schedule_by_machine` to control fan-out. Plan AC #6 says `machines: [...]` but doesn't specify whether this task runs on **one** machine (correct, to avoid double-PUT races) or fans out. | Acceptance Criteria (L164) | If both `ace-linux-1` and `ace-linux-2` install the cron, the script runs concurrently every 5 months — same race surface as F1, just inside the new design. Should specify `machines: [ace-linux-1]` (or use `prefer:` with an explicit single-runner contract) and document why. |
| F7 | MINOR | **Cron schedule `0 2 1 */5 *` is non-uniform.** Plan AC #7 (L165) accepts `0 2 1 */5 *` "or equivalent." That cron syntax fires at months 1/6/11 with intervals of 151/153/61 days, max gap 153 days — within `six_months` (≈183 days) but the description "every ~150 days" is misleading because the Nov→Jan gap is only 61 days. | Acceptance Criteria (L165) | Not a safety risk (max gap < expiry), but worth noting that on month-1 fires the script runs only ~61 days after the previous renewal — fine, just over-renewing. Reviewers will ask. Cleanest fix: replace with `0 2 1 1,6,11 *` and note explicit max gap = 153 days < 183-day expiry. |
| F8 | LOW | **`gh repo list --limit 100` long-horizon brittleness.** Plan acknowledges the limit risk (Risks §1, L185) and dismisses it as "Low risk now" with 27 total repos. For a 5+ year cron-task lifetime that's a fair call, but using `--paginate` in the script would cost nothing and remove the risk class entirely. | Pseudocode (L107); Risks (L185) | Future-proofing is cheap here; a one-line change. Not blocking. |
| F9 | LOW | **No exit-1 escalation path specified.** When the cron fires every 5 months and exits 1 (any reason: API blip, auth, non-compliant verification), nothing in the plan describes how the operator finds out. Existing precedent: `research-staleness` task uses `notify.sh` for similar alerts. | Risks and Open Questions (L184-189) | A security-control script that fails silently to a log file no one reads is de-facto undefended. Either wire `notify.sh` on non-zero exit, OR specify that the cron's `>> log` is the audit surface and the operator commits to checking it. Either is acceptable; "neither" is not. |
| F10 | LOW | **Adversarial Review Summary table (L173-181) is empty placeholder.** The plan template comment says "Do not post to GitHub until this section is populated" — but the issue is already at `status:plan-review` (verified live, see §4). | Adversarial Review Summary (L170-181) | Not blocking (the label is the *trigger* for reviews; populating the table is a post-review patch). Plan should be patched to include this review's verdict + any subsequent providers' verdicts before promotion. |
| F11 | LOW | **Front-matter `Review artifacts:` claims three providers.** Line 7 lists `claude.md | codex.md | gemini.md` per the template. Until cross-review actually runs, only the Claude artifact (this file's sibling at `scripts/review/results/2026-04-29-plan-2550-claude-r1.md` — note: NOT written by this lane per its prompt) will exist. | Front-matter L7 | Template artifact, not a falsehood, but should be patched to reflect actual review state at promotion time. |

**Severity legend:** MAJOR = patch required before approval. MINOR = patch strongly recommended. LOW = patch nice-to-have.

---

## 3. Required patches before approval

The following list, in priority order, is the minimum patch set to move the plan from `MINOR_PATCH_NEEDED` to `APPROVE_FOR_USER_REVIEW`:

### Patch 3.1 (resolves F1) — Hermes cron decommission

Add to **Files to Change** (after the row for `docs/ops/scheduled-tasks.md`):

> | Decommission | Hermes cron `d9b2d1c2270d` (`renew-github-collaborator-only-interaction-limits`) | retire local-only renewal once the canonical task is verified live |

Add to **Acceptance Criteria** (new bullet):

> - [ ] After the new `github-interaction-limit-renewal` task fires successfully on its first scheduled run, the Hermes cron `d9b2d1c2270d` is removed (or `disabled: true`-equivalent) and the change is recorded in `docs/handoffs/`.

Add to **Risks and Open Questions**:

> - **Operational gap:** Until the Hermes cron is removed, two renewal paths run concurrently every ~150 days. Cutover sequence: (a) install new task in dry-run mode for one cycle, (b) verify cron logs match expected behavior, (c) remove Hermes cron, (d) confirm next renewal cycle landed via the canonical task only.

### Patch 3.2 (resolves F2) — Test approach hardening

Replace the current Files-to-Change row 2 + TDD Test List with one of three options. **Strongly recommended option:** add a Bash integration test alongside the pytest suite, with a stubbed `gh` in `$PATH`:

> | Create | `tests/security/test_renew_interaction_limits.bats` | bats integration test using stubbed `gh` in `$PATH` |

Add three integration test rows:

| Test name | What it verifies | Mechanism | Expected result |
|---|---|---|---|
| `test_dry_run_live_call_pattern` | live `bash renew-interaction-limits.sh --dry-run` invokes only GET, no PUT | stub `gh` writes invoked args to `/tmp/gh-trace`; assert no PUT lines | `gh-trace` contains only `api repos/.../interaction-limits` GETs |
| `test_set_minus_e_propagates_jq_failure` | malformed `gh` JSON does not silently exit 0 | stub `gh` returns invalid JSON; run script | exit code != 0, stderr mentions JSON parse failure |
| `test_empty_repo_list_fails_closed` | empty `gh repo list` does not produce a "0 failures" success | stub `gh repo list` returns `[]`; run script | exit code 1, stderr mentions empty-repo-list condition |

Update Acceptance Criteria #4 to:

> - [ ] All TDD tests pass: `uv run pytest tests/security/test_renew_interaction_limits.py -v` AND `bats tests/security/test_renew_interaction_limits.bats`

(Alternative: convert the Bash script to Python — but that increases scope materially and isn't necessary if bats integration tests are added.)

### Patch 3.3 (resolves F3) — Fail-closed empty-repo-list guard

Add to **Pseudocode** (between the `PUBLIC_REPOS = ...` extraction and the for loop):

```
  if PUBLIC_REPOS is empty or null:
    print "FAIL: gh repo list returned no public repos — likely auth or API failure"
    exit 1
```

Add to **Acceptance Criteria**:

> - [ ] When `gh repo list` returns empty/null, script exits 1 with explicit error (verified by `test_empty_repo_list_fails_closed` from Patch 3.2).

### Patch 3.4 (resolves F4) — Schema completeness

Update Acceptance Criteria #6 to enumerate the full schema:

> - [ ] `config/scheduled-tasks/schedule-tasks.yaml` contains a `github-interaction-limit-renewal` task entry with `id`, `label`, `schedule`, `machines: [ace-linux-1]`, `requires: [bash, gh]`, `command`, `log`, `is_claude_task: false`, and `description`.

(The single-machine specification also resolves F6.)

### Patch 3.5 (resolves F5) — Drop `--output FILE` orphan

Remove `[--output FILE]` from pseudocode signature line. The cron command already redirects to a log file via `>> $WORKSPACE_HUB/logs/...` — separate flag is not needed.

### Patch 3.6 (resolves F7) — Concrete cron syntax

Update Acceptance Criteria #7 to:

> - [ ] Scheduled cadence is `0 2 1 1,6,11 *` (max interval 153 days < 183-day `six_months` expiry; min interval 61 days due to month-boundary spacing — over-renewal is safe).

### Patch 3.7 (resolves F9) — Failure escalation

Add to **Risks and Open Questions** as an Open question:

> - **Open:** On exit 1 (any failure mode), should the script invoke `scripts/notify.sh` like `research-staleness` does, OR is a `>> $WORKSPACE_HUB/logs/security/...log` audit-trail sufficient given the 5-month cadence? Flag for user during approval.

### Optional improvement (resolves F8) — pagination

In pseudocode, change `gh repo list $OWNER --json ... --limit 100` to `gh repo list $OWNER --json ... --paginate`. One-line change, removes the limit-class risk entirely.

### Post-approval housekeeping (F10, F11)

After Codex/Gemini cross-review (or after explicit user decision to accept single-author plan-review per `feedback_permission_gate_blocks_cross_review.md`), patch Adversarial Review Summary table and front-matter to reflect actual provider verdicts.

---

## 4. Evidence checked

### 4.1 Live issue state (read-only)

Verified via `gh issue view 2550 --json number,title,state,labels,updatedAt` at 2026-04-29T17:46Z:

```json
{
  "number": 2550,
  "title": "chore(security): codify public repo interaction-limit renewal in scheduled tasks",
  "state": "OPEN",
  "labels": [
    {"name": "enhancement"},
    {"name": "priority:medium"},
    {"name": "cat:operations"},
    {"name": "domain:automation"},
    {"name": "domain:security"},
    {"name": "status:plan-review"}
  ],
  "updatedAt": "2026-04-29T13:15:55Z"
}
```

Confirms: issue is OPEN, currently labeled `status:plan-review` (correct precondition for adversarial review), updated 13:15Z (≈4.5 hours before this review fires).

### 4.2 Plan file existence and commit

- Plan file: `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md` — EXISTS, 196 lines.
- Commit: `2734c103b docs(plans): draft plans for #2550 interaction-limit renewal and #2552 external contributor runbook` (verified via `git log --oneline -- docs/plans/2026-04-29-issue-2550-...`).

### 4.3 Plan-claimed file existence

| Claim in plan | Verified |
|---|---|
| `config/scheduled-tasks/schedule-tasks.yaml` exists | YES — 26869 bytes, schema confirmed |
| `scripts/security/secrets-scan.sh` exists | YES — 4425 bytes |
| `docs/ops/scheduled-tasks.md` exists | YES — 5085 bytes, table format confirmed |
| `docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md` exists | YES — 5111 bytes |
| `scripts/security/renew-interaction-limits.sh` MISSING (this plan creates) | CONFIRMED — `scripts/security/` contains only `secrets-scan.sh` |
| `tests/security/` MISSING (this plan creates) | CONFIRMED — `ls tests/security` returned "No such file or directory" |
| No existing renewal entry in schedule-tasks.yaml | CONFIRMED via grep — no `interaction` or `collaborators_only` matches in `config/` or `scripts/security/` |

### 4.4 Cross-checks against handoff doc

Read `docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md`:

- Confirms 10 public repos: `worldenergydata`, `workspace-hub`, `assethold`, `aceengineer-website`, `assetutilities`, `digitalmodel`, `teamresumes`, `hobbies`, `pdf-large-reader`, `aceengineercode` (1 archived: `aceengineercode`).
- Confirms `expiry=six_months` was applied 2026-04-29, expires 2026-10-29 (= 183 days, NOT 180).
- Confirms private repos return `405 Interaction limits cannot be set for private repositories` — plan's pre-filter on `isPrivate=false` is correct.
- **Confirms Hermes cron `d9b2d1c2270d` exists and runs the renewal today** — this is the source of finding F1.
- Confirms #2546 closed, #2550/#2551/#2552 opened as follow-ups.

### 4.5 schedule-tasks.yaml schema verification

Verified all task entries between L1 and L300 share the schema:
- `id`, `label`, `schedule` (or `schedule_by_machine`), `machines`, `requires`, `command`, `log`, `is_claude_task`, `description`.

Plan's AC #6 omits `log` and `is_claude_task` — source of F4.

### 4.6 Memory feedback files referenced

Verified at `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/`:
- `feedback_never_offer_to_self_label_plan_approved.md` — applied (no self-approval offered).
- `feedback_adversarial_review_stance.md` — applied (defect-hunting stance, not charitable reading).
- `feedback_permission_gate_blocks_cross_review.md` — applied (single-author transparent provenance, no false-cross-review framing).
- `feedback_codex_cli_0_124_upstream_regression.md` — applied (no codex invocation attempted).
- `feedback_mock_vs_live_invocation_divergence.md` — applied as basis for F2.

### 4.7 Boundary-context cross-checks

Per `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/autofeed-policy-and-next-queue.md` §6 Lane 1: this exact lane is the prescribed P0 first-fire. Verdict reached here matches the safe-auto-spawn allowed transition: "Plan exists, no cross-review artifact for it today → Plan-only adversarial review (Claude lane)."

Per `approval-synthesis-10.md` rank 10: #2550 is correctly classified `NEEDS_MINOR` pending review fanout. This review delivers the Claude-side verdict; user retains the option to (a) accept single-author Claude-only review per `feedback_permission_gate_blocks_cross_review.md` after patches land, OR (b) run terminal-session fanout for Codex+Gemini coverage.

### 4.8 Sources audited (count for ≥3 verification per template contract)

1. The plan file itself.
2. The handoff doc `github-collaborator-only-lockdown-2026-04-29.md`.
3. `config/scheduled-tasks/schedule-tasks.yaml` schema.
4. `docs/ops/scheduled-tasks.md` table format.
5. Live `gh issue view 2550` output.
6. Memory feedback files (5 distinct rules applied).

Count: 6 sources → satisfies ≥3 contract.

---

## 5. Boundary compliance

This lane operated within the prescribed authorization envelope. Read each boundary rule, then the verifying action:

| Rule (from prompt) | Verification |
|---|---|
| Do NOT mutate GitHub | Only read-only `gh issue view 2550 --json …` was executed. No `gh issue edit`, `gh issue close`, `gh issue comment`, or `gh pr *`. |
| Do NOT apply `status:plan-approved` or `status:plan-review` | No label mutation attempted. Confirmed via §4.1: live label state is unchanged from 13:15Z snapshot to 17:46Z review-write. |
| Do NOT create or edit `.planning/plan-approved/*` markers | No file written under `.planning/plan-approved/`. Verified post-write: only `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md` was authored. |
| Do NOT edit the plan file | All patches in §3 are recommendations expressed in this result file. Plan file `docs/plans/2026-04-29-issue-2550-...md` not opened in Edit mode. |
| Do NOT run plan-review-fanout.sh, codex, or gemini | None invoked. Single-author review only. |
| Do NOT implement code or cron changes | No changes to scripts, config, or cron. |
| Workspace = `/mnt/local-analysis/workspace-hub` | All operations relative to this path; no cross-workspace reads. |
| Do not send outreach, expose private contact details, hardcode secrets | None of the above appear in this artifact. |
| Write exactly one primary result artifact at the prescribed path | This file is the ONLY artifact written. |
| Do not overwrite other lanes' result files | Verified prescribed path is unique to this lane (timestamp `1246` differentiates from the in-flight 11:55-launch lanes). |
| If evidence insufficient, write blocker note and stop | Evidence sufficient for MINOR verdict. Lane completed normally, not blocked. |

---

## 6. Provider-coverage honesty statement

Per `feedback_permission_gate_blocks_cross_review.md`: this is a **single-author Claude-only review**. It is not a cross-provider verdict. Codex CLI is currently subject to the 0.124.0 stdin-hang regression (`feedback_codex_cli_0_124_upstream_regression.md`, #2479) and Gemini cross-review requires interactive permission grants this autofeed lane cannot satisfy.

If the user wants 2nd-and-3rd-provider coverage before approval, they (or a terminal-session operator) should run:

```bash
scripts/review/plan-review-fanout.sh \
  docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md
```

(With codex-cli pinned at 0.123.0 and `GEMINI_CLI_TRUST_WORKSPACE=true` per `feedback_gemini_trust_env_blocks_reviews.md`.)

If the user accepts single-author transparent-provenance review per the same memory rule, this verdict + the F1-F7 patches landed = sufficient to flip `status:plan-review` → `status:plan-approved`.

---

## 7. Recommended next-step sequence (operator-facing)

1. Patch the plan per §3.1 through §3.6 (F1-F7). Optionally apply F8 pagination improvement.
2. Decide single-author-vs-fanout coverage policy. If fanout, run `plan-review-fanout.sh` from a user terminal session and post Codex/Gemini verdicts to the Adversarial Review Summary table (F10 patch).
3. After patches land + provider-coverage decision is recorded, post bounded-scope approval comment to #2550 (paste-ready text below) and apply `status:plan-approved`.
4. Write `.planning/plan-approved/2550.md` marker citing the post-patch plan SHA and this review's path (per `project_issue_2460_approval_binding.md`).

**Suggested approval comment text** (operator paste, NOT auto-posted by this lane):

> Approving #2550 plan post-patches F1-F7. Single-author Claude review at
> `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md`
> verdict: MINOR_PATCH_NEEDED → patches landed in commit `<SHA>` → APPROVE.
> Scope: T2 plan covering script + tests + schedule-tasks.yaml entry + Hermes cron decommission.
> Cross-provider fanout deferred per `feedback_permission_gate_blocks_cross_review.md`.

---

## 8. Provenance

- Live state: `gh issue view 2550 --json …` at 2026-04-29T17:46Z (full JSON in §4.1).
- Plan content: read end-to-end at `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md` (committed in `2734c103b`).
- Template content: read end-to-end at `docs/plans/_template-issue-plan.md`.
- Cross-context: read `approval-synthesis-10.md` rank 10 + `autofeed-policy-and-next-queue.md` §6 Lane 1 + `docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md`.
- Filesystem checks: `ls scripts/security/`, `ls tests/security`, `ls -la` for each plan-cited path.
- Schema verification: grep + head against `config/scheduled-tasks/schedule-tasks.yaml`.
- Memory: 5 feedback files applied as cited in §4.6.

---

## 9. Lane classification

**COMPLETED_WITH_RESULT**

Verdict: `MINOR_PATCH_NEEDED`. Three MAJOR-class findings (F1 Hermes-cron decommission, F2 mock-vs-live divergence, F3 silent-failure on empty-repo-list) require patches before user approval; four MINOR-class findings (F4-F7) and four LOW-class findings (F8-F11) follow. Patch set is enumerated in §3 and is plan-file-only — no code changes required to reach `APPROVE_FOR_USER_REVIEW`. Single-author provider-coverage honesty preserved per memory rule. Boundary compliance §5 confirms no GitHub mutation, no label change, no `.planning/plan-approved/*` write, no plan-file edit, no cron-fanout invocation. Exactly one artifact written at the prescribed path.
