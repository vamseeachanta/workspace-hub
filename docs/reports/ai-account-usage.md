# AI account usage (fleet)

Generated 2026-11-17T20:14:12+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (90.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw
- **codex**: `codex-professional` (94.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 10% | 90% | 2026-11-21T14:00:00.817056+00:00 | ace-win-2 | oauth-api | ok | 2026-11-17T20:13:54+00:00 |
| claude-professional | claude | colleague |  | 51% | 49% | 2026-11-21T08:00:00.489613+00:00 | ace-win-1 | oauth-api | ok | 2026-11-17T20:14:00+00:00 |
| codex-owner | codex | owner |  | 61% | 39% | 2026-11-23T02:49:02+00:00 | ace-win-2 | app-server-live | ok | 2026-11-17T20:14:08+00:00 |
| codex-professional | codex | colleague |  | 6% | 94% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-17T20:14:00+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
