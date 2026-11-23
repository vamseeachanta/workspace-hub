# Cold-Context Plan Re-Review — #2550 interaction-limit renewal (post-patch 1310)

> **Lane:** next-wave-autofeed follow-up plan re-review (single-author, plan-only, read-only)
> **Worker:** ace-linux-1 control plane (Claude Opus 4.7, 1M ctx)
> **Date:** 2026-04-29 13:33 CDT (18:33 UTC)
> **Plan under review:** `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md`
> **Patch lane consumed:** `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2550-20260429-1310.md`
> **Prior review consumed:** `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md`
> **Issue:** [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550)
> **Provider count:** single-author Claude (no cross-provider fanout invoked by this lane — same constraints as the 12:46 review)

---

## 1. Executive verdict

**Verdict:** `APPROVE_FOR_USER_REVIEW`

Cold-context re-read of the post-patch plan confirms every prior-review finding (F1 through F11) is now either resolved in plan text OR explicitly preserved as a user-decision Open question (F9). No new MAJOR or MINOR regressions were introduced by the 13:10 patch lane. The plan is **ready for user decision** on three gates that remain outside this lane's authority:

1. F9 (notify.sh vs log-only) — explicit Open question with embedded recommendation; user picks one at approval time.
2. Cross-provider coverage policy — single-author Claude-only review is acceptable per `feedback_permission_gate_blocks_cross_review.md` if the user accepts transparent provenance; alternative is terminal-session `plan-review-fanout.sh` invocation.
3. The live `status:plan-review` → `status:plan-approved` label flip and `.planning/plan-approved/2550.md` marker write are user gates per `feedback_never_offer_to_self_label_plan_approved.md` and `project_issue_2460_approval_binding.md`. This re-review does NOT self-approve.

Three LOW-class observations are noted in §3 (table-semantic mismatch on the Decommission row, bats-stub-vs-live-gh distinction, single-machine offline-fallback gap). None block approval; surfaced for user awareness.

---

## 2. Prior findings re-check table

Cross-checked against the patched plan file by direct read + token grep. Every finding has a verified plan-location anchor.

| ID | Severity (prior) | Resolution claimed | Independent re-check evidence | Verdict |
|--:|:-:|---|---|:-:|
| F1 | MAJOR — Hermes cron `d9b2d1c2270d` decommission missing | Files-to-Change Decommission row + AC bullet + Risks cutover sequence | Plan L150 (Files to Change row): `Decommission \| Hermes cron \`d9b2d1c2270d\` ... retire local-only renewal once the canonical task is verified live for one cycle`. Plan L188 (AC): `After the new ... task fires successfully on its first scheduled run AND a follow-up dry-run cycle confirms expected behavior, the Hermes cron \`d9b2d1c2270d\` is removed ... cutover is recorded in a new \`docs/handoffs/\` artifact`. Plan L220 (Risks): full sequenced cutover (a)–(d). | **Resolved** |
| F2 | MAJOR — pytest mocks Bash script | Files-to-Change new bats row + TDD split + new AC | Plan L147: `Create \| tests/security/test_renew_interaction_limits.bats \| bats integration test using a stubbed \`gh\` in \`$PATH\` (live-invocation coverage; resolves F2 mock-vs-live divergence...)`. Plan L166–172: bats integration test table with `test_dry_run_live_call_pattern`, `test_set_minus_e_propagates_jq_failure`, `test_empty_repo_list_fails_closed`. Plan L183 (AC): `All bats integration tests pass: \`bats tests/security/test_renew_interaction_limits.bats\` (resolves F2 — live invocation against stubbed \`gh\`)`. | **Resolved** (with §3 LOW observation on stub-vs-live nuance) |
| F3 | MAJOR — empty `gh repo list` silent-success | Pseudocode empty-list guard + new AC + bats test | Plan L113–117 (Pseudocode): `# Fail-closed empty-list guard ... if PUBLIC_REPOS is empty or null: print "FAIL: gh repo list returned no public repos — likely auth, API, or network failure"; exit 1`. Plan L181 (AC): `When \`gh repo list\` returns empty/null (auth, network, or API failure), script exits 1 with explicit error message — verified by \`test_empty_repo_list_fails_closed\` (resolves F3)`. | **Resolved** |
| F4 | MINOR — incomplete schedule-tasks.yaml schema | AC #6 enumerates full schema | Plan L185 (AC): `\`config/scheduled-tasks/schedule-tasks.yaml\` contains a \`github-interaction-limit-renewal\` task entry with the full canonical schema: \`id\`, \`label\`, \`schedule\`, \`machines: [ace-linux-1]\` ... \`requires: [bash, gh]\`, \`command\`, \`log\`, \`is_claude_task: false\`, and \`description\``. Cross-checked against existing entries in `config/scheduled-tasks/schedule-tasks.yaml` per prior review §4.5 — every required field is named. | **Resolved** |
| F5 | MINOR — orphan `--output FILE` flag | Pseudocode signature simplified | Plan L104 (Pseudocode): `renew-interaction-limits.sh [--dry-run]` (no `--output FILE`). Token grep confirms `--output FILE` appears only in citation/revision-log contexts (lines 198, 207) — never in active spec. | **Resolved** |
| F6 | MINOR — single-machine vs fan-out unspecified | `machines: [ace-linux-1]` pinned | Plan L148 (Files to Change): `pinned to \`machines: [ace-linux-1]\` (single runner — avoids double-PUT race)`. Plan L185 (AC): same pin with explicit "single runner — see operational note below for why dual-machine fan-out is rejected". | **Resolved** |
| F7 | MINOR — imprecise `0 2 1 */5 *` cadence | Replaced with `0 2 1 1,6,11 *` and gap math | Plan L186 (AC): `Scheduled cadence is \`0 2 1 1,6,11 *\` — fires at 02:00 UTC on the 1st of January, June, and November (max gap 153 days < 183-day \`six_months\` expiry; min gap 61 days due to month-boundary spacing — over-renewal is safe and idempotent)`. Token grep confirms old `0 2 1 */5 *` appears only in revision log (line 210). Independent gap math: Jan→Jun = 31+28+31+30+31 = 151; Jun→Nov = 30+31+31+30+31 = 153; Nov→Jan = 30+31 = 61. Plan's claim "max gap 153" verified. | **Resolved** |
| F8 | LOW — `--limit 100` future brittleness | Pseudocode `--paginate` + Risks resolution | Plan L108 (Pseudocode): `gh repo list ... --paginate`. Plan L218 (Risks): `Resolved (F8): \`gh repo list\` pagination — pseudocode now uses \`--paginate\` instead of \`--limit 100\`, removing the >100-repo brittleness class entirely`. Token grep confirms `--limit 100` only in revision/Risks-resolution contexts, not active spec. | **Resolved** |
| F9 | LOW — failure escalation path unspecified | Recorded as Open question for user | Plan L221 (Risks/Open Questions): `Open (F9 — flag for user during approval): On exit 1 ... should the script invoke \`scripts/notify.sh\` like \`research-staleness\` and \`compliance-daily\` do, OR is a \`>> $WORKSPACE_HUB/logs/security/...log\` audit trail sufficient ... Recommend: yes, wire \`notify.sh\` on non-zero exit. Decision pending user approval.` | **Properly preserved as user decision** (NOT hidden scope — see §4) |
| F10 | LOW — Adversarial Review Summary placeholder | Table populated truthfully | Plan L196–204 (Adversarial Review Summary): three-row table with Claude verdict (`MINOR_PATCH_NEEDED → patches applied`) + full F1–F11 enumeration, Codex `NOT RUN` (cites `feedback_codex_cli_0_124_upstream_regression.md`, #2479), Gemini `NOT RUN` (cites `feedback_gemini_trust_env_blocks_reviews.md`). Provider-coverage honesty note at L204 reaffirms no self-approval per `feedback_never_offer_to_self_label_plan_approved.md`. | **Resolved** |
| F11 | LOW — front-matter `Review artifacts:` template-not-actual | Updated to actual single-author state | Plan L7: `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md (single-author Claude); Codex/Gemini fanout pending — see §"Adversarial Review Summary" provider-coverage note`. Path verified to exist on disk. | **Resolved** (with §3 LOW observation on path-pattern divergence from template canonical `scripts/review/results/`) |

**Aggregate:** 11 prior findings → 10 Resolved + 1 properly preserved as user decision (F9). Zero unaddressed.

---

## 3. New findings (introduced by or surviving the patch)

I went looking for regressions: section-internal contradictions, new past-tense artifact-claim drift (per `feedback_plan_past_tense_artifact_claims.md`), token replacements that left orphans active in spec, new scope creep, broken cross-references. Below is everything I found, with severity calibrated against the prompt's adversarial-stance contract.

| # | Severity | Finding | Plan location | Why it matters | Should block approval? |
|--:|:-:|---|---|---|:-:|
| N1 | LOW | **Decommission row places non-file in `Files to Change`'s Path column.** The "Path" cell contains `Hermes cron \`d9b2d1c2270d\` (\`renew-github-collaborator-only-interaction-limits\`)` — a runtime cron handle, not a workspace-hub file path. The `Action: Decommission` is also a custom verb not in the template's `Create | Modify | Update` set. | Plan L150 | Table semantic mismatch: every other row points to a file the executor will create or edit. A Hermes cron is decommissioned via the Hermes UI/CLI, not via a repo file edit. Pragmatic — there is no other obvious anchor — but a downstream executor following the table literally cannot do the work without consulting the Risks/AC sections for the actual cutover sequence. Cleaner fix would be a separate `## Operational Decommissions` subsection. Acceptable as-is given context. | NO |
| N2 | LOW | **Bats "live invocation" claim glosses over real-`gh`-CLI flag-parsing risk.** F2 cited four mock-divergence vectors: (a) `set -euo pipefail` interactions, (b) shell quoting of repo names with special chars, (c) actual `gh` CLI flag-parsing changes between versions, (d) PATH/env contamination. Bats-with-stubbed-`gh` exercises (a), (b), (d) but NOT (c) — the stub is a fake `gh` that ignores real `gh` flag-parsing semantics. Plan AC L183 says "live invocation against stubbed `gh`"; the "live" refers to the bash script, not the `gh` CLI. | Plan L147, L166, L183 | F2 substantially mitigated but not 100% closed. Real-`gh` flag-parsing changes would be caught only when the cron actually runs in production every 5 months — a long-feedback-loop failure mode. Mitigations available (scope creep) include a smoke-test step in CI against a sandbox repo, but adding that here would expand T2 → T3. Recommend acknowledging the residual risk in the plan rather than expanding scope. | NO |
| N3 | LOW | **No fallback if `ace-linux-1` is offline at fire time.** `machines: [ace-linux-1]` (correct for double-PUT race avoidance) means if ace-linux-1 is down at 02:00 UTC on the fire date, the renewal silently misses that cycle. Next fire is 5 months out — by then the 183-day expiry has lapsed and the repo flips off `collaborators_only` between fires. | Plan L148, L185 | A real-but-bounded risk: max-gap is 153 days, expiry is 183, leaving a 30-day margin. ace-linux-1 would need to be offline at exactly the fire date AND the next fire window AND the slack between would need to consume the 30-day margin. Realistic mitigation = a separate health-check task that alerts if the renewal log hasn't been updated within 160 days. Not strictly required for v1; reasonable to defer to post-MVP. | NO |
| N4 | LOW | **Cutover sequence ambiguity: "execute one cycle" — manual trigger or wait for cron?** Risks L220 step (b): "execute one `--dry-run` cycle"; step (c): "execute one live cycle". The cron fires every 5 months, so "execute" likely means manual `bash scripts/security/renew-interaction-limits.sh --dry-run` invocation rather than waiting for the cron. The plan supports manual invocation (pseudocode signature accepts the flag) but doesn't say "manual" or "cron-fire" explicitly in the cutover. | Plan L220 | An operator following the cutover sequence literally could waste 5 months waiting for cron-fire to verify. Easy fix in plan text would clarify "manually trigger" vs "wait for first scheduled cron-fire". Acceptable as-is given the operator can read the pseudocode. | NO |
| N5 | LOW | **Review-artifacts path divergence from template canonical.** Template L7 expects `scripts/review/results/YYYY-MM-DD-plan-NNN-{claude,codex,gemini}.md`. Patched plan L7 instead points to `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md`. | Plan L7 | The patch lane is honest about the divergence — it's a real path to a real file, and the autofeed-policy lane explicitly authorized this surface. But future cross-provider fanout would write to `scripts/review/results/` per template convention, leaving two parallel review-artifact directory trees. Reviewer-discoverability concern, not a falsehood. Could be patched at promotion time when canonical fanout runs, OR documented as a convention drift in `autofeed-policy-and-next-queue.md`. | NO |
| N6 | LOW | **First-cron-fire vs current expiry timing creates a single-cycle dependency on Hermes cron.** Current public-repo limits expire 2026-10-29 (per handoff doc). New cron's first fire after install (assume install in May 2026) would be 2026-06-01. That's fine — covers expiry. But cutover sequence keeps Hermes alive until "after the new task fires successfully on its first scheduled run". The Hermes cron at ~150 days from 2026-04-29 fires around 2026-09-26, which is BEFORE the new cron's 2026-11-01 second fire. So Hermes covers the 2026-10-29 expiry cycle even if it's decommissioned right after the 2026-06-01 first new-cron fire. **No actual risk** — the patch's cutover gate is correctly conservative. | Plan L188, L220 | Verified safe. Surfacing the timing analysis for review-completeness; not a defect. | NO |

**Severity legend:** MAJOR = blocks approval. MINOR = strongly recommend patch before approval. LOW = note for awareness, does not block.

**Aggregate new findings:** 6 LOW observations, 0 MAJOR, 0 MINOR. None block approval.

---

## 4. Approval boundary / user decisions

This section enumerates exactly what the user has to decide before flipping `status:plan-review` → `status:plan-approved`. The patch lane was meticulous about NOT silently absorbing decisions; the items below are the residue.

### 4.1 F9 — failure escalation path

**Decision:** wire `scripts/notify.sh` on non-zero exit, OR rely on log-file audit trail only.

**Plan recommendation (L221):** wire `notify.sh`. Rationale embedded: "A security control that fails silently to a log no one reads is de-facto undefended; an `notify.sh` integration is one extra line in the cron command and removes that risk class."

**User authority:** confirm or override the recommendation at approval time.

### 4.2 Cross-provider coverage policy

**Decision:** accept single-author Claude-only review per `feedback_permission_gate_blocks_cross_review.md`, OR run terminal-session `scripts/review/plan-review-fanout.sh` for Codex+Gemini coverage before approval.

**Constraints:** codex-cli must be pinned at 0.123.0 per `feedback_codex_cli_0_124_upstream_regression.md` (#2479). Gemini requires `GEMINI_CLI_TRUST_WORKSPACE=true` per `feedback_gemini_trust_env_blocks_reviews.md`.

**User authority:** policy choice; both paths are legitimate per documented memory rules.

### 4.3 Approval marker

Per `project_issue_2460_approval_binding.md`, approval markers must be revision-bound. When the user does approve, the marker at `.planning/plan-approved/2550.md` should cite the post-patch plan SHA + this re-review's path + the upstream review path + the patch lane's path. **This re-review lane does not write the marker** (forbidden by prompt; also a user gate).

### 4.4 GitHub label flip

**Decision:** flip `status:plan-review` → `status:plan-approved` only after items 4.1–4.3 are decided/written.

**This re-review lane does not flip labels** (forbidden by prompt).

---

## 5. Boundary compliance

| Rule (from prompt) | Verification |
|---|---|
| Workspace = `/mnt/local-analysis/workspace-hub` | All operations relative to this path. |
| ace-linux-1 control plane only; ace-linux-2 overflow only | Lane ran on ace-linux-1 only. |
| Planning/review/synthesis only — no implementation | Zero scripts/configs/tests/source files modified. Single result artifact written; plan file not opened in Edit mode. |
| No outreach, no private contact details, no secrets | None present in this artifact. |
| No `status:plan-approved` application | No label mutation invoked. Verified §1 explicitly defers to user. |
| No `.planning/plan-approved/*` marker create or edit | Not written. Verified post-write — only this artifact at the prescribed path. |
| No `gh issue edit / close / comment / pr *`, no `plan-review-fanout.sh`, no `codex`, no `gemini`, no mutating Hermes | Only `gh issue view 2550 --json …` (read-only) executed. No mutating CLI invoked. |
| No GitHub mutation; read-only `gh issue view/list` only if needed | Verified §1 live-state check used `gh issue view --json` only. |
| Plan file NOT edited | Confirmed: this lane writes one result artifact only. Plan file unchanged. |
| Do NOT write `scripts/review/results/` artifacts | Not written. |
| Result artifact at exactly the prescribed path | This file is at `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2550-20260429-1333.md` — matches prompt. |
| Do not overwrite other lanes' result files | Pre-write `ls` confirmed the prescribed file did not exist. Sibling lanes use distinct timestamp slugs (`1246` review, `1310` patch, `1333` re-review). |
| If evidence insufficient, write BLOCKED and stop | Evidence sufficient. Lane completed normally. |

### 5.1 Live state cross-check (read-only)

`gh issue view 2550 --json number,title,state,labels,updatedAt` at 2026-04-29T18:33Z returned:

```
state: OPEN
labels: enhancement, priority:medium, cat:operations, domain:automation, domain:security, status:plan-review
updatedAt: 2026-04-29T13:15:55Z
```

Confirms: issue is OPEN, label is `status:plan-review` (no mutation since prior 12:46 review snapshot at 13:15Z). The patch lane correctly did NOT advance the GitHub label, consistent with its own §6 boundary compliance claim.

### 5.2 Memory feedback files applied

Verified at `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/`:

- `feedback_never_offer_to_self_label_plan_approved.md` — §1 verdict explicitly defers to user; no self-approval framing.
- `feedback_adversarial_review_stance.md` — §3 hunts for new defects rather than charitably accepting the patch lane's claims.
- `feedback_permission_gate_blocks_cross_review.md` — §4.2 acknowledges single-author Claude-only is acceptable.
- `feedback_codex_cli_0_124_upstream_regression.md` (#2479) — §4.2 cites pinning constraint.
- `feedback_gemini_trust_env_blocks_reviews.md` — §4.2 cites env-var requirement.
- `feedback_mock_vs_live_invocation_divergence.md` — §3 N2 evaluates whether F2 patch actually closes the divergence vector.
- `feedback_plan_past_tense_artifact_claims.md` — checked patched plan for past-tense drift; "patches applied" / "patches landed in this revision" are accurate descriptions of the plan revision (not future-implementation claims), so not drift.
- `feedback_attestation_enables_contradiction_detection.md` — applied implicitly by token-grep cross-check ensuring orphan tokens (`--output FILE`, `--limit 100`, `0 2 1 */5 *`) only appear in citation contexts, not active spec.

---

## 6. Provider-coverage honesty statement

This re-review is **single-author Claude only**. It is not a cross-provider verdict. Same constraints as the 12:46 review apply:

- codex-cli 0.124.0 stdin-hang regression (`feedback_codex_cli_0_124_upstream_regression.md`, #2479) blocks `codex exec` from this autofeed lane.
- Gemini cross-review requires interactive permission grants this autofeed lane cannot satisfy + `GEMINI_CLI_TRUST_WORKSPACE=true` per `feedback_gemini_trust_env_blocks_reviews.md`.

If the user wants 2nd-and-3rd-provider coverage on the post-patch plan (rather than the pre-patch plan that the prior fanout would have targeted), they (or a terminal-session operator) should run:

```bash
scripts/review/plan-review-fanout.sh \
  docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md
```

— with codex-cli pinned at 0.123.0 and `GEMINI_CLI_TRUST_WORKSPACE=true` exported in the session env.

If the user accepts single-author transparent-provenance review per `feedback_permission_gate_blocks_cross_review.md`, the F1–F8 patches landed + this re-review's `APPROVE_FOR_USER_REVIEW` verdict + the F9 user decision = sufficient to flip `status:plan-review` → `status:plan-approved`.

---

## 7. Provenance

- **Inputs read end-to-end:** plan file (230 lines post-patch), 12:46 review file (291 lines), 13:10 patch file (183 lines), handoff doc (71 lines), plan template (199 lines).
- **Live read-only:** `gh issue view 2550 --json …` at 2026-04-29T18:33Z (full JSON in §5.1).
- **Read-only validation checks:** 4 distinct grep-based token-presence/absence cross-checks against the patched plan + 1 read-end-to-end + 1 git log against the plan file.
- **Memory rules consulted:** 8 feedback files cited in §5.2.
- **No subagent dispatched.** This re-review is a focused single-artifact lane; subagent overhead would not benefit it.
- **No GitHub mutation, no label change, no `.planning/plan-approved/*` write, no plan-file edit, no third-party CLI call.**

---

## 8. Recommended next-step sequence (operator-facing, not auto-executed)

1. User reviews this re-review's §1 verdict + §3 LOW observations + §4 user decisions.
2. User decides F9 (notify.sh wiring) and cross-provider-fanout policy.
3. (Optional) Operator runs `scripts/review/plan-review-fanout.sh` from terminal session if cross-provider verdicts desired before approval.
4. User flips GitHub label `status:plan-review` → `status:plan-approved`.
5. User (or authorized operator) writes `.planning/plan-approved/2550.md` marker citing: post-patch plan SHA, this re-review path, prior review path, patch lane path, F9 decision recorded explicitly.
6. Plan moves to executor wave.

**Suggested approval comment text** (operator paste; NOT auto-posted by this lane):

> Approving #2550 plan post-patches F1–F8.
> Single-author Claude review at `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md` (verdict MINOR_PATCH_NEEDED).
> Patch lane at `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2550-20260429-1310.md` landed F1–F8 in plan SHA `<post-patch-SHA>`.
> Cold-context re-review at `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2550-20260429-1333.md` (verdict APPROVE_FOR_USER_REVIEW).
> F9 decision: `<wire notify.sh | log-only>` (recorded here, to be implemented in script per AC).
> Cross-provider fanout: `<accepted single-author per memory rule | run before this comment>`.

---

## 9. Lane classification

**COMPLETED_WITH_RESULT**

Verdict: `APPROVE_FOR_USER_REVIEW`. All 11 prior findings (F1–F11) verified resolved or properly preserved as user-decision Open question (F9 only). Zero new MAJOR or MINOR regressions introduced by the 13:10 patch lane. Six LOW observations surfaced in §3 for user awareness — none block approval. F9 is correctly framed as a user decision rather than absorbed as hidden scope, satisfying `feedback_never_offer_to_self_label_plan_approved.md`. Boundary compliance §5 confirms no GitHub mutation, no label change, no `.planning/plan-approved/*` write, no plan-file edit, no fanout invocation, no implementation. Single-author provider-coverage honesty preserved per `feedback_permission_gate_blocks_cross_review.md`. Exactly one artifact written at the prescribed path. Issue #2550 remains live at `status:plan-review` awaiting user gate.
