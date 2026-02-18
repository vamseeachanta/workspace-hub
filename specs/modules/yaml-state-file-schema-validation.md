# YAML State File Schema Validation

## Summary

Add Pydantic-based schema validation for the 4 YAML state files in `.claude/state/` and `.claude/work-queue/`. These files had 24 corrections in 30 days due to type mismatches, missing fields, and invalid values. Validation catches errors at write-time.

## Files to Create

```
coordination/src/coordination/schemas/
  __init__.py           # Public API: validate_file(), load_and_validate()
  __main__.py           # CLI: python -m coordination.schemas <file>
  reflect_state.py      # ReflectState model (CRITICAL — 50+ fields)
  learnings.py          # LearningEntry / LearningsFile models
  work_queue.py         # WorkQueueState model
  cc_user_insights.py   # CCUserInsights model
  _registry.py          # Filename-to-schema mapping

coordination/tests/unit/
  test_reflect_state_schema.py
  test_learnings_schema.py
  test_work_queue_schema.py
  test_cc_user_insights_schema.py
  test_schema_cli.py
  test_schema_registry.py

coordination/tests/integration/
  test_validate_real_files.py
```

## File to Modify

- `coordination/pyproject.toml` — add `pydantic>=2.0` to dependencies

## Key Design Decisions

1. **Pydantic v2 models** — modern, good error messages, `RootModel` for list-typed YAML
2. **One top-level model per YAML file** with nested sub-models for sections
3. **Lenient mode first** — `extra="allow"` so unknown fields don't break existing workflows
4. **CLI entrypoint** — `python -m coordination.schemas <file>` for shell script callers (exit 0/1)
5. **Registry pattern** — `_registry.py` maps filenames to schema classes

## Schema Models

### ReflectState (reflect-state.yaml)
- `ChecklistStatus` enum: pass | fail | warn | none
- `PhasesCompleted`: 4 booleans (reflect, abstract, generalize, store)
- `ReflectMetrics`: ~11 non-negative int fields + 1 string
- `ReflectChecklist`: ~50 fields mixing ChecklistStatus enums, ints, floats, dates
- `ActionsTaken`: 5 non-negative int fields
- `ReflectFiles`: file path strings, with `"none"` -> `None` coercion

### LearningsFile (learnings.yaml)
- `RootModel[list[LearningEntry]]` — bare list at root
- `LearningEntry.score`: `float, ge=0.0, le=1.0` with validator for bare decimals (`.304`)
- Known corruption in ~30% of entries — lenient validation on `repos` and `pattern`

### WorkQueueState (work-queue/state.yaml)
- Simple: `last_id: int`, `last_processed: Optional[int]`, `created_at: datetime`
- Nested `WorkQueueStats` with 3 non-negative ints

### CCUserInsights (cc-user-insights.yaml)
- Flat: version strings + `general: list[str]` + `specific: list[str]`

## Implementation Sequence (TDD)

1. Add `pydantic>=2.0` to `coordination/pyproject.toml`
2. Write tests for `ReflectState` → implement `reflect_state.py`
3. Write tests for `LearningsFile` → implement `learnings.py`
4. Write tests for `WorkQueueState` + `CCUserInsights` → implement both
5. Write tests for `_registry.py` → implement
6. Write tests for `__init__.py` (validate_file, load_and_validate) → implement
7. Write tests for `__main__.py` CLI → implement
8. Integration tests against real YAML files
9. Run full suite: `cd coordination && uv run pytest tests/ -v`

## CLI Interface

```bash
# Validate a file (exit 0 = valid, exit 1 = invalid)
python -m coordination.schemas .claude/state/reflect-state.yaml

# JSON output for programmatic use
python -m coordination.schemas .claude/state/reflect-state.yaml --json
# {"valid": false, "errors": [{"loc": ["checklist", "hooks_coverage"], "msg": "..."}]}
```

## Verification

1. `cd /mnt/github/workspace-hub/coordination && uv run pytest tests/unit/ -v -m unit`
2. `cd /mnt/github/workspace-hub/coordination && uv run pytest tests/integration/ -v -m integration`
3. `cd /mnt/github/workspace-hub && python -m coordination.schemas .claude/state/reflect-state.yaml`
4. `cd /mnt/github/workspace-hub && python -m coordination.schemas .claude/work-queue/state.yaml`
5. All 4 real YAML files validate without errors (or known issues flagged as warnings)
