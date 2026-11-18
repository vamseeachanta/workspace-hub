# AI account usage (fleet)

Generated 2026-11-18T19:14:01+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (56.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw
- **codex**: `codex-owner` (94.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector, gpu-claw

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 44% | 56% | 2026-11-21T13:59:59.941525+00:00 | ace-win-2 | oauth-api | ok | 2026-11-18T19:13:48+00:00 |
| claude-professional | claude | colleague |  | 66% | 34% | 2026-11-21T08:00:00.336172+00:00 | ace-win-1 | oauth-api | ok | 2026-11-18T19:13:52+00:00 |
| codex-owner | codex | owner |  | 6% | 94% | 2026-11-25T16:31:50+00:00 | ace-win-2 | app-server-live | ok | 2026-11-18T19:13:57+00:00 |
| codex-professional | codex | colleague |  | 22% | 78% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-18T19:13:52+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
