# AI account usage (fleet)

Generated 2026-11-12T14:14:43+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (74.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (93.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 53% | 47% | 2026-11-14T13:59:59.722902+00:00 | ace-win-2 | oauth-api | ok | 2026-11-12T14:14:14+00:00 |
| claude-professional | claude | colleague |  | 26% | 74% | 2026-11-14T07:59:59.713381+00:00 | ace-win-1 | oauth-api | ok | 2026-11-12T14:14:34+00:00 |
| codex-owner | codex | owner |  | 23% | 77% | 2026-11-18T06:36:36+00:00 | ace-win-2 | app-server-live | ok | 2026-11-12T14:14:40+00:00 |
| codex-professional | codex | colleague |  | 7% | 93% | 2026-11-17T04:51:09+00:00 | ace-win-1 | app-server-live | ok | 2026-11-12T14:14:34+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
