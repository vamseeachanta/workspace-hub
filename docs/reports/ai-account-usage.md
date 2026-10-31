# AI account usage (fleet)

Generated 2026-10-31T01:13:31+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (48.0% weekly headroom) on ace-win-1
- **codex**: `codex-owner` (32.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector, gpu-claw

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 2% | 97% | 3% | 2026-10-31T14:00:00.128786+00:00 | ace-win-2 | oauth-api | ok | 2026-10-31T01:13:17+00:00 |
| claude-professional | claude | colleague | 0% | 52% | 48% | 2026-10-31T08:00:00.503931+00:00 | ace-win-1 | oauth-api | ok | 2026-10-31T01:13:21+00:00 |
| codex-owner | codex | owner |  | 68% | 32% | 2026-11-04T06:35:47+00:00 | ace-win-2 | app-server-live | ok | 2026-10-31T01:13:26+00:00 |
| codex-professional | codex | colleague |  | 94% | 6% | 2026-11-04T06:40:53+00:00 | ace-win-1 | app-server-live | ok | 2026-10-31T01:13:21+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
