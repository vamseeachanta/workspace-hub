# AI account usage (fleet)

Generated 2026-10-18T02:13:41+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (90.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw
- **codex**: `codex-professional` (98.0% weekly headroom) on ace-win-1 -- within 15 pts of codex-owner: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 18% | 10% | 90% | 2026-10-24T14:00:00.171292+00:00 | ace-win-2 | oauth-api |
| claude-professional | claude | colleague | 60% | 40% | 60% | 2026-10-24T08:00:00.169662+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 12% | 88% | 2026-10-24T20:40:38+00:00 | ace-win-2 | app-server-live |
| codex-professional | codex | colleague |  | 2% | 98% | 2026-10-24T20:40:45+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
