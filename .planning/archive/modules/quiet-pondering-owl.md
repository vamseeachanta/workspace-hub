# WRK-1169: Fix WRK Lifecycle Discipline

## Context

Audit of 22 WRK items and all stage scripts revealed 9 enforcement gaps. The most user-visible bug: HTML stage chips show the wrong active stage (e.g., stage 4 active while CLI is at stage 5) because `stage-evidence.yaml` is never updated by the stage scripts during normal lifecycle execution. The HTML generator either uses stale evidence or heuristic artifact detection.

Three architectural issues compound:
1. `exit_stage.py` regenerates HTML **before** updating stage state
2. Neither `start_stage.py` nor `exit_stage.py` calls `update-stage-evidence.py`
3. `start_stage.py` requires `working/` for Stage 1 but Stage 1's exit artifact is `pending/`

## Plan — 4 Changes

### Change 1: Wire `update-stage-evidence.py` into `exit_stage.py`

**File:** `scripts/work-queue/exit_stage.py` — `_main()` function (line ~329)

After `validate_exit()` succeeds (line 323) and **before** `_regenerate_lifecycle_html()` (line 330):

```python
# Update stage-evidence.yaml: mark current stage as done
_update_stage_ev(wrk_id, stage, "done", repo_root)

# THEN regenerate HTML (now reads correct stage state)
_regenerate_lifecycle_html(wrk_id, repo_root)
```

New helper `_update_stage_ev()` calls `update-stage-evidence.py` via subprocess:
```python
def _update_stage_ev(wrk_id, stage, status, repo_root):
    script = os.path.join(repo_root, "scripts", "work-queue", "update-stage-evidence.py")
    if not os.path.exists(script):
        return
    subprocess.run(
        ["uv", "run", "--no-project", "python", script, wrk_id,
         "--order", str(stage), "--status", status],
        capture_output=True, text=True, cwd=repo_root,
    )
```

### Change 2: Wire `update-stage-evidence.py` into `start_stage.py`

**File:** `scripts/work-queue/start_stage.py` — `_main()` function

After the stage guard checks (line ~506) and **before** HTML regeneration:

```python
# Mark current stage as in_progress in stage-evidence
_update_stage_ev(wrk_id, stage, "in_progress", repo_root)
```

Same helper pattern as exit_stage.py.

### Change 3: Fix Stage 1 working/ guard

**File:** `scripts/work-queue/start_stage.py` — lines 501-506

Change the guard logic so Stage 1 checks for the item in **either** `pending/` or `working/`:

```python
if stage == 1:
    _maybe_purge_stale_lock(...)
    _stage1_pending_or_working_guard(wrk_id, queue_dir)  # accepts both
elif stage >= 9:
    _stage1_working_guard(wrk_id, queue_dir)  # working/ only
```

New function:
```python
def _stage1_pending_or_working_guard(wrk_id, queue_dir):
    working = Path(queue_dir) / "working" / f"{wrk_id}.md"
    pending = Path(queue_dir) / "pending" / f"{wrk_id}.md"
    if not working.exists() and not pending.exists():
        print(f"✖ {wrk_id} not found in pending/ or working/", file=sys.stderr)
        sys.exit(1)
```

### Change 4: Add stage-progression guard to `start_stage.py`

**File:** `scripts/work-queue/start_stage.py` — add after stage guard checks

Prevents skipping stages (the WRK-1151/1159/1155 issue):

```python
def _stage_progression_guard(wrk_id, stage, repo_root):
    """Verify previous stage evidence exists before allowing entry."""
    if stage <= 1:
        return  # Stage 1 has no prerequisite
    prev_stage = stage - 1
    # Skip stage 18 (reclaim) — it's conditional
    if prev_stage == 18:
        prev_stage = 17
    script = os.path.join(repo_root, "scripts", "work-queue", "update-stage-evidence.py")
    # Read stage-evidence.yaml and check prev stage is done
    assets_dir = Path(repo_root) / ".claude" / "work-queue" / "assets" / wrk_id
    ev_path = assets_dir / "evidence" / "stage-evidence.yaml"
    if not ev_path.exists():
        return  # No evidence file yet — allow (backcompat)
    import yaml
    data = yaml.safe_load(ev_path.read_text()) or {}
    for entry in data.get("stages", []):
        order = entry.get("order", entry.get("stage"))
        if order == prev_stage:
            status = str(entry.get("status", "")).lower()
            if status not in ("done", "n/a"):
                print(f"⚠ Stage {prev_stage} is '{status}' — complete it before stage {stage}", file=sys.stderr)
                sys.exit(1)
            return
```

Call it after the working/ guard:
```python
_stage_progression_guard(wrk_id, stage, repo_root)
```

## Files Modified

| File | Change |
|------|--------|
| `scripts/work-queue/exit_stage.py` | Add `_update_stage_ev()`, call before HTML regen |
| `scripts/work-queue/start_stage.py` | Add `_update_stage_ev()`, `_stage1_pending_or_working_guard()`, `_stage_progression_guard()` |

## NOT In Scope (Future Work)

- Pre-check script wiring (stages 7, 17) — separate WRK
- Route-conditional artifact checks in exit_stage.py — separate WRK
- Stage 14 .yaml/.json mismatch — separate WRK
- Stage 10 test count blocking promotion — separate WRK

## Verification

1. Run `uv run --no-project python scripts/work-queue/start_stage.py WRK-1169 3` — should work with item in working/
2. Create a test WRK in pending/, run start_stage.py stage 1 — should succeed (not require working/)
3. Run exit_stage.py for a stage — verify stage-evidence.yaml is updated BEFORE HTML is generated
4. Open lifecycle HTML — verify active stage chip matches the actual current stage
5. Try to start stage 5 without completing stage 4 — should be blocked by progression guard
6. Run existing tests: `uv run --no-project python -m pytest scripts/work-queue/tests/ --noconftest -q`
