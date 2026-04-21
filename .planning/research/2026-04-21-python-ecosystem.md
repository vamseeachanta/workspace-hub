# Research: python-ecosystem — 2026-04-21

## Key Findings

- **uv 0.11.7 (released April 15, 2026) includes CPython OpenSSL security upgrade and resolves RECORD validation issue** — wheels with malformed RECORD entries no longer cause arbitrary file deletion during uninstall. Stable release cadence maintained; all tier-1 repos should upgrade to post-0.9.0 for RECORD validation fix (security-critical). TLS certificate verification maturity continues from prior research; `--system-certs` flag handling normalized. **Workspace impact:** Phase 7 licensed-win-1 remote execution with `uv pip install` should use latest stable (0.11.7+) for certificate chain validation + RECORD security.

- **NumPy 2.4.0 (December 2025) expired six major deprecations affecting array operations; NumPy 2.5 development ongoing (no release yet).** Confirmed breaking changes: (1) `np.sum(generator)` now raises TypeError (deprecated since 1.15.0) — must refactor to `np.sum(np.fromiter())` or builtin `sum()`; (2) `np.round()` always returns copy (not view); (3) strides attribute mutation deprecated due to thread-safety concerns; (4) positional `out=` argument to `np.maximum`/`np.minimum` deprecated (must use keyword form); (5) ndim > 0 array conversion to scalar now raises TypeError. **New finding:** Deleting numpy from sys.modules and re-importing now fails during multi-phase initialization — impacts test fixtures that reload numpy. Type-checker rejection of `start=` keyword in `np.arange()` adds linting friction if using strict type checking. **Workspace impact:** Phase 1 (digitalmodel spectral fatigue, wall thickness, on-bottom stability) audit must verify no generator usage in array summation, no in-place rounding assumptions, no numpy module reloading in test fixtures.

- **pandas 3.0.0 (January 21, 2026) Copy-on-Write now mandatory; setting `pd.options.mode.copy_on_write` has zero effect in 3.0.0 (deprecation grace period expired).** Chained assignment `df["foo"][df["bar"] > 5] = 100` no longer works; must refactor to `.loc[df["bar"] > 5, "foo"] = 100`. String dtype now infers as `str` type (backed by PyArrow if installed, else NumPy object fallback) instead of numpy object — changes Parquet serialization behavior. **Workspace impact:** Phase 2 (worldenergydata Parquet pipelines, EIA/BSEE/SODIR data ingestion) + Phase 1 (digitalmodel DataFrames) audit for chained assignment patterns is **blocking item for v1.1**; test Parquet round-trip with string columns to validate dtype inference compatibility.

- **pytest-cov + coverage.py 7.13.5 (March 17, 2026) standardize threshold enforcement (90%+ gates) as production-standard for CI/CD; free-threading support added; roadmap includes AI-driven coverage gap suggestions.** Latest pytest stable: 9.0.3. Threshold gating now universally expected in edge computing/cloud-native workflows. No breaking changes to pytest-cov API; existing coverage configuration files compatible. **Workspace impact:** Phase 1–6 (completed with ~90.5% coverage for digitalmodel) already meet 2026 standards; Phase 7 smoke tests should leverage coverage threshold gating (90%+ minimum) in CI/CD to prevent regression.

- **CVE-2026-24009 (PyYAML "shadow vulnerability"): unsafe YAML deserialization via transitive dependencies** — RCE occurs when applications deserialize untrusted YAML using `yaml.load()` or `FullLoader`. Safe across all PyYAML versions: `yaml.safe_load()`, `yaml.safe_load_all()`, `SafeLoader` class. **Critical finding:** Vulnerability can hide in transitive dependencies (e.g., libraries internally using `yaml.load()`), bypassing direct code inspection. **Workspace impact:** Phase 5 nightly research automation + Phase 7 solver job configs accept YAML manifests — if Phase 1.1 extends to client-supplied OrcaFlex job files in YAML format, add schema validation (Pydantic models) **before** YAML deserialization to prevent RCE vector.

## Relevance to Project

| Finding | Affected Workflow / Package | Impact |
|---|---|---|
| **uv 0.11.7 RECORD validation + TLS maturity** | All tier-1 repos + Phase 7 remote execution infrastructure | Confirm all 4 machines running uv post-0.9.0 stable (0.11.7+); RECORD validation prevents silent file deletion on wheel uninstall (security-critical). Phase 7 dev-primary → licensed-win-1 execution uses latest `uv` binary — certificate validation stable, no deprecation friction with `--system-certs` vs. `--native-tls` (issue resolved in stable). Recommend uv version pinning in CI/CD gate scripts (>=0.11.7). |
| **NumPy 2.4 expired deprecations (generator, round, strides, out=, import reload)** | `digitalmodel` Phase 1 (spectral fatigue, wall thickness, on-bottom stability), Phase 7 smoke tests | **BLOCKING for v1.1 gate:** Audit all module imports for `np.sum(generator)` patterns (replace with `np.sum(np.fromiter())` or builtin); verify test fixtures don't reload numpy (will now fail with ImportError); check all `np.round()` calls assume copy semantics; remove positional `out=` arguments to `np.maximum`/`np.minimum` (use keyword form); update type-checker config for `np.arange(start=...)` to positional form. **Priority:** resolve before Phase 7 shipping to avoid silent test failures. |
| **pandas 3.0 Copy-on-Write mandatory + string dtype inference** | `worldenergydata` Phase 2 (Parquet pipelines), `digitalmodel` Phase 1 (calculation DataFrames) | **BLOCKING for v1.1 shipping.** Grep all repos for `df[...][...] = ` chained assignment (convert to `.loc[..., ...] = `); test Parquet write → read round-trip with string columns on pandas 3.0 to catch dtype inference changes; run full v1.0 test suite on pandas 3.0 (Phase 1–6 regression audit). Both Phase 1 + Phase 2 shipped in v1.0 — existing tests must pass with pandas 3.0 or full code refactoring required before Phase 7. **Timeline:** finish before Phase 7 planning finalized (mid-April 2026). |
| **pytest-cov 7.13.5 + coverage.py threshold gating standard** | All phase test suites (Phase 1–7), CI/CD gate scripts | Current coverage (v1.0 Phase 1–6: ~90.5% for digitalmodel, similar for other modules) meets 2026 standards. Phase 7 smoke tests should enforce 90%+ threshold in CI gate (fail build if coverage drops below). Free-threading support relevant if Phase 7 uses parallel agents (multi-thread execution on licensed-win-1). AI-driven coverage gap suggestions available in coverage.py — monitor for Phase 7 edge case analysis if solver verification uncovers gaps. |
| **CVE-2026-24009 PyYAML RCE via transitive dependencies** | Phase 5 YAML research manifests, Phase 7 solver job configs, future Phase 1.1 client data integration | **Immediate:** Grep all repos for `yaml.load()` without SafeLoader; audit transitive dependencies (npm/Python packages) for unsafe YAML usage. **If Phase 1.1 integrates client-supplied YAML** (OrcaFlex job files, vessel specifications): add Pydantic schema validation layer before any YAML deserialization to prevent RCE. Phase 5 nightly researchers + Phase 7 job config YAML are currently trusted inputs (no immediate risk), but document CVE-2026-24009 as blocker for client data integration. |

## Recommended Actions

- [ ] **Create GitHub issue** — `workspace-hub` + all tier-1 repos: Verify all 4 machines running `uv` >= 0.11.7 (RECORD validation + TLS maturity). Run Phase 7 smoke test on licensed-win-1 with current `uv` binary; confirm `uv pip install` succeeds with certificate chain validation. Document `uv` version pinning in CI/CD gate scripts (>=0.11.7). **Target:** complete before Phase 7 execution begins.

- [ ] **Create GitHub issue — BLOCKING for v1.1** — `digitalmodel`: Complete NumPy 2.4 deprecation audit; identify and refactor all `np.sum(generator)` → `np.sum(np.fromiter())` or builtin `sum()` calls; verify test fixtures don't reload numpy module; confirm all `np.round()` calls assume copy semantics (not view); remove positional `out=` from `np.maximum`/`np.minimum`; update type-checker configuration for `np.arange(start=...)` → positional form. Run Phase 1 test suite to validate all changes. **Priority:** resolve before Phase 7 gate.

- [ ] **Create GitHub issue — BLOCKING for v1.1** — `worldenergydata` + `digitalmodel`: Complete pandas 3.0 Copy-on-Write audit; grep for chained assignment `df[...][...] = ` → refactor all to `.loc[..., ...] = `; test Parquet write → read round-trip with string columns on pandas 3.0; run full v1.0 test suite (Phase 1–6 regression). Document CoW semantics in calculation DataFrame documentation. **Timeline:** finish before Phase 7 planning finalized.

- [ ] **Create GitHub issue** — `workspace-hub` CI/CD: Upgrade CI/CD gate scripts to require pytest-cov + coverage.py >= 7.13.5 (March 2026 versions); set threshold enforcement to 90%+ for Phase 7 smoke tests + all tier-1 repos. Document free-threading implications if Phase 7 uses multi-threaded agents (coverage.py 7.13.5 supports it). **Target:** Phase 7 smoke test infrastructure.

- [ ] **Create GitHub issue** — `workspace-hub`: Security audit: grep all code for `yaml.load()` without `SafeLoader`; audit transitive Python/npm dependencies for unsafe YAML deserialization patterns (CVE-2026-24009 shadow vulnerability). Document CVE-2026-24009 as prerequisite blocker for Phase 1.1 client data integration (OrcaFlex YAML job files). **Target:** pre-flight audit before client-facing features ship.

- [ ] **Promote to PROJECT.md** — Add under Current Milestone (v1.1 OrcaWave Automation): "Dependencies modernization (NumPy 2.4, pandas 3.0, pytest-cov/coverage.py March 2026 versions, uv 0.11.7+) **blocking for v1.1 shipping**. NumPy 2.4 audit + refactoring complete (generator summation, round semantics, test reload safety). pandas 3.0 CoW compatibility audit complete (chained assignment refactor, Parquet round-trip testing). pytest-cov/coverage.py threshold enforcement (90%+ gate) integrated in Phase 7 CI/CD. uv 0.11.7 deployed across all 4 machines (RECORD validation + TLS stability). CVE-2026-24009 (PyYAML RCE) audit complete; prerequisite for Phase 1.1 client data integration."

- [ ] **Promote to PROJECT.md** — Add note on DNV-RP-C203:2024 spectral fatigue: "DNV-RP-C203:2024 (October 2024) resolves 2016 inconsistencies where lower-grade curves outperformed higher ones (B1 curve behavior unchanged; C-curves significantly improved). Phase 1 spectral fatigue module uses 2016 curves (v1.0 baseline). Phase 1.1 upgrade to 2024 S-N curves affects all existing benchmark calculations (L00–L06 examples) — measure accuracy improvement (especially C-curves) as competitive differentiator vs. SkyCiv/TheNavalArch commodity tools. Upgrade repositions aceengineer as 'standards-current by default' (citing DNV-RP-C203:2024, not 2016)."

---

## Cross-Research Synthesis

**Three critical dependencies block v1.1 shipping:**

1. **NumPy 2.4 expired deprecations** (generator summation, round semantics, strides mutation, import reload) affect **Phase 1 completed calculation modules** — spectral fatigue, wall thickness, on-bottom stability. **Blocking:** Must audit + refactor before Phase 7 shipping.

2. **pandas 3.0 Copy-on-Write mandatory** (chained assignment broken, string dtype inference) affects **Phase 2 completed Parquet pipelines** (EIA/BSEE/SODIR data ingestion) + **Phase 1 calculation DataFrames**. **Blocking:** Must validate full v1.0 test suite on pandas 3.0 before Phase 7 shipping.

3. **pytest-cov + coverage.py March 2026 threshold gating** establishes 90%+ enforcement as production-standard. Phase 7 smoke tests should leverage automated regression detection via coverage gates.

**Net effect:** v1.1 OrcaWave Automation ship gate requires resolution of three dependency breaking changes (NumPy, pandas, pytest infrastructure) **before Phase 7 planning finalized** (mid-April 2026). Once resolved, Phase 7 executes against modernized dependency stack with reduced runtime edge cases (uv 0.11.7+ security hardening, NumPy/pandas compatibility verified).

---

Sources:
- [uv Releases — GitHub](https://github.com/astral-sh/uv/releases)
- [uv CHANGELOG — GitHub](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)
- [uv Documentation](https://docs.astral.sh/uv/)
- [NumPy 2.4.0 Release Notes](https://numpy.org/devdocs/release/2.4.0-notes.html)
- [NumPy 2.0 Migration Guide](https://numpy.org/devdocs/numpy_2_0_migration_guide.html)
- [NumPy Release Notes Archive](https://numpy.org/doc/stable/release.html)
- [pandas 3.0.0 What's New (January 21, 2026)](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
- [Pandas 3.0 Released Announcement](https://pandas.pydata.org/community/blog/pandas-3-0.html)
- [Coverage.py Documentation — 7.13.5](https://coverage.readthedocs.io/)
- [pytest-cov — PyPI](https://pypi.org/project/pytest-cov/)
- [pytest-cov GitHub Repository](https://github.com/pytest-dev/pytest-cov)
- [Coverage.py PyTest Plugin: Threshold Enforcement in CI 2026](https://johal.in/coverage-py-pytest-plugin-threshold-enforcement-in-ci-2026/)
- [A Shadow Vulnerability Introduced via PyYAML (CVE-2026-24009)](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)
- [PyYAML Security Vulnerabilities — Snyk](https://security.snyk.io/package/pip/pyyaml)
- [DNV-RP-C203 Fatigue Design of Offshore Steel Structures](https://www.dnv.com/energy/standards-guidelines/dnv-rp-c203-fatigue-design-of-offshore-steel-structures/)
- [DNV-RP-C203 2024 vs 2016 Benchmark Comparison](https://sdcverifier.com/benchmarks/dnv-rp-c203-fatigue-comparison-2016-vs-2024/)
- [ASME B31.4 Pipeline Wall Thickness Calculation](https://epcmholdings.com/asme-b31-4-pipeline-wall-thickness-calculation/)
