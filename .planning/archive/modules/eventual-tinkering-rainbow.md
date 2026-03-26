# WRK-5113: Update Paths and Remove Old Skills — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the two-tier folder-skill migration by updating orchestration scripts to use new contract paths, removing old skill trees, and verifying end-to-end lifecycle works.

**Architecture:** Three phases — (1) update contract resolution in Python scripts from `scripts/work-queue/stages/` to `.claude/skills/workspace-hub/stages/stage-NN-*/contract.yaml`, (2) remove old skill trees and bare files, (3) update cross-references and verify.

**Tech Stack:** Python, Bash, YAML

---

## Context

WRK-1321 restructured the work-queue from 3 overlapping skill trees into a two-tier folder-skill architecture. Children WRK-5110 (orchestrator), WRK-5111 (20 stage folder-skills), and WRK-5112 (script redistribution) are complete. The new structure is in place but:
- Scripts still resolve stage contracts from `scripts/work-queue/stages/stage-NN-*.yaml` (the old flat location)
- Identical contract copies now live at `.claude/skills/workspace-hub/stages/stage-NN-*/contract.yaml`
- Old skill trees remain: `coordination/workspace/work-queue/` (20 sub-skills), `workflow-gatepass/` (9 sub-skills + SKILL.md), `work-queue-workflow/` (SKILL.md)
- 20 bare `stage-NN-name.md` files remain alongside their folder-skill replacements

## File Structure

### Files to Modify
- `scripts/work-queue/exit_stage.py` — contract glob path (line ~435)
- `scripts/work-queue/verify_checklist.py` — stages_dir references (lines ~147, ~160, ~165)
- `scripts/work-queue/generate_transition_table.py` — comment + contract glob (line ~133)
- `scripts/work-queue/tests/test-wrk1131-process-integration.sh` — hardcoded contract paths (lines ~20, ~36, ~51)
- `tests/work-queue/test_plan_mode_annotation.py` — STAGES_DIR constant (line ~5)
- `tests/work-queue/test_engine_integration.sh` — contract copy paths (lines ~70-71, ~259)
- `.claude/skills/workspace-hub/INDEX.md` — remove workflow-gatepass + work-queue-workflow entries
- 9 SKILL.md files — update `related_skills` referencing `workflow-gatepass`

### Files/Directories to Delete
- `scripts/work-queue/stages/` — 20 old contract YAMLs (now in folder-skills)
- `.claude/skills/workspace-hub/stages/stage-*.md` — 20 bare stage files
- `.claude/skills/workspace-hub/workflow-gatepass/` — entire directory (9 sub-skills + SKILL.md)
- `.claude/skills/workspace-hub/work-queue-workflow/` — entire directory (SKILL.md)
- `.claude/skills/coordination/workspace/work-queue/` sub-skill directories (17 dirs, keep SKILL.md + templates/)

### No Changes Needed
- `scripts/work-queue/dispatch-run.sh` — does NOT reference contract paths (only checkpoint.yaml + group runners)
- `scripts/work-queue/verify-gate-evidence.py` — does NOT reference contract paths (reads WRK frontmatter)

---

### Task 1: Create contract path resolver utility

**Files:**
- Create: `scripts/work-queue/resolve_contract.py`
- Test: `tests/work-queue/test_resolve_contract.py`

Centralizes contract path resolution so all scripts use one function. Looks in folder-skill location first, falls back to old location (for transition safety).

- [ ] **Step 1: Write the failing test**

```python
# tests/work-queue/test_resolve_contract.py
"""Tests for contract path resolver."""
import os
import tempfile
from pathlib import Path

import pytest


def test_resolve_finds_folder_skill_contract(tmp_path):
    """Contract found in folder-skill location."""
    from resolve_contract import resolve_contract_path

    # Create folder-skill structure
    stage_dir = tmp_path / ".claude/skills/workspace-hub/stages/stage-01-capture"
    stage_dir.mkdir(parents=True)
    (stage_dir / "contract.yaml").write_text("name: Capture\n")

    result = resolve_contract_path(1, str(tmp_path))
    assert result is not None
    assert result.endswith("contract.yaml")
    assert "stage-01-capture" in result


def test_resolve_falls_back_to_old_location(tmp_path):
    """Falls back to scripts/work-queue/stages/ if folder-skill missing."""
    from resolve_contract import resolve_contract_path

    old_dir = tmp_path / "scripts/work-queue/stages"
    old_dir.mkdir(parents=True)
    (old_dir / "stage-01-capture.yaml").write_text("name: Capture\n")

    result = resolve_contract_path(1, str(tmp_path))
    assert result is not None
    assert "scripts/work-queue/stages" in result


def test_resolve_returns_none_when_missing(tmp_path):
    """Returns None when no contract found anywhere."""
    from resolve_contract import resolve_contract_path

    result = resolve_contract_path(99, str(tmp_path))
    assert result is None


def test_resolve_stages_dir():
    """resolve_stages_dir returns folder-skill stages path."""
    from resolve_contract import resolve_stages_dir

    result = resolve_stages_dir("/fake/repo")
    assert result == "/fake/repo/.claude/skills/workspace-hub/stages"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /mnt/local-analysis/workspace-hub && uv run --no-project pytest tests/work-queue/test_resolve_contract.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/work-queue/resolve_contract.py
"""Contract path resolver for stage contracts.

Resolves stage contract YAML from folder-skill locations
(.claude/skills/workspace-hub/stages/stage-NN-*/contract.yaml),
with fallback to legacy flat location (scripts/work-queue/stages/).
"""
import glob
import os


def resolve_contract_path(stage: int, repo_root: str) -> str | None:
    """Find the contract YAML for a given stage number.

    Checks folder-skill location first, then legacy flat location.
    Returns absolute path or None.
    """
    # Primary: folder-skill location
    pattern = os.path.join(
        repo_root, ".claude", "skills", "workspace-hub", "stages",
        f"stage-{stage:02d}-*", "contract.yaml",
    )
    matches = glob.glob(pattern)
    if matches:
        return matches[0]

    # Fallback: legacy flat location
    pattern = os.path.join(
        repo_root, "scripts", "work-queue", "stages",
        f"stage-{stage:02d}-*.yaml",
    )
    matches = glob.glob(pattern)
    if matches:
        return matches[0]

    return None


def resolve_stages_dir(repo_root: str) -> str:
    """Return the canonical stages directory (folder-skill location)."""
    return os.path.join(repo_root, ".claude", "skills", "workspace-hub", "stages")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /mnt/local-analysis/workspace-hub && PYTHONPATH=scripts/work-queue:$PYTHONPATH uv run --no-project pytest tests/work-queue/test_resolve_contract.py -v`
Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/work-queue/resolve_contract.py tests/work-queue/test_resolve_contract.py
git commit -m "feat(WRK-5113): add contract path resolver for folder-skill locations"
```

---

### Task 2: Update exit_stage.py to use new contract paths

**Files:**
- Modify: `scripts/work-queue/exit_stage.py:428-437`

- [ ] **Step 1: Update contract resolution in _main()**

Replace the contract glob block (lines ~433-437):

```python
# OLD:
import glob as _glob
contract_glob = os.path.join(
    repo_root, "scripts", "work-queue", "stages", f"stage-{stage:02d}-*.yaml"
)
matches = _glob.glob(contract_glob)

# NEW:
from resolve_contract import resolve_contract_path as _resolve
_contract = _resolve(stage, repo_root)
if not _contract:
    print(f"No contract found for stage {stage}", file=sys.stderr)
    sys.exit(1)
matches = [_contract]
```

Remove the `import glob as _glob` at line ~433 (it IS also used at line ~159 for archive search — that usage must keep working; check if it's imported elsewhere).

- [ ] **Step 2: Run existing tests**

Run: `cd /mnt/local-analysis/workspace-hub && uv run --no-project pytest tests/work-queue/ -v -k "exit" 2>&1 | head -40`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add scripts/work-queue/exit_stage.py
git commit -m "feat(WRK-5113): update exit_stage.py to resolve contracts from folder-skills"
```

---

### Task 3: Update verify_checklist.py to use new contract paths

**Files:**
- Modify: `scripts/work-queue/verify_checklist.py:99-168`

- [ ] **Step 1: Update stages_dir and glob patterns**

In `summary_all_stages()` (line ~108), update the glob pattern:

```python
# OLD: matches = sorted(glob.glob(os.path.join(stages_dir, "stage-*-*.yaml")))
# NEW: matches = sorted(glob.glob(os.path.join(stages_dir, "stage-*", "contract.yaml")))
```

Update regex parsing to extract from directory name:

```python
# OLD:
basename = os.path.basename(stage_yaml_path)
m = re.match(r"stage-(\d+)-(.+)\.yaml", basename)

# NEW:
parent_dir = os.path.basename(os.path.dirname(stage_yaml_path))
m = re.match(r"stage-(\d+)-(.+)", parent_dir)
```

In `__main__` block, update `stages_dir` references (lines ~147, ~160):

```python
# OLD: stages_dir = os.path.join(repo_root, "scripts", "work-queue", "stages")
# NEW:
from resolve_contract import resolve_stages_dir
stages_dir = resolve_stages_dir(repo_root)
```

Update single-stage glob (line ~165):

```python
# OLD: matches = glob.glob(os.path.join(stages_dir, f"stage-{args.stage:02d}-*.yaml"))
# NEW: matches = glob.glob(os.path.join(stages_dir, f"stage-{args.stage:02d}-*", "contract.yaml"))
```

- [ ] **Step 2: Verify with --summary on real WRK**

Run: `cd /mnt/local-analysis/workspace-hub && PYTHONPATH=scripts/work-queue:$PYTHONPATH uv run --no-project python scripts/work-queue/verify_checklist.py --summary WRK-5112`
Expected: 20 stage lines

- [ ] **Step 3: Commit**

```bash
git add scripts/work-queue/verify_checklist.py
git commit -m "feat(WRK-5113): update verify_checklist.py to folder-skill contract paths"
```

---

### Task 4: Update remaining scripts and tests

**Files:**
- Modify: `scripts/work-queue/generate_transition_table.py:~133`
- Modify: `scripts/work-queue/tests/test-wrk1131-process-integration.sh:20,36,51`
- Modify: `tests/work-queue/test_plan_mode_annotation.py:5`
- Modify: `tests/work-queue/test_engine_integration.sh:70-71,259`

- [ ] **Step 1: Update generate_transition_table.py**

Update the source comment and any contract globs to reference `.claude/skills/workspace-hub/stages/`.

- [ ] **Step 2: Update test-wrk1131-process-integration.sh**

```bash
# OLD: ROUTING_YAML="$REPO_ROOT/scripts/work-queue/stages/stage-09-routing.yaml"
# NEW: ROUTING_YAML="$REPO_ROOT/.claude/skills/workspace-hub/stages/stage-09-routing/contract.yaml"
# (same pattern for lines 36 and 51)
```

- [ ] **Step 3: Update test_plan_mode_annotation.py**

```python
# OLD: STAGES_DIR = Path("scripts/work-queue/stages")
# NEW: STAGES_DIR = Path(".claude/skills/workspace-hub/stages")
```

- [ ] **Step 4: Update test_engine_integration.sh**

Update contract copy paths and `load_stage_contracts` reference.

- [ ] **Step 5: Run all work-queue tests**

Run: `cd /mnt/local-analysis/workspace-hub && uv run --no-project pytest tests/work-queue/ -v 2>&1 | tail -30`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/work-queue/generate_transition_table.py \
  scripts/work-queue/tests/test-wrk1131-process-integration.sh \
  tests/work-queue/test_plan_mode_annotation.py \
  tests/work-queue/test_engine_integration.sh
git commit -m "feat(WRK-5113): update remaining scripts/tests to folder-skill paths"
```

---

### Task 5: Remove old contract directory and bare stage files

**Files:**
- Delete: `scripts/work-queue/stages/` (20 YAML files)
- Delete: `.claude/skills/workspace-hub/stages/stage-*.md` (20 bare files)

- [ ] **Step 1: Verify no remaining references to old paths**

```bash
grep -rn "scripts/work-queue/stages" --include="*.py" --include="*.sh" | grep -v "done/" | grep -v "specs/" | grep -v "archive/"
```
Expected: No hits

- [ ] **Step 2: Remove old contract directory**

```bash
rm -rf scripts/work-queue/stages/
```

- [ ] **Step 3: Remove bare stage md files**

```bash
find .claude/skills/workspace-hub/stages/ -maxdepth 1 -name "stage-*.md" -delete
```

- [ ] **Step 4: Verify folder-skill contracts intact**

```bash
ls .claude/skills/workspace-hub/stages/stage-*/contract.yaml | wc -l
# Expected: 20
```

- [ ] **Step 5: Commit**

```bash
git add -A scripts/work-queue/stages/ .claude/skills/workspace-hub/stages/
git commit -m "feat(WRK-5113): remove old contract directory and bare stage files"
```

---

### Task 6: Remove old skill trees

**Files:**
- Delete: `.claude/skills/workspace-hub/workflow-gatepass/` (entire dir)
- Delete: `.claude/skills/workspace-hub/work-queue-workflow/` (entire dir)
- Delete: 17 sub-skill dirs in `.claude/skills/coordination/workspace/work-queue/` (keep SKILL.md + templates/)

- [ ] **Step 1: Remove workflow-gatepass and work-queue-workflow**

```bash
rm -rf .claude/skills/workspace-hub/workflow-gatepass/
rm -rf .claude/skills/workspace-hub/work-queue-workflow/
```

- [ ] **Step 2: Remove coordination/work-queue sub-skills (keep SKILL.md + templates/)**

```bash
cd .claude/skills/coordination/workspace/work-queue/
rm -rf archival-safety canonical-20-stage-lifecycle checkpoint-resume \
  command-interface complexity-routing cross-review-route-bc \
  feature-layer-epic-level-work integration-points key-scripts \
  machine-wrk-id-ranges parallel-work-policy planning-requirement \
  queue-directory-structure scope-discipline stage-contracts-summary \
  work-execution-principle-scripts-over-llm-overhead work-item-format \
  actions
```

- [ ] **Step 3: Commit**

```bash
git add -A .claude/skills/workspace-hub/workflow-gatepass/ \
  .claude/skills/workspace-hub/work-queue-workflow/ \
  .claude/skills/coordination/workspace/work-queue/
git commit -m "feat(WRK-5113): remove old overlapping skill trees"
```

---

### Task 7: Update cross-references

**Files:**
- Modify: `.claude/skills/workspace-hub/INDEX.md`
- Modify: 9 SKILL.md files with `workflow-gatepass` or `work-queue-workflow` in related_skills

- [ ] **Step 1: Update INDEX.md**

Remove entries for `work-queue-workflow` and `workflow-gatepass`. Add `work-queue-orchestrator` if missing.

- [ ] **Step 2: Update related_skills in SKILL.md files**

Replace `workflow-gatepass` → `work-queue-orchestrator` in:
- `.claude/skills/workspace-hub/session-start/SKILL.md`
- `.claude/skills/workspace-hub/session-end/SKILL.md`
- `.claude/skills/workspace-hub/work-document-exit/SKILL.md`
- `.claude/skills/workspace-hub/work-queue-orchestrator/SKILL.md`
- `.claude/skills/workspace-hub/wrk-lifecycle-testpack/SKILL.md`
- `.claude/skills/workspace-hub/checkpoint/SKILL.md`
- `.claude/skills/workspace-hub/plan-mode/SKILL.md`
- `.claude/skills/workspace-hub/stages/stage-09-routing/SKILL.md`
- `.claude/skills/coordination/workspace/work-queue/SKILL.md`

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/
git commit -m "feat(WRK-5113): update cross-references to removed skill trees"
```

---

### Task 8: End-to-end verification

- [ ] **Step 1: Run all work-queue tests**

```bash
uv run --no-project pytest tests/work-queue/ -v
```
Expected: All PASS

- [ ] **Step 2: Test dispatch-run.sh**

```bash
bash scripts/work-queue/dispatch-run.sh WRK-5113
```
Expected: Stage/group/runner shown without errors

- [ ] **Step 3: Verify all 20 contracts resolve**

```bash
for i in $(seq 1 20); do
  PYTHONPATH=scripts/work-queue:$PYTHONPATH uv run --no-project python -c \
    "from resolve_contract import resolve_contract_path; p = resolve_contract_path($i, '.'); assert p, f'Stage $i missing'; print(f'Stage {$i:02d}: OK')"
done
```

- [ ] **Step 4: Verify no dangling references**

```bash
grep -rn "workflow-gatepass" .claude/skills/ --include="*.md" --include="*.yaml" | grep -v "done/" | grep -v "archive/"
grep -rn "work-queue-workflow" .claude/skills/ --include="*.md" --include="*.yaml" | grep -v "done/" | grep -v "archive/"
grep -rn "scripts/work-queue/stages" --include="*.py" --include="*.sh" | grep -v "done/" | grep -v "specs/"
```
Expected: No hits
