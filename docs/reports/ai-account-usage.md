# AI account usage (fleet)

Generated 2026-10-31T22:13:57+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (96.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2 -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-owner` (28.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 4% | 96% | 2026-11-07T14:00:00.469883+00:00 | ace-win-2 | oauth-api | ok | 2026-10-31T22:13:44+00:00 |
| claude-professional | claude | colleague |  | 7% | 93% | 2026-11-07T07:59:59.959459+00:00 | ace-win-1 | oauth-api | ok | 2026-10-31T22:13:49+00:00 |
| codex-owner | codex | owner |  | 72% | 28% | 2026-11-04T06:35:47+00:00 | ace-win-2 | app-server-live | ok | 2026-10-31T22:13:54+00:00 |
| codex-professional | codex | colleague |  | 98% | 2% | 2026-11-04T06:40:53+00:00 | ace-win-1 | app-server-live | ok | 2026-10-31T22:13:49+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
