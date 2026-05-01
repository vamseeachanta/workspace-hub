# Archived Skill: `blender-worktree-test-hardening`

Original path: `/home/vamsee/.hermes/skills/digitalmodel/blender-worktree-test-hardening`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/digitalmodel/blender-worktree-test-hardening`
Consolidation date: 2026-04-29

---

---
name: blender-worktree-test-hardening
description: Recover and harden digitalmodel Blender automation work in isolated worktrees when uv/editable dependency paths break and local machines lack a Blender executable.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Blender worktree test hardening for digitalmodel

Use this when all of the following are true:
- you are working in an isolated `digitalmodel` git worktree under `/mnt/local-analysis/worktrees/...`
- Blender automation tests fail locally
- the machine may not have `blender` on PATH
- `uv run` may fail because digitalmodel's editable `assetutilities` dependency resolves relative to `../assetutilities`

## Symptoms

1. `uv run` fails in the worktree with an editable dependency error like:
- `Failed to generate package metadata for assetutilities==0.1.0 @ editable+../assetutilities`
- `Distribution not found at: file:///mnt/local-analysis/worktrees/assetutilities`

2. Blender wrapper tests fail during fixture construction with:
- `RuntimeError: Blender not found or not accessible: [Errno 2] No such file or directory: 'blender'`

3. Interactive Claude/Codex may get distracted by package-import theories even though the real failing boundary is missing external binary availability.

## Fast recovery sequence

### A. Fix the test environment first

Preferred path for targeted test execution in a digitalmodel worktree:

```bash
PYTHONPATH=src /mnt/local-analysis/workspace-hub/digitalmodel/.venv/bin/python -m pytest tests/solvers/blender_automation/test_blender_wrapper.py -q
```

Why:
- this avoids rebuilding a fresh worktree-local `uv` environment
- it bypasses the broken `editable+../assetutilities` worktree-relative path
- it uses the already-working main-checkout virtualenv

### B. If you really need `uv run` inside the worktree

Create the missing sibling path expected by digitalmodel's editable dependency:

```bash
ln -s /mnt/local-analysis/workspace-hub/assetutilities /mnt/local-analysis/worktrees/assetutilities
```

After the session, remove the temporary symlink if you don't want to keep it:

```bash
rm -f /mnt/local-analysis/worktrees/assetutilities
```

## Real root cause triage

Before changing code, confirm whether the problem is actually:
- missing Blender executable on PATH
- not an import-path bug
- not an internal Blender automation logic bug

Run the narrow failing slice first with the exact interpreter above.

If failures all originate from wrapper construction calling `subprocess.run(["blender", "--version"])`, treat this as an availability-hardening task, not a new feature task.

## Recommended TDD pattern for external executable wrappers

### 1. Red: rewrite tests around availability-aware behavior

For unit tests:
- mock `subprocess.run`
- keep wrapper construction deterministic
- verify command assembly and error handling without needing the real binary

For integration tests:
- use a skip marker gated on real binary availability
- do not let absence of Blender fail the whole unit test slice

In the Blender automation area, create a shared `conftest.py` with:
- `mock_blender_run`
- `mock_blender_run_error`
- `requires_blender`

### 2. Green: harden the wrapper minimally

For wrapper classes like `BlenderWrapper`, prefer this behavior:
- constructor does not raise if Blender is unavailable
- store availability explicitly, e.g. `self._available`
- expose a property like `is_available`
- `run_script()` returns a structured failure dict when Blender is unavailable instead of crashing

Good pattern:
- `version = None` when unavailable
- `is_available == False`
- methods return `{success: False, error: ...}`

### 3. Broaden only after the first slice is green

Run first:

```bash
PYTHONPATH=src /mnt/local-analysis/workspace-hub/digitalmodel/.venv/bin/python -m pytest tests/solvers/blender_automation/test_blender_wrapper.py -q
```

Then run the nearby regression slice:

```bash
PYTHONPATH=src /mnt/local-analysis/workspace-hub/digitalmodel/.venv/bin/python -m pytest tests/solvers/blender_automation/ -q
```

## Interactive Claude guidance

When using tmux/interactive Claude Code for this class of problem:
- give Claude the exact test command up front
- explicitly tell it to focus on the actual failing boundary
- steer it away from import-path rabbit holes unless imports are actually failing
- keep owned paths narrow:
  - `src/digitalmodel/solvers/blender_automation/**`
  - `tests/solvers/blender_automation/**`

Useful steering sentence:
- `Focus only on the actual failing boundary. Ignore import-path theory unless an import is actually failing. Harden wrapper/tests for deterministic behavior when Blender is absent on PATH.`

## Verification checklist

Before closing the issue, verify all of:
- targeted wrapper test slice passes
- broader `tests/solvers/blender_automation/` slice passes
- changes are confined to Blender automation source/tests
- any temporary prompt file or helper symlink is cleaned up
- pushed commit actually landed on `origin/main`

## What this solved in live use

This pattern successfully closed a digitalmodel Blender configuration issue by:
- using the main-checkout `.venv` to avoid worktree `uv` dependency breakage
- converting Blender wrapper behavior from constructor-crash to availability-aware degradation
- rewriting Blender unit tests to use mocked subprocess execution plus skip-gated real-Blender integration tests
- turning a machine-specific missing-binary failure into a deterministic, portable test suite
