# AI account usage (fleet)

Generated 2026-10-08T10:13:33+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (84.0% weekly headroom) on ace-linux-1, ace-linux-2
- **codex**: `codex-professional` (100.0% weekly headroom) on ace-win-1, ace-win-2 -- within 15 pts of codex-owner: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 0% | 16% | 84% | 2026-10-10T13:59:59.677993+00:00 | ace-linux-2 | oauth-api |
| claude-professional | claude | colleague |  |  |  |  |  | unavailable |
| codex-owner | codex | owner |  | 6% | 94% | 2026-10-14T04:04:15+00:00 | fleet-collector | app-server-live |
| codex-professional | codex | colleague |  | 0% | 100% | 2026-10-14T14:37:23+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-professional | codex-professional |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |

## Warnings

- ace-win-2: claude fingerprint 78d7e174f2d1 differs from claude-professional (c0c130b8018b)
- ace-win-2: codex fingerprint 78d7e174f2d1 differs from codex-professional (c0c130b8018b)
- ace-win-1: claude fingerprint 78d7e174f2d1 differs from claude-professional (c0c130b8018b)
