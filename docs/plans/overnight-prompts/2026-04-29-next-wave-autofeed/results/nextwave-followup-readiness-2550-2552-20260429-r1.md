# Readiness packet — [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) and [#2552](https://github.com/vamseeachanta/workspace-hub/issues/2552) (synthesis-only, no mutations)

> **Lane:** `2026-04-29-next-wave-autofeed` — bounded follow-up planning/review/synthesis only.
> **Synthesizer:** Claude Opus 4.7 (1M context), `ace-linux-1` autofeed worker.
> **Date:** 2026-04-29 (timestamp suffix `r1`).
> **Inputs consumed:** the two plan files at HEAD plus their three-lane review chains (review → patch → re-review). Full list in §"Files inspected".
> **Output policy:** synthesis only. No plan edits, no GitHub mutation, no commit, no marker. Re-states the residue the user must decide.

---

## Summary

Both plans are at the same governance state and both are **ready for user decision**:

| Issue | Plan SHA on `main` | Live label | Approval marker | Single-author chain verdict | Cross-AI fanout |
|---|---|---|---|---|---|
| [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) | `16724e9c7` (auto-sync 21:16Z) | `status:plan-review` | absent | review 1246 `MINOR_PATCH_NEEDED` → patch 1310 lands F1–F8 → re-review 1333 **`APPROVE_FOR_USER_REVIEW`** | NOT RUN |
| [#2552](https://github.com/vamseeachanta/workspace-hub/issues/2552) | `16724e9c7` (auto-sync 21:16Z) | `status:plan-review` | absent | review 1246 `MINOR_PATCH_NEEDED` → patch 1310 lands F1–F6 + L1 + L3 → re-review 1333 **`APPROVE_FOR_USER_REVIEW`** | NOT RUN |

The 13:10 patch lanes' plan-text deltas (working-tree only at the time) were absorbed into commit `16724e9c7 chore(sync): auto-sync 2026-04-29` at 21:16Z — auto-sync-as-silent-pusher per `feedback_autosync_silent_pusher.md`. Working tree on both files is clean as of this synthesis. The user-in-loop gate is intact: neither label has flipped, no `.planning/plan-approved/255{0,2}.md` marker exists, and no autofeed lane proposed self-promotion (per `feedback_never_offer_to_self_label_plan_approved.md`).

---

## (a) Artifact-ready for user review

| Artifact | Path | Use |
|---|---|---|
| #2550 plan (post-patch) | `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md` | Read end-to-end before approval; F1–F8 patches live in this commit. |
| #2552 plan (post-patch) | `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` | Read end-to-end before approval; F1–F6+L1+L3 patches live in this commit. |
| #2550 single-author Claude review | `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md` | Source of F1–F11 findings; verdict `MINOR_PATCH_NEEDED`. |
| #2550 patch report | `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2550-20260429-1310.md` | Maps each finding to plan-text edits; F9 explicitly preserved as user decision. |
| #2550 cold-context re-review | `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2550-20260429-1333.md` | Verdict `APPROVE_FOR_USER_REVIEW`; six LOW observations (N1–N6) surfaced for awareness, none block. |
| #2552 single-author Claude review | `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2552-20260429-1246.md` | Source of F1–F6 + L1–L3 findings; verdict `MINOR_PATCH_NEEDED`. |
| #2552 patch report | `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2552-20260429-1310.md` | Maps each finding to plan-text edits; L2 deferred per task scope. |
| #2552 cold-context re-review | `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2552-20260429-1333.md` | Verdict `APPROVE_FOR_USER_REVIEW`; four INFORMATIONAL non-actions surfaced for transparency. |

**No factual corrections were necessary.** Both plans, all six review-chain artifacts, and the working tree are internally consistent at `16724e9c7`. Per the prompt's "do not edit plans unless you find a clear factual bug" rule, no edits were made.

---

## (b) Still needs terminal fanout

These are the items that **cannot** be produced by this autofeed lane and therefore remain outstanding regardless of which approval path the user picks:

### B1 — Codex + Gemini cross-AI plan-review fanout (both plans)

**Why outstanding:** This autofeed lane is permission-gated per `feedback_permission_gate_blocks_cross_review.md`. Two specific blockers:

1. **codex-cli 0.124.0 stdin-hang regression** ([#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479)) — blocks `codex exec` on plans of any size from any sandbox. Memory rule: `feedback_codex_cli_0_124_upstream_regression.md`. Workaround: pin codex-cli to 0.123.0 in the terminal session.
2. **Gemini interactive permission grant + workspace-trust env** — `submit-to-gemini.sh` exits 55 in headless without `GEMINI_CLI_TRUST_WORKSPACE=true`. Memory rule: `feedback_gemini_trust_env_blocks_reviews.md`.

**Terminal command** (from an unsandboxed user terminal, after pinning codex-cli to 0.123.0 and exporting `GEMINI_CLI_TRUST_WORKSPACE=true`):

```bash
scripts/review/plan-review-fanout.sh \
  docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md
scripts/review/plan-review-fanout.sh \
  docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md
```

**Optional / not strictly required.** Both re-reviews note `feedback_permission_gate_blocks_cross_review.md` permits single-author transparent-provenance approval; fanout is only needed if the user wants higher-confidence verdicts before flipping the label. T1 (#2552) is precedent-supported for deferred-review path; T2 (#2550) is also acceptable single-author per the same memory rule, with the caveat that #2550 has a 5-month silent-failure horizon if the implementation breaks — fanout is a stronger fit for that issue if time permits.

### B2 — F9 implementation-design decision (#2550 only)

The patched plan preserves one Open question for user-at-approval: should `scripts/security/renew-interaction-limits.sh` invoke `scripts/notify.sh` on non-zero exit (matching `research-staleness` and `compliance-daily` precedent), or rely on a `>> $WORKSPACE_HUB/logs/security/...log` audit trail only?

**Plan recommendation embedded at L221:** wire `notify.sh`. Rationale: a 5-month-cadence security control that fails silently to a log no one reads is de-facto undefended; one extra line in the cron command removes that risk class.

**User authority:** confirm or override at approval-comment time. The decision needs to be recorded in the approval-marker and reflected in the implementation-phase script. No fanout addresses this — it is a Category B/C governance choice under `docs/governance/TRUST-ARCHITECTURE.md`.

### B3 — Approval-marker write + label flip (both plans)

Per `feedback_never_offer_to_self_label_plan_approved.md`, no autofeed lane (review, patch, re-review, or this synthesis) flips `status:plan-review` → `status:plan-approved` or writes `.planning/plan-approved/255{0,2}.md`. Both are user actions. Per `project_issue_2460_approval_binding.md`, the markers must be revision-bound to plan SHA `16724e9c7` (not the pre-patch draft SHA `2734c103b`). See §(c) below for paste-ready content.

---

## (c) Exact user action if both plans are acceptable

These instructions assume the user accepts the single-author Claude chain (T1 deferred-review path). If the user instead wants Codex+Gemini fanout, run §(b) B1 first, attach the resulting verdicts to each plan's Adversarial Review Summary section, and only then proceed below.

All commands below are user actions — none are auto-executed by this synthesis lane. They are sequenced (1 → 2 → 3 → 4) so that the marker SHA citation, the comment body, and the label flip can never disagree.

### Step 1 — record the F9 decision for #2550

Pick one of the two options below. The choice goes into the approval comment for #2550 and into the future implementation phase. (Plan recommendation: option A.)

- **Option A (recommended):** wire `scripts/notify.sh` on non-zero exit. Cron command becomes ` ... || /usr/bin/env bash $WORKSPACE_HUB/scripts/notify.sh "renew-interaction-limits FAIL"`.
- **Option B:** rely on log audit only. Cron command stays `... >> $WORKSPACE_HUB/logs/security/renew-interaction-limits.log 2>&1`. Operator commits to checking the log file each cycle.

### Step 2 — write approval markers (revision-bound)

```bash
cat > .planning/plan-approved/2550.md <<'EOF'
# Plan #2550 — approval marker

Plan path: docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md
Plan SHA at approval: 16724e9c7
Review chain (single-author Claude, sandbox-permitted):
  - docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md  (verdict: MINOR_PATCH_NEEDED)
  - docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2550-20260429-1310.md   (F1–F8 landed in plan SHA 16724e9c7)
  - docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2550-20260429-1333.md (verdict: APPROVE_FOR_USER_REVIEW)
F9 decision: <option A: wire notify.sh | option B: log-only>   # pick one before saving
Cross-provider fanout: <accepted single-author per feedback_permission_gate_blocks_cross_review.md | run before approval>
Storage surface: docs/plans/ + .planning/plan-approved/ + GitHub label
EOF
```

```bash
cat > .planning/plan-approved/2552.md <<'EOF'
# Plan #2552 — approval marker

Plan path: docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md
Plan SHA at approval: 16724e9c7
Review chain (single-author Claude, sandbox-permitted; T1 deferred-review path):
  - docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2552-20260429-1246.md  (verdict: MINOR_PATCH_NEEDED)
  - docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2552-20260429-1310.md   (F1–F6 + L1 + L3 landed in plan SHA 16724e9c7; L2 deferred)
  - docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2552-20260429-1333.md (verdict: APPROVE_FOR_USER_REVIEW)
Cross-provider fanout: <accepted single-author per feedback_permission_gate_blocks_cross_review.md | run before approval>
Storage surface: docs/plans/ + .planning/plan-approved/ + GitHub label
EOF
```

Commit both markers (single commit, message suggestion: `chore(approve): bind #2550 and #2552 plan approvals to 16724e9c7`).

### Step 3 — post bounded-scope approval comments + flip labels

Two paired commands per issue (comment first, then label). Per `feedback_gh_issue_close_silent_comment_drop.md` only the close-then-comment ordering breaks; for label-only flips with comments, this ordering is safe:

```bash
gh issue comment 2550 --body "$(cat <<'EOF'
Approving #2550 plan post-patches F1–F8.
Single-author Claude review: docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md
Patch lane:                 docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2550-20260429-1310.md
Cold-context re-review:     docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2550-20260429-1333.md (APPROVE_FOR_USER_REVIEW)
Plan SHA at approval: 16724e9c7
F9 decision: <wire notify.sh | log-only>
Cross-provider fanout: <accepted single-author per feedback_permission_gate_blocks_cross_review.md | ran before approval — see results above>
EOF
)"
gh issue edit 2550 --remove-label status:plan-review --add-label status:plan-approved

gh issue comment 2552 --body "$(cat <<'EOF'
Approving #2552 plan post-patches F1–F6 + L1 + L3 (T1 deferred-review path).
Single-author Claude review: docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2552-20260429-1246.md
Patch lane:                 docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2552-20260429-1310.md
Cold-context re-review:     docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2552-20260429-1333.md (APPROVE_FOR_USER_REVIEW)
Plan SHA at approval: 16724e9c7
Cross-provider fanout: <accepted single-author per feedback_permission_gate_blocks_cross_review.md | ran before approval — see results above>
EOF
)"
gh issue edit 2552 --remove-label status:plan-review --add-label status:plan-approved
```

### Step 4 — verify both gates landed

```bash
gh issue view 2550 --json labels --jq '[.labels[].name]'   # expect contains status:plan-approved, NOT status:plan-review
gh issue view 2552 --json labels --jq '[.labels[].name]'   # same
ls .planning/plan-approved/2550.md .planning/plan-approved/2552.md
git log -1 --pretty=oneline -- .planning/plan-approved/2550.md .planning/plan-approved/2552.md
```

After step 4 passes for both issues, the plans are eligible for executor pickup in a future implementation lane (separate prompt — not part of this packet).

---

## Files inspected

End-to-end reads (or full-section reads where the file exceeds 1k lines):

1. `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md` (post-patch, 230 lines).
2. `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` (post-patch, 181 lines).
3. `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2550-20260429-1246.md` (291 lines, MAJOR/MINOR/LOW analysis).
4. `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2552-20260429-1246.md` (137 lines, MINOR/LOW analysis).
5. `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2550-20260429-1310.md` (183 lines, F1–F8 mapping + diffstat verification).
6. `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2552-20260429-1310.md` (120 lines, F1–F6 + L1 + L3 mapping + diffstat verification).
7. `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2550-20260429-1333.md` (202 lines, `APPROVE_FOR_USER_REVIEW` + 6 LOW observations).
8. `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2552-20260429-1333.md` (131 lines, `APPROVE_FOR_USER_REVIEW` + 4 INFORMATIONAL).

Live reads (read-only):

9. `git log --oneline -5 -- docs/plans/2026-04-29-issue-255{0,2}-*.md` — confirms `16724e9c7 chore(sync): auto-sync 2026-04-29` absorbed both plan-patch deltas; no other commits since.
10. `git status --porcelain docs/plans/...255{0,2}-*.md` — clean working tree for both plan files.
11. `git show --stat 16724e9c7 -- docs/plans/...255{0,2}-*.md` — verifies the auto-sync commit captured both plan files (#2550: +51/-17 net; #2552: ~+37/-24 net per patch report, ~+35/-26 reported by `git show --stat`).
12. `gh issue view 255{0,2} --json number,state,labels` — confirms both OPEN with `status:plan-review`; no label drift since the 1333 re-review snapshots.
13. `ls .planning/plan-approved/255{0,2}.md` — confirms both markers absent; user-in-loop gate intact.

---

## Files changed

**None.** This synthesis lane wrote exactly one artifact: this readiness packet at the prescribed path. No plan edits, no GitHub mutation, no commit, no marker, no label change, no source/config/test/cron edit. Per the prompt's "do not edit plans unless you find a clear factual bug" rule, no factual bugs warranted a typo-level correction — the plans, reviews, patches, and re-reviews are internally consistent at SHA `16724e9c7`.

---

## Remaining blockers

None preventing user decision. Three items remain user-gated and are deliberately preserved:

1. **F9 implementation-design decision (#2550 only)** — wire `notify.sh` vs log-only audit. Plan recommendation: wire `notify.sh`. User picks at approval-comment time.
2. **Cross-provider fanout policy (both)** — accept single-author Claude chain per `feedback_permission_gate_blocks_cross_review.md`, OR run terminal-session `scripts/review/plan-review-fanout.sh` after pinning codex-cli to 0.123.0 and setting `GEMINI_CLI_TRUST_WORKSPACE=true`. Both paths are legitimate.
3. **Approval-marker write + GitHub label flip (both)** — user actions per `feedback_never_offer_to_self_label_plan_approved.md` and `project_issue_2460_approval_binding.md`.

No autofeed lane can resolve any of the three; surfacing them is the entire purpose of this packet.

---

## Next safe action

The user picks one of these branches:

- **Branch A (T1 deferred-review, fastest):** execute §(c) Steps 1 → 2 → 3 → 4 in order. Estimated time-on-task: 5–10 minutes. Plans become executor-eligible immediately after Step 4 verifies.
- **Branch B (full fanout, higher confidence):** execute §(b) B1 first from a terminal session; review the resulting Codex+Gemini verdicts; if both return MINOR-or-better, append the verdicts to each plan's Adversarial Review Summary section in a separate plan-text patch (not in this lane), then proceed to Branch A. Estimated time-on-task: 30–60 minutes including codex-cli 0.123.0 pin.
- **Branch C (defer):** take no action. Plans remain at `status:plan-review`. No risk to existing collaborators_only protection (Hermes cron `d9b2d1c2270d` continues to renew per the lockdown handoff). Re-evaluate at a future session.

This synthesis lane is not authorized to pick the branch.

---

## Boundary compliance

| Rule (from prompt) | Verification |
|---|---|
| Workspace = `/mnt/local-analysis/workspace-hub` | All operations relative to this path. |
| Bounded follow-up planning/review/synthesis only | This artifact is synthesis; no implementation, no plan edits, no GitHub mutation. |
| No `gh issue edit / comment / close` | Only `gh issue view --json` (read-only) executed. |
| No `status:plan-review` or `status:plan-approved` application | No label mutation invoked by this lane. |
| No `.planning/plan-approved/*` marker create or edit | Markers remain absent for both issues. |
| No outreach, no commit, no push | None invoked. |
| No production implementation | No script/config/test/cron/source edit. |
| Do not overwrite existing result path | Pre-write `ls` confirmed `nextwave-followup-readiness-2550-2552-20260429-r1.md` was unoccupied. |
| Re-read current files and live context before editing | Read 8 lane artifacts + 2 plans + live `gh issue view` + `git log/status/show` before writing. |
| Keep changes scoped to named issues/files | Single result artifact written; no plan edits. |
| Write primary result artifact at exactly the requested path | This file is at the exact path the prompt specified. |
| Do not edit plans unless clear factual bug | Confirmed: no factual bugs found across the four lane artifacts and two plan files at SHA `16724e9c7`. No edits made. |

Single-author provenance disclosure: this is a Claude-authored synthesis of a Claude-authored review chain. It is not a substitute for cross-AI fanout; B1 in §(b) is the only path to that. Self-approval check (per `feedback_never_offer_to_self_label_plan_approved.md`): this artifact does not pre-authorize any downstream agent or handoff to flip the label or write the marker — those steps are explicitly user actions in §(c) and are executable only in the user's own terminal session.

---

## Lane classification

**COMPLETED_WITH_RESULT.** Three buckets ((a) artifact-ready, (b) needs terminal fanout, (c) exact user action) populated for both [#2550](https://github.com/vamseeachanta/workspace-hub/issues/2550) and [#2552](https://github.com/vamseeachanta/workspace-hub/issues/2552). Re-review verdicts (`APPROVE_FOR_USER_REVIEW`) reaffirmed against live state at SHA `16724e9c7`. Zero plan edits, zero GitHub mutations, zero commits, zero markers. Exactly one artifact written at the prescribed path.
