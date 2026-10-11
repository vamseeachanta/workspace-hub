# AI account usage (fleet)

Generated 2026-10-11T04:13:33+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (90.0% weekly headroom) on ace-win-1, ace-win-2
- **codex**: `codex-owner` (100.0% weekly headroom) on ace-linux-1, ace-linux-2, fleet-collector -- within 15 pts of codex-professional: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  |  |  |  |  | unavailable |
| claude-professional | claude | colleague | 7% | 10% | 90% | 2026-10-17T07:59:59.933200+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 0% | 100% | 2026-10-18T04:13:34+00:00 | fleet-collector | app-server-live |
| codex-professional | codex | colleague |  | 0% | 100% | 2026-10-18T04:13:30+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-professional | codex-professional |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |

## Warnings

- ace-win-2: claude fingerprint 78d7e174f2d1 differs from claude-professional (c0c130b8018b)
- ace-win-2: codex fingerprint 78d7e174f2d1 differs from codex-professional (c0c130b8018b)
