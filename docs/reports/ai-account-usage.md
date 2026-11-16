# AI account usage (fleet)

Generated 2026-11-16T17:13:58+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (65.0% weekly headroom) on ace-win-1 -- within 15 pts of claude-owner: stay on whichever host you are on
- **codex**: `codex-owner` (80.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector, gpu-claw

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 39% | 61% | 2026-11-21T13:59:59.651854+00:00 | ace-win-2 | oauth-api | ok | 2026-11-16T17:13:43+00:00 |
| claude-professional | claude | colleague |  | 35% | 65% | 2026-11-21T07:59:59.771838+00:00 | ace-win-1 | oauth-api | ok | 2026-11-16T17:13:47+00:00 |
| codex-owner | codex | owner |  | 20% | 80% | 2026-11-23T02:49:02+00:00 | ace-win-2 | app-server-live | ok | 2026-11-16T17:13:52+00:00 |
| codex-professional | codex | colleague |  | 40% | 60% | 2026-11-17T04:51:09+00:00 | ace-win-1 | app-server-live | ok | 2026-11-16T17:13:47+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
