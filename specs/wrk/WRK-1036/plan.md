# WRK-1036 Plan — Agent teams lifecycle: audit, session-start, session-exit tidy

## Mission
Audit stale agent teams, expose actionable team state during session start, and add
deterministic session-exit cleanup so archived-team directories and orphaned task
directories do not accumulate.

## Scope

### In scope
- Phase 1: audit + cleanup of 3 stale named teams and 76 orphaned UUID task dirs
- Phase 2: session-start SKILL.md Step 3b + `spawn-team.sh` helper (prints recipe only)
- Phase 3: `tidy-agent-teams.sh` Stop hook (bash+coreutils, no jq) + wiring into settings.json

### Out of scope
- WRK-1008 P1 findings (captured as WRK-1037)
- Changes to MAX_TEAMMATES or CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS settings
- Changes to team member agent logic or task dispatch
- Concurrent-agent race condition handling (defer — rare; log WRK if encountered)
- JSON signal output (plain text sufficient; JSON is over-engineering for now)

## Acceptance Criteria

### Phase 1 — Audit & Cleanup
- [ ] Per-team audit summary written: source path, last signal, attempted work,
      completion state, delete/retain rationale
- [ ] WRK-1008 P1 Codex findings captured as WRK-1037 before team deleted ✓ (done)
- [ ] c915cd54 UUID dir WAR-extractor work inspected; keep/capture/discard decision recorded
- [ ] All 3 stale named teams removed from `~/.claude/teams/` only after audit records exist
- [ ] All purge-eligible UUID task dirs removed from `~/.claude/tasks/` only after c915cd54 resolved
- [ ] Non-target dirs that don't match naming rules are skipped and reported, not deleted
- [ ] Cleanup is idempotent: rerunning Phase 1 yields zero additional deletions

### Phase 2 — Session-start availability
- [ ] `session-start/SKILL.md` has new Step 3b: agent-teams status (≤10 lines output)
- [ ] `scripts/work-queue/spawn-team.sh` created, executable, validated
- [ ] Naming convention `wrk-NNN-<slug>` documented and enforced via strict regex
- [ ] Script rejects: malformed WRK IDs, empty slugs, uppercase slugs, unsafe chars,
      duplicate teams — all with non-zero exit
- [ ] Script emits deterministic instructions only; does not create teams itself

### Phase 3 — Session-exit tidy
- [ ] `scripts/hooks/tidy-agent-teams.sh` created, executable, completes in <5s
- [ ] No jq dependency — bash + coreutils only
- [ ] Repo root resolved from `$SCRIPT_DIR`, not `$PWD` (cwd-independent)
- [ ] Script wired into Stop hooks in `.claude/settings.json`
- [ ] `--dry-run` reports same candidates as live run without deleting
- [ ] Smoke test: dummy archived WRK team deleted; active WRK team preserved
- [ ] Empty stale UUID dirs (>7 days) purged; non-empty or recent dirs preserved
- [ ] Missing `~/.claude/teams/`, `~/.claude/tasks/`, or archive dirs → zero-state exit 0
- [ ] Signal line: `agent_teams_tidied: deleted=N tasks_purged=M skipped=K`

## Pseudocode

### spawn-team.sh
```text
spawn_team(wrk_id, slug) -> exit_code
  require exactly 2 args → exit 1 with usage if not
  validate wrk_id matches ^WRK-[0-9]+$           → exit 1 "Invalid WRK ID"
  validate slug matches ^[a-z0-9-]+$ and not empty → exit 1 "Invalid slug"
  team_name = "wrk-" + numeric_part(wrk_id) + "-" + slug
  if ~/.claude/teams/team_name exists → exit 1 "Team already exists: <team_name>"
  print "Team name: <team_name>"
  print "Description: WRK-<NNN> <slug>"
  print "Spawn: TeamCreate team_name=<team_name>"
  print "Suggested teammates: <team_name>-lead, <team_name>-impl, <team_name>-review"
  exit 0
```

### tidy-agent-teams.sh
```text
tidy_agent_teams(dry_run=false) -> exit_code
  SCRIPT_DIR = dirname(realpath($0))
  REPO_ROOT  = SCRIPT_DIR/../../..      # scripts/hooks/ → repo root
  teams_dir  = $HOME/.claude/teams
  tasks_dir  = $HOME/.claude/tasks
  archive_dir = $REPO_ROOT/.claude/work-queue/archive
  deleted_teams=0; purged_tasks=0; skipped=0

  # Build archived WRK ID set once — one glob, not one find per team
  archived_ids = set of "WRK-NNN" from basenames of $archive_dir/WRK-*.md

  if teams_dir exists:
    for each team_dir in direct_children(teams_dir) matching wrk-*:
      team_name = basename(team_dir)
      if team_name matches ^wrk-([0-9]+)-[a-z0-9-]+$:
        wrk_id = "WRK-" + captured_digits
        if wrk_id in archived_ids:
          report "[tidy] team <team_name> → archived WRK, candidate for deletion"
          if not dry_run: rm -rf team_dir
          deleted_teams++
        # else: active WRK — skip silently
      else:
        skipped++; report "[tidy] skip <team_name> — does not match naming convention"

  UUID_RE = ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$
  if tasks_dir exists:
    for each task_dir in direct_children(tasks_dir):
      if basename(task_dir) not matches UUID_RE:  skipped++; continue
      if not is_directory(task_dir):               skipped++; continue
      if not is_empty(task_dir):                   skipped++; continue
      if mtime(task_dir) >= now_minus_7_days:      skipped++; continue
      report "[tidy] task <task_dir> → empty+stale, candidate for purge"
      if not dry_run: rm -rf task_dir
      purged_tasks++

  print "agent_teams_tidied: deleted=$deleted_teams tasks_purged=$purged_tasks skipped=$skipped"
  exit 0
```

## Tests / Verification (TDD)

`tidy-agent-teams.sh` is production code — verified by controlled fixture-based shell
smoke tests, not just live filesystem checks.

### TDD cycle per phase

**Before Phase 1** — write `--dry-run` stub (exits 0, prints zero-state):
- Red: stale-team fixture present → dry-run reports candidate (stub doesn't detect it yet)
- Red: active-team fixture present → dry-run must NOT report it
- Red: non-empty UUID task dir → must NOT be reported

**After Phase 1 cleanup**:
- `tidy-agent-teams.sh --dry-run` against real state → `deleted=0 tasks_purged=0 skipped=0` ✓
- Rerun Phase 1 cleanup → zero additional deletions (idempotent) ✓

**After Phase 2 spawn script**:
- `spawn-team.sh WRK-1036 test` → prints `wrk-1036-test` recipe, exit 0 ✓
- `spawn-team.sh INVALID slug` → exit 1 ✓
- `spawn-team.sh WRK-1036 ""` → exit 1 (empty slug) ✓
- `spawn-team.sh WRK-1036 Test` → exit 1 (uppercase slug) ✓
- `spawn-team.sh WRK-1036 bad slug` → exit 1 (space/unsafe chars) ✓
- duplicate `wrk-1036-test` dir exists → exit 1 "already exists" ✓
- `tidy-agent-teams.sh --dry-run` with `wrk-1036-test` (WRK-1036 in pending/) → skips it ✓

**After Phase 3 implementation** — fixture-based smoke tests:
- Create `archive/WRK-9999.md` + `~/.claude/teams/wrk-9999-dummy/`:
  `--dry-run` → reports candidate, no deletion ✓
  live run → deletes `wrk-9999-dummy`, prints `deleted=1` ✓
- Pending WRK team (`wrk-1036-test`, WRK-1036 in pending/) → skipped ✓
- Empty UUID dir >7 days old → purged ✓
- Empty UUID dir <7 days old → preserved ✓
- Non-empty UUID dir >7 days old → skipped (`skipped` count increments) ✓
- Missing `~/.claude/teams/` → exit 0, `deleted=0 tasks_purged=0 skipped=0` ✓
- Hook from arbitrary cwd (not repo root) → runs correctly ✓
- `time bash scripts/hooks/tidy-agent-teams.sh --dry-run` → <5s ✓

### Stage-gate verification matrix

| Stage | Tidy check | Spawn check | Expected |
|-------|-----------|-------------|----------|
| After Stage 10 Phase 1 | `--dry-run` real state | — | `deleted=0 tasks_purged=0` |
| After Stage 10 Phase 2 | `--dry-run` skips active WRK | happy/invalid/dup/slug suite | All pass |
| After Stage 10 Phase 3 | fixture dry-run + live run | — | Archived deleted, active skipped |
| Stage 12 (TDD/Eval) | Full fixture suite + timing | Full arg-validation suite | All pass, <5s |

## Implementation Sequence

1. **Phase 1** (audit first, destructive cleanup second):
   - Write per-team audit summaries from inbox messages
   - Inspect c915cd54 content; record keep/capture/discard decision
   - Delete audited stale teams; purge confirmed orphan UUID dirs
   - Rerun `--dry-run` to confirm idempotent zero-state

2. **Phase 2** (session-start + spawn helper):
   - Edit `session-start/SKILL.md` — insert Step 3b (≤10 lines)
   - Write `scripts/work-queue/spawn-team.sh` (~25 lines, `set -euo pipefail`)
   - `chmod +x`; smoke-test valid/invalid/duplicate/slug paths

3. **Phase 3** (Stop hook):
   - Write `scripts/hooks/tidy-agent-teams.sh` (bash+coreutils, no jq, <50 lines)
   - Resolve repo root from `$SCRIPT_DIR`
   - Wire into `.claude/settings.json` Stop hooks
   - Run fixture-based smoke tests; verify timing <5s

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Tidy deletes active team | Archive set built from filenames once; only WRK-*.md in archive/ matches; pending/working WRKs are safe |
| Hook cwd sensitivity | Resolve repo root from `$SCRIPT_DIR` (dirname of script), not `$PWD` |
| jq unavailable | No jq used — bash + coreutils only |
| UUID regex too loose | Anchored full UUID pattern: `^[0-9a-f]{8}-...-[0-9a-f]{12}$` |
| Non-empty orphan dirs purged | Explicit `is_empty` check; non-empty dirs always skipped |
| c915cd54 WAR extractor lost | Inspect task JSON fully; capture WRK if needed before purge |
| session-start output noisy | Step 3b capped at ≤10 lines; only actionable states surfaced |
| Stop hook >5s on many dirs | Non-recursive `direct_children` scan; archive set built once, not per-team |

## Cross-Review Synthesis Notes (Stage 6)
- Codex and Gemini agreed on all 8 points; no conflicts between reviewers
- Claude draft adopted Codex/Gemini improvements: skipped counter, no jq, strict UUID
  regex, missing-dir guards, single-pass archive set, strict slug validation, removed
  MAX_TEAMMATES from spawn output, cwd-independent hook via SCRIPT_DIR
- Deferred: concurrent-agent race condition (rare), JSON signal format (over-engineering)
