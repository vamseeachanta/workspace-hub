# AI account usage (fleet)

Generated 2026-10-30T08:13:27+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (59.0% weekly headroom) on ace-win-1
- **codex**: `codex-owner` (41.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector, gpu-claw

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 1% | 94% | 6% | 2026-10-31T13:59:59.660309+00:00 | ace-win-2 | oauth-api |
| claude-professional | claude | colleague | 5% | 41% | 59% | 2026-10-31T08:00:00.322213+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 59% | 41% | 2026-11-04T06:35:47+00:00 | ace-win-2 | app-server-live |
| codex-professional | codex | colleague |  | 89% | 11% | 2026-11-04T06:40:53+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
