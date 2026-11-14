# AI account usage (fleet)

Generated 2026-11-14T07:13:57+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (1.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw -- every claude account is below 10% weekly headroom; defer marathons
- **codex**: `codex-professional` (69.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 99% | 1% | 2026-11-14T13:59:59.913331+00:00 | ace-win-2 | oauth-api | ok | 2026-11-14T07:13:46+00:00 |
| claude-professional | claude | colleague |  |  |  |  |  | unavailable | auth-expired | 2026-11-14T07:13:50+00:00 |
| codex-owner | codex | owner |  | 76% | 24% | 2026-11-18T06:36:36+00:00 | ace-win-2 | app-server-live | ok | 2026-11-14T07:13:54+00:00 |
| codex-professional | codex | colleague |  | 31% | 69% | 2026-11-17T04:51:09+00:00 | ace-win-1 | app-server-live | ok | 2026-11-14T07:13:50+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional | claude: access token expired; a Claude Code session on this host will refresh it |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
