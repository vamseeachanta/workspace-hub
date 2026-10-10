# AI account usage (fleet)

Generated 2026-10-10T05:13:27+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (62.0% weekly headroom) on ace-linux-1, ace-linux-2, gpu-claw -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-professional` (94.0% weekly headroom) on ace-win-1, ace-win-2

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 17% | 38% | 62% | 2026-10-10T14:00:00.278025+00:00 | ace-linux-2 | oauth-api |
| claude-professional | claude | colleague | 2% | 42% | 58% | 2026-10-10T07:59:59.774840+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 38% | 62% | 2026-10-14T04:04:15+00:00 | fleet-collector | app-server-live |
| codex-professional | codex | colleague |  | 6% | 94% | 2026-10-14T14:37:23+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| ace-win-2 | yes | claude-professional | codex-professional |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |

## Warnings

- gpu-claw: codex sample's weekly window reset at 2026-09-19T11:46:38+00:00; ignored
- ace-win-2: claude fingerprint 78d7e174f2d1 differs from claude-professional (c0c130b8018b)
- ace-win-2: codex fingerprint 78d7e174f2d1 differs from codex-professional (c0c130b8018b)
