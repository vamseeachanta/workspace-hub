# WRK-1123 Plan: Stage 1 Guard — start_stage.py

## Context

`start_stage.py` writes `session-lock.yaml` during Stage 1 before verifying the item
is in `working/`. A crashed Stage 1 session on a `pending/` item leaves an orphaned
lock that causes `whats-next.sh` to surface the item as "unclaimed active" (observed
WRK-1069, PID 347842, lock at 10:22Z).

The existing guard at line 339 only fires for `stage >= 9`. Stage 1 is unguarded.

## Route

A — Simple (inline plan, 3-5 bullets, single cross-review pass)

## Critical Files

- `scripts/work-queue/start_stage.py` — lines 339–378 (guard + Stage 1 block)
- `scripts/work-queue/tests/test_start_stage_guards.py` — new test file

## Implementation (3 steps)

### Step 1 — Stale lock purge (before guard, stdlib only)

Insert immediately before the `if stage == 1:` block (~line 350):

```python
# Auto-purge stale session-lock (PID dead + age > 2h)
_maybe_purge_stale_lock(Path(output_dir) / "evidence" / "session-lock.yaml")
```

New helper function (add near top of `main()`):

```python
def _maybe_purge_stale_lock(lock_path: Path) -> None:
    import datetime
    if not lock_path.exists():
        return
    try:
        import yaml as _yaml
        data = _yaml.safe_load(lock_path.read_text()) or {}
    except Exception:
        return
    pid = data.get("session_pid")
    locked_at_str = data.get("locked_at", "")
    # Check age > 2h
    try:
        locked_at = datetime.datetime.fromisoformat(locked_at_str.rstrip("Z"))
        age = (datetime.datetime.utcnow() - locked_at).total_seconds()
    except Exception:
        return
    if age <= 7200:
        return
    # Check PID dead
    try:
        os.kill(int(pid), 0)
        return  # process still alive
    except (ProcessLookupError, PermissionError, TypeError, ValueError):
        pass
    lock_path.unlink(missing_ok=True)
    print(f"  Auto-purged stale session-lock for PID {pid} (age {age/3600:.1f}h).",
          file=sys.stderr)
```

### Step 2 — Stage 1 working/ guard

Insert immediately after the stale-lock purge, before the lock write (~line 350):

```python
# Stage 1 guard: item must be in working/ before session-lock is written
if stage == 1:
    working_path = Path(queue_dir) / "working" / f"{wrk_id}.md"
    if not working_path.exists():
        print(
            f"✖ {wrk_id} is not in working/ — claim it before starting stage 1:\n"
            f"  bash scripts/work-queue/claim-item.sh {wrk_id}",
            file=sys.stderr,
        )
        sys.exit(1)
```

### Step 3 — Unit test

New file `scripts/work-queue/tests/test_start_stage_guards.py`:

```python
"""
test_stage1_guard_blocks_pending — WRK-1123 AC verification.

Directly imports and calls _stage1_working_guard() to test the guard logic
without spinning up the full start_stage.main() harness.
"""
import pathlib, tempfile, pytest, sys, os
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

# We'll extract the guard logic into a helper so it's testable in isolation.
# The helper is _stage1_working_guard(wrk_id, queue_dir) -> None (or sys.exit(1)).
from start_stage import _stage1_working_guard  # added in Step 2 as importable fn

def test_stage1_guard_blocks_pending(tmp_path):
    """Stage 1 on pending item exits 1."""
    queue = tmp_path / "work-queue"
    (queue / "pending").mkdir(parents=True)
    (queue / "working").mkdir()
    (queue / "pending" / "WRK-999.md").write_text("id: WRK-999\n")
    with pytest.raises(SystemExit) as exc_info:
        _stage1_working_guard("WRK-999", str(queue))
    assert exc_info.value.code == 1

def test_stage1_guard_passes_working(tmp_path):
    """Stage 1 on working item does not exit."""
    queue = tmp_path / "work-queue"
    (queue / "working").mkdir(parents=True)
    (queue / "working" / "WRK-999.md").write_text("id: WRK-999\n")
    _stage1_working_guard("WRK-999", str(queue))  # must not raise
```

Note: `_stage1_working_guard` needs to be extracted from the inline `if stage == 1:`
block into a named function in `start_stage.py` so the test can import it.

## Verification

```bash
# Run new tests
uv run --no-project python -m pytest scripts/work-queue/tests/test_start_stage_guards.py -v

# Smoke test: stage 1 on pending item should exit 1
uv run --no-project python scripts/work-queue/start_stage.py WRK-999 1 2>&1
# Expected: "✖ WRK-999 is not in working/ — claim it before starting stage 1"

# Regression: stage 1 on a working item should proceed
# (requires a real WRK in working/ — use WRK-1123 after claim)
```
