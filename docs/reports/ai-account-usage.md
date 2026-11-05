# AI account usage (fleet)

Generated 2026-11-05T00:13:36+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (70.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (90.0% weekly headroom) on ace-win-1 -- within 15 pts of codex-owner: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 53% | 47% | 2026-11-07T14:00:00.415605+00:00 | ace-win-2 | oauth-api | ok | 2026-11-05T00:13:22+00:00 |
| claude-professional | claude | colleague |  | 30% | 70% | 2026-11-07T07:59:59.614454+00:00 | ace-win-1 | oauth-api | ok | 2026-11-05T00:13:26+00:00 |
| codex-owner | codex | owner |  | 19% | 81% | 2026-11-11T06:35:56+00:00 | ace-win-2 | app-server-live | ok | 2026-11-05T00:13:33+00:00 |
| codex-professional | codex | colleague |  | 10% | 90% | 2026-11-08T11:32:57+00:00 | ace-win-1 | app-server-live | ok | 2026-11-05T00:13:26+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
