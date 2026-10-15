# AI account usage (fleet)

Generated 2026-10-15T15:13:31+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (73.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw
- **codex**: `codex-professional` (91.0% weekly headroom) on ace-win-1 -- within 15 pts of codex-owner: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 10% | 27% | 73% | 2026-10-17T13:59:59.741488+00:00 | ace-win-2 | oauth-api |
| claude-professional | claude | colleague | 29% | 67% | 33% | 2026-10-17T07:59:59.603014+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 23% | 77% | 2026-10-22T06:13:31+00:00 | ace-win-2 | app-server-live |
| codex-professional | codex | colleague |  | 9% | 91% | 2026-10-22T08:40:50+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
