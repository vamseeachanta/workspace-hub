# AI account usage (fleet)

Generated 2026-11-19T17:14:22+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (36.0% weekly headroom) on ace-linux-1, ace-linux-2
- **codex**: `codex-owner` (55.0% weekly headroom) on ace-linux-1, ace-linux-2, fleet-collector

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 64% | 36% | 2026-11-21T14:00:00.094046+00:00 | ace-linux-2 | oauth-api | ok | 2026-11-19T17:13:50+00:00 |
| claude-professional | claude | colleague |  |  |  |  |  | unavailable | unreachable | 2026-11-19T17:13:58+00:00 |
| codex-owner | codex | owner |  | 45% | 55% | 2026-11-25T16:31:50+00:00 | fleet-collector | app-server-live | ok | 2026-11-19T17:14:19+00:00 |
| codex-professional | codex | colleague |  |  |  |  |  | unavailable | unreachable | 2026-11-19T17:13:58+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | no | claude-owner | codex-owner | exit 255 |
| ace-win-1 | no | claude-professional | codex-professional | exit 255 |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
