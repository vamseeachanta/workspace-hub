# Session handoff — statusline blank-render + stale Codex quota fixes, cross-machine rollout (2026-06-04)

## Summary

One ace-linux-1 session diagnosed and fixed two related telemetry failures, both now
MERGED to main. Other machines roll out with the single combined prompt below.

### Fix 1 — invisible statusline (PR #2954, MERGED)

`.claude/statusline-command.sh` runs under `set -euo pipefail`; two unguarded command
substitutions killed the script with no output whenever the session cwd was outside a
git repo (e.g. `/mnt/local-analysis`) or the branch had no issue number (e.g. `main`):

- `issue_num=$(echo "$branch" | grep -oE '[0-9]{3,5}' | head -1)` — grep exits 1 on no match
- `lr=$(git rev-list --count --left-right '@{u}...HEAD' 2>/dev/null)` — fails with no upstream

Claude Code hides statusline command errors entirely (non-zero exit → blank line, no
diagnostic), so the failure was silent. Third instance of the
pipefail-kills-optional-match defect class in this ecosystem (review-gate SIGPIPE
`e0c1e9767`, verification-queue CRLF, now statusline). Fix: `|| true` guards.

### Fix 2 — stale Codex usage (PR #2956, MERGED)

`scripts/ai/assessment/query-codex-usage.sh` only mined `~/.codex/sessions/*.jsonl`
token_count events — a passive trail that freezes at the last session's view of the
rate-limit window. Across a weekly window rollover (or idle days) the snapshot goes
badly stale: observed 2026-06-04, snapshot said 21% used / resets Jun 7 (a window that
had already rolled) while live was 1% used / resets Jun 11 — statusline rendered
`O:79%` vs true `O:99%`.

Fix: live-first query via `codex app-server` JSON-RPC `account/rateLimits/read`
(initialize → initialized → read; JSONL over stdio; stdin held open ~3s because
immediate EOF kills the server pre-response; `timeout`-guarded), falling back to
session-log parse, then manual file. `--no-live` / `CODEX_USAGE_NO_LIVE=1` for offline.
`lib/providers.sh` accepts + propagates the new `app-server-live` source label.
Approach mirrors CodexBar (steipete/CodexBar docs/codex.md) and the official
app-server docs (developers.openai.com/codex/app-server). Adversarial review (T1):
APPROVE-WITH-NITS, nits applied — evidence on PR #2956.

## State

| Item | State | Evidence |
|---|---|---|
| Statusline guards | MERGED to main | PR #2954 (`500ebba28`) |
| Codex live quota | MERGED to main | PR #2956 (`d18dee625` + `f03ddc2c1`) |
| ace-linux-1 | LIVE — statusline renders from any cwd; refresh writes `source: app-server-live`, `O:99%` | end-to-end run 2026-06-04 |
| Other machines | **PENDING** — run the combined prompt below | — |

## Verification invariants (do not skip)

- Statusline: pipe minimal JSON from a NON-git cwd; Claude Code hides errors, so
  non-zero exit = invisible line with no diagnostic.
- Codex quota: live query must report `source: "app-server-live"`; session-log parsing
  alone is not trustworthy across weekly rollovers.

## Combined cross-machine rollout prompt (paste into Claude Code on each machine, any OS)

```text
Sync this machine's Claude Code statusline + AI-quota tooling with workspace-hub
origin/main (context: PRs #2954 statusline pipefail fix, #2956 codex live quota — both
MERGED; handoff doc: docs/session-handoffs/2026-06-04-statusline-pipefail-fix-rollout.md).
Work read-only against git: update local checkout, settings, and env — do NOT commit or
push anything.

1. LOCATE the workspace-hub repo for this OS (Linux: /mnt/local-analysis/workspace-hub
   or ~/workspace-hub; Windows: D:\workspace-hub; macOS: search common roots). Call it
   HUB. All later steps use HUB.

2. UPDATE: git fetch origin, then get these files at the origin/main version on disk
   (pull/fast-forward if clean; otherwise `git checkout origin/main -- <file>` is fine):
   - .claude/statusline-command.sh        (must contain "|| true" on the issue_num grep
                                           line and the rev-list '@{u}' line)
   - scripts/ai/assessment/query-codex-usage.sh   (must contain get_live_rate_limits and
                                                   "account/rateLimits/read")
   - scripts/ai/assessment/lib/providers.sh       (must accept source "app-server-live")
   Do not hand-edit any of them.

3. SETTINGS: ensure ~/.claude/settings.json (Windows: %USERPROFILE%\.claude\settings.json)
   has this statusLine block (preserve all other keys):
   "statusLine": { "type": "command", "padding": 0, "command":
     "bash \"${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel)}/.claude/statusline-command.sh\"" }
   On Windows confirm Git Bash is reachable by Claude Code; if `bash` isn't on PATH for
   the statusline subprocess, use the full path to bash.exe and write HUB with forward
   slashes.

4. ENV: ensure WORKSPACE_HUB is persistently set to HUB (Linux/macOS: shell profile;
   Windows: user environment variable) — sessions may start outside any git repo.

5. TEST STATUSLINE exactly as Claude Code invokes it, from BOTH a non-git directory
   (/tmp or C:\) and from inside HUB — both MUST exit 0 and print one line (the non-git
   cwd is the regression that made the statusline invisible; do not skip it):
   echo '{"model":{"display_name":"X"},"workspace":{"current_dir":"<that dir>"},"cost":{"total_cost_usd":0}}' | bash HUB/.claude/statusline-command.sh

6. TEST CODEX QUOTA only if the `codex` CLI is installed and logged in on this machine:
   bash HUB/scripts/ai/assessment/query-codex-usage.sh --json
   Expect source "app-server-live" with a plausible week_pct (it queries
   `codex app-server` JSON-RPC live, ~3s). If codex is not installed, record N/A and
   skip. Also run: bash HUB/scripts/ai/assessment/query-codex-usage.sh --no-live --json
   to confirm the session-log fallback still answers (or falls to "manual" cleanly).

7. REFRESH SCHEDULE (informational, don't create anything new): report whether this
   machine already schedules scripts/cron/provider-utilization-refresh.sh (Linux/macOS:
   crontab -l; Windows: schtasks query). If yes, run it once now and confirm
   config/ai-tools/agent-quota-latest.json updates with codex source "app-server-live".
   If no scheduler entry exists, just say so — do not add one.

8. REPORT one table: HUB path | each of the 3 files at origin/main yes/no (git log -1
   per file) | settings block present/added | WORKSPACE_HUB value | statusline test
   results (both cwds) | codex live + fallback test results | refresh schedule status.
   List anything you could not complete and why.
```

## Dirty-state exceptions (expected residue on ace-linux-1)

- Main checkout remains on in-flight branch `fix/track-fleet-skills-2925-portable` with
  its pre-existing #2925 dirty files (config/ai-tools/*, docs/reports/*, logs/*) — not
  this session's work; untouched.
- Working-tree copies of the three fixed files on that branch are byte-identical to the
  merged origin/main versions; reconcile on the branch's next rebase. Do not revert —
  they are the live tooling for current sessions.

## Known follow-ons (not blocking)

- `C:-%` (Claude quota unknown) in the rendered statusline: `agent-quota-latest.json`
  lacks a `claude.week_pct` entry; real session JSON normally fills it via
  `rate_limits.seven_day`. Separate concern.
- SPECULATIVE (review finding 3, PR #2956): `~/.codex/auth.json` refresh race if two
  concurrent `codex app-server` starts hit token expiry simultaneously; not reproducible,
  no lock files observed. Revisit only if quota queries start failing near token refresh.

## No-external-action status

PRs #2954/#2955/#2956 created by these sessions; all merged by the user (#2955 merged
2026-06-04T16:53Z). No cron, settings, or env changes made on ace-linux-1. Review
evidence posted on PR #2956.
