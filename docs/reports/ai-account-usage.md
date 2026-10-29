# AI account usage (fleet)

Generated 2026-10-29T17:13:36+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (61.0% weekly headroom) on ace-win-1
- **codex**: `codex-owner` (53.0% weekly headroom) on ace-linux-1, ace-linux-2, fleet-collector, gpu-claw

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 4% | 92% | 8% | 2026-10-31T14:00:00.466883+00:00 | gpu-claw | oauth-api |
| claude-professional | claude | colleague | 0% | 39% | 61% | 2026-10-31T08:00:00.446664+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 47% | 53% | 2026-11-04T06:35:47+00:00 | fleet-collector | app-server-live |
| codex-professional | codex | colleague |  | 87% | 13% | 2026-11-04T06:40:53+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | no | claude-owner | codex-owner | exit 255 |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
