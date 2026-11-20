# AI account usage (fleet)

Generated 2026-11-20T23:14:24+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: no live sample for any account
- **codex**: `codex-owner` (22.0% weekly headroom) on fleet-collector

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  |  |  |  |  | unavailable | unreachable | 2026-11-20T23:14:05+00:00 |
| claude-professional | claude | colleague |  |  |  |  |  | unavailable | unreachable | 2026-11-20T23:14:13+00:00 |
| codex-owner | codex | owner |  | 78% | 22% | 2026-11-25T16:31:50+00:00 | fleet-collector | app-server-live | ok | 2026-11-20T23:14:21+00:00 |
| codex-professional | codex | colleague |  |  |  |  |  | unavailable | unreachable | 2026-11-20T23:14:13+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | no | claude-owner | codex-owner | exit 255 |
| ace-linux-2 | no | claude-owner | codex-owner | exit 255 |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | no | claude-owner | codex-owner | exit 255 |
| ace-win-1 | no | claude-professional | codex-professional | exit 255 |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
