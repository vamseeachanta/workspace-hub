# AI account usage (fleet)

Generated 2026-10-28T18:13:45+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: no live sample for any account
- **codex**: `codex-owner` (85.0% weekly headroom) on ace-linux-1, ace-linux-2, fleet-collector -- within 15 pts of codex-professional: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  |  |  |  |  | unavailable |
| claude-professional | claude | colleague |  |  |  |  |  | unavailable |
| codex-owner | codex | owner |  | 15% | 85% | 2026-11-04T06:35:47+00:00 | fleet-collector | app-server-live |
| codex-professional | codex | colleague |  | 22% | 78% | 2026-11-04T06:40:53+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | no | claude-owner | codex-owner | exit 255 |
| ace-win-1 | yes | claude-professional | codex-professional | claude: credentials file has no accessToken |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
