# AI account usage (fleet)

Generated 2026-11-20T10:13:56+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (30.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2 -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-professional` (65.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 70% | 30% | 2026-11-21T14:00:00.123211+00:00 | ace-win-2 | oauth-api | ok | 2026-11-20T10:13:44+00:00 |
| claude-professional | claude | colleague |  | 82% | 18% | 2026-11-21T08:00:00.443986+00:00 | ace-win-1 | oauth-api | ok | 2026-11-20T10:13:48+00:00 |
| codex-owner | codex | owner |  | 62% | 38% | 2026-11-25T16:31:50+00:00 | ace-win-2 | app-server-live | ok | 2026-11-20T10:13:53+00:00 |
| codex-professional | codex | colleague |  | 35% | 65% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-20T10:13:48+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
