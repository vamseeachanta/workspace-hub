# Plan for #2604: fix(digitalmodel): loosen test_packaged_b1528_yaml_declared_as_package_data substring assertion

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2604
> **Review artifacts:** scripts/review/results/2026-05-02-plan-2604-claude.md (single-author, see review.md)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `digitalmodel/tests/naval_architecture/test_b1528_sirocco_yaw_moment.py` line 109-111 — failing test reads `pyproject.toml` and asserts a single-line literal substring.
- Found: `digitalmodel/pyproject.toml` line 219-220 — `[tool.setuptools.package-data]` declares `digitalmodel = ["subsea/cross_sections/fixtures/*.yml", "naval_architecture/data/*.yml"]` (two entries on one line).
- Found: `digitalmodel/tests/naval_architecture/test_rudder_stock_torque_sweep.py::test_packaged_yaml_in_built_distribution_preserves_existing_package_data` (line 180-220) — verifies the **wheel manifest** actually contains `digitalmodel/naval_architecture/data/*.yml` plus `subsea/cross_sections/fixtures/*.yml` after `python -m build --wheel`. This is the durable behavioral check; #2604's failing test is redundant declaration-level validation.
- Found: `digitalmodel/tests/subsea/cross_sections/test_fixtures.py::test_fixture_package_data_available_after_install_metadata` (line 97-99) — uses `importlib.resources.files(...).iterdir()` against the installed package; another behavioral cross-check.
- No other tests in `digitalmodel/tests/` perform literal-string assertions on the `package-data` section (verified via `grep -rn "package-data\|package_data" digitalmodel/tests/`).

### Standards
Not applicable — packaging-test bugfix, not a standards-derived calculation.

### LLM Wiki pages consulted
No relevant wiki pages — this is a test-quality fix.

### Documents consulted
- Issue #2604 body — supplies the recommended fix verbatim: parse the TOML and assert array membership.
- Source #2566 (validation report referenced in #2604) — flagged this as a low-severity test bug; packaging itself works.
- `digitalmodel/pyproject.toml` line 1-3 — `requires-python = ">=3.11"` so `tomllib` (stdlib since 3.11) is always available. No new dependency required.

### Gaps identified
- No declaration-level test currently survives a multi-entry single-line array layout. The fix closes that gap.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):
- `#2604` — OPEN — title matches; labels: `priority:low`; severity called Low in body.

**File existence** (verified via Read tool 2026-05-02):
- EXISTS: `digitalmodel/tests/naval_architecture/test_b1528_sirocco_yaw_moment.py`
- EXISTS: `digitalmodel/pyproject.toml`
- EXISTS: `digitalmodel/tests/naval_architecture/test_rudder_stock_torque_sweep.py`
- EXISTS: `digitalmodel/tests/subsea/cross_sections/test_fixtures.py`

**Line excerpts**

`digitalmodel/tests/naval_architecture/test_b1528_sirocco_yaw_moment.py` lines 109-111:
```python
def test_packaged_b1528_yaml_declared_as_package_data():
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    assert 'digitalmodel = ["naval_architecture/data/*.yml"]' in pyproject
```

`digitalmodel/pyproject.toml` lines 219-220:
```toml
[tool.setuptools.package-data]
digitalmodel = ["subsea/cross_sections/fixtures/*.yml", "naval_architecture/data/*.yml"]
```

**Gap proofs**:
- `grep -rn "package-data\|package_data" digitalmodel/tests/` returns only 3 matches; only #2604's test does literal-string parsing — confirms no parallel literal-substring traps.
- Default `python3 --version` on host = 3.13.12, `python3 -c "import tomllib"` succeeds — tomllib is callable in any conforming venv.

Source count: 5 (issue body, failing test file, pyproject.toml, sibling test #1 rudder_stock, sibling test #2 cross_sections fixtures) — exceeds minimum 3.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-05-02-issue-2604-loosen-b1528-package-data-test.md |
| Test (modify) | `digitalmodel/tests/naval_architecture/test_b1528_sirocco_yaw_moment.py` |
| Implementation | none — test-only change |
| Plan review (single-author) | scripts/review/results/2026-05-02-plan-2604-claude.md |

---

## Deliverable

`test_packaged_b1528_yaml_declared_as_package_data` will pass against the current `pyproject.toml` by parsing TOML and asserting array membership of `naval_architecture/data/*.yml`, instead of matching a single-line literal that breaks whenever a second glob is added.

---

## Pseudocode

T1 — trivial. Replace the literal-substring assertion with a TOML parse and array-membership check using stdlib `tomllib`.

```python
import tomllib
data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
package_data = data["tool"]["setuptools"]["package-data"]["digitalmodel"]
assert "naval_architecture/data/*.yml" in package_data
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/tests/naval_architecture/test_b1528_sirocco_yaw_moment.py` | Replace literal-substring assertion (line 109-111) with `tomllib.loads(...)` + array-membership check |

No change to `pyproject.toml`. No new dependency (`tomllib` is Python 3.11+ stdlib; `requires-python = ">=3.11"`).

---

## TDD Test List

Existing test transitions from RED → GREEN. No new test cases needed; the fix is to relax over-strict assertion semantics.

| Test name | Pre-fix | Post-fix |
|---|---|---|
| `test_packaged_b1528_yaml_declared_as_package_data` | FAIL — literal substring `digitalmodel = ["naval_architecture/data/*.yml"]` not in current pyproject (which has 2 entries on one line) | PASS — parses TOML, asserts `"naval_architecture/data/*.yml" in package-data["digitalmodel"]` |

Adjacent tests that should remain GREEN (cross-checks, not modified):
- `test_packaged_yaml_in_built_distribution_preserves_existing_package_data` (rudder_stock_torque_sweep.py) — wheel-manifest level
- `test_fixture_package_data_available_after_install_metadata` (subsea/cross_sections/test_fixtures.py) — runtime resources level

---

## Acceptance Criteria

- [ ] `uv run pytest digitalmodel/tests/naval_architecture/test_b1528_sirocco_yaw_moment.py::test_packaged_b1528_yaml_declared_as_package_data -v` passes against current `pyproject.toml`.
- [ ] Same test still passes if `pyproject.toml` `package-data` is collapsed to a single-entry layout (`digitalmodel = ["naval_architecture/data/*.yml"]`) — forward-compat.
- [ ] Same test still fails (correctly) if `naval_architecture/data/*.yml` is removed from `package-data["digitalmodel"]` — negative-case correctness.
- [ ] `uv run pytest digitalmodel/tests/naval_architecture/ -v` regression-clean.
- [ ] No new dependency added to `digitalmodel/pyproject.toml`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (single-author) | see `/tmp/plan-issue-2604/review.md` | (defect count emitted in review) |

**Overall result:** to be set after review and user approval.

Single-author rationale: T1 packaging-test fix; cross-AI review optional per project policy. Codex sandbox cannot exec the venv (per memory `feedback_codex_sandbox_no_execution`), and the change surface is a single test file with a referenced fix in the issue body — disproportionate to dispatch.

---

## Risks and Open Questions

- **Risk (low):** `tomllib` parse path requires Python 3.11+. Mitigated — `digitalmodel/pyproject.toml` declares `requires-python = ">=3.11"`; verified `tomllib` is importable on host Python 3.13.12.
- **Risk (very low):** Test relies on `Path("pyproject.toml")` resolving from cwd. Pytest runs with `testpaths = ["tests"]` and cwd typically at repo root; pre-existing behavior, not changed by this fix.
- **Risk (negligible):** A typo in the dotted-key path (`tool.setuptools.package-data.digitalmodel`) would cause `KeyError`. Mitigated by emitting an explicit assertion message and the structure being stable.
- **Open:** Should the fix also assert `"subsea/cross_sections/fixtures/*.yml" in package_data` for symmetry? This would couple the b1528 test to subsea fixtures — out of scope; the rudder_stock wheel-manifest test already covers it. Recommend NO.
- **Open:** Should we additionally tighten `digitalmodel/tests/naval_architecture/test_rudder_stock_torque_sweep.py` or `test_fixtures.py` while in the area? They use behavioral checks (importlib.resources, wheel manifest) and are not affected by literal-string drift. Recommend NO — out of scope.

---

## Out of Scope

- Modifying `pyproject.toml` package-data layout (works correctly today).
- Refactoring sibling tests (`test_rudder_stock_torque_sweep.py`, `test_fixtures.py`) — they already use behavioral assertions.
- Adding a generic pyproject-validation utility — overkill for one assertion.
- Fixing other tests flagged by #2566 validation — separate issues each.

---

## Complexity: T1

T1 — single-file, single-test, ~3-line assertion swap; no new dependencies; deterministic; behavioral cross-checks already exist in adjacent tests.
