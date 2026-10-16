# AI account usage (fleet)

Generated 2026-10-16T19:19:36+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (21.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw
- **codex**: `codex-professional` (62.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 8% | 79% | 21% | 2026-10-17T14:00:00.252094+00:00 | ace-win-2 | oauth-api |
| claude-professional | claude | colleague | 0% | 100% | 0% | 2026-10-17T07:59:59.798666+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 78% | 22% | 2026-10-22T06:13:31+00:00 | ace-win-2 | app-server-live |
| codex-professional | codex | colleague |  | 38% | 62% | 2026-10-22T08:40:50+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
