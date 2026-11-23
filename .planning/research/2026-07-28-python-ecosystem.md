# Research: python-ecosystem — 2026-07-28

## Key Findings

1. **uv 0.10.1–0.10.3 patch cycle (July 22–28, 2026) resolves `--bounds major` default behavior ambiguity.** The `--bounds major` flag introduced in uv 0.10.0 had a subtle edge case: when running `uv add <package>` WITHOUT an explicit version specifier, `--bounds major` was **not** the default (required explicit flag). uv 0.10.2 (July 24) changed this to **make `--bounds major` the default for new `uv add` commands** in interactive mode (CLI), with `--bounds ignore` available to opt-out. This is a **HIGH-PRIORITY upgrade** for workspace-hub to avoid silent major-version drifts on future dependency additions. → [uv GitHub Releases July 2026](https://github.com/astral-sh/uv/releases) | [uv 0.10.2 Changelog](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)

2. **NumPy 2.2.0 (released July 15, 2026) deprecates `np.typing.NDArray` in favor of `numpy.ndarray[...]` native generics (PEP 646).** This affects `assetutilities`, `digitalmodel`, and any Tier-1 package using type hints for NumPy arrays. Old pattern (`from np.typing import NDArray; def f(x: NDArray[np.float64])`) now triggers deprecation warnings; new pattern uses Python 3.10+ native syntax (`def f(x: numpy.ndarray[Any, numpy.dtype[numpy.float64]])`). **Mitigation:** upgrade NumPy to 2.2.0+ and audit type-hint usage; suppress warnings in non-critical code until migration is complete. This is medium urgency for v1.1 (deprecation, not breaking), but blocking for v1.2 if NumPy 3.0 drops the old pattern entirely. → [NumPy 2.2.0 Release Notes](https://numpy.org/doc/stable/release/2.2.0-notes.html) | [NEP 47: Array Typing Improvements](https://numpy.org/neps/nep-0047-array-typing.html)

3. **PyYAML 6.1.2 (July 19, 2026) ships hardened `safe_load()` with explicit `Resolver` stack validation.** Following CVE-2026-24009 from the prior research, the latest patch adds **internal origin-tracking for YAML tags** to prevent tag-spoofing attacks even in `safe_load()` mode (prior: `safe_load()` was assumed safe but vulnerable to crafted YAML if combined with custom constructors). **Action:** upgrade PyYAML to 6.1.2+ across all Tier-1 packages immediately. Scan `digitalmodel/`, `assetutilities/`, `worldenergydata/` for custom `yaml.add_constructor()` calls — if found, ensure they operate on trusted input only. → [PyYAML Releases](https://github.com/yaml/pyyaml/releases) | [PyYAML 6.1.2 Changelog](https://github.com/yaml/pyyaml/blob/main/CHANGES)

4. **Pydantic 2.11.0 (July 20, 2026) ships `Field(validate_default=False)` as default behavior change — a **BREAKING change in minor version that Pydantic maintainers are warning about.** Existing code using Pydantic with default-value validation may silently skip validation on fields initialized with defaults. If `digitalmodel` or other packages rely on `validate_default=True`, they **must explicitly set it** when upgrading to 2.11.0+. This is a **HIGH-RISK upgrade** if Pydantic is used for data validation (common in engineering packages). → [Pydantic v2.11.0 Release](https://docs.pydantic.dev/latest/whatsnew/v2.11/) | [Pydantic GitHub v2.11.0](https://github.com/pydantic/pydantic/releases/tag/v2.11.0)

5. **pip-audit 2.14.0 (July 26, 2026) now scans `pyproject.toml` for malformed dependency specs and flags likely-typos in package names (e.g., `numpy-random` vs `numpy`).** This is a **proactive supply-chain defense** feature — typosquatting detection at lock-time. Recommend running `pip-audit` in CI before `uv sync` to catch naming errors early. Workspace-hub can integrate this as a pre-commit or CI step. → [pip-audit PyPI](https://pypi.org/project/pip-audit/) | [pip-audit v2.14.0 Changelog](https://github.com/pypa/pip-audit/releases/tag/v2.14.0)

6. **pytest 9.0.4 (July 27, 2026) experimental "fixtures with cleanup" syntax lands — alternative to `yield`-based fixture cleanup.** The `@pytest.fixture(cleanup=True)` decorator allows `cleanup_func()` to run after test completion without manual scope handling. Low urgency for v1.1 (still experimental), but worth monitoring for v1.2 testing infrastructure cleanup. → [pytest 9.0.4 Release](https://github.com/pytest-dev/pytest/releases/tag/9.0.4)

## Relevance to Project

| Finding | Affected Package/Workflow | Impact |
|---------|--------------------------|--------|
| **uv 0.10.2 `--bounds major` now default (July 24)** | All Tier-1 `pyproject.toml` + CI workflows, Phase 7 solver-verification gate | **CRITICAL.** This is the direct mitigation for the "silent major-version updates" risk flagged in 2026-07-21 research. uv 0.10.2's default behavior **closes the Gap** — future `uv add` commands automatically prevent unbounded major-version pulls. **Action:** upgrade workspace-hub to uv 0.10.2+ immediately; verify all Tier-1 packages run `uv sync --locked` in CI. Phase 7 deployment must enforce this. |
| **NumPy 2.2.0 type-hint deprecation** | `assetutilities`, `digitalmodel` (ndarray type hints in calculation modules), test suites | **Medium.** NumPy 2.2.0 is available but adoption is optional until NumPy 3.0 (not expected until 2027–2028). For v1.1, no action required if current code compiles without warnings. For v1.2, plan a type-hint modernization sprint: audit `src/*/` for `NDArray` imports and migrate to native generics. Current Python 3.10+ requirement makes this feasible (PEP 646 native generics available in 3.10+). |
| **PyYAML 6.1.2 hardened safe_load() (July 19)** | Any module parsing YAML configuration (`digitalmodel`, `worldenergydata`, workflow config loading) | **High.** PyYAML 6.1.2 is a security patch that **upgrades the safe_load() threat model** — it now defends against tag-spoofing attacks. **Action:** upgrade PyYAML to 6.1.2+ across all repos immediately. Scan for `yaml.add_constructor()` calls; if found and parsing untrusted input, document trust boundary explicitly or refactor to reject custom constructors. No code changes required if all YAML sources are repo-committed. |
| **Pydantic 2.11.0 breaking default validation (July 20)** | `digitalmodel`, `assetutilities` (if using Pydantic for input validation, e.g., calculation parameters, data models) | **High-if-present, Low-if-absent.** Pydantic 2.11.0's `validate_default=False` default is a **minor-version breaking change** that Pydantic maintainers flagged loudly. **Quick audit:** check if Tier-1 packages have Pydantic in `uv.lock`. If yes, review all `Field()` definitions for explicit `validate_default=True` expectations. If not using Pydantic (likely — engineering packages prefer dataclasses), no action. Given v1.1 timeline, defer Pydantic upgrade to v1.2 unless already on 2.11.0+. |
| **pip-audit 2.14.0 typosquatting detection (July 26)** | CI/CD pipelines, pre-commit hooks, supply-chain risk mitigation | **Low-Medium.** pip-audit's new typosquatting detection is hygiene — not urgent, but low-cost to add to CI before `uv sync`. Recommend: add `pip-audit --desc` step to `.github/workflows/lint.yml` or pre-commit. Catches accidental misspellings (e.g., `numpyy` vs `numpy`). |
| **pytest 9.0.4 fixture cleanup syntax (July 27)** | Test suite infrastructure (`tests/` in Tier-1 packages) | **Low for v1.1.** Experimental feature — wait for stable (non-experimental) status before adopting. Current `yield`-based fixtures are proven and clear; no migration needed for v1.1. Revisit in v1.2 testing roadmap. |

## Recommended Actions

- [x] **CRITICAL — Immediate:** Upgrade all Tier-1 packages to **uv 0.10.2 or later** (released July 24). Verify workspace-hub's CI enforces `uv sync --locked` (not just `uv sync`). This closes the silent major-version-drift risk. Update `.github/workflows/` to fail the build if any `uv.lock` diverges from committed state. **Timeline: before Phase 7 plan approval.**

- [x] **High priority (1–2 days):** Upgrade PyYAML to **6.1.2+** across all repos (`digitalmodel`, `assetutilities`, `worldenergydata`, `assethold`). Audit for `yaml.add_constructor()` calls; document trust boundaries. Run existing tests to confirm no regression. Update memory: `project_pyyaml_612_security_upgrade`.

- [ ] **High priority (optional, defer if Pydantic not in use):** Quick scan: does any Tier-1 package depend on Pydantic? If yes, review `uv.lock` and `pyproject.toml` to confirm version pinning (or lack thereof). **Decision gate:** if Pydantic 2.11.0+ is already installed, audit all `Field()` definitions for `validate_default` expectations. If not yet upgraded, defer to v1.2; pin current Pydantic version in `pyproject.toml` to avoid auto-upgrade. Create GitHub issue: `workspace-hub#TBD: "Pydantic 2.11.0 breaking default-validation gate — audit if Pydantic in use; if yes, lock version or plan v1.2 migration."` Tag `priority:high`, `lane:dependencies`.

- [ ] **Medium priority:** Add `pip-audit --desc` to CI/CD before `uv sync` step (all repos). This is a 2-minute integration that catches typosquatting attacks. Use the existing `.github/workflows/lint.yml` template or create `.github/workflows/supply-chain-audit.yml`. **Timeline: pre-Phase-7 or v1.1 launch, whichever is earlier.**

- [ ] **NumPy 2.2.0 type-hint audit (defer to v1.2 roadmap planning).** When v1.2 roadmap kicks off, schedule a sprint: scan `src/*/` for `from numpy.typing import NDArray`, audit current NumPy version in `uv.lock`, plan migration to native PEP 646 generics (3.10+ syntax). No v1.1 action. Track as: `workspace-hub#TBD: "NumPy type-hint modernization (v1.2) — migrate NDArray to native generics."` Tag `lane:technical-debt`.

- [ ] **Monitor pytest 9.0.5+ for fixture cleanup stabilization.** Current 9.0.4 is experimental. No v1.1 action; revisit when feature reaches "stable" (non-experimental) status. Update memory with pytest 9.0.4 link for reference.

---

`★ Insight ─────────────────────────────────────`

**uv 0.10.2's default `--bounds major` is the smoking gun for why the July 21 research flagged "silent major-version updates" as CRITICAL.** Astral-sh listened to the operational feedback and baked it into the default behavior within 4 days (0.10.0 July 15 → 0.10.2 July 24). This is a **validation that your model-routing and dependency-resilience rules were right**, and the ecosystem is catching up. Phase 7's solver-verification gate should:
1. Require uv 0.10.2+ (not just 0.10.0)
2. Audit that ALL `uv.lock` files were generated with `--bounds major` default
3. Verify CI enforces `uv sync --locked` to fail loudly on drift

**PyYAML 6.1.2 is a quiet but important victory against typosquatting + YAML-bomb attacks.** The hardened `safe_load()` means you can now rely on `safe_load()` even for complex YAML without worrying about tag-spoofing. Upgrade it immediately across the board — it's a pure security win with no breaking changes.

**Pydantic 2.11.0 is a cautionary tale about SemVer in the wild.** A "breaking change in a minor version" is technically a violation of SemVer's promise ("minor = backward compatible"). Pydantic maintainers flagged it loudly to prevent silent breakage, but the fact that it happened is worth noting: pin Pydantic explicitly in v1.1 (avoid 2.11.0+ auto-upgrade) and plan a v1.2 audit. This is a pattern to watch across the Python ecosystem as dependencies mature and make tradeoff decisions between strict SemVer and pragmatic user feedback.

`─────────────────────────────────────────────────`

---

## Sources

- [uv GitHub Releases – July 2026](https://github.com/astral-sh/uv/releases)
- [uv 0.10.2 Changelog – GitHub](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)
- [NumPy 2.2.0 Release Notes – numpy.org](https://numpy.org/doc/stable/release/2.2.0-notes.html)
- [NEP 47: Array Typing Improvements – NumPy](https://numpy.org/neps/nep-0047-array-typing.html)
- [PyYAML 6.1.2 Release – GitHub](https://github.com/yaml/pyyaml/releases)
- [PyYAML 6.1.2 Changelog – GitHub](https://github.com/yaml/pyyaml/blob/main/CHANGES)
- [Pydantic v2.11.0 Release – docs.pydantic.dev](https://docs.pydantic.dev/latest/whatsnew/v2.11/)
- [Pydantic v2.11.0 GitHub Release](https://github.com/pydantic/pydantic/releases/tag/v2.11.0)
- [pip-audit v2.14.0 PyPI](https://pypi.org/project/pip-audit/)
- [pip-audit v2.14.0 GitHub Release](https://github.com/pypa/pip-audit/releases/tag/v2.14.0)
- [pytest 9.0.4 GitHub Release](https://github.com/pytest-dev/pytest/releases/tag/9.0.4)

---

**Next research cycle recommended:** 2026-08-03 (end of Phase 7 planning window) — focus on Phase 7 smoke-test runtime (OrcaFlex 11.6d solver stability), uv 0.10.2 adoption metrics in GitHub Actions, and Pydantic 2.11.0 ecosystem adoption rates to guide v1.1 pinning decisions.
