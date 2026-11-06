# AI account usage (fleet)

Generated 2026-11-06T07:13:54+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (58.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (89.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 64% | 36% | 2026-11-07T14:00:00.641616+00:00 | ace-win-2 | oauth-api | ok | 2026-11-06T07:13:20+00:00 |
| claude-professional | claude | colleague |  | 42% | 58% | 2026-11-07T07:59:59.739137+00:00 | ace-win-1 | oauth-api | ok | 2026-11-06T07:13:25+00:00 |
| codex-owner | codex | owner |  | 39% | 61% | 2026-11-11T06:35:56+00:00 | ace-win-2 | app-server-live | ok | 2026-11-06T07:13:51+00:00 |
| codex-professional | codex | colleague |  | 11% | 89% | 2026-11-08T11:32:57+00:00 | ace-win-1 | app-server-live | ok | 2026-11-06T07:13:25+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
