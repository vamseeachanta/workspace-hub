# Plan for #2463: aceengineer-website canonical routing surfaces and legacy product-doc reference cleanup

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2463
> **Review artifacts:** scripts/review/results/2026-04-22-plan-2463-claude.md | scripts/review/results/2026-04-22-plan-2463-codex.md | scripts/review/results/2026-04-22-plan-2463-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `aceengineer-website/AGENTS.md` — is a bare pointer to `../AGENTS.md` (workspace-hub), not a repo-specific routing contract. It establishes that a real routing surface is missing, not that the adapter pointer must be deleted.
- Found: `aceengineer-website/README.md` — describes current Vercel deployment, but also carries strategic-planning pointers to root-level `PHASE_4_AND_6_PLAN.md` and `PHASE_6_EXECUTION_CHECKLIST.md`. These two root-level markdowns exist but are not an architecture/routing surface.
- Found: `aceengineer-website/docs/WEBSITE_ARCHITECTURE.md` — short current-state map, Vercel-aligned, acceptable to keep as an architecture surface but not sufficient alone for operator routing.
- Found: `aceengineer-website/docs/DEPLOYMENT_GUIDE.md` — still describes GitHub Pages deployment and references a `deploy.yml` GitHub Actions workflow that no longer exists. This is the primary concrete "legacy missing product-doc reference" the issue targets.
- Found: `aceengineer-website/.github/workflows/` — directory exists but is empty (0 files). `DEPLOYMENT_GUIDE.md:42` references `deploy.yml` as if it were canonical; there is no such file on disk.
- Found: `aceengineer-website/content/`, `blog/`, `case-studies/`, `calculators/`, `scripts/`, `tests/` — all exist on disk and are the real routing surfaces an operator map must cover.
- Gap: no `aceengineer-website/docs/README.md` canonical docs entry point exists.
- Gap: no `aceengineer-website/docs/maps/aceengineer-website-operator-map.md` exists.
- Gap: no freshness-aligned statement in `aceengineer-website/docs/WEBSITE_ARCHITECTURE.md` or README calling out that DEPLOYMENT_GUIDE has been superseded.

### Standards

| Standard | Status | Source |
|---|---|---|
| Control-plane entry point rule (`AGENTS.md` canonical) | existing baseline | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Tier-1 indexing and code-placement contract | proposed under #2460 | `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` |
| File-structure taxonomy starter expectations | existing baseline | `docs/standards/FILE_STRUCTURE_TAXONOMY.md` |

### LLM Wiki pages consulted

- Not applicable — this is a repo-routing/documentation issue, not a domain-knowledge issue.

### Documents consulted

- GitHub issue #2463 — defines scope: remove legacy product-doc references from trusted docs surfaces, add `docs/README.md`, add `docs/maps/aceengineer-website-operator-map.md`, define routing surfaces and minimal freshness checks.
- `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` — aceengineer-website section scored 9/20. Specifically calls out: AGENTS.md is only a pointer; README + DEPLOYMENT_GUIDE still point to legacy missing product-doc refs; no `docs/README.md`; no operator map.
- `docs/reports/tier-1-indexing-freshness-latest.md` — current portfolio status yellow; aceengineer-website listed with the same three concerns, and names #2463 as the follow-through remediation issue.
- `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` — defines the umbrella contract this plan implements for one repo. #2463 is intentionally scoped narrower: concrete routing surfaces for this one repo plus removal of the specific legacy refs identified above.
- Related umbrella #1962 and #2397 — broader tier-1 refactor trees; this issue is a scoped leaf, not a structural rewrite.
- Contract issue #2460 — this plan's concrete surfaces must satisfy the minimum contract the #2460 plan defines (AGENTS.md, README.md, `docs/README.md`, `docs/maps/<repo>-operator-map.md`, source-hygiene rule applicability).

### Gaps identified

- No repo-specific routing contract on `aceengineer-website/AGENTS.md` beyond the adapter pointer.
- No canonical docs entry point at `aceengineer-website/docs/README.md`.
- No operator map at `aceengineer-website/docs/maps/aceengineer-website-operator-map.md`.
- `aceengineer-website/docs/DEPLOYMENT_GUIDE.md` still documents GitHub Pages deployment and references `deploy.yml`, which is the literal legacy missing product-doc pattern the issue targets.
- No minimal validation exists that would catch the reintroduction of those legacy refs on trusted routing surfaces.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-22 via `gh issue view`):
- `#2463` — OPEN — `chore(aceengineer-website): canonical routing surfaces and legacy product-doc reference cleanup`
- `#2460` — OPEN — contract dependency
- `#2465` — OPEN — sibling daily-freshness issue
- `#1962` — OPEN — broader tier-1 refactor umbrella
- `#2397` — OPEN — epic repo-organization tree

**File existence** (from `ls -la` on 2026-04-22):
- EXISTS: `aceengineer-website/AGENTS.md` (pointer-only, 10 lines)
- EXISTS: `aceengineer-website/README.md`
- EXISTS: `aceengineer-website/docs/WEBSITE_ARCHITECTURE.md`
- EXISTS: `aceengineer-website/docs/DEPLOYMENT_GUIDE.md`
- EXISTS: `aceengineer-website/.github/workflows/` (empty directory, 0 files)
- EXISTS: `aceengineer-website/PHASE_4_AND_6_PLAN.md`
- EXISTS: `aceengineer-website/PHASE_6_EXECUTION_CHECKLIST.md`
- EXISTS: `aceengineer-website/content/`, `blog/`, `case-studies/`, `calculators/`, `scripts/`, `tests/`
- MISSING (new — this plan proposes): `aceengineer-website/docs/README.md`
- MISSING (new — this plan proposes): `aceengineer-website/docs/maps/aceengineer-website-operator-map.md`

**Line excerpts** (from `grep -n`):
```
aceengineer-website/docs/DEPLOYMENT_GUIDE.md:3:> Complete step-by-step guide for deploying the static AceEngineer website to GitHub Pages with custom domain
aceengineer-website/docs/DEPLOYMENT_GUIDE.md:6:**Status:** Phase 3 - GitHub Pages Deployment
aceengineer-website/docs/DEPLOYMENT_GUIDE.md:42:**Important:** The GitHub Actions workflow (`deploy.yml`) will automatically handle the deployment when you push to the main branch.
aceengineer-website/README.md:125:**Migrated from**: GitHub Pages (January 2025)
```

**Gap proofs**:
- `ls aceengineer-website/docs/README.md 2>&1` → "No such file or directory" → confirms no canonical docs entry point.
- `ls aceengineer-website/docs/maps/ 2>&1` → "No such file or directory" → confirms operator-map directory does not exist.
- `ls -la aceengineer-website/.github/workflows/` → 0 files → confirms `deploy.yml` is legacy ref, not current file.

<!-- Verification: 6 distinct sources consulted (issue body + scorecard + freshness report + contract plan + control-plane standard + live file inspection). Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2463-aceengineer-website-canonical-routing-and-legacy-ref-cleanup.md` |
| Repo routing contract | `aceengineer-website/AGENTS.md` (expand beyond pointer) |
| Canonical docs entry point | `aceengineer-website/docs/README.md` |
| Operator map | `aceengineer-website/docs/maps/aceengineer-website-operator-map.md` |
| Legacy-ref cleanup targets | `aceengineer-website/README.md`, `aceengineer-website/docs/DEPLOYMENT_GUIDE.md` |
| Architecture pointer | `aceengineer-website/docs/WEBSITE_ARCHITECTURE.md` (minor touch to name the canonical surfaces) |
| Minimal validation | `aceengineer-website/tests/docs/test_routing_surfaces.py` or equivalent repo-local test — exact placement decided at implementation time |
| Plan review — Claude | `scripts/review/results/2026-04-22-plan-2463-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-22-plan-2463-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-22-plan-2463-gemini.md` |

---

## Deliverable

One sentence: a canonical routing triad (`AGENTS.md`, `docs/README.md`, `docs/maps/aceengineer-website-operator-map.md`) inside `aceengineer-website/`, plus removal of the GitHub Pages / `deploy.yml` legacy-reference block from `README.md` and `DEPLOYMENT_GUIDE.md`, so any future issue lands on pages / content / calculators / scripts / tests without rediscovery and no trusted doc advertises a workflow file that does not exist.

---

## Pseudocode

```text
function add_repo_specific_agents_routing():
    keep the adapter pointer header so workspace-hub AGENTS.md stays authoritative
    add a "Routing (repo-specific)" section listing:
        root pages            -> aceengineer-website/*.html
        content               -> aceengineer-website/content/
        blog                  -> aceengineer-website/blog/
        case studies          -> aceengineer-website/case-studies/
        calculators           -> aceengineer-website/calculators/
        scripts               -> aceengineer-website/scripts/
        tests                 -> aceengineer-website/tests/
        architecture doc      -> aceengineer-website/docs/WEBSITE_ARCHITECTURE.md
        operator map          -> aceengineer-website/docs/maps/aceengineer-website-operator-map.md
    add a "Common issue type -> target path hints" table
    do NOT override workspace-hub-level policy, only add repo-specific retrieval info

function create_docs_entry_point():
    write aceengineer-website/docs/README.md with:
        purpose of the docs directory
        list of trusted docs with one-line description per file
        explicit note that DEPLOYMENT_GUIDE.md is either rewritten for Vercel or retired
        link to operator map
        source-hygiene rule: this directory MUST NOT point to files that do not exist

function create_operator_map():
    write aceengineer-website/docs/maps/aceengineer-website-operator-map.md with:
        a table: area | source path | tests path | docs path | common issue labels
        entries for root pages, content, blog, case-studies, calculators, scripts, tests
        a note that the map is the canonical routing surface for this repo

function cleanup_legacy_refs():
    in aceengineer-website/README.md:
        remove or rewrite any block that describes GitHub Pages as the current deployment target
        keep the "Migrated from GitHub Pages (January 2025)" historical note, because it is factual history
        keep links to PHASE_4_AND_6_PLAN.md ONLY if README explicitly labels them as strategic planning, not as architecture authority; otherwise relocate or down-rank those pointers
    in aceengineer-website/docs/DEPLOYMENT_GUIDE.md:
        either (a) replace with a Vercel-accurate short deployment doc, or
               (b) rename to DEPLOYMENT_GUIDE_LEGACY_GITHUB_PAGES.md with a banner saying "Historical only, site deploys via Vercel, see aceengineer-website/docs/README.md"
        remove or disclaim the `deploy.yml` reference on line 42
        implementation agent picks (a) or (b) at execution time; either satisfies the issue

function minimal_validation():
    add a repo-local docs-routing test (pytest in aceengineer-website/tests/... OR a shell check under aceengineer-website/scripts/...)
    the test MUST fail if any of these are true:
        aceengineer-website/docs/README.md does not exist
        aceengineer-website/docs/maps/aceengineer-website-operator-map.md does not exist
        aceengineer-website/README.md still contains an active block describing GitHub Pages as the current deployment target (not just a historical "migrated from" note)
        aceengineer-website/docs/DEPLOYMENT_GUIDE.md still references `deploy.yml` as a current workflow without a legacy banner or rewrite
    the test MUST be fast, local-only, require no network.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `aceengineer-website/AGENTS.md` | add repo-specific routing section below the adapter pointer |
| Create | `aceengineer-website/docs/README.md` | canonical docs entry point |
| Create | `aceengineer-website/docs/maps/aceengineer-website-operator-map.md` | operator map for pages/content/calculators/scripts/tests |
| Modify | `aceengineer-website/README.md` | remove/disclaim active GitHub Pages block; preserve factual "migrated from" note |
| Modify | `aceengineer-website/docs/DEPLOYMENT_GUIDE.md` | rewrite to Vercel OR rename with legacy banner; remove `deploy.yml` active reference |
| Modify | `aceengineer-website/docs/WEBSITE_ARCHITECTURE.md` | add pointer to new `docs/README.md` + operator map (≤5 lines) |
| Create | `aceengineer-website/tests/docs/test_routing_surfaces.py` (or shell equivalent under `aceengineer-website/scripts/`) | minimal regression guard for the four conditions above |
| Update | `docs/plans/README.md` | add this plan's row (workspace-hub index, allowed) |

Notes on scope boundaries:
- This plan **does not** restructure the site, does not touch `aceengineer-website/blog/`, `content/`, `calculators/`, `scripts/` runtime files, and does not change deployment configuration.
- This plan **does not** create or modify workflow files under `aceengineer-website/.github/workflows/`.
- This plan **does not** delete `PHASE_4_AND_6_PLAN.md` / `PHASE_6_EXECUTION_CHECKLIST.md`; the README is free to keep strategic-planning pointers if clearly labeled as such.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_docs_readme_exists` | canonical docs entry point exists and is non-empty | file read | non-empty content |
| `test_operator_map_exists` | operator map file exists and is non-empty | file read | non-empty content |
| `test_operator_map_has_required_areas` | operator map covers root-pages, content, blog, case-studies, calculators, scripts, tests | content scan | all 7 area strings present |
| `test_agents_has_repo_routing_section` | AGENTS.md contains a "Routing (repo-specific)" block beyond the adapter pointer | content scan | section heading present |
| `test_readme_has_no_active_github_pages_block` | README does not advertise GitHub Pages as current deployment target | content scan against explicit discriminator lists below | passes if no banned token appears outside an allowed context |
| `test_deployment_guide_has_no_active_deploy_yml_ref` | DEPLOYMENT_GUIDE.md does not carry an active `deploy.yml` reference without a legacy banner | content scan against explicit discriminator lists below | either rewritten-to-Vercel OR prefixed with a `<!-- LEGACY ... -->` banner block on line 1 |

**Concrete discriminator strings (pinned so two implementation agents produce the same test):**

- `README.md` — **banned active substrings** (fail test if present anywhere outside a heading/paragraph starting with the literal token `Historical:` or `Migrated from`): `Deploy to GitHub Pages`, `GitHub Pages Settings`, `Enable GitHub Pages`, `pages.github.com`.
- `README.md` — **allowed historical substrings** (must not trigger failure): `Migrated from GitHub Pages (January 2025)`, `Historical:`, any occurrence inside a fenced code block documenting prior state.
- `DEPLOYMENT_GUIDE.md` — **banned active substrings** (fail unless the file starts with a legacy banner — see allowed below): ``deploy.yml`` (backticked or bare), `Phase 3 - GitHub Pages Deployment`, `deploying the static AceEngineer website to GitHub Pages`, `Enable GitHub Pages`.
- `DEPLOYMENT_GUIDE.md` — **allowed prefixes** (accept the file if line 1 matches one of these, i.e. rename-with-banner path): `<!-- LEGACY: This document describes the historical GitHub Pages deployment path.`, `# Legacy: GitHub Pages deployment (retired)`.
- `DEPLOYMENT_GUIDE.md` — **rewrite-to-Vercel path sanity check** (only applies if file does NOT start with a legacy banner): file MUST contain each of the literal tokens `Vercel`, `vercel.json`, `CNAME`, and `https://aceengineer.com`, and MUST NOT contain any banned-active substring listed above. Rationale: `aceengineer-website/vercel.json` and `aceengineer-website/CNAME` both already exist on disk, so a rewrite-to-Vercel guide is expected to reference both.
| `test_no_broken_internal_doc_links` | no internal links in the new/edited docs point to nonexistent files | path resolution | all links resolve |

Each test must be deterministic, offline, and completable in under 1 second.

---

## Acceptance Criteria

- [ ] `aceengineer-website/docs/README.md` exists, is non-empty, and lists the trusted docs of this repo.
- [ ] `aceengineer-website/docs/maps/aceengineer-website-operator-map.md` exists and covers root pages, content, blog, case-studies, calculators, scripts, tests.
- [ ] `aceengineer-website/AGENTS.md` contains a repo-specific routing section beyond the adapter pointer.
- [ ] `aceengineer-website/README.md` no longer describes GitHub Pages as the current deployment target (factual "migrated from GitHub Pages (January 2025)" note MAY remain).
- [ ] `aceengineer-website/docs/DEPLOYMENT_GUIDE.md` is either rewritten for Vercel or carries a clear legacy banner at the top and no longer presents `deploy.yml` as a live workflow.
- [ ] A minimal test or shell check enforces the four conditions above and is runnable locally with no network. **Invocation path is pinned, not orphan:** if Python, the test is collectable by `uv run pytest aceengineer-website/tests/docs/ -k routing_surfaces` (and the test function name contains `routing_surfaces`); if bash/shell, the check is referenced by a `## How to verify` section in `aceengineer-website/AGENTS.md` with the exact command (e.g. `bash aceengineer-website/scripts/verify_routing_surfaces.sh`). Rationale (per Claude self-review MINOR #1): prevents the check from landing as an orphan file with no discoverable entrypoint.
- [ ] **Source-hygiene obligation is an explicit no-op for aceengineer-website.** Per the 2026-04-22 tier-1 indexing scorecard, this repo carries no backup artifacts (`*.bak`, `*.orig`, `*_backup*`) or runtime-noise artifacts (`node_modules/` in git, `.DS_Store` tracked, `*.pyc` tracked) under its tracked source tree. The plan inherits the #2460 contract's source-hygiene universal rule, but the regression test for this plan does NOT need to add a source-hygiene assertion here. If #2465's daily audit ever surfaces new source-hygiene drift in aceengineer-website, that is handled as a separate remediation, not a retroactive amendment to this plan.
- [ ] All new/edited docs avoid adding new references to files that do not exist in the repo.
- [ ] `docs/plans/README.md` has a row for this plan.
- [ ] Review artifacts exist under `scripts/review/results/`.

---

## Relationship to the broader repo-ecosystem knowledge layer

- This issue is the aceengineer-website leaf of the tier-1 routing/index wave under #2460 (contract), #2461 (assetutilities), #2462 (digitalmodel), #2464 (workspace-hub).
- Even though aceengineer-website is a GTM/externalization surface, it is still a tier-1 repo in `docs/BUSINESS_BRAIN.md`, so it must satisfy the same minimum routing surfaces as the engineering-core repos.
- The operator map produced here is intentionally the same shape as the planned operator maps for the engineering-core repos, so future multi-repo queries ("where do calculator-related changes live?") can use a consistent retrieval pattern across tier-1.
- #2465 (daily freshness) consumes these surfaces: once they exist, the daily audit has concrete files to check, not vague notions.

---

## Adversarial Review Summary

Two sequential states documented below: r1 (initial single-author Claude self-review, completed 2026-04-22) and post-r1 patches (this rerun, 2026-04-23). Codex and Gemini dispatch remain gated by the session's planning-only permission scope (see memory `feedback_permission_gate_blocks_cross_review.md`); both must be run in a dispatch-capable session before `status:plan-approved`.

### r1 wave (single-author Claude, 2026-04-22)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (local, single-author) | MINOR | 5 findings + 1 NIT: (1) regression-test invocation path unresolved, (2) "active GitHub Pages block" discriminator strings not pinned in TDD row, (3) DEPLOYMENT_GUIDE rewrite-to-Vercel path lacks content sanity check, (4) minimal-validation contract is one-sided (no guard on future creep in new docs), (5) source-hygiene not addressed explicitly for aceengineer-website. NIT: `PHASE_4_AND_6_PLAN.md` at repo root. |
| Codex | NOT RUN (planning-only session) | to be dispatched via `scripts/review/cross-review.sh` once plan is pushed and fresh |
| Gemini | NOT RUN (planning-only session) | same as above |

Review artifact: `scripts/review/results/2026-04-22-plan-2463-claude.md`.

### Post-r1 patches applied in this plan (2026-04-23 rerun)

- **r1 MINOR #1 (invocation path):** acceptance criteria now require the regression test to be collectable by `uv run pytest aceengineer-website/tests/docs/ -k routing_surfaces` if Python, OR referenced by a `## How to verify` section in `aceengineer-website/AGENTS.md` with the exact shell command if bash/shell. Prevents orphan-file landing.
- **r1 MINOR #2 (discriminator strings):** TDD rows for `test_readme_has_no_active_github_pages_block` and `test_deployment_guide_has_no_active_deploy_yml_ref` now reference an inline `Concrete discriminator strings` block listing banned-active substrings (`Deploy to GitHub Pages`, `GitHub Pages Settings`, `deploy.yml`, `Phase 3 - GitHub Pages Deployment`, etc.), allowed-historical substrings (`Migrated from GitHub Pages (January 2025)`, `Historical:`), and allowed legacy-banner prefixes. Two implementation agents now produce the same test.
- **r1 MINOR #3 (rewrite-to-Vercel sanity):** content sanity check added to the discriminator block: a non-banner DEPLOYMENT_GUIDE.md must contain `Vercel`, `vercel.json`, `CNAME`, and `https://aceengineer.com` — all grounded in existing on-disk evidence (`aceengineer-website/vercel.json` and `aceengineer-website/CNAME` both exist).
- **r1 MINOR #5 (source-hygiene no-op):** acceptance criterion now states the source-hygiene obligation for aceengineer-website is explicitly a no-op per the 2026-04-22 scorecard, with the #2465 daily audit as the sustaining loop if future drift appears.
- **r1 MINOR #4 (cross-doc creep guard):** DEFERRED — extending `tests/docs/test_banned_stale_references.py` to cover the new `aceengineer-website/docs/README.md` and operator map is recorded as a post-implementation follow-up, not folded in here, so this plan's scope stays bounded; tracked in the Risks and Open Questions section below.
- **r1 NIT (root-level strategic docs):** DEFERRED — intentionally out of scope; a separate follow-up issue can address `PHASE_4_AND_6_PLAN.md` / `PHASE_6_EXECUTION_CHECKLIST.md` placement.

**Overall result:** DRAFT (post-r1 tightening — PENDING cross-provider re-review). Three of five MINOR findings folded in directly; two documented as deliberate deferrals with rationale. A future dispatch-capable session must run Codex + Gemini before advancing to `status:plan-approved`.

---

## Risks and Open Questions

- **Risk:** the implementation agent may over-interpret "remove legacy product-doc references" and delete historically-useful migration notes. Mitigation: the plan explicitly permits keeping the factual "migrated from GitHub Pages" note, and the regression test only bans *active* GitHub-Pages-as-current language.
- **Risk:** the implementation agent may restructure content/calculator/blog trees. Mitigation: scope boundaries section above forbids this; operator map only documents existing paths.
- **Risk:** the implementation agent may rename `aceengineer-website/AGENTS.md` out of the adapter-pointer shape. Mitigation: the plan explicitly says keep the adapter-pointer header and only extend below it.
- **Open:** should `DEPLOYMENT_GUIDE.md` be rewritten or retired? The plan intentionally permits either path so the implementation agent can pick based on how much Vercel operator content is worth preserving. Both paths satisfy acceptance criteria.
- **Open:** should the minimal-validation test live in `aceengineer-website/tests/` or in workspace-hub `tests/docs/`? This plan prefers repo-local so the test travels with the surface it guards, but defers final placement to implementation.
- **Deferred (r1 MINOR #4):** extending workspace-hub `tests/docs/test_banned_stale_references.py` to cover the new `aceengineer-website/docs/README.md` and `aceengineer-website/docs/maps/aceengineer-website-operator-map.md` is a sensible cross-doc creep guard but intentionally scoped out of this plan to keep surface area bounded. Tracked as a post-implementation follow-up; the #2465 daily freshness audit is the primary sustaining loop that would surface regressions here, so the gap is not silent.

---

## Complexity: T2

**T2** — multi-file documentation contract with regression test, no runtime code changes, no deployment-config changes. Execution fits a single TDD loop. Not T1 because multiple new files plus a regression test are required; not T3 because no cross-repo code changes or architecture decisions are involved.
