# AI account usage (fleet)

Generated 2026-11-27T00:13:59+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (69.0% weekly headroom) on ace-win-1
- **codex**: `codex-owner` (93.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector, gpu-claw

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 99% | 1% | 2026-11-28T13:59:59.882821+00:00 | ace-win-2 | oauth-api | ok | 2026-11-27T00:13:47+00:00 |
| claude-professional | claude | colleague |  | 31% | 69% | 2026-11-28T07:59:59.974210+00:00 | ace-win-1 | oauth-api | ok | 2026-11-27T00:13:51+00:00 |
| codex-owner | codex | owner |  | 7% | 93% | 2026-12-03T18:41:43+00:00 | ace-win-2 | app-server-live | ok | 2026-11-27T00:13:56+00:00 |
| codex-professional | codex | colleague |  | 80% | 20% | 2026-12-02T10:35:47+00:00 | ace-win-1 | app-server-live | ok | 2026-11-27T00:13:51+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
