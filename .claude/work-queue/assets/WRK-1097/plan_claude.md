# WRK-1097 Plan — surface unclaimed-but-active items + active-sessions skill
# v2 — post cross-review (Codex REQUEST_CHANGES fixed, Gemini MINOR fixed)

## Mission
Prevent /whats-next from showing actively-executing WRK items as "high-ready" when
claim-item.sh was not run. Add session discovery as a reusable capability.

## Route: B (Medium)

## Key Design Decision (fixed after Codex review)

**session_pid is NOT useful for liveness.** It stores the PID of `start_stage.py`
(a short-lived script that exits immediately). `kill -0 <pid>` will always fail.

**Canonical detection logic:**
1. **Claimed/unclaimed** = queue folder location (`working/` vs `pending/`) — NOT lock status field
2. **Liveness filter** = `locked_at` recency < 2h (age-only heuristic, documented as such)
3. **Lock `status` field** = advisory only (double `status:` bug in claim-item.sh means it's unreliable)

Future WRK: Add heartbeat mechanism (session writes timestamp every N min) for true liveness.

## Deliverables

### Scripts (4)

| File | Change |
|------|--------|
| `scripts/work-queue/whats-next.sh` | Add `⚠ IN-PROGRESS UNCLAIMED` section; pending items with recent session-lock (< 2h) |
| `scripts/work-queue/active-sessions.sh` *(new)* | Scan all `assets/*/evidence/session-lock.yaml`; classify by queue location + lock age |
| `scripts/work-queue/start_stage.py` | Hard error for stage ≥9 if item still in `pending/`; clear actionable message |
| `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` | Stage 8 = hard gate + active-sessions pointer |

### Skills (3)

| File | Change |
|------|--------|
| `.claude/skills/workspace-hub/active-sessions/SKILL.md` *(new)* | Skill wrapping active-sessions.sh — reuse at session-start, claim-item, whats-next |
| `.claude/skills/workspace-hub/whats-next/SKILL.md` | Add `⚠ IN-PROGRESS UNCLAIMED` to output sections table |
| `.claude/skills/workspace-hub/session-start/SKILL.md` | Add Step 3c: run active-sessions.sh at session start |

## active-sessions.sh Design (v1 — age-only, intentional)

```bash
Usage: bash scripts/work-queue/active-sessions.sh [--json] [--unclaimed-only]

For each assets/WRK-NNN/evidence/session-lock.yaml:
  1. Read: wrk_id, locked_at, hostname
  2. Age = now - locked_at (seconds)
  3. Skip if age > 7200 (2h) — stale
  4. Queue location: check working/WRK-NNN.md vs pending/WRK-NNN.md
  5. claimed   = found in working/
     unclaimed = found in pending/
     unknown   = not in either (may be mid-claim or archived)
  6. Output row: WRK-ID  STATUS  AGE  HOSTNAME  LOCKED_AT
```

*v1 is age-only heuristic. PID check removed (session_pid is start_stage.py — short-lived).*
*Future WRK: heartbeat file for true liveness.*

## whats-next.sh — Detection Function

```bash
has_recent_session_lock() {
  local lock="$1"
  [[ ! -f "$lock" ]] && return 1
  local locked_at
  locked_at=$(grep "^locked_at:" "$lock" | tr -d '"' | awk '{print $2}')
  [[ -z "$locked_at" ]] && return 1
  local age=$(( $(date +%s) - $(date -d "$locked_at" +%s 2>/dev/null || echo 0) ))
  [[ $age -lt 7200 ]]   # < 2h = recent
}
```

For each pending item: if lock present AND age < 2h → UNCLAIMED_ACTIVE array → own section.
Item is excluded from HIGH_UNBLOCKED/MED_UNBLOCKED (not shown twice).

## start_stage.py Guard

```python
# After archive check, before stage-1 block
if stage >= 9:
    pending_path = Path(queue_dir) / "pending" / f"{wrk_id}.md"
    if pending_path.exists():
        print(
            f"✖ {wrk_id} is still in pending/ — claim it first:\n"
            f"  bash scripts/work-queue/claim-item.sh {wrk_id}",
            file=sys.stderr,
        )
        sys.exit(1)
```

## Test Strategy (TDD — tests first)
`scripts/work-queue/tests/test_unclaimed_detection.py` (8 tests):
1. pending + lock age 30min → UNCLAIMED section
2. pending + lock age 3h → NOT in UNCLAIMED (stale), normal HIGH bucket
3. pending + no lock → normal HIGH bucket
4. pending + lock age exactly 7200s → boundary: stale (not shown)
5. active-sessions.sh: item in pending/ + recent lock → unclaimed
6. active-sessions.sh: item in working/ + recent lock → claimed
7. active-sessions.sh: lock age > 2h → skipped
8. start_stage stage 9 + pending/ → exit(1) with claim message
9. start_stage stage 9 + working/ → no error
10. start_stage stage 2 + pending/ → no error (pre-claim OK)

## Execution Order
1. Write tests (TDD)
2. Implement `active-sessions.sh`
3. Wire into `whats-next.sh` (UNCLAIMED section)
4. Implement `start_stage.py` guard (stage ≥9)
5. Update `work-queue-workflow/SKILL.md` (Stage 8 hard gate)
6. Write `active-sessions/SKILL.md` (new skill)
7. Update `whats-next/SKILL.md` + `session-start/SKILL.md`
8. Run all tests + existing test suite
9. Future WRK: heartbeat mechanism for true liveness (spin off)

## Cross-Review Resolution
- Codex REQUEST_CHANGES: **FIXED** — removed PID check; age-only v1; queue location = canonical source
- Gemini MINOR: **FIXED** — clear error message in start_stage.py; hostname documented as same-machine
