# Plan — Issue #2607: Document lxml build dependency for clean-venv smoke installs

**Repo:** digitalmodel | **Tier:** T1 docs | **Author:** Team D (planning) | **Date:** 2026-05-02
**Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2607
**Source:** Validation report on #2566

## 1. Problem statement (verbatim)

`pip install dist/digitalmodel-0.1.1-py3-none-any.whl` in a clean Python 3.13 venv on Ubuntu 25.10 fails with `ERROR: Failed to build 'lxml' when getting requirements to build wheel`. lxml requires native compilation (`libxml2-dev`, `libxslt1-dev`); clean venvs cannot build it without system dev packages. `uv sync` masks the issue because uv resolves a binary wheel.

## 2. Resource intel

### 2.1 lxml declaration

- `digitalmodel/pyproject.toml:62`: `"lxml==4.9.3", # XMLprocessing,` — direct pin in `[project.dependencies]`.
- `src/digitalmodel/visualization/orcaflex_dashboard/backend/requirements.txt:137`: `lxml==4.9.3` — duplicate pin in subcomponent requirements file.
- `src/digitalmodel.egg-info/PKG-INFO:56` and `requires.txt:41` — derived; will regenerate from pyproject.

### 2.2 Use-site inventory (production code)

Located via `grep -rn 'lxml\|from lxml\|import lxml' digitalmodel/src/`.

| File | Usage | Scope |
|---|---|---|
| `src/digitalmodel/gis/io/kml_handler.py:15` | `from lxml import etree` | KML read/write — XPath-heavy |
| `src/digitalmodel/gis/integrations/google_earth_export.py:12` | `from lxml import etree` | KML emission |
| `src/digitalmodel/gis/integrations/temporal_export.py:9` | `from lxml import etree` | KML/time-stamped export |
| `src/digitalmodel/asset_integrity/common/DataFrame_To_doc.py:3` | `import lxml` | Word/HTML doc generation (likely python-docx side-effect) |
| `src/digitalmodel/specialized/finance/stock_analysis/finance_components_get_SEC_data.py:7,275` | `import lxml` + BS4 `features='lxml'` | SEC EDGAR scraping |
| `src/digitalmodel/data_systems/data_scraping/scrapers/equipment_scraper.py:230,255,405` | `BeautifulSoup(html, 'lxml')` | Web scraping |
| `src/digitalmodel/data_systems/data_scraping/scrapers/fender_scraper.py:251` | `BeautifulSoup(response.text, 'lxml')` | Web scraping |
| `src/digitalmodel/infrastructure/utils/visualization/data_extraction.py:305` | `cfg.get('features', 'lxml')` | BS4 parser default |

**Verdict:** 8 use-sites across 4 subsystems (GIS KML, asset_integrity, finance, scrapers). The 3 GIS modules use `etree` directly (XPath, namespace handling) — non-trivial migration to stdlib `xml.etree`. **Option (c) replace is NOT feasible** at issue priority.

### 2.3 Existing docs (canonical surface)

- `digitalmodel/README.md` lines 17–22 — current install section. 6 lines total: `pip install digitalmodel`, "Requires Python 3.10+", link to pyproject.toml.
- `digitalmodel/CONTRIBUTING.md` — does NOT exist.
- `digitalmodel/INSTALL.md` — does NOT exist.
- `digitalmodel/docs/README.md` — exists, no install/system-deps content (verified absent for `libxml2|apt`).

**Convention:** README is the canonical install surface. There is no CONTRIBUTING/INSTALL doc to update.

### 2.4 Adjacent system-dep references

- `pyproject.toml:138`: `pygmt` carries an inline comment `# requires GMT system lib` — precedent that system deps are flagged inline only.
- No top-level "System prerequisites" subsection exists anywhere in the repo's user-facing docs.

## 3. Decision: Option (a) — document

| Option | Verdict | Rationale |
|---|---|---|
| (a) Document `libxml2-dev`/`libxslt1-dev` in README | **PICK** | Lowest-risk, addresses reported bootstrapping break, consistent with `pygmt` precedent, no runtime/dependency-resolution change. |
| (b) Pin a pre-built lxml wheel | Reject for now | lxml ships manylinux wheels for cpython 3.7–3.12 but **not 3.13** as of 2026-05; the failure on Py 3.13 is precisely because no binary wheel exists. Pinning won't help until upstream ships 3.13 wheels. Revisit when lxml ≥5.x publishes 3.13 wheels (already shipped on PyPI for 5.2+; consider unpinning to allow 5.x in a follow-up). |
| (c) Replace lxml with stdlib | Reject | 3 GIS modules call `etree` directly with XPath; equipment/fender scrapers and finance SEC code use BS4-with-lxml-parser idiom. ~8 sites; not "small scope". |

**Forward-looking follow-up (out of scope for #2607):** open a separate issue to bump `lxml==4.9.3` toward `lxml>=5.2` so Py 3.13 binary wheels resolve and option (b) becomes free. That is an upgrade plan, not a doc fix.

## 4. Files to change

| File | Change | Future-tense description |
|---|---|---|
| `digitalmodel/README.md` | Insert `### System prerequisites` subsection inside `## Installation` (after line 22, before `## Quick Start`). | Will list `libxml2-dev`, `libxslt1-dev` for Debian/Ubuntu, with apt one-liner; equivalent dnf line for Fedora/RHEL; brew line for macOS; note that `uv sync` will resolve binary wheels and bypass the requirement. Will explicitly call out Python 3.13 + Ubuntu 25.10 as the verified-broken combo until a follow-up bumps lxml. |
| `digitalmodel/scripts/bash/check-install-prereqs.sh` (NEW) | Optional smoke pre-check. | Will probe for `libxml2-config` + `xslt-config` binaries (proxy for `-dev` packages), print PASS/FAIL per platform. ~30 lines. Surfaces from README install section as an optional verifier. |

**Out of scope for this plan:**
- No change to `pyproject.toml` (no version bump in this issue).
- No change to `src/digitalmodel/visualization/orcaflex_dashboard/backend/requirements.txt` (subcomponent; out of scope for clean-venv top-level smoke install).
- No CI workflow changes (issue is "low" severity, doc-only).

## 5. Acceptance criteria

A.C. 1 — Doc presence: `digitalmodel/README.md` will contain a `### System prerequisites` subsection naming `libxml2-dev` and `libxslt1-dev` with a copy-pasteable apt command.
A.C. 2 — Reproduction loop: an operator on a stock Ubuntu 25.10 image with Python 3.13 will, by following only the README, `apt install` the named packages, then `pip install dist/digitalmodel-0.1.1-py3-none-any.whl` will succeed.
A.C. 3 — Cross-platform note: README will state the macOS and Fedora/RHEL equivalents OR explicitly scope verification to Debian/Ubuntu and decline support claims for other distros (see review §R2).
A.C. 4 — uv sync caveat: README will note that `uv sync`/`uv pip install` resolves manylinux binaries and bypasses this requirement on supported platforms — preserves the existing dev-loop UX.
A.C. 5 — Smoke pre-check (optional): `scripts/bash/check-install-prereqs.sh` will exit 0 when both libs are present, exit 1 with actionable hint otherwise.

## 6. TDD approach (limited surface)

A README change cannot be unit-tested. Substitutes:

1. **Bash smoke script as the test surface**: `scripts/bash/check-install-prereqs.sh` will be the testable artifact. It will be exercised in two manual modes: (i) on a clean Docker `python:3.13-slim` (will exit 1, print the README-aligned remediation), (ii) after `apt install libxml2-dev libxslt1-dev` (will exit 0). Capture both transcripts in the PR description.
2. **Doc-link integrity**: `markdown-link-check` (existing tooling pattern in workspace-hub) will be run against the modified README; new internal anchor links must resolve.
3. **No new pytest target.** Filing a separate issue to add a `tests/integration/test_install_smoke.py` Docker-driven test would be over-scope for #2607.

## 7. Risks and mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Doc-only fix doesn't help GitHub-Actions CI runners that pre-bake images | M | Plan documents in README that the GH Actions Ubuntu 22.04/24.04 base images already ship `libxml2-dev`; CI is unaffected. Verified by ref to `actions/runner-images` software list (will cite link in README). |
| `lxml==4.9.3` is the actual root cause; documenting hides the version-pin defect | M | Plan §3 explicitly flags follow-up to bump lxml; this issue is scoped doc-only per problem statement. |
| Promised platform support exceeds what we test | H | Plan §A.C.3 forces explicit scope: Debian/Ubuntu verified, others "best-effort, untested". (See review §R2.) |
| README bloat — install section becomes long | L | Use a collapsible `<details>` block for cross-platform commands; keep top-of-section to 4 lines. |
| Subcomponent `requirements.txt:137` still pins lxml; mismatched if pyproject ever changes | L | Note in plan that the dashboard backend has its own pin; out of scope here. |

## 8. Implementation steps (future tense)

1. Will draft README diff: add `### System prerequisites` block under `## Installation`.
2. Will draft `scripts/bash/check-install-prereqs.sh` with shellcheck-clean Bash.
3. Will manually validate on a clean Docker `python:3.13-slim`: confirm failure pre-fix, success post-fix; capture both transcripts.
4. Will run `markdown-link-check` on the modified README.
5. Will open PR titled `docs(digitalmodel): document lxml libxml2-dev system prerequisite (#2607)`.
6. Will request cross-review per workspace-hub policy before merge.

## 9. Estimated effort

- README diff: 15 min
- Smoke script: 30 min
- Docker-based verification: 30 min
- PR + cross-review cycle: 1 review round
- **Total:** ~90 min implementation, 1 day calendar including review.

## 10. Open questions

OQ-1. Should we also create a dedicated `docs/install.md` for cross-platform detail, keeping README terse? (Bias: NO — single canonical surface is simpler, matches current convention.)
OQ-2. Should the follow-up `lxml>=5.2` upgrade be filed as a sibling issue now or after this lands? (Bias: file now, link from PR.)
