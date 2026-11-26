# AI account usage (fleet)

Generated 2026-11-26T14:14:05+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (75.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (52.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 98% | 2% | 2026-11-28T13:59:59.863160+00:00 | ace-win-2 | oauth-api | ok | 2026-11-26T14:13:51+00:00 |
| claude-professional | claude | colleague |  | 25% | 75% | 2026-11-28T08:00:00.005633+00:00 | ace-win-1 | oauth-api | ok | 2026-11-26T14:13:57+00:00 |
| codex-owner | codex | owner |  | 98% | 2% | 2026-11-29T17:50:08+00:00 | ace-win-2 | app-server-live | ok | 2026-11-26T14:14:02+00:00 |
| codex-professional | codex | colleague |  | 48% | 52% | 2026-12-02T10:35:47+00:00 | ace-win-1 | app-server-live | ok | 2026-11-26T14:13:57+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
