# AI account usage (fleet)

Generated 2026-11-19T18:14:12+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (36.0% weekly headroom) on ace-linux-1, ace-linux-2 -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-professional` (69.0% weekly headroom) on ace-win-1 -- within 15 pts of codex-owner: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 64% | 36% | 2026-11-21T14:00:00.177231+00:00 | ace-linux-2 | oauth-api | ok | 2026-11-19T18:13:53+00:00 |
| claude-professional | claude | colleague |  | 73% | 27% | 2026-11-21T07:59:59.565902+00:00 | ace-win-1 | oauth-api | ok | 2026-11-19T18:14:01+00:00 |
| codex-owner | codex | owner |  | 45% | 55% | 2026-11-25T16:31:50+00:00 | fleet-collector | app-server-live | ok | 2026-11-19T18:14:08+00:00 |
| codex-professional | codex | colleague |  | 31% | 69% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-19T18:14:01+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | no | claude-owner | codex-owner | exit 255 |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
