# AI account usage (fleet)

Generated 2026-11-28T04:13:54+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (56.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (100.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 100% | 0% | 2026-11-28T13:59:59.646366+00:00 | ace-win-2 | oauth-api | ok | 2026-11-28T04:13:41+00:00 |
| claude-professional | claude | colleague |  | 44% | 56% | 2026-11-28T07:59:59.650442+00:00 | ace-win-1 | oauth-api | ok | 2026-11-28T04:13:45+00:00 |
| codex-owner | codex | owner |  | 50% | 50% | 2026-12-03T18:41:43+00:00 | ace-win-2 | app-server-live | ok | 2026-11-28T04:13:51+00:00 |
| codex-professional | codex | colleague |  | 0% | 100% | 2026-12-05T01:20:24+00:00 | ace-win-1 | app-server-live | ok | 2026-11-28T04:13:45+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
