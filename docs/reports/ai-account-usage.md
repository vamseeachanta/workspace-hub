# AI account usage (fleet)

Generated 2026-10-31T10:13:24+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (100.0% weekly headroom) on ace-win-1
- **codex**: `codex-owner` (31.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector, gpu-claw

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 98% | 2% | 2026-10-31T13:59:59.843363+00:00 | ace-win-2 | oauth-api | ok | 2026-10-31T10:13:11+00:00 |
| claude-professional | claude | colleague |  | 0% | 100% | 2026-11-07T08:00:00.058283+00:00 | ace-win-1 | oauth-api | ok | 2026-10-31T10:13:15+00:00 |
| codex-owner | codex | owner |  | 69% | 31% | 2026-11-04T06:35:47+00:00 | ace-win-2 | app-server-live | ok | 2026-10-31T10:13:20+00:00 |
| codex-professional | codex | colleague |  | 95% | 5% | 2026-11-04T06:40:53+00:00 | ace-win-1 | app-server-live | ok | 2026-10-31T10:13:15+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
