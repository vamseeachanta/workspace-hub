OpenAI Codex v0.111.0 (research preview)
--------
workdir: /mnt/local-analysis/workspace-hub
model: gpt-5.4
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR, /home/vamsee/.codex/memories]
reasoning effort: medium
reasoning summaries: none
session id: 019ccd1f-5997-7021-b8b2-1275acfc616f
--------
user
# Stance: Codex Plan Draft Review

You are a software engineer agent. Your focus is on **implementation correctness, edge cases, and testability**.

You will receive a Claude-authored plan draft. Walk it section-by-section and produce your own refined version.

When reviewing:
1. Challenge any assumptions about implementation approach — is there a simpler or more robust way?
2. Identify edge cases not covered (malformed input, missing fields, timezone/date math, quota exhaustion).
3. Flag AC gaps — things implementable but not covered by the listed tests.
4. Assess integration risks (nightly cron, file writes, CLI availability).
5. Verify uv run --no-project python is used wherever Python is called.

Your output must be a complete refined plan (same structure as the input draft).
Add a "Codex Notes" section at the end with your specific findings.

---
CLAUDE DRAFT PLAN:
# WRK-1036 Plan — Agent teams lifecycle: audit, session-start, session-exit tidy

## Mission
Audit stale agent teams, make teams readily available at session-start, and add
session-exit tidy-up so ghost teams and orphaned task dirs never accumulate again.

## Scope

### In scope
- Phase 1: audit + cleanup of 3 stale named teams and 76 orphaned UUID task dirs
- Phase 2: session-start SKILL.md step + `spawn-team.sh` helper script
- Phase 3: `tidy-agent-teams.sh` Stop hook + wiring into settings.json

### Out of scope
- WRK-1008 P1 findings (separate WRK to be captured in Phase 1)
- Changes to MAX_TEAMMATES or CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS settings
- Any changes to team member agent logic or task dispatch

## Acceptance Criteria

### Phase 1 — Audit & Cleanup
- [ ] Per-team audit summary written (what attempted / completed / abandoned)
- [ ] WRK-1008 P1 Codex findings captured as new WRK item before team deleted
- [ ] c915cd54 UUID dir WAR-extractor work investigated; decision recorded
- [ ] All 3 named teams deleted from `~/.claude/teams/`
- [ ] All 76 UUID task dirs purged from `~/.claude/tasks/` (after c915cd54 resolved)

### Phase 2 — Session-start availability
- [ ] `session-start/SKILL.md` has new Step 3b: agent-teams status (≤10 lines)
- [ ] `scripts/work-queue/spawn-team.sh` created, executable, tested
- [ ] Naming convention `wrk-NNN-<slug>` documented and enforced in spawn script

### Phase 3 — Session-exit tidy
- [ ] `scripts/hooks/tidy-agent-teams.sh` created (<50 lines, <5s runtime)
- [ ] Script wired into Stop hooks in `.claude/settings.json`
- [ ] `--dry-run` flag shows correct candidates without deleting
- [ ] Smoke test: dummy team + archived WRK → tidy detects and removes
- [ ] Signal `agent_teams_tidied: N deleted, M tasks purged` printed to stdout

## Pseudocode

### spawn-team.sh
```
spawn-team(wrk_id, slug):
  team_name = "wrk-" + wrk_id.lower() + "-" + slug
  validate wrk_id matches WRK-\d+ pattern  → exit 1 if invalid
  check ~/.claude/teams/team_name exists   → exit 1 if already exists
  print TeamCreate instructions (name, description)
  print: "Spawn in Claude: TeamCreate team_name=<team_name>"
  print: "MAX_TEAMMATES=10 — name teammates: <team_name>-lead, <team_name>-impl, etc."
```

### tidy-agent-teams.sh
```
tidy-agent-teams(dry_run=false):
  # Fires at every stage-gate Stop hook (stages 1-20 are linear/monotonic).
  # Stage 20 (Archive) is not special — same logic applies uniformly.
  # After Stage 20 completes the Stop hook fires and WRK is in archive/ → team deleted.
  archive_dir = workspace_hub/.claude/work-queue/archive/
  deleted_teams = 0; purged_tasks = 0

  for each dir in ~/.claude/teams/:
    team_name = basename(dir)
    wrk_id = extract WRK-NNN from team_name via regex  (skip if no match)
    if wrk_id found in archive_dir (find archive/ -name "WRK-NNN.md"):
      if not dry_run: rm -rf dir
      deleted_teams++

  cutoff = date 7 days ago (epoch seconds)
  for each dir in ~/.claude/tasks/:
    if dir is UUID (matches [0-9a-f-]{36}):
      if dir is empty AND mtime < cutoff:
        if not dry_run: rm -rf dir
        purged_tasks++

  print "agent_teams_tidied: deleted=$deleted_teams tasks_purged=$purged_tasks"
```

## Tests / Verification (TDD)

`tidy-agent-teams.sh` is the living test harness for WRK-1036 — written first (Red),
then each phase makes it go Green. Run at every stage gate.

### TDD cycle per phase

**Before Phase 1** — write `tidy-agent-teams.sh --dry-run` stub (exits 0, prints nothing):
- Red: run against current state → prints 0 candidates (script not yet implemented)

**After Phase 1 cleanup** — teams + UUID dirs deleted:
- `tidy-agent-teams.sh --dry-run` → 0 teams, 0 tasks to purge ✓

**After Phase 2 spawn script** — create a test team `wrk-1036-test` for a pending WRK:
- `tidy-agent-teams.sh --dry-run` → 0 deletions (WRK-1036 is not archived) ✓
- `spawn-team.sh WRK-1036 test` → prints correct team name + TeamCreate recipe ✓
- `spawn-team.sh INVALID slug` → exit 1 with error ✓
- `spawn-team.sh WRK-1036 test` (duplicate) → exit 1 "already exists" ✓

**After Phase 3 implementation** — full tidy logic in place:
- Create dummy archived WRK dir under `archive/` + dummy team dir `wrk-9999-dummy`:
  `tidy-agent-teams.sh --dry-run` → lists `wrk-9999-dummy` as candidate, no deletions ✓
  `tidy-agent-teams.sh` (live) → deletes `wrk-9999-dummy`, prints `deleted=1 tasks_purged=N` ✓
- `tidy-agent-teams.sh` with active WRK team (`wrk-1036-test`, WRK-1036 in pending/) → skips it ✓
- Stop hook timing: `time bash scripts/hooks/tidy-agent-teams.sh` → <5s ✓

### Stage-gate verification matrix

| Stage | Tidy check | spawn check | Expected |
|-------|-----------|-------------|----------|
| After Stage 10 Phase 1 | `--dry-run` → 0 candidates | — | Cleanup confirmed |
| After Stage 10 Phase 2 | `--dry-run` → skips wrk-1036-test | happy/error/dup paths | All pass |
| After Stage 10 Phase 3 | live run on dummy | — | Deletes dummy, skips active |
| Stage 12 (TDD/Eval) | Full suite + timing | Full suite | All pass, <5s |

## Implementation Sequence

1. **Phase 1** (audit — read only, no writes until decisions confirmed):
   - Write per-team summary from inbox messages already read
   - Capture WRK for WRK-1008 P1 Codex findings
   - Investigate c915cd54 content; decide capture-or-discard
   - Delete all 3 named teams; purge UUID task dirs

2. **Phase 2** (session-start + spawn script):
   - Edit `session-start/SKILL.md` — insert Step 3b after Step 3
   - Write `scripts/work-queue/spawn-team.sh` (bash, ~25 lines)
   - `chmod +x` the script; smoke-test locally

3. **Phase 3** (Stop hook):
   - Write `scripts/hooks/tidy-agent-teams.sh` (bash+jq, <50 lines)
   - Add entry to `.claude/settings.json` Stop hooks array
   - Run `--dry-run` to confirm detection logic
   - Create dummy team, confirm live run deletes it

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| tidy deletes an active team | Only deletes when WRK found in `archive/` — pending/working WRKs are safe |
| c915cd54 WAR extractor work is unrecoverable | Read task JSON fully before purging; capture WRK if needed |
| Stop hook exceeds 5s on large task dirs | Use `find -maxdepth 1` + stat; avoid recursive scan |
| session-start SKILL.md exceeds word limit | New section is ≤10 lines; verify word count after edit |
mcp startup: no servers
codex
Reviewing the WRK-1036 draft as a plan-only pass. I’m loading the workflow gate instructions first so the refinement stays aligned with the repo’s WRK contract before I rewrite the plan.
exec
/bin/bash -lc "sed -n '1,220p' /mnt/local-analysis/workspace-hub/.claude/skills/workspace-hub/work-queue-workflow/SKILL.md" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,260p' /mnt/local-analysis/workspace-hub/.claude/skills/workspace-hub/workflow-gatepass/SKILL.md" in /mnt/local-analysis/workspace-hub succeeded in 50ms:
---
name: work-queue-workflow
description: >
  Explicit entrypoint skill for the WRK work-queue lifecycle workflow. Points to
  the canonical work-queue process and gatepass enforcement sequence.
version: 1.5.0
updated: 2026-03-07
category: workspace-hub
triggers:
  - work-queue workflow
  - wrk workflow
  - /work workflow
  - lifecycle workflow
related_skills:
  - coordination/workspace/work-queue
  - workspace-hub/workflow-gatepass
  - workspace-hub/workflow-html
  - workspace-hub/session-start
  - workspace-hub/session-end
capabilities:
 succeeded in 50ms:
---
name: workflow-gatepass
description: >
  Enforce WRK lifecycle gatepass from session start through close/archive with
  machine-checkable evidence requirements and explicit no-bypass rules.
version: 1.0.6
updated: 2026-03-07
category: workspace-hub
triggers:
  - workflow gatepass
  - wrk gate enforcement
  - lifecycle gate
  - close gate evidence
related_skills:
  - workspace-hub/session-start
  - coordination/workspace/work-queue
  - workspace-hub/session-end
  - workspace-hub/wrk-lifecycle-testpack
capabilities:
  - lifecycle-gate-enforcement
codex
# WRK-1036 Plan — Agent teams lifecycle: audit, session-start, session-exit tidy

## Mission
Audit stale agent teams, expose actionable team state during session start, and add deterministic session-exit cleanup so archived-team directories and orphaned task directories do not accumulate.

## Scope

### In scope
- Phase 1: audit and clean up the currently identified stale named teams and orphaned UUID task dirs under the Claude state directories
- Phase 2: add a session-start status step and a `spawn-team.sh` helper for WRK-scoped team creation
- Phase 3: add a `tidy-agent-teams.sh` Stop hook and wire it into `.claude/settings.json`

### Out of scope
- WRK-1008 P1 findings beyond capturing them into a separate WRK item
- Changes to `MAX_TEAMMATES` or `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`
- Changes to team member agent logic, routing, or task dispatch behavior
- Any cleanup outside the Claude agent-team/task state directories required by this WRK

## Acceptance Criteria

### Phase 1 — Audit & Cleanup
- [ ] A per-team audit summary is written with: source path, last meaningful signal, attempted work, completion state, and delete/retain rationale
- [ ] WRK-1008 P1 Codex findings are captured as a new WRK item before any related team state is deleted
- [ ] `c915cd54` task-dir contents are inspected; the keep/capture/discard decision is recorded with evidence
- [ ] All targeted stale named teams are removed from `~/.claude/teams/` only after their audit records exist
- [ ] All purge-eligible orphaned UUID task dirs are removed from `~/.claude/tasks/` only after the `c915cd54` decision is resolved
- [ ] Non-target directories that do not match expected naming rules are skipped and reported, not deleted
- [ ] Cleanup commands are idempotent: rerunning Phase 1 after success yields zero additional deletions

### Phase 2 — Session-start availability
- [ ] `session-start/SKILL.md` includes a new Step 3b for agent-team status, capped at 10 lines of user-facing output
- [ ] `scripts/work-queue/spawn-team.sh` is created, executable, and validated
- [ ] Naming convention `wrk-<NNN>-<slug>` is documented and enforced by the script
- [ ] Script rejects malformed WRK ids, empty slugs, uppercase slug content, unsafe characters, and duplicate teams with non-zero exit
- [ ] Script does not create teams itself; it emits deterministic instructions only

### Phase 3 — Session-exit tidy
- [ ] `scripts/hooks/tidy-agent-teams.sh` is created, executable, and completes within 5 seconds on the expected directory sizes
- [ ] Script is wired into Stop hooks in `.claude/settings.json`
- [ ] `--dry-run` reports the same candidates a live run would remove, without deleting anything
- [ ] Smoke test with a dummy archived WRK team confirms archived teams are removed and active teams are preserved
- [ ] Empty stale orphaned UUID task dirs older than the cutoff are purged; non-empty or recent dirs are preserved
- [ ] Script prints a stable signal line to stdout: `agent_teams_tidied: deleted=N tasks_purged=M skipped=K`
- [ ] Missing `~/.claude/teams/`, missing `~/.claude/tasks/`, or missing archive directories are handled as zero-state, not errors

## Pseudocode

### spawn-team.sh
```text
spawn_team(wrk_id, slug) -> exit_code  # validate inputs and print deterministic TeamCreate instructions
  require exactly 2 args
  normalize wrk_id by stripping optional "WRK-" prefix only for validation
  validate wrk_id matches ^WRK-[0-9]+$
  validate slug matches ^[a-z0-9-]+$ and is not empty
  team_name = "wrk-" + numeric_part(wrk_id) + "-" + slug

  teams_dir = "${HOME}/.claude/teams"
  if path_exists(teams_dir + "/" + team_name):
    print error "team already exists"
    exit 1

  print "team_name=<team_name>"
  print "description=WRK-<NNN> <slug>"
  print "TeamCreate team_name=<team_name>"
  print "Suggested teammates: <team_name>-lead <team_name>-impl <team_name>-review"
  exit 0
```

### tidy-agent-teams.sh
```text
tidy_agent_teams(dry_run=false) -> exit_code  # delete archived WRK teams and stale empty orphan task dirs
  teams_dir = "${HOME}/.claude/teams"
  tasks_dir = "${HOME}/.claude/tasks"
  archive_dir = "<repo>/.claude/work-queue/archive"

  deleted_teams = 0
  purged_tasks = 0
  skipped = 0

  archived_wrk_ids = build_set_from_files(archive_dir, pattern="WRK-*.md")
    # Use filename stems; do not shell out per team if avoidable.

  for each team_dir in direct_children(teams_dir):
    team_name = basename(team_dir)
    if not matches ^wrk-([0-9]+)-[a-z0-9-]+$:
      skipped += 1
      continue

    wrk_id = "WRK-" + captured_digits
    if wrk_id in archived_wrk_ids:
      report candidate
      if not dry_run:
        remove_directory(team_dir)
      deleted_teams += 1

  cutoff_epoch = now_minus_days(7)
  for each task_dir in direct_children(tasks_dir):
    task_name = basename(task_dir)
    if not matches strict_uuid_v4_or_uuid_generic_pattern:
      skipped += 1
      continue
    if not is_directory(task_dir):
      skipped += 1
      continue
    if not is_empty(task_dir):
      skipped += 1
      continue
    if mtime(task_dir) >= cutoff_epoch:
      skipped += 1
      continue

    report candidate
    if not dry_run:
      remove_directory(task_dir)
    purged_tasks += 1

  print "agent_teams_tidied: deleted=<deleted_teams> tasks_purged=<purged_tasks> skipped=<skipped>"
  exit 0
```

## Tests / Verification (TDD)

`tidy-agent-teams.sh` should not be the only test harness. Treat it as production code plus shell smoke tests around it. Verification should cover behavior, safety, and hook integration.

### TDD cycle per phase

**Before Phase 1**
- Capture current filesystem state under `~/.claude/teams/` and `~/.claude/tasks/`
- Write a dry-run-capable `tidy-agent-teams.sh` skeleton that prints zero-state output when no candidates match
- Red:
  - stale-team fixture present | happy | dry-run reports candidate
  - active-team fixture present | edge | dry-run does not report candidate
  - non-empty UUID task dir present | edge | dry-run does not report candidate

**After Phase 1 cleanup**
- `tidy-agent-teams.sh --dry-run` against the real current state reports `deleted=0 tasks_purged=0` after cleanup
- Re-running the Phase 1 cleanup path makes no further changes
- Audit artifacts exist before deletion evidence is recorded

**After Phase 2 spawn script**
- `spawn-team.sh WRK-1036 test` | happy | prints `wrk-1036-test` recipe and exits 0
- `spawn-team.sh 1036 test` | edge | rejected unless script explicitly supports normalization; behavior documented and tested
- `spawn-team.sh WRK-1036 ""` | error | exits 1
- `spawn-team.sh WRK-1036 Test` | error | exits 1 for uppercase slug
- `spawn-team.sh INVALID slug` | error | exits 1
- duplicate existing `wrk-1036-test` dir | error | exits 1 with deterministic message
- `tidy-agent-teams.sh --dry-run` with `wrk-1036-test` and WRK-1036 not archived | edge | does not mark it for deletion

**After Phase 3 implementation**
- archived WRK file + matching team dir | happy | dry-run reports candidate, live run deletes it
- pending/active WRK file + matching team dir | edge | dry-run/live both preserve it
- empty UUID dir older than cutoff | happy | dry-run reports candidate, live run deletes it
- empty UUID dir newer than cutoff | edge | preserved
- non-empty UUID dir older than cutoff | edge | preserved
- missing `~/.claude/teams/` or `~/.claude/tasks/` | edge | exits 0 and prints zero-state counts
- Stop hook invocation through configured settings path | integration | script runs without repo-relative path failures
- timing check: `time bash scripts/hooks/tidy-agent-teams.sh --dry-run` | non-functional | completes in under 5 seconds on representative state

### Stage-gate verification matrix

| Stage | Tidy check | Spawn check | Expected |
|-------|-----------|-------------|----------|
| After Stage 10 Phase 1 | `--dry-run` against real state | — | No remaining eligible stale items |
| After Stage 10 Phase 2 | `--dry-run` preserves active WRK team | happy + invalid + duplicate + slug validation | All pass |
| After Stage 10 Phase 3 | dry-run then live run on archived-team fixture | — | Archived team deleted, active team preserved |
| Stage 12 (TDD/Eval) | full shell smoke matrix + hook invocation + timing | full argument-validation matrix | All pass, runtime <5s |

## Implementation Sequence

1. **Phase 1** (audit first, destructive cleanup second):
   - Inventory actual candidates under `~/.claude/teams/` and `~/.claude/tasks/`
   - Write per-team audit summaries and capture any needed follow-up WRK items
   - Inspect `c915cd54` before touching UUID cleanup
   - Delete only audited stale teams and purge only confirmed orphan UUID dirs
   - Re-run dry-run verification to confirm idempotent zero-state

2. **Phase 2** (session-start + spawn helper):
   - Edit `session-start/SKILL.md` to add Step 3b with bounded output
   - Write `scripts/work-queue/spawn-team.sh`
   - Make it executable and smoke-test valid, invalid, and duplicate paths
   - Ensure documentation and script behavior use the same naming convention

3. **Phase 3** (Stop hook tidy):
   - Write `scripts/hooks/tidy-agent-teams.sh` in bash without requiring `jq`
   - Prefer repo-root resolution relative to the script location so hook execution is cwd-independent
   - Add the hook entry to `.claude/settings.json`
   - Run dry-run and live smoke tests with controlled fixtures
   - Verify runtime and stdout signal stability

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Tidy deletes an active team because archive detection is wrong | Build archived WRK set from archive filenames once, test active vs archived explicitly, skip unknown name formats |
| Hook runs from unexpected cwd and cannot find repo archive path | Resolve repo root from script location, not `$PWD` |
| `jq` or non-portable shell features are unavailable in the hook environment | Implement in POSIX-friendly bash with coreutils only; avoid `jq` unless settings wiring strictly requires it elsewhere |
| Empty-but-important task dir is purged too aggressively | Restrict purge to UUID-named, empty, older-than-cutoff directories only; inspect exceptional dirs like `c915cd54` before cleanup |
| Team/task counts in plan go stale before execution | Treat counts as current observations, not hardcoded assumptions; implementation should discover actual candidates dynamically |
| Session-start output becomes noisy | Cap Step 3b to concise summary lines and only surface actionable states |
| Stop hook exceeds runtime budget on large task directories | Use non-recursive scans, single-pass directory iteration, and avoid per-item expensive subprocess chains |
| Duplicate/unsafe team names slip through spawn helper | Validate slug charset and reject empty, uppercase, whitespace, or shell-unsafe characters |
| Python helper use drifts from repo policy | Any Python invocation must use `uv run --no-project python ...`; prefer shell-only implementation here to avoid the dependency entirely |

## Codex Notes
- The draft assumes exactly 3 stale teams and 76 orphaned UUID dirs. That should be treated as audit-time evidence, not baked into implementation or AC.
- `tidy-agent-teams.sh` should not depend on `jq` unless there is a demonstrated need. The proposed logic does not require it, and hook environments are safer with fewer external dependencies.
- The original UUID regex `[0-9a-f-]{36}` is too loose and can match non-UUID garbage. Use a stricter UUID pattern or at minimum anchor the regex.
- The original plan does not cover missing-directory behavior, cwd sensitivity in hooks, non-empty orphan dirs, recent empty dirs, or malformed team names. Those are the main deletion-safety edge cases.
- The original TDD section treats the production tidy script as the only living harness. That is weak. Add shell smoke tests that exercise dry-run/live behavior against controlled fixtures.
- The original `spawn-team.sh` pseudocode mentions `MAX_TEAMMATES=10`, which conflicts with scope being out of bounds. The helper should not restate or imply a policy change.
- The original plan does not explicitly test slug validation, empty args, uppercase input, or duplicate team detection beyond one happy-path duplicate case.
- The original integration risk section misses hook execution context and CLI availability. Those are more likely failure modes than the cleanup logic itself.
- No Python is required for the new scripts. Where existing WRK tooling is invoked, keep `uv run --no-project python ...` exactly as required by repo policy.
tokens used
43,336
# WRK-1036 Plan — Agent teams lifecycle: audit, session-start, session-exit tidy

## Mission
Audit stale agent teams, expose actionable team state during session start, and add deterministic session-exit cleanup so archived-team directories and orphaned task directories do not accumulate.

## Scope

### In scope
- Phase 1: audit and clean up the currently identified stale named teams and orphaned UUID task dirs under the Claude state directories
- Phase 2: add a session-start status step and a `spawn-team.sh` helper for WRK-scoped team creation
- Phase 3: add a `tidy-agent-teams.sh` Stop hook and wire it into `.claude/settings.json`

### Out of scope
- WRK-1008 P1 findings beyond capturing them into a separate WRK item
- Changes to `MAX_TEAMMATES` or `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`
- Changes to team member agent logic, routing, or task dispatch behavior
- Any cleanup outside the Claude agent-team/task state directories required by this WRK

## Acceptance Criteria

### Phase 1 — Audit & Cleanup
- [ ] A per-team audit summary is written with: source path, last meaningful signal, attempted work, completion state, and delete/retain rationale
- [ ] WRK-1008 P1 Codex findings are captured as a new WRK item before any related team state is deleted
- [ ] `c915cd54` task-dir contents are inspected; the keep/capture/discard decision is recorded with evidence
- [ ] All targeted stale named teams are removed from `~/.claude/teams/` only after their audit records exist
- [ ] All purge-eligible orphaned UUID task dirs are removed from `~/.claude/tasks/` only after the `c915cd54` decision is resolved
- [ ] Non-target directories that do not match expected naming rules are skipped and reported, not deleted
- [ ] Cleanup commands are idempotent: rerunning Phase 1 after success yields zero additional deletions

### Phase 2 — Session-start availability
- [ ] `session-start/SKILL.md` includes a new Step 3b for agent-team status, capped at 10 lines of user-facing output
- [ ] `scripts/work-queue/spawn-team.sh` is created, executable, and validated
- [ ] Naming convention `wrk-<NNN>-<slug>` is documented and enforced by the script
- [ ] Script rejects malformed WRK ids, empty slugs, uppercase slug content, unsafe characters, and duplicate teams with non-zero exit
- [ ] Script does not create teams itself; it emits deterministic instructions only

### Phase 3 — Session-exit tidy
- [ ] `scripts/hooks/tidy-agent-teams.sh` is created, executable, and completes within 5 seconds on the expected directory sizes
- [ ] Script is wired into Stop hooks in `.claude/settings.json`
- [ ] `--dry-run` reports the same candidates a live run would remove, without deleting anything
- [ ] Smoke test with a dummy archived WRK team confirms archived teams are removed and active teams are preserved
- [ ] Empty stale orphaned UUID task dirs older than the cutoff are purged; non-empty or recent dirs are preserved
- [ ] Script prints a stable signal line to stdout: `agent_teams_tidied: deleted=N tasks_purged=M skipped=K`
- [ ] Missing `~/.claude/teams/`, missing `~/.claude/tasks/`, or missing archive directories are handled as zero-state, not errors

## Pseudocode

### spawn-team.sh
```text
spawn_team(wrk_id, slug) -> exit_code  # validate inputs and print deterministic TeamCreate instructions
  require exactly 2 args
  normalize wrk_id by stripping optional "WRK-" prefix only for validation
  validate wrk_id matches ^WRK-[0-9]+$
  validate slug matches ^[a-z0-9-]+$ and is not empty
  team_name = "wrk-" + numeric_part(wrk_id) + "-" + slug

  teams_dir = "${HOME}/.claude/teams"
  if path_exists(teams_dir + "/" + team_name):
    print error "team already exists"
    exit 1

  print "team_name=<team_name>"
  print "description=WRK-<NNN> <slug>"
  print "TeamCreate team_name=<team_name>"
  print "Suggested teammates: <team_name>-lead <team_name>-impl <team_name>-review"
  exit 0
```

### tidy-agent-teams.sh
```text
tidy_agent_teams(dry_run=false) -> exit_code  # delete archived WRK teams and stale empty orphan task dirs
  teams_dir = "${HOME}/.claude/teams"
  tasks_dir = "${HOME}/.claude/tasks"
  archive_dir = "<repo>/.claude/work-queue/archive"

  deleted_teams = 0
  purged_tasks = 0
  skipped = 0

  archived_wrk_ids = build_set_from_files(archive_dir, pattern="WRK-*.md")
    # Use filename stems; do not shell out per team if avoidable.

  for each team_dir in direct_children(teams_dir):
    team_name = basename(team_dir)
    if not matches ^wrk-([0-9]+)-[a-z0-9-]+$:
      skipped += 1
      continue

    wrk_id = "WRK-" + captured_digits
    if wrk_id in archived_wrk_ids:
      report candidate
      if not dry_run:
        remove_directory(team_dir)
      deleted_teams += 1

  cutoff_epoch = now_minus_days(7)
  for each task_dir in direct_children(tasks_dir):
    task_name = basename(task_dir)
    if not matches strict_uuid_v4_or_uuid_generic_pattern:
      skipped += 1
      continue
    if not is_directory(task_dir):
      skipped += 1
      continue
    if not is_empty(task_dir):
      skipped += 1
      continue
    if mtime(task_dir) >= cutoff_epoch:
      skipped += 1
      continue

    report candidate
    if not dry_run:
      remove_directory(task_dir)
    purged_tasks += 1

  print "agent_teams_tidied: deleted=<deleted_teams> tasks_purged=<purged_tasks> skipped=<skipped>"
  exit 0
```

## Tests / Verification (TDD)

`tidy-agent-teams.sh` should not be the only test harness. Treat it as production code plus shell smoke tests around it. Verification should cover behavior, safety, and hook integration.

### TDD cycle per phase

**Before Phase 1**
- Capture current filesystem state under `~/.claude/teams/` and `~/.claude/tasks/`
- Write a dry-run-capable `tidy-agent-teams.sh` skeleton that prints zero-state output when no candidates match
- Red:
  - stale-team fixture present | happy | dry-run reports candidate
  - active-team fixture present | edge | dry-run does not report candidate
  - non-empty UUID task dir present | edge | dry-run does not report candidate

**After Phase 1 cleanup**
- `tidy-agent-teams.sh --dry-run` against the real current state reports `deleted=0 tasks_purged=0` after cleanup
- Re-running the Phase 1 cleanup path makes no further changes
- Audit artifacts exist before deletion evidence is recorded

**After Phase 2 spawn script**
- `spawn-team.sh WRK-1036 test` | happy | prints `wrk-1036-test` recipe and exits 0
- `spawn-team.sh 1036 test` | edge | rejected unless script explicitly supports normalization; behavior documented and tested
- `spawn-team.sh WRK-1036 ""` | error | exits 1
- `spawn-team.sh WRK-1036 Test` | error | exits 1 for uppercase slug
- `spawn-team.sh INVALID slug` | error | exits 1
- duplicate existing `wrk-1036-test` dir | error | exits 1 with deterministic message
- `tidy-agent-teams.sh --dry-run` with `wrk-1036-test` and WRK-1036 not archived | edge | does not mark it for deletion

**After Phase 3 implementation**
- archived WRK file + matching team dir | happy | dry-run reports candidate, live run deletes it
- pending/active WRK file + matching team dir | edge | dry-run/live both preserve it
- empty UUID dir older than cutoff | happy | dry-run reports candidate, live run deletes it
- empty UUID dir newer than cutoff | edge | preserved
- non-empty UUID dir older than cutoff | edge | preserved
- missing `~/.claude/teams/` or `~/.claude/tasks/` | edge | exits 0 and prints zero-state counts
- Stop hook invocation through configured settings path | integration | script runs without repo-relative path failures
- timing check: `time bash scripts/hooks/tidy-agent-teams.sh --dry-run` | non-functional | completes in under 5 seconds on representative state

### Stage-gate verification matrix

| Stage | Tidy check | Spawn check | Expected |
|-------|-----------|-------------|----------|
| After Stage 10 Phase 1 | `--dry-run` against real state | — | No remaining eligible stale items |
| After Stage 10 Phase 2 | `--dry-run` preserves active WRK team | happy + invalid + duplicate + slug validation | All pass |
| After Stage 10 Phase 3 | dry-run then live run on archived-team fixture | — | Archived team deleted, active team preserved |
| Stage 12 (TDD/Eval) | full shell smoke matrix + hook invocation + timing | full argument-validation matrix | All pass, runtime <5s |

## Implementation Sequence

1. **Phase 1** (audit first, destructive cleanup second):
   - Inventory actual candidates under `~/.claude/teams/` and `~/.claude/tasks/`
   - Write per-team audit summaries and capture any needed follow-up WRK items
   - Inspect `c915cd54` before touching UUID cleanup
   - Delete only audited stale teams and purge only confirmed orphan UUID dirs
   - Re-run dry-run verification to confirm idempotent zero-state

2. **Phase 2** (session-start + spawn helper):
   - Edit `session-start/SKILL.md` to add Step 3b with bounded output
   - Write `scripts/work-queue/spawn-team.sh`
   - Make it executable and smoke-test valid, invalid, and duplicate paths
   - Ensure documentation and script behavior use the same naming convention

3. **Phase 3** (Stop hook tidy):
   - Write `scripts/hooks/tidy-agent-teams.sh` in bash without requiring `jq`
   - Prefer repo-root resolution relative to the script location so hook execution is cwd-independent
   - Add the hook entry to `.claude/settings.json`
   - Run dry-run and live smoke tests with controlled fixtures
   - Verify runtime and stdout signal stability

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Tidy deletes an active team because archive detection is wrong | Build archived WRK set from archive filenames once, test active vs archived explicitly, skip unknown name formats |
| Hook runs from unexpected cwd and cannot find repo archive path | Resolve repo root from script location, not `$PWD` |
| `jq` or non-portable shell features are unavailable in the hook environment | Implement in POSIX-friendly bash with coreutils only; avoid `jq` unless settings wiring strictly requires it elsewhere |
| Empty-but-important task dir is purged too aggressively | Restrict purge to UUID-named, empty, older-than-cutoff directories only; inspect exceptional dirs like `c915cd54` before cleanup |
| Team/task counts in plan go stale before execution | Treat counts as current observations, not hardcoded assumptions; implementation should discover actual candidates dynamically |
| Session-start output becomes noisy | Cap Step 3b to concise summary lines and only surface actionable states |
| Stop hook exceeds runtime budget on large task directories | Use non-recursive scans, single-pass directory iteration, and avoid per-item expensive subprocess chains |
| Duplicate/unsafe team names slip through spawn helper | Validate slug charset and reject empty, uppercase, whitespace, or shell-unsafe characters |
| Python helper use drifts from repo policy | Any Python invocation must use `uv run --no-project python ...`; prefer shell-only implementation here to avoid the dependency entirely |

## Codex Notes
- The draft assumes exactly 3 stale teams and 76 orphaned UUID dirs. That should be treated as audit-time evidence, not baked into implementation or AC.
- `tidy-agent-teams.sh` should not depend on `jq` unless there is a demonstrated need. The proposed logic does not require it, and hook environments are safer with fewer external dependencies.
- The original UUID regex `[0-9a-f-]{36}` is too loose and can match non-UUID garbage. Use a stricter UUID pattern or at minimum anchor the regex.
- The original plan does not cover missing-directory behavior, cwd sensitivity in hooks, non-empty orphan dirs, recent empty dirs, or malformed team names. Those are the main deletion-safety edge cases.
- The original TDD section treats the production tidy script as the only living harness. That is weak. Add shell smoke tests that exercise dry-run/live behavior against controlled fixtures.
- The original `spawn-team.sh` pseudocode mentions `MAX_TEAMMATES=10`, which conflicts with scope being out of bounds. The helper should not restate or imply a policy change.
- The original plan does not explicitly test slug validation, empty args, uppercase input, or duplicate team detection beyond one happy-path duplicate case.
- The original integration risk section misses hook execution context and CLI availability. Those are more likely failure modes than the cleanup logic itself.
- No Python is required for the new scripts. Where existing WRK tooling is invoked, keep `uv run --no-project python ...` exactly as required by repo policy.
