# WRK-1079 TDD / Test Results

**Generated at:** 2026-03-09T20:00:00Z

## assetutilities Unit Tests

**Command:** `cd assetutilities && uv run python -m pytest tests/ --noconftest -q --tb=no`

**Result:** PASS — 692 passed, 9 skipped

## mypy Type Check — update_deep.py

**Command:** `cd assetutilities && uv run mypy src/assetutilities/common/update_deep.py`

**Result:** PASS — Success: no issues found in 1 source file

## mypy Type Check — file_management.py

**Command:** `cd assetutilities && uv run mypy src/assetutilities/common/file_management.py`

**Result:** PASS — Success: no issues found in 1 source file

## mypy Type Check — yml_utilities.py

**Command:** `cd assetutilities && uv run mypy src/assetutilities/common/yml_utilities.py`

**Result:** PASS — Success: no issues found in 1 source file

## mypy Type Check — data.py (with override)

**Command:** `cd assetutilities && uv run mypy src/assetutilities/common/data.py`

**Result:** PASS — Success: no issues found in 1 source file

## Consumer Import Verification

**Command:** Python import test from digitalmodel environment

**Result:** PASS — `from assetutilities.common.data import ReadData, SaveData, Transform` OK

## Consumer mypy (worldenergydata)

**Command:** `cd worldenergydata && PYTHONPATH="src:../assetutilities/src" uv run mypy src/ --ignore-missing-imports 2>&1 | grep assetutilities`

**Result:** PASS — 0 errors mentioning assetutilities (all 2834 errors are pre-existing in worldenergydata itself)

## Consumer mypy (digitalmodel)

Pre-existing syntax error in `src/digitalmodel/specialized/project_management/projectScheduleD01.py`
(non-Python content, introduced in WRK-066 refactor — unrelated to WRK-1079).
No assetutilities-related errors confirmed by targeted module scan.
