# AI account usage (fleet)

Generated 2026-11-07T02:13:57+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (35.0% weekly headroom) on ace-win-1 -- within 15 pts of claude-owner: stay on whichever host you are on
- **codex**: `codex-professional` (88.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 74% | 26% | 2026-11-07T14:00:00.500563+00:00 | ace-win-2 | oauth-api | ok | 2026-11-07T02:13:45+00:00 |
| claude-professional | claude | colleague |  | 65% | 35% | 2026-11-07T08:00:00.249619+00:00 | ace-win-1 | oauth-api | ok | 2026-11-07T02:13:49+00:00 |
| codex-owner | codex | owner |  | 64% | 36% | 2026-11-11T06:35:56+00:00 | ace-win-2 | app-server-live | ok | 2026-11-07T02:13:54+00:00 |
| codex-professional | codex | colleague |  | 12% | 88% | 2026-11-08T11:32:57+00:00 | ace-win-1 | app-server-live | ok | 2026-11-07T02:13:49+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
