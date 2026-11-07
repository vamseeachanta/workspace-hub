# AI account usage (fleet)

Generated 2026-11-07T13:14:05+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (99.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (87.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 76% | 24% | 2026-11-07T13:59:59.603197+00:00 | ace-win-2 | oauth-api | ok | 2026-11-07T13:13:52+00:00 |
| claude-professional | claude | colleague |  | 1% | 99% | 2026-11-14T07:59:59.821831+00:00 | ace-win-1 | oauth-api | ok | 2026-11-07T13:13:56+00:00 |
| codex-owner | codex | owner |  | 73% | 27% | 2026-11-11T06:35:56+00:00 | ace-win-2 | app-server-live | ok | 2026-11-07T13:14:02+00:00 |
| codex-professional | codex | colleague |  | 13% | 87% | 2026-11-08T11:32:57+00:00 | ace-win-1 | app-server-live | ok | 2026-11-07T13:13:56+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
