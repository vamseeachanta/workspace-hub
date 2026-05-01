# claude-plan-review-hardening-2 — fallback result

> **ENV-MISMATCH**: Lane prescribed result path
> `/mnt/local-analysis/agent-logs/provider-autofeed-20260430-114355/results/claude-plan-review-hardening-2.md`
> is **outside** the session sandbox (`/mnt/local-analysis/workspace-hub`). Read/Write/stat all
> blocked. Per memory `feedback_lane_result_path_outside_sandbox.md` (2026-04-27), falling back
> to `docs/sessions/` and emitting this banner. Orchestrator should redirect future lanes or
> mount agent-logs into the allowed dirs list.

## STARTED
- timestamp: 2026-04-30T (lane invocation)
- lane: claude-plan-review-hardening-2
- run dir: /mnt/local-analysis/agent-logs/provider-autofeed-20260430-114355
- session sandbox: /mnt/local-analysis/workspace-hub
- task: Inspect docs/plans and review artifacts for closest approval-prep candidates,
  invalid/zero-byte/provider-failure reviews, and safe next review prompts. **No status changes.**
- mode: planning/review/evidence/handoff only — no implementation, no self-approval

## Inspection plan
1. Enumerate `docs/plans/` for active issue plans (and exclude `_template-issue-plan.md`).
2. Survey companion review artifacts (typical surfaces: `reviews/`, `docs/reviews/`,
   `.planning/reviews/`, sibling `*-review*.md` next to each plan).
3. Classify each candidate plan:
   - **Approval-prep ready**: r3 review present, all reviewers MINOR/APPROVE, no blockers.
   - **Invalid/zero-byte/provider-failure**: review file is 0 bytes, truncated, or contains
     known sandbox-error signatures (e.g., Codex "stdin hang" / Gemini "exit 55" /
     "GEMINI_CLI_TRUST_WORKSPACE" / "permission denied").
   - **Safe next review prompt**: plan exists but no review yet, or review is rN<3 and
     re-dispatch is the next step.
4. Cross-check approval-prep candidates against:
   - `.planning/plan-approved/<issue>.md` markers (must be ABSENT — gate is user-only).
   - GitHub issue label `status:plan-review` vs `status:plan-approved` (do not mutate).
5. Emit handoff lines: per-issue verdict, evidence paths, next-action prompt, no labels touched.

## Commands inspected

- `ls /mnt/local-analysis/agent-logs/provider-autofeed-20260430-114355/` → blocked (sandbox)
- `ls /mnt/local-analysis/workspace-hub/docs/plans/` → 268 plan files enumerated
- `ls /mnt/local-analysis/workspace-hub/scripts/review/results/ | grep '^(2026-04-29|2026-04-30)'` → 60 recent artifacts
- `ls /mnt/local-analysis/workspace-hub/.planning/plan-approved/` → 25 markers; latest = 2560.md
- Targeted `stat` + Read on batch2 (#2550, #2552, #2564) and recent GTM (#2554, #2556, #2561, #2562) review artifacts
- Read of `docs/plans/nightly-immediate-batch2-20260430-plan-review-hardening.md` (lane-anchor batch plan)

## Approval-prep candidates (snapshot)

| Issue | State | Closest readiness | Blockers |
|---|---|---|---|
| #2554 | Hermes-delegate live re-review = **MINOR** (substantive findings clean) | T1 deferred-review path **only** with explicit user waiver of cross-provider evidence. | Live cross-provider rerun never executed; #2556 dependency; legal scan; user approval. |
| #2556 | r4b local Hermes = MAJOR→**MINOR** after patch | Cross-provider rerun pending; **not** approval-ready. | #2554 + #2560 dependencies; contractor-evidence readiness/waiver; enum reconciliation; legal scan; user approval. |
| #2561 | r2 local Hermes = MAJOR→**MINOR** after patch | Cross-provider rerun pending; **not** approval-ready. | Provider fanout hasn't run cleanly against r2 plan; copyright/standards-quotation legal scan. |
| #2562 | r2 local Hermes = MAJOR→**MINOR** after patch | Cross-provider rerun pending; **not** approval-ready. | Provider fanout hasn't run cleanly against r2 plan; #2554/#2560 boundary still document-only. |
| #2552 | r4 final 2026-04-30: Codex **MAJOR** + Gemini **MAJOR** (substantive, non-overlapping) | T1 deferred-review path candidate iff user waives — author must revise first. | jq vs `gh --jq` decision; brittle plan-index CI test; CONTRIBUTING.md off-GitHub contact path missing; stale 2026-04-29 embedded evidence; open-question punt to user. |
| #2550 | r4 final 2026-04-30: Codex **MAJOR** + Gemini **MAJOR** (substantive, non-overlapping) | Not close — author must revise then rerun. | Dry-run semantic ambiguity (`--dry-run` vs `--check`); `requires:` missing jq; `mkdir -p logs/security/`; Hermes cron decommission access; deterministic report-delivery default; open-question punts. |
| #2564 | All three CLIs **UNAVAILABLE** today; only Hermes governance returned (CONDITIONAL) | Approval-blocked; engineering-critical plan needs ≥2 substantive no-MAJOR cross-provider reviews. | All three review CLIs failed today (see below); 2026-04-29 MAJOR artifacts remain authoritative. |

**No issues are flagged as ready for `status:plan-approved`.** Approval gate stays user-only and revision-bound (per memory `project_issue_2460_approval_binding.md`).

## Invalid / zero-byte / provider-failure reviews

| Artifact | Size | Failure mode | Classification |
|---|---:|---|---|
| `scripts/review/results/2026-04-30-plan-2564-claude.md` | 357 B | rc=124 `SessionEnd hook [...session-lifecycle-hook.mjs SessionEnd] failed: Hook cancelled` | Claude CLI session-lifecycle regression. **Not zero-byte** but 100% UNAVAILABLE stub — same shape as previous stdin-hang stubs. |
| `scripts/review/results/2026-04-30-plan-2564-codex.md` | 277 B | rc=124 `Reading additional input from stdin...` | Codex 0.124.0 upstream stdin-hang (matches memory `feedback_codex_cli_0_124_upstream_regression.md`; #2479 unresolved). |
| `scripts/review/results/2026-04-30-plan-2564-gemini.md` | 658 B | rc=124 `429 No capacity available for model gemini-3.1-pro-preview on the server` | Gemini Cloud capacity exhaustion on the pinned model — first time observed in this lane. Raises model-pinning risk separately from the trust-env regression in `feedback_gemini_trust_env_blocks_reviews.md`. |
| `scripts/review/results/2026-04-29-plan-2552-codex.md` | 673 B | UNAVAILABLE timeout/stdin (already noted by batch2 plan) | Codex stdin-hang. |
| `scripts/review/results/2026-04-29-plan-2550-codex.md` | 1.2 KB | UNAVAILABLE timeout/stdin | Codex stdin-hang. |
| `scripts/review/results/2026-04-29-plan-2552-gemini.md` | 3.0 KB | Reviewed `/tmp/wiki-health-workspace-hub` instead of the isolated worktree | Stale-workspace false-negative (already noted by batch2 plan). |

**No literal zero-byte files** were found in the 2026-04-29..30 slice — but the 277/357/658 B `UNAVAILABLE` stubs from the fanout wrapper are the operational equivalent: they consume a slot in the verdict matrix without contributing review signal. **Do not** count any of them toward an approval gate.

## Safe next review prompts (non-mutating)

These are *prompts to be issued by the user or a future approved lane*; no labels are touched here.

1. **#2564 — hold the fanout.** Until at least one of the three CLI regressions clears (Codex 0.124.0 stdin-hang fix / Gemini capacity restored or fanout repinned off `gemini-3.1-pro-preview` / Claude `SessionEnd` hook fix), do **not** rerun providers — repeat fanouts will burn provider-quota and produce identical UNAVAILABLE stubs. Keep #2564 blocked on the Hermes-governance CONDITIONAL verdict + 2026-04-29 MAJOR baseline. Recommend filing two tracking notes against #2479: (a) Claude `SessionEnd` hook regression repro, (b) Gemini `gemini-3.1-pro-preview` capacity-pinning hazard with proposal to fall back to a non-preview model.

2. **#2550 — author revision required before rerun.** Suggested revision checklist: (a) split dry-run semantics (`--dry-run` = report-only; add `--check` for compliance verification with non-zero exit), (b) reconcile jq vs `gh --jq` and update `requires:` + Bats test wording to match the chosen path, (c) add `mkdir -p logs/security/` to script bootstrap, (d) state Hermes cron decommission as manual step or specify exact `crontab -r` / unit-disable command, (e) decide deterministic report delivery (recommend: dated local report by default, GitHub-comment behind `--post-comment` flag), (f) close all "open questions" in the plan body. Then rerun Codex + Gemini + Claude against the patched plan; archive fresh artifacts; update review table; user re-evaluates.

3. **#2552 — author revision required before rerun.** Suggested revision checklist: (a) drop `test_plan_index_contains_2552_row` from the permanent test suite (move to one-time execution check), (b) add `CONTRIBUTING.md` (or `README.md`) update task to Files-to-Change so the off-GitHub contact path is publicly discoverable, (c) decide GitHub-comment vs log-only and remove from open questions, (d) declare jq vs `gh --jq`, (e) replace stale 2026-04-29 embedded evidence block with the 2026-04-30 attested set; explicitly verify labels and issue bodies. Then rerun cross-provider fanout.

4. **#2561 / #2562 — defer rerun until provider tooling recovers.** Local Hermes review already records MINOR after r2 patch; running a fresh cross-provider fanout *today* would inherit the same UNAVAILABLE failure modes seen on #2564. Once the Codex stdin-hang and Gemini capacity issues are resolved, a single clean fanout against each r2 plan should suffice.

5. **#2554 — surface deferred-review decision to user.** Hermes delegate live re-review is MINOR with substantive findings clean. The user can either (a) expressly waive cross-provider evidence under the T1 documentation deferred-review path, or (b) wait for a clean three-provider rerun. Either way, do not self-approve in the lane.

## Lane invariants confirmed

- No `status:plan-approved` labels mutated, no `.planning/plan-approved/<issue>.md` markers written or removed.
- No outreach, no external sending, no implementation work attempted.
- Sandbox boundary respected: result emitted to `docs/sessions/` with ENV-MISMATCH banner; orchestrator should re-mount `agent-logs/` or update lane prescription.
- Approval-binding rule (`project_issue_2460_approval_binding.md`) honored: every "approval-prep candidate" row above is treated as advisory — final approval still requires user action with revision-bound markers.

## Handoff

- Write the same content to the prescribed `agent-logs/` path **only** if a future lane is granted broader sandbox access; until then, this fallback file is the durable artifact.
- Memory entry `feedback_lane_result_path_outside_sandbox.md` (2026-04-27) is now reinforced; consider promoting it to a hookify rule that catches lane prompts prescribing paths outside the workspace allowlist before a session even starts.
- Recommend a follow-up issue (or appending to #2479) tracking the **simultaneous triple-provider failure** observed on #2564 today — the routing-policy assumption that "≥1 provider will be available" is now empirically violated in this run.

