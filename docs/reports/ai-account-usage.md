# AI account usage (fleet)

Generated 2026-10-30T19:14:12+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (49.0% weekly headroom) on ace-win-1
- **codex**: `codex-owner` (33.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 5% | 96% | 4% | 2026-10-31T13:59:59.573563+00:00 | ace-win-2 | oauth-api | ok | 2026-10-30T19:13:58+00:00 |
| claude-professional | claude | colleague | 26% | 51% | 49% | 2026-10-31T08:00:00.365147+00:00 | ace-win-1 | oauth-api | ok | 2026-10-30T19:14:03+00:00 |
| codex-owner | codex | owner |  | 67% | 33% | 2026-11-04T06:35:47+00:00 | ace-win-2 | app-server-live | ok | 2026-10-30T19:14:08+00:00 |
| codex-professional | codex | colleague |  | 93% | 7% | 2026-11-04T06:40:53+00:00 | ace-win-1 | app-server-live | ok | 2026-10-30T19:14:03+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
