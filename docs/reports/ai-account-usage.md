# AI account usage (fleet)

Generated 2026-11-21T16:14:10+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (100.0% weekly headroom) on ace-win-1 -- within 15 pts of claude-owner: stay on whichever host you are on
- **codex**: `codex-professional` (62.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 1% | 99% | 2026-11-28T13:59:59.604306+00:00 | ace-win-2 | oauth-api | ok | 2026-11-21T16:13:57+00:00 |
| claude-professional | claude | colleague |  | 0% | 100% | 2026-11-28T07:59:59.634734+00:00 | ace-win-1 | oauth-api | ok | 2026-11-21T16:14:00+00:00 |
| codex-owner | codex | owner |  | 88% | 12% | 2026-11-25T16:31:50+00:00 | ace-win-2 | app-server-live | ok | 2026-11-21T16:14:06+00:00 |
| codex-professional | codex | colleague |  | 38% | 62% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-21T16:14:00+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
