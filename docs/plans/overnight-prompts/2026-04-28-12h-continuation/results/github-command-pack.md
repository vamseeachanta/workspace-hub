# GitHub command pack — Lane C1 control reconciler

Generated: 2026-04-28 ~22:00 CDT by ace-linux-1 Lane C1 (Claude, Opus 4.7, 1M).
Stop target: 2026-04-29 09:49:46 CDT.

## Use rules

1. **Nothing in this pack has been executed.** Every command is a draft.
2. Re-verify live state with `gh issue view N --json state,labels,updatedAt` before pasting any mutation.
3. Run from `ace-linux-1` only — control-plane authority lives there.
4. Where a command requires a body, the body is staged via heredoc into a file under `/tmp/ghpack-2026-04-28/` so reviewers can diff before sending.
5. None of the commands close, merge, or force-push.

```bash
mkdir -p /tmp/ghpack-2026-04-28
```

---

## Section A — VERIFY_CLOSE candidates: comment evidence, do not close

### A1. #2462 (digitalmodel) — branch pushed but no PR

Branch: `codex/burn-20260427-issue-2462` head `4ad99a36af5a501e3c…` in `vamseeachanta/digitalmodel`.

Draft PR-open command (review remote state first):

```bash
# 1. Confirm branch still exists upstream
gh api repos/vamseeachanta/digitalmodel/git/refs/heads/codex/burn-20260427-issue-2462 \
  --jq '.object.sha'

# 2. Open PR (DRAFT — replace title/body if user prefers different framing)
cat >/tmp/ghpack-2026-04-28/2462-pr-body.md <<'EOF'
Closes vamseeachanta/workspace-hub#2462.

Implements repo-wide operator map and canonical routing surfaces beyond
OrcaWave/OrcaFlex per the approved plan. Branch was pushed on 2026-04-27
but had no PR; this opens it for review.

Evidence:
- Approved plan: see workspace-hub commit history for #2462
- Push evidence: comment 2026-04-28T03:40:15Z on workspace-hub#2462
EOF

gh pr create --repo vamseeachanta/digitalmodel \
  --base main \
  --head codex/burn-20260427-issue-2462 \
  --title "feat: repo-wide operator map and canonical routing (#2462)" \
  --body-file /tmp/ghpack-2026-04-28/2462-pr-body.md \
  --draft
```

### A2. #2458 (digitalmodel) — multi-body benchmark fixture branches pushed

```bash
# Inspect both refs first; comment in 2026-04-27T18:55:44Z mentions two scoped refs
gh api repos/vamseeachanta/digitalmodel/branches?per_page=100 \
  --jq '.[].name' | grep -E '2458|burn' || echo "no match — re-read comment thread"

# Open PR (DRAFT — adjust head once branch confirmed)
cat >/tmp/ghpack-2026-04-28/2458-pr-body.md <<'EOF'
Closes vamseeachanta/workspace-hub#2458.

Promotes named OrcaWave multi-body benchmark fixture for roundtrip and
handoff readiness, per approved plan.

Evidence:
- Push evidence: comment 2026-04-27T18:55:44Z on workspace-hub#2458
EOF

# Replace <head-branch> after gh api lookup above
# gh pr create --repo vamseeachanta/digitalmodel --base main \
#   --head <head-branch> \
#   --title "feat(canonical-spec): OrcaWave multi-body benchmark fixture (#2458)" \
#   --body-file /tmp/ghpack-2026-04-28/2458-pr-body.md --draft
```

### A3. #2433 (worldenergydata PR #356) — verify CI then comment

```bash
gh pr view 356 --repo vamseeachanta/worldenergydata \
  --json state,headRefOid,statusCheckRollup,mergeable

# If green and mergeable, draft a closure-readiness comment on workspace-hub#2433:
cat >/tmp/ghpack-2026-04-28/2433-comment.md <<'EOF'
PR vamseeachanta/worldenergydata#356 head 397686ed68 status check:

- mergeable: <fill from gh pr view>
- statusCheckRollup: <fill from gh pr view>

Original blocker (executable-bit / setup-data-link) is addressed in this PR.
Awaiting human merge; this issue can move to status:verified once PR merges.
EOF

# DO NOT post until reviewer pastes verified status
# gh issue comment 2433 --repo vamseeachanta/workspace-hub --body-file /tmp/ghpack-2026-04-28/2433-comment.md
```

### A4. #2459 (assethold PR #47) — token-reset blocker

```bash
gh pr view 47 --repo vamseeachanta/assethold \
  --json state,headRefOid,statusCheckRollup,mergeable

# Comment template (do not send if PR still red):
cat >/tmp/ghpack-2026-04-28/2459-comment.md <<'EOF'
assethold#47 head b922e2533b status:
- mergeable: <fill>
- failingChecks: <fill>

Lane recovery state: focused workflow-verifier hardening tests pass in CI.
Outstanding blocker per 2026-04-28T10:31:27Z comment.
EOF
```

### A5. #2269 — verify worktree commit landed and request review

Branch: `codex/10thread-20260428-issue-2269` commit `464efb8cc3…`.

```bash
# Workspace-hub: check whether branch was pushed
gh api repos/vamseeachanta/workspace-hub/git/refs/heads/codex/10thread-20260428-issue-2269 \
  --jq '.object.sha' 2>/dev/null || echo "branch not pushed to origin"

# If not pushed, no PR action; if pushed, draft PR
cat >/tmp/ghpack-2026-04-28/2269-pr-body.md <<'EOF'
Closes #2269.

Enforces approved OpenFOAM ESI v2312 validator contract.
Files: scripts/openfoam/verify-openfoam-baseline.sh

Evidence: comment 2026-04-28T06:12:10Z, commit 464efb8cc3.
EOF
```

### A6. #2346 — GTM demo pipeline; Codex pushed `codex/10thread-20260428-issue-2346`

```bash
gh api repos/vamseeachanta/workspace-hub/git/refs/heads/codex/10thread-20260428-issue-2346 \
  --jq '.object.sha' 2>/dev/null || echo "branch not pushed"

# Draft PR if branch present
cat >/tmp/ghpack-2026-04-28/2346-pr-body.md <<'EOF'
Closes #2346.

Materializes demo_03 prospect inputs for the GTM customized-demo pipeline.
Commit: 44735e979a.

Evidence: comment 2026-04-28T06:07:51Z.
EOF
```

### A7. #2519 (priority:critical) — verify epic satisfied

```bash
# Spinoffs already created (#2523/#2524/#2525). Confirm prompt-pack commit in main.
git -C /mnt/local-analysis/workspace-hub log --oneline 3e136a524 -1
# If commit present and prompt files in repo, draft a status comment without closing.
cat >/tmp/ghpack-2026-04-28/2519-comment.md <<'EOF'
#2519 epic state — 2026-04-28 reconciler pass:

- Spinoffs landed: #2523, #2524, #2525.
- Prompt-pack commit 3e136a524 present in main.
- Continuation pack 2026-04-28-12h-continuation now drives the dispatch loop.
- Recommendation: keep #2519 open as the umbrella; close once #2523-#2525 ship.
EOF
```

---

## Section B — BLOCKED_RESOURCE: collapse the upstream gate, do not implement

### B1. #2402 (doc-intel embeddings index) — approval-revision drift

```bash
# Read current marker
cat /mnt/local-analysis/workspace-hub/.planning/plan-approved/2402.md

# Read approved plan SHA reference
gh issue view 2402 --repo vamseeachanta/workspace-hub --json body \
  --jq '.body' | grep -i 'plan' || true

# Decision required from user: re-bind marker to current plan SHA.
# DRAFT comment:
cat >/tmp/ghpack-2026-04-28/2402-comment.md <<'EOF'
#2402 unblock request — approval-revision drift.

Codex 10-thread workers reported "approval-revision drift" twice (2026-04-28
07:25 and 09:19). Local marker `.planning/plan-approved/2402.md` is dated
`approved 2026-04-26` but plan artifact has been edited since.

Two safe paths forward:
1. User refreshes marker SHA (preferred) — `.planning/plan-approved/2402.md`
   line 1 becomes `revision: <current plan SHA>`.
2. User confirms plan is finalized at <current SHA> in a comment, and an
   ace-linux-1 control-plane lane regenerates the marker.

This issue is a primary blocker for #2403 and the doc-intel L2/L3 ship path.
EOF
```

### B2. #2364 (knowledge Batch Pack 1) — approved artifact mismatch (twice)

Same pattern as #2402. Codex blocked on artifact mismatch in worktree.

```bash
ls -la /mnt/local-analysis/workspace-hub/.planning/plan-approved/2364.md 2>/dev/null

cat >/tmp/ghpack-2026-04-28/2364-comment.md <<'EOF'
#2364 unblock request — approved artifact mismatch (recurring).

Codex 10-thread worker reported "approved-plan artifact gate not satisfied"
on 2026-04-28 07:27 and again 09:17, in worktree
`/mnt/local-analysis/codex-10thread-20260427-existing/issue-2364`.

Asks: confirm the canonical plan path for Batch Pack 1 is current, and update
the local approval marker to the plan's HEAD SHA. Until then, implementation
lanes will keep no-op blocking.

Sister issue #2369 / #2373 / #2368 (other Batch Packs) probably share the
same gate — checking next.
EOF
```

### B3. #2272 — env-blocked Codex worker

```bash
cat >/tmp/ghpack-2026-04-28/2272-comment.md <<'EOF'
#2272 portability smoke — Codex worker emitted no code on 2026-04-28
(branch codex/10thread-20260428-issue-2272). Likely env mismatch in
sparse fallback clone `/mnt/local-analysis/codex-10thread-20260427-existing/sparse-2272`.

Next step: dispatch a fresh ace-linux-1 worktree (NOT a sparse-fallback) to
this issue and re-run the smoke pack. If still no code, escalate to env
diagnosis under #2229 portability lanes.
EOF
```

### B4. #2289 — pre-push hook blocked Codex commit `681da033`

```bash
# Diagnose the hook locally without bypassing it
cd /mnt/local-analysis/codex-10thread-20260427-existing/issue-2289 2>/dev/null \
  && git log -1 --stat \
  || echo "worktree not present on this host"

# Comment template
cat >/tmp/ghpack-2026-04-28/2289-comment.md <<'EOF'
#2289 push gate diagnosis request.

Codex local commit 681da0334a is staged on branch
codex/10thread-20260428-issue-2289 but pre-push hook blocks the push.

Action: an ace-linux-1 control-plane operator should
1. fetch the commit by branch into a fresh ace-linux-1 worktree,
2. run `git push --dry-run` to capture the exact hook denial,
3. either fix the underlying issue (preferred) or document why
   the bypass route is unsafe under the rollback-recovery policy
   that #2289 itself defines.

DO NOT use --no-verify; that is the very anti-pattern this issue exists
to address.
EOF
```

### B5. #2515 — ace-linux-2 lane env-blocked; queue ace1 fallback

```bash
cat >/tmp/ghpack-2026-04-28/2515-comment.md <<'EOF'
#2515 implementation handoff request.

Lane B1 on ace-linux-2 (Claude) reported BLOCKED on env mismatch
2026-04-29T02:28Z (sandbox restricted writes; full report in
docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/ace2-digitalmodel-report.md).

Plan was approved 2026-04-28T17:26 (commit b711f3b46b).

Next-lane queue: ace-linux-1 fresh worktree under
`/mnt/local-analysis/night-runs/ace1-2515/` with `digitalmodel/` subrepo
mounted. Implementation prompt staged in next-dispatch-queue.md.
EOF
```

---

## Section C — NEEDS_REVIEW (status:plan-review)

### C1. #2510 — chip CAD demo, stuck after r13 review

```bash
# View the latest review artifact
ls -la /mnt/local-analysis/workspace-hub/scripts/review/results/ | grep -i 2510 | tail -5

cat >/tmp/ghpack-2026-04-28/2510-comment.md <<'EOF'
#2510 plan-review escalation — r13 still not approval-ready (2026-04-27 10:36).

Recommendation: pause the review-cycle loop and run an ace-linux-1 plan
hardening pass (Lane C3) to identify which adversarial finding has not
been folded into the plan. Per #2045/#2289 anti-pattern memory: if Codex
sustained MAJOR for 3+ rounds while other reviewers are at MINOR, this is
a consensus-vs-minority decision rather than auto-cycle.

C3 lane will produce a r14 plan-edit pack within the 12h window, but will
NOT label changes; user-in-loop approval gate stands.
EOF
```

### C2. #2490 — coverage-gate plan draft pushed `f14872956b`

```bash
# Has any cross-review run yet for this plan?
ls -la /mnt/local-analysis/workspace-hub/scripts/review/results/ | grep -i 2490 | tail -5

cat >/tmp/ghpack-2026-04-28/2490-comment.md <<'EOF'
#2490 plan-review next step — plan draft pushed 2026-04-27T17:07 commit
f14872956b (`docs/plans/2026-04-27-issue-2490-coverage-gate-fix.md`).

This plan has not yet had a cross-provider adversarial pass. Lane C3
(ace-linux-1 plan-review hardener) will queue a r1 review and write the
output to `scripts/review/results/2026-04-28-plan-2490-claude-r1.md`.

No labels will be moved until user-approved. Awaiting C3 output.
EOF
```

---

## Section D — NEEDS_PLAN (priority seeds with no plan + no comments)

These four are fresh; no comments, no plan artifact, no working branch. Priority-ranked by GTM/throughput value.

### D1. #2525 — Codex expiring-credit burn-down controller (priority:high)

```bash
# Confirm: 0 comments, OPEN
gh issue view 2525 --repo vamseeachanta/workspace-hub --json comments,state \
  --jq '{state:.state, comments:(.comments|length)}'

# Comment to attach a planning-lane spawn:
cat >/tmp/ghpack-2026-04-28/2525-plan-attach.md <<'EOF'
#2525 planning lane attached.

Lane C3 (ace-linux-1 plan-review hardener) will draft a plan skeleton in
`docs/plans/2026-04-28-issue-2525-codex-burn-down-controller.md` referencing:
- Provider-routing scorecard `config/ai-tools/provider-routing-scorecard.json`
- Existing prompt-pack queue surface
- Hermes config (cron/triggers under .claude/state/)

Plan WILL NOT be self-approved. Standard plan-review workflow follows.
EOF
```

### D2. #2548 — control-plane machine inventory + OrcaFlex/AQWA dispatch (priority:high)

```bash
cat >/tmp/ghpack-2026-04-28/2548-plan-attach.md <<'EOF'
#2548 planning lane attached.

Scope (verbatim from issue body):
- Machine/software/auth inventory across ace-linux-1, ace-linux-2,
  licensed-win-1, achanta-personal devices.
- OrcaFlex/AQWA dispatch readiness on licensed-win-1.
- Business Brain pointer.

Dependencies / overlaps:
- #2523 Hermes preflight readiness checker (overlaps inventory step)
- #2524 machine-aware dispatch ledger (overlaps dispatch surface)
- Existing inventory at `docs/BUSINESS_BRAIN.md` and
  `config/ai-tools/agent-quota-latest.json`.

Lane C3 will produce a plan skeleton; user approval required.
EOF
```

### D3. #2524 — machine-aware dispatch ledger and reconciler (priority:high)

```bash
cat >/tmp/ghpack-2026-04-28/2524-plan-attach.md <<'EOF'
#2524 planning lane attached. Sibling of #2523/#2525, child of #2519.

Plan skeleton scope: schema for dispatch ledger + reconciler hooks +
integration with existing master-dispatch-ledger.md packs.

Lane C3 will draft `docs/plans/2026-04-28-issue-2524-machine-dispatch-ledger.md`
within the 12h window.
EOF
```

### D4. #2523 — Hermes preflight readiness checker (priority:high)

```bash
cat >/tmp/ghpack-2026-04-28/2523-plan-attach.md <<'EOF'
#2523 planning lane attached. Sibling of #2524/#2525, child of #2519.

Scope per gemini-recon (#2520 partial overlap): pre-delegation script
runnable from ace-linux-1 to verify SSH/PATH/Hermes/Codex/gh on every
worker.

Lane C3 will draft `docs/plans/2026-04-28-issue-2523-hermes-preflight.md`.
EOF
```

---

## Section E — Defensive checks before any mutation

```bash
# 1. Always re-read live label set
gh issue view <N> --repo vamseeachanta/workspace-hub --json state,labels

# 2. Confirm not already CLOSED before commenting (per memory:
#    feedback_gh_issue_close_silent_comment_drop — closed issues silently
#    drop --comment payload).
# 3. Check parallel work signals (per memory: feedback_check_parallel_work).
ps -eo pid,etime,cmd | grep -E 'codex|gemini|claude -p' | grep -v grep

# 4. Confirm reflog state matches push expectation (per memory:
#    feedback_reflog_as_ground_truth).
git -C /mnt/local-analysis/workspace-hub reflog -n 10
```

---

## Out of scope for this pack

- Closing any issue (rule from lane prompt).
- Force-pushing or hard-resetting (rule from lane prompt).
- Mutating `.planning/plan-approved/*` markers — that is a control-plane operator decision, not an unattended one.
- Any `gh issue edit --add-label status:plan-approved` — feedback_never_offer_to_self_label_plan_approved memory is load-bearing.
