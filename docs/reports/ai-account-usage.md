# AI account usage (fleet)

Generated 2026-10-14T18:21:41+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (65.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (49.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 0% | 90% | 10% | 2026-10-17T13:59:59.695215+00:00 | ace-win-2 | oauth-api |
| claude-professional | claude | colleague | 8% | 35% | 65% | 2026-10-17T07:59:59.881930+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 72% | 28% | 2026-10-20T04:58:10+00:00 | ace-win-2 | app-server-live |
| codex-professional | codex | colleague |  | 51% | 49% | 2026-10-20T04:58:10+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
