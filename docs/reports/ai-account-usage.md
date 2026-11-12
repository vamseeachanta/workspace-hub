# AI account usage (fleet)

Generated 2026-11-12T05:13:58+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (78.0% weekly headroom) on ace-win-1 -- within 15 pts of claude-owner: stay on whichever host you are on
- **codex**: `codex-professional` (93.0% weekly headroom) on ace-win-1 -- within 15 pts of codex-owner: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source | status | probed at |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner |  | 35% | 65% | 2026-11-14T14:00:00.860660+00:00 | ace-win-2 | oauth-api | ok | 2026-11-12T05:13:46+00:00 |
| claude-professional | claude | colleague |  | 22% | 78% | 2026-11-14T07:59:59.603052+00:00 | ace-win-1 | oauth-api | ok | 2026-11-12T05:13:50+00:00 |
| codex-owner | codex | owner |  | 8% | 92% | 2026-11-18T06:36:36+00:00 | ace-win-2 | app-server-live | ok | 2026-11-12T05:13:55+00:00 |
| codex-professional | codex | colleague |  | 7% | 93% | 2026-11-17T04:51:09+00:00 | ace-win-1 | app-server-live | ok | 2026-11-12T05:13:50+00:00 |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
