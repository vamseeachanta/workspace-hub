# Adversarial Plan Review Request: Issue #2460

You are an adversarial reviewer. Assume the plan has defects until proven otherwise.
Do not praise. Do not restate the plan. Focus only on what is wrong, missing, risky, contradictory, or insufficiently evidenced.
Return APPROVE only after affirmatively verifying correctness-critical claims. When in doubt, return MINOR or MAJOR.
Each finding must cite a specific file path, plan section, quoted claim, or missing artifact.
If you find no problems, explicitly state what you checked.

## Review target
- Issue: #2460 feat(repo-organization): tier-1 indexing and code-placement contract
- Review stage: PLAN REVIEW
- Repository: /mnt/local-analysis/workspace-hub

## Context
This issue is intentionally narrower than #2397 and #1962. It should define a reusable contract for trusted tier-1 routing/index surfaces, not perform repo-specific implementation or daily-automation implementation directly.
Child issues already filed:
- #2461 assetutilities routing surfaces and source-hygiene cleanup
- #2462 digitalmodel repo-wide routing surfaces
- #2463 aceengineer-website routing surfaces cleanup
- #2464 workspace-hub curated routing index cleanup
- #2465 daily tier-1 indexing freshness audit and scorecard refresh

Known baseline evidence the plan is supposed to reflect:
- docs/standards/CONTROL_PLANE_CONTRACT.md makes AGENTS.md the canonical repo entry point.
- docs/standards/FILE_STRUCTURE_TAXONOMY.md defines starter repo expectations including AGENTS.md, README.md, src/, tests/, docs/, pyproject.toml.
- docs/standards/DATA_PLACEMENT.md defines what belongs in-repo vs /mnt/ace/data.
- docs/reports/2026-04-22-tier-1-indexing-scorecard.md identifies the main gaps: noisy CONTENT_INDEX, missing docs/README.md in some tier-1 repos, stale/missing registries, source-hygiene drift, and lack of operationalized daily freshness.

## What good review should test
Check whether the plan:
1. Stays narrowly scoped to contract/checklist/docs-index/tests, without sneaking in child-issue implementation.
2. Defines the right artifact set and does not omit a correctness-critical surface.
3. Has a TDD/validation strategy strong enough to keep the contract durable.
4. Avoids legacy product-doc reference patterns while still handling migration/replacement boundaries coherently.
5. Correctly handles curated-vs-raw inventory and repo-vs-/mnt/ace/data placement.
6. Makes future approval possible without unresolved contradictions or missing decisions.
7. Has acceptance criteria that are actually testable.
8. Has any hidden coupling to current dirty working tree state, stale docs, or assumptions not proven in the plan.

## Required output format
Use exactly these headings:

Verdict: APPROVE | MINOR | MAJOR

Findings:
- [severity] <concise title> — <why it matters, citing file/section/claim>

Checks performed:
- <what you verified>

Focus on substantive defects. Do not give implementation advice unless tied to a finding.

## Plan under review

# Plan for #2460: Tier-1 indexing and code-placement contract

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2460
> **Review artifacts:** scripts/review/results/2026-04-22-plan-2460-claude.md | scripts/review/results/2026-04-22-plan-2460-codex.md | scripts/review/results/2026-04-22-plan-2460-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/search/build_content_index.py` — current raw content indexing walks repos broadly and only ignores a narrow set of runtime/build directories, which helps explain why `docs/CONTENT_INDEX.md` is too noisy to serve as a curated routing index.
- Found: `tests/docs/test_banned_stale_references.py` — existing docs validation pattern already enforces banned references on curated documentation files; #2460 can follow the same style for a new contract doc.
- Found: `tests/docs/test_staleness_scanner.py` and `tests/quality/test_check_doc_drift.py` — repo already uses doc-staleness and doc-drift tests, so this issue should define the contract in documentation and add focused regression tests rather than inventing a new enforcement framework here.
- Gap: no existing tier-1 indexing contract file exists under `docs/standards/`.
- Gap: no existing targeted plan file for #2460 exists under `docs/plans/`.

### Standards

| Standard | Status | Source |
|---|---|---|
| Control-plane repo discovery contract | existing baseline | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Starter repo taxonomy expectations | existing baseline | `docs/standards/FILE_STRUCTURE_TAXONOMY.md` |
| Data placement decision rule | existing baseline | `docs/standards/DATA_PLACEMENT.md` |

### LLM Wiki pages consulted
- Not applicable — this is a documentation + harness contract issue, not a domain wiki-content issue.

### Documents consulted
- GitHub issue #2460 — defines the narrow scope: canonical routing, operator maps, canonical entry points, machine-readable registries, and daily freshness.
- `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` — confirms portfolio-wide weaknesses: noisy routing surfaces, missing docs entry points, stale/missing registries, and lack of operationalized freshness.
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — establishes `AGENTS.md` as canonical repo entry point and provider adapters as supporting surfaces.
- `docs/standards/FILE_STRUCTURE_TAXONOMY.md` — defines expected starter-repo top-level anatomy (`AGENTS.md`, `README.md`, `src/`, `tests/`, `docs/`, `pyproject.toml`).
- `docs/standards/DATA_PLACEMENT.md` — gives the durable rule for what belongs in repo versus on `/mnt/ace/data/`, which must be incorporated into tier-1 routing guidance.
- `docs/plans/README.md` — confirms no #2460 plan is currently indexed and provides the canonical plan-index format to update.
- Related issues #2397 and #1962 — broader repo-organization and tier-1 refactor umbrellas; #2460 is intentionally narrower and should define the routing/index contract that child issues #2461-#2465 implement.

### Gaps identified
- No canonical tier-1 indexing contract currently tells workers the minimum trusted routing surfaces per repo.
- No per-repo checklist derived from that contract currently exists.
- No current validation test ensures the future contract document includes the required sections, links the remediation issues, and avoids legacy product-doc reference patterns.
- No canonical document currently distinguishes curated routing surfaces from raw inventories in a way reusable across all tier-1 repos.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-22T20:20:11Z via `gh issue view`):
- `#2397` — OPEN — `epic(repo-organization): canonical folder structure and refactor contract across tier-1 repos`
- `#1962` — OPEN — `FEATURE: Tier-1 Repo Ecosystem Refactoring — audit, plan, execute with Claude Code plan mode`
- `#2460` — OPEN — `feat(repo-organization): tier-1 indexing and code-placement contract`
- `#2461` — OPEN — `chore(assetutilities): canonical routing surfaces and source-hygiene cleanup for tier-1 issue work`
- `#2462` — OPEN — `feat(digitalmodel): repo-wide operator map and canonical routing surfaces beyond OrcaWave/OrcaFlex`
- `#2463` — OPEN — `chore(aceengineer-website): canonical routing surfaces and legacy product-doc reference cleanup`
- `#2464` — OPEN — `chore(workspace-hub): split curated tier-1 routing index from raw inventory and clean routing noise`
- `#2465` — OPEN — `feat(automation): daily tier-1 indexing freshness audit and scorecard refresh`

**File existence** (`test -e` / `find` at 2026-04-22T20:20:11Z):
- EXISTS: `docs/reports/2026-04-22-tier-1-indexing-scorecard.md`
- EXISTS: `docs/reports/tier-1-indexing-freshness-latest.md`
- EXISTS: `docs/standards/CONTROL_PLANE_CONTRACT.md`
- EXISTS: `docs/standards/FILE_STRUCTURE_TAXONOMY.md`
- EXISTS: `docs/standards/DATA_PLACEMENT.md`
- MISSING (new — this issue should create): `docs/standards/TIER1_INDEXING_CONTRACT.md`
- MISSING (new — this issue should create): `tests/docs/test_tier1_indexing_contract.py`
- MISSING (current gap): any `docs/plans/*2460*` file before this draft was created

**Line excerpts** (`sed -n`):
```
## Entry Point

**`AGENTS.md`** is the canonical entry point for every repository. It tells both humans and AI agents:
- What the repo does
- How to work in it (workflow, commands, policies)
- Hard gates and constraints

Every repo MUST have an `AGENTS.md` at the root.

---
## Starter Repo Taxonomy Expectations

For each starter repo (digitalmodel, worldenergydata, assethold, assetutilities), the expected top-level structure:

repo-name/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── .claude/
├── .codex/
├── .gemini/
├── .gitignore
├── src/ or repo_name/
├── tests/
├── docs/
├── pyproject.toml
└── .mcp.json
```

```
Weaknesses
- `docs/CONTENT_INDEX.md` is too broad/noisy to serve as a trusted issue-routing index.
- It includes archive, environment, and cross-repo spillover, which weakens path trust.
...
2. Trusted machine-readable routing is missing.
- No consistent repo-level module/operator registry exists across all tier-1 repos.
- digitalmodel still has stale registry references without a restored canonical registry.
...
4. Documentation freshness is not yet operationalized.
- There is no daily curation job dedicated to tier-1 routing/index freshness.
- Several broken or stale references remain live in tier-1 repos.
```

```
# We will walk through the repository but ignore some common large/binary directories
ignore_dirs = {".git", "node_modules", ".venv", "__pycache__", "dist", "build", "htmlcov", ".tox", ".pytest_cache", ".ruff_cache"}

for root, dirs, files in os.walk(repo_path):
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
```

**Gap proofs**:
- `find docs/plans -maxdepth 1 -type f | grep '2460'` → empty output before this draft → confirms no canonical #2460 plan artifact existed.
- `test -e docs/standards/TIER1_INDEXING_CONTRACT.md && echo EXISTS || echo MISSING` → `MISSING` → confirms contract doc does not yet exist.
- `test -e tests/docs/test_tier1_indexing_contract.py && echo EXISTS || echo MISSING` → `MISSING` → confirms targeted regression test does not yet exist.

<!-- Verification: count distinct sources above (across all sub-sections).
     Minimum 3 required (issue body + 2 others). Current count: 8 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` |
| Contract doc | `docs/standards/TIER1_INDEXING_CONTRACT.md` |
| Checklist doc | `docs/standards/TIER1_INDEXING_CHECKLIST.md` |
| Docs index update | `docs/README.md` |
| Tests | `tests/docs/test_tier1_indexing_contract.py` |
| Optional script/docs drift follow-up only (not in this issue) | `scripts/` / child issue `#2465` |
| Plan review — Claude | `scripts/review/results/2026-04-22-plan-2460-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-22-plan-2460-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-22-plan-2460-gemini.md` |

---

## Deliverable

A canonical tier-1 indexing contract and derived checklist under `docs/standards/`, linked from `docs/README.md`, with regression tests that verify required sections, child-issue linkage, daily freshness language, and absence of legacy product-doc reference patterns.

---

## Pseudocode

```text
function define_tier1_indexing_contract():
    read baseline repo discovery and layout standards
    extract minimum required routing surfaces shared across tier-1 repos
    separate required surfaces from optional repo-specific extensions
    encode freshness rule and curated-vs-raw inventory rule
    record child issues for repo-specific implementation follow-through

function define_tier1_checklist(contract):
    for each tier-1 repo in scope:
        list required surfaces and current pass/fail checks
        note repo-specific evidence from the scorecard
        link the corresponding remediation issue

function validate_contract_docs():
    assert contract doc exists
    assert checklist doc exists
    assert docs index links contract
    assert contract includes required sections and child issue references
    assert contract/checklist contain no legacy product-doc reference pattern
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/TIER1_INDEXING_CONTRACT.md` | canonical written contract for trusted routing surfaces, required/optional inventory, freshness rule, and validation rules |
| Create | `docs/standards/TIER1_INDEXING_CHECKLIST.md` | per-repo checklist derived from the contract for workspace-hub, digitalmodel, assetutilities, and aceengineer-website |
| Modify | `docs/README.md` | add the new contract/checklist to a trusted discovery surface |
| Create | `tests/docs/test_tier1_indexing_contract.py` | regression tests for required sections, child issue references, daily freshness language, and absence of legacy product-doc references |
| Update | `docs/plans/README.md` | add this #2460 plan to the index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_tier1_contract_doc_exists` | contract doc is present at canonical standards path | `docs/standards/TIER1_INDEXING_CONTRACT.md` | file exists |
| `test_tier1_contract_contains_required_sections` | contract doc includes required routing surfaces, required-vs-optional section, freshness rule, and curated-vs-raw inventory rule | contract text | required headings present |
| `test_tier1_contract_links_child_issues` | contract doc references #2461-#2465 as implementation follow-through | contract text | all child issue numbers present |
| `test_tier1_contract_avoids_legacy_product_doc_reference_pattern` | contract doc does not reintroduce legacy product-doc reference pattern | contract text | forbidden string absent |
| `test_tier1_checklist_covers_all_scope_repos` | checklist covers the four in-scope repos from the scorecard | checklist text | all four repo names present |
| `test_docs_readme_links_tier1_contract` | docs index exposes the new contract for discovery | `docs/README.md` | link text/path present |

---

## Acceptance Criteria

- [ ] `docs/standards/TIER1_INDEXING_CONTRACT.md` exists and defines the minimum trusted routing/index surfaces for tier-1 repos
- [ ] `docs/standards/TIER1_INDEXING_CHECKLIST.md` exists and covers workspace-hub, digitalmodel, assetutilities, and aceengineer-website
- [ ] contract explicitly separates required surfaces from optional repo-specific extensions
- [ ] contract includes a daily freshness rule and points follow-through work to `#2465`
- [ ] contract links repo-specific implementation follow-through issues `#2461`-`#2464`
- [ ] `docs/README.md` links the new contract/checklist from a trusted discovery surface
- [ ] targeted regression tests pass: `uv run pytest tests/docs/test_tier1_indexing_contract.py -v`
- [ ] existing curated-doc stale-reference guard still passes: `uv run pytest tests/docs/test_banned_stale_references.py -v`
- [ ] review artifacts are posted to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | review not yet run |
| Codex | PENDING | review not yet run |
| Gemini | PENDING | review not yet run |

**Overall result:** PENDING — adversarial review required before posting to GitHub for plan review.

Revisions made based on review:
- none yet

---

## Risks and Open Questions

- **Risk:** The broader `docs/standards/CONTROL_PLANE_CONTRACT.md` still contains historical legacy-path discussion; implementation for #2460 should avoid copying that legacy language into the new contract except where absolutely necessary to define retirement boundaries.
- **Risk:** It is easy to let #2460 grow into automation or repo-specific remediation. Automation belongs to `#2465`; repo-specific changes belong to `#2461`-`#2464`.
- **Risk:** If the contract is too abstract, it will not be implementable; if it is too specific, it will duplicate the child issues. The implementation should define a minimum reusable contract plus repo-specific checklist, not solve every child issue.
- **Open:** Should the contract live only in `docs/standards/` or also be summarized in `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`? The plan keeps the implementation narrow by requiring only a `docs/README.md` link in this issue.
- **Open:** Should “machine-readable registry” be standardized on one exact filename across all tier-1 repos, or only standardized as one canonical registry per repo? This issue should define the rule; child issues can pick the per-repo file path where needed.

---

## Complexity: T2

**T2** — documentation contract plus a derived checklist, one trusted discovery-surface update, and focused regression tests. This is broader than a trivial docs edit but does not require multi-module implementation or deep runtime changes.
