# AI account usage (fleet)

Generated 2026-11-24T17:13:58+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (96.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (100.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 81% | 19% | 2026-11-28T14:00:00.326510+00:00 | ace-win-2 | oauth-api | ok | 2026-11-24T17:13:42+00:00 |
| claude-professional | claude | colleague |  | 4% | 96% | 2026-11-28T07:59:59.932746+00:00 | ace-win-1 | oauth-api | ok | 2026-11-24T17:13:47+00:00 |
| codex-owner | codex | owner |  | 31% | 69% | 2026-11-29T17:50:08+00:00 | ace-win-2 | app-server-live | ok | 2026-11-24T17:13:54+00:00 |
| codex-professional | codex | colleague |  | 0% | 100% | 2026-12-01T17:13:55+00:00 | ace-win-1 | app-server-live | ok | 2026-11-24T17:13:47+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
