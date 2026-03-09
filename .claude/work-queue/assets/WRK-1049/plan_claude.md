# WRK-1049 Plan — Prevent Concurrent Session Claim Collision (rev 2)

## Codex P1/P2 Resolutions

**P1 (atomicity)**: `mv` on the same filesystem uses `rename(2)` which is atomic.
If two sessions both pass the working/ pre-check before either reaches mv, the second
session's mv will fail with "No such file or directory" (the source file is gone after the
first mv). The pre-check is a fast-fail guard; the mv itself is the atomic race-breaker.
`claim-item.sh` asserts mv exit code and propagates failure.

**P2 (active-wrk)**: Added P4 — validate `.claude/state/active-wrk` at Stage 1.
If active-wrk points to a different WRK still in working/, warn and log.

**P2 (lock lifecycle)**: Defined — lock written at Stage 1 with `status: in_progress`,
updated to `status: claimed` when claim-item.sh succeeds. Never deleted (audit trail).
Stale if `session_pid` no longer alive on `hostname`.

---

## P1 — Retire `process.md` Step 4 Auto-Claim

**File**: `.claude/skills/coordination/workspace/work-queue/actions/process.md`

Replace Step 4 (the `mv pending→working` bash snippet) with a script-first redirect:

```
## Step 4: Claim via claim-item.sh (MANDATORY)

Run the canonical claim script. Do not move files manually.

    bash scripts/work-queue/claim-item.sh WRK-NNN

If the script exits non-zero, stop. Do not proceed to Stage 9.
See scripts/work-queue/claim-item.sh for claim gate details.
```

No inline bash. No operational duplication. process.md is a pointer only.

---

## P2 — Session Lock in `start_stage.py` Stage 1

**File**: `scripts/work-queue/start_stage.py`

After `assets_dir.mkdir(exist_ok=True)`, write session ownership lock:

```python
import os, socket, datetime
lock = assets_dir / "evidence" / "session-lock.yaml"
lock.write_text(
    f"wrk_id: {wrk_id}\n"
    f"session_pid: {os.getpid()}\n"
    f"hostname: {socket.gethostname()}\n"
    f"locked_at: \"{datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}\"\n"
    f"status: in_progress\n"
)
```

Lock lifecycle:
- Written at Stage 1 with `status: in_progress`
- Updated to `status: claimed` by claim-item.sh on successful claim
- Never deleted — serves as audit trail; stale if `session_pid` no longer alive

---

## P3 — working/ Pre-check + Atomic mv Guard in `claim-item.sh`

**File**: `scripts/work-queue/claim-item.sh`

Insert before the existing mv command:

```bash
# Fast-fail: warn immediately if already claimed by another session
if [[ -f "${QUEUE_DIR}/working/${WRK_ID}.md" ]]; then
  echo "✖ ${WRK_ID} is already in working/ — concurrent session collision." >&2
  lock_file="${QUEUE_DIR}/../assets/${WRK_ID}/evidence/session-lock.yaml"
  [[ -f "$lock_file" ]] && grep -E 'hostname|locked_at|session_pid|status' "$lock_file" >&2
  exit 1
fi

# Atomic claim: mv uses rename(2) — if a racing session claimed first,
# source file is gone and mv exits non-zero (race-safe by filesystem guarantee)
mv "${FILE_PATH}" "${QUEUE_DIR}/working/${WRK_ID}.md" || {
  echo "✖ ${WRK_ID} claim race: source gone (another session claimed first)." >&2
  exit 1
}

# Update session-lock status to claimed
lock_file="${QUEUE_DIR}/../assets/${WRK_ID}/evidence/session-lock.yaml"
if [[ -f "$lock_file" ]]; then
  printf "\nstatus: claimed\nclaimed_at: \"%s\"\n" \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$lock_file"
fi
```

---

## P4 — active-wrk Pre-validation in `start_stage.py` Stage 1

**File**: `scripts/work-queue/start_stage.py`

Before writing the session lock, check `.claude/state/active-wrk`:

```python
active_wrk_path = workspace_root / ".claude" / "state" / "active-wrk"
if active_wrk_path.exists():
    current = active_wrk_path.read_text().strip()
    if current and current != wrk_id:
        working_dir = workspace_root / ".claude" / "work-queue" / "working"
        if (working_dir / f"{current}.md").exists():
            print(f"⚠ Warning: active-wrk={current} is still in working/. "
                  f"Starting {wrk_id} anyway — verify no collision.", flush=True)
```

Warns but does not block (active-wrk may be stale from a crashed session).

---

## Test Plan

**New test** `scripts/work-queue/tests/test-claim-collision.sh`:
- T1: claim-item.sh on a pending item → exits 0 (baseline)
- T2: claim-item.sh when WRK already in working/ → exits 1 with collision message
- T3: start_stage.py Stage 1 → session-lock.yaml written with pid/hostname/locked_at/status=in_progress
- T4: claim-item.sh success → session-lock.yaml updated with status=claimed
- T5: Two concurrent claim-item.sh calls → exactly one succeeds, second exits 1

**Existing tests**: full `scripts/work-queue/tests/` suite after changes.

## Files Changed
1. `.claude/skills/coordination/workspace/work-queue/actions/process.md` — Step 4 script-first redirect
2. `scripts/work-queue/start_stage.py` — session-lock write + active-wrk warn at Stage 1
3. `scripts/work-queue/claim-item.sh` — working/ pre-check + atomic mv guard + lock status update
4. `scripts/work-queue/tests/test-claim-collision.sh` — new T1–T5 test suite

## Acceptance Criteria
- [ ] process.md Step 4 is a script-first redirect (no bash mv logic)
- [ ] A WRK item can never exist in both pending/ and working/ after claim-item.sh runs
- [ ] Concurrent claim attempts: second exits 1 (working/ check or mv failure)
- [ ] session-lock.yaml written at Stage 1; updated to status=claimed on successful claim
- [ ] active-wrk mismatch logs a warning when existing working/ item detected
- [ ] T1–T5 all pass
