# ace-linux-1 Continuous + Parallel Work Prompt — 2026-04-27

You are running on **ace-linux-1**, the primary Hermes/control-plane workstation for `vamseeachanta/workspace-hub`.

## Mission

For the next 24 hours, keep useful AI work moving continuously and in parallel while preserving governance:

1. **Primary objective:** burn roughly **50% of remaining Codex subscription usage** productively on approved implementation/test/refactor/doc issues.
2. **Secondary objective:** keep Claude/Gemini lanes useful for planning, review, research, and handoffs without wasting Codex on open-ended analysis.
3. **Governance:** never implement an issue unless it is `status:plan-approved` or the work is explicitly planning/review-only.
4. **Machine role:** ace-linux-1 is the **control plane**: GitHub mutations, labels, comments, merges, dispatch ledger, final verification, and issue closeout happen here.
5. **Worker role for ace-linux-2:** use ace-linux-2 as overflow execution only; assume `gh auth` may be invalid there, so keep GitHub comments/labels/closures on ace-linux-1 unless fresh readiness proves otherwise.

## Current state snapshot

- Date/time captured: 2026-04-27T13:15:03-05:00.
- Repo root: `/mnt/local-analysis/workspace-hub`.
- Repo: `vamseeachanta/workspace-hub`.
- Provider telemetry snapshot:
  - Codex: `week_messages=5`, `weekly_limit=1400`, `pct_remaining=100`, source `history.jsonl`.
  - Claude: source unavailable; preserve for orchestration/review.
  - Gemini: estimated daily quota, `today_messages=0`; use for research/recon if needed.
- Current Codex burn target: approximately **~700 Codex messages** over 24h, but only through useful work.
- Known active/just-dispatched Codex lanes from prior control-plane action:
  - #2462 — `/mnt/local-analysis/codex-burn-20260427/issue-2462`, branch `codex/burn-20260427-issue-2462`.
  - #2227 — `/mnt/local-analysis/codex-burn-20260427/issue-2227`, branch `codex/burn-20260427-issue-2227`.
  - #2458 — `/mnt/local-analysis/codex-burn-20260427/issue-2458`, branch `codex/burn-20260427-issue-2458`.
- Known #2518 Claude lander may be active or may have completed; do not trample `/mnt/local-analysis/reconcile-main-20260427` until inspected.

## Hard rules

- Do **not** force-push.
- Do **not** close issues unless landed/verified or explicitly proven already satisfied with evidence.
- Do **not** mutate `/mnt/local-analysis/reconcile-main-20260427` except to verify/land #2518.
- Do **not** launch duplicate lanes for issues already labeled `status:working` or with active Codex/Claude processes.
- Do **not** route implementation to issues lacking `status:plan-approved`; for those, generate planning/review packets only.
- Do **not** use `delegate_task` for repo writes. Use real worktrees/clones and real CLI processes.
- Keep every worker lane in an isolated worktree or clone.
- For Codex background runs, avoid the stdin hang: launch as background, then close stdin, or run a pattern already proven to exit cleanly.

## Startup checks

Run from ace-linux-1:

```bash
cd /mnt/local-analysis/workspace-hub

git fetch origin main --prune
git status --short
gh auth status

# Refresh provider/work-queue artifacts if safe
bash scripts/cron/provider-utilization-refresh.sh || bash scripts/ai/assessment/query-quota.sh --refresh --log || true

# Inspect current queues
python - <<'PY'
import json, pathlib
p=pathlib.Path('config/ai-tools/provider-work-queue.json')
if p.exists():
    data=json.load(open(p))
    for provider in ['codex','gemini','claude']:
        q=data.get('provider_queues',{}).get(provider,{})
        print('\n', provider, 'ready=', q.get('execution_ready_count'), 'total=', q.get('total_candidates'))
        for it in q.get('top_issues',[])[:10]:
            print(f"#{it['number']} ready={it.get('execution_ready')} labels={','.join(it.get('labels',[]))} :: {it['title']}")
PY

# Inspect active local processes and existing Codex worktrees
ps -ef | egrep 'codex exec|claude --print|claude -p' | grep -v grep || true
git worktree list | egrep 'codex-burn|reconcile-main|issue-' || true
```

## Continuous controller loop

Repeat every 60–90 minutes, or whenever a lane completes:

### 1. Reconcile active lanes

For each active Codex/Claude lane:

```bash
# Example for issue NNNN
cd /mnt/local-analysis/codex-burn-20260427/issue-NNNN 2>/dev/null || true
git status --short || true
git log --oneline -5 || true
git branch --show-current || true
```

Classify each lane:

- `RUNNING`: process alive, no action except monitor.
- `LANDED_BRANCH`: commit exists and branch pushed; post/verify GitHub comment if worker did not.
- `NEEDS_CENTRAL_VERIFY`: worker made changes but did not validate/commit/push; ace-linux-1 verifies and finishes.
- `BLOCKED`: worker left a blocker report/comment; either create follow-up issue or assign a different approved issue.
- `STALLED_STDIN_OR_SANDBOX`: kill and relaunch with known-safe Codex pattern below.

### 2. Maintain 3–5 active Codex lanes

Use Codex for bounded implementation/test/refactor/doc work.

Preferred issue pool:

- Current top Codex-ready from scorecard:
  - #2462 — repo-wide operator map and canonical routing surfaces beyond OrcaWave/OrcaFlex.
  - #2227 — promote OCIMF Tandem Mooring and CSA Z276 coverage into LLM-wikis.
  - #2458 — named OrcaWave multi-body benchmark fixture.
  - #2464 — split curated tier-1 routing index from raw inventory and clean routing noise.
- Additional explicit `agent:codex,status:plan-approved` candidates if above complete or blocked:
  - #2124, #2125, #2126, #1962, then other `agent:codex` items only after plan-approved verification.

Before launching any issue:

```bash
gh issue view NNNN --repo vamseeachanta/workspace-hub --json state,labels,title,url
```

Require: `state=OPEN` and `status:plan-approved` unless planning-only.

### 3. Launch new Codex lane from ace-linux-1

Use this pattern. Replace `NNNN`, title, and plan paths.

```bash
ISSUE=NNNN
ROOT=/mnt/local-analysis/workspace-hub
BURN=/mnt/local-analysis/codex-burn-20260427
WT=$BURN/issue-$ISSUE
BR=codex/burn-20260427-issue-$ISSUE
mkdir -p "$BURN"
cd "$ROOT"
git fetch origin main --prune
if [ ! -d "$WT/.git" ] && [ ! -f "$WT/.git" ]; then
  git worktree add -b "$BR" "$WT" origin/main
fi

gh issue edit "$ISSUE" --repo vamseeachanta/workspace-hub --add-label agent:codex,status:working || true
gh issue comment "$ISSUE" --repo vamseeachanta/workspace-hub --body "Codex burn lane started on ace-linux-1: isolated worktree \`$WT\`, branch \`$BR\`. Will execute approved scope with TDD, validation, adversarial self-review, push evidence, and leave issue open unless landed/verified." || true

cat > /tmp/codex-burn-issue-$ISSUE.md <<'PROMPT'
You are Codex executing approved workspace-hub issue #NNNN on ace-linux-1.

Repo: vamseeachanta/workspace-hub
Worktree: /mnt/local-analysis/codex-burn-20260427/issue-NNNN
Branch: codex/burn-20260427-issue-NNNN
Issue URL: https://github.com/vamseeachanta/workspace-hub/issues/NNNN

Objectives:
1. Verify issue is OPEN and has status:plan-approved.
2. Read the latest issue body/comments and relevant plan docs under docs/plans/.
3. Inspect whether origin/main already satisfies the issue. If yes, comment evidence and do not duplicate.
4. Create .planning/plan-approved/NNNN.md if local hooks require it, with truthful approval text.
5. Implement only the approved scope using TDD where applicable.
6. Run targeted validators and a reasonable broader sanity check.
7. Perform adversarial self-review of your diff; fix material findings and rerun validators.
8. Commit all and only issue #NNNN changes with a message ending '(#NNNN)'.
9. Push branch. Do not force-push.
10. Post GitHub progress/closeout comment with commit SHA, branch, validation commands/results, and blockers.
11. Close only if landed/verified per repo policy; otherwise leave open with evidence.

Hard constraints:
- Do not touch /mnt/local-analysis/reconcile-main-20260427 or #2518.
- Do not modify unrelated files.
- Do not absorb future-scope work.
- If blocked, produce a precise blocker report and safe preparatory commit only if clearly in scope.

Final output: issue number, branch, commit SHA(s), pushed ref/PR if any, validation commands, issue URL, open/closed state, blockers.
PROMPT

# Launch: background + close stdin immediately if using a process manager.
# If using Hermes terminal/process tools, start background then process.close(session_id).
codex exec -c model_reasoning_effort="high" \
  --dangerously-bypass-approvals-and-sandbox \
  --cd "$WT" \
  "$(cat /tmp/codex-burn-issue-$ISSUE.md)"
```

If Codex prints `Reading additional input from stdin...` and then stalls, terminate and relaunch under a process manager that supports closing stdin immediately after start. If bubblewrap fails (`bwrap: loopback: Failed RTM_NEWADDR`), use `--dangerously-bypass-approvals-and-sandbox` only inside the isolated issue worktree.

### 4. Use ace-linux-2 as overflow

Before assigning work to ace-linux-2, send it the separate `ace-linux-2-continuous-parallel-work-prompt.md`. Keep GitHub mutations on ace-linux-1 unless ace-linux-2 freshly proves `gh auth` is valid.

Good ace-linux-2 overflow tasks:

- Additional Codex implementation lanes in isolated worktrees/clones.
- Read-only verification/adversarial review of ace-linux-1 branches.
- Test-heavy runs in clean worktrees.
- Engineering smoke tests where ace-linux-2 has the needed OSS tools.

Bad ace-linux-2 tasks unless fixed:

- Anything requiring local `gh` mutation if `gh auth status` is invalid.
- Main checkout root-level edits in a dirty root.
- Proprietary OrcaFlex/OrcaWave/ANSYS/MATLAB work; not detected in prior readiness baseline.

### 5. Finish #2518 if still active

Check:

```bash
ps -ef | grep finish-land-2518 | grep -v grep || true
cd /mnt/local-analysis/reconcile-main-20260427 && git status --short && git log --oneline -3
```

If #2518 is complete but not landed, finish central verification and closeout. Do not let it block Codex burn lanes unless the same files overlap.

## Dispatch ledger

Maintain a simple ledger at:

`docs/reports/2026-04-27-codex-burn-dispatch-ledger.md`

Append one row per lane:

```markdown
| Time | Machine | Provider | Issue | Branch/worktree | Status | Validation/evidence | Next action |
|---|---|---|---:|---|---|---|---|
```

Commit/push ledger updates in small batches if useful, but do not let ledger churn block implementation.

## Morning/shift-end report

Produce a concise report with:

- Codex quota at start/end.
- Active lane count and completed lane count.
- Issue URLs touched.
- Branches/commits pushed.
- Issues closed and evidence links.
- Blockers requiring human decision.
- Recommended next 3 Codex lanes if still under 50% burn.
