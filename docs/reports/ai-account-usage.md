# AI account usage (fleet)

Generated 2026-10-04T08:13:36+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (99.0% weekly headroom) on ace-linux-1, ace-linux-2
- **codex**: `codex-owner` (94.0% weekly headroom) on ace-linux-1, ace-linux-2, fleet-collector

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 0% | 1% | 99% | 2026-10-10T14:00:00.280242+00:00 | ace-linux-2 | oauth-api |
| claude-professional | claude | colleague |  |  |  |  |  | unavailable |
| codex-owner | codex | owner |  | 6% | 94% | 2026-10-09T22:10:35+00:00 | fleet-collector | app-server-live |
| codex-professional | codex | colleague |  |  |  |  |  | unavailable |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | no | claude-owner | codex-owner | exit 255 |
| ace-win-2 | no | claude-professional | codex-professional | exit 255 |
| ace-win-1 | no | claude-professional | codex-professional | exit 255 |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |

## Warnings

- ace-linux-1: codex sample's weekly window reset at 2026-10-03T17:19:42+00:00; ignored
- ace-linux-2: codex sample's weekly window reset at 2026-08-21T11:50:27+00:00; ignored
