# AI account usage (fleet)

Generated 2026-11-08T19:14:11+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (96.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-professional` (100.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 4% | 96% | 2026-11-14T13:59:59.877188+00:00 | ace-win-2 | oauth-api | ok | 2026-11-08T19:13:56+00:00 |
| claude-professional | claude | colleague |  | 7% | 93% | 2026-11-14T07:59:59.768070+00:00 | ace-win-1 | oauth-api | ok | 2026-11-08T19:14:01+00:00 |
| codex-owner | codex | owner |  | 82% | 18% | 2026-11-11T06:35:56+00:00 | ace-win-2 | app-server-live | ok | 2026-11-08T19:14:08+00:00 |
| codex-professional | codex | colleague |  | 0% | 100% | 2026-11-15T19:14:08+00:00 | ace-win-1 | app-server-live | ok | 2026-11-08T19:14:01+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
