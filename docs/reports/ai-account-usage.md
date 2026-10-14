# AI account usage (fleet)

Generated 2026-10-14T08:13:33+00:00 by fleet-collector collect_account_usage_fleet. Percentages are USED; headroom = 100 - weekly used. Source of truth: `config/ai-tools/account-usage-latest.json`.

## Recommendation

- **claude**: `claude-professional` (70.0% weekly headroom) on ace-win-1
- **codex**: `codex-professional` (51.0% weekly headroom) on ace-win-1 -- within 15 pts of codex-owner: stay on whichever host you are on

## Accounts

| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |
|---|---|---|---|---|---|---|---|---|
| claude-owner | claude | owner | 28% | 80% | 20% | 2026-10-17T14:00:00.502874+00:00 | ace-win-2 | oauth-api |
| claude-professional | claude | colleague | 6% | 30% | 70% | 2026-10-17T08:00:00.240157+00:00 | ace-win-1 | oauth-api |
| codex-owner | codex | owner |  | 55% | 45% | 2026-10-20T04:58:10+00:00 | ace-win-2 | app-server-live |
| codex-professional | codex | colleague |  | 49% | 51% | 2026-10-20T04:58:10+00:00 | ace-win-1 | app-server-live |

## Hosts

| host | reachable | claude | codex | note |
|---|---|---|---|---|
| ace-linux-1 | yes | claude-owner | codex-owner |  |
| ace-linux-2 | yes | claude-owner | codex-owner |  |
| gpu-claw | yes | claude-owner | codex-owner | claude: URLError: <urlopen error [Errno -3] Temporary failure in name resolution> |
| ace-win-2 | yes | claude-owner | codex-owner |  |
| ace-win-1 | yes | claude-professional | codex-professional |  |
| fleet-collector | yes |  | codex-owner | claude: credentials file has no accessToken |
