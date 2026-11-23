# Plan for #2463: aceengineer-website — canonical routing surfaces and legacy product-doc reference cleanup

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2463
> **Review artifacts:** scripts/review/results/2026-04-22-plan-2463-claude.md | scripts/review/results/2026-04-22-plan-2463-codex.md | scripts/review/results/2026-04-22-plan-2463-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `aceengineer-website/AGENTS.md` — 10 lines, a pure pointer (`This repository inherits the canonical contract from: ../AGENTS.md`). Not a repo-specific routing contract.
- Found: `aceengineer-website/README.md` — marketing-oriented doc. Current deploy is declared as Vercel (§"Deployment"). References four legacy `.agent-os/product/*.md` paths that **do not exist** in this repo (§"Documentation", §"Related Resources"). Also references `VERCEL_DEPLOY.md` (exists), `PHASE_4_AND_6_PLAN.md` (exists), `CASE_STUDY_TEMPLATE.md` (exists), `GITHUB_ORG_SETUP.md` (exists), `GOOGLE_ANALYTICS_SETUP.md` (exists).
- Found: `aceengineer-website/docs/WEBSITE_ARCHITECTURE.md` — accurate current-state map of root HTML, `blog/`, `case-studies/`, `calculators/`, `assets/`, `scripts/`, and `tests/python|js`. Short and correct — reuse as authoritative input for the new operator map.
- Found: `aceengineer-website/docs/DEPLOYMENT_GUIDE.md` — 991 lines describing **GitHub Pages** deployment and certain `.agent-os/product/*.md` references. This is architecturally stale: the site was migrated to Vercel in January 2025 (per `README.md` and `VERCEL_DEPLOY.md`). Guide is dated `2026-01-09` and describes GoDaddy→GitHub Pages A-records.
- Found: `aceengineer-website/VERCEL_DEPLOY.md` — concise, status `✅ Active` with "Migrated from GitHub Pages, January 2025" banner. This is the current-state deployment doc.
- Found: `aceengineer-website/docs/DNS_CONFIGURATION.md` — still describes GitHub Pages DNS target; stale.
- Found: `aceengineer-website/docs/modules/README.md` — describes enhanced-create-specs module organization and references `.agent-os/` persistence paths that are not present in this repo.
- Found: `aceengineer-website/docs/modules/agent-os/` — four legacy enhanced-create-specs migration guides.
- Found: `aceengineer-website/docs/` sub-folders — `api/`, `guides/`, `marketing/`, `modules/`; docs: `AI_AGENT_ORCHESTRATION.md`, `HTML_REPORTING_STANDARDS.md`, `LIGHTHOUSE_AUDIT_FINDINGS.md`, `PHASE_4_OPTIMIZATION_CHECKLIST.md`, `SKILLS_REQUIRED.md`.
- Found (routing surfaces):
  - root HTML: `index.html`, `about.html`, `engineering.html`, `energy.html`, `faq.html`, `contact.html`, `pricing.html`, `404.html` (8 pages).
  - `blog/` — 15 HTML posts (e.g., `ai-native-structural-analysis.html`, `cfd-offshore-engineering.html`, `digital-twins-offshore-assets.html`).
  - `case-studies/` — 7 case studies (`bsee-field-economics.html`, `marine-safety-correlation.html`, `offshore-platform-fatigue-optimization.html`, `orcaflex-riser-sensitivity-automation.html`, `subsea-fea-automation.html`, `wind-turbine-foundation-analysis.html`, plus `index.html`).
  - `calculators/` — 4 HTML calculators (`fatigue-life-calculator.html`, `fatigue-sn-curve.html`, `index.html`, `npv-field-development.html`).
  - `demos/`, `methodology/`, `partials/`, `content/` (mirrors root HTML for static-site build).
  - `scripts/` — `competitor_analysis.py`, `content_sync.py`, `cron-setup.sh`, `daily-update.sh`, `generate_field_economics_data.py`, `generate_marine_safety_data.py`, `generate_mpd_charts.py`.
  - `tests/python/` — `conftest.py`, `test_competitor_analysis.py`, `test_content_sync.py`, `test_wrk146_positioning.py`.
  - `tests/js/` — `build.test.js`, `demo-links.test.js`, `hse-risk-dashboard.test.js`, `navbar-toggle.test.js`, `npv-calculator.test.js`, `obs-calculator.test.js`, `wall-thickness.test.js`.
- Gap: `aceengineer-website/docs/README.md` does NOT exist.
- Gap: `aceengineer-website/docs/maps/aceengineer-website-operator-map.md` does NOT exist.
- Gap: `aceengineer-website/.agent-os/` directory does NOT exist, so all `.agent-os/product/*.md` references are broken.
- Gap: no test asserts that referenced internal docs actually exist (broken-link / stale-reference detection).

### Standards

| Standard | Status | Source |
|---|---|---|
| Canonical entry-point contract (`AGENTS.md` is canonical) | existing baseline | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Starter repo taxonomy / top-level hygiene expectations | existing baseline | `docs/standards/FILE_STRUCTURE_TAXONOMY.md` |
| Tier-1 indexing and code-placement contract | **in-flight on this same branch** | `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` |

### LLM Wiki pages consulted
- Not applicable — this is a repo-internal documentation/routing issue, not a domain wiki-content issue.

### Documents consulted
- Issue #2463 body — scope, deliverables, acceptance criteria (canonical docs entry point, operator map, legacy ref cleanup, minimal validation).
- Issue #2460 (OPEN, parent contract) — requires every tier-1 repo to have `AGENTS.md` + `README.md` + `docs/README.md` + `docs/maps/<repo>-operator-map.md` + machine-readable registry + hygiene rules. This plan implements the aceengineer-website slice.
- Issue #2397 (OPEN) — epic umbrella for tier-1 canonical folder structure.
- Issue #1962 (OPEN) — tier-1 refactor umbrella.
- `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` — scores aceengineer-website 9/20 with: weak canonical retrieval, AGENTS pointer only, README/DEPLOYMENT_GUIDE still reference legacy missing product-doc references, no `docs/README.md`, no operator map, `.github/workflows/` empty.
- `aceengineer-website/README.md` — current root README; primary reference surface to edit.
- `aceengineer-website/docs/WEBSITE_ARCHITECTURE.md` — accurate short current-state map; authoritative input for operator map.
- `aceengineer-website/docs/DEPLOYMENT_GUIDE.md` — architecturally stale (GitHub Pages) but factually present; must be retired or rewritten.
- `aceengineer-website/VERCEL_DEPLOY.md` — current deployment authority.
- `workspace-hub/AGENTS.md` — the portfolio contract that `aceengineer-website/AGENTS.md` currently redirects to; this plan does not replace that inheritance, only adds repo-specific override content.
- `.claude/rules/patterns.md` enforcement gradient — new rules land at Level 0 (prose docs) + Level 2 (link-validation script/regression test).

### Gaps identified
- No canonical `docs/README.md` → workers must discover where things live via README (marketing-heavy) or WEBSITE_ARCHITECTURE (short but incomplete for scripts/tests).
- No operator map → no mapping of page/content/calculator/script/test routing at issue-planning time.
- AGENTS.md is a pure pointer → zero repo-specific routing guidance, contradicting #2460's required shape.
- Legacy missing product-doc references (`.agent-os/product/mission.md|tech-stack.md|roadmap.md|decisions.md`) in both `README.md` and `docs/DEPLOYMENT_GUIDE.md` → every new reader is fed broken links.
- `docs/DEPLOYMENT_GUIDE.md` (GitHub Pages) contradicts the live deployment (Vercel) → routing bias toward wrong procedures.
- `docs/DNS_CONFIGURATION.md` still reflects GitHub Pages A-records → stale.
- `docs/modules/README.md` refers to `.agent-os/` context paths that do not exist → hidden rot.
- No automated check that referenced internal docs exist → every future edit can silently reintroduce the same failure mode.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-22 via `gh issue view`):
- `#2463` — OPEN — `chore(aceengineer-website): canonical routing surfaces and legacy product-doc reference cleanup`
- `#2460` — OPEN — `feat(repo-organization): tier-1 indexing and code-placement contract` — parent contract
- `#2397` — OPEN — epic
- `#1962` — OPEN — umbrella

**File existence** (verified in worktree on `nightly/2460-2465-planwave`):
- EXISTS: `aceengineer-website/AGENTS.md` (10 lines, pointer-only)
- EXISTS: `aceengineer-website/README.md`
- EXISTS: `aceengineer-website/docs/WEBSITE_ARCHITECTURE.md`
- EXISTS: `aceengineer-website/docs/DEPLOYMENT_GUIDE.md` (stale — GitHub Pages)
- EXISTS: `aceengineer-website/docs/DNS_CONFIGURATION.md` (stale — GitHub Pages)
- EXISTS: `aceengineer-website/docs/modules/README.md` (references `.agent-os/`)
- EXISTS: `aceengineer-website/VERCEL_DEPLOY.md`
- EXISTS: `aceengineer-website/PHASE_4_AND_6_PLAN.md`, `PHASE_6_EXECUTION_CHECKLIST.md`, `CASE_STUDY_TEMPLATE.md`, `GITHUB_ORG_SETUP.md`, `GOOGLE_ANALYTICS_SETUP.md`
- MISSING: `aceengineer-website/.agent-os/` (entire directory, so all four `.agent-os/product/*.md` refs are broken)
- MISSING (this plan creates): `aceengineer-website/docs/README.md`
- MISSING (this plan creates): `aceengineer-website/docs/maps/aceengineer-website-operator-map.md`
- MISSING (this plan creates): `aceengineer-website/scripts/validate_docs_links.py`
- MISSING (this plan creates): `aceengineer-website/tests/python/test_docs_routing.py`

**Line excerpts proving stale references:**
- `aceengineer-website/README.md` lines 97–100 cite `VERCEL_DEPLOY.md`, `.agent-os/product/mission.md`, `.agent-os/product/tech-stack.md`, `.agent-os/product/roadmap.md` — the three `.agent-os/` paths are all broken because the directory doesn't exist.
- `aceengineer-website/docs/DEPLOYMENT_GUIDE.md` lines 948–951 cite the same four `.agent-os/product/*.md` paths — identically broken, and the entire deployment procedure targets GitHub Pages rather than Vercel.

**Source count**: issue body (1) + #2460 contract plan (2) + scorecard (3) + `aceengineer-website/README.md` (4) + `aceengineer-website/docs/DEPLOYMENT_GUIDE.md` (5) + `aceengineer-website/docs/WEBSITE_ARCHITECTURE.md` (6) + `VERCEL_DEPLOY.md` (7). ≥3 distinct sources — retrieval contract satisfied.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-22-issue-2463-aceengineer-website-canonical-routing.md |
| New canonical docs entry point | aceengineer-website/docs/README.md |
| New operator map | aceengineer-website/docs/maps/aceengineer-website-operator-map.md |
| AGENTS.md upgrade (pointer + repo-specific block) | aceengineer-website/AGENTS.md |
| README.md legacy-ref cleanup | aceengineer-website/README.md |
| Legacy deployment doc retire | aceengineer-website/docs/DEPLOYMENT_GUIDE.md |
| DNS config refresh | aceengineer-website/docs/DNS_CONFIGURATION.md |
| Module README cleanup | aceengineer-website/docs/modules/README.md |
| Link-validation script | aceengineer-website/scripts/validate_docs_links.py |
| Regression test | aceengineer-website/tests/python/test_docs_routing.py |
| Plan review — Claude | scripts/review/results/2026-04-22-plan-2463-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-22-plan-2463-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-22-plan-2463-gemini.md |

---

## Deliverable

After this issue is complete, `aceengineer-website/` will have:
1. a canonical docs entry point (`docs/README.md`) that names the current deployment authority (Vercel), links the operator map, and provides a routing table for pages/content/blog/case-studies/calculators/scripts/tests;
2. an operator map (`docs/maps/aceengineer-website-operator-map.md`) that gives issue-planning-time routing for every major surface;
3. an upgraded `AGENTS.md` that, while still inheriting from the portfolio contract, contains the repo-specific purpose/entry-points/test-command/issue-type-routing block required by #2460;
4. no remaining references to legacy missing `.agent-os/product/*.md` paths in any trusted doc surface;
5. `docs/DEPLOYMENT_GUIDE.md` retired (archived with a supersedes banner pointing at `VERCEL_DEPLOY.md`) so new readers are not routed into the wrong deployment procedure; and
6. a link-validation script plus regression test that fails fast on any reintroduction of broken internal doc refs.

---

## Pseudocode

```
# docs/README.md shape
sections = [
    "Purpose",                     # what this repo is / is not
    "Deployment",                  # Vercel; link VERCEL_DEPLOY.md
    "Routing table",               # issue-type → path hints for pages, content, blog,
                                   # case-studies, calculators, scripts, tests
    "Operator map",                # link docs/maps/aceengineer-website-operator-map.md
    "Testing",                     # tests/python and tests/js entry commands
    "Contributing",                # link AGENTS.md + workspace-hub/AGENTS.md
    "Retired docs",                # explicit pointer to DEPLOYMENT_GUIDE.md archive
]

# docs/maps/aceengineer-website-operator-map.md shape (follow digitalmodel operator map pattern)
sections = [
    "What this map is for",
    "Canonical routing — pages",         # root HTML, content/, blog/, case-studies/, calculators/
    "Canonical routing — scripts",       # scripts/ entries and what each owns
    "Canonical routing — tests",         # tests/python + tests/js
    "Issue-type hints",                  # page edits, blog post, case study, calculator, script, test, SEO
    "Known drift",                       # legacy .agent-os refs, DEPLOYMENT_GUIDE status
]

# AGENTS.md upgrade (still inherits but adds repo-specific block)
header = existing 10-line inheritance block (kept)
add:
    "## Repo-specific routing",
    purpose_line,
    entry_points_block,             # root HTML, content/, blog/, scripts/, tests/
    test_command_block,             # uv run pytest tests/python/ ; npm test
    issue_type_hints_block          # same table as operator map, shortened

# scripts/validate_docs_links.py
# Scope locked: every tracked .md under aceengineer-website/ minus node_modules/ and _archive/
glob_include = "aceengineer-website/**/*.md"
glob_exclude = ["aceengineer-website/node_modules/**", "aceengineer-website/_archive/**"]

for md_file in gitls(glob_include, exclude=glob_exclude):
    for link in parse_markdown_links(md_file):   # parses inline, reference-style, and image links
        if link.is_external():    # scheme:// → skip
            continue
        if link.is_anchor_only(): # "#section" → skip
            continue
        target = link.target_path.split("#", 1)[0]   # drop fragment for file-existence check
        if not path_exists_relative_to(md_file, target):
            yield BrokenLink(md_file, link.line, target)
sys.exit(1 if any broken else 0)
# Exit codes: 0 = clean, 1 = broken links found, 2 = usage/internal error.

# tests/python/test_docs_routing.py
def test_docs_readme_exists_and_covers_surfaces(): ...
def test_operator_map_exists_and_covers_surfaces(): ...
def test_no_dot_agent_os_product_references():
    # Regex banned-prefix guard (tightened per r3 Codex+Claude reviews):
    banned_re = re.compile(r'(?<![A-Za-z])\.agent-os/product/')
    for md in gitls("aceengineer-website/**/*.md",
                     exclude=["aceengineer-website/node_modules/**",
                              "aceengineer-website/_archive/**"]):
        body = read(md)
        assert not banned_re.search(body), f"banned ref in {md}"
def test_no_broken_internal_links():
    assert run("uv run python aceengineer-website/scripts/validate_docs_links.py") == 0
def test_validator_catches_broken_link_in_fixture():
    # Negative-path assertion: fixture under tests/python/fixtures/ has a deliberately
    # broken link; validator must exit non-zero.
    assert run("uv run python aceengineer-website/scripts/validate_docs_links.py "
               "--root aceengineer-website/tests/python/fixtures/broken-link-fixture/") != 0
def test_deployment_guide_replaced_with_stub():
    body = read("aceengineer-website/docs/DEPLOYMENT_GUIDE.md")
    assert len(body.splitlines()) <= 25          # body replaced with short redirect stub
    assert "SUPERSEDED" in body
    assert "VERCEL_DEPLOY.md" in body
def test_agents_md_sentinel_guarded_repo_block():
    body = read("aceengineer-website/AGENTS.md")
    assert "<!-- aceengineer-website:repo-specific:begin -->" in body
    assert "<!-- aceengineer-website:repo-specific:end -->" in body
    assert "## Repo-specific routing" in body
    # Inheritance header preserved
    assert "Contract-Version:" in body
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | aceengineer-website/docs/README.md | canonical repo docs entry point with routing table |
| Create | aceengineer-website/docs/maps/aceengineer-website-operator-map.md | operator map for pages/content/scripts/tests |
| Modify | aceengineer-website/AGENTS.md | retain inheritance header; add repo-specific routing block wrapped in sentinel markers `<!-- aceengineer-website:repo-specific:begin -->` … `<!-- aceengineer-website:repo-specific:end -->` so the workspace-hub adapter regenerator can preserve it across future regenerations (addresses r3 Codex+Gemini-stance P2 on regenerator conflict) |
| Modify | aceengineer-website/README.md | remove every `.agent-os/product/*.md` reference (exact strings: `.agent-os/product/mission.md`, `.agent-os/product/tech-stack.md`, `.agent-os/product/roadmap.md`, `.agent-os/product/decisions.md`); insert one pointer to `docs/README.md`; keep valid refs (`VERCEL_DEPLOY.md`, `PHASE_4_AND_6_PLAN.md`, etc.) |
| Modify | aceengineer-website/docs/DEPLOYMENT_GUIDE.md | **replace body with ≤25-line redirect stub** (not just a top banner, per r3 Codex-stance P1). Stub: `> **SUPERSEDED (2026-04-22) — superseded by #2463** — canonical deploy doc is now [VERCEL_DEPLOY.md](../VERCEL_DEPLOY.md). The original 991-line GitHub Pages procedure is preserved at `aceengineer-website/_archive/docs/DEPLOYMENT_GUIDE.md-2026-04-22.md`.` Then move the original body verbatim to that archive path in the same commit. Do NOT rewrite the GitHub Pages procedure into a Vercel procedure (still out of scope). |
| Modify | aceengineer-website/docs/DNS_CONFIGURATION.md | **replace body with ≤25-line redirect stub** pointing at `VERCEL_DEPLOY.md`'s DNS section; original body archived to `aceengineer-website/_archive/docs/DNS_CONFIGURATION.md-2026-04-22.md` (same pattern as DEPLOYMENT_GUIDE.md) |
| Create | aceengineer-website/_archive/docs/DEPLOYMENT_GUIDE.md-2026-04-22.md | archived original body of `docs/DEPLOYMENT_GUIDE.md` (history preservation after redirect-stub replace) |
| Create | aceengineer-website/_archive/docs/DNS_CONFIGURATION.md-2026-04-22.md | archived original body of `docs/DNS_CONFIGURATION.md` |
| Modify | aceengineer-website/docs/modules/README.md | delete the `.agent-os/` directory references outright (that directory was removed at Phase 1 per `README.md` §"Phase 1 Completed"); add a one-line note that enhanced-create-specs infra is not currently wired in this repo |
| Modify | aceengineer-website/scripts/daily-update.sh | invoke `uv run python scripts/validate_docs_links.py` as a step; fail the cron run if the script exits non-zero (addresses r3 Gemini-stance P1 on freshness cadence) |
| Modify | data/document-index/intelligence-accessibility-registry.yaml | register `aceengineer-website/docs/README.md` as an L2 `entry-point` asset AND `aceengineer-website/docs/maps/aceengineer-website-operator-map.md` as an L2 `map` asset; both with `owner_issue: 2463`, `freshness_cadence: weekly`, `discoverability: discoverable`, `validator: aceengineer-website/scripts/validate_docs_links.py` (addresses r3 Gemini-stance P1 on missing registry entry + discoverability wiring) |
| Create | aceengineer-website/scripts/validate_docs_links.py | walks `aceengineer-website/**/*.md` (excluding `node_modules/**` and `_archive/**`); handles inline, reference-style, and image links; skips `http(s)://`/mailto/anchor-only links; drops fragments before file-existence check; exits 0/1/2 (clean/broken-found/internal-error). Scope broadened per r3 Codex-stance P1. |
| Create | aceengineer-website/tests/python/test_docs_routing.py | regression over the creates/updates above — includes fixture-based negative-path assertion |
| Create | aceengineer-website/tests/python/fixtures/broken-link-fixture/broken.md | deliberately-broken-link fixture consumed by `test_validator_catches_broken_link_in_fixture` |

Out of scope for this plan (explicit):
- Rewriting the GitHub Pages procedure in `DEPLOYMENT_GUIDE.md` into a Vercel procedure — `VERCEL_DEPLOY.md` already exists and is authoritative; this plan retires + archives the stale guide only.
- Cleaning up `aceengineer-website/docs/modules/agent-os/` (four enhanced-create-specs migration guides) — follow-on; link at execution time.
- Restoring a real `.agent-os/` directory — `.agent-os/` was deliberately removed at Phase 1 (per `README.md` §"Phase 1 Completed"); this plan removes references to it, not the directory.
- Cleaning up the content of `PHASE_4_AND_6_PLAN.md`, `PHASE_6_EXECUTION_CHECKLIST.md`, `GITHUB_ORG_SETUP.md`, etc. — these still exist and are referenced; their freshness is a separate concern. The new link validator will cover broken internal links inside those files as a byproduct; stale-but-valid content remains out of scope.
- Populating empty `.github/workflows/` (scorecard finding) — separate CI hardening issue. The validator's `daily-update.sh` integration provides the freshness cadence without a new CI workflow.
- Replacing the workspace-hub AGENTS adapter regenerator — this plan uses sentinel markers to coexist with whatever the regenerator does today; refactoring the regenerator to honor overlay files is out of scope.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_docs_readme_exists_and_has_required_sections | `aceengineer-website/docs/README.md` exists and contains headings "Purpose", "Deployment", "Routing table", "Operator map", "Testing", "Contributing", "Retired docs" | repo at HEAD | pass |
| test_operator_map_exists_and_covers_surfaces | `aceengineer-website/docs/maps/aceengineer-website-operator-map.md` exists and mentions pages, content, blog, case-studies, calculators, scripts, tests | repo at HEAD | pass |
| test_agents_md_sentinel_guarded_repo_block | `aceengineer-website/AGENTS.md` contains both sentinel markers AND a `## Repo-specific routing` section AND retains the `Contract-Version` inheritance header | repo at HEAD | pass |
| test_no_broken_internal_links_in_all_aceeng_md | `aceengineer-website/scripts/validate_docs_links.py` exits 0 over the broadened scope (`aceengineer-website/**/*.md` minus `node_modules/**` and `_archive/**`) | repo at HEAD | pass |
| test_validator_catches_broken_link_in_fixture | validator exits non-zero over `aceengineer-website/tests/python/fixtures/broken-link-fixture/` (negative-path assertion) | repo at HEAD | pass |
| test_no_dot_agent_os_product_references_regex | every tracked `aceengineer-website/**/*.md` (minus `node_modules/**`, `_archive/**`) is regex-checked against `(?<![A-Za-z])\.agent-os/product/` — tightened from substring-based per r3 reviews | repo at HEAD | pass |
| test_deployment_guide_replaced_with_stub | `aceengineer-website/docs/DEPLOYMENT_GUIDE.md` has ≤25 lines and contains both "SUPERSEDED" and a link to `VERCEL_DEPLOY.md` (hard-retire replaces soft banner per r3 Codex-stance P1) | repo at HEAD | pass |
| test_deployment_guide_archive_preserved | `aceengineer-website/_archive/docs/DEPLOYMENT_GUIDE.md-2026-04-22.md` exists and contains the `# AceEngineer.com Deployment Guide` header from the original body | repo at HEAD | pass |
| test_dns_configuration_replaced_with_stub | `aceengineer-website/docs/DNS_CONFIGURATION.md` has ≤25 lines and links `VERCEL_DEPLOY.md`; archive file exists | repo at HEAD | pass |
| test_operator_map_covers_all_calculators | operator map mentions each of the 4 calculator HTML files currently in `calculators/` | repo at HEAD | pass |
| test_registry_entries_for_new_surfaces | `data/document-index/intelligence-accessibility-registry.yaml` has entries for `aceengineer-website/docs/README.md` and `aceengineer-website/docs/maps/aceengineer-website-operator-map.md` with the required fields | repo at HEAD | pass |
| test_daily_update_invokes_validator | `aceengineer-website/scripts/daily-update.sh` contains an invocation of `validate_docs_links.py` with a fail-on-nonzero wrapper | repo at HEAD | pass |
| test_sibling_python_tests_still_pass | `uv run pytest aceengineer-website/tests/python/` passes — protects `test_wrk146_positioning.py` et al. from accidental breakage | repo at HEAD | pass |

---

## Acceptance Criteria

- [ ] **#2460 merge gate:** #2460's canonical contract doc is merged to `main` (not merely the nightly branch) OR the contract's required-section list is captured verbatim as a constant the regression test consumes. (Promoted from Risks → Acceptance per r3 Gemini-stance P2.)
- [ ] `aceengineer-website/docs/README.md` exists and contains the required sections.
- [ ] `aceengineer-website/docs/maps/aceengineer-website-operator-map.md` exists and covers pages, content, blog, case-studies, calculators, scripts, tests.
- [ ] `aceengineer-website/AGENTS.md` retains inheritance header AND wraps a repo-specific routing block in the `<!-- aceengineer-website:repo-specific:begin -->` … `<!-- aceengineer-website:repo-specific:end -->` sentinels.
- [ ] `aceengineer-website/README.md` no longer references `.agent-os/product/*.md` anywhere (regex-verified).
- [ ] `aceengineer-website/docs/DEPLOYMENT_GUIDE.md` is a ≤25-line redirect stub pointing at `VERCEL_DEPLOY.md`; original body preserved at `_archive/docs/DEPLOYMENT_GUIDE.md-2026-04-22.md`.
- [ ] `aceengineer-website/docs/DNS_CONFIGURATION.md` is a ≤25-line redirect stub pointing at `VERCEL_DEPLOY.md`; original body preserved at `_archive/docs/DNS_CONFIGURATION.md-2026-04-22.md`.
- [ ] `aceengineer-website/docs/modules/README.md` no longer references `.agent-os/` paths that do not exist.
- [ ] `aceengineer-website/scripts/validate_docs_links.py` exits 0 over `aceengineer-website/**/*.md` (minus `node_modules/**`, `_archive/**`) AND exits non-zero when run against the broken-link fixture.
- [ ] `aceengineer-website/scripts/daily-update.sh` invokes the validator and fails the cron run on non-zero exit.
- [ ] `data/document-index/intelligence-accessibility-registry.yaml` has entries for both new surfaces (`docs/README.md` as `entry-point`, operator map as `map`), both with `owner_issue: 2463`, `freshness_cadence: weekly`, `discoverability: discoverable`.
- [ ] `uv run pytest aceengineer-website/tests/python/test_docs_routing.py -v` passes.
- [ ] `uv run pytest aceengineer-website/tests/python/ -v` shows no regression in sibling tests (`test_competitor_analysis`, `test_content_sync`, `test_wrk146_positioning`).
- [ ] Plan-review artifacts posted to `scripts/review/results/`.

---

## Adversarial Review Summary

<!-- Populated 2026-04-22 from r3 single-author review. Cross-review CLI (scripts/review/cross-review.sh) blocked in the planning-only sandbox (memory feedback_permission_gate_blocks_cross_review.md); three independent defect-hunting passes executed with transparent provenance in each artifact. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (completeness/evidence stance) | MINOR | Banner-retire of DEPLOYMENT_GUIDE is soft; validator scope excludes top-level MDs; substring-based banned-ref test is fragile; operator-map shape not locked to digitalmodel exemplar. |
| Codex (defect-hunting stance) | MINOR | P1: banner-retire leaves 991 lines of stale GitHub Pages procedure in-tree. P1: validator scope is an arbitrary subset. P2: AGENTS.md regenerator will clobber the repo-specific block; validator edge cases (fragments, anchors, images) underspecified; banned-ref test substring-fragile; DNS banner does not replace body; no validator fixture spec. |
| Gemini (architectural-fit stance) | MINOR | P1: new surfaces lack freshness mechanism → same class of defect the scorecard flags for `CONTENT_INDEX.md`. P2: #2460 dependency only in Risks, not Acceptance; AGENTS.md edit conflicts with adapter regenerator contract; new surfaces not registered in accessibility registry; calculator-list asymmetry undocumented. |

**Overall result:** MINOR across all three stances → approval-ready. Plan tightened in one additional pass to internalize all four P1 findings rather than ship them as open risks.

Revisions made based on review:
- **Hard retire (Codex P1):** `DEPLOYMENT_GUIDE.md` and `DNS_CONFIGURATION.md` are now replaced by ≤25-line redirect stubs; original bodies archived under `aceengineer-website/_archive/docs/*-2026-04-22.md`. Tests updated: `test_deployment_guide_replaced_with_stub`, `test_deployment_guide_archive_preserved`, `test_dns_configuration_replaced_with_stub`.
- **Validator scope broadened (Codex P1):** walks `aceengineer-website/**/*.md` (minus `node_modules/**`, `_archive/**`) rather than the arbitrary README+AGENTS+docs subset. Edge cases (fragments, anchors, images, malformed) enumerated in pseudocode with explicit exit codes 0/1/2.
- **Registry entries added (Gemini P1):** Files-to-Change now modifies `data/document-index/intelligence-accessibility-registry.yaml` to register both new surfaces with `owner_issue: 2463`, `freshness_cadence: weekly`, `validator: …validate_docs_links.py`. `test_registry_entries_for_new_surfaces` asserts this.
- **Freshness cadence wired (Gemini P1):** `aceengineer-website/scripts/daily-update.sh` now invokes the validator with fail-on-non-zero, giving the new surfaces a daily-refresh signal. `test_daily_update_invokes_validator` asserts this.
- **Sentinel-guarded AGENTS.md block (Codex+Gemini P2):** repo-specific routing block wrapped in `<!-- aceengineer-website:repo-specific:begin -->` … `<!-- aceengineer-website:repo-specific:end -->` so the adapter regenerator can preserve it. `test_agents_md_sentinel_guarded_repo_block` asserts both markers + the Contract-Version inheritance header.
- **Banned-ref test tightened (Codex+Claude P2/P3):** substring check replaced by regex `(?<![A-Za-z])\.agent-os/product/` applied to the broadened scope.
- **#2460 gate promoted to Acceptance (Gemini P2):** merge gate now a checkbox, not just a risk.
- **Validator fixture specified:** negative-path assertion fixture committed under `aceengineer-website/tests/python/fixtures/broken-link-fixture/broken.md`.
- **Sibling tests protected:** dedicated `test_sibling_python_tests_still_pass` keeps `test_wrk146_positioning.py` et al. green.
- **`docs/modules/README.md`:** `remove or correct` replaced with the concrete disposition "delete the .agent-os/ references outright; add a one-line historical note".

---

## Risks and Open Questions

- **Risk (highest) — #2460 not yet merged.** Now gated in Acceptance Criteria (first checkbox). Mitigation still the same: hard gate — do NOT merge until #2460 lands on `main` OR the required-sections list is captured as a verbatim constant the regression test consumes.
- **Risk — AGENTS.md adapter regenerator may still strip the sentinel-guarded block.** The workspace-hub adapter regenerator has not been inspected by this plan. If it rewrites `AGENTS.md` wholesale and does not honor the sentinels, the repo-specific block disappears on the next regeneration. Mitigation: the regression test runs nightly via `daily-update.sh`; a missing sentinel/block fails fast and a follow-on can teach the regenerator to overlay the block.
- **Risk — `_archive/docs/*.md` growth.** This plan writes two archive files; future retires will grow the archive indefinitely. Mitigation: archive paths are dated, so cleanup can proceed by age; a future tier-1 archive-hygiene plan can compress older archives without breaking links.
- **Risk — `aceengineer-website/tests/python/` has a `test_wrk146_positioning.py`.** Its name references a WRK ID, which per memory `feedback_no_reserved_wrk_ids` is deprecated; per memory `feedback_check_parallel_work` another session may be touching it. Mitigation: `test_sibling_python_tests_still_pass` asserts the full sibling suite passes, protecting against accidental breakage.
- **Risk — blog/case-studies/calculators churn.** These surfaces grow frequently; an operator map that enumerates every file will go stale. Mitigation: the operator map enumerates **directories and naming conventions**, not individual files, except for calculators (small, stable set) where the regression test locks the full list. Documented explicitly inside the operator map to avoid ambiguity.
- **Risk — validator edge cases.** Image links, reference-style links, anchors, malformed markdown can produce false positives or silent passes. Mitigation: pseudocode enumerates the handling for each case, and the fixture-based negative-path test exercises at least one broken link end-to-end.
- **Open → closed** — AGENTS.md content: sentinel-guarded repo-specific block below the inheritance header (so the 10-line pointer discipline survives while #2460 compliance is added and regenerator coexistence is preserved).
- **Open → closed** — Should we physically archive `DEPLOYMENT_GUIDE.md` / `DNS_CONFIGURATION.md`? **Yes** — this revision promotes the hard retire + date-stamped archive pattern.
- **Open → closed** — Is `aceengineer-website/.github/workflows/` in scope for CI wiring? **No** — daily-update.sh invocation provides the freshness cadence without a new CI workflow; populating `.github/workflows/` is a separate issue.

---

## Complexity: T2

**T2** — Multiple file creates + multiple targeted modifies + one new script + one new test module. Touches 9 files across the repo. No new automation hooks; the validator lands at the Level-2 script tier per `.claude/rules/patterns.md`. Coupling to #2460 adds coordination risk but is managed with the same hard gate as the #2464 sibling plan.
