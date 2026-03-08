YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
# WRK-1036 Plan — Agent teams lifecycle: audit, session-start, session-exit tidy

## Mission
Audit stale agent teams, make teams readily available at session-start, and add an idempotent, fail-safe session-exit tidy-up so ghost teams and orphaned task dirs never accumulate again without risking active work.

## Scope

### In scope
- Phase 1: audit + cleanup of 3 stale named teams and 76 orphaned UUID task dirs.
- Phase 2: session-start SKILL.md step + `spawn-team.sh` helper script with strict input validation.
- Phase 3: `tidy-agent-teams.sh` Stop hook + robust, non-destructive wiring into `settings.json`.
- Graceful degradation: Scripts must exit cleanly if target directories (`~/.claude/teams/`, `~/.claude/tasks/`) do not exist.

### Out of scope
- WRK-1008 P1 findings (separate WRK to be captured in Phase 1)
- Changes to MAX_TEAMMATES or CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS settings
- Any changes to team member agent logic or task dispatch

## Acceptance Criteria

### Phase 1 — Audit & Cleanup
- [ ] Per-team audit summary written (what attempted / completed / abandoned).
- [ ] WRK-1008 P1 Codex findings captured as new WRK item before team deleted.
- [ ] c915cd54 UUID dir WAR-extractor work investigated; decision recorded.
- [ ] All 3 named teams safely deleted from `~/.claude/teams/`.
- [ ] All 76 UUID task dirs purged from `~/.claude/tasks/` (after c915cd54 resolved).

### Phase 2 — Session-start availability
- [ ] `session-start/SKILL.md` has new Step 3b: agent-teams status (≤10 lines).
- [ ] `scripts/work-queue/spawn-team.sh` created, executable, and tested for missing/invalid arguments.
- [ ] Naming convention `wrk-NNN-<slug>` documented and enforced via strict regex in spawn script.

### Phase 3 — Session-exit tidy
- [ ] `scripts/hooks/tidy-agent-teams.sh` created (<50 lines, <5s runtime, strict `set -euo pipefail`).
- [ ] Script wired into Stop hooks in `.claude/settings.json` (must safely handle malformed JSON).
- [ ] `--dry-run` flag shows correct candidates and is mathematically guaranteed not to mutate state.
- [ ] Smoke test: dummy team + archived WRK → tidy detects and removes.
- [ ] Signal `agent_teams_tidied: N deleted, M tasks purged` printed to stdout.
- [ ] Execution gracefully skips and logs a warning if `~/.claude/teams` or `~/.claude/tasks` do not exist.

## Pseudocode

### spawn-team.sh
```bash
spawn-team(wrk_id, slug):
  # Strict validation
  if wrk_id or slug is empty → exit 1 with usage
  if wrk_id does not match ^WRK-\d+$ → exit 1 "Invalid WRK ID"
  if slug does not match ^[a-z0-9-]+$ → exit 1 "Invalid slug"
  
  team_name = "wrk-" + wrk_id.lower() + "-" + slug
  teams_dir = ~/.claude/teams/
  
  if directory teams_dir/team_name exists → exit 1 "Team already exists"
  
  print "Spawn in Claude: TeamCreate team_name=" + team_name
  print "MAX_TEAMMATES=10 — name teammates: " + team_name + "-lead, " + team_name + "-impl"
```

### tidy-agent-teams.sh
```bash
tidy-agent-teams(dry_run=false):
  set -euo pipefail
  archive_dir="workspace_hub/.claude/work-queue/archive/"
  deleted_teams=0; purged_tasks=0

  # Safe directory checks
  if [ -d "$HOME/.claude/teams" ]; then
    for dir in "$HOME/.claude/teams"/wrk-*; do
      [ -e "$dir" ] || continue
      team_name=$(basename "$dir")
      
      # Extract WRK ID safely
      if [[ "$team_name" =~ ^wrk-([0-9]+)- ]]; then
        wrk_id="WRK-${BASH_REMATCH[1]}"
        # Exact match required to prevent false positives
        if [ -f "$archive_dir/$wrk_id.md" ]; then
          if [ "$dry_run" = false ]; then rm -rf "$dir"; fi
          ((deleted_teams++))
        fi
      fi
    done
  fi

  if [ -d "$HOME/.claude/tasks" ]; then
    # Use cross-platform compatible find / date logic
    # Find empty directories older than 7 days matching UUID pattern
    cutoff_days=7
    while IFS= read -r dir; do
      if [[ $(basename "$dir") =~ ^[0-9a-f-]{36}$ ]]; then
        if [ "$dry_run" = false ]; then rm -rf "$dir"; fi
        ((purged_tasks++))
      fi
    done < <(find "$HOME/.claude/tasks" -mindepth 1 -maxdepth 1 -type d -empty -mtime +$cutoff_days)
  fi

  echo "agent_teams_tidied: deleted=$deleted_teams tasks_purged=$purged_tasks"
```

## Tests / Verification (TDD)

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
- `spawn-team.sh ""` → exit 1 with usage instructions ✓

**After Phase 3 implementation** — full tidy logic in place:
- Create dummy archived WRK dir under `archive/` + dummy team dir `wrk-9999-dummy`:
  `tidy-agent-teams.sh --dry-run` → lists `wrk-9999-dummy` as candidate, no deletions ✓
  `tidy-agent-teams.sh` (live) → deletes `wrk-9999-dummy`, prints `deleted=1 tasks_purged=N` ✓
- `tidy-agent-teams.sh` with active WRK team (`wrk-1036-test`, WRK-1036 in pending/) → skips it ✓
- Stop hook timing: `time bash scripts/hooks/tidy-agent-teams.sh` → <5s ✓
- Missing directory test: Temporarily rename `~/.claude/teams`, verify script exits 0 gracefully ✓

## Implementation Sequence

1. **Phase 1** (audit — read only, no writes until decisions confirmed):
   - Write per-team summary from inbox messages already read.
   - Capture WRK for WRK-1008 P1 Codex findings.
   - Investigate c915cd54 content; decide capture-or-discard.
   - Delete all 3 named teams; purge UUID task dirs.

2. **Phase 2** (session-start + spawn script):
   - Edit `session-start/SKILL.md` — insert Step 3b after Step 3.
   - Write `scripts/work-queue/spawn-team.sh` (bash, ~25 lines, `set -euo pipefail`).
   - `chmod +x` the script; smoke-test locally.

3. **Phase 3** (Stop hook):
   - Write `scripts/hooks/tidy-agent-teams.sh` (bash, <50 lines).
   - Backup `.claude/settings.json`, then add entry to Stop hooks array (verify JSON validity with `jq . .claude/settings.json`).
   - Run `--dry-run` to confirm detection logic.
   - Create dummy team, confirm live run deletes it.

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| tidy deletes an active team | Strict regex parsing; only deletes when explicit exact match `WRK-NNN.md` file is found in `archive/`. |
| c915cd54 WAR extractor work is unrecoverable | Read task JSON fully before purging; capture WRK if needed. |
| Stop hook exceeds 5s on large task dirs | Use `find -mindepth 1 -maxdepth 1` to avoid recursive tree traversal. |
| `rm -rf` deletes wrong directory | Quote all variables; ensure script runs with `set -eu` so it fails immediately if variables are unbound. |
| JSON corruption during hook injection | Manual backup of `settings.json` + `jq` linting before applying changes. |
| Missing user directories cause hook failure | Explicit `-d` existence checks before running loop logic. |

---

## Gemini Notes (Systems Reliability Audit)

*(Note: The review prompts provided included criteria tailored for a different architecture—specifically L3 parsing, portfolio-signals, dual-mode thresholds, and cron tasks. I have audited the WRK-1036 plan using those conceptual lenses to ensure maximum robustness.)*

1. **Failure Modes in Output Parsing (L3 Gemini or Script Output)**:
   - *Concern*: If `.claude/settings.json` is modified programmatically in the future, relying on unstructured CLI output or manual injection is risky.
   - *Recommendation*: Ensure any script output (`agent_teams_tidied: N deleted...`) is rigidly formatted. If downstream hooks parse this, emit standard JSON instead of plain text to avoid regex-parsing fragility. 
2. **Carry-Forward Logic (`portfolio-signals.yaml` / Global State equivalent)**:
   - *Concern*: What happens if the `archive/` directory itself is missing or corrupted, or if `.claude/settings.json` becomes invalid?
   - *Recommendation*: The scripts must treat missing state as an active safety halt. If `workspace_hub/.claude/work-queue/archive/` does not exist, `tidy-agent-teams.sh` should exit cleanly rather than assuming 0 archives. This prevents accidental deletion logic if the workspace is mounted incorrectly.
3. **Dual-Mode Tie-Break (Engineering >= Harness equivalent)**:
   - *Concern*: When determining if a task directory is "abandoned", relying solely on "is it empty?" and "is it older than 7 days?" might result in deleting valid, empty directories that are actively holding a structure.
   - *Recommendation*: The threshold logic (`-empty -mtime +7`) is currently acceptable, but if task directories ever contain hidden state `.dotfiles` immediately on creation, `-empty` will fail to clean them up. Verify that Claude's task UUID directories are strictly empty when orphaned.
4. **Test Coverage (16 tests vs. AC Surface Area)**:
   - *Concern*: The plan relies on a manual TDD cycle. While sufficient for a bash script, it leaves gaps for edge cases (e.g., directory names with spaces, symlinks, or missing permissions).
   - *Recommendation*: Add specific test cases to the TDD cycle for: 
     - A team name with invalid characters.
     - Execution when `~/.claude/tasks/` contains non-directory files matching the UUID pattern.
     - Execution when `jq` is uninstalled (if relied upon later).
5. **Nightly Cron Risks vs. Stop Hook Execution**:
   - *Concern*: The original prompt asked about 3am cron risks, version drift, and file lock races. WRK-1036 utilizes a Stop hook instead of a cron job, which mitigates time-based quotas but introduces execution-time blocking.
   - *Recommendation*: Since the hook fires at every stage-gate Stop, multiple agents closing work simultaneously could create race conditions on `rm -rf`. While minor, adding a simple file lock or utilizing atomic directory moves (`mv dir /tmp/trash && rm -rf /tmp/trash &`) can prevent IO blocking and race condition errors during the session-exit tidy. Ensure the script runtime remains strictly under the 5s limit by adhering to the non-recursive `find` pattern defined in the plan.
