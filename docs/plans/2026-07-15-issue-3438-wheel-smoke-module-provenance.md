# Plan for #3438: Require complete module provenance in installed-wheel smoke tests

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-07-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3438
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-15-plan-3438-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `tests/ci_smoke/test_workspace_hub_importable.py:47-53` — imports `workspace_hub.workstations.resolver`, calls `inspect.getfile(WorkstationPathResolver)`, and asserts the path equals `src/workspace_hub/workstations/resolver.py`. Gap: checks exactly ONE class from ONE module; does not sweep all loaded `workspace_hub.*` entries in `sys.modules` after import.
- Found: `tests/ci_smoke/test_workspace_hub_importable.py:1-8` — comment documents the intentional `PYTHONPATH=src` requirement for namespace package resolution. This design means CI smoke tests run against the checkout, not an installed wheel — a known, accepted pattern for workspace-hub. The issue's fix must distinguish "checkout mode" (expected here) from "installed-wheel mode" (the scenario that needs provenance checks).
- Found: `.github/workflows/baseline-check.yml:62-64` — CI runs `tests/ci_smoke/` with `PYTHONPATH: src`. The `uv sync --group dev` step does NOT install workspace-hub as a wheel; modules load from the checkout via PYTHONPATH. No provenance assertion exists to detect if a `workspace_hub` package were shadowing the namespace package from site-packages.
- Found: `tests/ci_smoke/test_workspace_hub_importable.py:72-101` — `test_workspace_hub_import_fails_without_pythonpath_src` verifies that WITHOUT PYTHONPATH the import fails. This guards against a silent shadowing scenario from PyPI, but only at the NAMESPACE level — a split module (e.g., `workspace_hub.parsing`) installed as an editable package alongside the namespace package would not be caught.
- Gap: No test sweeps `sys.modules` after import to enumerate all loaded `workspace_hub.*` modules and verify each resolves under the expected root. This is the "complete module provenance" check the issue requires.
- Gap: No workspace-hub test demonstrates the pattern for installed-wheel scenarios (where `sysconfig.get_path("purelib")` is the correct root, not `src/`). A reference implementation here lets worldenergydata and other tier-1 repos copy the pattern.

### Standards

| Standard | Status | Source |
|---|---|---|
| PEP 517 / PEP 660 — wheel build and editable installs | applicable | Issue body ("editable checkout or host installation") |
| PEP 420 — namespace packages (no `__init__.py`) | applicable | `test_workspace_hub_importable.py:7` comment |

### LLM Wiki pages consulted

- No relevant wiki pages under `knowledge/wikis/` covering Python wheel provenance or module `__file__` verification patterns.

### Documents consulted

- Issue [worldenergydata#924](https://github.com/vamseeachanta/worldenergydata/issues/924) — OPEN; this is the trigger finding. The landman package in worldenergydata is a proper pip-installable package (not a namespace package), making it the primary target for installed-wheel provenance checks. Body: "A fixture-backed CLI search or lookup completes without live network access."
- `tests/ci_smoke/test_workspace_hub_importable.py` — (see "Existing repo code" above) — existing pattern that this plan extends.
- `.github/workflows/baseline-check.yml:62` — `PYTHONPATH: src` injection documented as a deliberate test precondition.
- `.claude/rules/coding-style.md` — "Only validate at system boundaries." Module load is a trust boundary: code executing from an unexpected path constitutes a supply-chain risk.

### Gaps identified

- `sys.modules` sweep after import: not implemented anywhere in `tests/ci_smoke/`.
- Purelib-path check: no test verifies `__file__` resolves under `sysconfig.get_path("purelib")` in an installed-wheel context.
- Cross-platform portability: no test of the `Path.is_relative_to()` check on Windows (NTFS) vs Linux (ext4) — relevant since ace-win-1 is in the fleet.
- No reusable `_assert_module_provenance(prefix, expected_root)` helper that other repos can import.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-15T via `gh issue view`):
- `#3438` — OPEN — Require complete module provenance in installed-wheel smoke tests
- `worldenergydata#924` — OPEN — fix(landman): make provider routing executable and prove the CLI smoke path

**File existence** (verified 2026-07-15):
- EXISTS: `tests/ci_smoke/test_workspace_hub_importable.py`
- EXISTS: `tests/ci_smoke/test_ci_workflows_use_uv.py`
- EXISTS: `tests/ci_smoke/test_review_gate_no_uv_dependency.py`
- EXISTS: `.github/workflows/baseline-check.yml`
- MISSING (new — this plan creates): `tests/ci_smoke/test_module_provenance.py`

**Line excerpts** (`test_workspace_hub_importable.py:47-57` — the current one-class check):
```python
resolver_mod = importlib.import_module("workspace_hub.workstations.resolver")
cls = getattr(resolver_mod, "WorkstationPathResolver")
assert cls is not None, "WorkstationPathResolver class missing from resolver module"

resolved_path = Path(inspect.getfile(cls)).resolve()
expected_path = (REPO_ROOT / RESOLVER_REL).resolve()
assert resolved_path == expected_path, (
    f"WorkstationPathResolver loaded from {resolved_path}, expected {expected_path}. ..."
)
```

**Gap proofs**:
- `grep -n "sys.modules" tests/ci_smoke/test_workspace_hub_importable.py` → 0 matches → confirms no sys.modules sweep exists.
- `grep -rn "get_path.*purelib\|purelib" tests/ci_smoke/` → 0 matches → confirms no installed-wheel provenance check exists.

**Reproduction proofs**:

N/A — this is not a runtime failure; it is a false-pass scenario (a test that should fail on a misconfigured environment but currently passes). The "failure" is the absence of a check. Marking: N/A — structural gap, not a failing test.

<!-- Verification: distinct sources counted — issue body (1), test_workspace_hub_importable.py code (2), baseline-check.yml (3), worldenergydata#924 (4), coding-style.md rule (5). Count: 5 ≥ 3 required. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-15-issue-3438-wheel-smoke-module-provenance.md` |
| New test (sys.modules sweep) | `tests/ci_smoke/test_module_provenance.py` |
| Modified test (extend coverage) | `tests/ci_smoke/test_workspace_hub_importable.py` |
| Plan review — Claude | `scripts/review/results/2026-07-15-plan-3438-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-07-15-plan-3438-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-07-15-plan-3438-gemini.md` |

---

## Deliverable

A new `tests/ci_smoke/test_module_provenance.py` file that (a) sweeps `sys.modules` after importing `workspace_hub` to enumerate all loaded `workspace_hub.*` modules, (b) verifies each `__file__` resolves under the expected root, and (c) provides a `_assert_module_provenance(prefix, expected_root)` helper that worldenergydata and other tier-1 repos can copy for installed-wheel scenarios. The existing `test_workspace_hub_importable.py` gains a companion assertion that the sweep catches shadowing from an editable install.

---

## Pseudocode

```python
# tests/ci_smoke/test_module_provenance.py

import importlib
import sysconfig
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"

def _assert_module_provenance(prefix: str, expected_root: Path) -> dict[str, Path]:
    """
    Import prefix, then sweep sys.modules for all loaded sub-modules.
    Assert every __file__ is under expected_root.
    Returns dict of {module_name: resolved_path} for inspection.
    """
    # clear any prior imports of this namespace
    for key in list(sys.modules):
        if key == prefix or key.startswith(prefix + "."):
            del sys.modules[key]

    importlib.import_module(prefix)

    violations = {}
    resolved = {}
    for name, mod in sys.modules.items():
        if not (name == prefix or name.startswith(prefix + ".")):
            continue
        file_attr = getattr(mod, "__file__", None)
        if file_attr is None:
            continue  # namespace package root — no __file__
        path = Path(file_attr).resolve()
        resolved[name] = path
        if not path.is_relative_to(expected_root.resolve()):
            violations[name] = path

    assert not violations, (
        f"Modules loaded from outside {expected_root}:\n"
        + "\n".join(f"  {k}: {v}" for k, v in violations.items())
    )
    return resolved


def test_workspace_hub_all_modules_resolve_under_src():
    """
    All workspace_hub.* modules loaded after import must resolve under src/.
    Catches editable-install shadowing that the one-class check in
    test_workspace_hub_importable.py would miss.
    Precondition: PYTHONPATH=src (set in CI; run locally with: PYTHONPATH=src pytest ...)
    """
    resolved = _assert_module_provenance("workspace_hub", SRC_ROOT)
    # At minimum, resolver must have been imported
    assert any("resolver" in name for name in resolved), (
        "Expected workspace_hub.workstations.resolver to be loaded; "
        "check that the namespace package and its sub-modules are reachable under PYTHONPATH=src."
    )


# --- Pattern for installed-wheel repos (e.g., worldenergydata/landman) ---
# Copy this pattern into that repo's smoke test, substituting:
#   prefix = "worldenergydata_landman"  (or the actual top-level package name)
#   expected_root = Path(sysconfig.get_path("purelib"))  (installed wheel location)
#
# def test_landman_all_modules_resolve_under_purelib():
#     purelib = Path(sysconfig.get_path("purelib"))
#     _assert_module_provenance("worldenergydata_landman", purelib)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/ci_smoke/test_module_provenance.py` | New test: sys.modules sweep + `_assert_module_provenance` helper |
| Modify | `tests/ci_smoke/test_workspace_hub_importable.py` | Add a call to `_assert_module_provenance` (or re-export its assertion) as a companion to the existing single-class check, so both are enforced together |
| Update | `docs/plans/2026-07-15-issue-3438-wheel-smoke-module-provenance.md` | This plan file |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_workspace_hub_all_modules_resolve_under_src` | All `workspace_hub.*` modules in sys.modules after import resolve under `src/` | Normal import with `PYTHONPATH=src` | No violations; `resolved` dict non-empty |
| `test_assert_module_provenance_detects_outside_module` | Helper raises `AssertionError` when a module resolves outside expected root | Monkeypatch `__file__` of a loaded module to `/tmp/fake.py` | `AssertionError` listing the offending module |
| `test_assert_module_provenance_tolerates_none_file` | Namespace package root (no `__file__`) is not flagged | Normal import of namespace package | No violation raised for `workspace_hub` entry itself |
| `test_workspace_hub_import_sweep_catches_editable_shadow` | Editable-install lookalike in site-packages would be caught | Monkeypatch sys.modules to inject a `workspace_hub.fake` with `__file__` under `/usr/lib/` | `AssertionError` naming the injected module |
| `test_module_provenance_is_platform_independent` | `Path.is_relative_to` handles platform path separators | Run on Linux path (backslash-free) | No assertion error; relies on `Path.resolve()` normalization |

---

## Acceptance Criteria

- [ ] All new tests pass: `PYTHONPATH=src uv run pytest tests/ci_smoke/test_module_provenance.py -v`
- [ ] No regression: `PYTHONPATH=src uv run pytest tests/ci_smoke/ -v` passes (all 5 existing tests still pass)
- [ ] `_assert_module_provenance("workspace_hub", SRC_ROOT)` returns a non-empty dict in CI (proves sweep is not vacuously passing on empty import)
- [ ] An injected `workspace_hub.fake` module with `__file__` outside `src/` causes the sweep test to fail (manually verified or via the monkeypatched test)
- [ ] Issue comment posted documenting the purelib-path pattern for worldenergydata to adopt (out-of-scope for this PR but required before close)
- [ ] Plan review adversarial artifacts posted to `scripts/review/results/`

---

## Risks and Open Questions

- **Risk:** `sys.modules` at sweep time may contain fewer modules than a deep import chain would load (lazy imports). The sweep should call `importlib.import_module(prefix)` then force-import all known sub-modules before sweeping, or accept that lazy-imported modules are not covered (document this limitation in test docstring).
- **Risk:** `__file__` for `.pyc` compiled files points to the `.pyc` under `__pycache__/`, not the `.py` source. `Path(file_attr).resolve()` still resolves under `src/` for checkout-mode tests — acceptable, since `.pyc` is under `src/workspace_hub/**/__pycache__/`.
- **Risk:** On Windows (ace-win-1), `Path.is_relative_to()` requires `Path.resolve()` to normalize drive letters. The pseudocode uses `.resolve()` on both sides — this is correct but should be verified on NTFS paths.
- **Open:** Should `_assert_module_provenance` be published as a workspace-hub utility that worldenergydata can pip-install, or should worldenergydata copy the helper into its own test suite? (Copy is simpler and avoids a packaging dependency — flag for user during approval.)

---

## Complexity: T2

**T2** — one new test file created, one existing test file modified with a companion assertion. No implementation code changes. Requires adversarial review before implementation per issue gate.
