# AI account usage (fleet)

Generated 2026-11-28T03:13:50+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (57.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (100.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 100% | 0% | 2026-11-28T13:59:59.879529+00:00 | ace-win-2 | oauth-api | ok | 2026-11-28T03:13:39+00:00 |
| claude-professional | claude | colleague |  | 43% | 57% | 2026-11-28T08:00:00.176044+00:00 | ace-win-1 | oauth-api | ok | 2026-11-28T03:13:43+00:00 |
| codex-owner | codex | owner |  | 50% | 50% | 2026-12-03T18:41:43+00:00 | ace-win-2 | app-server-live | ok | 2026-11-28T03:13:47+00:00 |
| codex-professional | codex | colleague |  | 0% | 100% | 2026-12-05T01:20:24+00:00 | ace-win-1 | app-server-live | ok | 2026-11-28T03:13:43+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
