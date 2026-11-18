# AI account usage (fleet)

Generated 2026-11-18T18:13:53+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (58.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw
- **codex**: `codex-owner` (98.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector, gpu-claw -- within 15 pts of codex-professional: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 42% | 58% | 2026-11-21T14:00:00.056722+00:00 | ace-win-2 | oauth-api | ok | 2026-11-18T18:13:42+00:00 |
| claude-professional | claude | colleague |  | 61% | 39% | 2026-11-21T07:59:59.655314+00:00 | ace-win-1 | oauth-api | ok | 2026-11-18T18:13:46+00:00 |
| codex-owner | codex | owner |  | 2% | 98% | 2026-11-25T16:31:50+00:00 | ace-win-2 | app-server-live | ok | 2026-11-18T18:13:50+00:00 |
| codex-professional | codex | colleague |  | 13% | 87% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-18T18:13:46+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
