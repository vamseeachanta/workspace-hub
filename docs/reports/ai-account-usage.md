# AI account usage (fleet)

Generated 2026-10-15T18:13:29+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (63.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw
- **codex**: `codex-professional` (86.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 47% | 37% | 63% | 2026-10-17T13:59:59.524052+00:00 | ace-win-2 | oauth-api |
| claude-professional | claude | colleague | 20% | 71% | 29% | 2026-10-17T07:59:59.792621+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 31% | 69% | 2026-10-22T06:13:31+00:00 | ace-win-2 | app-server-live |
| codex-professional | codex | colleague |  | 14% | 86% | 2026-10-22T08:40:50+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
