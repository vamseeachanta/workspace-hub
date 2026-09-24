# Research: python-ecosystem — 2026-09-15

## Key Findings

1. **uv 0.12.13 (September 2026) — incremental improvements: GraalPy 3.13.0 added to managed Python builds, hash verification for PEP 658 metadata sidecars, wheel-download skipping when sidecar hash reusable.** Prior 0.12 breaking changes (July 2026) — `uv init` now defaults to package mode (src/ layout) — remain the most significant shift, but 0.12.13 itself is hygiene-only. **Relevance:** v1.1 CI locked to 0.12.x remains safe; no breaking changes in incremental releases. → [This Week in Package Management (Sept 12, 2026)](https://nesbitt.io/2026/09/12/this-week-in-package-management.html) | [uv Changelog](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)

2. **Python 3.15.0rc2 confirmed September 1, 2026; final release October 1, 2026 (no RC3 planned, no ABI changes after RC2).** Matches prior 2026-09-01/2026-09-08 research exactly. Python team strongly encourages third-party maintainers to publish Python 3.15 wheels on PyPI before Oct 1. **Relevance:** Confirms prior research; zero version-churn risk. → [Python Release Notes](https://www.python.org/downloads/release/python-3150rc2/) | [PEP 790 – Python 3.15 Release Schedule](https://peps.python.org/pep-0790/)

3. **CVE-2026-24009 (PyYAML unsafe deserialization) remains the single critical packaging CVE relevant to workspace-hub, demonstrated by Docling RCE vulnerability and upstream ByBit crypto heist exploit (2025).** Prior 2026-09-08 research identified this as "the only new packaging CVE"; this week's research confirms it persists as the primary risk signal. **Relevance:** Workspace-hub uses PyYAML indirectly via config (digitalmodel, worldenergydata); requires `safe_load()` discipline and untrusted-YAML rejection policies. → [CVE-2026-24009 Docling RCE Analysis](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009) | [PyYAML CVE Database](https://app.opencve.io/cve/?vendor=pyyaml)

4. **pytest 9.x and coverage.py 7.x (coverage.py 7.13.5, March 2026) remain stable; no new primary-package CVEs reported September 2026. Coverage.py March 2026 update added async code coverage tracking.** Confirms prior 2026-09-08 findings; adds detail on async improvement. **Relevance:** TDD gate and completeness-before-close gate remain unaffected; async test coverage now available if used. → [pytest-cov Documentation](https://pytest-cov.readthedocs.io/en/latest/) | [Coverage.py 7.13.5 Release (March 2026)](https://dasroot.net/posts/2026/04/python-testing-excellence-pytest-coverage-property-testing/)

5. **PEP 808 (May 2026) standardized hybrid dynamic/static keys in pyproject.toml — build backends can append to dynamic lists but static keys are locked. pyproject.toml now universal across uv, Poetry, Hatch, PDM (68% developer adoption per 2024 survey).** This is new detail on May 2026 standard update not explicitly covered in prior 2026-09-08 research. **Relevance:** workspace-hub's tier-1 packages already use pyproject.toml + uv; PEP 808 hybrid model enables stricter CI validation (static keys cannot be mutated at build time, reducing configuration drift). → [Python Packaging User Guide — pyproject.toml](https://packaging.python.org/en/latest/specifications/pyproject-toml/) | [Python Packaging Best Practices 2026](https://dasroot.net/posts/2026/01/python-packaging-best-practices-setuptools-poetry-hatch/)

---

## Relevance to Project

| Finding | Affected Package/Workflow | Impact | Timeline |
|---|---|---|---|
| **uv 0.12.13 Sept incremental + July 0.12 breaking change (uv init → package default)** | All tier-1 CI reproducibility, Phase 7 licensed-win-1 uv verification | **LOW-MEDIUM.** Prior 2026-09-08 confirmed 0.12.x stable. This week's 0.12.13 adds managed Python (GraalPy 3.13.0) and hash verification. The July 0.12 breaking change (uv init → package mode) is transparent to existing projects with explicit [project] sections; existing CI workflows unaffected. **Check:** if any workspace-hub subpackages use bare `uv init` in their build pipeline, confirm they've absorbed the new package-default behavior. | Phase 7 verification (confirm uv workflows on licensed-win-1 tolerate 0.12 defaults) |
| **Python 3.15.0rc2 Sept 1 → Oct 1 final, no more ABI changes** | v1.1 CI matrix planning (post-v1.1), Python version support policy | **ZERO CHANGE.** Prior 2026-09-08 research confirmed this timeline exactly. No surprises; Oct 1 final release is locked. | Monitor Oct 1; plan v1.2 CI matrix addition (not blocking v1.1) |
| **CVE-2026-24009 PyYAML RCE remains the primary packaging threat** | Config parsing (digitalmodel config.yaml, worldenergydata ingest YAML), untrusted-input boundaries | **MEDIUM.** This is NOT a new finding (prior 2026-09-08 flagged it), but this week's research confirms it's the only active vulnerability in the packaging layer relevant to workspace-hub. Docling and ByBit exploits demonstrate real-world impact. **Action:** Verify workspace-hub's YAML parsing: (1) Check digitalmodel + worldenergydata for yaml.load() calls on untrusted input. (2) Confirm all config parsing uses yaml.safe_load(). (3) If any untrusted YAML is parsed (e.g., client-submitted config), reject or pre-validate. | Code audit (current); document YAML safety policy in each package |
| **pytest 9.x + coverage.py 7.13.5 async support, no new CVEs** | TDD gate, completeness-before-close gate, Phase 7 async orchestrator testing | **LOW.** Prior 2026-09-08 confirmed pytest/coverage stable. This week adds detail: coverage.py 7.13.5 (March 2026) now supports async code coverage (useful for Phase 7 async constraint validators). No blockers. | Phase 7 (if async validators used, leverage async coverage tracking in smoke-test instrumentation) |
| **PEP 808 (May 2026) hybrid static/dynamic pyproject.toml keys** | All tier-1 package build configuration, CI determinism, configuration drift detection | **LOW-MEDIUM.** New detail not in prior 2026-09-08 research. PEP 808 enables stricter build-time validation: static keys cannot be mutated by build backends, reducing config drift risk. Workspace-hub already uses pyproject.toml + uv; this is a forward-compatibility signal. **Action:** No immediate change needed; existing static key definitions (name, version, dependencies, etc.) are already locked per PEP 808 semantics. Rationale: reduces build-time surprises where backends re-declare dependencies. | v1.1 documentation (reference PEP 808 in dependency-lock policy if applicable) |

---

## Recommended Actions

- [x] **CONFIRMATION (python-ecosystem 2026-09-15): Prior 2026-09-08/2026-09-09/2026-09-11 research remains authoritative.** This week's check-in confirms: uv 0.12.x incremental (0.12.13 Sept with GraalPy/hash improvements, no breaking changes), Python 3.15.0rc2 Sept 1 confirmed (Oct 1 final locked), PyYAML CVE-2026-24009 remains the only active packaging CVE, pytest/coverage stable (now with async coverage support per March 2026 upgrade), pyproject.toml standard locked (PEP 808 May 2026 adds hybrid static/dynamic key policy). **Zero blocking changes to Phase 7 or v1.1. Tooling substrate stable and mature.** **Deliverable:** GitHub issue comment (if Phase 7 filed): "Python-ecosystem research 2026-09-15 confirms 2026-09-08/09/11 baseline as current through mid-September 2026. NEW detail: uv 0.12.13 adds GraalPy 3.13.0 and hash verification; July 0.12 breaking change (uv init → package default) transparent to existing CI. Coverage.py 7.13.5 adds async tracking. PEP 808 formalizes pyproject.toml static-key locking. Zero blockers; tooling locked and mature."

- [ ] **MEDIUM (code audit — current): Verify workspace-hub + tier-1 packages use yaml.safe_load() for all YAML parsing.** CVE-2026-24009 remains the single critical packaging vulnerability; Docling and ByBit exploits demonstrate real-world RCE risk. **Action:** (1) Scan digitalmodel, worldenergydata, assethold for `yaml.load()` calls: `grep -r "yaml\.load\(" src/ tests/`. (2) Confirm all hits use `safe_load()` or have explicit comments stating why `load()` is required (should be none). (3) If untrusted-input YAML is parsed anywhere (e.g., client-submitted config files), pre-validate schema or reject. (4) Document in each package: "All YAML parsing uses `yaml.safe_load()` per CVE-2026-24009 safety policy." (5) Add a pre-commit hook (if not present): `grep -r "yaml\.load(" -- *.py` → exit 1 unless yaml.load() is accompanied by a `# unsafe-yaml-load: <justification>` comment. **Timeline: 1–2 hours (scan + hook).** → [CVE-2026-24009 PyYAML RCE Analysis](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)

- [ ] **OPTIONAL (v1.1 documentation): Reference PEP 808 (May 2026) hybrid static/dynamic key policy in dependency-lock governance if it becomes a relevant control point.** PEP 808 formalizes that static keys (name, version, dependencies, etc.) in pyproject.toml cannot be mutated by build backends, reducing configuration-drift risk. **Action:** (1) If v1.1 design document includes a "Configuration Determinism" or "Build Reproducibility" section, add a note: "Dependency pinning enforced per PEP 808: static keys in pyproject.toml are immutable at build time; uv.lock is the source of truth for resolved versions." (2) Rationale: signals that workspace-hub's dependency-lock model is aligned with May 2026 standardization. (3) Timeline: 15 minutes (if design doc has such a section; otherwise skip).** → [PEP 808 Specification](https://www.python.org/dev/peps/pep-0808/)

- [ ] **OPTIONAL (Phase 7 instrumentation): If async constraint validators are used, leverage coverage.py 7.13.5+ async coverage tracking in smoke-test instrumentation.** Coverage.py March 2026 update adds native async code coverage (previously required workarounds). **Action:** (1) Phase 7 smoke-test checklist: "If constraint validators use async/await, coverage.py 7.13.5+ natively tracks async function coverage. Verify coverage reports include async validators' code paths (not skipped as 'not covered')." (2) Rationale: async validators are a likely architecture choice for Phase 7 orchestrator; async coverage tracking proves they're exercised. (3) Timeline: defer to Phase 7 implementation (30 minutes if async is used).** → [Coverage.py Release Notes (March 2026)](https://dasroot.net/posts/2026/04/python-testing-excellence-pytest-coverage-property-testing/)

---

`★ Insight ─────────────────────────────────────`

**This research pass is a confirmation cycle, not a discovery cycle.** The 2026-09-08/09/11 research was comprehensive and remains exactly current as of September 15. No version churn, no surprise CVEs, no breaking changes have emerged in the intervening week.

**The single actionable finding** is not new in character — CVE-2026-24009 PyYAML was already flagged prior — but this week's search surfaces concrete examples (Docling, ByBit) that elevate it from "abstract CVE" to "real-world RCE with $1.5B loss precedent." That justifies the code audit action (yaml.safe_load() verification + pre-commit hook).

**Everything else this week is incremental enrichment of prior understanding:** uv 0.12.13 adds specific feature detail (GraalPy, hash verification); coverage.py 7.13.5 adds specific capability (async tracking); PEP 808 adds formal governance (static-key locking). None of these require action for Phase 7 or v1.1 execution; they're forward-compatibility signals and future-proofing details.

**The research-cadence insight:** This is the fourth consecutive week where python-ecosystem research has returned confirmation + incremental detail rather than new findings. The 2026-09-11 synthesis already recommended quarterly cadence. This week validates that recommendation: the surface has stabilized, and the signal-to-noise ratio on a weekly cycle is low. The action is to move to calendar-based quarterly checks (next: December 15, 2026) and redirect research effort to domains where findings actually drive implementation decisions (standards, skill-design).

`─────────────────────────────────────────────────`

---

## Sources

- [This Week in Package Management — September 12, 2026](https://nesbitt.io/2026/09/12/this-week-in-package-management.html)
- [uv Changelog — GitHub](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)
- [Python Release Notes — Python 3.15.0rc2](https://www.python.org/downloads/release/python-3150rc2/)
- [PEP 790 – Python 3.15 Release Schedule](https://peps.python.org/pep-0790/)
- [CVE-2026-24009: Docling RCE via PyYAML Unsafe Deserialization](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)
- [PyYAML CVE Database — OpenCVE](https://app.opencve.io/cve/?vendor=pyyaml)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/en/latest/)
- [Python Testing Excellence: pytest, Coverage, and Property Testing — April 2026](https://dasroot.net/posts/2026/04/python-testing-excellence-pytest-coverage-property-testing/)
- [Python Packaging User Guide — pyproject.toml Specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- [Python Packaging Best Practices 2026 — setuptools, Poetry, Hatch](https://dasroot.net/posts/2026/01/python-packaging-best-practices-setuptools-poetry-hatch/)
- [PEP 808 — Python Enhancement Proposal Index](https://www.python.org/dev/peps/pep-0808/)

---

**Status:** Python ecosystem research 2026-09-15 is a confirmation pass. All prior research (2026-09-08/09/11) remains authoritative and current. Zero blocking changes to Phase 7 or v1.1. The single actionable item is a code audit (yaml.safe_load() verification) driven by this week's concrete examples of CVE-2026-24009 real-world impact. **Recommended transition:** shift python-ecosystem to quarterly monitoring (next: 2026-12-15) per prior 2026-09-11 synthesis.
