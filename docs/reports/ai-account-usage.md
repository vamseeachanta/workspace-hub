# AI account usage (fleet)

Generated 2026-11-17T09:14:08+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (53.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (100.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 86% | 14% | 2026-11-21T14:00:00.407544+00:00 | gpu-claw | oauth-api | ok | 2026-11-17T09:13:44+00:00 |
| claude-professional | claude | colleague |  | 47% | 53% | 2026-11-21T07:59:59.578523+00:00 | ace-win-1 | oauth-api | ok | 2026-11-17T09:13:59+00:00 |
| codex-owner | codex | owner |  | 52% | 48% | 2026-11-23T02:49:02+00:00 | fleet-collector | app-server-live | ok | 2026-11-17T09:14:05+00:00 |
| codex-professional | codex | colleague |  | 0% | 100% | 2026-11-24T09:14:06+00:00 | ace-win-1 | app-server-live | ok | 2026-11-17T09:13:59+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner |  |
| ace-win-2 | no | claude-owner | codex-owner | exit 255 |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
