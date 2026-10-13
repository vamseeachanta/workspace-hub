# AI account usage (fleet)

Generated 2026-10-13T10:13:29+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (85.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (95.0% weekly headroom) on ace-win-1 -- within 15 pts of codex-owner: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 18% | 49% | 51% | 2026-10-17T13:59:59.562969+00:00 | ace-win-2 | oauth-api |
| claude-professional | claude | colleague | 0% | 15% | 85% | 2026-10-17T08:00:00.085954+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 8% | 92% | 2026-10-20T04:58:10+00:00 | ace-win-2 | app-server-live |
| codex-professional | codex | colleague |  | 5% | 95% | 2026-10-20T04:58:10+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |

## Warnings

- gpu-claw: codex sample's weekly window reset at 2026-09-19T11:46:38+00:00; ignored
