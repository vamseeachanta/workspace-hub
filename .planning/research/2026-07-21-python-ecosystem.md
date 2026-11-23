# Research: python-ecosystem — 2026-07-21

## Key Findings

1. **uv 0.10.0 (Q2 2026) ships Ruff 0.15.0 with 2026 style guide changes.** Format behavior updated: lambda parameters stay on one line, improved spacing around magic literals. TY and RUFF environment variables now allow configuring paths for format and check binaries. Also: `--bounds major` flag added to `uv add` to prevent silent major version pulls (per issue #2 below). → [uv GitHub Releases](https://github.com/astral-sh/uv/releases) | [uv CHANGELOG.md](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)

2. **uv dependency resolution silently pulls major version updates on `uv lock --upgrade` (HIGH RISK).** When no upper bound is set on dependencies in pyproject.toml, running `uv lock --upgrade` or `uv sync` on a different machine can silently install breaking major versions without explicit constraint updates. Mitigation: use `--bounds major` flag with `uv add`, commit uv.lock to git, and enforce `uv sync --locked` or `uv run --frozen` in CI to fail loudly instead of slipping through. This is especially critical for multi-machine deployments (workspace-hub's dev-primary + licensed-win-1 + dev-secondary setup). → [uv Locking and Syncing Docs](https://docs.astral.sh/uv/concepts/projects/sync/) | [Why uv run --frozen matters in production](https://www.yellowduck.be/posts/why-using-uv-run-frozen-matters-in-production)

3. **uv astral-async-zip v0.0.20 (July 15, 2026) hardens ZIP archive handling against parser differentials.** 15 changes to reject malformed/ambiguous ZIP content previously accepted. Affects any uv subcommand that processes wheels or archives (e.g., `uv sync`, `uv pip compile`). No immediate action unless you have malformed wheels in your dependency graph; update uv to 0.10.0+ to get the hardening. → [uv Release Notes](https://github.com/astral-sh/uv/releases)

4. **PyYAML CVE-2026-24009 — Remote Code Execution via unsafe deserialization.** Affects Docling Core and any code using `yaml.full_load()` on untrusted YAML. Workaround: use `yaml.safe_load()` for all non-trusted content. workspace-hub uses pyyaml (checked in .claude/memory); verify no code paths use `full_load()` on user input. Patch available via Snyk. → [CVE-2026-24009: RCE in Docling via PyYAML](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009) | [PyYAML Security Advisories (Snyk)](https://security.snyk.io/package/pip/pyyaml)

5. **pytest 9.0.3 (2026 release) introduces experimental subtests as alternative to parametrization.** Subtests allow capturing partially-known test parameters at test-collection time, with better error reporting for multi-assertion scenarios. Complementary to existing pytest parametrization (not a replacement). Also: coverage.py 7.13.5 (March 2026) now supports Python 3.10–3.15 alpha + PyPy3. → [Best Python testing tools 2026](https://medium.com/@inprogrammer/best-python-testing-tools-2026-updated-884dcb78b115) | [pytest-cov PyPI](https://pypi.org/project/pytest-cov/)

## Relevance to Project

| Finding | Affected Package/Workflow | Impact |
|---------|--------------------------|--------|
| **uv silent major-version pulls (Issue #2)** | `uv.lock` files in all 5 Tier-1 packages + hub; multi-machine deployments (dev-primary → licensed-win-1 smoke tests, Phase 7) | **HIGH/CRITICAL.** This is a real operational risk for workspace-hub's multi-machine model. A developer runs `uv add requests` on dev-primary without `--bounds major`, commits to main. On licensed-win-1 (or in CI), a stale `uv.lock` is updated via plain `uv sync`, silently pulling `requests==3.0.0` (breaking API). Phase 7's solver-verification gate includes remote execution from dev-primary → licensed-win-1; CI/CD must enforce `uv sync --locked` to prevent this. Current CLAUDE.md instructs `uv run` but does NOT enforce `--locked` in CI workflows — needs explicit audit + enforcement script. |
| **uv 0.10.0 format changes (lambda, spacing)** | `.claude/skills/`, `/src/` directories across Tier-1 packages if using `uv format` for code style | **LOW-MEDIUM.** The 2026 style guide changes are backward-compatible (prefer-over, not enforce). If workspace-hub adopts `uv format` for pre-commit hooks (per `verify-ci-lint-toolchain.md`), test against Ruff 0.15.0 to ensure no drift between local and CI. Current `.claude/rules/verify-ci-lint-toolchain.md` does NOT mention `uv format`; style enforcement uses `black`/`isort`/`flake8` explicitly — no action required. |
| **uv ZIP hardening (astral-async-zip v0.0.20)** | Wheel installation in `uv sync`, `uv pip compile` | **LOW.** Hardening is defensive; only affects malformed wheels (rare). No action unless your dependency graph includes wheels with known malformation. Recommend: auto-update uv to 0.10.0+ in CI (already done via release tracking). |
| **PyYAML CVE-2026-24009 (unsafe deserialization)** | Any module using `pyyaml` (configuration parsing, data ingest); `digitalmodel`, `assetutilities`, `worldenergydata` | **MEDIUM.** Grep codebase for `yaml.full_load()` or `FullLoader` — if found and processing untrusted input, upgrade pyyaml and switch to `safe_load()`. If all YAML sources are trusted (e.g., committed config files), patch is optional but recommended. Create GitHub issue to audit + enforce `safe_load()` only. |
| **pytest 9.0.3 subtests + coverage.py 7.13.5 (Python 3.15 support)** | Test suites in Tier-1 packages (`tests/` directories, CI/CD) | **LOW-MEDIUM.** Subtests are experimental; no action required. However, coverage.py 7.13.5 (March 2026) now targets Python 3.15 alpha — if you're running CI against 3.15 pre-release, confirm coverage compatibility. Recommend: update coverage.py in all `uv.lock` files to 7.13.5+ for forward compatibility. Current test targets (Python 3.10–3.13 per workspace-hub setup) are already covered. |

## Recommended Actions

- [x] **Promote to PROJECT.md / create GitHub issue** — `workspace-hub#TBD`: "**uv lock silent major-version updates — CRITICAL mitigation required.** Phase 7 (solver-verification gate) and all CI/CD workflows must enforce `uv sync --locked` or `uv run --frozen` to fail loudly on lock/pyproject drift. All `uv add` commands must use `--bounds major` to prevent unbounded major-version constraints. Audit current CI steps in `.github/workflows/` for enforcement; add pre-commit hook to verify `--bounds major` on all new adds. Timeline: merge Phase 7 plan with enforcement script as a dependency." Tag `priority:critical`, `lane:infrastructure`, `blocking:Phase-7`.

- [ ] **Create GitHub issue** — `workspace-hub#TBD`: "PyYAML CVE-2026-24009 audit: grep codebase for `yaml.full_load()` or `FullLoader`; if found, refactor to `safe_load()` and upgrade pyyaml version. Scope: `digitalmodel/`, `assetutilities/`, `worldenergydata/`, `assethold/`. Timeline: pre-Phase-7." Tag `lane:security`, `priority:high`.

- [ ] **Monitor** — uv 0.11.0 (expected Q4 2026 or Q1 2027) for stabilization of `--bounds` flag and any default-behavior changes around lock file updates. Current guidance (commit `uv.lock`, use `--locked`, use `--bounds major`) is sufficient for now.

- [ ] **Defer** — pytest 9.0.3 subtests (experimental, low adoption). Revisit when subtests reach stable (non-experimental) status in pytest 9.1+. No action for v1.1 OrcaWave milestone.

- [ ] **Defer** — Wheel Next initiative (PEP 817 variants). Expected to move from prototype to PEPs in 2026, production implementations 2027+. Monitor for GA announcements; no v1.1 action.

- [ ] **Ignore with reason** — PEP 621/518 adoption trends (68% of developers): workspace-hub is already 100% on `pyproject.toml` via `uv` (no action). The standards are mature and locked; no breaking changes expected.

---

`★ Insight ─────────────────────────────────────`

**The uv lock silent-major-version issue is not new, but it's acute for multi-machine deployments like workspace-hub.** You have three physical machines (dev-primary, dev-secondary, licensed-win-1) sharing uv.lock files across git + pushing to main. If a developer anywhere runs `uv add requests` without `--bounds major` and a CI job later runs `uv lock --upgrade` on a different branch/machine, the lockfile silently drifts. This is exactly the failure mode your Phase 7 solver-verification gate is designed to catch — but CI must enforce `--locked` to *fail loudly* instead of slipping through.

**PyYAML's CVE-2026-24009 is a reminder that configuration files are attack surfaces.** If workspace-hub's YAML config (skill definitions, project metadata, client data) is ever parsed from untrusted sources (e.g., uploaded files), the full_load/FullLoader path becomes a real vulnerability. Current usage is probably safe (all YAML is repo-committed), but a pre-Phase-7 audit takes 30 minutes and eliminates the class entirely.

**The testing ecosystem is stable but slowly evolving.** pytest 9.0.3's subtests are interesting for scenarios where parametrization doesn't fit (e.g., multi-assertion test cases), but they're experimental — not a v1.1 priority. coverage.py's Python 3.15 support is forward-looking and good hygiene, but your current test matrix (3.10–3.13) doesn't require it yet.

`─────────────────────────────────────────────────`

---

**Sources:**
- [Releases · astral-sh/uv](https://github.com/astral-sh/uv/releases)
- [uv CHANGELOG.md at main](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)
- [uv Locking and Syncing Docs](https://docs.astral.sh/uv/concepts/projects/sync/)
- [Why uv run --frozen matters in production - YellowDuck.be](https://www.yellowduck.be/posts/why-using-uv-run-frozen-matters-in-production)
- [How to use a uv lockfile for reproducible Python environments](https://pydevtools.com/handbook/how-to/how-to-use-a-uv-lockfile-for-reproducible-python-environments/)
- [CVE-2026-24009: RCE in Docling via Unsafe PyYAML Deserialization - Oligo Security](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)
- [PyYAML Security Vulnerabilities - Snyk](https://security.snyk.io/package/pip/pyyaml)
- [Best Python testing tools 2026 - Medium](https://medium.com/@inprogrammer/best-python-testing-tools-2026-updated-884dcb78b115)
- [pytest-cov · PyPI](https://pypi.org/project/pytest-cov/)
- [Pytest Coverage with pytest-cov: Complete 2026 Guide - QASkills.sh](https://qaskills.sh/blog/pytest-coverage-pytest-cov-guide-2026)
- [PEP 621 – Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [PEP 518 – Specifying Minimum Build System Requirements for Python Projects](https://peps.python.org/pep-0518/)
- [Python Packaging pyproject.toml: Modern Packaging Guide 2026 - GUVI](https://www.guvi.in/blog/python-packaging-with-pyproject-toml/)
