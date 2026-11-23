# WRK-1174: Agent Scope Guard — One-Feature-Per-Session Discipline

## Context

Anthropic identifies "the agent's tendency to do too much at once" as the core failure mode for long-running agents. Workspace-hub tracks active WRK via `.claude/state/active-wrk` (plain-text file), but nothing prevents an agent from activating a second WRK mid-session without completing the first.

## Plan (Route A — 3 deliverables)

### 1. Enhance `set-active-wrk.sh` with scope guard + timestamp

**File:** `scripts/work-queue/set-active-wrk.sh`

- Before writing new WRK ID, check if `active-wrk` already contains a WRK ID
- If current WRK exists and differs from requested WRK: check if current WRK status is `done` or `archived`
  - If NOT done/archived → print `SCOPE_GUARD_WARNING` to stderr and exit 1
  - If done/archived → allow overwrite
- Change state format from plain-text to include timestamp: write `WRK-NNN` on line 1, `started_at: <ISO8601>` on line 2
- Add `--force` flag to bypass guard (for legitimate multi-WRK scenarios like archival)

**Reuse:** existing `find` logic at line 13 for WRK file lookup; extend to check `status:` in frontmatter

### 2. Add scope discipline reminder to session-start skill

**File:** `.claude/skills/workspace-hub/session-start/SKILL.md`

- Add new step **3d. Scope Discipline Check** after step 3c (Active Session Audit)
- Read `.claude/state/active-wrk` — if non-empty, display:
  ```
  **Active WRK:** WRK-NNN (started: <timestamp>)
  ⚠ One-feature-per-session: complete or checkpoint this WRK before starting another.
  ```
- This is informational only (no hard block at session-start)

### 3. Add scope guard documentation to work-queue SKILL.md

**File:** `.claude/skills/coordination/workspace/work-queue/SKILL.md`

- Add `## Scope Discipline` section after `## Parallel Work Policy`
- Document the one-feature-per-session rule and `--force` bypass

## Test Plan

| # | What | Type | Expected |
|---|------|------|----------|
| 1 | `set-active-wrk.sh WRK-999` when active-wrk has WRK-888 (status: working) | edge | Exit 1, SCOPE_GUARD_WARNING |
| 2 | `set-active-wrk.sh WRK-999` when active-wrk is empty | happy | Exit 0, writes WRK-999 + timestamp |
| 3 | `set-active-wrk.sh WRK-999 --force` when active-wrk has WRK-888 | happy | Exit 0, overwrites |
| 4 | `set-active-wrk.sh WRK-999` when active-wrk has WRK-888 (status: done) | edge | Exit 0, allows overwrite |

## Scripts-Over-LLM Audit

No new scripts needed beyond the `set-active-wrk.sh` enhancement — the guard logic is deterministic shell code in an existing script.

## Verification

```bash
# Test 1: Guard blocks second WRK
echo "WRK-888" > .claude/state/active-wrk
bash scripts/work-queue/set-active-wrk.sh WRK-999  # should fail

# Test 2: Force bypass works
bash scripts/work-queue/set-active-wrk.sh WRK-999 --force  # should succeed

# Test 3: Empty state works
> .claude/state/active-wrk
bash scripts/work-queue/set-active-wrk.sh WRK-999  # should succeed

# Test 4: Verify timestamp written
cat .claude/state/active-wrk  # should show WRK-999 + started_at
```

## Files Modified

1. `scripts/work-queue/set-active-wrk.sh` — scope guard + timestamp
2. `.claude/skills/workspace-hub/session-start/SKILL.md` — step 3d
3. `.claude/skills/coordination/workspace/work-queue/SKILL.md` — scope discipline section
