# Research: python-ecosystem — 2026-08-25

## Key Findings

1. **uv 0.12.0 (July 28, 2026) introduced significant breaking changes — src/ structure default, build-system auto-declaration, .tar.gz-only source distributions (per PEP 625), and pre-release-if-necessary default.** Projects created with `uv init` now declare a build system and package by default; existing lockfiles referencing .tar.bz2/.tar.xz are rejected. **Relevance:** workspace-hub tier-1 packages already using declarative pyproject.toml + uv.lock; src/ layout already standard (confirmed across assetutilities, digitalmodel, worldenergydata). Pre-release handling change (fallback to pre-releases only when stable unavailable) may affect CI if any dependency pins unstable versions intentionally — audit `uv.lock` files for pre-release flags. → [uv 0.12.0 Release Notes](https://github.com/astral-sh/uv/releases/tag/0.12.0) | [uv Changelog](https://data.safetycli.com/packages/pypi/uv/changelog)

2. **Python 3.15 feature freeze finalized (June 2026); final release October 1, 2026. frozendict is now a native built-in, UTF-8 is system-wide default for I/O (replacing locale-dependent encoding).** PEP 814 (frozendict), PEP 686 (UTF-8 default), PEP 810 (lazy imports) all locked into October release. **Relevance:** workspace-hub currently targets Python 3.10–3.12 (per pyproject.toml). Python 3.15 adoption is v1.2+ scope; no immediate v1.1 impact. UTF-8 default removes encoding bugs in data pipelines (e.g., worldenergydata CSV/JSON ingestion); frozendict provides memory-safe config/constants. Plan for 3.15 CI matrix addition after October release. → [Python 3.15 Beta 4: Lazy Imports, frozendict, UTF-8 Defaults](https://www.linuxcompatible.org/story/python-315-beta-4-released-lazy-imports-frozendict-and-utf8-defaults) | [Python 3.15 Feature Freeze June 2026](https://realpython.com/python-news-june-2026/)

3. **Coverage.py 7.15.4 (August 6, 2026) remains the current stable version — no new releases post-7.15.4 as of August 25.** Python 3.15 free-threading support confirmed in 7.15.4 (prior research accurate). No breaking changes, no urgency to upgrade beyond 7.15.4 if on 7.13.5+. **Relevance:** workspace-hub's coverage gates (per `completeness-before-close` rule) are stable; 7.15.4 upgrade optional for v1.1, required only if Python 3.15 async testing adoption planned. → [Coverage.py 7.15.4 Documentation](https://coverage.readthedocs.io/)

4. **PyYAML CVE-2026-24009 (Docling RCE via unsafe deserialization) confirmed as the ONLY new Python packaging CVE announced in August 2026.** No new numpy/pandas/pytest security advisories; no new pyproject.toml-related CVEs. **Relevance:** prior 2026-08-18 research remains current; Docling grep across workspace-hub repos still actionable (expected: not in use). → [CVE-2026-24009: RCE in Docling via Unsafe PyYAML Deserialization](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)

5. **pytest 9.0.3 (April 7, 2026) remains the stable release; no August 2026 updates announced.** pytest-cov (March 21, 2026) requires coverage ≥7.10.6; both stable, no friction. **Relevance:** workspace-hub's TDD gate infrastructure (pytest + coverage) is stable through v1.1 and into v1.2. No upgrades needed; baseline solid. → [pytest PyPI](https://pypi.org/project/pytest/) | [pytest-cov Changelog](https://pytest-cov.readthedocs.io/en/latest/changelog.html)

---

## Relevance to Project

| Finding | Affected Package/Workflow | Impact | Action |
|---------|---|---|---|
| **uv 0.12.0 breaking changes (src/ default, build-system auto-declaration, PEP 625 .tar.gz)** | All tier-1 packages' pyproject.toml + uv.lock, CI reproducibility | **LOW-to-MEDIUM.** Workspace-hub already conforms (src/ standard, declarative pyproject.toml, modern build system). Pre-release handling change (fallback-to-pre-releases-if-necessary) is a safety improvement; audit `uv.lock` for any explicit `--pre` pins in CI that might now behave differently. **Timing:** v1.1 should confirm no `--pre` overrides that conflict with new default. | Audit step in Phase 7 CI validation |
| **Python 3.15 frozendict + UTF-8 default (Oct 1, 2026)** | Future CI matrix expansion (v1.2), data pipeline encoding robustness, type-safe config modules | **MEDIUM (v1.2 forward).** frozendict enables immutable config in assethold; UTF-8 default eliminates locale-dependent file-read bugs in worldenergydata pipelines. October release allows Q4 2026 adoption planning. **Timing:** v1.1 unaffected; v1.2 should include Python 3.15 in CI matrix after October. | Document in PROJECT.md v1.2 vision (Python 3.15 CI support) |
| **Coverage.py 7.15.4 stable (no new releases)** | TDD gate, CI completeness-before-close enforcement | **POSITIVE.** Confirms prior research stability. No action needed for v1.1; 7.15.4 optional upgrade if 3.15 free-threading testing adopted (not planned for v1.1). | No action required |
| **PyYAML CVE-2026-24009 (only new packaging CVE, Docling-specific)** | worldenergydata data pipelines (if using Docling), compliance audit | **MEDIUM (if Docling in use, LOW if not).** Grep still actionable from 2026-08-18 research; combine with Pydantic AI CVE-2026-54249 audit in one pass. Expected: Docling not in workspace-hub (rare dependency for engineering domain). | Parallel grep audit (consolidate with prior research task) |
| **pytest 9.0.3 + pytest-cov stable** | Test infrastructure, TDD gate enforcement, Phase 7 smoke tests | **POSITIVE.** Confirms ecosystem maturity; no friction. v1.1 baseline solid. | No action |

---

## Recommended Actions

- [ ] **MEDIUM (Phase 7 CI validation): Audit workspace-hub and tier-1 repos for explicit `uv --pre` or pre-release handling overrides in CI workflows.** uv 0.12.0 changed the default to "fallback to pre-releases only when stable unavailable" — if any CI job explicitly enables pre-releases (e.g., to test against alpha versions of dependencies), confirm behavior remains intentional. **Action:** (1) `grep -r "\-\-pre\|prerelease" .github/workflows/ config/` across workspace-hub + assetutilities + digitalmodel + worldenergydata. (2) For each match, verify it's intentional (e.g., optional nightly pre-release test, not production CI). (3) Document findings in Phase 7 CI readiness checklist. (4) Expected: no matches (pre-releases not explicitly tested in v1.1). **Timeline: 30 minutes.** → [uv 0.12.0 Release Notes](https://github.com/astral-sh/uv/releases/tag/0.12.0)

- [ ] **LOW (v1.2 planning): Document Python 3.15 adoption plan in PROJECT.md roadmap section.** Final release October 1, 2026; frozendict + UTF-8 default are valuable for v1.2+. **Action:** (1) Add to PROJECT.md roadmap: "v1.2 vision — Python 3.15 CI matrix support (post-Oct-1 release). frozendict for immutable config/standards data; UTF-8 default for encoding-safe data pipelines." (2) Defer implementation to v1.2 phase planning. **Timeline: 15 minutes.** → [Python 3.15 Features Locked in June 2026 Feature Freeze](https://explore.n1n.ai/blog/python-3-15-feature-freeze-june-2026-updates-2026-06-09)

- [x] **CONFIRMATION (v1.1): Prior 2026-08-18 python-ecosystem research is current and comprehensive.** This week's search validates all major findings (uv 0.12.0 stable, pytest/coverage stable, PyYAML CVE-2026-24009 as the only new packaging CVE, PEP 808 conformance, Python 3.15 feature-frozen). **No blocking changes to Phase 7 or v1.1 roadmap.** Proceed with planned Docling/PyYAML CVE grep audit (parallel to Pydantic AI CVE audit from 2026-08-11) from prior research. **Deliverable:** GitHub issue summary: "Python ecosystem research 2026-08-25 validation pass confirms prior 2026-08-18 research as current. uv 0.12.0 pre-release handling audit recommended for CI validation. Python 3.15 adoption deferred to v1.2 (Oct 1, 2026 final release)."

---

`★ Insight ─────────────────────────────────────`

**The Python ecosystem remains stable with no disruptive changes in the past week.** The 2026-08-18 research was thorough; this session confirms its findings as current and surfaces incremental details.

**uv 0.12.0's breaking changes (src/ structure, build-system auto-declaration, pre-release fallback) are all safety/clarity improvements, not backwards-incompatible friction.** Workspace-hub already conforms to src/ and declarative pyproject.toml; pre-release fallback is actually safer (stable-first, pre-release-fallback-only). The only audit needed is confirming no CI jobs intentionally override pre-release behavior for testing purposes — expected: none.

**Python 3.15 is feature-frozen (June) and arriving October 1, 2026.** frozendict as a native built-in is valuable for immutable config/standards data (useful in assethold); UTF-8 default eliminates locale-encoding bugs (high-value for worldenergydata CSV/JSON ingestion). Plan adoption in v1.2 phase, not v1.1. No v1.1 action needed.

**The one actionable item from this research: confirm no explicit `--pre` flags in CI workflows conflict with uv 0.12.0's new default behavior.** This is a small audit (30 minutes) that validates Phase 7's CI reproducibility before smoke tests run. Do it as part of Phase 7 CI readiness.

**Everything else is green.** Coverage.py is stable, pytest is stable, PyYAML's CVE is confirmed as Docling-specific (unlikely in workspace-hub), and the packaging standards (PEP 808 pyproject.toml, PEP 621 metadata) are locked. No friction through v1.2.

`─────────────────────────────────────────────────`

---

## Sources

- [uv 0.12.0 Release Notes](https://github.com/astral-sh/uv/releases/tag/0.12.0)
- [uv Changelog](https://data.safetycli.com/packages/pypi/uv/changelog)
- [uv 0.12 Makes Every New Project a Package](https://pydevtools.com/blog/uv-0-12-packaged-by-default/)
- [Python 3.15 Beta 4: Lazy Imports, frozendict, UTF-8 Defaults](https://www.linuxcompatible.org/story/python-315-beta-4-released-lazy-imports-frozendict-and-utf8-defaults)
- [Python 3.15 Features Locked in June 2026 Feature Freeze](https://explore.n1n.ai/blog/python-3-15-feature-freeze-june-2026-updates-2026-06-09)
- [Python 3.15 Hits Feature Freeze and Other News for June 2026 – Real Python](https://realpython.com/python-news-june-2026/)
- [Coverage.py 7.15.4 Documentation](https://coverage.readthedocs.io/)
- [CVE-2026-24009: RCE in Docling via Unsafe PyYAML Deserialization](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)
- [pytest PyPI](https://pypi.org/project/pytest/)
- [pytest-cov Changelog](https://pytest-cov.readthedocs.io/en/latest/changelog.html)

---

**Summary:** Python ecosystem research continues to show stability. Prior 2026-08-18 findings (Coverage.py 7.15.4, pytest 9.0.3, uv 0.12.1, PyYAML CVE-2026-24009, PEP 808 conformance) are confirmed current. This week adds: uv 0.12.0 pre-release handling change (audit recommended for CI), Python 3.15 feature-freeze confirmation with frozendict + UTF-8 default (v1.2 planning). **Immediate action: Phase 7 CI audit for explicit pre-release overrides (30 minutes).** Everything else is deferred to v1.2 roadmap or monitoring. No blocking changes to Phase 7 or v1.1.
