# WRK-1049 Plan — Prevent Concurrent Session Claim Collision

## P1 — Retire `process.md` Step 4 Auto-Claim

**File**: `.claude/skills/coordination/workspace/work-queue/actions/process.md`

Replace the entire Step 4 block (lines 75–105, the bash `mv pending→working` snippet)
with a hard redirect to `claim-item.sh`:

```markdown
## Step 4: Claim via claim-item.sh (MANDATORY — do not mv manually)

NEVER move the item from `pending/` to `working/` directly. The 20-stage lifecycle
requires all gate evidence to be captured through the claim gate.

Run:
```bash
bash scripts/work-queue/claim-item.sh WRK-NNN
```

This script:
- Validates quota, session_id, and Stage 7 gate evidence
- Updates frontmatter (status: working, claimed_at, route)
- Moves the file atomically (pending/ → working/)
- Writes claim-evidence.yaml and activation.yaml

If claim-item.sh exits non-zero, stop — do not proceed to Stage 9.
```

---

## P2 — Session Lock in `start_stage.py` Stage 1

**File**: `scripts/work-queue/start_stage.py`

In the Stage 1 block, after creating the assets dir, write
`assets/WRK-NNN/evidence/session-lock.yaml`:

```python
# Stage 1: write session ownership lock
import os, socket, datetime
lock_path = assets_dir / "evidence" / "session-lock.yaml"
lock_path.write_text(
    f"wrk_id: {wrk_id}\n"
    f"session_pid: {os.getpid()}\n"
    f"hostname: {socket.gethostname()}\n"
    f"locked_at: \"{datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}\"\n"
)
```

`claim-item.sh` (P3) checks this file to warn about in-progress sessions.

---

## P3 — working/ Pre-check in `claim-item.sh`

**File**: `scripts/work-queue/claim-item.sh`

Insert after the `FILE_PATH` resolution block (after line ~27, before provider check):

```bash
# Guard: reject claim if already in working/ (concurrent session collision)
if [[ -f "${QUEUE_DIR}/working/${WRK_ID}.md" ]]; then
  echo "✖ Error: ${WRK_ID} is already in working/ — another session may be active." >&2
  lock_file="${QUEUE_DIR}/../assets/${WRK_ID}/evidence/session-lock.yaml"
  if [[ -f "$lock_file" ]]; then
    echo "  Session lock: $(grep 'hostname\|locked_at\|session_pid' "$lock_file" | tr '\n' ' ')" >&2
  fi
  exit 1
fi
```

---

## Test Plan

**New test** `scripts/work-queue/tests/test-claim-collision.sh`:
- T1: claim-item.sh on a pending item → succeeds (baseline)
- T2: claim-item.sh on same item while already in working/ → exits 1 with collision message
- T3: start_stage.py Stage 1 → session-lock.yaml created with pid/hostname/locked_at

**Existing tests**: run `scripts/work-queue/tests/` suite after changes.

## Files Changed
- `.claude/skills/coordination/workspace/work-queue/actions/process.md` (Step 4 rewrite)
- `scripts/work-queue/start_stage.py` (session-lock write in Stage 1)
- `scripts/work-queue/claim-item.sh` (working/ pre-check guard)
- `scripts/work-queue/tests/test-claim-collision.sh` (new)
