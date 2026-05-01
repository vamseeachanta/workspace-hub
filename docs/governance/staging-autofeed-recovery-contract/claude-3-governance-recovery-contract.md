<!--
DISPATCHER NOTE — sandbox redirect
Original result path requested by orchestrator:
  /mnt/local-analysis/agent-logs/provider-autofeed-20260430-100339/results/claude-3-governance-recovery-contract.md
The subagent (Claude Opus 4.7) is sandboxed to /mnt/local-analysis/workspace-hub and could not
write to /mnt/local-analysis/agent-logs/. This staged copy is a faithful render of the requested
result file. Orchestrator action required:
  cp '/mnt/local-analysis/workspace-hub/docs/governance/staging-autofeed-recovery-contract/claude-3-governance-recovery-contract.md' \
     '/mnt/local-analysis/agent-logs/provider-autofeed-20260430-100339/results/claude-3-governance-recovery-contract.md'
This staging file is safe to delete after copy. Lane gates honored: documentation-only, no GH
mutations, no approvals, no implementation.
-->

# Provider Autofeed Recovery & Routing Contract

**Lane:** claude-3-governance-recovery-contract
**Workspace:** /mnt/local-analysis/workspace-hub
**Drafted:** 2026-04-30
**Status:** Documentation-only handoff. No GitHub mutations, no approvals, no implementation performed.
**Scope:** Durable rules for keeping ≥3 useful active lanes per provider (Claude, Codex, Gemini), with recovery, stall detection, relaunch limits, and routing constraints derived from observed failure modes.

---

## 1. Purpose

The autofeed orchestrator dispatches review/research/governance work across three providers. Empirically (2026-04-23 → 2026-04-29), several lanes have died silently — sandbox blocks, stdin hangs, overlay blindness, trust-env exits, idle-lane gaps — leaving the orchestrator with <3 useful lanes per provider while still appearing "green" at the dispatcher level. This contract defines the **minimum useful-lane floor**, the **objective signals** that distinguish a useful lane from a zombie, and the **bounded recovery actions** the autofeed cron is authorized to take without human approval.

The contract is fail-closed by default: if recovery cannot restore the floor within the limits below, the autofeed pauses dispatch on the affected provider and surfaces an operator alert rather than silently degrading.

---

## 2. Useful-Lane Definition

A lane is **useful** at evaluation time T iff **all** of the following hold:

| Signal | Threshold | Source |
|---|---|---|
| Log file present | exists at expected path | filesystem |
| Log mtime fresh | `now - mtime <= LOG_MTIME_MAX_S` | `stat -c %Y` |
| Log size growing | `size(T) > size(T - WINDOW_S)` OR lane is in completion state | two stat samples |
| Result artifact landed (if completion expected) | non-empty file at result path with no `ERROR:` / `Traceback` head line | `head -5` |
| No active stall signature | log tail does not match patterns in §5 | `tail -200` regex |
| Provider not in `routing_block` set | provider absent from §7 block list | runtime config |

A lane that is **dispatched but not yet started** (no log file) is **pending** for `PENDING_GRACE_S`, after which it counts as failed.

A lane in **completed** state (result artifact present, exit code 0 captured) is **terminal-useful** and does not need to be relaunched; it counts toward the floor only until the next dispatch cycle.

### Defaults

```
LOG_MTIME_MAX_S        = 600     # 10 min — covers normal review pauses
WINDOW_S               = 180     # 3 min — size-delta sampling window
PENDING_GRACE_S        = 120     # 2 min — dispatcher-to-first-write
RESULT_MIN_BYTES       = 256     # below this, suspect truncation/abort
TAIL_LINES             = 200
```

---

## 3. Active-Lane Floor

**Per-provider invariant:** the autofeed must maintain **≥ 3 simultaneously useful lanes** per provider during a dispatch window. Floor evaluation runs every `FLOOR_CHECK_INTERVAL_S = 300` (5 min).

| Provider | Floor | Ceiling | Concurrency note |
|---|---|---|---|
| Claude | 3 | 8 | Sonnet 4.6 / Opus 4.7 — no shared CLI lock |
| Codex | 3 | 6 | Per-process stdin; serialize launch by 2s |
| Gemini | 3 | 6 | Headless requires `GEMINI_CLI_TRUST_WORKSPACE=true` |

If a provider falls below 3 useful lanes:

1. Identify dead lanes via §4 signals.
2. Apply §6 recovery to each dead lane up to `MAX_RELAUNCH_PER_LANE`.
3. If after recovery the floor is still unmet, set provider to **degraded** and emit operator alert (§9). Do **not** auto-route work onto the surviving lanes beyond ceiling — that masks the gap.

The 3-lane floor is **load-bearing for cross-provider triangulation**: GSD policy (memory: `feedback_cross_provider_review_payoff`) treats single-provider reviews as weakly grounded. A degraded provider invalidates triangulation for that cycle.

---

## 4. Health Signals (Filesystem-First)

The autofeed cron is **forbidden from interpreting log content semantically** for liveness — it must rely on cheap, deterministic filesystem signals first, falling back to log-tail regex only for stall-pattern matching (§5).

### 4.1 Log mtime check

```bash
log_age_s() {
  local log="$1"
  [ -f "$log" ] || { echo -1; return; }
  local mt; mt=$(stat -c %Y "$log" 2>/dev/null || echo 0)
  echo $(( $(date +%s) - mt ))
}
```

A lane whose log mtime exceeds `LOG_MTIME_MAX_S` is **stalled-or-done**; disambiguate via §4.3.

### 4.2 Log size-delta check

Sample size at T and T+WINDOW_S. A lane that is **not in completion state** and shows **zero growth** over the window is stalled. This catches the codex-cli 0.124.0 stdin-hang case where the process is alive but emits no output (memory: `feedback_codex_cli_0_124_upstream_regression`).

```bash
size_delta_b() {
  local log="$1" prev_size="$2"
  local cur; cur=$(stat -c %s "$log" 2>/dev/null || echo 0)
  echo $(( cur - prev_size ))
}
```

### 4.3 Result artifact check

If the lane's expected `result_path` is present:
- `size < RESULT_MIN_BYTES` → suspect abort; mark for relaunch.
- First non-empty line matches `^(ERROR:|Traceback|fatal:|panic:)` → mark for relaunch.
- Final line is a known truncation marker (e.g. `<<TRUNCATED>>`, partial JSON without closing brace) → mark for relaunch.
- Otherwise → terminal-useful; no recovery needed.

### 4.4 Combined liveness predicate

```
useful(lane) :=
  exists(log) AND
  age(log) <= LOG_MTIME_MAX_S AND
  (size_delta(log, WINDOW_S) > 0 OR result_artifact_ok(lane)) AND
  NOT matches_stall_signature(log) AND
  provider_not_blocked(lane.provider)
```

---

## 5. Known Stall Signatures

These patterns are matched against the **last 200 lines** of the lane log. Matching any one classifies the lane as stalled and triggers recovery (§6). Each entry cites the originating incident in memory or the GitHub issue.

### 5.1 Codex

| Signature (regex, multiline) | Meaning | Evidence |
|---|---|---|
| `codex-cli/0\.124\.\d+.*\nReading from stdin` followed by ≥`LOG_MTIME_MAX_S` of silence | 0.124.0 stdin-hang regression | `feedback_codex_cli_0_124_upstream_regression`, [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) |
| `sandbox: write blocked` OR `sandbox: exec blocked` | Codex sandbox refusing the operation | `feedback_codex_sandbox_write_blocked`, `feedback_codex_sandbox_no_execution` |
| `connector: github\(.*\) request failed.*timeout` (3+ in tail) | Connector rate-limit or network partition | `feedback_codex_needs_pushed_artifact` |
| Sustained `verdict: MAJOR` over ≥3 consecutive review rounds while peer providers report MINOR/APPROVE | Codex MAJOR-loop anti-pattern | `feedback_codex_sustained_major_loop`, [#2045](https://github.com/vamseeachanta/workspace-hub/issues/2045)/[#2289](https://github.com/vamseeachanta/workspace-hub/issues/2289) |
| `js_repl fallback engaged` without subsequent `wrote .* bytes` line | Fallback path stalled | `feedback_codex_sandbox_fallback_paths` |

### 5.2 Gemini

| Signature | Meaning | Evidence |
|---|---|---|
| `Trust workspace? \[y/N\]` OR exit code 55 in trailer | Headless trust-env not set | `feedback_gemini_trust_env_blocks_reviews` |
| `file not found:.*` for paths confirmed by `git ls-files` | Sparse-overlay blindness | `feedback_gemini_sandbox_overlay_blindness` |
| `MODEL_RESOURCE_EXHAUSTED` OR `quota exceeded` | Daily quota hit; provider degraded | runtime |

### 5.3 Claude

| Signature | Meaning | Evidence |
|---|---|---|
| `Error: rate_limit` with retry-after >300s | Per-model RPM cap | runtime |
| `permission_denied` on path inside expected sandbox | Subagent sandbox mismatch | observed 2026-04-30 (this lane) |
| Prompt-injection refusal on user-trusted artifact | Misclassified input; needs prompt repair | runtime |
| `<<autonomous-loop` sentinel leaked into user-visible output | Loop sentinel escaped resolution | `ScheduleWakeup` contract |

### 5.4 Universal

| Signature | Meaning |
|---|---|
| Log mtime fresh BUT identical 200-line tail across two consecutive samples (≥WINDOW_S apart) | Process printing keepalive but not progressing |
| `git: lock failed` repeating | Multi-agent commit race; serialize per `feedback_multi_agent_commit_serialization` |
| `[rejected] ... non-fast-forward` followed by retry within 60s | Auto-sync race; the reflog is ground truth (`feedback_reflog_as_ground_truth`) |

---

## 6. Recovery Actions & Limits

Recovery is bounded. The cron must not loop.

### 6.1 Per-lane relaunch budget

```
MAX_RELAUNCH_PER_LANE      = 2     # initial + 2 retries = 3 total attempts
RELAUNCH_BACKOFF_S         = [60, 300]   # exponential: 60s after attempt 1, 300s after attempt 2
LANE_LIFETIME_RELAUNCH_CAP = 5     # over a 24h rolling window across all lanes for that task
```

After `MAX_RELAUNCH_PER_LANE` exhausted, the lane is **abandoned** for the dispatch cycle and its task re-enters the dispatcher queue with a `repeat_failures` counter incremented. Three abandonments within 24h for the same task mark the task as **needs-human**.

### 6.2 Recovery decision table

| Stall class | First action | If still stalled |
|---|---|---|
| Mtime stale, no stall signature | `kill -TERM` lane PID; relaunch with same prompt | Relaunch on different provider per §7 routing |
| Codex 0.124.0 stdin-hang | Refuse relaunch on codex; route to Claude or Gemini | Mark codex provider degraded if ≥2 lanes hit this in 1h |
| Codex sandbox-block | Do **not** relaunch codex for shell-exec/write tasks | Re-route to Claude (memory: `feedback_codex_sandbox_no_execution`) |
| Gemini trust-env exit 55 | Relaunch with `GEMINI_CLI_TRUST_WORKSPACE=true` injected | If still failing, route to Claude |
| Gemini overlay blindness | Verify file with `git ls-files`; if present, re-route | Do not relaunch gemini for sparse-overlay paths |
| Claude rate_limit | Wait `retry-after`, then relaunch | Route to other Claude key/profile if available |
| Universal git lock | Defer relaunch by 30s; serialize commit phase | Move agent to write-only mode (memory: `feedback_parallel_agent_write_only_pattern`) |
| Codex sustained-MAJOR loop | Halt relaunch; surface consensus-vs-minority decision | No further automatic action |

### 6.3 Forbidden recovery actions

The cron **must not**, under any circumstance:

- `git push --force` to recover a lane.
- Self-label issues with `status:plan-approved` (memory: `feedback_never_offer_to_self_label_plan_approved`).
- Close GitHub issues with `--comment` on a CLOSED issue (memory: `feedback_gh_issue_close_silent_comment_drop`); use reopen-comment-close.
- Write through `git checkout` when `.claude/state/` is dirty (memory: `feedback_git_switch_discard_changes_pattern`); use `git switch --discard-changes`.
- Run `git reset HEAD -- .` in a retry loop (memory: `feedback_retry_loop_reset_hazard`).
- Relaunch a lane while a Hermes cleanup loop is active on `main` (memory: `feedback_hermes_active_preflight_check`); preflight `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'` first.

---

## 7. Safe Provider Routing

Routing rules constrain **which provider is permitted** for which task class. They are matched **before** dispatch.

### 7.1 Hard blocks (do not dispatch)

| Task class | Blocked provider | Reason |
|---|---|---|
| Shell command execution | Codex | Sandbox blocks all exec (`feedback_codex_sandbox_no_execution`) |
| Filesystem writes (any path, even pushed) | Codex | Sandbox blocks writes (`feedback_codex_sandbox_write_blocked`) |
| Implementation/build/commit | Codex | Sandbox prevents any code-landing path |
| File-existence verification on sparse overlays | Gemini | Overlay blindness (`feedback_gemini_sandbox_overlay_blindness`) |
| Browser automation (`mcp__claude-in-chrome__*`) | Subagents (any provider) | Session-scoped to main (`feedback_claude_in_chrome_session_scoped`) |
| Live-CLI repro of CLI defects | Mocked-only providers | Mock-vs-live divergence (`feedback_mock_vs_live_invocation_divergence`) |

### 7.2 Soft routing preferences

| Task class | Preferred providers (in order) |
|---|---|
| Code review (defect hunting) | Claude → Codex (read-only) → Gemini |
| Plan adversarial review | Codex (read-only) → Claude → Gemini |
| Documentation drafting | Claude → Gemini → (Codex blocked on write) |
| Research / web-fetch | Claude → Gemini → Codex (connector path) |
| Cross-provider triangulation | Require ≥2 distinct providers; if only 1 available, surface as single-author r3 with provenance (`feedback_permission_gate_blocks_cross_review`) |

### 7.3 Codex pinning

Until `codex-cli ≥ 0.125.0` lands and [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) is verified closed:

```
CODEX_CLI_REQUIRED_VERSION = "0.123.0"
CODEX_CLI_BANNED_VERSIONS  = ["0.124.0", "0.124.1", "0.124.2"]
```

Autofeed must `codex --version` parse before dispatch and skip Codex lanes if the installed CLI is in the banned set.

### 7.4 Provider-degraded latch

When a provider is marked **degraded**, the latch holds for `DEGRADE_LATCH_S = 1800` (30 min) before the floor check will retry that provider. This prevents thrash where a provider flaps between healthy and degraded every 5-min check cycle.

---

## 8. Cron-Ready Prompt Fragments

Reusable text blocks for the autofeed cron to compose prompts without re-deriving the contract each cycle. All fragments are **append-safe** and assume the prompt opens with task context.

### 8.1 Subagent dispatch preamble

```
Workspace: /mnt/local-analysis/workspace-hub
Lane: {{lane_id}}
Provider: {{provider}}
Result file: {{result_path}}
Hard gates: documentation/handoff only; no GitHub mutations; no approvals; no implementation.
Stall signatures to avoid emitting: see §5 of provider-autofeed contract.
If you hit a sandbox block, emit a single line "BLOCKED: <reason>" to your log and exit; do not retry.
```

### 8.2 Codex dispatch addendum (read-only review)

```
Codex sandbox blocks all shell exec and filesystem writes. You may read, reason, and emit findings inline.
You MUST NOT propose `bash`, `git`, or file-write actions; if a finding requires verification, cite the file and line and let the orchestrator verify.
If you find yourself about to issue MAJOR for the 3rd consecutive round while peers report MINOR, STOP and emit:
  "CONSENSUS-CHECK: minority MAJOR after N rounds — surfacing instead of cycling."
```

### 8.3 Gemini dispatch addendum

```
Headless precondition: GEMINI_CLI_TRUST_WORKSPACE=true must be exported before invocation.
Before claiming "file not found": verify with `git ls-files -- <path>`; sparse-overlay blindness causes ~54 false-positives per 8-plan batch (2026-04-23).
If you exit on trust prompt or quota, emit "DEGRADED: <reason>" and exit non-zero.
```

### 8.4 Claude dispatch addendum

```
This is a subagent dispatch. The SUBAGENT-STOP marker in `using-superpowers` applies — skip skill invocation and proceed directly.
If your sandbox cannot write to the requested result path, write to a workspace-hub staging path
(under docs/governance/staging-*/) and prepend a redirect header so the orchestrator can copy.
Result file must be written via the Write tool (Bash sandbox blocks paths outside workspace).
```

### 8.5 Liveness watchdog (cron — runs every 5 min)

```bash
#!/usr/bin/env bash
# autofeed-watchdog.sh — invoked by cron; relies on contract §4
set -uo pipefail
ROOT=/mnt/local-analysis/agent-logs/provider-autofeed-${RUN_ID}
NOW=$(date +%s)
LOG_MTIME_MAX_S=600

declare -A LIVE_PER_PROV=( [claude]=0 [codex]=0 [gemini]=0 )

for lane_dir in "$ROOT"/lanes/*/; do
  lane=$(basename "$lane_dir")
  prov="${lane%%-*}"   # convention: <provider>-<n>-<task>
  log="$lane_dir/lane.log"
  [ -f "$log" ] || { echo "PENDING $lane"; continue; }
  age=$(( NOW - $(stat -c %Y "$log") ))
  if [ "$age" -gt "$LOG_MTIME_MAX_S" ]; then
    if grep -qE 'sandbox: (write|exec) blocked|Reading from stdin|Trust workspace\?' "$log"; then
      echo "STALL_KNOWN $lane (matched signature)"
    else
      echo "STALL_UNKNOWN $lane (mtime+${age}s)"
    fi
  else
    echo "LIVE $lane (mtime+${age}s)"
    LIVE_PER_PROV[$prov]=$(( LIVE_PER_PROV[$prov] + 1 ))
  fi
done

for prov in claude codex gemini; do
  count=${LIVE_PER_PROV[$prov]}
  if [ "$count" -lt 3 ]; then
    echo "FLOOR_BREACH $prov (live=$count/3)" >&2
  fi
done
```

### 8.6 Operator alert payload (when degraded)

```
[autofeed] provider {{provider}} below floor: {{live_count}}/3 useful lanes
Last {{abandoned_count}} abandonments: {{lane_list}}
Stall signatures hit: {{signature_summary}}
Recovery exhausted at: {{timestamp}}
Contract reference: docs/governance/provider-autofeed-recovery-contract.md §3, §6
Suggested operator action: {{routing_suggestion_from_§7}}
```

### 8.7 Codex CLI version preflight

```bash
codex_version_ok() {
  local v; v=$(codex --version 2>/dev/null | awk '{print $NF}')
  case "$v" in
    0.124.*) return 1 ;;   # banned: stdin-hang regression
    0.123.*|0.125.*|0.126.*) return 0 ;;
    *) echo "WARN: untested codex-cli $v" >&2; return 0 ;;
  esac
}
```

---

## 9. Operator Procedures

### 9.1 When the cron emits FLOOR_BREACH

1. Read the alert payload (§8.6).
2. Confirm the stall class against §5.
3. If a known signature: apply the §6 routing change manually and clear the latch.
4. If unknown: capture the lane's last 500 log lines + the result artifact (if any) into a new GitHub issue; do **not** auto-relaunch.

### 9.2 When promoting this contract

This document is **handoff-only**. Promotion to a durable repo location requires:

1. Copy to `docs/governance/provider-autofeed-recovery-contract.md` in workspace-hub.
2. Open issue using the planning-mode template (`docs/plans/_template-issue-plan.md`); apply `status:plan-review`.
3. Cross-review per `project_cross_review_policy` (≥2 providers).
4. User-approval gate before `status:plan-approved` — never self-approve (memory: `feedback_never_offer_to_self_label_plan_approved`).
5. Implementation issue separate from this contract; this file is a contract, not a delivery plan.

### 9.3 Out of scope for this lane

- No GitHub issue creation, labelling, or commenting was performed.
- No code was changed.
- No cron entries were installed.
- No Hermes or auto-sync interaction was attempted.
- The result file was staged inside workspace-hub due to sandbox boundaries; orchestrator copies it to the requested path.

---

## 10. Changelog

| Date | Change | Author |
|---|---|---|
| 2026-04-30 | Initial draft (lane claude-3-governance-recovery-contract) | Claude (Opus 4.7, 1M-context subagent) |

---

## Appendix A — Memory references consulted

- `feedback_codex_cli_0_124_upstream_regression` — 0.124.0 stdin-hang, [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479)
- `feedback_codex_sandbox_no_execution` — Codex sandbox blocks shell exec
- `feedback_codex_sandbox_write_blocked` — Codex sandbox blocks writes
- `feedback_codex_sandbox_fallback_paths` — js_repl + connector fallback
- `feedback_codex_needs_pushed_artifact` — Codex requires pushed artifact for review
- `feedback_codex_sustained_major_loop` — Codex MAJOR-loop anti-pattern, [#2045](https://github.com/vamseeachanta/workspace-hub/issues/2045)/[#2289](https://github.com/vamseeachanta/workspace-hub/issues/2289)
- `feedback_gemini_trust_env_blocks_reviews` — Gemini exit 55 in headless
- `feedback_gemini_sandbox_overlay_blindness` — sparse-overlay false-positives
- `feedback_multi_agent_commit_serialization` — git lock races
- `feedback_parallel_agent_write_only_pattern` — main session serializes commits
- `feedback_permission_gate_blocks_cross_review` — single-author r3 fallback
- `feedback_never_offer_to_self_label_plan_approved` — user-in-loop gate
- `feedback_reflog_as_ground_truth` — `[rejected]` / lock failures interpretation
- `feedback_retry_loop_reset_hazard` — `git reset HEAD -- .` hazard
- `feedback_git_switch_discard_changes_pattern` — `git switch --discard-changes`
- `feedback_hermes_active_preflight_check` — Hermes preflight before parallel commit
- `feedback_mock_vs_live_invocation_divergence` — mock tests pass, live tests fail
- `feedback_claude_in_chrome_session_scoped` — browser tools main-session only
- `feedback_gh_issue_close_silent_comment_drop` — close --comment silent drop on closed issue
- `feedback_cross_provider_review_payoff` — triangulation requires ≥2 providers
- `feedback_autosync_silent_pusher` — auto-sync silently resolves push contention

## Appendix B — Issue references

- [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) — codex-cli 0.124.0 stdin-hang regression
- [#2045](https://github.com/vamseeachanta/workspace-hub/issues/2045), [#2289](https://github.com/vamseeachanta/workspace-hub/issues/2289) — Codex sustained-MAJOR anti-pattern precedent
- [#2460](https://github.com/vamseeachanta/workspace-hub/issues/2460) — approval-binding contract (related governance decision)
