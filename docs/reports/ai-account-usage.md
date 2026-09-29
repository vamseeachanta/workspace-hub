# AI account usage (fleet)

Generated 2026-09-29T14:13:26+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (57.0% weekly headroom) on ace-linux-1, ace-linux-2, gpu-claw
- **codex**: `codex-owner` (96.0% weekly headroom) on ace-linux-1, ace-linux-2, fleet-collector, gpu-claw -- within 15 pts of codex-professional: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 20% | 43% | 57% | 2026-10-03T14:00:00.260198+00:00 | ace-linux-2 | oauth-api |
| claude-professional | claude | colleague |  |  |  |  |  | unavailable |
| codex-owner | codex | owner |  | 4% | 96% | 2026-10-03T17:19:42+00:00 | fleet-collector | app-server-live |
| codex-professional | codex | colleague |  | 16% | 84% | 2026-10-03T17:17:20+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-win-2 | yes | claude-professional | codex-professional |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |

## Warnings

- ace-linux-2: codex sample's weekly window reset at 2026-08-21T11:50:27+00:00; ignored
- ace-win-2: claude fingerprint 78d7e174f2d1 differs from claude-professional (c0c130b8018b)
- ace-win-1: claude fingerprint 78d7e174f2d1 differs from claude-professional (c0c130b8018b)
