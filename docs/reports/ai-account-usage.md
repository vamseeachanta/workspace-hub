# AI account usage (fleet)

Generated 2026-11-27T18:13:52+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (62.0% weekly headroom) on ace-win-1
- **codex**: `codex-owner` (63.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector, gpu-claw

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 100% | 0% | 2026-11-28T14:00:00.419451+00:00 | ace-win-2 | oauth-api | ok | 2026-11-27T18:13:40+00:00 |
| claude-professional | claude | colleague |  | 38% | 62% | 2026-11-28T07:59:59.843822+00:00 | ace-win-1 | oauth-api | ok | 2026-11-27T18:13:44+00:00 |
| codex-owner | codex | owner |  | 37% | 63% | 2026-12-03T18:41:43+00:00 | ace-win-2 | app-server-live | ok | 2026-11-27T18:13:49+00:00 |
| codex-professional | codex | colleague |  | 84% | 16% | 2026-12-02T10:35:47+00:00 | ace-win-1 | app-server-live | ok | 2026-11-27T18:13:44+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
