# Research: python-ecosystem — 2026-03-27

## Key Findings

- **uv 0.11.0 (2026-03-23) — TLS breaking change:** Upgraded `reqwest` to v0.13, switching certificate verification to `rustls-platform-verifier`. May reject certificates previously trusted. Also: `--native-tls` deprecated in 0.10.0 (Feb) in favor of `--system-certs`. ([uv releases](https://github.com/astral-sh/uv/releases), [uv 0.11.0](https://github.com/astral-sh/uv/releases/tag/0.11.0))

- **pandas 3.0.0 (2026-01-21) — Major breaking release:** Copy-on-Write is now the only mode (chained assignment `df[col][row] = val` no longer works). String columns default to `str` dtype instead of `object` (uses PyArrow backend if installed). `SettingWithCopyWarning` removed entirely. ([pandas 3.0 what's new](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html), [migration guide](https://pandas.pydata.org/docs/user_guide/migration-3-strings.html))

- **NumPy 2.4.x (Dec 2025 – Mar 2026):** Expired deprecations now raise errors — `np.sum(generator)` → `TypeError`, ndim>0 array-to-scalar conversion → `TypeError`, `ndincr()` removed. `np.testing.assert_warns` deprecated. Continues free-threaded Python support work. ([NumPy 2.4.0 notes](https://numpy.org/devdocs/release/2.4.0-notes.html))

- **CVE-2026-24009 — PyYAML unsafe loader RCE:** Affects `docling-core` >=2.21.0,<2.48.4 when using `yaml.FullLoader` on untrusted input. While this CVE is in `docling-core` (not in your stack), it's a reminder that **any code using `yaml.load()` without `Loader=yaml.SafeLoader` is vulnerable**. ([Oligo Security advisory](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009))

- **pytest-cov 7.1.0 (2026-03-21) + coverage.py 7.13.5 (2026-03-17):** New releases support Python 3.10–3.15. Fixed `breakpoint()` stopping in wrong frame under coverage. Fixed incorrect branch coverage claims with `sys.monitoring` core on multi-line `case`/`for` clauses. ([coverage.py docs](https://coverage.readthedocs.io/en/latest/changes.html), [pytest-cov changelog](https://pytest-cov.readthedocs.io/en/latest/changelog.html))

## Relevance to Project

- **uv TLS change → all 24 repos:** Since you use `uv` exclusively, the 0.11.0 TLS certificate verification change could break `uv sync`/`uv pip install` on any machine with corporate or self-signed certificates (especially `licensed-win-1` and `licensed-win-2`). The `--native-tls` → `--system-certs` rename also affects any scripts using the old flag.

- **pandas 3.0 → `worldenergydata`, `assetutilities`, `digitalmodel`:** These repos likely use pandas heavily for data pipelines and engineering calculations. Copy-on-Write semantics will break any chained assignment patterns. The string dtype change may affect column type checks, `.dtype == object` tests, and serialization logic (especially Parquet output in the data adapters shipped in Phase 2).

- **NumPy 2.4 expired deprecations → `digitalmodel`, `assetutilities`:** Engineering calculation modules may use patterns like `np.sum(generator)` or implicit array-to-scalar conversion. These now raise `TypeError` instead of warnings.

- **PyYAML safe loading → `digitalmodel` manifests:** Phase 1 shipped YAML manifest schemas (Pydantic model + CI validation). Ensure all `yaml.load()` calls use `Loader=yaml.SafeLoader` or Pydantic's own parsing — never `yaml.FullLoader` or `yaml.UnsafeLoader`.

- **pytest-cov/coverage.py updates → all repos with test suites:** The `breakpoint()` fix and branch coverage accuracy improvements are quality-of-life upgrades. Worth pinning to latest versions given TDD mandate.

## Recommended Actions

- [ ] **Create GitHub issue:** Audit all 24 repos for uv version pinning and test `uv sync` against 0.11.0 TLS changes on all 4 machines (especially Windows workstations with corporate certs)
- [ ] **Create GitHub issue:** Audit `worldenergydata`, `assetutilities`, and `digitalmodel` for pandas 3.0 compatibility — search for chained assignment, `.dtype == object` checks, and string column assumptions
- [ ] **Create GitHub issue:** Grep tier-1 repos for `np.sum(generator)`, implicit array-to-scalar, and other NumPy 2.4 expired deprecations
- [ ] **Create GitHub issue:** Audit all `yaml.load()` calls across repos to confirm `SafeLoader` usage (especially `digitalmodel` manifest handling)
- [ ] **Ignore (low urgency):** pytest-cov 7.1.0 and coverage.py 7.13.5 — upgrade opportunistically during next dependency refresh; no breaking changes

Sources:
- [uv releases](https://github.com/astral-sh/uv/releases)
- [uv 0.11.0 release](https://github.com/astral-sh/uv/releases/tag/0.11.0)
- [uv TLS docs](https://docs.astral.sh/uv/concepts/authentication/certificates/)
- [pandas 3.0.0 what's new](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
- [pandas string migration guide](https://pandas.pydata.org/docs/user_guide/migration-3-strings.html)
- [NumPy 2.4.0 release notes](https://numpy.org/devdocs/release/2.4.0-notes.html)
- [CVE-2026-24009 (PyYAML/docling-core)](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)
- [coverage.py changelog](https://coverage.readthedocs.io/en/latest/changes.html)
- [pytest-cov 7.1.0 changelog](https://pytest-cov.readthedocs.io/en/latest/changelog.html)
- [Python packaging in 2026](https://learn.repoforge.io/posts/the-state-of-python-packaging-in-2026/)
