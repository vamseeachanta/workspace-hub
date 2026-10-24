# AI account usage (fleet)

Generated 2026-10-24T00:13:33+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (0.0% weekly headroom) on ace-linux-1, ace-linux-2, gpu-claw -- every claude account is below 10% weekly headroom; defer marathons
- **codex**: `codex-owner` (86.0% weekly headroom) on ace-linux-1, ace-linux-2, fleet-collector, gpu-claw

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 0% | 100% | 0% | 2026-10-24T14:00:00.421965+00:00 | gpu-claw | oauth-api |
| claude-professional | claude | colleague |  |  |  |  |  | unavailable |
| codex-owner | codex | owner |  | 14% | 86% | 2026-10-30T17:41:09+00:00 | fleet-collector | app-server-live |
| codex-professional | codex | colleague |  |  |  |  |  | unavailable |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | no | claude-owner | codex-owner | exit 255 |
| ace-win-1 | no | claude-professional | codex-professional | exit 255 |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
