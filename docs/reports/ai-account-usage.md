# AI account usage (fleet)

Generated 2026-11-14T01:14:42+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (35.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (69.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 98% | 2% | 2026-11-14T13:59:59.943318+00:00 | ace-win-2 | oauth-api | ok | 2026-11-14T01:13:53+00:00 |
| claude-professional | claude | colleague |  | 65% | 35% | 2026-11-14T08:00:00.405429+00:00 | ace-win-1 | oauth-api | ok | 2026-11-14T01:13:56+00:00 |
| codex-owner | codex | owner |  | 68% | 32% | 2026-11-18T06:36:36+00:00 | fleet-collector | app-server-live | ok | 2026-11-14T01:14:39+00:00 |
| codex-professional | codex | colleague |  | 31% | 69% | 2026-11-17T04:51:09+00:00 | ace-win-1 | app-server-live | ok | 2026-11-14T01:13:56+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
