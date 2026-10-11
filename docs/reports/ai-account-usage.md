# AI account usage (fleet)

Generated 2026-10-11T23:13:31+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (91.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-professional` (100.0% weekly headroom) on ace-win-1 -- within 15 pts of codex-owner: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 11% | 9% | 91% | 2026-10-17T13:59:59.669160+00:00 | ace-win-2 | oauth-api |
| claude-professional | claude | colleague | 4% | 13% | 87% | 2026-10-17T07:59:59.810280+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 9% | 91% | 2026-10-18T12:05:07+00:00 | ace-win-2 | app-server-live |
| codex-professional | codex | colleague |  | 0% | 100% | 2026-10-18T21:10:03+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |

## Warnings

- gpu-claw: codex sample's weekly window reset at 2026-09-19T11:46:38+00:00; ignored
