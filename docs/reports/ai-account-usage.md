# AI account usage (fleet)

Generated 2026-11-16T00:14:01+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (80.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-professional` (67.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 20% | 80% | 2026-11-21T14:00:00.432752+00:00 | ace-win-2 | oauth-api | ok | 2026-11-16T00:13:48+00:00 |
| claude-professional | claude | colleague |  | 22% | 78% | 2026-11-21T08:00:00.291063+00:00 | ace-win-1 | oauth-api | ok | 2026-11-16T00:13:52+00:00 |
| codex-owner | codex | owner |  | 98% | 2% | 2026-11-18T06:36:36+00:00 | ace-win-2 | app-server-live | ok | 2026-11-16T00:13:58+00:00 |
| codex-professional | codex | colleague |  | 33% | 67% | 2026-11-17T04:51:09+00:00 | ace-win-1 | app-server-live | ok | 2026-11-16T00:13:52+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
