# Session Handoff — statusline + AI-quota sync on ws014 (Windows)

> Archived 2026-10-09 from the C:/ws root under #3987 Phase 0 (historical; superseded by the PowerShell-native statusline).

- **Date:** 2026-06-09
- **Machine:** ws014 (Windows 11 Pro, win32)
- **Scope:** Sync this machine's Claude Code statusline + codex-quota tooling to workspace-hub `origin/main` (context: PRs #2954 statusline pipefail fix, #2956 codex live quota — both MERGED).
- **Constraint honored:** read-only against git — **no commits, no pushes**. HUB working tree left CLEAN.

## Outcome: GREEN — all sync targets verified

| Area | State |
|---|---|
| HUB | `C:\ws\workspace-hub`, `main` == `origin/main` (0/0), tree CLEAN |
| `.claude/statusline-command.sh` | at `b13cbdf2a` (#2954); `\|\| true` guards on L34 (`@{u}` rev-list) + L45 (issue_num grep) |
| `scripts/ai/assessment/query-codex-usage.sh` | at `74c94f751` (#2956); has `get_live_rate_limits` + `account/rateLimits/read` |
| `scripts/ai/assessment/lib/providers.sh` | at `74c94f751` (#2956); accepts `source == "app-server-live"` |
| settings.json statusLine | present, unchanged — Windows shim (see below) |
| WORKSPACE_HUB (User env) | `C:/ws/workspace-hub` |

## Windows-specific adaptation (already in place, working)
- `~/.claude/settings.json` statusLine runs `bash "C:/Users/vamseea/.claude/statusline-wrapper.sh"`.
- `statusline-wrapper.sh` prepends winget-`jq` to PATH, then `exec`s `${WORKSPACE_HUB:-C:/ws/workspace-hub}/.claude/statusline-command.sh`.
- Reason: a bare Git-Bash login shell does NOT have `jq` on PATH; raw `bash statusline-command.sh` fails `jq: command not found`. The wrapper is the real Claude Code invocation path.
- bash: `C:\Program Files\Git\usr\bin\bash.exe` (on PATH).

## Test evidence
- **Statusline, non-git `C:\`:** exit 0, one line, branch `?` (the #2954 regression case — now renders).
- **Statusline, inside HUB:** exit 0, one line — `workspace-hub main … O:97% …`.
- **Codex live `--json`:** `source: "app-server-live"`, week_pct 24, pct_remaining 76, resets 2026-06-11. (NOTE: first call cold-starts past the 3s `CODEX_APPSERVER_WAIT` and falls back; re-run is clean. Codex 0.135.0, logged in via ChatGPT/pro.)
- **Codex fallback `--no-live --json`:** `source: "local-session-rate-limits"` (does NOT degrade to `manual`).

## Open items / next steps
1. **No refresh scheduler on this machine.** `scripts/cron/provider-utilization-refresh.sh` exists but neither `schtasks` nor `crontab` references it. Per task constraints, none was added.
2. **`config/ai-tools/agent-quota-latest.json` is stale** — timestamp 2026-06-01, codex `week_pct 3.0` / `local-session-rate-limits`. That stale value is what the statusline shows as `O:97%`; live is 24% used / 76% remaining. With no scheduler, the `O:` figure keeps drifting.
   - To fix accuracy: schedule `provider-utilization-refresh.sh`, OR run it manually. Either path WRITES the tracked file `config/ai-tools/agent-quota-latest.json` (→ dirty tree), so it was deliberately left untouched under this session's read-only/no-commit rule. Decide and authorize before running.
3. **Codex cold-start latency:** if the statusline or refresh ever needs first-call reliability, consider raising `CODEX_APPSERVER_WAIT` above the 3s default on this box.

## No external actions taken
No commits, no pushes, no emails, no issue comments, no scheduler entries. Probe scripts created during testing were removed; HUB tree confirmed clean. This handoff lives OUTSIDE the repo (`C:\ws\`) to avoid dirtying the tracked tree.
