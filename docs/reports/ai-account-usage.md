# AI account usage (fleet)

Generated 2026-11-19T01:14:08+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (49.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2
- **codex**: `codex-owner` (76.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector -- within 15 pts of codex-professional: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 51% | 49% | 2026-11-21T14:00:00.272066+00:00 | ace-win-2 | oauth-api | ok | 2026-11-19T01:13:55+00:00 |
| claude-professional | claude | colleague |  | 72% | 28% | 2026-11-21T08:00:00.442836+00:00 | ace-win-1 | oauth-api | ok | 2026-11-19T01:13:59+00:00 |
| codex-owner | codex | owner |  | 24% | 76% | 2026-11-25T16:31:50+00:00 | ace-win-2 | app-server-live | ok | 2026-11-19T01:14:04+00:00 |
| codex-professional | codex | colleague |  | 29% | 71% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-19T01:13:59+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
