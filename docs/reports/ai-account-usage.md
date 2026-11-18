# AI account usage (fleet)

Generated 2026-11-18T20:14:06+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (54.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2
- **codex**: `codex-owner` (88.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector -- within 15 pts of codex-professional: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 46% | 54% | 2026-11-21T13:59:59.957652+00:00 | ace-win-2 | oauth-api | ok | 2026-11-18T20:13:55+00:00 |
| claude-professional | claude | colleague |  | 67% | 33% | 2026-11-21T08:00:00.354377+00:00 | ace-win-1 | oauth-api | ok | 2026-11-18T20:13:58+00:00 |
| codex-owner | codex | owner |  | 12% | 88% | 2026-11-25T16:31:50+00:00 | ace-win-2 | app-server-live | ok | 2026-11-18T20:14:03+00:00 |
| codex-professional | codex | colleague |  | 23% | 77% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-18T20:13:58+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
