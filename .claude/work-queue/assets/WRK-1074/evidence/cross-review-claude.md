# WRK-1074 Cross-Review — Claude
reviewer: claude
stage: 6
date: 2026-03-09

## Verdict: APPROVE (with MINOR notes)

## Findings

### P2 — PYTHONPATH for worldenergydata is non-trivial
worldenergydata installs assetutilities via git URL (`git+https://...`), not as an editable
local path. Contract tests that `import assetutilities` will resolve to the git-installed version,
not the local workspace copy. This means `PYTHONPATH=src:../assetutilities/src` may not work as
expected unless the local path takes precedence over the installed package.

**Mitigation:** In conftest.py, assert `importlib.metadata.version("assetutilities")` and compare
with the local version. Document in docs/api-contracts.md that worldenergydata tests pin to the
installed git version. In development, use `pip install -e ../assetutilities` or adjust PYTHONPATH
order to ensure local copy takes precedence.

### P2 — ymlInput legacy alias
The plan marks ymlInput as a "legacy alias" with `provisional` stability. If ymlInput is actually
a wrapper or re-export rather than a true alias, the contract test needs to verify it returns the
same type as WorkingWithYAML usage would produce, not just that it's callable. Risk: the test
passes even after ymlInput is removed if the import error is silently caught.

**Mitigation:** Test should use `pytest.importorskip` or explicit `try/except ImportError` to
produce a SKIP (not PASS) if ymlInput is absent. This distinguishes "removed" from "changed".

### P3 — conftest pytest_runtest_makereport hook format
The plan says "prepend [CONTRACT VIOLATION]..." to longrepr. The `longrepr` field in
`pytest_runtest_makereport` is not always a string — it can be a `ReprExceptionInfo` object.
String prepending may fail or produce garbled output.

**Mitigation:** Use `report.longreprtext` (if available) or convert to str with `str(report.longrepr)`
before prepending. Or add a custom `pytest_terminal_summary` hook instead.

### P3 — AU_VERSION at module level
`importlib.metadata.version("assetutilities")` at module level will raise `PackageNotFoundError`
if assetutilities is not installed as a package (e.g., only on PYTHONPATH). This would silently
fail test collection.

**Mitigation:** Wrap in try/except, fall back to reading `__version__` from the module directly.

## Improvements

1. Add `conftest.py` at both `tests/contracts/` levels; also add `contracts` to each repo's
   `pytest.ini` `markers` section to avoid "unknown marker" warnings.
2. The run-all-tests.sh step should set `--markers contracts` not `-m contracts` (the flag is `-m`).
   Also, failing contracts should produce a clear section header in the run-all-tests.sh summary table.
3. Consider adding a `test_assetutilities_constants_contract.py` (basic: key physical constants
   importable and within expected magnitude) — very low cost, high signal.

## Overall
The plan is sound. The PYTHONPATH/version pinning issue (P2) is the most important thing to
handle correctly in implementation. The conftest hook approach is good but needs the longrepr
type-safety fix.
