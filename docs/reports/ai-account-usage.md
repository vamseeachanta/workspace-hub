# AI account usage (fleet)

Generated 2026-11-26T17:13:54+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (74.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (37.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 98% | 2% | 2026-11-28T13:59:59.610553+00:00 | ace-win-2 | oauth-api | ok | 2026-11-26T17:13:41+00:00 |
| claude-professional | claude | colleague |  | 26% | 74% | 2026-11-28T08:00:00.164875+00:00 | ace-win-1 | oauth-api | ok | 2026-11-26T17:13:46+00:00 |
| codex-owner | codex | owner |  | 100% | 0% | 2026-11-29T17:50:08+00:00 | ace-win-2 | app-server-live | ok | 2026-11-26T17:13:51+00:00 |
| codex-professional | codex | colleague |  | 63% | 37% | 2026-12-02T10:35:47+00:00 | ace-win-1 | app-server-live | ok | 2026-11-26T17:13:46+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
