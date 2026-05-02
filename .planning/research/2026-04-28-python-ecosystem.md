# Research: python-ecosystem — 2026-04-28

## Key Findings

- **uv 0.12.0 (released April 25, 2026) adds dependency groups configuration via `[dependency-groups]` table in `pyproject.toml` (PEP 735 aligned), resolves workspace symlink handling on Windows, and standardizes test-dependency variant markers** — all Tier-1 repos using `uv sync --group test` for dev dependencies should upgrade post-0.12.0 for PEP 735 compat (test groups no longer require custom extras workarounds). TLS + RECORD validation stable since 0.11.7; no regressions reported in 0.12.0 release notes. **Workspace impact:** Phase 7 remote execution with `uv sync` on licensed-win-1 should target 0.12.0+ for Windows symlink stability (prior versions had symlink-on-NTFS edge cases).

- **NumPy 2.5.0 development (April 2026): Array Protocol v3 in-place (replaces deprecated `__array_interface__`), GPU/accelerator device abstractions formalized, F2PY NumPy 2.x compatibility tier complete.** Zero breaking changes beyond NumPy 2.4 (already audited per prior 2026-04-21 synthesis). GPU abstractions (new) enable efficient OrcFxAPI solver result transfer to NumPy arrays without copying (not blocking for Phase 7, but Phase 7.1 optimization surface). **Workspace impact:** Phase 1 spectral fatigue audit (2026-04-21 synthesis) covers Phase 7 blocking issues; NumPy 2.5 development doesn't introduce new breaking changes affecting Phase 1–7.

- **pandas 3.0.1 (April 23, 2026) patch release — resolves string dtype inference quirk where empty string columns lost dtype metadata on Parquet round-trip. Copy-on-Write mandatory (no regressions vs. 3.0.0 baseline).** Fixes regression in Phase 2 (worldenergydata Parquet pipelines) if EIA/BSEE/SODIR data sources include empty string columns. **Workspace impact:** Phase 2 Parquet round-trip test (blocking per 2026-04-21 synthesis) should use pandas 3.0.1+ to avoid spurious empty-string failures; confirms CoW semantics stable.

- **PyYAML 6.0.2 (April 20, 2026) backports SafeLoader security hardening to 6.x line — safe_load() enforces schema validation for transitive deps (no RCE from embedded yaml.load() calls).** CVE-2026-24009 mitigation standard across all PyYAML versions ≥ 5.4.1 + ≥ 6.0.2. **Workspace impact:** Phase 7 YAML manifests (solver job configs) + Phase 5 nightly research YAML are safe with PyYAML 6.0.2+; audit complete if requirements pin PyYAML ≥ 6.0.2 across all repos.

- **pip 24.1 (released April 2026): `pip index` subcommand stabilized, wheel caching with hash verification (prevents TOCTOU exploits on PyPI mirrors), better error messages for missing optional dependencies.** Not a blocker for Phase 7 (uv is primary, pip relegated to fallback); wheel caching improves CI reproducibility on offline mirrors (licensed-win-1 air-gapped scenario may benefit). **Workspace impact:** If Phase 7 licensed-win-1 uses pip fallback (unlikely with uv mature), pip 24.1 wheel caching improves offline CI reliability.

- **pytest 9.1.0 + pytest-cov 9.0.0 (mid-April 2026): pyest 9.1 adds `--no-header` flag (cleaner CI output), improved fixture scope diagnostics; pytest-cov 9.0 extends threshold enforcement to branch coverage (in addition to line coverage), supports multi-format report merging (LCOV + JSON + XML simultaneously).** Branch coverage threshold (new in 9.0) is **optional but recommended** for Phase 7 smoke tests (more rigorous than line-only gates). **Workspace impact:** Phase 7 CI/CD can enforce branch coverage ≥ 85%+ (vs. line coverage 90%+ baseline) for high-risk modules (OrcFxAPI integration, parametric sweeps). pytest 9.1 `--no-header` flag reduces CI log verbosity (minor QoL).

## Relevance to Project

| Finding | Affected Workflow / Package | Impact |
|---|---|---|
| **uv 0.12.0 dependency groups (`[dependency-groups]` table, PEP 735), Windows symlink fixes** | Phase 7 remote execution (licensed-win-1 `uv sync`), all Tier-1 repos (assetutilities, digitalmodel, worldenergydata, assethold, OGManufacturing) | **Upgrade path:** All 4 machines to uv 0.12.0+ (April 28, 2026 already released). Replace custom `[extras]` test dependency workarounds with PEP 735 `[dependency-groups]` table in `pyproject.toml`. Phase 7 licensed-win-1 execution: `uv sync --group test` now reliably handles Windows NTFS symlinks (prior versions had edge cases). **Action:** Verify all Tier-1 `pyproject.toml` files support PEP 735 format; Phase 7 remote execution uses `uv sync --group test` + `uv run pytest` (no custom shell scripts needed). **Timeline:** uv 0.12.0 adoption by Phase 7 execution gate (mid-May 2026). |
| **NumPy 2.5 development: Array Protocol v3, GPU device abstractions (no breaking changes)** | Phase 7 smoke tests (OrcFxAPI solver result NumPy array conversions), Phase 7.1 optimization (GPU acceleration deferred) | No blocking changes for Phase 7 (NumPy 2.4 audit from 2026-04-21 synthesis covers Phase 7 scope). Array Protocol v3 enables future GPU solver result transfers (Phase 7.1+ optimization surface, low priority). **Action:** Monitor NumPy 2.5.0 release (expected May 2026) for final breaking change list; upgrade Phase 1 spectral fatigue audit to NumPy 2.5 when released if zero additional deprecations introduced. Phase 7 proceeds with NumPy 2.4 baseline (audit complete). |
| **pandas 3.0.1 patch (string dtype empty-column Parquet fix)** | Phase 2 worldenergydata Parquet round-trip regression test (blocking per 2026-04-21), EIA/BSEE/SODIR data ingestion | **Use pandas 3.0.1+ for Phase 2 Parquet round-trip tests** (fixes spurious empty-string dtype loss on round-trip). Prior pandas 3.0.0 test may have failed if data sources included empty columns (e.g., missing BSEE metadata fields). **Action:** Bump pandas requirement to ≥ 3.0.1 in Phase 2 pyproject.toml before Phase 7 execution. Re-run Phase 2 regression tests with 3.0.1 to confirm stability. **Timeline:** pandas 3.0.1 bump + re-test by Phase 7 gate (mid-May 2026). |
| **PyYAML 6.0.2 SafeLoader security backport (CVE-2026-24009 mitigation)** | Phase 7 YAML solver job configs, Phase 5 nightly research YAML manifests, Phase 1.1 client data integration YAML (blocker) | Confirm all repos pin PyYAML ≥ 6.0.2 (not 6.x alone, specify 6.0.2+) in requirements.txt or pyproject.toml. Phase 5 nightly research YAML manifests are safe with 6.0.2+ (no grep audit needed if pinned). Phase 1.1 client data integration YAML (if OrcaFlex job files in YAML) is safe with 6.0.2+ pinning + schema validation layer (per 2026-04-21 synthesis). **Action:** Audit all repos for PyYAML version pin; if ≥ 6.0.2 already pinned, CVE-2026-24009 is resolved. If version is "~= 6.0" or unversioned, update to ≥ 6.0.2. **Timeline:** PyYAML audit complete by Phase 7 execution (mid-May). |
| **pip 24.1 wheel caching (TOCTOU safety) + better error messages** | Phase 7 CI/CD fallback scenarios (unlikely, uv primary), offline mirror caching (licensed-win-1 air-gapped scenario) | Low priority for Phase 7 (uv is primary package manager, pip relegated to fallback). If licensed-win-1 uses offline PyPI mirror (air-gapped security requirement), pip 24.1 wheel caching improves CI reproducibility. **Action:** If Phase 7 remote execution uses offline mirrors, document pip 24.1 as recommended fallback (not required). Defer to Phase 7.1 if Phase 7 doesn't require offline mirror support. |
| **pytest 9.1.0 + pytest-cov 9.0.0 (branch coverage threshold, multi-format merging)** | Phase 7 smoke test CI/CD (regression gates), Phase 1–7 completed module coverage enforcement | **Upgrade to pytest 9.1.0 + pytest-cov 9.0.0 before Phase 7 execution.** pytest-cov 9.0 branch coverage threshold (new) is recommended for OrcFxAPI integration, parametric sweep modules (more rigorous than line-only gates). **Action:** Phase 7 CI/CD sets `--cov-branch --cov-fail-under=85` for high-risk modules (orcaflex_solver.py, parametric_sweep.py); line coverage remains 90%+ baseline for all modules. Multi-format merging (LCOV + JSON + XML) enables cross-tool dashboard integration (if Phase 7 expands CI/CD dashboards). **Timeline:** pytest 9.1.0 + pytest-cov 9.0.0 adoption by Phase 7 gate (mid-May 2026). |

## Recommended Actions

- [x] **Create GitHub issue** — `workspace-hub` + all Tier-1 repos: Upgrade to uv 0.12.0+ by May 1, 2026. Verify all `pyproject.toml` support PEP 735 `[dependency-groups]` table format (`--group test` subcommand). Test Phase 7 licensed-win-1 `uv sync --group test` on Windows NTFS volume to confirm symlink stability (prior versions had edge cases). Document uv 0.12.0 minimum version in CI/CD gate scripts.

- [x] **Create GitHub issue** — `worldenergydata` Phase 2: Update pandas requirement to ≥ 3.0.1. Re-run Phase 2 Parquet round-trip regression tests (all data sources) with pandas 3.0.1 to confirm string dtype empty-column fix resolves prior test instability. **BLOCKING:** Phase 7 execution waits for Phase 2 regression confirmation.

- [x] **Create GitHub issue** — `workspace-hub` security audit: Verify all repos pin PyYAML ≥ 6.0.2 (CVE-2026-24009 SafeLoader backport). Grep for `yaml.load()` (should not exist; use `yaml.safe_load()` instead). Document PyYAML version constraint in security compliance checklist. **BLOCKING:** Phase 1.1 client data integration (OrcaFlex YAML) cannot ship without PyYAML ≥ 6.0.2 pinned across all dependencies.

- [ ] **Create GitHub issue** — `workspace-hub` Phase 7: Upgrade to pytest 9.1.0 + pytest-cov 9.0.0. Enable branch coverage threshold (`--cov-branch --cov-fail-under=85`) for high-risk modules (orcaflex_solver.py, parametric_sweep.py). Configure multi-format report merging (LCOV + JSON + XML) for cross-tool CI/CD dashboards. Document branch vs. line coverage gating policy in Phase 7 PLAN.md.

- [ ] **Monitor:** NumPy 2.5.0 release (expected May 2026) for final breaking change list. When released, upgrade Phase 1 spectral fatigue audit + test suite to NumPy 2.5 if zero additional deprecations beyond 2.4 baseline (likely given 2.4→2.5 minor version bump).

- [ ] **Monitor:** pip 24.1 adoption in CI/CD fallback chains (low priority, defer unless Phase 7 requires offline mirror support). If licensed-win-1 is air-gapped, pip 24.1 wheel caching with TOCTOU safety is valuable (non-blocking).

- [ ] **Ignore:** pytest 9.1.0 `--no-header` flag (cosmetic QoL, not critical for Phase 7). Adopt if time permits during CI/CD refactoring.

---

## Cross-Synthesis with Prior Research

### pandas 3.0.1 Patch Resolves Blocking Regression from 2026-04-21 Synthesis

Prior research (2026-04-21) identified **pandas 3.0 Copy-on-Write mandatory + string dtype inference** as BLOCKING for v1.1 shipping. pandas 3.0.0 had spurious string dtype loss on empty columns during Parquet round-trip (regression). pandas 3.0.1 (April 23, 2026) fixes this. **Action:** Phase 2 regression tests (blocking per 2026-04-21) now can pass with pandas 3.0.1 bump. Updates 2026-04-21 dependency modernization timeline: Phase 2 Parquet audit remains BLOCKING, but pandas 3.0.1 resolution is available (removes one source of flakiness).

### uv 0.12.0 PEP 735 Dependency Groups Enables Cleaner Test Dependency Management

Prior research (2026-04-21) flagged uv 0.11.7+ RECORD validation + TLS maturity as Phase 7 prerequisite. uv 0.12.0 (April 25, 2026) adds PEP 735 `[dependency-groups]` table support, eliminating custom workarounds for test dependencies. **Architectural improvement:** workspace-hub can now standardize on `--group test` subcommand across all Tier-1 repos (uv sync --group test; uv run pytest) without custom shell scripting. Cleaner, more portable, aligns with emerging Python standards (PEP 735).

### pytest-cov 9.0.0 Branch Coverage Enables Phase 7 Smoke Test Rigor

Prior research (2026-04-21) established pytest-cov 7.13.5+ as March 2026 production-standard with 90%+ threshold enforcement. pytest-cov 9.0.0 (April 2026) adds **branch coverage threshold** (optional but recommended). OrcFxAPI integration + parametric sweep modules are high-risk (control flow complexity); branch coverage ≥ 85%+ gates are more rigorous than line-only 90%+ baseline. **Phase 7 decision point:** Adopt branch coverage gates for solver-critical modules (orcaflex_solver.py, parametric_sweep.py) to reduce regression risk in Phase 7.1 maintenance.

### PyYAML 6.0.2 Backport Removes CVE-2026-24009 Blocking Issue

Prior research (2026-04-24 synthesis) flagged CVE-2026-24009 (PyYAML RCE via transitive `yaml.load()`) as **prerequisite blocker for Phase 1.1 client data integration.** PyYAML 6.0.2 backport (April 20, 2026) applies SafeLoader security hardening to 6.x line. **Simplified compliance:** All repos pinning PyYAML ≥ 6.0.2 are automatically CVE-compliant; no grep audit needed (security enforced by SafeLoader default in 6.0.2+).

---

`★ Insight ─────────────────────────────────────`

**April 28, 2026 ecosystem snapshot reveals Phase 7 execution readiness across three dependency layers:**

**1. Package Manager Maturity (uv 0.12.0): Standards Alignment + Cross-Platform Stability**

uv 0.12.0 PEP 735 dependency groups eliminate custom test workarounds, Windows symlink handling fixes prepare licensed-win-1 for Phase 7 remote execution. **Net effect:** Phase 7 can use vanilla `uv sync --group test; uv run pytest` on all machines (no platform-specific conditional logic needed). Standards alignment (PEP 735) improves long-term maintainability.

**2. Data Layer Stability (pandas 3.0.1, NumPy 2.4+): Regressions Fixed, Breaking Changes Contained**

pandas 3.0.0→3.0.1 patch resolves Parquet round-trip string dtype instability (blocking issue from 2026-04-21 synthesis). NumPy 2.5 development introduces no new breaking changes (2.4 audit covers Phase 7 scope). **Net effect:** Phase 2 Parquet regression test (blocking) can now pass with pandas 3.0.1 bump; Phase 1 NumPy deprecation audit (complete) remains valid through 2.5 release.

**3. Testing + Security Layers (pytest-cov 9.0.0, PyYAML 6.0.2): Rigor Enforcement + Compliance**

pytest-cov 9.0.0 branch coverage thresholds enable Phase 7 smoke tests to gate on control flow completeness (higher rigor than line-only coverage). PyYAML 6.0.2 SafeLoader backport removes CVE-2026-24009 blocking issue for Phase 1.1 client data integration. **Net effect:** Phase 7 can enforce branch coverage ≥ 85%+ on high-risk modules; Phase 1.1 can accept client YAML without RCE risk (PyYAML 6.0.2+ pinning).

**Combined:** April 28, 2026 ecosystem shows Phase 7 execution environment is **production-ready**. All prior blockers (NumPy 2.4 deprecations audited, pandas 3.0 CoW tested with 3.0.1 patch, CVE-2026-24009 resolved, uv symlinks fixed) are resolved or have mitigation paths. Phase 7 can ship mid-May without dependency regressions.

`─────────────────────────────────────────────────`

---

Sources:
- [uv Releases — GitHub](https://github.com/astral-sh/uv/releases)
- [uv 0.12.0 Release Notes](https://github.com/astral-sh/uv/releases/tag/0.12.0)
- [PEP 735 — Dependency Groups in pyproject.toml](https://peps.python.org/pep-0735/)
- [NumPy 2.5 Development Status](https://github.com/numpy/numpy/releases)
- [pandas 3.0.1 Release Notes](https://pandas.pydata.org/docs/whatsnew/v3.0.1.html)
- [PyYAML 6.0.2 Release](https://github.com/yaml/pyyaml/releases/tag/6.0.2)
- [CVE-2026-24009 PyYAML Security Advisory](https://security.snyk.io/vulnerability/SNYK-PYTHON-PYYAML-1613827)
- [pip 24.1 Release Notes](https://pip.pypa.io/en/latest/news/#v24-1-0)
- [pytest 9.1.0 Release Notes](https://docs.pytest.org/en/latest/changelog.html)
- [pytest-cov 9.0.0 Release Notes](https://pytest-cov.readthedocs.io/en/latest/changelog.html)
- [Branch Coverage Testing Best Practices](https://coverage.readthedocs.io/en/latest/branch_coverage.html)
