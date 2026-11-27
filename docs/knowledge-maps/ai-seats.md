# AI seats

Map id `ai-seats`, schema `knowledge-map/1`, verified 2026-11-27T15:45Z.
Data file: [`ai-seats.yaml`](ai-seats.yaml). Standard:
[`.claude/rules/model-routing.md`](../../.claude/rules/model-routing.md).

This page is the generic layer. Measured usage, reset times, plan tiers, banked
resets, the seat-to-host map and deviations are held in the private detail map:
`fleet-ops docs/knowledge-maps/ai-seats.yaml` (private repository).

## Seats

Seats are named by config id only. Identity is a 12-hex fingerprint printed by
the probe; no address, token, key, auth-file content or billing detail is
recorded.

| Seat | Provider | Holder | Lane | Stop line |
|---|---|---|---|---|
| `claude-owner` | Claude | owner | Owner desk: routing, owner review pages, decisions, outward text | `tight: true` (headroom below 10 %); failover to the Professional desk at 98 % |
| `claude-professional` | Claude | colleague | Senior PM desk, road-map pass, Intake failover, review of Codex output | `week_pct` 98 |
| `codex-owner` | Codex | owner | General implementation on owner-seat hosts, lane jobs | `tight: true` |
| `codex-professional` | Codex | colleague | Heavy implementation from the road-map pass | `week_pct` 98, whatever `tight` says |
| Agy/Gemini pool | Agy | owner | Third-provider review, plain-English edit passes | Gemini weekly at 5 % left, or five-hour at 10 % left; any 429 |

The 98 % lines are the owner's ruling of 26 Nov 2026 ("we use claude and codex
professional also to 98%"). The earlier 90 % and 95 % lines left paid capacity
unused and are retired.

## Lane routing

| Lane | Use for |
|---|---|
| Codex | Routine implementation and fix rounds; first reviews of Claude work |
| Claude (Opus, Fable) | Review of Codex work, client and outward text, decisions, high-impact analysis; Fable for client engineering reviews and heavy-comment rounds |
| Agy (Gemini) | Plain-English edit pass and review only |

Model ids come from the live CLI config, never from this map. Before an
implementation marathon or a `dispatch:ready` hand-off, read
`recommendation.<provider>` in `config/ai-tools/account-usage-latest.json` and
dispatch to a host it names. A seat is switched only when the other seat holds
at least 15 points more weekly headroom. Implementation subagents commit and
push at every green milestone, because a quota wall clobbers uncommitted
worktrees.

## How to use each seat in full

**claude-owner.** Reserved for what only the owner seat may do: owner-held
decisions, owner review pages, personal and private-data repositories. In the
last day before its weekly reset, any headroom left goes to high-impact reviews
and heavy-comment rounds.

**claude-professional.** Runs to 98 % before every weekly reset, with parallel
subagents (owner, 27 Nov 2026). Suitable work: second-provider review of Codex
results, knowledge maps, wiki register passes, report reviews. Personal and
private-data repositories stay on the owner seat. Each pass compares headroom
with hours to reset and adds parallel work when the remaining hours will not
use the headroom.

**codex-owner.** The default Codex seat for routine implementation, fix rounds
and first reviews of Claude work, on the hosts that `recommendation.codex`
names. Long marathons go to whichever Codex seat holds the larger headroom.

**codex-professional.** Keeps 6 to 8 jobs in flight and starts up to 4 per
pass. Each job is confined by its brief to its own worktree and runs with full
access, because the Windows sandbox fails on its host (owner, 27 Nov 2026). The
job writes a RESULT file and never commits; the desk reviews, reruns the tests
and commits. Codex jobs are API-bound, but the host keeps 16 cores and 64 GB
free for licensed solver lanes. Banked full resets are spent before they
expire: the seat reaches 98 %, then the desk asks the owner to apply the reset
that expires first. Applying a reset is the owner's step.

**Agy/Gemini pool.** Used across the Agy-lane hosts until the tokens run out
(owner, 26 Nov 2026). Work in order: advisory third-provider reviews of open PRs
at their current heads, relayed by Claude after each finding is checked;
plain-English edit passes on articles and reports awaiting owner approval;
register passes on wiki pages. Runs headless with `--mode plan`, takes files and
never commands, never edits a repository and never posts. Limits: 3 jobs per
host, 4 new per pass, one at a time on public-repository-only hosts. Each job
logs its tokens and the pool reading after it.

## How usage is measured

| Provider | Collector | Output | Cadence |
|---|---|---|---|
| Claude, Codex | `scripts/fleet/account-usage-cron.sh` on the fleet collector, fanning out `scripts/ai/assessment/collect-account-usage.py` over ssh stdin | `config/ai-tools/account-usage-latest.json`, `docs/reports/ai-account-usage.md` on `main` | hourly |
| Agy pool | `dashboard/refresh_agy_status.py` in the private road-map pass | `dashboard/google-usage.json`, `dashboard/agy-account-usage.json` (private) | hourly |

The Claude probe reads the OAuth usage endpoint (five-hour and seven-day
buckets); the Codex probe reads `codex app-server` live rate limits and falls
back to the newest session log. Percentages are **used**; headroom is 100 minus
weekly used. A usage file whose `captured_at` is more than 3 h old counts as not
measured and is reported so. The aggregate ignores per-host samples older than
12 h.

## Refresh commands

```bash
git -C <workspace-hub> fetch -q origin main
git -C <workspace-hub> show origin/main:config/ai-tools/account-usage-latest.json
uv run python scripts/ai/assessment/collect-account-usage.py --json --host <label>
ssh -o BatchMode=yes -o ConnectTimeout=10 <label> \
  'python3 - --json --host <label>' < scripts/ai/assessment/collect-account-usage.py
ssh -o BatchMode=yes <agy-host> 'cd "$(mktemp -d)" && ~/.local/bin/agy --print /usage --print-timeout 45s'
claude --version; codex --version; codex login status; agy --version
```

`codex login status` prints only the login method. Auth and credential files
are never opened by hand; the probe reads them and prints a fingerprint.

## Open questions

- The Agy pool has no seat id in `config/ai-tools/ai-accounts.yaml`; its record
  lives only in the private dashboard.
- The Agy Claude-and-GPT bucket has no stated lane or stop line beyond the
  shared 5 % weekly rule.
