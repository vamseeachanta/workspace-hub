# AI account usage (fleet)

Generated 2026-11-01T20:13:38+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (91.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-professional` (98.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 9% | 91% | 2026-11-07T13:59:59.687757+00:00 | ace-win-2 | oauth-api | ok | 2026-11-01T20:13:24+00:00 |
| claude-professional | claude | colleague |  | 11% | 89% | 2026-11-07T07:59:59.958346+00:00 | ace-win-1 | oauth-api | ok | 2026-11-01T20:13:28+00:00 |
| codex-owner | codex | owner |  | 76% | 24% | 2026-11-04T06:35:47+00:00 | ace-win-2 | app-server-live | ok | 2026-11-01T20:13:34+00:00 |
| codex-professional | codex | colleague |  | 2% | 98% | 2026-11-08T11:32:57+00:00 | ace-win-1 | app-server-live | ok | 2026-11-01T20:13:28+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
