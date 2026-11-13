# AI account usage (fleet)

Generated 2026-11-13T14:14:01+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (57.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (70.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 92% | 8% | 2026-11-14T13:59:59.863521+00:00 | ace-win-2 | oauth-api | ok | 2026-11-13T14:13:50+00:00 |
| claude-professional | claude | colleague |  | 43% | 57% | 2026-11-14T08:00:00.305865+00:00 | ace-win-1 | oauth-api | ok | 2026-11-13T14:13:54+00:00 |
| codex-owner | codex | owner |  | 56% | 44% | 2026-11-18T06:36:36+00:00 | ace-win-2 | app-server-live | ok | 2026-11-13T14:13:59+00:00 |
| codex-professional | codex | colleague |  | 30% | 70% | 2026-11-17T04:51:09+00:00 | ace-win-1 | app-server-live | ok | 2026-11-13T14:13:54+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
