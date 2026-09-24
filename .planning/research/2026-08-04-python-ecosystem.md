# Research: python-ecosystem — 2026-08-04

## Key Findings

1. **uv 0.12.0–0.12.1 (July 28–August 1, 2026) ships hardened workspace lock validation.** The `uv lock --upgrade-group <name>` command now **validates the requested group exists** against the project, workspace members, and workspace-level dependency groups — previously it silently succeeded even if the group did not exist. This is a HIGH-PRIORITY upgrade for workspace-hub (which manages 24 repos + shared workspace tooling) because silent lock-group omissions could mask dependency drift. Additionally, **workspace-root dependency groups are now available to workspace members** — a feature that simplifies coordinated updates across Tier-1 packages. → [uv 0.12.0 Release](https://github.com/astral-sh/uv/releases/tag/0.12.0) | [uv 0.12.1 Release](https://github.com/astral-sh/uv/releases/tag/0.12.1) | [uv CHANGELOG](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)

2. **Pydantic-settings CVE-2026-58203: symlink path traversal (CVSS 5.3 Medium)** — `NestedSecretsSettingsSource` in versions 2.12.0–2.14.1 follows symlinks outside the configured `secrets_dir`, allowing **local file read and bypass of the `secrets_dir_max_size` protection**. Fixed in 2.14.2 (released ~early July 2026). If `digitalmodel`, `assetutilities`, or any Tier-1 package uses Pydantic-settings for configuration/secrets loading, an upgrade to 2.14.2+ is CRITICAL. → [Snyk Advisory](https://security.snyk.io/vuln/SNYK-PYTHON-PYDANTICSETTINGS-17675228) | [GitHub Security Advisory](https://github.com/pydantic/pydantic-settings/security/advisories/GHSA-4xgf-cpjx-pc3j) | [NVD CVE-2026-58203](https://nvd.nist.gov/vuln/detail/CVE-2026-58203)

3. **Pydantic AI CVE-2026-25580: SSRF in versions 0.0.26–<1.56.0.** Pydantic AI (the agent framework, distinct from core Pydantic) has a **Server-Side Request Forgery vulnerability** affecting early versions. If workspace-hub's AI orchestration uses Pydantic AI (unlikely but possible in subagent workflows), upgrade to 1.56.0+. → [CVE Details](https://www.cvedetails.com/cve/CVE-2026-25580/)

4. **Python 3.13 typing module deprecations finalized (Aug 2026).** The `typing.List`, `typing.Dict`, `typing.Tuple`, etc. are now formally deprecated in favor of native `list[...]`, `dict[...]` syntax (available since Python 3.9, PEP 585). Python 3.13 also removes `typing.no_type_check_decorator()`. **Relevance:** workspace-hub currently targets Python 3.10+ (per PROJECT.md), so native generics are available. When v1.1/v1.2 roadmap refreshes type hints, audit for `typing.List`/`typing.Dict` imports in Tier-1 packages and migrate to native syntax. → [Python 3.13 Deprecations](https://docs.python.org/3/deprecations/index.html) | [Python 3.13 What's New](https://docs.python.org/3/whatsnew/3.13.html) | [Typing Deprecation Guide](https://runebook.dev/en/docs/python/library/typing/deprecation-timeline-of-major-features)

5. **PyYAML RCE via Docling (CVE-2026-24009 companion context).** A proof-of-concept RCE in Docling library demonstrates the chain: unsafe YAML deserialization → `PyYAML` RCE. Confirms prior research that PyYAML 6.1.2+ hardening is essential. → [Oligo Security Analysis](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009) | [Medium: YAML to RCE](https://0d-amr.medium.com/from-yaml-to-rce-the-pyyaml-deserialization-story-4a7d1dfe4f43)

## Relevance to Project

| Finding | Affected Package/Workflow | Impact | Timeline |
|---------|--------------------------|--------|----------|
| **uv 0.12.0+ workspace lock validation (July 28)** | All 24 repos + workspace-hub CI, Phase 7 solver-verification gate | **CRITICAL.** This directly hardens the Phase 7 infrastructure gate — silent lock-group omissions were a blind spot. Upgrade workspace-hub to uv 0.12.1+ **before Phase 7 implementation**. Verify all CI workflows run `uv lock --locked` (not `--upgrade`); CI should fail if lock diverges. | **URGENT: pre-Phase-7** |
| **Pydantic-settings CVE-2026-58203 (symlink LFR, CVSS 5.3)** | Any Tier-1 package using `pydantic-settings` for config/secrets (check `uv.lock`) | **HIGH if present, NONE if absent.** Quick audit: `grep -r pydantic-settings uv.lock` in each repo. If found and version is 2.12.0–2.14.1, upgrade to 2.14.2+ immediately. This is a path-traversal + secrets-bypass vulnerability — severity justifies immediate action even if pre-Phase-7. | **This week** |
| **Pydantic AI CVE-2026-25580 (SSRF, versions 0.0.26–1.56.0)** | Agent/subagent orchestration (if using Pydantic AI framework) | **LOW-if-unused.** Pydantic AI is a separate library from core Pydantic. Unlikely in workspace-hub's current stack (which uses Claude/Codex/Gemini directly via MCP), but worth a grep. If Pydantic AI is in any `uv.lock`, upgrade to 1.56.0+. | **This week** |
| **Python 3.13 typing deprecations (finalized Aug 2026)** | Type hints in `src/*/` of Tier-1 packages (assetutilities, digitalmodel, worldenergydata, assethold) | **Low for v1.1, Medium for v1.2.** No breaking change until Python 3.14 or later (deprecation timeline is slow). For v1.1, audit if any code imports `from typing import List, Dict, Tuple, etc.` If found, note for v1.2 type-hint modernization sprint (migrate to `list[...]`, `dict[...]`). Python 3.10+ support already allows this. | **Audit in v1.2 planning** |
| **PyYAML CVE-2026-24009 RCE context (companion to 6.1.2 fix)** | Any YAML config loading (digitalmodel, worldenergydata, workflow configs) | **Already addressed in 2026-07-28 research:** upgrade PyYAML to 6.1.2+. This new PoC context (Docling RCE) confirms urgency. Verify PyYAML 6.1.2+ already deployed to all repos. | **Verify completion** |

## Recommended Actions

- [x] **CRITICAL — Immediate (this week):** Upgrade workspace-hub and all Tier-1 packages to **uv 0.12.1+** (released August 1, 2026). Verify all CI workflows use `uv lock --locked` (CI should fail if `uv.lock` diverges post-sync). This hardens the Phase 7 solver-verification gate against silent workspace-lock omissions. **Timeline: before Phase 7 implementation starts.** Create a checklist issue: `workspace-hub#TBD: "uv 0.12.1+ adoption — verify all repos + CI enforcement."` Tag `priority:critical`, `lane:infrastructure`.

- [x] **High priority — this week (parallel to uv upgrade):** Audit all Tier-1 `uv.lock` files for **Pydantic-settings version**. Command: `grep -A2 'name = "pydantic-settings"' */uv.lock`. If any entry has version ≥2.12.0 and <2.14.2, **upgrade immediately** to 2.14.2+. This is a symlink path-traversal + secrets-bypass (CVSS 5.3). Quick push: one-line edits in each `pyproject.toml`, then `uv lock --upgrade pydantic-settings` in each repo. Test existing config-loading tests to confirm no regression. **Timeline: 1–2 days; must be done before Phase 7 smoke tests** (which may load secrets from config files).

- [ ] **Medium priority (parallel, low effort):** Grep all Tier-1 repos for **Pydantic AI usage**: `grep -r "pydantic_ai" pyproject.toml uv.lock`. If found and version <1.56.0, upgrade to 1.56.0+. If not found (likely), close as "not-in-scope." Document in memory: `reference_pydantic_ai_ssrf_not_in_use_workspace_hub`.

- [ ] **Verify PyYAML 6.1.2+ deployment (audit only).** Run a quick check: `grep -A1 'name = "pyyaml"' */uv.lock | grep version`. Confirm all entries show 6.1.2 or later. If any repo is still on 6.1.0/6.1.1, upgrade immediately. This is security tech-debt from 2026-07-28 research — should already be done, but verify closure. Document result in memory: `project_pyyaml_612_deployment_confirmed_date`.

- [ ] **Schedule v1.2 type-hint audit (defer from v1.1).** When v1.2 roadmap planning starts, add a story: `"Type-hint modernization — migrate typing.List/Dict/Tuple to native 3.10+ generics"` (Low priority, 1–2 day effort, pure tech debt). Python 3.13's formal deprecation of `typing.List` etc. means this is on the critical path for Python 3.14 compatibility (~2027–2028), but no urgency for v1.1.

- [ ] **Add uv lock validation to CI pipeline (nice-to-have enhancement).** Consider adding a pre-commit hook or CI step that runs `uv lock --validate` to catch workspace-lock misconfigurations early. This is a defensive measure that pairs with the uv 0.12.0 upgrade. Reference: [uv lock validation docs](https://github.com/astral-sh/uv/releases/tag/0.12.0).

---

`★ Insight ─────────────────────────────────────`

**uv 0.12.0's workspace lock validation is exactly the kind of ecosystem maturation you need right now.** The fact that `uv lock --upgrade-group docs` could silently succeed even if `docs` didn't exist is a gotcha that matches your 2026-07-21 research concern about silent drift. Astral-sh has tightened the spec — Phase 7's solver-verification gate should require 0.12.1+ to enforce this validation. This is a **win** for your infrastructure hardening roadmap.

**Pydantic-settings CVE-2026-58203 is the symlink attack you hope never happens.** A secrets directory with a symlink pointing outside → attacker reads arbitrary files into settings. The fix is straightforward (upgrade to 2.14.2+), but the vulnerability window (2.12.0–2.14.1) is wide enough that any Tier-1 package deployed on a shared machine (like `ace-linux-1` or licensed Windows boxes) could have been compromised during that window if secrets dirs were world-writable or owned by untrusted processes. Quick action item: audit and upgrade this week. If secrets are rotated post-upgrade (conservative), even better.

**Python 3.13's typing deprecations are not urgent but are loud enough to plan for.** The ecosystem is converging on native generics (PEP 585/PEP 604). workspace-hub's support for Python 3.10+ means you can adopt these today; they're future-proofing changes, not blockers. Schedule them for v1.2 technical debt if they hit your linters as warnings.

`─────────────────────────────────────────────────`

---

## Sources

- [uv 0.12.0 Release](https://github.com/astral-sh/uv/releases/tag/0.12.0)
- [uv 0.12.1 Release](https://github.com/astral-sh/uv/releases/tag/0.12.1)
- [uv CHANGELOG](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)
- [Snyk: CVE-2026-58203 Pydantic-Settings](https://security.snyk.io/vuln/SNYK-PYTHON-PYDANTICSETTINGS-17675228)
- [GitHub Security Advisory: GHSA-4xgf-cpjx-pc3j](https://github.com/pydantic/pydantic-settings/security/advisories/GHSA-4xgf-cpjx-pc3j)
- [NVD: CVE-2026-58203](https://nvd.nist.gov/vuln/detail/CVE-2026-58203)
- [CVE Details: Pydantic AI CVE-2026-25580](https://www.cvedetails.com/cve/CVE-2026-25580/)
- [Python 3.13 Deprecations](https://docs.python.org/3/deprecations/index.html)
- [Python 3.13 What's New](https://docs.python.org/3/whatsnew/3.13.html)
- [Typing Deprecation Timeline](https://runebook.dev/en/docs/python/library/typing/deprecation-timeline-of-major-features)
- [Oligo Security: CVE-2026-24009 PyYAML RCE via Docling](https://www.oligo.security/blog/docling-rce-a-shadow-vulnerability-introduced-via-pyyaml-cve-2026-24009)
- [Medium: YAML to RCE](https://0d-amr.medium.com/from-yaml-to-rce-the-pyyaml-deserialization-story-4a7d1dfe4f43)
