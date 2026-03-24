# WRK-6670 Notes — /whats-next Fine-tuning

## Note 1 — Stale items in "Top High-Priority Ready" list (2026-03-24)

**Observation:** 3 of 6 items in the high-priority ready list don't belong:

| WRK | Title | Problem |
|-----|-------|---------|
| WRK-1360 | 3D CAD geometry (FreeCAD) | Already in `done/` |
| WRK-1362 | Chute drag force | Already in `done/` |
| WRK-1269 | POC v2 — XLSX-to-Python | `status: closed`, `close_reason: completed-negative-finding` — still in `pending/` dir |
| WRK-1386 | Trim child repo CLAUDE.md | Already in `done/` |

Also: WRK-1341 title mismatch — list shows "CalculiX beam/frame element support" but file says "Slim down large repos".

Only **WRK-1341** and **WRK-1376** genuinely belong.

## Root Cause — `rebuild-wrk-index.sh` doesn't scan `done/` directory

**File:** `scripts/work-queue/rebuild-wrk-index.sh`, line 12

```bash
for dir in "pending" "working" "blocked"; do
```

The rebuild script scans `pending/`, `working/`, `blocked/`, and `archive/` — but **skips `done/`**. Consequences:

1. **Items moved to `done/` after last index rebuild retain their old status** (pending/working) in `wrk-status-index.json`
2. **`whats-next.sh` line 111 correctly filters `status == "done"`** — but the index never marks them as "done", so the filter never fires
3. **Closed items still in `pending/` dir** (like WRK-1269 with `status: closed`) are indexed with their frontmatter status, but `whats-next.sh` only filters `archived` and `done` — not `closed`

## Fix Required (two-part)

1. **`rebuild-wrk-index.sh` line 12** — Add `"done"` to the dir scan loop:
   ```bash
   for dir in "pending" "working" "blocked" "done"; do
   ```
2. **`whats-next.sh` line 111** — Add `"closed"` to the exclusion filter:
   ```python
   if status in ("archived", "done", "closed"):
   ```

## Secondary Issue

WRK-1269 has `status: closed` but still lives in `pending/` directory — it should have been moved to `done/` or `archive/` when closed. This suggests the close workflow doesn't always move files.

### Note 2 — No machine filtering in whats-next.sh (2026-03-24)

**Observation:** `whats-next.sh` captures `THIS_HOST=$(hostname -s)` (line 8) and passes it to Python as `this_host` (line 45), but **never uses it for filtering**. The `computer` field is display-only — every machine sees the entire queue.

**Expected behavior:** Default should show only items assigned to the current machine. Flags for broader views:
- `--machine <name>` — show items for a specific machine
- `--all-machines` — show items across all machines

**Fix location:** `whats-next.sh` Python block, around line 109-120 — add host filter before classification loop, with flag passthrough from bash arg parsing.

### Note 3 — Index lacks execution machine; display doesn't show machine (2026-03-24)

**Observation:** The index has two machine-related fields:
- `machine` (line 86 in `update-wrk-index.sh`) — the host that last updated the index entry (operational metadata, not meaningful)
- `computer` (line 101) — from WRK frontmatter, the *assigned* machine

Neither tracks which machine actually **executed** the work. Also, `whats-next.sh` output doesn't display the machine column by default — it's carried through classification but the user can't see at a glance which machine owns each item.

**Expected behavior:**
1. Index should include `execution_machine` — set when work execution actually starts (stage 10 / dispatch-run.sh), distinct from `computer` (planning assignment)
2. `whats-next.sh` should display the `computer` column by default in all sections so the user can see resource allocation at a glance

**Fix locations:**
- `update-wrk-index.sh` — read `execution_workstations` from frontmatter into index
- `dispatch-run.sh` or `start_stage.py` — stamp `execution_machine: $(hostname -s)` when execution begins
- `whats-next.sh` — include machine in default output columns

### Note 4 — GitHub Issues as single source of truth (2026-03-24)

**Observation:** The current architecture has local WRK markdown files as source of truth, with GH issues as a mirror. This causes:
- Stale index (Notes 1-3) because local files drift from actual state
- Duplicate bookkeeping — status, priority, machine, category all maintained in two places
- No enforcement of required fields — easy to create incomplete WRK items locally

**Proposed direction:** Flip the flow. Make **GitHub Issues the single source of truth**:
- Required fields enforced via GH issue templates / project board custom fields (status, priority, machine, category, complexity)
- Labels for routing (route-A/B/C), status (pending/working/done/blocked), machine assignment
- Local WRK files become **cached views** pulled from GH, not the authoritative copy
- `whats-next.sh` queries GH API (or a locally synced snapshot) instead of scanning markdown frontmatter
- Creation: `gh issue create` with template → triggers local cache sync
- Updates: GH project board moves → webhook or poll updates local cache

**Benefits:**
- Single source eliminates index staleness entirely
- Required fields on issue templates prevent incomplete items
- Machine assignment via GH labels or project fields — filterable in GH UI too
- PR linking, cross-references, and timeline come free
- Multiple machines see consistent state without rebuild scripts

**Migration path:** Incremental — start by making GH authoritative for status/priority/machine, keep local files for spec/notes/evidence that don't belong in GH.

## Tasks

- [ ] **Task 1**: `rebuild-wrk-index.sh` line 12 — add `"done"` to dir scan loop (`for dir in "pending" "working" "blocked" "done"`)
- [ ] **Task 2**: `whats-next.sh` line 111 — add `"closed"` to exclusion filter (`if status in ("archived", "done", "closed")`)
- [ ] **Task 3**: Move WRK-1269 from `pending/` to `done/` or `archive/` (it has `status: closed`)
- [ ] **Task 4**: Audit `pending/` for other items with `status: closed` or `status: done` that were never relocated
- [ ] **Task 5**: Investigate WRK-1341 title mismatch — `/whats-next` shows "CalculiX beam/frame element support" but file says "Slim down large repos". Check if index has stale title or if there's a collision
- [ ] **Task 6**: Rebuild index (`rebuild-wrk-index.sh`) after fixes and verify `/whats-next` output is clean
- [ ] **Task 7**: Review close/archive workflow scripts to ensure they always move files out of `pending/`
- [ ] **Task 8**: `whats-next.sh` — default to showing only items where `computer` matches `$(hostname -s)`. Add `--machine <name>` flag for a specific machine and `--all-machines` flag to show everything. Update both bash arg parsing (line 16-26) and Python filter logic (around line 109).
- [ ] **Task 9**: `update-wrk-index.sh` — read `execution_workstations` from WRK frontmatter into index (alongside existing `computer` field)
- [ ] **Task 10**: `dispatch-run.sh` or `start_stage.py` — stamp `execution_machine: $(hostname -s)` on the WRK frontmatter when execution actually begins
- [ ] **Task 11**: `whats-next.sh` — display machine (`computer`) column by default in all output sections so resource allocation is visible at a glance
- [ ] **Task 12**: Retire WRK-NNN numbering — adopt GH issue numbers as the sole ID going forward. All new items use `#NNN` (GH issue number). Existing WRK-NNN items keep their IDs but no new WRK IDs are minted. Update: `gh-next-id.sh` (retire), `reserved-wrk-ids.txt` (freeze), file naming (`WRK-*.md` → `#NNN.md` or `GH-NNN.md`), all scripts that parse `WRK-\d+`, commit message convention (`feat(WRK-NNN)` → `feat(#NNN)`), and skill docs referencing WRK format.
- [ ] **Task 13**: Design GH issue template with required fields: status, priority, machine, category, subcategory, complexity, route
- [ ] **Task 13**: Set up GH project board custom fields (or labels) for machine assignment and execution tracking
- [ ] **Task 14**: Write `gh-sync-down.sh` — pull GH issue metadata → update local WRK frontmatter + rebuild index (GH → repo direction)
- [ ] **Task 15**: Refactor `whats-next.sh` to query GH API (with local cache fallback) instead of scanning local markdown
- [ ] **Task 16**: Refactor `/work add` to create GH issue first (`gh issue create --template`), then generate local WRK file from GH response
- [ ] **Task 17**: Deprecate `rebuild-wrk-index.sh` in favor of GH-sourced index — keep as fallback only
- [ ] **Task 18**: Audit all scripts, skills, hooks, and docs that reference `WRK-\d+` pattern — update to support GH `#NNN` format or both during transition
- [ ] **Task 19**: Renumber local pending/unstarted WRK items to match their GH issue numbers — rename files (`WRK-1269.md` → `WRK-15.md` etc.), update `id:` frontmatter, update cross-references (`related`, `blocked_by`, `parent`, `children`) in all WRK files, and update assets directories. Script this — too many items for manual rename.
- [ ] **Task 20**: Cross-review pass 1 — run `/whats-next --all` after fixes, compare full output against GH issues list (`gh issue list`). GH is the single source of truth — any local item not matching GH state is wrong. Flag stale items, missing items, wrong metadata.
- [ ] **Task 21**: Cross-review pass 2 — independent review by a second agent (Codex or Gemini) of the `/whats-next` pipeline end-to-end: index build → filtering → display. Verify GH → local sync is faithful. Catch anything missed in pass 1.
