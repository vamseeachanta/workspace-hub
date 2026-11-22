# AI account usage (fleet)

Generated 2026-11-22T02:14:02+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (99.0% weekly headroom) on ace-win-1 -- within 15 pts of claude-owner: stay on whichever host you are on
- **codex**: `codex-professional` (60.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 9% | 91% | 2026-11-28T14:00:00.705456+00:00 | ace-win-2 | oauth-api | ok | 2026-11-22T02:13:50+00:00 |
| claude-professional | claude | colleague |  | 1% | 99% | 2026-11-28T07:59:59.597645+00:00 | ace-win-1 | oauth-api | ok | 2026-11-22T02:13:53+00:00 |
| codex-owner | codex | owner |  | 97% | 3% | 2026-11-25T16:31:50+00:00 | ace-win-2 | app-server-live | ok | 2026-11-22T02:13:58+00:00 |
| codex-professional | codex | colleague |  | 40% | 60% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-22T02:13:53+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
