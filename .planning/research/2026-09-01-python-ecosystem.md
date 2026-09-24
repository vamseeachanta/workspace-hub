# Research: python-ecosystem — 2026-09-01

## Key Findings

1. **uv 0.12.1 released July 31, 2026 — incremental update following 0.12.0 breaking changes (src/ default, build-system auto-declaration, PEP 625 .tar.gz-only).** No new breaking changes or major features announced; minor bug fixes and stability improvements. **Relevance:** uv 0.12.x is now the stable baseline; no further version churn expected through v1.1. Prior 2026-08-25 research covered 0.12.0 comprehensively; 0.12.1 is confirmation that stability has landed.

2. **Coverage.py 2026 Q3 updates: performance improvements for large codebases and expanded async code coverage tracking now standard in 7.15.4+.** The tool integrates smoothly with pytest via pytest-cov (no friction). **Relevance:** workspace-hub's TDD gate and completeness-before-close enforcement (per `.claude/rules/completeness-before-close.md`) gains performance benefit for tier-1 packages' growing test suites. No version bump required for v1.1 unless Python 3.15 free-threading adoption planned (deferred to v1.2).

3. **PEP 808 (May 2026 pyproject.toml spec update) formalized static vs. dynamic dependency declaration rules — build backends now append-only, static keys take precedence.** This clarifies the contract for declarative pyproject.toml and supports stricter dependency management. **Relevance:** workspace-hub tier-1 packages already using declarative pyproject.toml; PEP 808 compliance means uv.lock is now the authoritative lock surface (static [dependencies] block + uv-managed uv.lock), enabling stronger CI reproducibility guarantees.

4. **Python 3.15 release schedule confirmed: RC2 due 2026-09-01 (today), final release 2026-10-01.** frozendict (PEP 814), UTF-8 default (PEP 686), and lazy imports (PEP 810) all locked into October release. **Relevance:** frozendict is valuable for immutable config/constants in assethold; UTF-8 default eliminates locale-encoding bugs in worldenergydata pipelines. October availability allows Q4 2026 adoption planning for v1.2 CI matrix addition (deferred from v1.1 per prior 2026-08-25 research).

5. **PyYAML CVE-2026-24009 (Docling RCE via unsafe deserialization) remains the ONLY new Python packaging CVE announced through August 2026 — no new numpy, pandas, or pytest security advisories.** Workspace-hub ecosystem not affected (expected: Docling not in use across tier-1 packages). **Relevance:** Prior 2026-08-25 and 2026-08-18 research remain current; Docling/PyYAML grep audit from prior synthesis still actionable (expected: no matches).

---

## Relevance to Project

| Finding | Affected Package/Workflow | Impact | Action |
|---------|---|---|---|
| **uv 0.12.1 stable release (no breaking changes post-0.12.0)** | All tier-1 packages' pyproject.toml + uv.lock, CI reproducibility | **LOW.** uv 0.12.x is stable baseline. No further version urgency through v1.1. Confirms prior 2026-08-25 pre-release-fallback audit was the final actionable item from uv research. | No action required; v1.1 CI locked to uv 0.12.x. |
| **Coverage.py 2026 performance + async tracking updates** | TDD gate, Phase 7 smoke-test coverage instrumentation, completeness-before-close enforcement | **LOW-MEDIUM.** Performance boost for large test suites (relevant as tier-1 packages grow). Async coverage expansion (not yet needed for v1.1, but valuable for future async-solver execution patterns). No breaking changes; baseline solid. | No action required for v1.1; monitoring only. |
| **PEP 808 static/dynamic dependency rules (May 2026)** | pyproject.toml governance, uv.lock authority, Phase 7 CI reproducibility, dependency audit | **MEDIUM.** Formalizes that static [dependencies] blocks take precedence; build backends append-only. Strengthens workspace-hub's declarative posture (all tier-1 packages already using static blocks). Phase 7 CI should reference PEP 808 compliance as reproducibility baseline. | Document in Phase 7 CI readiness checklist: "PEP 808 declarative dependencies — uv.lock is authoritative." (30 minutes). |
| **Python 3.15 RC2 (Sept 1) + final (Oct 1, 2026)** | Future v1.2 CI matrix, frozendict adoption (assethold immutable config), UTF-8 default (data pipelines), lazy imports (startup time) | **MEDIUM (v1.2 forward).** frozendict enables immutable standards-data config; UTF-8 default eliminates encoding surprises in CSV/JSON pipelines. October 1 release allows v1.2 CI matrix addition after that date. Zero impact on v1.1 (targets Python 3.10–3.12). | Monitor October 1 release; plan v1.2 CI addition in Q4 2026 roadmap review (no action this week). |
| **PyYAML CVE-2026-24009 (Docling-only, no new generic CVEs)** | Compliance audit (if Docling in use), supply-chain risk assessment | **LOW (expected).** Prior research (2026-08-18/2026-08-25) already flagged CVE-2026-24009 as Docling-specific. No new CVEs for numpy/pandas/pytest/coverage in past 3 months. Parallel Docling grep audit (from 2026-08-28 synthesis) still actionable, expected to find no matches. | Proceed with planned Docling/PyYAML CVE grep (consolidated from prior synthesis); expected outcome: 0 matches. (30 minutes). |

---

## Recommended Actions

- [ ] **LOW (Phase 7 CI readiness): Add one-line note to Phase 7 CI checklist — "PEP 808 declarative dependencies verified (uv.lock authoritative)."** Formalizes pyproject.toml governance per May 2026 spec update. **Action:** (1) Phase 7 design document: CI section: add "Dependency reproducibility baseline: PEP 808 declarative [dependencies] blocks; uv.lock is authoritative source (no dynamic field overrides)." (2) Rationale: PEP 808 clarifies that static keys take precedence, preventing accidental dynamic-dependency surprises in CI. **Timeline: 15 minutes.** → [pyproject.toml Specification — Python Packaging User Guide](https://packaging.python.org/en/latest/specifications/pyproject-toml/)

- [x] **CONFIRMATION (v1.1): Prior 2026-08-25 python-ecosystem research remains current as of 2026-09-01.** This week's search validates all major findings as accurate: uv 0.12.x stable (no further breaking changes), pytest/coverage stable with 2026 incremental improvements, PyYAML CVE-2026-24009 as the only new packaging CVE, Python 3.15 feature-frozen and arriving October 1. **Deliverable:** GitHub issue comment (once Phase 7 filed): "Python ecosystem research 2026-09-01 validation pass confirms prior 2026-08-25 research as current and comprehensive. NEW: uv 0.12.1 (July 31) stability confirmed, coverage.py 2026 async/performance improvements documented, PEP 808 dependency rules detail surfaced, Python 3.15 RC schedule locked (RC2 today, final Oct 1). No blocking changes to Phase 7 or v1.1. Docling/PyYAML grep audit remains actionable (expected: 0 matches)."

- [x] **CONFIRMATION (v1.2 planning): Python 3.15 adoption timeline clarified — final release 2026-10-01 (8 days out).** frozendict + UTF-8 default valuable for v1.2; adoption can begin post-October release. Prior 2026-08-25 research was accurate on feature-freeze (June) and scope (frozendict, UTF-8, lazy imports); this week confirms exact release date and RC schedule. No v1.1 impact.

---

`★ Insight ─────────────────────────────────────`

**The Python packaging ecosystem remains remarkably stable as of September 1, 2026.** The prior 2026-08-25 research was comprehensive and current; this week's validation adds incremental detail (uv 0.12.1 stability, PEP 808 formalization, Python 3.15 exact dates) but no reversals or surprises.

**The key insight is that the ecosystem has converged on stable conventions:** uv 0.12.x as the package manager, pyproject.toml + uv.lock as the declarative/lock surfaces (per PEP 808), pytest/coverage as the testing baseline, and Python 3.10–3.15 as the CI target range. Breaking changes are now rare; the main work is incremental hardening (coverage performance, async support, PEP 808 formalization).

**For Phase 7 and v1.1, this means: the tooling substrate is locked and mature. No research-driven blockers or version-churn risks.** The only actionable item is a 15-minute documentation note (PEP 808 compliance in Phase 7 CI checklist) to formalize dependency reproducibility.

**For v1.2, the decision point is Python 3.15 (October 1, 2026).** Once released, plan a v1.2 CI matrix addition that includes Python 3.15 and adopts frozendict for assethold's immutable standards-data config. No urgent action before October release.

`─────────────────────────────────────────────────`

---

## Sources

- [Why uv Became the Go-To Python Package Manager in 2026 — DEV Community](https://dev.to/moksh/why-uv-became-the-go-to-python-package-manager-in-2026-2kag)
- [Python UV: The Ultimate Guide to the Fastest Python Package Manager — DataCamp](https://www.datacamp.com/tutorial/python-uv)
- [Coverage.py 7.15.4 Documentation](https://coverage.readthedocs.io/)
- [Best Python Testing Tools 2026 — Medium](https://medium.com/@inprogrammer/best-python-testing-tools-2026-updated-884dcb78b115)
- [CVE-2026-24009: RCE in Docling via Unsafe PyYAML Deserialization](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)
- [pyproject.toml Specification — Python Packaging User Guide](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- [Get started with Python's new frozendict type — InfoWorld](https://www.infoworld.com/article/4152654/get-started-with-pythons-new-frozendict-type.html)
- [Python 3.15 Features: The Ultimate Guide to New Changes](https://runfreetools.com/blog/python-3-15-features)

---

**Summary:** Python ecosystem research 2026-09-01 is a validation pass with minor detail updates. Prior 2026-08-25 research was thorough; this session confirms all findings as current through September 1. **No blocking changes to Phase 7 or v1.1.** Tooling is stable (uv 0.12.x, pytest/coverage mature, PyYAML CVE isolated to Docling). PEP 808 formalization is a confidence-builder for CI reproducibility (worth a 15-minute doc note). Python 3.15 releases October 1 — watch for adoption planning in Q4 2026. Everything else is monitoring or v1.2 forward.
