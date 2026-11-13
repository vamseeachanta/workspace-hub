# AI account usage (fleet)

Generated 2026-11-13T20:14:01+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (40.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (69.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 96% | 4% | 2026-11-14T14:00:00.362533+00:00 | ace-win-2 | oauth-api | ok | 2026-11-13T20:13:49+00:00 |
| claude-professional | claude | colleague |  | 60% | 40% | 2026-11-14T07:59:59.640931+00:00 | ace-win-1 | oauth-api | ok | 2026-11-13T20:13:52+00:00 |
| codex-owner | codex | owner |  | 63% | 37% | 2026-11-18T06:36:36+00:00 | ace-win-2 | app-server-live | ok | 2026-11-13T20:13:58+00:00 |
| codex-professional | codex | colleague |  | 31% | 69% | 2026-11-17T04:51:09+00:00 | ace-win-1 | app-server-live | ok | 2026-11-13T20:13:52+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
