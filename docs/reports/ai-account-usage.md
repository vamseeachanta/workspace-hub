# AI account usage (fleet)

Generated 2026-11-01T05:13:32+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (95.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2 -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-owner` (26.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 5% | 95% | 2026-11-07T14:00:00.739035+00:00 | ace-win-2 | oauth-api | ok | 2026-11-01T05:13:19+00:00 |
| claude-professional | claude | colleague |  | 8% | 92% | 2026-11-07T07:59:59.611074+00:00 | ace-win-1 | oauth-api | ok | 2026-11-01T05:13:23+00:00 |
| codex-owner | codex | owner |  | 74% | 26% | 2026-11-04T06:35:47+00:00 | ace-win-2 | app-server-live | ok | 2026-11-01T05:13:30+00:00 |
| codex-professional | codex | colleague |  | 99% | 1% | 2026-11-04T06:40:53+00:00 | ace-win-1 | app-server-live | ok | 2026-11-01T05:13:23+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
