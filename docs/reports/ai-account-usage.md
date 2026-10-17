# AI account usage (fleet)

Generated 2026-10-17T00:13:55+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: no live sample for any account
- **codex**: `codex-owner` (18.0% weekly headroom) on fleet-collector

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  |  |  |  |  | unavailable |
| claude-professional | claude | colleague |  |  |  |  |  | unavailable |
| codex-owner | codex | owner |  | 82% | 18% | 2026-10-22T06:13:31+00:00 | fleet-collector | app-server-live |
| codex-professional | codex | colleague |  |  |  |  |  | unavailable |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | no | claude-owner | codex-owner | exit 255 |
| ace-linux-2 | no | claude-owner | codex-owner | exit 255 |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | no | claude-owner | codex-owner | exit 255 |
| ace-win-1 | no | claude-professional | codex-professional | exit 255 |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
