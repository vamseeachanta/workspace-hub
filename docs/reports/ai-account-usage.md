# AI account usage (fleet)

Generated 2026-11-02T16:13:32+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (85.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2 -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-professional` (98.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 15% | 85% | 2026-11-07T14:00:00.474405+00:00 | ace-win-2 | oauth-api | ok | 2026-11-02T16:13:20+00:00 |
| claude-professional | claude | colleague |  | 17% | 83% | 2026-11-07T08:00:00.326953+00:00 | ace-win-1 | oauth-api | ok | 2026-11-02T16:13:23+00:00 |
| codex-owner | codex | owner |  | 80% | 20% | 2026-11-04T06:35:47+00:00 | ace-win-2 | app-server-live | ok | 2026-11-02T16:13:28+00:00 |
| codex-professional | codex | colleague |  | 2% | 98% | 2026-11-08T11:32:57+00:00 | ace-win-1 | app-server-live | ok | 2026-11-02T16:13:23+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
