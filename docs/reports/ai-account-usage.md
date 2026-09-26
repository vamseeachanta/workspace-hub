# AI account usage (fleet)

Generated 2026-09-26T18:13:46+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-owner` (100.0% weekly headroom) on ace-linux-1, ace-linux-2, gpu-claw
- **codex**: `codex-owner` (99.0% weekly headroom) on ace-linux-1, ace-linux-2 -- within 15 pts of codex-professional: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 2% | 0% | 100% | 2026-10-03T14:00:00.174589+00:00 | ace-linux-1 | oauth-api |
| claude-professional | claude | colleague | 52% | 25% | 75% | 2026-10-03T07:59:59.960208+00:00 | ace-win-2 | oauth-api |
| codex-owner | codex | owner |  | 1% | 99% | 2026-08-21T11:50:27+00:00 | ace-linux-2 | local-session-rate-limits |
| codex-professional | codex | colleague |  | 2% | 98% | 2026-10-03T17:17:20+00:00 | ace-win-2 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner | claude: credentials file has no accessToken |
| gpu-claw | yes | claude-owner |  | claude: access token expired; a Claude Code session on this host will refresh it |
| ace-win-2 | yes | claude-professional | codex-professional |  |
| ace-win-1 | no | claude-professional | codex-professional | exit 255 |
| fleet-collector | yes |  |  | claude: credentials file has no accessToken |

## Warnings

- gpu-claw: codex is logged in but ai-accounts.yaml maps no account
- fleet-collector: codex is logged in but ai-accounts.yaml maps no account
