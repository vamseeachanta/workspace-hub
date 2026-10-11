# AI account usage (fleet)

Generated 2026-10-11T09:13:36+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (98.0% weekly headroom) on ace-linux-1, ace-linux-2 -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-owner` (100.0% weekly headroom) on ace-linux-1, ace-linux-2, fleet-collector -- within 15 pts of codex-professional: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 0% | 2% | 98% | 2026-10-17T14:00:00.104972+00:00 | ace-linux-2 | oauth-api |
| claude-professional | claude | colleague | 0% | 10% | 90% | 2026-10-17T08:00:00.328414+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 0% | 100% | 2026-10-18T09:13:36+00:00 | fleet-collector | app-server-live |
| codex-professional | codex | colleague |  | 0% | 100% | 2026-10-18T09:13:33+00:00 | ace-win-1 | app-server-live |

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
