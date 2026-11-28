# AI account usage (fleet)

Generated 2026-11-28T15:14:06+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (98.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw
- **codex**: `codex-professional` (99.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 2% | 98% | 2026-12-05T14:00:00.921743+00:00 | ace-win-2 | oauth-api | ok | 2026-11-28T15:13:54+00:00 |
| claude-professional | claude | colleague |  |  |  |  |  | unavailable | not-reported | 2026-11-28T15:13:58+00:00 |
| codex-owner | codex | owner |  | 58% | 42% | 2026-12-03T18:41:43+00:00 | ace-win-2 | app-server-live | ok | 2026-11-28T15:14:03+00:00 |
| codex-professional | codex | colleague |  | 1% | 99% | 2026-12-05T01:20:24+00:00 | ace-win-1 | app-server-live | ok | 2026-11-28T15:13:58+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional | claude: credentials file has no accessToken |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
