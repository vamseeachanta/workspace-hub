# AI account usage (fleet)

Generated 2026-10-13T02:13:37+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (85.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (83.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 14% | 35% | 65% | 2026-10-17T13:59:59.799709+00:00 | ace-win-2 | oauth-api |
| claude-professional | claude | colleague | 0% | 15% | 85% | 2026-10-17T08:00:00.144796+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 48% | 52% | 2026-10-18T12:05:07+00:00 | ace-win-2 | app-server-live |
| codex-professional | codex | colleague |  | 17% | 83% | 2026-10-18T21:10:03+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
