# AI account usage (fleet)

Generated 2026-11-22T23:14:06+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (97.0% weekly headroom) on ace-win-1
- **codex**: `codex-owner` (96.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector, gpu-claw

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 42% | 58% | 2026-11-28T14:00:00.347523+00:00 | ace-win-2 | oauth-api | ok | 2026-11-22T23:13:52+00:00 |
| claude-professional | claude | colleague |  | 3% | 97% | 2026-11-28T07:59:59.882103+00:00 | ace-win-1 | oauth-api | ok | 2026-11-22T23:13:57+00:00 |
| codex-owner | codex | owner |  | 4% | 96% | 2026-11-29T17:50:08+00:00 | ace-win-2 | app-server-live | ok | 2026-11-22T23:14:03+00:00 |
| codex-professional | codex | colleague |  | 53% | 47% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-22T23:13:57+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
