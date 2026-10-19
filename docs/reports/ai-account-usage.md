# AI account usage (fleet)

Generated 2026-10-19T01:13:28+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (81.0% weekly headroom) on ace-linux-1, ace-linux-2, gpu-claw
- **codex**: `codex-owner` (59.0% weekly headroom) on ace-linux-1, ace-linux-2, fleet-collector, gpu-claw

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 5% | 19% | 81% | 2026-10-24T13:59:59.630590+00:00 | ace-linux-2 | oauth-api |
| claude-professional | claude | colleague |  |  |  |  |  | unavailable |
| codex-owner | codex | owner |  | 41% | 59% | 2026-10-24T20:40:38+00:00 | fleet-collector | app-server-live |
| codex-professional | codex | colleague |  |  |  |  |  | unavailable |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-win-2 | no | claude-owner | codex-owner | exit 255 |
| ace-win-1 | no | claude-professional | codex-professional | exit 255 |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
