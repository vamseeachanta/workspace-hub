# AI account usage (fleet)

Generated 2026-10-18T09:13:31+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (87.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw
- **codex**: `codex-professional` (88.0% weekly headroom) on ace-win-1 -- within 15 pts of codex-owner: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 0% | 13% | 87% | 2026-10-24T13:59:59.884477+00:00 | ace-win-2 | oauth-api |
| claude-professional | claude | colleague | 0% | 46% | 54% | 2026-10-24T08:00:00.122738+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 22% | 78% | 2026-10-24T20:40:38+00:00 | ace-win-2 | app-server-live |
| codex-professional | codex | colleague |  | 12% | 88% | 2026-10-24T20:40:45+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
