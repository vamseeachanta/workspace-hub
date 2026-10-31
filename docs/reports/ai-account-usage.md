# AI account usage (fleet)

Generated 2026-10-31T19:13:40+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (97.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-owner` (29.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector, gpu-claw

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 3% | 97% | 2026-11-07T14:00:00.499193+00:00 | ace-win-2 | oauth-api | ok | 2026-10-31T19:13:28+00:00 |
| claude-professional | claude | colleague |  | 5% | 95% | 2026-11-07T08:00:00.117736+00:00 | ace-win-1 | oauth-api | ok | 2026-10-31T19:13:32+00:00 |
| codex-owner | codex | owner |  | 71% | 29% | 2026-11-04T06:35:47+00:00 | ace-win-2 | app-server-live | ok | 2026-10-31T19:13:36+00:00 |
| codex-professional | codex | colleague |  | 97% | 3% | 2026-11-04T06:40:53+00:00 | ace-win-1 | app-server-live | ok | 2026-10-31T19:13:32+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
