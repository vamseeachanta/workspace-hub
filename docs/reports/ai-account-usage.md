# AI account usage (fleet)

Generated 2026-10-09T20:13:31+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (77.0% weekly headroom) on ace-win-1, ace-win-2 -- within 15 pts of claude-owner: stay on whichever host you are on
- **codex**: `codex-professional` (96.0% weekly headroom) on ace-win-1, ace-win-2

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 10% | 32% | 68% | 2026-10-10T14:00:00.119537+00:00 | ace-linux-1 | oauth-api |
| claude-professional | claude | colleague | 8% | 23% | 77% | 2026-10-10T07:59:59.516063+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 30% | 70% | 2026-10-14T04:04:15+00:00 | fleet-collector | app-server-live |
| codex-professional | codex | colleague |  | 4% | 96% | 2026-10-14T14:37:23+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| ace-win-2 | yes | claude-professional | codex-professional |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |

## Warnings

- gpu-claw: codex sample's weekly window reset at 2026-09-19T11:46:38+00:00; ignored
- ace-win-2: claude fingerprint 78d7e174f2d1 differs from claude-professional (c0c130b8018b)
- ace-win-2: codex fingerprint 78d7e174f2d1 differs from codex-professional (c0c130b8018b)
