# AI account usage (fleet)

Generated 2026-10-31T16:13:30+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (99.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-owner` (30.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector, gpu-claw

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 1% | 99% | 2026-11-07T14:00:00.998509+00:00 | ace-win-2 | oauth-api | ok | 2026-10-31T16:13:18+00:00 |
| claude-professional | claude | colleague |  | 3% | 97% | 2026-11-07T08:00:00.106164+00:00 | ace-win-1 | oauth-api | ok | 2026-10-31T16:13:21+00:00 |
| codex-owner | codex | owner |  | 70% | 30% | 2026-11-04T06:35:47+00:00 | ace-win-2 | app-server-live | ok | 2026-10-31T16:13:26+00:00 |
| codex-professional | codex | colleague |  | 96% | 4% | 2026-11-04T06:40:53+00:00 | ace-win-1 | app-server-live | ok | 2026-10-31T16:13:21+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
