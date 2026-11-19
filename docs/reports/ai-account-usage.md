# AI account usage (fleet)

Generated 2026-11-19T23:14:10+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (36.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2 -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-professional` (67.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 64% | 36% | 2026-11-21T13:59:59.639918+00:00 | ace-win-2 | oauth-api | ok | 2026-11-19T23:13:57+00:00 |
| claude-professional | claude | colleague |  | 74% | 26% | 2026-11-21T08:00:00.205576+00:00 | ace-win-1 | oauth-api | ok | 2026-11-19T23:14:01+00:00 |
| codex-owner | codex | owner |  | 50% | 50% | 2026-11-25T16:31:50+00:00 | ace-win-2 | app-server-live | ok | 2026-11-19T23:14:07+00:00 |
| codex-professional | codex | colleague |  | 33% | 67% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-19T23:14:01+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
