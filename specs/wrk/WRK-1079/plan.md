# WRK-1079 Plan: PEP 561 Type Stubs for assetutilities Public API

## Objective

Add PEP 561 inline type annotations to assetutilities contracted public API symbols to enable
mypy type checking in consumers (digitalmodel, worldenergydata) without errors.

## Contracted Symbols

- `SaveData`, `ReadData`, `Transform` — `common/data.py`
- `AttributeDict`, `update_deep_dictionary` — `common/update_deep.py`
- `WorkingWithYAML` — `common/yml_utilities.py`
- `TrackedQuantity`, `unit_checked`, `UnitMismatchError` — via pint units module
- `FileManagement` — `common/file_management.py`

## Route

Route B (Medium) — 3 phases

## Phase 1: Infrastructure + Units

- Create `assetutilities/src/assetutilities/py.typed` (PEP 561 marker)
- Update `pyproject.toml`: mypy python_version=3.9, add per-module override for data.py
- Annotate `update_deep.py` (AttributeDict, update_deep_dictionary)

## Phase 2: WorkingWithYAML + FileManagement

- Annotate `yml_utilities.py` (WorkingWithYAML + module-level functions)
- Annotate `file_management.py` (FileManagement class)

## Phase 3: data.py Contracted Classes

- Annotate `ReadData`, `SaveData`, `Transform` in `data.py`
- Use `disallow_untyped_defs = false` override to avoid annotating 50+ legacy helper classes

## Test Plan

- mypy clean pass on all 3 annotated files in assetutilities
- assetutilities unit tests: 692 pass
- Consumer verification: 0 assetutilities-related errors in digitalmodel + worldenergydata

## Acceptance Criteria

- `py.typed` marker present in assetutilities package
- All contracted public API symbols have complete type annotations
- `uv run mypy` on assetutilities passes with 0 errors
- Consumer repos show 0 new mypy errors attributable to assetutilities
