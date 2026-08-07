---
name: reference_digitalmodel_python_env_venv
description: digitalmodel Python env — .venv has NO pytest; to run tests use `uv run --with-editable '.[test]' python -m pytest`; cold import ~117s
metadata:
  node_type: memory
  type: reference
  originSessionId: 4e19e539-dc4c-444f-8e16-f47bd024a295
  modified: 2026-08-06T12:54:39.238Z
---

**To RUN TESTS in digitalmodel, `.venv` is useless — it has no pytest.**
Verified 2026-08-05: 507 packages installed, the entire `[test]` extra absent
(pytest, pytest-asyncio, pytest-timeout, pytest-randomly, hypothesis, coverage,
meshio, pyvista, memory-profiler). `.venv` was rebuilt 2026-08-03 from base deps
only. The system interpreters that DO have pytest (9.0.2 / 9.0.3) are outside the
repo's `pytest>=7.4.3,<9.0.0` pin and cannot import `digitalmodel` anyway.

The **only** working invocation, and what CI's domain gates use:

```
export UV_CACHE_DIR=/mnt/ace/ws/.uv-cache
uv run --with-editable '.[test]' python -m pytest ...
```

Documented only in a `pyproject.toml:124-125` comment — it is absent from
`README.md`, `Makefile`, and `AGENTS.md`, all three of which document commands
that fail with `No module named pytest`. Filed as digitalmodel #1982.

**Two traps once pytest runs:**
- `pytest.ini` `addopts` contains `-v`, which OVERRIDES a `-q` you pass — you get
  tree-format output with NO node IDs, and a `grep '::'` silently returns zero,
  which reads exactly like "the change added nothing". For node IDs override it:
  `-o addopts='--import-mode=importlib --tb=short --strict-markers' -q`.
  Keep `--import-mode=importlib` — it is load-bearing (53 duplicate test
  basenames coexist only because of it).
- Collection currently aborts on 2 pre-existing errors in `tests/workflow_api/`
  (drifted local `assetutilities` sibling). Pass
  `--continue-on-collection-errors` or you get NO listing at all.

**For plain imports** (not tests) `.venv/bin/python` still works, and `uv run
python ...` may hang re-syncing. **Cold `import digitalmodel` takes ~117s**: the
package `__init__.py` installs a "Layer 2 group redirect finder" import hook and
site-packages sits on a slow filesystem. Import ONCE in a long-lived process for
parametric sweeps; never spawn a subprocess per case. Use `timeout 200-300` on
first runs; ignore `OrcaFlex license not available` and pint `bbl` warnings.

Corrects this file's earlier claim that "digitalmodel `.venv` is fine" — true for
imports, false for tests. Briefing two subagents with `.venv/bin/python -m pytest`
on 2026-08-05 cost both of them a full round of failures before the real
interpreter was found. See [[feedback_verify_against_real_ci_lint_toolchain]] for
the same lesson on the lint side.
