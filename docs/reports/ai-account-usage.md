# AI account usage (fleet)

Generated 2026-11-14T09:13:48+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (97.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (68.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 100% | 0% | 2026-11-14T13:59:59.568980+00:00 | ace-win-2 | oauth-api | ok | 2026-11-14T09:13:37+00:00 |
| claude-professional | claude | colleague |  | 3% | 97% | 2026-11-21T07:59:59.572076+00:00 | ace-win-1 | oauth-api | ok | 2026-11-14T09:13:40+00:00 |
| codex-owner | codex | owner |  | 78% | 22% | 2026-11-18T06:36:36+00:00 | ace-win-2 | app-server-live | ok | 2026-11-14T09:13:45+00:00 |
| codex-professional | codex | colleague |  | 32% | 68% | 2026-11-17T04:51:09+00:00 | ace-win-1 | app-server-live | ok | 2026-11-14T09:13:40+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
