# AI account usage (fleet)

Generated 2026-11-24T20:13:54+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (96.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (100.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 83% | 17% | 2026-11-28T13:59:59.795062+00:00 | ace-win-2 | oauth-api | ok | 2026-11-24T20:13:42+00:00 |
| claude-professional | claude | colleague |  | 4% | 96% | 2026-11-28T08:00:00.311176+00:00 | ace-win-1 | oauth-api | ok | 2026-11-24T20:13:45+00:00 |
| codex-owner | codex | owner |  | 32% | 68% | 2026-11-29T17:50:08+00:00 | ace-win-2 | app-server-live | ok | 2026-11-24T20:13:50+00:00 |
| codex-professional | codex | colleague |  | 0% | 100% | 2026-12-01T20:13:51+00:00 | ace-win-1 | app-server-live | ok | 2026-11-24T20:13:45+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
