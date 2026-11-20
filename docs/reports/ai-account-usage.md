# AI account usage (fleet)

Generated 2026-11-20T08:14:04+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (30.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2 -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-professional` (66.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 70% | 30% | 2026-11-21T13:59:59.888226+00:00 | ace-win-2 | oauth-api | ok | 2026-11-20T08:13:52+00:00 |
| claude-professional | claude | colleague |  | 81% | 19% | 2026-11-21T08:00:00.349959+00:00 | ace-win-1 | oauth-api | ok | 2026-11-20T08:13:55+00:00 |
| codex-owner | codex | owner |  | 61% | 39% | 2026-11-25T16:31:50+00:00 | ace-win-2 | app-server-live | ok | 2026-11-20T08:14:00+00:00 |
| codex-professional | codex | colleague |  | 34% | 66% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-20T08:13:55+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
