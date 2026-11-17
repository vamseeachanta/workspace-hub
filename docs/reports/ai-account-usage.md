# AI account usage (fleet)

Generated 2026-11-17T17:13:55+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (50.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (96.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 100% | 0% | 2026-11-21T14:00:00.771751+00:00 | ace-win-2 | oauth-api | ok | 2026-11-17T17:13:44+00:00 |
| claude-professional | claude | colleague |  | 50% | 50% | 2026-11-21T08:00:00.244935+00:00 | ace-win-1 | oauth-api | ok | 2026-11-17T17:13:47+00:00 |
| codex-owner | codex | owner |  | 58% | 42% | 2026-11-23T02:49:02+00:00 | ace-win-2 | app-server-live | ok | 2026-11-17T17:13:52+00:00 |
| codex-professional | codex | colleague |  | 4% | 96% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-17T17:13:47+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
