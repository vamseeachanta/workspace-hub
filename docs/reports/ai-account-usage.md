# AI account usage (fleet)

Generated 2026-10-15T13:13:28+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (79.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw
- **codex**: `codex-professional` (93.0% weekly headroom) on ace-win-1 -- within 15 pts of codex-owner: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 42% | 21% | 79% | 2026-10-17T14:00:00.279622+00:00 | ace-win-2 | oauth-api |
| claude-professional | claude | colleague | 15% | 65% | 35% | 2026-10-17T08:00:00.269114+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 17% | 83% | 2026-10-22T06:13:31+00:00 | ace-win-2 | app-server-live |
| codex-professional | codex | colleague |  | 7% | 93% | 2026-10-22T08:40:50+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
