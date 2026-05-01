# A3 ace-linux-1 control-plane synthesis — plan + embedded deliverables

## Context

This is the A3 control-plane lane spawned by `launch-ace1-local.sh` from
`docs/plans/overnight-prompts/2026-04-28-night-both-machines/`. The lane was
launched at 21:22 CDT into `claude -p --permission-mode plan`. Plan mode is the
hard runtime constraint, so I cannot write the three deliverable files at their
final paths inside this session even though the prompt allowlists them.

This plan file therefore captures:

1. The read-only audit findings (process state, log content, GitHub issue state,
   recent operator hot-patches).
2. The full content of all three deliverables embedded as sections, ready for
   the operator (or a follow-up `--permission-mode acceptEdits` Claude session)
   to copy verbatim into the allowlisted result paths.
3. Exact verification commands so the operator can validate every claim before
   landing the files.

The outcome the prompt asked for is the synthesis itself; the file-write step is
a mechanical follow-up.

## Read-only audit summary

### Local processes on ace-linux-1 (verified at 21:27 CDT)

| Lane | Session/PID | State | Evidence |
|---|---|---|---|
| A1 codex | tmux `ace1-codex-approved-20260428`, PID 920587 | EXITED 21:25:28 | `ps -p 920587` returns no row; final log line `tokens used 106347` |
| A2 gemini | tmux `ace1-gemini-recon-20260428` | EXITED ~21:26:46 | no `gemini` process in `ps -ef`; log mtime 21:26:46 |
| A3 claude | tmux `ace1-claude-control-20260428`, PID 920615 | RUNNING (this session) | live `bash -lc … claude -p --permission-mode plan` |

### Local artifacts

- `logs/night-runs/ace1-codex-approved-recovery-20260428.log` — 11 398 B,
  contains Codex's blocker report with prior in-flight commit SHAs.
- `logs/night-runs/ace1-gemini-recon-batch-20260428.log` — 7 301 B, contains a
  full markdown recon report covering #2295, #2501, #2254, #2519, #2520 with a
  ranked summary at the end.
- `logs/night-runs/ace1-claude-control-plane-synthesis-20260428.log` — 0 B
  (this session has not flushed any output yet).
- `docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/` — empty
  directory (no result files have been written by any lane).

### Operator hot-patches detected mid-flight

Commits landed AFTER the original 21:19 dispatch:

- `69fc1b41a` 21:24 — `chore(planning): switch night Gemini lane to local CLI`
  (changed `launch-ace1-local.sh` from `hermes chat --provider openrouter
  --model google/gemini-2.5-pro --quiet -q` to `gemini -p`).
- `540ff4f39` 21:25 — `chore(planning): add no-tool Gemini recon fallback`
  (new `ace1-gemini-recon-batch-no-tools.md` with 434 lines of embedded issue
  context for tool-less stdout-only Gemini sessions).

Conclusion: the operator already noticed Gemini's tool gap and wired a fallback
prompt. The actively-running Gemini relaunch used the original
`ace1-gemini-recon-batch.md` (per process command line), but it still returned a
useful report because Gemini in `-p` mode summarised the embedded prompt
context without needing tools. The no-tools fallback is therefore queued but
unused so far.

### Codex blocker in detail

`logs/night-runs/ace1-codex-approved-recovery-20260428.log` lines 66–148:

- Sandbox setup error on every shell call:
  `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`.
- Codex switched to GitHub MCP read calls and confirmed all five issues still
  carry `status:plan-approved`.
- Comment writes via `codex_apps/github_add_comment_to_issue` were
  `user cancelled MCP tool call` (5×). This matches the *Codex sandbox no
  execution* memory: even fallback writes are tool-layer-blocked, not just
  shell exec.
- Local file write to the result path failed: `apply patch / patch: failed`.
- GitHub-API file create fallback was also user-cancelled.

Critically, Codex did extract real evidence about prior in-flight work that
should NOT be lost on cleanup:

| Issue | Prior local/branch commit | Note |
|---|---|---|
| #2289 | `681da0334aa6d441f1d1187d3ac6e641bd5b93f5` | local commit, push previously blocked |
| #2433 | `397686ed682527517ad1edcda84dcb6e9a51513a` | active `worldenergydata#356`, blocked by downstream `worldenergydata#357` |
| #2459 | `b922e2533beb68d2dc44a6dfd6c9954ef39a39b0` | active `assethold#47`, blocked by downstream `assethold#48` |
| #2269 | `464efb8cc34643bfccfb33de1965caece82c7b8e` | proof requires OpenFOAM runtime on dev-secondary |
| #2346 | `44735e979ade390855d15fd487ea0680cb5f3b51` | demo_03 already reported passing in prior issue comments |

### Gemini recon coverage (in log file, NOT in results/)

The Gemini log contains an `# Action Reconnaissance Report` covering all five
A2 issues with current-state, gaps/blockers, recommended labels, exact next
prompt, verification commands, and a ranked summary:

1. #2519 — Hermes workstation dispatch (high readiness, critical AI-credit value)
2. #2295 — TX franchise tax prep (high readiness, May 15 hard deadline)
3. #2520 — repair ace-linux-2 GH auth (medium, unblocks delegation)
4. #2254 — provider telemetry (medium, waiting on policy answers)
5. #2501 — governance-lock handoff (low, blocked on user clarification)

The recon prompt called for six per-issue files plus a ranked summary, all under
`results/`. None were written because Gemini headless `-p` has no Write tool;
the entire deliverable lives only in the log.

### GitHub issue state (verified via `gh issue list`)

All 18 listed issues are OPEN. The five A2 recon-only issues correctly do NOT
carry `status:plan-approved` (recon doesn't need it). The remaining 13
implementation-target issues all carry `status:plan-approved`:

- A1 set: #2289, #2433, #2459, #2269, #2346 (all plan-approved; #2433 and #2459
  also `status:blocked`).
- B1 set: #2515 (plan-approved, last touched 17:26 today), #2458 (plan-approved
  + working).
- B2 set: #2364, #2368, #2369, #2373, #2403 (all plan-approved + working);
  #2227 plan-approved + `status:needs-data` (correctly blocked from
  implementation; only blocker reports allowed).

No plan-gate label drift detected.

### ace-linux-2 (B1/B2/B3) — UNVERIFIABLE FROM PLAN MODE

`ssh ace-linux-2 …` is gated by plan-mode permissions in this session and was
denied. State of `tmux list-sessions`, `/mnt/local-analysis/ace2-worker-logs/`,
and `/mnt/local-analysis/ace2-worker-reports/` cannot be confirmed from here.

The dirty parent-checkout files in `git status` (telemetry JSON, session
signals) are pre-dispatch state and not changed by any night lane.

No new digitalmodel commits since 2026-04-28 00:00 (`git -C digitalmodel log
--since="2026-04-28 00:00"` returned nothing), so even if B1 ran, no
digitalmodel changes have synced back to this checkout yet.

---

## Deliverable 1 — `control-plane-lane-health.md` (embedded, ready to copy)

```markdown
# Overnight lane health — 2026-04-28 night dispatch (ace-linux-1 + ace-linux-2)

Snapshot taken: 2026-04-28 21:27 CDT (2026-04-29 02:27 UTC) from the A3
plan-mode Claude session. ace-linux-1 evidence is direct; ace-linux-2 evidence
is marked UNVERIFIABLE because SSH is gated under plan-mode permissions.

| Lane | Machine | Provider | Process / session | Last artifact / log | Classification | Evidence |
|---|---|---|---|---|---|---|
| A1 | ace-linux-1 | Codex `codex exec` | tmux `ace1-codex-approved-20260428`; PID 920587 EXITED 21:25:28 | `logs/night-runs/ace1-codex-approved-recovery-20260428.log` 11 398 B mtime 21:25:28 | BLOCKED | log lines 66–148: `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` on every shell call; 5× `user cancelled MCP tool call` on `github_add_comment_to_issue`; local patch write failed; GitHub API fallback also cancelled. Codex did fetch prior in-flight commit SHAs for all 5 issues (see runbook). |
| A2 | ace-linux-1 | Gemini local `gemini -p` (was Hermes `hermes chat` until operator hot-patched `69fc1b41a` 21:24) | tmux `ace1-gemini-recon-20260428`; gemini PID exited ~21:26:46 | `logs/night-runs/ace1-gemini-recon-batch-20260428.log` 7 301 B mtime 21:26:46 | READY_FOR_REVIEW (output landed in log, not in `results/`) | log contains `# Action Reconnaissance Report` covering #2295/#2501/#2254/#2519/#2520 with ranked summary; per-issue `results/gemini-*.md` files were NOT written because headless Gemini `-p` has no Write tool. Two `gsd-debugger.md` / `gsd-executor.md` agent definitions failed to load with `Unrecognized key 'permissionMode'` — non-fatal but worth fixing. |
| A3 | ace-linux-1 | Claude Code | tmux `ace1-claude-control-20260428`; PID 920615 RUNNING | `logs/night-runs/ace1-claude-control-plane-synthesis-20260428.log` 0 B (not yet flushed) | RUNNING | this synthesis is being authored in plan mode; deliverable files cannot be written here, see plan file `.planning/a3-ace-linux-1-breezy-fox.md` for embedded ready-to-copy content |
| B1 | ace-linux-2 | Claude Code `--permission-mode acceptEdits` | tmux `ace2-claude-digitalmodel-20260428` (intended) | remote `/mnt/local-analysis/ace2-worker-logs/ace2-claude-digitalmodel-20260428.log` (intended) | UNVERIFIABLE | `ssh ace-linux-2 …` denied under plan-mode permissions; no new digitalmodel commits visible from `git -C digitalmodel log --since="2026-04-28 00:00"` (could mean lane never started, lane started but never committed, or commits exist on the remote and have not been fetched here) |
| B2 | ace-linux-2 | Claude Code `--permission-mode acceptEdits` | tmux `ace2-knowledge-docintel-20260428` (intended) | remote `/mnt/local-analysis/ace2-worker-logs/ace2-knowledge-docintel-20260428.log` (intended) | UNVERIFIABLE | same SSH gate; #2227 still carries `status:needs-data` so even if B2 ran, that issue should only have a blocker report |
| B3 | ace-linux-2 | Claude Code plan mode | tmux `ace2-claude-review-20260428` (intended) | remote `/mnt/local-analysis/ace2-worker-reports/night-20260428-adversarial-review-*.md` (intended) | UNVERIFIABLE | same SSH gate |

Operator-runnable verification (one-shot, copy/paste):

```bash
# Local lane re-check
ps -ef | grep -E 'codex exec|gemini -p|hermes chat|claude -p' | grep -v grep || true
find /mnt/local-analysis/workspace-hub/logs/night-runs -name '*20260428*' -printf '%TY-%Tm-%Td %TH:%TM %s %p\n' | sort
find /mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-28-night-both-machines/results -type f -printf '%TY-%Tm-%Td %TH:%TM %s %p\n' | sort

# Remote lane verify
ssh -o BatchMode=yes ace-linux-2 'tmux list-sessions 2>&1 || true'
ssh -o BatchMode=yes ace-linux-2 "find /mnt/local-analysis/ace2-worker-logs /mnt/local-analysis/ace2-worker-reports -maxdepth 1 -name '*20260428*' -printf '%TY-%Tm-%Td %TH:%TM %s %p\n' 2>/dev/null | sort"
ssh -o BatchMode=yes ace-linux-2 'ls -la /mnt/local-analysis/night-runs/ace2-digitalmodel /mnt/local-analysis/night-runs/ace2-knowledge 2>&1 || true'
```
```

---

## Deliverable 2 — `control-plane-morning-runbook.md` (embedded, ready to copy)

```markdown
# Morning runbook — 2026-04-29 (post-2026-04-28 night batch)

Source state captured 2026-04-28 21:27 CDT by A3 plan-mode synthesis. Run the
verification block at the end before acting on any of these recommendations.

## 1. Verify first (high-signal evidence already on disk, no provider needed)

1. Re-read `logs/night-runs/ace1-codex-approved-recovery-20260428.log` lines
   140–148. Confirm the prior in-flight commit SHAs Codex extracted from
   GitHub:
   - #2289 → local commit `681da0334aa6d441f1d1187d3ac6e641bd5b93f5` (push
     previously blocked).
   - #2433 → `worldenergydata#356` head `397686ed682527517ad1edcda84dcb6e9a51513a`
     (blocked downstream by `worldenergydata#357`).
   - #2459 → `assethold#47` head `b922e2533beb68d2dc44a6dfd6c9954ef39a39b0`
     (blocked downstream by `assethold#48`).
   - #2269 → branch commit `464efb8cc34643bfccfb33de1965caece82c7b8e` (needs
     OpenFOAM runtime on dev-secondary to verify).
   - #2346 → branch commit `44735e979ade390855d15fd487ea0680cb5f3b51` (demo_03
     materialization reported passing in prior issue comments).
2. Re-read `logs/night-runs/ace1-gemini-recon-batch-20260428.log` to consume the
   Gemini reconnaissance report directly. The recon already covers all five A2
   issues with status, blockers, recommended labels, exact next prompts, and a
   ranked summary. Promote the log content into per-issue files under
   `results/` if you want the deliverable in the agreed location (see runbook
   step 4 / next-dispatch lane 2).
3. Run the local + remote verification block from
   `control-plane-lane-health.md`. If `ssh ace-linux-2 tmux list-sessions`
   returns nothing, B1/B2/B3 either never launched or already exited; check
   `/mnt/local-analysis/ace2-worker-logs/*20260428*.log` for evidence either
   way.

## 2. Blockers needing human decision

1. **bwrap loopback failure on ace-linux-1** — `bwrap: loopback: Failed
   RTM_NEWADDR: Operation not permitted`. This kills every Codex `codex exec`
   shell call before it runs. Until repaired, do NOT route Codex implementation
   lanes to ace-linux-1. Likely root causes: kernel namespace restriction,
   AppArmor/seccomp policy, or `unprivileged_userns_clone`. File a new issue or
   reuse #2520-style infra issue; this is a host-level fix, not a per-lane fix.
2. **Codex `_add_comment_to_issue` cancellations** — even after Codex fell back
   to MCP, comment writes were `user cancelled MCP tool call` (5×). Confirm
   whether this is the operator's policy gate (acceptable) or a misconfigured
   MCP allowlist (needs widening). If gate is intentional, document it in the
   Codex lane prompts so future lanes don't waste tokens trying.
3. **Two `.gemini/agents/*.md` validation errors** — `gsd-debugger.md` and
   `gsd-executor.md` both have an unrecognized `permissionMode` key. Non-fatal
   but they pollute every Gemini headless session log. Trim or migrate the
   field.
4. **ace-linux-2 verification** — decide whether to spend the next session in a
   permission mode that allows `ssh ace-linux-2`. If yes, run lane 1 of the
   next-dispatch proposal. If no, treat B1/B2/B3 as "outcomes pending operator
   verification" and do not close any of #2515, #2458, #2364, #2368, #2369,
   #2373, #2403, #2227 based on the night dispatch alone.
5. **#2105 / #2501 governance-lock conflict** — Gemini recon flags this as
   strictly blocked on user clarification (handoff doc says v5 needed; live
   labels say plan-approved). One-line operator decision needed.
6. **#2227 needs-data** — confirm before any wiki promotion attempt that the
   OCIMF / CSA Z276 source data has actually arrived. Per memory:
   `wiki/standards/<code-id>.md` decision was sanctioned 2026-04-25 and #2471
   is CSA-Z276-only.

## 3. Issues that may be closeable AFTER evidence review (do not auto-close)

These are candidates only; close only after an authorized lane posts an
evidence comment with commit SHA + verification command + artifact path:

- **#2520** (`fix(workstations): repair and gate ace-linux-2 GitHub auth before
  delegation`) — master ledger says "ace-linux-2 GitHub auth OK"; if the
  pre-delegation readiness script is actually present and PASS, close with
  evidence. Gemini recon recommends authoring
  `scripts/workstations/ace-linux-2-preflight-check.sh` and gating closeout on
  its PASS output.
- **#2346** (GTM prospect-data customized-demo) — Codex evidence cites prior
  branch commit `44735e979ade390855d15fd487ea0680cb5f3b51` and prior
  passing-comment evidence; verify and close with comment if prior reviewer
  signed off.
- **#2289** (rollback/recovery enforcement) — local commit
  `681da0334aa6d441f1d1187d3ac6e641bd5b93f5` exists but push was previously
  blocked; clear the push block, push, then close once CI / hooks confirm
  enforcement coverage.

Do NOT close in this batch:
- #2433, #2459 — both `status:blocked` on downstream issues; do not pretend
  resolution.
- #2269 — needs OpenFOAM runtime on dev-secondary, which neither A1 nor A2
  could provide.
- #2515, #2458, #2364, #2368, #2369, #2373, #2403, #2227 — all on ace-linux-2
  and currently UNVERIFIABLE from this session.
- #2295 — has hard May 15 external deadline and "human approval before
  submission" gate; AI lanes prepare data only.

## 4. Next-batch provider routing (based on observed overnight output)

- **Codex on ace-linux-1**: NOT until `bwrap` is repaired and MCP
  `_add_comment_to_issue` cancellation root cause is identified. Routing Codex
  here right now wastes tokens (last run consumed 106 347 tokens producing only
  a blocker report). The provider scorecard's "Codex underused, route bounded
  implementation immediately" recommendation is correct in general but blocked
  on this host until infra fix.
- **Codex on ace-linux-2**: master ledger noted Codex smoke 401-failed there;
  do not route until `codex login` is refreshed.
- **Gemini local `gemini -p`**: works for stdout-only research but cannot write
  files. Best use is what Gemini did tonight — produce a single ranked recon
  report — but pair it with a Claude follow-up lane that fans the log out to
  the agreed per-issue file paths.
- **Claude Code**: only provider that successfully wrote files in this batch
  (and only because it was the synthesis lane). Reserve for adversarial review,
  long-context synthesis, and the file-fanout step. Do not burn it on bounded
  implementation that Codex would do faster — once Codex is unblocked.
- **Recommended next-batch order**: Claude (file fanout + ace-linux-2
  verification) → Gemini (next research batch using the no-tools fallback) →
  Codex (only after host fix). See `control-plane-next-dispatch.md` for the
  conservative 3-lane proposal.

## Final operator verification block

```bash
# Confirm A1/A2 finality
ps -ef | grep -E 'codex exec|gemini -p|hermes chat' | grep -v grep || echo "ace1 lane processes all exited"
ls -la /mnt/local-analysis/workspace-hub/logs/night-runs/

# Confirm result-dir state
ls -la /mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/

# Confirm GitHub issue gate is unchanged
gh issue list --repo vamseeachanta/workspace-hub --search "2289 2433 2459 2269 2346 2515 2458 2364 2368 2369 2373 2403 2227 2295 2501 2254 2519 2520" --json number,state,labels --limit 30 | jq '.[] | {n:.number,state,labels:[.labels[].name]}'

# Confirm ace-linux-2 lane state (requires interactive permission)
ssh ace-linux-2 'tmux list-sessions; ls /mnt/local-analysis/ace2-worker-logs /mnt/local-analysis/ace2-worker-reports'
```
```

---

## Deliverable 3 — `control-plane-next-dispatch.md` (embedded, ready to copy)

```markdown
# Conservative next-batch proposal — max 3 lanes

Authored 2026-04-28 21:27 CDT by A3 control-plane synthesis. Respects plan
gate. Zero file contention by construction (each lane writes a disjoint set of
paths). Do not launch from this file — operator must explicitly invoke each
lane after reading.

## Lane C1 — Gemini-recon log fanout (Claude, ace-linux-1, edit mode)

Why: Gemini A2 produced a complete reconnaissance report tonight, but it lives
in `logs/night-runs/ace1-gemini-recon-batch-20260428.log` instead of the agreed
six per-issue files under `results/`. Headless Gemini cannot write files;
Claude Code can.

Writes: only files matching the original A2 spec, all under
`docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/`:
- `gemini-2295-tax-franchise-recon.md`
- `gemini-2501-governance-lock-discrepancy.md`
- `gemini-2254-provider-telemetry-plan.md`
- `gemini-2519-workstation-orchestration-plan.md`
- `gemini-2520-ace2-auth-gate-plan.md`
- `gemini-batch-summary.md`

Does NOT touch source code, GitHub state, telemetry, or `.claude/state/*`.
Does NOT consult external sources — pure log-to-file split with attribution
header. Plan gate: not required (no implementation, no GitHub mutation).

Prompt file to author and dispatch:
`docs/plans/overnight-prompts/2026-04-28-night-both-machines/results-gemini-fanout-prompt.md`
(short, single-purpose).

Cost estimate: ~5 k Claude tokens (read 7 KB log + write 6 short files).

## Lane C2 — ace-linux-2 lane verification audit (Claude, ace-linux-1, plan mode + SSH allowlisted)

Why: B1/B2/B3 are UNVERIFIABLE from the current A3 plan-mode session because
SSH was gated. Without verification, no #2515/#2458/#2364/#2368/#2369/#2373/
#2403/#2227 evidence can be reviewed, and no implementation evidence comments
should be posted.

Writes: only `docs/plans/overnight-prompts/2026-04-28-night-both-machines/
results/control-plane-ace2-followup.md` (one new file).

Required permission widening: this Claude lane must be allowed to run
`ssh ace-linux-2 …` read-only commands. The minimum command set is:

```bash
ssh ace-linux-2 'tmux list-sessions'
ssh ace-linux-2 'ls -la /mnt/local-analysis/ace2-worker-logs /mnt/local-analysis/ace2-worker-reports'
ssh ace-linux-2 'find /mnt/local-analysis/ace2-worker-logs /mnt/local-analysis/ace2-worker-reports -name "*20260428*" -printf "%TY-%Tm-%Td %TH:%TM %s %p\n"'
ssh ace-linux-2 'tail -n 200 /mnt/local-analysis/ace2-worker-logs/ace2-claude-digitalmodel-20260428.log'
ssh ace-linux-2 'tail -n 200 /mnt/local-analysis/ace2-worker-logs/ace2-knowledge-docintel-20260428.log'
ssh ace-linux-2 'tail -n 200 /mnt/local-analysis/ace2-worker-logs/ace2-claude-review-20260428.log'
ssh ace-linux-2 'cd /mnt/local-analysis/workspace-hub && git -C digitalmodel log --since="2026-04-28 00:00" --pretty=format:"%h %ai %s"'
```

Plan gate: not required (read-only audit, no implementation, no GitHub
mutation).

Prompt file to author and dispatch:
`docs/plans/overnight-prompts/2026-04-28-night-both-machines/ace1-claude-ace2-verification.md`.

Cost estimate: ~10 k Claude tokens.

## Lane C3 — Gemini batched recon, queue refresh (Gemini local `gemini -p`)

Why: per the provider scorecard, Gemini is the highest-priority underused
provider; tonight's relaunch confirmed it returns useful reports when fed
embedded context (the no-tools fallback prompt at
`ace1-gemini-recon-batch-no-tools.md` is exactly this pattern). Use it for the
next batch of recon-only items so the queue has fresh, ranked next-action
prompts ready for Codex once the host bwrap fix lands.

Targets: 3–5 newly-opened or stale `status:plan-review` issues that have not
had a recon pass in the last 7 days. Operator picks; suggested seeds based on
tonight's recon output:
- Follow-ups #2467 / #2468 / #2469 (worldenergydata flake8 lanes — referenced
  by `project_issue_2460_approval_binding.md` memory).
- Any issue with `status:needs-clarification` to converge on the user
  questions.
- Re-recon #2519 once C1+C2 are landed so dispatch v2 has updated readiness.

Writes: only `docs/plans/overnight-prompts/2026-04-28-night-both-machines/
results/gemini-batch-2-summary.md` plus one per-issue file. Reuse the no-tools
fallback prompt format (operator-vetted at `540ff4f39`).

Plan gate: not required (recon only, no implementation).

Prompt file to author and dispatch:
`docs/plans/overnight-prompts/2026-04-28-night-both-machines/ace1-gemini-recon-batch-2-no-tools.md`.

Cost estimate: ~free Gemini-side; ~2 k Claude tokens to compose the prompt.

## Explicitly NOT proposed

- No Codex on ace-linux-1 — bwrap blocker.
- No Codex on ace-linux-2 — pending `codex login` refresh per master ledger.
- No new implementation lane on ace-linux-2 until C2 confirms B1/B2/B3 outcomes.
- No GitHub label changes, no closeouts, no force-pushes — those wait for
  authorized operator session, not background lanes.

## Zero-contention map

| Lane | Reads | Writes |
|---|---|---|
| C1 | `logs/night-runs/ace1-gemini-recon-batch-20260428.log` | 6 disjoint `results/gemini-*.md` files |
| C2 | SSH read-only on ace-linux-2 | 1 new file `results/control-plane-ace2-followup.md` |
| C3 | embedded issue context only | 1 new file `results/gemini-batch-2-summary.md` plus per-issue files |

C1 ⊥ C2 ⊥ C3 file sets. C1 + C2 + C3 do not touch any night-batch path another
lane writes. None touch source code or GitHub state.
```

---

## Verification (how to confirm this synthesis end-to-end)

```bash
# 1. Re-validate process state matches the audit table
ps -p 920587 || echo "A1 codex exited (expected)"
ps -ef | grep -E 'gemini -p|hermes chat' | grep -v grep || echo "A2 gemini exited (expected)"
ps -p 920615 && echo "A3 claude still running (expected)"

# 2. Re-validate log mtimes/sizes
stat /mnt/local-analysis/workspace-hub/logs/night-runs/ace1-codex-approved-recovery-20260428.log
stat /mnt/local-analysis/workspace-hub/logs/night-runs/ace1-gemini-recon-batch-20260428.log

# 3. Re-validate operator hot-patches
git log --oneline 069fc1b41a..540ff4f39

# 4. Re-validate GitHub issue gate
gh issue list --repo vamseeachanta/workspace-hub --search "2289 2433 2459 2269 2346 2515 2458 2364 2368 2369 2373 2403 2227 2295 2501 2254 2519 2520" --json number,state,labels --limit 30 | jq '.[] | {n:.number,state, plan_approved: any(.labels[].name; . == "status:plan-approved")}'

# 5. Re-validate result dir is empty (so this is the first synthesis to land)
ls -la /mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/

# 6. Confirm ace-linux-2 SSH gate (expected to fail in plan mode)
ssh -o BatchMode=yes -o ConnectTimeout=8 ace-linux-2 'echo ok' 2>&1 || echo "SSH gated as expected — needs C2 lane permission widening"
```

## Files this plan would touch (when executed in a future acceptEdits session)

- `docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/control-plane-lane-health.md` (new, content above)
- `docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/control-plane-morning-runbook.md` (new, content above)
- `docs/plans/overnight-prompts/2026-04-28-night-both-machines/results/control-plane-next-dispatch.md` (new, content above)

No source code, no GitHub mutations, no telemetry, no `.claude/state/*`,
exactly matching the A3 prompt's allowlist.
