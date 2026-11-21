# AI account usage (fleet)

Generated 2026-11-21T04:14:05+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (13.0% weekly headroom) on ace-linux-1, ace-linux-2, ace-win-2 -- within 15 pts of claude-professional: stay on whichever host you are on
- **codex**: `codex-professional` (63.0% weekly headroom) on ace-win-1

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 87% | 13% | 2026-11-21T14:00:00.064398+00:00 | ace-win-2 | oauth-api | ok | 2026-11-21T04:13:53+00:00 |
| claude-professional | claude | colleague |  | 92% | 8% | 2026-11-21T07:59:59.697109+00:00 | ace-win-1 | oauth-api | ok | 2026-11-21T04:13:56+00:00 |
| codex-owner | codex | owner |  | 81% | 19% | 2026-11-25T16:31:50+00:00 | ace-win-2 | app-server-live | ok | 2026-11-21T04:14:01+00:00 |
| codex-professional | codex | colleague |  | 37% | 63% | 2026-11-24T13:11:16+00:00 | ace-win-1 | app-server-live | ok | 2026-11-21T04:13:56+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
