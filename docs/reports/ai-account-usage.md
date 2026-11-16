# AI account usage (fleet)

Generated 2026-11-16T21:14:09+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (59.0% weekly headroom) on ace-win-1
- **codex**: `codex-owner` (64.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector, gpu-claw

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 58% | 42% | 2026-11-21T14:00:00.866713+00:00 | ace-win-2 | oauth-api | ok | 2026-11-16T21:13:51+00:00 |
| claude-professional | claude | colleague |  | 41% | 59% | 2026-11-21T07:59:59.550292+00:00 | ace-win-1 | oauth-api | ok | 2026-11-16T21:13:58+00:00 |
| codex-owner | codex | owner |  | 36% | 64% | 2026-11-23T02:49:02+00:00 | ace-win-2 | app-server-live | ok | 2026-11-16T21:14:05+00:00 |
| codex-professional | codex | colleague |  | 55% | 45% | 2026-11-17T04:51:09+00:00 | ace-win-1 | app-server-live | ok | 2026-11-16T21:13:58+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
