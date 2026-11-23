# Archived Skill: `diagnose-stale-pycache-import-mismatch`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/diagnose-stale-pycache-import-mismatch`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/diagnose-stale-pycache-import-mismatch`
Consolidation date: 2026-04-29

---

---
name: diagnose-stale-pycache-import-mismatch
description: Diagnose Python ImportError cases where a symbol cannot be imported even though the source file already defines it; verify live source, interpreter/venv selection, clear stale __pycache__, and rerun targeted imports/tests.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [python, importerror, pycache, bytecode, debugging, venv]
    related_skills: [systematic-debugging]
---

# Diagnose stale __pycache__ import mismatch

Use when Python reports an error like:
- `ImportError: cannot import name 'X' from 'module'`
- but the referenced source file already contains `X`

## Why this matters

This failure is often misdiagnosed as a missing code change. In practice, common causes are:
1. stale `.pyc` bytecode in `__pycache__/`
2. the wrong virtualenv/interpreter
3. a long-lived process still using old imports
4. multiple copies of the repo/module on disk

## Procedure

1. Confirm the symbol exists in the live source file.
   - Read the exact file path shown in the traceback.
   - Verify the function/class really exists there now.

2. Confirm where Python is importing from.
   - Activate the intended environment.
   - Run a tiny import script and print `module.__file__`.
   - Check `hasattr(module, 'symbol')`.

3. Check both common local environments if the repo has more than one.
   - In hermes-agent, both `venv` and `.venv` may exist.
   - Validate imports under each when the failing process is unclear.

4. If source is correct but import still fails, clear local bytecode.
   - Target the module cache first:
     `rm -f __pycache__/module*.pyc`
   - If needed, clear repo caches:
     `find . -path '*/__pycache__/*' -delete`

5. Re-run the minimal import check.
   - Example:
     `python - <<'PY'`
     `import module`
     `print(module.__file__)`
     `print(hasattr(module, 'symbol'))`
     `PY`

6. Re-run targeted regression tests around the affected import path.
   - Prefer the smallest relevant set first, then widen if needed.

## Hermes-agent-specific pattern

In `/home/vamsee/.hermes/hermes-agent`, when a traceback references `utils.py` but a newly added helper is already present in that file:

1. Read `utils.py` and confirm the helper exists.
2. Import it under both environments if both exist:
   - `source venv/bin/activate`
   - `source .venv/bin/activate`
3. Print `utils.__file__` and verify `hasattr(utils, 'helper_name')`.
4. Remove local cached bytecode:
   - `rm -f __pycache__/utils.cpython-311.pyc __pycache__/utils.cpython-313.pyc`
5. Re-run the import and targeted pytest selection.

## Good verification bundle

```bash
source venv/bin/activate
python - <<'PY'
import utils
print(utils.__file__)
print(hasattr(utils, 'base_url_host_matches'))
PY
find . -path '*/__pycache__/*' -delete
pytest -q tests/test_base_url_hostname.py
```

## Decision rule

- If `module.__file__` points somewhere unexpected: fix environment/path selection.
- If `module.__file__` is correct and symbol is missing only before cache clear: stale bytecode was the likely cause.
- If imports succeed in a fresh shell but fail in the original process: restart that long-lived process/session.

## Pitfalls

- Do not assume the traceback path means the running interpreter has reloaded that file.
- Do not stop after reading source; always verify with a live import.
- Do not clear only site-packages caches if the failing module is from the repo root.
- If both `venv` and `.venv` exist, checking only one can hide the real problem.
