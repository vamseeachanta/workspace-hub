# AI account usage (fleet)

Generated 2026-11-11T07:13:55+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (83.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-owner` (100.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector, gpu-claw -- within 15 pts of codex-professional: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 17% | 83% | 2026-11-14T14:00:00.200279+00:00 | ace-win-2 | oauth-api | ok | 2026-11-11T07:13:43+00:00 |
| claude-professional | claude | colleague |  | 19% | 81% | 2026-11-14T07:59:59.895063+00:00 | ace-win-1 | oauth-api | ok | 2026-11-11T07:13:47+00:00 |
| codex-owner | codex | owner |  | 0% | 100% | 2026-11-18T06:36:36+00:00 | ace-win-2 | app-server-live | ok | 2026-11-11T07:13:52+00:00 |
| codex-professional | codex | colleague |  | 2% | 98% | 2026-11-17T04:51:09+00:00 | ace-win-1 | app-server-live | ok | 2026-11-11T07:13:47+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
