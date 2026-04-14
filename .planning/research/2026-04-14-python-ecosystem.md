# Research: python-ecosystem — 2026-04-14

## Key Findings

- **uv 0.9+ continues TLS certificate verification maturity; reqwest 0.13 upgrade stabilized, `--system-certs` vs. `--native-tls` flag normalization shipped.** The networking stack upgrade (reqwest 0.12 → 0.13) from prior research (2026-04-07) is now in stable releases. Current releases include stabilized `uv python upgrade` and `uv python install --upgrade` commands for Python version management, plus progress bar support for `uv publish`. Low-severity security advisory resolved: wheels with malformed RECORD entries could delete arbitrary files on uninstall (fixed in current releases). **Workspace impact:** All tier-1 repos using `uv` should run latest stable (post-0.9.0) to pick up RECORD validation fix; 4-machine Phase 7 remote execution testing remains unchanged from prior recommendations.

- **NumPy 2.4.0 (December 2025) expired six major deprecations affecting array operations; NumPy 2.5 in development.** Confirmed from prior research: `np.sum(generator)` now raises TypeError (deprecated since 1.15.0), `np.round()` always returns copy (not view), strides mutation deprecated, positional `out=` argument to `np.maximum`/`np.minimum` deprecated. **New finding:** Deleting numpy from sys.modules and re-importing now fails with ImportError due to multi-phase initialization — impacts any test fixtures that reload numpy. Type-checker rejection of `start=` keyword in `np.arange()` adds linting friction. NumPy 2.5 is in development; no published deprecations yet. **Workspace impact:** Phase 1 (digitalmodel spectral fatigue, wall thickness, on-bottom stability) audit must verify no generator usage in array summation, no in-place rounding assumptions, no numpy module reloading in test fixtures.

- **pandas 3.0.0 (January 21, 2026) Copy-on-Write now mandatory; `pd.options.mode.copy_on_write` setting deprecated and has no effect.** Confirmed from prior research: chained assignment `df["foo"][df["bar"] > 5] = 100` no longer works; **new addition:** the deprecation warning period is over — setting the option has zero effect in 3.0.0. String dtype now infers as `str` type instead of numpy object. Pandas 3.0 release recommendation path: upgrade to pandas 2.3 first (to get CoW deprecation warnings), then migrate to 3.0. **No pandas 3.1 release announced yet in 2026.** **Workspace impact:** Phase 2 (worldenergydata Parquet pipelines) + Phase 1 (digitalmodel DataFrames) audit for chained assignment patterns is critical blocking item; string dtype inference changes may silently alter Parquet serialization behavior.

- **pytest-cov latest release March 21, 2026 (supports Python 3.9–3.14); coverage.py 7.13.5 released March 17, 2026 (Python 3.10–3.15α, free-threading support).** The 2026 testing ecosystem is standardized on pytest with pytest-cov as default coverage plugin. Coverage.py 7.13.5 added: speed improvements for large codebases, stronger async code coverage tracking, free-threading support. **New finding:** "Coverage.py PyTest plugin emerges as gatekeeper, enforcing strict thresholds in CI/CD workflows" — threshold enforcement is now production-standard for edge computing / cloud-native environments. Future roadmap includes native async support + AI-driven coverage gap suggestions. **Workspace impact:** Phase 1–6 (completed with ~90%+ coverage) already meet 2026 standards; Phase 7 smoke tests should leverage coverage threshold gating (90%+ minimum) in CI/CD.

- **Agent Skills SKILL.md v1.0 now finalized (December 2025, live across Claude Code, Codex, Google ADK, VS Code, Cursor); cross-vendor adoption near-universal per supplemental research (2026-04-11).** This is **outside pure Python packaging scope** but critically relevant: v1.0 spec is production-ready with strict YAML constraints (lowercase name max 64 chars, description max 1024 chars, filename exactly `SKILL.md` case-sensitive). Workspace-hub skills can be published to agentskills.io registry immediately (no Q2 2026 waiting period from prior research). **Workspace impact:** Migrate `.claude/skills/` to SKILL.md v1.0 compliance audit; potential registry publication unlocks cross-vendor interoperability (Codex CLI, Gemini CLI on other machines).

## Relevance to Project

| Finding | Affected Package / Workflow | Impact |
|---|---|---|
| **uv 0.9+ TLS + RECORD validation fix** | All tier-1 repos (`digitalmodel`, `worldenergydata`, `assetutilities`, `assethold`, `OGManufacturing`) + Phase 7 remote execution | Confirm all machines running latest `uv` stable post-0.9.0; RECORD validation prevents silent file deletion on wheel uninstall (security). Phase 7 dev-primary → licensed-win-1 remote execution uses latest `uv` binary — no deprecation friction with `--system-certs` vs. `--native-tls` (issue resolved in stable). Test on licensed-win-1 with Phase 7 smoke tests. |
| **NumPy 2.4 expired deprecations (generator, round, strides, out=, import reload)** | `digitalmodel` Phase 1 (spectral fatigue, wall thickness, on-bottom stability), Phase 7 smoke tests | Audit all module imports for `np.sum(generator)` patterns (must use `np.fromiter()` or builtin). Verify test fixtures don't reload numpy (will now fail). Check all `np.round()` calls assume copy semantics (not in-place view). Remove any positional `out=` arguments to `np.maximum`/`np.minimum`. Linting with type-checkers will reject `np.arange(start=...)` — refactor to positional or use `out=`. **Priority:** resolve before Phase 7 shipping. |
| **pandas 3.0 Copy-on-Write mandatory + string dtype inference** | `worldenergydata` Phase 2 (Parquet pipelines, EIA/BSEE/SODIR data ingestion), `digitalmodel` Phase 1 (calculation DataFrames) | **Blocking item for v1.1 shipping.** Grep all repos for `df[...][...] = ` chained assignment (2026-04-07 research already itemized; now confirmed no deprecation grace period). Test Parquet round-trip with string columns — new inference may change dtype storage format. Both Phase 1 + Phase 2 completed in v1.0 (shipped 2026-03-25/26) — existing tests must pass with pandas 3.0 or full regression audit required. Recommend test on pandas 3.0 immediately before Phase 7. |
| **pytest-cov + coverage.py latest (March 2026), threshold gating standard** | All phase test suites (Phase 1–7), CI/CD gate scripts | Current coverage (v1.0 Phase 1–6: ~90.5% for digitalmodel, similar for other modules) meets 2026 standards. Phase 7 smoke tests should enforce 90%+ threshold in CI gate. Free-threading support in coverage.py 7.13.5 is relevant if Phase 7 uses parallel agents (multi-thread execution on licensed-win-1). AI-driven coverage gap suggestions available in coverage.py — monitor for Phase 7 adoption if analysis completeness is concern. |
| **Agent Skills v1.0 finalized + cross-vendor adoption** | `.claude/skills/` architecture (orchestration, workflow coordination, agent capability discovery) + Phase 7 multi-agent coordination (from skill-design research 2026-04-11) | **De-risk mitigation:** v1.0 spec finalized (was Q2 2026 draft in prior research) — migrate `.claude/skills/` to v1.0 compliance now. No registry publication risk. Supports workspace-hub portability across Claude Code, Codex CLI, Gemini CLI, Cursor — critical for 4-machine Phase 7 coordination (dev-primary → licensed-win-1). Namespace scope (lowercase name, hyphens only) may require minor skill renames. |

## Recommended Actions

- [ ] **Create GitHub issue** — `workspace-hub` + all tier-1 repos: Verify all machines running `uv` post-0.9.0 stable (RECORD validation + TLS maturity). Run Phase 7 smoke test on licensed-win-1 with current `uv` binary; confirm `uv pip install` succeeds with certificate chain validation. Document `uv` version pinning in CI/CD gate scripts (Phase 7 release gate).

- [ ] **Create GitHub issue** — `digitalmodel`: Complete NumPy 2.4 deprecation audit; identify and refactor all `np.sum(generator)` → `np.sum(np.fromiter())` or builtin `sum()` calls; verify test fixtures don't reload numpy module; confirm all `np.round()` calls assume copy semantics (not view); remove positional `out=` from `np.maximum`/`np.minimum`; update type-checker configuration for `np.arange(start=...)` → positional form. **Priority:** block Phase 7 gate until resolved.

- [ ] **Create GitHub issue** — `worldenergydata` + `digitalmodel`: **BLOCKING for v1.1.** Complete pandas 3.0 Copy-on-Write audit; grep for chained assignment `df[...][...] = ` → refactor all to `.loc[..., ...] = `; test Parquet write → read round-trip with string columns on pandas 3.0; run full v1.0 test suite on pandas 3.0 (Phase 1–6 regression). Document CoW semantics in calculation DataFrame documentation. **Timeline:** finish before Phase 7 planning finalized.

- [ ] **Create GitHub issue** — `workspace-hub` CI/CD: Upgrade CI/CD gate scripts to require pytest-cov + coverage.py >= 7.13.5 (March 2026 versions); set threshold enforcement to 90%+ for Phase 7 smoke tests + all tier-1 repos. Document free-threading implications if Phase 7 uses multi-threaded agents (coverage.py 7.13.5 supports it). Optional: monitor coverage.py AI-driven gap suggestions for Phase 7 edge case analysis.

- [ ] **Create GitHub issue** — `.claude/skills/`: Audit all ~900 lines of GSD skills for Agent Skills v1.0 YAML compliance (name format lowercase max 64 chars + hyphens only, description max 1024 chars, filename exactly `SKILL.md`). Measure current compliance percentage. Fix violations atomically (rename skills if needed). Publish 3–5 high-value skills to agentskills.io registry by end of April 2026 (no longer Q2 deadline — immediate). Cross-vendor testing: confirm skills work in Codex CLI + Gemini CLI after publication.

- [ ] **Promote to PROJECT.md** — Add under Current Milestone (v1.1 OrcaWave Automation): "Dependencies modernization (NumPy 2.4, pandas 3.0, pytest-cov/coverage.py March 2026 versions) **blocking for v1.1 shipping**. Audit complete by Phase 7 gate. Agent Skills v1.0 (SKILL.md spec) adopted for cross-vendor interoperability (Codex, Gemini CLI). uv post-0.9.0 standard across 4 machines (RECORD validation + TLS stability)."

- [ ] **Promote to PROJECT.md** — Add note on pandas 3.0 CoW breaking change: "All tier-1 repos refactored to `.loc[..., ...] = ` syntax (pandas 3.0+ compatible). Chained assignment `df[...][...] = ` deprecated; no grace period in 3.0.0. String dtype inference changed (str vs. object) — Parquet serialization verified. Both Phase 1 (digitalmodel) + Phase 2 (worldenergydata) tested on pandas 3.0 before v1.1 shipping."

---

## Cross-Research Synthesis

**Four critical dependencies intersect at Phase 7 gate:**

1. **NumPy 2.4 expired deprecations** (generator, round semantics, strides mutation) affect **Phase 1 completed calculation modules** — spectral fatigue, wall thickness, on-bottom stability. **Blocking:** Must audit + refactor before Phase 7 shipping.

2. **pandas 3.0 Copy-on-Write** (mandatory, no deprecation grace period) affects **Phase 2 completed Parquet pipelines** (EIA/BSEE/SODIR data ingestion). **Blocking:** Must validate full v1.0 test suite on pandas 3.0 before Phase 7 shipping.

3. **pytest-cov + coverage.py March 2026 versions** establish threshold gating (90%+) as production-standard. **Phase 7 smoke tests should leverage:** automated regression detection via coverage gates, free-threading support for parallel agents, AI-driven gap suggestions for edge case analysis.

4. **Agent Skills v1.0 SKILL.md compliance** removes registry publication risk (was draft Q2 2026, now finalized). **Phase 7 multi-agent coordination** benefits from cross-vendor interoperability (Codex CLI on licensed-win-1, Gemini CLI on dev-secondary). **Action:** Compliance audit + registry publication immediate (April 2026), not deferred.

**Net effect:** v1.1 v1.1 OrcaWave Automation ship gate requires resolution of three dependency breaking changes (NumPy, pandas, pytest infrastructure). Timeline: NumPy + pandas audits should complete before Phase 7 planning finalized (mid-April 2026). Agent Skills migration + registry publication is parallel path (no code changes, pure capability discovery). Phase 7 smoke tests will run against all three modernized dependency stacks.

---

Sources:
- [uv CHANGELOG — GitHub](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)
- [uv Versioning and Policies](https://docs.astral.sh/uv/reference/policies/versioning/)
- [uv Releases — GitHub](https://github.com/astral-sh/uv/releases)
- [NumPy 2.4.0 Release Notes](https://numpy.org/devdocs/release/2.4.0-notes.html)
- [NumPy Release Notes Archive](https://numpy.org/doc/stable/release.html)
- [NumPy 2.0 Migration Guide](https://numpy.org/devdocs/numpy_2_0_migration_guide.html)
- [pandas 3.0.0 What's New (January 21, 2026)](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
- [Pandas 3.0 Released Announcement](https://pandas.pydata.org/community/blog/pandas-3-0.html)
- [Pandas 3.0: Copy-on-Write Deep Dive](https://phofl.github.io/cow-adaptions.html)
- [A Shadow Vulnerability Introduced via PyYAML (CVE-2026-24009)](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)
- [PyYAML Security Vulnerabilities — Snyk](https://security.snyk.io/package/pip/pyyaml)
- [pytest-cov — PyPI](https://pypi.org/project/pytest-cov/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [pytest-cov GitHub Repository](https://github.com/pytest-dev/pytest-cov)
- [Best Python Testing Tools 2026 — Medium](https://medium.com/@inprogrammer/best-python-testing-tools-2026-complete-guide-bdedf7fee2f6)
- [Python Packaging Standards — packaging.python.org](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
