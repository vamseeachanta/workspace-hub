# Plan-approved queue audit — 2026-04-30 (Claude lane, ace-linux-1)

> **Mode:** plan/read-only. No GitHub label mutations. No issue closes. No process kills. No cleanup of dirty files.
> **Capacity context:** ~40% Claude weekly remaining, ~36 h to reset.
> **Repo:** `/mnt/local-analysis/workspace-hub` @ `main` (32 open issues with `status:plan-approved`).

## Context

Operator asked for the next 6 safest Claude-capacity execution candidates from the open `status:plan-approved` queue, plus already-done verification-close candidates and blocked candidates. This audit was triggered by capacity that is finite this week and a recurring approval-binding hazard ([memory: `feedback_issue_2460_approval_binding.md`](https://github.com/vamseeachanta/workspace-hub/issues/2460)) where label state and durable marker state diverge.

## Method (read-only evidence sources)

1. `gh issue list --label "status:plan-approved" --state open --limit 100` → 32 issues.
2. Per-candidate cross-check of three independent surfaces:
   - **Plan body status field** in `docs/plans/<date>-issue-<n>-…md`.
   - **Latest issue-thread author comment** (ground truth — frequently contradicts label).
   - **Local approval marker** at `.planning/plan-approved/<n>.md` (revision-bound per #2460 rule).
3. Contention scan via labels: `status:working`, `agent:codex`, `agent:claude`, `machine:*`, `wip:ace-linux-1`, `status:blocked`, `status:needs-data`, `dark-intelligence`.
4. Job-queue surface (`queue/pending/`) is empty — no validation jobs in flight.

## Headline finding (load-bearing)

**The label `status:plan-approved` is currently unreliable in this queue.** Of the 7 issues that pass the easy filters (no `status:working`, no `status:blocked`, no `status:needs-data`):

| # | Marker file present? | Plan body status | Latest author comment |
|---|---|---|---|
| 2544 | ❌ | `plan-review` | "remains `status:plan-review` pending …" (2026-04-29 09:35) |
| 2541 | ❌ | `plan-review` | "remains `status:plan-review` pending …" (2026-04-29 09:35) |
| 2540 | ❌ | umbrella | "Execution complete — #2543 + #2542" (2026-04-29 09:45) |
| 2510 | ❌ | `plan-review` (r13) | "still **not approval-ready**; implementation remains blocked" (2026-04-27 10:36) |
| 2490 | ❌ | `draft` | only comment is "Plan draft — 2026-04-27" |
| 2227 | ✅ `b77bdd038` | approved (Branch B only) | Branch B already executed by Codex 2026-04-27; content sub-gate FAIL as designed |
| 2112 | ✅ live-instruction | active | Checkpoint artifact `624c87f12` landed 2026-04-29 18:06 |

→ **Only #2112 passes all three gates as still-executable. #2227 is approval-scope-complete (verification-close).**

## Recommendations — top 6 candidates for Claude capacity

### 1. **#2112 — finish + verify SubseaIQ backfill** (HIGHEST CONFIDENCE)

- **URL:** https://github.com/vamseeachanta/workspace-hub/issues/2112
- **Labels:** `enhancement, priority:high, cat:engineering, agent:claude, status:plan-approved`
- **Plan:** none yet on disk (issue body + comment thread acts as the plan).
- **Marker:** `.planning/plan-approved/2112.md` — "Approved by: user live instruction on 2026-04-29".
- **State:** in flight on this lane. Checkpoint commit `624c87f12` already produced `data/field-development/gom-field-development-unblock-2112.json`, `docs/reports/field-development-unblock-2112.md`, and `scripts/knowledge/tests/test_field_…`. Final gates remain.
- **Why safe:** sole `agent:claude`, no machine tag, no Codex contention, online research only (no Elements/Win surfaces).
- **Bounded tests:** `scripts/knowledge/tests/test_field_*` — already wired in checkpoint.
- **Execution prompt snippet:**
  ```
  Resume #2112 SubseaIQ backfill. Marker scope: ≥10 GoM fields with provenance-backed equipment counts to unblock #2055.
  Verify gate: `uv run pytest scripts/knowledge/tests/test_field_development_unblock_2112.py`
  Then post a closing comment on #2112 with: row count, schema diff vs. data/field-development/subseaiq-scan-latest.json,
  unblocker hand-off to #2055. Do NOT close #2112; do NOT touch #2055 labels.
  ```

### 2. **#2490 — digitalmodel coverage-gate structural blocker** (T1, low-risk)

- **URL:** https://github.com/vamseeachanta/workspace-hub/issues/2490
- **Labels:** `enhancement, priority:medium, cat:infrastructure, status:plan-approved`
- **Plan:** `docs/plans/2026-04-27-issue-2490-coverage-gate-fix.md` (T1, body status `draft`).
- **Marker:** ❌ **MISSING.** Single comment is the plan draft itself. T1 review-waiver is the implicit justification, but no revision-bound marker.
- **Risk:** label-only approval; no commit-bound marker. Mitigated by T1 scope (one `--cov` flag in `digitalmodel/.claude/quality-gates.yaml` line 10 + a smoke test).
- **Why included anyway:** smallest blast radius of any open candidate; the change is one YAML line and one test that confirms `coverage.json` lands. Easy to revert.
- **Execution prompt snippet:**
  ```
  Implement #2490 per docs/plans/2026-04-27-issue-2490-coverage-gate-fix.md.
  TDD: write a failing test in digitalmodel that asserts `_execute_coverage_gate()` returns OK when --cov is on.
  Edit digitalmodel/.claude/quality-gates.yaml line 10 to append `--cov=src --cov-report=json:coverage.json`.
  Re-run quality_gates locally; confirm overall_status flips ERROR→PASS. Single PR; no scope creep.
  Before commit: ALSO write `.planning/plan-approved/2490.md` with revision-bound marker per #2460.
  ```
  → **Recommend the operator add the missing marker themselves before this lane executes.**

### 3. **#2227 — verification-close (NOT a re-execute)**

- **URL:** https://github.com/vamseeachanta/workspace-hub/issues/2227
- **Labels:** `enhancement, priority:medium, cat:documentation, agent:codex, status:plan-approved`
- **Plan:** `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md`.
- **Marker:** `.planning/plan-approved/2227.md` — revision-bound to `b77bdd038`, **scope = Branch B only** ("execute v5 Branch B when OCIMF preview content gate fails; do not write wiki pages under Branch B").
- **State:** Branch B already executed 2026-04-27 in Codex burn lane (`b7f7225693d`). Content sub-gate FAILED as designed. Per the marker, the approved scope is satisfied. Upstream #2471 has since CLOSED (`status:done`); #2521 landed an OCIMF Tandem preview/summary artifact (2026-04-29 17:30) that *could* unblock Branch A — but **Branch A is outside the marker scope**, so it requires a fresh approval round before any wiki page can be written.
- **Recommendation:** Claude lane should **not** execute Branch A. Instead, post a verification-close comment that summarises Branch B completion + new #2521 unblock + the need for a v6 plan / fresh approval to attempt Branch A.
- **Caveat:** `agent:codex` label means Codex is the named-author; coordinate before Claude touches the issue.

### 4. **#2540 — umbrella verification-close (re-scope down)**

- **URL:** https://github.com/vamseeachanta/workspace-hub/issues/2540
- **Labels:** `priority:high, cat:data-pipeline, domain:knowledge-management, status:plan-approved`
- **Plan:** none on disk; the umbrella body declares "does NOT authorize broad raw-data extraction".
- **Marker:** ❌ missing.
- **State:** bounded children #2542 and #2543 executed and merged (`b0dac4608`, 2026-04-29 09:45). Outstanding child issues are #2541 and #2544 — both contradict their `status:plan-approved` label per latest comment. Per the umbrella's own scope, the approved part is done.
- **Recommendation:** Claude lane should add a single comment summarising "umbrella's bounded mandate satisfied via #2542/#2543; #2541/#2544 are sub-children whose label state is being audited (see #2541/#2544 below)." **Do not close** (operator instruction); do not mutate labels (operator instruction).

### 5. **#2541 — surface label/state mismatch for operator action** (DO NOT EXECUTE)

- **URL:** https://github.com/vamseeachanta/workspace-hub/issues/2541
- **Labels:** `priority:medium, cat:data-pipeline, domain:marine, domain:knowledge-management, status:plan-approved`
- **Plan:** `docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md` (body status `plan-review`).
- **Marker:** ❌ missing.
- **Latest author comment (2026-04-29):** "Issue remains `status:plan-review` pending …". The label and the most-recent comment disagree.
- **Recommendation:** Claude lane should comment-only: cite the contradiction + ask the operator whether the label was set intentionally or carried forward from the overnight wave by mistake. Do not mutate labels (operator instruction). Do not start execution.

### 6. **#2544 — surface label/state mismatch for operator action** (DO NOT EXECUTE)

- **URL:** https://github.com/vamseeachanta/workspace-hub/issues/2544
- **Labels:** `priority:medium, cat:data-pipeline, domain:marine, domain:knowledge-management, status:plan-approved`
- **Plan:** `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md` (body status `plan-review`).
- **Marker:** ❌ missing.
- **Latest author comment (2026-04-29):** "remains `status:plan-review` pending …".
- **Recommendation:** same comment-only treatment as #2541. Bundle the comment for #2541 + #2544 into a single operator question if they were both labelled in the same overnight pass.

> **NOTE on slot 5/6:** I deliberately did NOT pick a riskier execute-candidate to fill slot 5/6. Picking either #2541 or #2544 to execute against the contradictory label would re-create the #2460 binding-failure incident. The honest top-6 has only **two execute-this-week** picks (#2112, #2490 with marker fix) and **two verification-close** picks (#2227, #2540), with the remaining two slots used to surface the broken label state instead of consuming it.

## Already-done / verification-close candidates

| # | Why "done" | Action for Claude lane |
|---|---|---|
| #2227 | Branch B executed 2026-04-27 (`b7f7225693d`). Content sub-gate FAIL is the documented expected outcome under marker scope. | Post Branch-B-complete comment; flag Branch A as new-approval-round (not auto-executable). |
| #2540 | Bounded children #2542/#2543 merged 2026-04-29 (`b0dac4608`). | Comment-only; do not close (operator instruction). |
| #2112 | Online-research checkpoint commit `624c87f12` lands the unblocker dataset. | Finalize remaining gates (above) and post the unblock summary on #2055. |

## Blocked candidates (with reason)

| # | Block reason | Evidence |
|---|---|---|
| #2055 | `status:needs-data` + `dark-intelligence` + `wip:ace-linux-1`; depends on #2112 closing first | issue labels |
| #2152 | `status:blocked` | label |
| #1264 | `machine:licensed-win-1` only — not this lane | label |
| #2229 | `machine:licensed-win-1` only — not this lane | label |
| #2269 | `machine:dev-secondary` | label |
| #2270 | `machine:dev-secondary` | label |
| #2272 | `machine:multi` + `agent:codex` (named) + `status:working` | label |
| #2462, #2458, #2402, #2403, #2373, #2368, #2364, #2346, #2327, #2227 (codex lane), #2129, #2124, #2125, #2126, #2070, #2046 | `status:working` + `agent:codex`: Codex worker has the issue claimed | label combo |
| #1962, #1782, #1583 | epic/multi-machine, `status:working`, multiple named agents | label combo |
| #2510 | label says `status:plan-approved` but latest author comment (2026-04-27) says "still **not approval-ready**" after 13 review rounds; treat as plan-review | comment evidence + missing marker |
| #2541, #2544 | label says approved, plan body + latest comment say `plan-review`; missing marker | comment evidence + missing marker |
| #2490 | label says approved but no marker file; T1 review-waiver is informal | missing marker |

## Risks not surfaced in label state

1. **Approval-binding gap (recurring).** Five of the seven non-`status:working` plan-approved issues have NO marker file. Recommend the operator either (a) audit and demote the labels back to `status:plan-review` for #2510/#2541/#2544, or (b) write the missing markers for #2490 with explicit revision binding before any Claude lane executes them.
2. **Codex-lane contention.** Of the 32 open issues, ~20 carry `agent:codex` + `status:working`. Picking these for Claude capacity will collide on the same issue thread (memory: `feedback_isolated_clone_dispatch_race.md`). Avoid.
3. **Hermes activity.** Memory `feedback_hermes_active_preflight_check.md` warns Hermes cleanup loops on `main` can revert parallel commits within minutes. Recommend `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'` preflight before any `main`-targeting commit, and prefer a worktree+feature-branch lane for any execution slot above.

## Suggested next-action ordering for the Claude lane

1. **Slot A (highest confidence):** finish #2112 → unblock #2055.
2. **Slot B:** add marker to `.planning/plan-approved/2490.md`, then execute #2490 T1 fix.
3. **Slot C:** post the #2227 Branch-B-complete + Branch-A-new-approval comment (no code).
4. **Slot D:** post the #2540 umbrella-bounded-mandate-satisfied comment (no code).
5. **Slot E:** post the #2541/#2544 label-vs-marker contradiction question to the operator.
6. **Slot F:** flag #2510 separately given its 13-round review history; recommend operator demote the label.

## Verification (read-only — no code change)

After this audit is read, the operator can independently confirm with:

```
# Marker-vs-label cross-check (run anywhere with gh + repo checkout)
gh issue list --label "status:plan-approved" --state open --limit 100 --json number --jq '.[].number' \
  | while read n; do
      [ -f ".planning/plan-approved/${n}.md" ] && echo "marker: ${n}" || echo "MISSING-MARKER: ${n}"
    done

# Label vs latest-comment cross-check (spot-check 2510, 2541, 2544)
for n in 2510 2541 2544; do
  echo "=== #${n} ==="
  gh issue view "${n}" --json comments --jq '.comments[-1].body[0:200]'
  echo
done
```

The first command should show 5–7 `MISSING-MARKER` lines for the open queue (consistent with the body of this audit). The second should show "still not approval-ready" / "remains `status:plan-review`" language for all three.

## What I did NOT do (per operator instruction)

- Did **not** edit any GitHub labels.
- Did **not** close any issues.
- Did **not** kill any processes.
- Did **not** clean any dirty files in `git status`.
- Did **not** request or print API keys.
- Did **not** execute any code change beyond writing this audit file.
