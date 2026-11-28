# AI account usage (fleet)

Generated 2026-11-28T12:13:50+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (0.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw -- every claude account is below 10% weekly headroom; defer marathons
- **codex**: `codex-professional` (100.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 100% | 0% | 2026-11-28T14:00:00.432615+00:00 | ace-win-2 | oauth-api | ok | 2026-11-28T12:13:38+00:00 |
| claude-professional | claude | colleague |  |  |  |  |  | unavailable | not-reported | 2026-11-28T12:13:42+00:00 |
| codex-owner | codex | owner |  | 54% | 46% | 2026-12-03T18:41:43+00:00 | ace-win-2 | app-server-live | ok | 2026-11-28T12:13:47+00:00 |
| codex-professional | codex | colleague |  | 0% | 100% | 2026-12-05T01:20:24+00:00 | ace-win-1 | app-server-live | ok | 2026-11-28T12:13:42+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional | claude: credentials file has no accessToken |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
