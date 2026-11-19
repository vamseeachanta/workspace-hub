# AI account usage (fleet)

Generated 2026-11-19T07:14:26+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (42.0% weekly headroom) on ace-linux-1, ace-linux-2
- **codex**: `codex-owner` (67.0% weekly headroom) on ace-linux-1, ace-linux-2, fleet-collector

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 58% | 42% | 2026-11-21T14:00:00.211066+00:00 | ace-linux-2 | oauth-api | ok | 2026-11-19T07:13:53+00:00 |
| claude-professional | claude | colleague |  |  |  |  |  | unavailable | unreachable | 2026-11-19T07:14:01+00:00 |
| codex-owner | codex | owner |  | 33% | 67% | 2026-11-25T16:31:50+00:00 | fleet-collector | app-server-live | ok | 2026-11-19T07:14:23+00:00 |
| codex-professional | codex | colleague |  |  |  |  |  | unavailable | unreachable | 2026-11-19T07:14:01+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | no | claude-owner | codex-owner | exit 255 |
| ace-win-1 | no | claude-professional | codex-professional | exit 255 |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
