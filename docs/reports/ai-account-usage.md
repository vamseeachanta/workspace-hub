# AI account usage (fleet)

Generated 2026-11-18T17:14:09+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (61.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, gpu-claw
- **codex**: `codex-owner` (99.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2, fleet-collector, gpu-claw -- within 15 pts of codex-professional: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 39% | 61% | 2026-11-21T14:00:00.608553+00:00 | ace-win-2 | oauth-api | ok | 2026-11-18T17:13:55+00:00 |
| claude-professional | claude | colleague |  | 60% | 40% | 2026-11-21T08:00:00.140023+00:00 | ace-win-1 | oauth-api | ok | 2026-11-18T17:13:58+00:00 |
| codex-owner | codex | owner |  | 1% | 99% | 2026-11-25T16:31:50+00:00 | ace-win-2 | app-server-live | ok | 2026-11-18T17:14:06+00:00 |
| codex-professional | codex | colleague |  | 9% | 91% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-18T17:13:58+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
