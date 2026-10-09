# AI account usage (fleet)

Generated 2026-10-09T13:13:44+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (85.0% weekly headroom) on ace-win-1, ace-win-2 -- within 15 pts of claude-owner: stay on whichever host you are on
- **codex**: `codex-professional` (97.0% weekly headroom) on ace-win-1, ace-win-2 -- within 15 pts of codex-owner: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 5% | 26% | 74% | 2026-10-10T14:00:00.013102+00:00 | ace-linux-2 | oauth-api |
| claude-professional | claude | colleague | 3% | 15% | 85% | 2026-10-10T08:00:00.036395+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 15% | 85% | 2026-10-14T04:04:15+00:00 | fleet-collector | app-server-live |
| codex-professional | codex | colleague |  | 3% | 97% | 2026-10-14T14:37:23+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-professional | codex-professional |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |

## Warnings

- ace-win-2: claude fingerprint 78d7e174f2d1 differs from claude-professional (c0c130b8018b)
- ace-win-2: codex fingerprint 78d7e174f2d1 differs from codex-professional (c0c130b8018b)
