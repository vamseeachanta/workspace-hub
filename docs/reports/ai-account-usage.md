# AI account usage (fleet)

Generated 2026-11-02T10:13:37+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (89.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2 -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-professional` (98.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 11% | 89% | 2026-11-07T13:59:59.681799+00:00 | ace-win-2 | oauth-api | ok | 2026-11-02T10:13:26+00:00 |
| claude-professional | claude | colleague |  | 14% | 86% | 2026-11-07T08:00:00.149915+00:00 | ace-win-1 | oauth-api | ok | 2026-11-02T10:13:30+00:00 |
| codex-owner | codex | owner |  | 78% | 22% | 2026-11-04T06:35:47+00:00 | ace-win-2 | app-server-live | ok | 2026-11-02T10:13:35+00:00 |
| codex-professional | codex | colleague |  | 2% | 98% | 2026-11-08T11:32:57+00:00 | ace-win-1 | app-server-live | ok | 2026-11-02T10:13:30+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
