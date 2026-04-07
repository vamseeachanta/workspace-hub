# Research: python-ecosystem — 2026-04-07

## Key Findings

- **uv 0.11.0 — TLS certificate verification changes from `--native-tls` to `--system-certs` flag; reqwest 0.13 upgrade impacts cross-machine compatibility.** The upgrade from reqwest 0.12 to 0.13.1 changed TLS handling: bundled Mozilla certificates are now default (improved portability), but the `--native-tls` flag is deprecated in favor of `--system-certs` for system certificate store access. Environment variables `UV_NATIVE_TLS`, `SSL_CERT_FILE`, and `SSL_CERT_DIR` remain functional but behavior changed. This affects all 4 machines (dev-primary, dev-secondary, licensed-win-1, licensed-win-2) if they use custom corporate proxies or self-signed certificates.

- **pandas 3.0 (January 21, 2026) — Copy-on-Write default breaks chained assignment; SettingWithCopyWarning removed, `.loc` now mandatory.** The most impactful breaking change: `df["foo"][df["bar"] > 5] = 100` no longer works; must use `df.loc[df["bar"] > 5, "foo"] = 100`. The `pd.options.mode.copy_on_write` setting is deprecated and has no effect. This affects worldenergydata Parquet pipelines (Phase 2 completed 2026-03-26) and any digitalmodel calculation DataFrames using chained assignment patterns. String dtype defaults also changed, impacting serialization.

- **NumPy 2.4 — `np.sum(generator)` now raises TypeError; `np.round()` always returns copy; strides mutation deprecated.** The generator deprecation removes a long-standing (since NumPy 1.15.0) warning and makes it an error — code using `np.sum(generator)` must switch to `np.sum(np.fromiter(generator))` or Python's builtin `sum()`. The `np.round()` behavior change (now always copy vs. view for integer inputs) breaks assumptions in code relying on in-place modification. This impacts spectral fatigue and wall thickness calculation modules if they use generator-based array operations.

- **PyYAML — CVE-2026-24009 shadow vulnerability: unsafe YAML deserialization in downstream libraries (Docling, others) enables RCE when processing untrusted YAML.** The vulnerability occurs when libraries internally use `yaml.load()` without `SafeLoader`, creating an RCE window for attacker-supplied YAML documents. Workspace-hub's `.planning/research/` YAML manifests and Phase 5 nightly researcher configuration files are trusted inputs, but any integration with untrusted external YAML sources (e.g., client-supplied OrcaFlex job files in YAML format) becomes a risk vector. This is a "shadow vulnerability" — the risk exists at runtime without direct code visibility.

- **ASME B31.4-2025 (approved October 27, 2025) — All equations unified for both US and SI units; longitudinal stress equations revised to align with B31.3; new low-temperature material requirements.** The 2025 edition eliminates separate US/SI equation sets, which simplifies code but requires unit-aware verification. Longitudinal stress (SL) calculations now match B31.3 methodology — wall thickness module (Phase 1 completed 2026-03-25) must verify equation equivalence with current implementation. Low-temperature material requirements are new, affecting offshore subsea applications in cold regions. Cross-referenced standards baseline shift requires compliance audit.

- **DNV-RP-C203 2024 (October 2024) — S-N curves revised (B1–C2 focus); grit blasting factor removed for ground welds; subsea connector methodology updated.** The 2024 revision improves fatigue strength estimates and removes inconsistencies where lower-grade curves outperformed higher ones. Spectral fatigue module (Phase 1 completed) uses 2016 curves; migration to 2024 curves affects all existing calculations and benchmarking results. The subsea connector methodology change impacts any future connector-specific modules. This is high-priority technical debt per prior research synthesis.

## Relevance to Project

| Finding | Affected Package / Workflow | Impact |
|---|---|---|
| **uv 0.11.0 TLS changes** | All tier-1 repos + 4-machine CI/CD | `--native-tls` deprecation requires testing on licensed machines; Windows certificate store handling differs from Linux. Phase 7 remote execution (dev-primary → licensed-win-1) must verify certificate chain validation. |
| **pandas 3.0 Copy-on-Write** | `worldenergydata` (Phase 2, Parquet pipelines), `digitalmodel` (Phase 1, DataFrame calculations) | Chained assignment patterns in Parquet read/write code will silently fail with CoW semantics. Grep for `df[...][...] = ` patterns across both repos and refactor to `.loc`. String dtype changes may affect Parquet round-trip compatibility. |
| **NumPy 2.4 deprecations** | `digitalmodel` (spectral fatigue, wall thickness, on-bottom stability modules) | `np.sum(generator)` → `np.sum(np.fromiter())` refactor needed. `np.round()` behavior change affects rounding of design factors and safety margins — verify no in-place modification assumptions. Test coverage must validate all array roundtrip behavior. |
| **PyYAML CVE-2026-24009** | Phase 5 (nightly research automation YAML manifests), Phase 7 (solver verification job configs) | Internal YAML is trusted, but audit all `yaml.load()` calls to ensure `SafeLoader` is used. If Phase 5 integrates with external sources (e.g., client OrcaFlex job files in YAML), add input validation layer before YAML deserialization. |
| **ASME B31.4-2025** | `digitalmodel` wall thickness module (Phase 1) | Unit system unification simplifies code but requires equation-by-equation equivalence audit: verify current implementation equations match 2025 revision. Low-temperature material requirements may enable new calculation domain (Arctic/subsea). |
| **DNV-RP-C203 2024 S-N curves** | `digitalmodel` spectral fatigue module (Phase 1) | 2016 curves vs. 2024 curves show measurable differences (B1 nearly identical, C-curves significant). Benchmark existing calculations (L00–L06 examples) against 2024 curves. Update standards traceability manifests. High technical debt priority. |

## Recommended Actions

- [ ] **Create GitHub issue** — `workspace-hub`: Audit all tier-1 repos for uv 0.11.0+ TLS compatibility; test `uv pip install` on all 4 machines (especially licensed-win-1/2) with `--system-certs` flag; document certificate chain requirements in Phase 7 smoke tests
- [ ] **Create GitHub issue** — `worldenergydata` + `digitalmodel`: Audit for pandas 3.0 Copy-on-Write breaking changes; grep all repos for chained assignment pattern `df[...][...] = ` and refactor to `.loc[..., ...] = `; benchmark Parquet string dtype round-trip compatibility
- [ ] **Create GitHub issue** — `digitalmodel`: Refactor NumPy 2.4 deprecations; replace `np.sum(generator)` with `np.sum(np.fromiter())` or builtin `sum()`; verify all array rounding logic assumes copy semantics (not view)
- [ ] **Create GitHub issue** — `workspace-hub`: Security audit — grep all code for `yaml.load()` without `SafeLoader`; if Phase 5 nightly researchers accept external YAML, add schema validation layer before deserialization
- [ ] **Create GitHub issue** — `digitalmodel`: Audit ASME B31.4-2025 vs. 2016/2020 wall thickness equations; verify unit unification doesn't change calculation logic; add low-temperature material requirements to future backlog (Phase 999.2)
- [ ] **Create GitHub issue** — `digitalmodel`: Upgrade spectral fatigue module to DNV-RP-C203 2024 S-N curves; benchmark L00–L06 examples against 2016 baseline; update standards traceability manifests; measure fatigue strength delta (especially C-curves)
- [ ] **Promote to PROJECT.md** — Add under Current Milestone (v1.1 OrcaWave Automation): "TLS certificate verification standardization (uv `--system-certs`, Phase 7 remote execution) and pandas 3.0 Copy-on-Write adoption required for v1.1 shipping; verify on all 4 machines and update CI/CD gate scripts"
- [ ] **Promote to ROADMAP.md** — Add Phase 999.2 (Wind Energy, Turbines, FFS) backlog refinement: "ASME B31.4-2025 low-temperature material requirements enable Arctic/subsea domain; DNV-RP-C203 2024 S-N curves improve fatigue accuracy across all structural modules"

---

Sources:
- [uv TLS Certificates Documentation](https://docs.astral.sh/uv/concepts/authentication/certificates/)
- [uv Versioning and Policies](https://docs.astral.sh/uv/reference/policies/versioning/)
- [uv GitHub CHANGELOG](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)
- [pandas 3.0.0 Release Notes (January 21, 2026)](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
- [Pandas 3.0 Released Announcement](https://pandas.pydata.org/community/blog/pandas-3-0.html)
- [Pandas 3.0: Copy-on-Write Deep Dive](https://phofl.github.io/cow-adaptions.html)
- [NumPy 2.4.0 Release Notes](https://numpy.org/devdocs/release/2.4.0-notes.html)
- [NumPy Release Notes Archive](https://numpy.org/doc/stable/release.html)
- [PyYAML CVE-2026-24009 Shadow Vulnerability](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)
- [PyYAML Security Vulnerabilities — Snyk](https://security.snyk.io/package/pip/pyyaml)
- [ASME B31.4-2025 Pipeline Transportation Systems](https://www.intertekinform.com/en-us/standards/asme-b31-4-2025-137813_saig_asme_asme_3782260/)
- [What's New in ASME B31.4-2025](https://whatispiping.com/asme-b31-4-2025/)
- [DNV-RP-C203 Fatigue Design 2024 Update](https://www.dnv.com/energy/standards-guidelines/dnv-rp-c203-fatigue-design-of-offshore-steel-structures/)
- [DNV-RP-C203 2024 Benchmark Comparison](https://sdcverifier.com/benchmarks/dnv-rp-c203-fatigue-comparison-2016-vs-2024/)
- [DNV July 2025 Edition Release](https://www.dnv.com/news/2025/now-available-july-2025-edition-of-dnv-class-rules-and-documents-for-ship-and-offshore/)
- [DNV Rules 2026 — Hearing Period Open](https://www.dnv.com/news/2026/dnv-rules-2026-hearing-period-now-open/)
