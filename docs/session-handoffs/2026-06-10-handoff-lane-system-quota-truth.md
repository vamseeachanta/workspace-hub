# Session handoff — 2026-06-10: compute-lane system + quota truth chain

> Host: ace-linux-2 | Repo: workspace-hub (+ label writes across 26 repos)
> Session scope: user request "delegate heavy work to codex until codex weekly
> available <10%" grown into a full plan-time lane system, then the quota-truth
> defects that work exposed.

## Shipped and CLOSED

| Issue | What | Key commits / evidence |
|---|---|---|
| [#3028](https://github.com/vamseeachanta/workspace-hub/issues/3028) (record) | `lane:codex`/`lane:claude` labels on every open issue in 26 repos (1,790 verified: 556 codex / 1,234 claude, exactly-one invariant); compute-lane rule git-tracked in `agents-template.md` + `agents.md` | `5ce951be2`; rate-limit gotcha: ~4 GraphQL pts per `gh issue edit` |
| [#3029](https://github.com/vamseeachanta/workspace-hub/issues/3029) | route.py lane-aware provider resolution (`ai:` > rule > `lane:` > default, lane never sticky), `Lane:` plan-template field, planning-skill steps | `367baf4b6`, `fc4d866a7`; dispatch tests 36/36 |
| [#3030](https://github.com/vamseeachanta/workspace-hub/issues/3030) | dispatch quota gate: lane:codex demotes below 10% weekly remaining, current-window snapshot guard, fail-open, loud `--codex-remaining` CLI (no env path) | `6f1e4ab86`, `360b46231`; 51/51 tests; dry-run 501 vs 0 demotions |

All three closed with evidence comments; T2 adversarial review (Claude + Codex)
at both plan and code stages throughout. Codex r2 caught real defects every
round (routing-rule inversion, sticky-label materialization, cross-reset stale
quota, env backdoor, out-of-range numerics, copied-fixture test, legacy cron
file, per-file freshness granularity) — the cross-review gate earned its cost.

## IN FLIGHT at handoff — #3034 (approved, implemented, NOT yet closed)

[#3034](https://github.com/vamseeachanta/workspace-hub/issues/3034) — statusline
quota staleness (root cause: the canonical 4h refresh task targets
dev-primary/ace-linux-1 only; on ace-linux-2 the git-tracked cache was a 3-day-old
propagated snapshot reading codex 79% vs live 29%).

**Implemented this session (commit in flight or just landed — verify
`git log origin/main` for `feat(statusline): quota-file freshness sourcing`):**
- `.claude/statusline-command.sh`: per-value freshest-file sourcing (fresh
  primary > fresh cache > stale primary > stale cache, for percentages AND
  reset countdowns), `?` marker on stale/undatable components, threshold env
  bounds-validated to (0,168]h (default 6).
- `tests/statusline/test_quota_staleness.bats` (8 tests) + existing fixtures
  stamped fresh; suite 22/22 green (bats installed via npm: `~/.npm-global/bin/bats`).
- `scripts/ai/assessment/query-quota.sh --cache-only` (HOME cache only, repo
  file untouched).
- `config/scheduled-tasks/schedule-tasks.yaml`: `quota-snapshot-refresh`
  (`10 */4 * * *`, dev-secondary/ace-linux-2); validates 48 tasks; **cron
  applied live on ace-linux-2** (setup-cron.sh installed 4 entries — the new
  one plus 3 other pending roster entries this box had drifted on).
- Live verification: before `O:79%?·0.3d?` → after slim refresh `O:25%·0.3d`
  (matches live), tracked file clean.

**Remaining for #3034 (next session):**
1. Verify the implementation commit landed on origin/main (push may have needed
   a rebase retry behind the kanban cron — same pattern as every push today).
2. Code-stage adversarial review (T2): r1 inline + codex r2 via
   `env -u CLAUDECODE bash scripts/review/submit-to-codex.sh --commit <sha> ...`
   (#2684 workaround), artifacts to `scripts/review/results/2026-06-10-code-3034-*.md`.
3. Resolve findings, close #3034 with evidence comment, flip plans README row
   to done.

## Repo / state notes

- **workspace-hub pulls are pathologically slow on this box today** (10-15 min
  `git merge --ff-only --autostash` phases, mostly I/O wait) and the kanban
  cron pushes frequently → every push needed one rejected-then-rebase retry.
  Changes are safe in `MERGE_AUTOSTASH` during the window; do NOT interrupt.
- Dirty exceptions (expected): `.claude/state/session-signals/*.jsonl`
  (harness-owned); `/tmp/lane-assign/` scratch (lane plan JSONs + apply logs,
  ephemeral, documented in #3028).
- External actions this session: GitHub label writes (26 repos), issues
  #3028/#3029/#3030/#3034 created/commented/closed, crontab modified on
  ace-linux-2 (via setup-cron.sh, roster-declared), npm global install of bats.
- Codex weekly quota: ~25% remaining at handoff (burned ~50% today on the
  classification sweep + reviews); resets ~03:30 -05:00. Above the 10% gate —
  codex delegation stays ON.
- Memory updated: `delegate-heavy-compute-to-codex.md` carries the full chain
  (rule → labels → routing → quota gate → statusline truth).
