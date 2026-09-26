# AI account usage (fleet)

Generated 2026-09-26T19:13:39+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (97.0% weekly headroom) on ace-linux-1, ace-linux-2
- **codex**: `codex-owner` (99.0% weekly headroom) on ace-linux-1, ace-linux-2, fleet-collector -- within 15 pts of codex-professional: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 10% | 3% | 97% | 2026-10-03T14:00:00.085243+00:00 | ace-linux-1 | oauth-api |
| claude-professional | claude | colleague | 55% | 25% | 75% | 2026-10-03T08:00:00.429045+00:00 | ace-win-2 | oauth-api |
| codex-owner | codex | owner |  | 1% | 99% | 2026-10-03T17:19:42+00:00 | fleet-collector | app-server-live |
| codex-professional | codex | colleague |  | 2% | 98% | 2026-10-03T17:17:20+00:00 | ace-win-2 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-professional | codex-professional |  |
| ace-win-1 | no | claude-professional | codex-professional | exit 255 |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
