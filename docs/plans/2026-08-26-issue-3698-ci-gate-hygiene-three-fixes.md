# Plan for #3698: PR gate is baseline-red: two enforcement checks fail on every PR, plus an undeclared test dep

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-08-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3698
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-08-26-plan-3698-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/enforcement/check-scheduler-mutation-surfaces.py` — the gate script that exits with "identity inventory input digest is stale". Entry point for Fix 1.
- Found: `scripts/enforcement/scheduler_mutation_delegation.py` lines 110–126 — `_validate_inventory_digest` computes a SHA256 over 8 source files (`config/scheduled-tasks/schedule-tasks.yaml`, `config/workstations/registry.yaml`, `config/workstations/harness-state-classes.yaml`, and 5 `scripts/cron/*.py` files) and compares against `inventory["input_digest"]`. Stale when any of those 8 files has changed since the last `build-cron-identity-inventory.py` run.
- Found: `scripts/cron/build-cron-identity-inventory.py` — regenerates `docs/reports/issue-3475-command-identity-inventory.json` with a fresh digest; single-command fix for Fix 1.
- Found: `docs/reports/issue-3475-command-identity-inventory.json` — current inventory artifact; `input_digest: b8fe099c6e205a0ccc4db6292d02328c30c431bc50e5435314874fab1ccb7209`; needs regeneration.
- Found: `.github/workflows/legal-rule-authority-gate.yml` — **Fix 2 is already applied.** The workflow was updated (Owner directive 2026-08-01) to run `bash scripts/legal/legal-sanity-scan.sh --repo=workspace-hub` directly, removing the AUTH_ENVELOPE dependency. The comment in the file confirms: "a secret that was never provisioned in this repo. `test -n "$AUTH_ENVELOPE"` therefore exited 1 on EVERY same-repo PR". This fix was landed; the issue body pre-dates the fix.
- Found: `tests/hf/test_save_results_to_hf.py` line 41 — `import pandas as pd` inside `test_numeric_stats_reports_min_max_nulls`. Fix 3 target.
- Found: `pyproject.toml` lines 22–32 — `[project.optional-dependencies].dev` lists pytest, pytest-cov, jsonschema, pytest-socket, zss, scipy, PyYAML. `pandas` is absent from all extras.

### Standards

| Standard | Status | Source |
|---|---|---|
| pytest `importorskip` / conditional skip pattern for optional deps | Standard pytest practice | pytest docs; not repo-specific |
| Governance: stale digest = blocked gate (by design) | Confirmed | `scheduler_mutation_delegation.py` lines 121–126; issue #3475 |

### LLM Wiki pages consulted

- No relevant wiki pages found under `knowledge/wikis/` for pytest optional-dep skip patterns or CI gate governance.

### Documents consulted

- Issue #3698 body — three defects precisely described with reproduction context (merged PRs #3599, #3597, #3581 showed the red checks)
- `.github/workflows/legal-rule-authority-gate.yml` (live checkout) — confirmed Fix 2 (AUTH_ENVELOPE) is already applied; the comment in the file cites the owner directive date 2026-08-01
- `scripts/enforcement/scheduler_mutation_delegation.py` (live checkout, lines 110–126) — confirmed the 8-file digest computation; this is the exact check that exits 1
- `pyproject.toml` (live checkout, lines 22–32) — confirmed `pandas` is absent from all optional dependency groups
- Related issue #3475 — `docs/reports/issue-3475-command-identity-inventory.json` is the governance artifact for the scheduler mutation surface guard; the inventory must be regenerated, not silently patched

### Gaps identified

- The identity inventory regeneration command (`uv run python scripts/cron/build-cron-identity-inventory.py`) must be run and the output committed; the plan cannot pre-calculate which of the 8 inputs drifted without running it
- The `strict-scan / authority` gate status post-fix-2 is not independently verified in a real PR run (the workflow file shows the fix, but no confirmed green PR evidence exists yet)

### Evidence (embedded verification)

**Issue status** (verified 2026-08-26 via `gh issue view 3698`):
- `#3698` — OPEN — PR gate is baseline-red: two enforcement checks fail on every PR, plus an undeclared test dep
- Labels: `machine:dev-primary`, `domain:ci-release`

**File existence** (`ls -la` 2026-08-26):
- EXISTS: `scripts/enforcement/check-scheduler-mutation-surfaces.py`
- EXISTS: `scripts/enforcement/scheduler_mutation_delegation.py`
- EXISTS: `scripts/cron/build-cron-identity-inventory.py`
- EXISTS: `docs/reports/issue-3475-command-identity-inventory.json` — contains `input_digest: b8fe099c6e205a0ccc4db6292d02328c30c431bc50e5435314874fab1ccb7209`
- EXISTS: `.github/workflows/legal-rule-authority-gate.yml` — already contains the direct `legal-sanity-scan.sh` invocation (Fix 2 applied)
- EXISTS: `tests/hf/test_save_results_to_hf.py`
- EXISTS: `pyproject.toml`

**Line excerpts** (`sed -n 110,127p scripts/enforcement/scheduler_mutation_delegation.py` 2026-08-26):
```python
def _validate_inventory_digest(inventory, records, errors):
    sources = [b"config/scheduled-tasks/schedule-tasks.yaml", b"config/workstations/registry.yaml",
               b"config/workstations/harness-state-classes.yaml", b"scripts/cron/build-cron-identity-inventory.py",
               b"scripts/cron/cron_render.py", b"scripts/cron/cron_transaction.py",
               b"scripts/cron/cron_line_model.py", b"scripts/cron/cron_identity.py"]
    digest = hashlib.sha256(b"cron-identity-input-v1\0")
    for source in sorted(sources):
        digest.update(struct.pack(">Q", len(source)) + source)
        body = records[source]
        digest.update(struct.pack(">Q", len(body)) + body)
    if inventory.get("input_digest") != digest.hexdigest():
        errors.append("identity inventory input digest is stale")
```

**pyproject.toml dev extras** (`sed -n 22,32p pyproject.toml` 2026-08-26):
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "jsonschema>=4.21",
    "pytest-socket",
    "zss==1.2.0",
    "scipy>=1.11",
    "PyYAML>=6.0",
]
```
— `pandas` absent; confirmed.

**test_save_results_to_hf.py line 41** (2026-08-26):
```python
    import pandas as pd
```
— bare import inside test function; no skip guard.

**Gap proof — Fix 2 already applied** (`head -60 .github/workflows/legal-rule-authority-gate.yml` 2026-08-26):
```yaml
  strict-scan:
    name: strict-scan
    if: ${{ github.event.pull_request.head.repo.full_name == github.repository }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Legal sanity scan
        run: bash scripts/legal/legal-sanity-scan.sh --repo=workspace-hub
```
Confirms Fix 2 was already implemented; only Fix 1 and Fix 3 remain as actual work.

**Reproduction proof**: N/A for Fix 1 (stale digest is a deterministic state, confirmed by inventory file contents). Fix 3 — the import at line 41 fails on bare `uv run --with pytest python -m pytest tests/hf/test_save_results_to_hf.py::test_numeric_stats_reports_min_max_nulls` when pandas is absent.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-08-26-issue-3698-ci-gate-hygiene-three-fixes.md` |
| Fix 1 — regenerated inventory | `docs/reports/issue-3475-command-identity-inventory.json` (regenerated in-place) |
| Fix 3 — pyproject.toml pandas dep | `pyproject.toml` |
| Fix 3 — test skip guard | `tests/hf/test_save_results_to_hf.py` |
| Plan review — Claude | `scripts/review/results/2026-08-26-plan-3698-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-08-26-plan-3698-codex.md` |
| Plan review — Agy | `scripts/review/results/2026-08-26-plan-3698-agy.md` |

---

## Deliverable

The PR gate will be green on the next same-repo PR: the scheduler mutation guard will pass (fresh inventory digest), the `legal-rule-authority` gate was already fixed (Fix 2 verified), and `test_numeric_stats_reports_min_max_nulls` will either skip cleanly when pandas is absent or pass when pandas is present — removing the undocumented `--with pandas` workaround requirement.

---

## Pseudocode

```
# Fix 1: Regenerate inventory digest
cd workspace-hub
uv run python scripts/cron/build-cron-identity-inventory.py
# Verify no errors in output
# Confirm docs/reports/issue-3475-command-identity-inventory.json has new input_digest
# Verify the check now passes:
uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py
# Commit the updated inventory file

# Fix 2: Already applied — verify only
# Confirm legal-rule-authority-gate.yml contains direct scan call (not AUTH_ENVELOPE check)
# No file changes needed

# Fix 3a: Add pandas to pyproject.toml dev extras
# Edit pyproject.toml: add "pandas>=1.5" to [project.optional-dependencies].dev
# AND to [dependency-groups].dev (if that group is the CI-installed one)

# Fix 3b: Add pytest.importorskip guard in test
# In tests/hf/test_save_results_to_hf.py:
#   Change `import pandas as pd` to:
#   pd = pytest.importorskip("pandas")
# This makes the test skip (not fail) when pandas is absent
```

---

## Files to Change

1. **`docs/reports/issue-3475-command-identity-inventory.json`** — regenerated by running `uv run python scripts/cron/build-cron-identity-inventory.py`; the file's `input_digest` field will be updated to reflect current state of the 8 source files. This is a governance artifact — must be regenerated, not hand-edited.

2. **`pyproject.toml`** — add `"pandas>=1.5"` to `[project.optional-dependencies].dev` (line ~29). Also add to `[dependency-groups].dev` if that is the group CI installs (check `uv sync --group dev` vs `uv pip install -e '.[dev]'` in CI).

3. **`tests/hf/test_save_results_to_hf.py`** line 41 — change `import pandas as pd` to `pd = pytest.importorskip("pandas")`. The `pytest.importorskip` call skips the enclosing test with a clear skip message when the module is absent, rather than raising an ImportError that shows as a test error.

---

## TDD Test List

Fix 1 (inventory digest) — no new test file; verification is the gate itself:

1. **`verify_scheduler_gate_passes_after_regeneration`** (manual verification step, not a new pytest) — run `uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` after regenerating inventory; exit code must be 0. Documents the "before/after" in the commit message.

Fix 3 (pandas) — existing test `test_numeric_stats_reports_min_max_nulls`:

2. **`test_numeric_stats_reports_min_max_nulls` with no pandas** — after adding `pytest.importorskip`, running without pandas installed must show `SKIPPED` (not `ERROR`). Verifiable by `uv run pytest tests/hf/test_save_results_to_hf.py::test_numeric_stats_reports_min_max_nulls` in a bare environment.

3. **`test_numeric_stats_reports_min_max_nulls` with pandas** — same test must `PASS` when run with `uv run --with pandas pytest ...`. This test already passes with pandas; guard must not break it.

4. **New: `test_dev_extra_declares_pandas`** (in `tests/hf/test_save_results_to_hf.py` or a new `tests/test_project_metadata.py`) — read `pyproject.toml`, assert `pandas` appears in the `dev` optional-dependency group. Locks the declared-dep requirement in CI so it cannot silently disappear.

---

## Acceptance Criteria

1. `uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` exits 0 after inventory regeneration
2. The legal-rule-authority CI gate (`strict-scan` job) is already green — confirmed by reading `.github/workflows/legal-rule-authority-gate.yml` (Fix 2 previously applied); no file changes required
3. `uv run pytest tests/hf/test_save_results_to_hf.py` exits 0 (all pass or skip — no errors)
4. `pandas>=1.5` is listed in `[project.optional-dependencies].dev` in `pyproject.toml`
5. The commit message for Fix 1 documents which of the 8 source files drifted (derived from `build-cron-identity-inventory.py` output)
6. No new permanently-red CI check introduced (the `test_dev_extra_declares_pandas` test must itself be green)

---

## Risks and Open Questions

- **Fix 1 governance risk**: The issue body explicitly cautions: "Silently regenerating a digest to make a guard go green is exactly the move that guard exists to catch." Before committing the regenerated inventory, the implementer must inspect `build-cron-identity-inventory.py` output to identify *which* of the 8 source files drifted and confirm the drift was intentional (not a rogue change). This is the due-diligence step the issue requires.
- **Two `dev` groups**: `pyproject.toml` has both `[project.optional-dependencies].dev` and `[dependency-groups].dev` (lines 22–32 and 43–52). CI may install from one but not the other. Implementer must check which one the CI workflow uses (`uv sync --group dev` uses dependency-groups; `uv pip install -e '.[dev]'` uses optional-dependencies). Add pandas to whichever group CI reads; adding to both is safe but worth noting.
- **Fix 2 verification**: The AUTH_ENVELOPE fix is present in the workflow file, but no confirmed green PR run is cited. The first PR after this plan lands should verify the `strict-scan` job produces a green result. If the legal-sanity-scan.sh script itself fails for an unrelated reason, that's a new issue — not in scope here.
- **`pytest.importorskip` placement**: The current `import pandas as pd` is at line 41, inside the test function body. `pytest.importorskip` at function-body scope skips only that test; a module-scope call would skip all tests in the file. Given only one test imports pandas, function-scope skip is correct.
