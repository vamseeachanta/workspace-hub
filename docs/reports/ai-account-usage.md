# AI account usage (fleet)

Generated 2026-10-16T12:13:44+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (29.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2
- **codex**: `codex-professional` (70.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 3% | 71% | 29% | 2026-10-17T14:00:00.066001+00:00 | ace-win-2 | oauth-api |
| claude-professional | claude | colleague | 27% | 100% | 0% | 2026-10-17T08:00:00.148208+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 73% | 27% | 2026-10-22T06:13:31+00:00 | ace-win-2 | app-server-live |
| codex-professional | codex | colleague |  | 30% | 70% | 2026-10-22T08:40:50+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
