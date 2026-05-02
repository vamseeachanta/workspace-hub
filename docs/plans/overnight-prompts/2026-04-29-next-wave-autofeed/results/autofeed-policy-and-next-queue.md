# Autofeed policy and next-queue — fix the run conveyor

> **Wave:** `2026-04-29-next-wave-autofeed`
> **Author:** ace-linux-1 control plane (Claude Opus 4.7, 1M ctx)
> **Date:** 2026-04-29 12:05 CDT (17:05 UTC)
> **Mission:** Produce a durable safe auto-feed policy and a 10-lane next-queue without unsafe autonomous approval/implementation.
> **Authorization boundary:** This artifact does NOT label, approve, close, comment on, or merge any issue. It does NOT create approval markers. It does NOT modify the cronjob. It is a paste-ready policy + prompt queue for the user / orchestrator.

---

## 1. Diagnosis — why the conveyor under-launched

### 1.1 What the cronjobs `3dae8266219b` and `5ae81116b608` do today (inferred)

Neither handle is in local `crontab -l` (verified via `crontab -l | grep -c 3dae8266219b` → 0). They are external scheduler handles — almost certainly `RemoteTrigger` / `/schedule` IDs registered against the user account, not workspace-hub cron entries. The only references to those handles in this repo are in the autofeed prompt itself (`autofeed-fix-and-queue.md`), so behavior must be inferred from the artifacts they have produced this wave:

| Handle | Inferred role (from artifacts produced) | Evidence |
|---|---|---|
| `3dae8266219b` | "Lane monitor" — periodic sweeper that classifies prior lanes as COMPLETED / RUNNING / BLOCKED and launches at most **one** follow-up per pass. | Pattern matches `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/lane-monitor-latest.md` row 18: "Launched exactly one bounded non-destructive follow-up this run." Sequential feed16→…→feed21 chain on #2374 over 7 hours is consistent with a one-launch-per-pass cadence. |
| `5ae81116b608` | "Wave dispatcher" — periodic launcher that consumes a per-wave prompt pack (e.g. `autofeed-fix-and-queue.md`, `approval-synthesis-10.md`, `gtm-review-2554-2555.md`, `gtm-review-2556-2557.md`) and tmux-launches each pack via `launch-local.sh` / `launch-ace2-remote.sh`. | At 11:55 CDT all four packs in this wave's `launch-local.sh` started at the same minute (`logs/night-runs/nextwave-{autofeed-fix,approval-synthesis,gtm-review-{a,b}}-20260429.log` all timestamped `Apr 29 11:55`, all 0-byte until claude finishes). |

If those role assumptions are wrong, the policy below still applies because it is keyed off **filesystem state** (result files, tmux session names, log byte counts) rather than cron internals.

### 1.2 Five concrete failure modes the current monitors hit

1. **One-launch-per-pass starvation.** The monitor's safety rule "launch exactly one safe follow-up per run" is correct for parallel-write isolation but pathologically slow when many distinct chains are eligible. The 12h continuation wave produced 21 feeds, but ~15 of them are on a single plan chain (`#2374` feed8→feed21). Other live `status:plan-review` candidates at the same time (`#2363`, `#2474`, `#2509`) got **zero** follow-up lanes. This is the dominant failure mode.

2. **Stale-review false-positive risk.** The 04:33 adversarial-readiness review treated `#2540`, `#2541`, `#2544` as `status:plan-review`. By 14:30Z the user had already moved them to `status:plan-approved` (`gh issue view 2540/2541/2544` confirms). Any monitor that reads `results/approval-pack-elements-2540-2544.md` or `adversarial-readiness-review.md` as ground-truth will recommend label flips that have already occurred → noisy `gh issue edit` retries, possible label-drift commits, and most dangerously a re-promote that erases the user's chosen scope-bounded wording.

3. **Completion classifier conflates "log-still-0-byte" with "still running".** The runner script at `run-claude-prompt.sh` line 10 pipes through `tee` which only flushes on stdout flush. `claude -p` emits its full text in a single late chunk, so the log file stays 0 bytes for ~30-40 min and then jumps to ~2-3 KB at the end. If the monitor's "RUNNING vs COMPLETED" decision rule is `[ -s "$log" ]` (non-empty), it is correct; if it is `wc -l > N`, it can momentarily lose track. The 4 nextwave-*.log files at 11:55 were 0-byte for the entire monitor pass that produced `lane-monitor-latest.md` at 07:44 (different wave, same shape).

4. **No queue file → every monitor pass re-derives "next lane" from scratch.** `next-dispatch-queue.md` is human-curated, written once per shift, and not consumed by the cronjob. The monitor therefore re-greps the entire `docs/plans/overnight-prompts/*/results/` tree every pass — fragile to typos in result filenames and prone to picking the same chain twice in a row when capacity opens up.

5. **No capacity ceiling.** The monitor doesn't track "max concurrent local sessions" or "max concurrent ace-linux-2 remote sessions". When `tmux ls` shows 0 active sessions the monitor launches one; when it shows N active sessions, the monitor still launches one (or skips). It has no concept of "we have 3 free slots, fill all 3." That asymmetry is the second-biggest source of starvation.

Together: failures 1 and 5 cause under-launch when capacity is free; failure 2 risks dangerous redundant action; failures 3 and 4 cause occasional double-spawn or skipped chains. The new policy below addresses all five.

---

## 2. Current run inventory (live, 2026-04-29 12:05 CDT)

### 2.1 Currently running this wave (ace-linux-1)

| tmux session | Prompt | Log | Result expected at | Status |
|---|---|---|---|---|
| `nextwave-gtm-review-a-20260429` | `gtm-review-2554-2555.md` | `logs/night-runs/nextwave-gtm-review-a-20260429.log` (0 byte) | `results/gtm-review-2554-2555.md` | RUNNING (started 11:55) |
| `nextwave-gtm-review-b-20260429` | `gtm-review-2556-2557.md` | `logs/night-runs/nextwave-gtm-review-b-20260429.log` (0 byte) | `results/gtm-review-2556-2557.md` | RUNNING (started 11:55) |
| `nextwave-approval-synthesis-20260429` | `approval-synthesis-10.md` | `logs/night-runs/nextwave-approval-synthesis-20260429.log` (0 byte) | `results/approval-synthesis-10.md` | RUNNING (started 11:55) |
| `nextwave-autofeed-fix-20260429` | `autofeed-fix-and-queue.md` (this lane) | `logs/night-runs/nextwave-autofeed-fix-20260429.log` (0 byte until finish) | `results/autofeed-policy-and-next-queue.md` (this file) + `generated/safe-autofeed-cron-prompt.md` | RUNNING — **this artifact** |

### 2.2 Currently dispatched on ace-linux-2 (per `launch-ace2-remote.sh`)

| Remote tmux session | Prompt | Result expected at |
|---|---|---|
| `nextwave-ace2-blocker-prep-20260429` | `ace2-blocker-prep.md` | `results/ace2-blocker-prep.md` |
| `nextwave-ace2-approved-scout-20260429` | `ace2-approved-scout.md` | `results/ace2-approved-scout.md` |

These were not directly verified from this lane (avoided ssh probe to keep this artifact filesystem-only). The dispatcher at `launch-ace2-remote.sh` line 16-20 does check `tmux has-session -t "$session"` before launching, so a re-dispatch is idempotent.

### 2.3 Last 24 hours of finished result artifacts (most-recent first)

From `ls -lt logs/night-runs/ | head -25`:

| Lane | Log size | Finished | Result artifact | Verdict (from artifact) |
|---|---:|---|---|---|
| ace1-plan-crossreview-readiness-2374-feed21 | 2300 | 09:29 CDT | `results/ace1-plan-crossreview-readiness-2374-feed21.md` | **READY_FOR_CROSS_REVIEW** (Claude only) |
| ace1-plan-micropatch-2374-feed20 | 2052 | 08:54 CDT | `results/ace1-plan-micropatch-2374-feed20.md` | COMPLETED_WITH_RESULT |
| ace1-plan-rereview-2374-feed19 | 2548 | 08:22 CDT | `results/ace1-plan-rereview-2374-feed19.md` | APPROVE_FOR_CROSS_REVIEW |
| ace1-plan-patch-2374-feed18 | 2782 | 07:48 CDT | `results/ace1-plan-patch-2374-feed18.md` | COMPLETED_WITH_RESULT |
| ace1-plan-review-2374-feed17 | 2452 | 07:17 CDT | `results/ace1-plan-review-2374-feed17.md` | MINOR (3 patches) |
| ace1-plan-patch-2374-feed16 | 2278 | 06:41 CDT | `results/ace1-plan-patch-2374-feed16.md` | COMPLETED_WITH_RESULT |
| ace1-plan-patch-2375-feed15 | 2659 | 05:35 CDT | `results/ace1-plan-patch-2375-feed15.md` | COMPLETED_WITH_RESULT |
| ace1-plan-review-2375-feed14 | 2590 | 05:02 CDT | `scripts/review/results/2026-04-29-plan-2375-claude-feed14.md` | (review artifact) |
| ace1-codex-readiness-review | 13527 | 04:58 CDT | `results/adversarial-readiness-review.md` | 0/14 promotion-ready (now stale: see 2.4) |
| weekly-gtm-2554/2555/2556 + weekly-productivity-2557 | ~3KB each | 10:23-10:29 CDT | `docs/reports/gtm/...` + plans `docs/plans/2026-04-29-issue-255{4,5,6,7}-*` | Plans drafted, not in `status:plan-review` |

### 2.4 Live GitHub state (queried at 17:05 UTC)

| Issue | State | Labels (live) | Plan path | Notes |
|---:|---|---|---|---|
| #2540 | OPEN | `status:plan-approved` (changed 14:30Z) | epic, no plan file | Promoted; awaits children execution |
| #2541 | OPEN | `status:plan-approved` (14:31Z) | `docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md` | Promoted with bounded SESA wording |
| #2542 | CLOSED | `status:done` | (already executed `b0dac4608`) | DONE |
| #2543 | CLOSED | `status:done` | (already executed `b0dac4608`) | DONE |
| #2544 | OPEN | `status:plan-approved` (14:30Z) | `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md` | Promoted with pointer/scout-only wording |
| #2490 | OPEN | `status:plan-approved` | `docs/plans/2026-04-27-issue-2490-coverage-gate-fix.md` | T1 deferred-review path approved |
| #2510 | OPEN | `status:plan-approved` | `docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md` | Approved despite sustained-MAJOR loop |
| #2538 | OPEN | priority:medium, no `status:plan-review` | (none) | NEEDS_PLAN |
| #2370 | OPEN | no `status:plan-review` | `docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md` | Single-provider review only |
| #2374 | OPEN | no `status:plan-review` | `docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md` | feed21 = READY_FOR_CROSS_REVIEW |
| #2375 | OPEN | no `status:plan-review` | `docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md` | Plan now committed (`c89b…` series); needs cross-review |
| #2378 | OPEN | no `status:plan-review` | `docs/plans/2026-04-28-issue-2378-plan-draft.md` | Single-provider MINOR; needs Codex/Gemini |
| #2363 | OPEN | no `status:plan-review` | `docs/plans/2026-04-26-issue-2363-wiki-refs-reverse-lookup.md` | Claude r1 = MAJOR unanswered |
| #2474 | OPEN | no `status:plan-review` | `docs/plans/2026-04-26-issue-2474-orcaflex-reverse-parser.md` | Claude r1 = MAJOR unanswered |
| #2509 | OPEN | no `status:plan-review` | `docs/plans/2026-04-26-issue-2509-openlane-rtl-to-gds-demo.md` | Stub-only reviews; needs first real fanout |
| #2550 | OPEN | `status:plan-review` | `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md` | Fresh draft; no review yet |
| #2552 | OPEN | `status:plan-review` | `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` | Fresh draft; no review yet |
| #2554 | OPEN | priority:high, cat:business, no `status:plan-review` | `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md` | Weekly GTM plan — review running NOW (lane gtm-review-a) |
| #2555 | OPEN | priority:high, cat:business, no `status:plan-review` | `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md` | Weekly GTM plan — review running NOW (lane gtm-review-a) |
| #2556 | OPEN | priority:high, cat:business, no `status:plan-review` | `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` | Weekly GTM plan — review running NOW (lane gtm-review-b) |
| #2557 | OPEN | priority:high, cat:ai-orchestration, no `status:plan-review` | `docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md` | Weekly GTM plan — review running NOW (lane gtm-review-b) |

The only currently `status:plan-review` issues live are **#2550** and **#2552** — both fresh today, no cross-review evidence yet. **All** of #2540, #2541, #2544, #2490, #2510 are already past `status:plan-review` into `status:plan-approved`; that's a major shift versus the 04:33 review's snapshot.

---

## 3. Completion classifier (deterministic, filesystem-only)

A lane is classified by reading three signals — tmux session, log file, expected result artifact path — in this order:

```
def classify(lane_session, log_path, result_path):
    if tmux_has_session(lane_session):
        # session still alive: trust tmux over log emptiness
        return "RUNNING"
    if not exists(log_path):
        return "NEVER_STARTED"
    log_size = size(log_path)
    if not exists(result_path):
        if log_size == 0:
            return "ABORTED_NO_OUTPUT"   # session died without ever flushing
        if log_size < 200:
            return "ABORTED_EARLY"       # crash trace or "permission denied"
        return "FAILED_NO_RESULT"        # ran but did not write the expected file
    # result file exists
    result_size = size(result_path)
    if result_size < 200:
        return "STUB_RESULT"             # placeholder, almost certainly an aborted write
    return "COMPLETED_WITH_RESULT"
```

**Why three signals, not just `[ -s "$log" ]`:** the runner pipes through `tee` and `claude -p` flushes once at the end, so log emptiness during a run is the rule, not the exception. Tmux-presence is the only reliable RUNNING signal; result-file-presence is the only reliable COMPLETED signal. Log size is the tiebreaker for failure modes.

**Stale-process guard:** if `tmux_has_session` returns true AND log mtime is older than 90 minutes AND log size is still 0 bytes, classify as `STALE_RUNNING` and require human inspection before relaunch. This is the safety net for the codex-cli 0.124 stdin-hang regression and the Hermes preflight contention pattern.

---

## 4. Safe auto-spawn transitions

The cronjob may launch a follow-up lane **only** when ALL of the following are true:

1. The follow-up's tmux session name is unique (no live `tmux has-session` collision).
2. The follow-up's prompt file is in this wave's `generated/` dir, is git-tracked, and is < 200 KB.
3. The follow-up's expected result file does not yet exist (no overwrite).
4. Current local active session count < `MAX_LOCAL_LANES` (default 3) **or** current ace-linux-2 active session count < `MAX_REMOTE_LANES` (default 2). The cronjob picks the host with capacity.
5. The trigger condition for the follow-up is met. Allowed triggers:

| Trigger | Allowed follow-up |
|---|---|
| Plan exists, no cross-review artifact for it today | Plan-only adversarial review (Claude lane) writing to `scripts/review/results/2026-04-29-plan-NNNN-claude-rN.md` |
| Plan-only Claude review = MINOR with named patch list | Plan-only patch lane writing back to plan file (dry edit) and `results/ace1-plan-patch-NNNN-feedX.md` |
| Plan-only Claude review = MAJOR | Block, write blocker note `results/ace1-plan-blocker-NNNN-feedX.md`; do NOT auto-cycle (per `feedback_codex_sustained_major_loop.md` if 3+ MAJOR rounds) |
| Plan-only patch landed | Cold-context re-review by Claude (different feed number) |
| Cold-context re-review = APPROVE_FOR_CROSS_REVIEW | Cross-review readiness packet (paste-ready operator commands; no fanout execution) |
| Result artifact `gtm-review-*.md` lands | Inline-comment draft pack at `generated/<issue>-gh-comment-pack.md` (no `gh` execution) |
| Result artifact `approval-synthesis-10.md` lands | Per-issue verify-and-prep packet at `generated/<issue>-verify-pack.md` (read-only verification commands) |
| ace-linux-2 blocker prep lands a row classified `BLOCKED_RESOURCE` | Inline blocker comment draft (no execution) |

Each follow-up writes:
- **Exactly one** primary result file under this wave's `results/`.
- **Optionally one** review artifact under `scripts/review/results/<date>-plan-NNNN-<provider>-<rN|feedX>.md`.

That's it. Anything else is unsafe.

---

## 5. Unsafe transitions — require user approval, never auto-spawn

The cronjob must NOT launch any of the following without an explicit, user-typed token (e.g. an `.approved` marker file with a fresh SHA per `#2460`). All of these are silently destructive when wrong.

1. **`gh issue edit … --add-label status:plan-approved`** on any issue. Per `feedback_never_offer_to_self_label_plan_approved.md` this is the load-bearing user-in-loop gate.
2. **`gh issue close`** or **`--remove-label status:done`** on any issue. The 09:45Z close of #2542/#2543 was operator-driven; agents must not move issues past the executed state.
3. **`gh issue comment`** on any public-facing issue (GTM, security runbook, partner work). Drafts to `generated/*.md` only.
4. **`gh pr create`**, **`gh pr merge`**, **`gh pr review --approve`**, or any PR mutation.
5. **`git push`** to any non-`workspace-hub` remote, or **`git push --force`** to anything.
6. **`scripts/review/plan-review-fanout.sh`** — invokes Codex and Gemini CLIs which spend external credits and (per `feedback_codex_cli_0_124_upstream_regression.md`) may stdin-hang. Run only on operator command.
7. **Any write to `digitalmodel/`, `assethold/`, `worldenergydata/`, `frontierdeepwater/`, `ai-orchestrator-template/`** sub-repos.
8. **Any mutation to `.planning/plan-approved/*` markers.** Approval marker creation is human-only.
9. **Implementation lanes** — anything that edits source files referenced by an issue plan, even if the issue is `status:plan-approved`. Implementation requires the marker file AND the operator's authorization-bound sequence (`#2460` revision-bound contract).
10. **Outreach** — any email send, Slack message, or external network call to an operator-uncontrolled endpoint.
11. **`hermes` invocations** that mutate state. Inspect-only is OK.
12. **codex-cli or gemini-cli direct invocations.** Both have known sandbox/regression failure modes that must be supervised.

Any cron pass that detects one of these conditions in its candidate queue must skip that candidate and emit a `results/<date>-cron-skipped-<reason>.md` row instead.

---

## 6. Next 10-lane queue (priority-ordered, bounded, plan-only)

All 10 are plan-only / review-only / synthesis-only. None require user approval to launch (only #6 and #7 produce output that the user reviews before any mutation). All are safe under the rules in §4 / §5.

| # | Priority | Trigger condition | Generated prompt file | Result artifact | Lane host | Est. runtime |
|---:|---:|---|---|---|---|---:|
| 1 | P0 | live `gh issue list --label status:plan-review` returns #2550 with no review artifact for today | `generated/ace1-plan-review-2550-feed1.md` | `scripts/review/results/2026-04-29-plan-2550-claude-r1.md` + `results/ace1-plan-review-2550-feed1.md` | ace-linux-1 | ~30 min |
| 2 | P0 | same condition for #2552 | `generated/ace1-plan-review-2552-feed1.md` | `scripts/review/results/2026-04-29-plan-2552-claude-r1.md` + `results/ace1-plan-review-2552-feed1.md` | ace-linux-1 | ~30 min |
| 3 | P0 | `results/gtm-review-2554-2555.md` lands AND review verdict ≠ MAJOR | `generated/ace1-gtm-comment-pack-2554-2555.md` | `generated/2554-gh-comment-pack.md`, `generated/2555-gh-comment-pack.md`, `results/ace1-gtm-comment-pack-2554-2555.md` | ace-linux-1 | ~20 min |
| 4 | P0 | `results/gtm-review-2556-2557.md` lands AND review verdict ≠ MAJOR | `generated/ace1-gtm-comment-pack-2556-2557.md` | `generated/2556-gh-comment-pack.md`, `generated/2557-gh-comment-pack.md`, `results/ace1-gtm-comment-pack-2556-2557.md` | ace-linux-1 | ~20 min |
| 5 | P1 | `results/approval-synthesis-10.md` lands | `generated/ace1-approval-verify-pack.md` | `generated/approval-verify-pack.md` (per-issue verification commands), `results/ace1-approval-verify-pack.md` | ace-linux-1 | ~25 min |
| 6 | P1 | feed21 readiness packet exists for #2374 AND no `2026-04-29-plan-2374-claude.md` final | `generated/ace1-plan-final-claude-2374.md` | `scripts/review/results/2026-04-29-plan-2374-claude-final.md` + `results/ace1-plan-final-claude-2374.md` | ace-linux-1 | ~35 min |
| 7 | P1 | live #2375 plan is committed AND no review artifact today | `generated/ace1-plan-review-2375-feed16.md` | `scripts/review/results/2026-04-29-plan-2375-claude-feed16.md` + `results/ace1-plan-review-2375-feed16.md` | ace-linux-1 | ~30 min |
| 8 | P2 | #2378 plan exists AND no Codex/Gemini review of post-feed5 plan AND no Claude re-review since feed5 | `generated/ace1-plan-rereview-2378-feed7.md` | `scripts/review/results/2026-04-29-plan-2378-claude-feed7.md` + `results/ace1-plan-rereview-2378-feed7.md` | ace-linux-1 | ~30 min |
| 9 | P2 | #2363 has open Claude r1 MAJOR unanswered AND no patch lane today | `generated/ace1-plan-patch-2363-feed1.md` | `results/ace1-plan-patch-2363-feed1.md` (patch proposal only — no plan rewrite without user OK) | ace-linux-2 | ~30 min |
| 10 | P2 | #2474 has open Claude r1 MAJOR unanswered AND no patch lane today | `generated/ace2-plan-patch-2474-feed1.md` | `results/ace2-plan-patch-2474-feed1.md` (patch proposal only) | ace-linux-2 | ~30 min |

Optional fill-in lanes 11/12 if capacity remains after 1-10:

| 11 | P3 | `ace2-blocker-prep.md` lands AND any row marks `BLOCKED_RESOURCE` for #2509 stub-reviews | `generated/ace2-plan-review-2509-feed1.md` | `scripts/review/results/2026-04-29-plan-2509-claude-r1.md` + `results/ace2-plan-review-2509-feed1.md` | ace-linux-2 | ~30 min |
| 12 | P3 | #2538 has no plan AND has been open ≥ 3 days | `generated/ace1-plan-skeleton-2538.md` | `docs/plans/2026-04-29-issue-2538-skeleton-DRAFT.md` + `results/ace1-plan-skeleton-2538.md` | ace-linux-1 | ~30 min |

**Why 10 (not "as many as possible"):** the local capacity ceiling is 3 concurrent Claude lanes (the box is shared with Hermes loops, the auto-sync cron, and interactive sessions). With 35-min average lane runtime and 3 slots, the conveyor can process ~5 lanes/hour. 10 priority-ordered lanes is ~2 hours of free-feed work — enough to cover one autofeed-pass + one operator review window without producing a backlog the operator cannot inspect. P3 lanes 11-12 absorb residual capacity if any P0-P2 trigger fails to fire.

**Note on the prompt files:** each `generated/<lane>.md` listed above is **not yet written** in this artifact — by design. The cron prompt in §8 will draft each one on the fly when its trigger fires, using the §7 prompt template. That keeps the queue self-healing: if live state changes (e.g. user promotes #2550 to `status:plan-approved` before its review fires), the cron skips the stale lane.

---

## 7. Standard prompt template for each lane

Every lane in §6 uses the same structural template, which embeds all guardrails inline so a fresh Claude session running headless never loses them.

```
Global rules for this autofeed worker:
- Workspace: /mnt/local-analysis/workspace-hub.
- Treat ace-linux-1 as the control plane; ace-linux-2 is overflow only.
- Do not send outreach. Do not expose private contact details. Do not hardcode or print secrets.
- Do not apply status:plan-approved. User approval is required.
- Do not run gh issue edit, gh issue close, gh issue comment, gh pr *,
  scripts/review/plan-review-fanout.sh, or any codex/gemini CLI invocation.
- Implementation/code changes are forbidden unless a live issue is status:plan-approved
  AND a local approval marker exists at .planning/plan-approved/<issue>.md;
  this lane is planning/review/synthesis only.
- Write exactly one primary result artifact in
  docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/<expected-name>.md
  plus any review artifacts explicitly named below.
- Before trusting stale context, re-check live issue labels/state with
  gh issue view <N> --json state,labels,updatedAt
- Run a legal sanity scan on any public-facing GTM/data artifact before commit.

Task: <one-line description>

Inputs to read first:
- <plan path>
- <prior result artifact paths>
- <relevant memory feedback files>

Do:
1. <step-by-step, no implementation, no GitHub mutation>
2. <produce verdict in {APPROVE_FOR_CROSS_REVIEW, MINOR_PATCH_NEEDED,
   MAJOR_PATCH_NEEDED, BLOCKED}>
3. Write <result file path>.

Hard guardrails:
- Do NOT mutate GitHub.
- Do NOT create or edit .planning/plan-approved/* markers.
- Do NOT overwrite other lanes' result files.
- Do NOT run plan-review-fanout.sh.
- If evidence is insufficient, write a blocker note and stop.

End with explicit lane classification.
```

The cron prompt in §8 produces a complete ready-to-tmux-launch file matching this template for each fired trigger.

---

## 8. Exact cronjob update recommendation

The orchestrator should re-register the two scheduler handles as follows. **The orchestrator runs these — this lane does not.**

### `5ae81116b608` — wave dispatcher (every 30 min, business hours; every 60 min off-hours)

- **Cadence:** `*/30 13-23 * * *` UTC (08:00-18:00 CDT business hours), `0 0-12,23 * * *` UTC otherwise.
- **Stop condition:** any `.planning/cron-stop.flag` file existing in the workspace causes the cronjob to write `results/<date>-cron-stopped.md` and exit 0 without launching.
- **Action:** invoke `bash $WAVE_DIR/launch-local.sh` and `bash $WAVE_DIR/launch-ace2-remote.sh` where `$WAVE_DIR` is the active wave's directory. Idempotent because the launch scripts already check `tmux has-session`.
- **Kill switch:** if `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'` returns non-empty (Hermes active), defer dispatch by writing `results/<date>-cron-deferred-hermes.md` and exit 0.

### `3dae8266219b` — autofeed cron (every 20 min)

- **Cadence:** `*/20 * * * *` UTC.
- **Action:** `bash $ROOT/scripts/cron/run-claude-prompt.sh $ROOT/docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/safe-autofeed-cron-prompt.md $ROOT/logs/night-runs/safe-autofeed-cron-$(date +\%Y\%m\%d-\%H\%M).log acceptEdits`.
  Note: each fire produces a unique log file (timestamp-suffixed) so concurrent fires don't truncate each other.
- **Lock:** `flock -n /tmp/safe-autofeed-cron.lock` wrapper so only one autofeed pass runs at a time.
- **Stop condition:** same `.planning/cron-stop.flag` short-circuit.

### Both jobs

- Run from `/mnt/local-analysis/workspace-hub` (the autofeed cron prompt re-asserts this in its first line).
- Inherit the workspace-level PATH (already a hardening step landed in `5829db53e fix(orchestration): set PATH for remote next-wave runner`).
- Append, not truncate, any aggregate log file.

The orchestrator should diff the existing `3dae8266219b` and `5ae81116b608` definitions against the above and update only what diverges.

---

## 9. Operator manual checklist (paste-ready)

```bash
# 1. Verify current state matches what this artifact expects
gh issue list --state open --label status:plan-review --json number --jq '.[].number'
ls -la /mnt/local-analysis/workspace-hub/logs/night-runs/nextwave-*.log
tmux ls 2>/dev/null | grep nextwave-

# 2. Verify the cron prompt exists and is git-tracked
git ls-files --error-unmatch \
  docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/safe-autofeed-cron-prompt.md

# 3. Manual test of one autofeed pass (no commit, no GitHub)
bash docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/run-claude-prompt.sh \
  docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/safe-autofeed-cron-prompt.md \
  /tmp/safe-autofeed-test-$(date +%H%M).log acceptEdits

# 4. After review, register/update the cron handles
#    (use whatever scheduler surface the orchestrator uses — RemoteTrigger /
#     /schedule / external cron — to match §8 exactly).
```

---

## 10. Provenance

- Live `gh issue view` for #2540, #2541, #2542, #2543, #2544, #2490, #2510, #2370, #2374, #2375, #2378, #2363, #2474, #2509, #2538, #2550, #2552, #2554, #2555, #2556, #2557 at 17:05 UTC.
- `crontab -l` (no entries match the two scheduler handles).
- `tmux ls` blocked by sandbox; classifier compensates with filesystem signals.
- File listings: `logs/night-runs/`, `docs/plans/overnight-prompts/2026-04-{28,29}-*/results/`, `scripts/review/results/`.
- Memory feedback files referenced inline by tag (`feedback_never_offer_to_self_label_plan_approved.md`, `feedback_codex_sustained_major_loop.md`, `feedback_codex_cli_0_124_upstream_regression.md`, `feedback_hermes_active_preflight_check.md`, `feedback_queue_git_tracked.md`, `feedback_attestation_enables_contradiction_detection.md`).

## 11. Boundary compliance statement

- Did NOT commit, push, or mutate git state from this lane (the operator decides whether to commit the artifacts produced).
- Did NOT execute `plan-review-fanout.sh` or any provider CLI.
- Did NOT mutate GitHub: no `gh issue comment`, labels, PRs, closes, merges.
- Did NOT create or edit `.planning/plan-approved/*` markers.
- Did NOT register, update, or remove any cronjob.
- Did NOT implement code or launch tests.
- Wrote exactly two artifacts: this file and `generated/safe-autofeed-cron-prompt.md`.
