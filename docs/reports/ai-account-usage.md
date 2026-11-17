# AI account usage (fleet)

Generated 2026-11-17T16:13:54+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (50.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (97.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 97% | 3% | 2026-11-21T14:00:00.291648+00:00 | ace-win-2 | oauth-api | ok | 2026-11-17T16:13:41+00:00 |
| claude-professional | claude | colleague |  | 50% | 50% | 2026-11-21T08:00:00.336241+00:00 | ace-win-1 | oauth-api | ok | 2026-11-17T16:13:44+00:00 |
| codex-owner | codex | owner |  | 57% | 43% | 2026-11-23T02:49:02+00:00 | ace-win-2 | app-server-live | ok | 2026-11-17T16:13:51+00:00 |
| codex-professional | codex | colleague |  | 3% | 97% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-17T16:13:44+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
