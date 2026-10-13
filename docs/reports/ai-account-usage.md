# AI account usage (fleet)

Generated 2026-10-13T23:13:42+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (77.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (86.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 4% | 63% | 37% | 2026-10-17T14:00:00.102228+00:00 | ace-win-2 | oauth-api |
| claude-professional | claude | colleague | 18% | 23% | 77% | 2026-10-17T07:59:59.701740+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 34% | 66% | 2026-10-20T04:58:10+00:00 | ace-win-2 | app-server-live |
| codex-professional | codex | colleague |  | 14% | 86% | 2026-10-20T04:58:10+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |

## Warnings

- gpu-claw: codex sample's weekly window reset at 2026-09-19T11:46:38+00:00; ignored
