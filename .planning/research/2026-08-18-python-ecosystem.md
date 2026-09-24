# Research: python-ecosystem — 2026-08-18

## Key Findings

1. **Coverage.py 7.15.4 released August 6, 2026 (upgrade from 7.13.5).** New version adds support for Python 3.15 rc1 and free-threading mode. Retains AI-driven gap suggestions from 7.13.5. **Relevance:** workspace-hub's existing coverage gates can upgrade to capture threading-safety coverage on Python 3.15 codebases (not immediate for v1.1, but forward-compatible). → [Coverage.py 7.15.4 Documentation](https://coverage.readthedocs.io/)

2. **PyYAML CVE-2026-24009: Remote Code Execution via unsafe deserialization in Docling (NEW, distinct from prior PyYAML legacy CVEs).** When Docling (document processing library) deserializes untrusted YAML input using PyYAML's unsafe loader, attacker-controlled documents execute arbitrary Python during normal parsing. Affects Docling integration if workspace-hub ingests user-supplied documents with embedded YAML. **Impact:** if `worldenergydata` or other pipelines use Docling for PDF/document metadata extraction, audit for YAML deserialization patterns and upgrade Docling + pin PyYAML to safe versions (6.0.2+). → [CVE-2026-24009: RCE in Docling via Unsafe PyYAML Deserialization](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009) | [PyYAML Security on Snyk](https://security.snyk.io/package/pip/pyyaml)

3. **PEP 808 (May 2026): pyproject.toml now allows static key specification alongside dynamic lists** — build backends can only append, not rewrite. Strengthens pyproject.toml immutability and predictability. **Relevance:** workspace-hub's existing pyproject.toml structure (all repos using declarative build config) already conforms. No action needed, but validates forward-compat of current structure. → [pyproject.toml Specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/) | [PEP 808](https://peps.python.org/pep-0808/)

4. **uv 0.12.1 (July 31, 2026) + August 13 release maintain compatibility; no breaking changes announced.** OpenAI's acquisition of Astral (March 2026) confirmed ongoing development. Projects initialized with `uv init` now declare build system and are packaged by default. **Relevance:** workspace-hub's exclusive use of `uv` for package management confirmed as stable + future-backed. No migration or upgrade friction expected for v1.1–v1.2. → [uv GitHub Releases](https://github.com/astral-sh/uv/releases) | [uv 2026 Guide](https://pyobfuscate.com/blog/uv-python-package-manager)

5. **pytest 9.0.3 + pytest-cov ecosystem remains stable; 1,300+ plugins on PyPI, with pytest-cov/pytest-xdist/pytest-mock covering 90% of testing needs.** No new breaking changes or security advisories since prior research. **Relevance:** workspace-hub's existing pytest + coverage gate infrastructure stable for v1.1–v1.2. TDD mandate continues to be enforceable without infrastructure changes. → [Best Python Testing Tools 2026 — Medium](https://medium.com/@inprogrammer/best-python-testing-tools-2026-updated-884dcb78b115)

## Relevance to Project

| Finding | Affected Package/Workflow | Impact | Action |
|---------|---|---|---|
| **Coverage.py 7.15.4 (Aug 6, 2026)** | TDD gate, CI coverage enforcement (`completeness-before-close`), Phase 7 smoke tests | **LOW-to-MEDIUM.** Upgrade from 7.13.5 is recommended but not urgent for v1.1. Free-threading support is useful if Tier-1 packages adopt Python 3.15 async optimizations (not planned for v1.1). **Timing:** optional upgrade at v1.1 coverage audit; mandatory by v1.2 if Python 3.15 support is adopted. | Monitor; defer to v1.1 optional refresh |
| **PyYAML CVE-2026-24009 (Docling RCE)** | `worldenergydata` data pipelines (if using Docling for document ingestion), compliance/risk audit | **MEDIUM-if-present.** Docling is a relatively new document processing lib; workspace-hub may or may not use it. **Quick action:** `grep -r "docling\|Docling" */pyproject.toml */uv.lock` across all Tier-1 repos + workspace-hub. If found, audit for YAML deserialization patterns and upgrade Docling + pin PyYAML ≥6.0.2. Expected: **not in use** (rare dependency for this domain). | **Parallel to prior Pydantic AI CVE grep (2026-08-11)** — execute both greps in one pass |
| **PEP 808 (May 2026, pyproject.toml static keys)** | All repos' pyproject.toml configurations, build backend compatibility | **LOW.** No action needed. Workspace-hub's declarative build config already conforms; PEP 808 reinforces immutability constraints you're already following. | Document in `.claude/rules/coding-style.md` (optional: add PEP 808 as forward-compat note) |
| **uv 0.12.1+ stability + OpenAI backing** | Package management, uv.lock reproducibility, CI dependency resolution | **POSITIVE.** Confirms uv as stable, vendor-backed (OpenAI), no migration friction. Workspace-hub's exclusive uv adoption is de-risked for multi-year horizon. | No action; confidence in uv strategy validated |
| **pytest 9.0.3 + 1,300+ plugins stable** | Test infrastructure, TDD gate enforcement, Phase 7 smoke tests | **POSITIVE.** Confirms pytest ecosystem maturity. No breaking changes, plugin compatibility stable. Workspace-hub's test infrastructure solid for v1.1–v1.2. | No action; foundation stable |

## Recommended Actions

- [ ] **MEDIUM (this week, parallel to Pydantic AI CVE grep): Audit all repos for Docling + PyYAML CVE-2026-24009 exposure.** Run `grep -r "docling\|Docling" */pyproject.toml */uv.lock` across workspace-hub and all Tier-1 packages. **Expected result: not in use** (rare dependency for engineering domain). **Deliverable:** GitHub issue comment: "(1) Docling grep result (found/not found); (2) if found, Docling version + PyYAML version audit; (3) action taken (upgrade Docling + pin PyYAML ≥6.0.2 if present, or close as N/A if absent)." **Timeline: 30 minutes, combine with existing Pydantic AI CVE grep from 2026-08-11 research.**

- [ ] **LOW (v1.1 optional): Evaluate Coverage.py 7.15.4 upgrade for Python 3.15 threading support.** If any Tier-1 package is planning Python 3.15 adoption with async I/O optimizations (not planned for v1.1), Coverage.py 7.15.4's free-threading support is relevant. **Timeline: defer to v1.1 coverage audit; optional refresh if test-coverage infrastructure changes.** **Reference:** [Coverage.py 7.15.4 Documentation](https://coverage.readthedocs.io/).

- [x] **CONFIRMATION (v1.1): Document PEP 808 conformance in `.claude/rules/coding-style.md`.** Workspace-hub's declarative pyproject.toml structure already conforms to PEP 808 (static key + dynamic list immutability). Add optional reference to `.claude/rules/coding-style.md` under Agent Harness Files section: "PEP 808 conformance: build backends append to dynamic lists only; keys remain static once declared." **Timeline: 15 minutes, low priority.** **Reference:** [pyproject.toml Specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/).

---

`★ Insight ─────────────────────────────────────`

**The Python ecosystem update landscape remains stable.** The 2026-08-11 research (Coverage.py 7.13.5, pytest 9.0.3, pyproject.toml ecosystem) was thorough and comprehensive. This week's update is primarily confirmatory (uv stable, pytest ecosystem healthy) plus one NEW security finding (PyYAML CVE-2026-24009 in Docling, likely not in your stack).

**Coverage.py's incremental release (7.13.5 → 7.15.4, Aug 6) adds Python 3.15 support but no breaking changes.** If you're on 7.13.5 already, upgrading to 7.15.4 is a low-friction point-release (same AI-gap-suggestion feature set, plus threading support). Not urgent for v1.1 (which targets Python 3.10–3.12), but worth noting for v1.2's Python version expansion plan.

**The PyYAML/Docling CVE-2026-24009 is a pattern repeat from prior PyYAML CVEs (2020, 2023), not a category change.** The risk is real (RCE via unsafe deserialization), but the mitigation is known (use safe loader, pin PyYAML ≥6.0.2). Quick grep confirms whether Docling is in your dependency tree; expected answer is "no, not in use for engineering domain." If it turns up in a data pipeline, the fix is immediate (upgrade + pin). This is parallel to the Pydantic AI CVE audit from 2026-08-11 — bundle both greps in one pass.

**uv + OpenAI backing validates your package-management strategy for the next 2–3 years.** No new friction, no alternative solutions needed. The "exclusive uv" decision from v1.0 (PROJECT.md) continues to be durable.

`─────────────────────────────────────────────────`

---

## Sources

- [Coverage.py 7.15.4 Documentation](https://coverage.readthedocs.io/)
- [CVE-2026-24009: RCE in Docling via Unsafe PyYAML Deserialization](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)
- [PyYAML Security on Snyk](https://security.snyk.io/package/pip/pyyaml)
- [pyproject.toml Specification — Python Packaging User Guide](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- [PEP 808 — Specifying pyproject.toml Keys](https://peps.python.org/pep-0808/)
- [uv GitHub Releases](https://github.com/astral-sh/uv/releases)
- [uv 2026 Python Package Manager Guide](https://pyobfuscate.com/blog/uv-python-package-manager)
- [Best Python Testing Tools 2026 — Medium](https://medium.com/@inprogrammer/best-python-testing-tools-2026-updated-884dcb78b115)

---

**Status:** This week's research consolidates the 2026-08-11 findings (which remain current) and surfaces one new CVE (PyYAML in Docling). No blocking changes to Phase 7 planning or v1.1 roadmap. **Recommended action: combine PyYAML/Docling CVE grep with the Pydantic AI CVE grep from 2026-08-11 (both parallel one-time checks); document results in same GitHub issue.** Everything else is validation of existing infrastructure stability.
