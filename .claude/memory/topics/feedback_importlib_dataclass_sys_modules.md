> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-19
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_importlib_dataclass_sys_modules.md

---
name: importlib-dataclass-sys-modules
description: kebab-case Python scripts loaded via spec_from_file_location must register in sys.modules BEFORE exec_module if they contain @dataclass — otherwise dataclass machinery raises AttributeError on cls.__module__.__dict__ lookup
metadata: 
  node_type: memory
  type: feedback
  originSessionId: dda679b1-6aba-45a0-8665-9e2fdb62d530
---

When loading a kebab-case Python script (e.g., `scripts/ai/approve-provider-plan.py`) into a test using `importlib.util.spec_from_file_location("snake_name", path)`, register the module in `sys.modules` BEFORE calling `spec.loader.exec_module(module)`:

```python
spec = importlib.util.spec_from_file_location("approve_provider_plan", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules["approve_provider_plan"] = module  # ← REQUIRED before exec
spec.loader.exec_module(module)
```

**Why:** Python's `@dataclass` decorator calls `_is_type(cls, ...)` internally which reads `sys.modules.get(cls.__module__).__dict__`. If the module isn't in `sys.modules` at decoration time, that returns `None` and the dataclass setup raises:

```
AttributeError: 'NoneType' object has no attribute '__dict__'
```

This only happens with modules loaded via `spec_from_file_location` that contain dataclasses. Normal `import x` registers the module automatically; the file-based loader does not.

**How to apply:**

- Apply whenever you write tests for a kebab-case Python script that contains `@dataclass` (or any decorator that introspects `cls.__module__`).
- The `sys.modules` key MUST match `spec.name`. Mismatches will fail silently with the same error.
- This pattern is now used in workspace-hub at:
  - `tests/ai/test_approve_provider_plan.py:19`
  - `tests/ai/test_provider_kanban.py:18`
  - `tests/ai/test_provider_kanban_server.py:21`
  - `tests/ai/test_provider_dispatch_loop.py:16`

Related: existing pattern in `tests/analysis/test_provider_work_queue.py` and `tests/analysis/test_continuous_planning_pipeline.py` did NOT need this because they don't contain dataclasses — the failure mode is decoration-time, not call-time.

**Do NOT apply when:** the script being tested has no decorators that introspect `cls.__module__` (plain functions are fine without `sys.modules` registration).

**Pilot reference:** discovered 2026-05-13 during #2665 implementation. First failure: tests/ai/test_approve_provider_plan.py collection raised `AttributeError: 'NoneType' object has no attribute '__dict__'` during `@dataclass` decoration of `TxState`. Fix: add `sys.modules["approve_provider_plan"] = module` before `exec_module`. Verified by 63/63 passing acceptance suite.
