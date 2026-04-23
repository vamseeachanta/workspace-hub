# Adversarial Plan Review Request: Issue #2460 (rerun after blocker patch)

You are an adversarial reviewer. Assume the plan has defects until proven otherwise.
Do not praise. Do not restate the plan. Focus only on what is wrong, missing, risky, contradictory, or insufficiently evidenced.
Return APPROVE only after affirmatively verifying correctness-critical claims. When in doubt, return MINOR or MAJOR.
Each finding must cite a specific file path, plan section, quoted claim, or missing artifact.
If you find no problems, explicitly state what you checked.

## Review target
- Issue: #2460 feat(repo-organization): tier-1 indexing and code-placement contract
- Review stage: PLAN REVIEW (rerun after blocker patch)
- Repository: /mnt/local-analysis/workspace-hub
- Plan path: docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md

## Context
This issue is intentionally narrower than #2397 and #1962. It should define a reusable contract for trusted tier-1 routing/index surfaces, not perform repo-specific implementation or daily-automation implementation directly.
Child issues already filed:
- #2461 assetutilities routing surfaces and source-hygiene cleanup
- #2462 digitalmodel repo-wide routing surfaces
- #2463 aceengineer-website routing surfaces cleanup
- #2464 workspace-hub curated routing index cleanup
- #2465 daily tier-1 indexing freshness audit and scorecard refresh

Previous rerun blockers were:
- daily freshness cadence not independently testable
- local scorecard attestation not explicitly guarded from becoming canonical authority
- legacy retirement rule too abstract
- checklist validation too coarse
- /mnt/ace/data wording maybe too workspace-specific

This rerun should test whether those blockers are now resolved enough for plan-review readiness.

## Required review checks
Check whether the revised plan now:
1. states a daily freshness cadence/obligation, not just a link to #2465
2. explicitly forbids treating the scorecard as required canonical authority
3. makes the legacy-retirement rule concrete enough to implement
4. strengthens checklist validation beyond repo-name presence
5. handles `/mnt/ace/data` scope clearly enough for a tier-1-wide contract
6. remains narrow and approval-ready overall

## Required output format
Use exactly these headings:

Verdict: APPROVE | MINOR | MAJOR

Findings:
- [severity] <concise title> — <why it matters, citing file path/section/claim>

Checks performed:
- <what you verified>

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
- `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` — local attestation baseline used to identify the gap inventory for this draft. The contract itself must not depend on that report being canonical branch state; implementation should encode durable rules from standards + issue scope, while the checklist can cite the scorecard as current local evidence when available.
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

**Evidence-status note**:
- `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` exists in the current local workspace and was used as local attestation for this draft, but the contract deliverable must remain valid even if that scorecard is not yet canonical branch state. The durable contract requirements must come from issue scope plus `CONTROL_PLANE_CONTRACT.md`, `FILE_STRUCTURE_TAXONOMY.md`, and `DATA_PLACEMENT.md`.
- EXISTS: `docs/reports/2026-04-22-tier-1-indexing-scorecard.md`
- EXISTS: `docs/reports/tier-1-indexing-freshness-latest.md`
- EXISTS: `docs/standards/CONTROL_PLANE_CONTRACT.md`
- EXISTS: `docs/standards/FILE_STRUCTURE_TAXONOMY.md`
- EXISTS: `docs/standards/DATA_PLACEMENT.md`
- MISSING (new — this issue should create): `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`
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
- `test -e docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md && echo EXISTS || echo MISSING` → `MISSING` → confirms contract doc does not yet exist.
- `test -e tests/docs/test_tier1_indexing_contract.py && echo EXISTS || echo MISSING` → `MISSING` → confirms targeted regression test does not yet exist.

<!-- Verification: count distinct sources above (across all sub-sections).
     Minimum 3 required (issue body + 2 others). Current count: 8 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` |
| Contract doc | `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` |
| Checklist doc | `docs/standards/TIER1_INDEXING_CHECKLIST.md` |
| Docs index update | `docs/README.md` |
| Tests | `tests/docs/test_tier1_indexing_contract.py` |
| Optional script/docs drift follow-up only (not in this issue) | `scripts/` / child issue `#2465` |
| Plan review — Claude | `scripts/review/results/2026-04-22-plan-2460-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-22-plan-2460-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-22-plan-2460-gemini.md` |

---

## Deliverable

A canonical tier-1 indexing and code-placement contract plus derived checklist under `docs/standards/`, linked from `docs/README.md`, that makes each issue-required routing surface independently testable: `AGENTS.md`, `README.md`, `docs/README.md`, repo operator maps, one canonical machine-readable registry per repo, code/tests/docs routing tables, source-hygiene rules, the repo-vs-`/mnt/ace/data` placement boundary, and explicit retirement guidance for legacy product-doc reference patterns.

---

## Pseudocode

```text
function define_tier1_indexing_and_code_placement_contract():
    read control-plane, taxonomy, and data-placement standards
    define required routing surfaces one by one:
        AGENTS.md, README.md, docs/README.md,
        docs/maps/<repo>-operator-map.md,
        one canonical machine-readable registry per repo,
        code/tests/docs routing table,
        source-hygiene rules,
        repo-vs-/mnt/ace/data placement rule
    define optional repo-specific extensions separately
    define curated-vs-raw inventory boundary
    define explicit legacy product-doc retirement rule:
        allowed = retirement/migration note pointing to canonical surfaces
        banned examples include concrete legacy-reference signatures to enumerate in the contract,
            such as missing-product-doc filenames or path patterns used as active navigation authority
        banned = using legacy product-doc references as active navigation authority
    define freshness rule with daily cadence and explicit follow-through issue #2465
    define negative authority rule:
        the contract/checklist may cite the scorecard as local attestation only
        the contract/checklist must not require scorecard presence as canonical authority
    clarify data-placement scope:
        if `/mnt/ace/data` is workspace-specific, state the general rule as repo-vs-bulk-artifact-store
        and document `/mnt/ace/data` as the current workspace-hub implementation example

function define_tier1_checklist(contract):
    for each tier-1 repo in scope:
        list each required routing surface with pass/fail status
        record evidence source for the current status
        link the corresponding remediation issue
        record whether repo-vs-/mnt/ace/data placement guidance is covered

function validate_contract_docs():
    assert contract doc exists
    assert checklist doc exists
    assert docs index links both
    assert contract doc names every required surface independently
    assert contract doc names the repo-vs-/mnt/ace/data rule explicitly
    assert contract doc states the daily freshness cadence/obligation explicitly
    assert contract doc names #2465 as the daily-freshness follow-through issue
    assert contract doc states the scorecard is optional local attestation, not required canonical authority
    assert legacy retirement rule allows explicit migration language and enumerates at least one concrete banned-pattern example while banning legacy product-doc references as active routing authority
    assert checklist covers all four tier-1 repos and links #2461-#2464
    assert checklist records per-repo operator-map, registry, and data-placement coverage status
    assert docs/plans/README.md contains the #2460 index row
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` | canonical written contract for trusted routing surfaces, code-placement boundary, required-vs-optional inventory, freshness rule, and validation rules |
| Create | `docs/standards/TIER1_INDEXING_CHECKLIST.md` | per-repo checklist derived from the contract for workspace-hub, digitalmodel, assetutilities, and aceengineer-website |
| Modify | `docs/README.md` | add the new contract/checklist to a trusted discovery surface |
| Create | `tests/docs/test_tier1_indexing_contract.py` | regression tests for each required routing surface, data-placement rule, daily-freshness linkage, explicit legacy-retirement rule, and checklist/index coverage |
| Update | `docs/plans/README.md` | add this #2460 plan to the index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_tier1_contract_doc_exists` | contract doc is present at canonical standards path | `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` | file exists |
| `test_tier1_contract_requires_agents_md` | contract explicitly requires `AGENTS.md` as a trusted routing surface | contract text | requirement present |
| `test_tier1_contract_requires_repo_readme` | contract explicitly requires `README.md` as a trusted routing surface | contract text | requirement present |
| `test_tier1_contract_requires_docs_readme` | contract explicitly requires `docs/README.md` | contract text | requirement present |
| `test_tier1_contract_requires_operator_map` | contract explicitly requires `docs/maps/<repo>-operator-map.md` | contract text | requirement present |
| `test_tier1_contract_requires_machine_readable_registry` | contract explicitly requires one canonical machine-readable registry per repo | contract text | requirement present |
| `test_tier1_contract_requires_code_tests_docs_routing_table` | contract explicitly requires code/tests/docs routing-table semantics | contract text | requirement present |
| `test_tier1_contract_requires_source_hygiene_rules` | contract explicitly requires source-hygiene rules for backup/cache/runtime noise | contract text | requirement present |
| `test_tier1_contract_requires_repo_vs_ace_data_rule` | contract explicitly carries forward the repo-vs-`/mnt/ace/data` placement boundary from `docs/standards/DATA_PLACEMENT.md` | contract text | rule present |
| `test_tier1_contract_defines_curated_vs_raw_inventory_boundary` | contract distinguishes curated routing surfaces from raw inventory surfaces | contract text | boundary rule present |
| `test_tier1_contract_defines_legacy_retirement_rule` | contract explicitly defines allowed migration language, bans active legacy product-doc routing authority, and enumerates at least one concrete banned-pattern example | contract text | allowed rule, banned rule, and example present |
| `test_tier1_contract_links_child_issues` | contract doc references #2461-#2465 as implementation follow-through | contract text | all child issue numbers present |
| `test_tier1_contract_marks_2465_as_daily_freshness_followthrough` | contract explicitly names `#2465` as the daily-freshness follow-through issue | contract text | linkage present |
| `test_tier1_contract_requires_daily_freshness_cadence` | contract explicitly states a daily freshness cadence/obligation, not just a child-issue link | contract text | daily cadence language present |
| `test_tier1_contract_forbids_scorecard_as_required_canonical_authority` | contract states the scorecard may be cited as local attestation but must not be required canonical authority | contract text | negative authority rule present |
| `test_tier1_checklist_covers_all_scope_repos` | checklist covers workspace-hub, digitalmodel, assetutilities, and aceengineer-website | checklist text | all four repo names present |
| `test_tier1_checklist_links_repo_specific_child_issues` | checklist links #2461-#2464 to the relevant repos | checklist text | all repo-specific child issue numbers present |
| `test_tier1_checklist_records_surface_status_per_repo` | checklist records per-repo operator-map, registry, and data-placement coverage status | checklist text | required status fields present |
| `test_docs_readme_links_tier1_contract_and_checklist` | docs index exposes both contract and checklist for discovery | `docs/README.md` | link text/path present |
| `test_plans_readme_indexes_2460_plan` | planning index includes the #2460 row | `docs/plans/README.md` | row present |

---

## Acceptance Criteria

- [ ] `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` exists and defines the minimum trusted routing/index surfaces for tier-1 repos
- [ ] contract explicitly and independently requires: `AGENTS.md`, `README.md`, `docs/README.md`, repo operator maps, one canonical machine-readable registry per repo, code/tests/docs routing tables, and source-hygiene rules
- [ ] contract explicitly encodes the repo-vs-`/mnt/ace/data` placement rule from `docs/standards/DATA_PLACEMENT.md`
- [ ] contract explicitly separates curated routing surfaces from raw inventory surfaces
- [ ] contract explicitly defines retirement of legacy product-doc reference patterns by allowing migration/retirement language, banning their use as active routing authority, and enumerating at least one concrete banned-pattern example
- [ ] contract includes a daily freshness rule, explicitly states daily cadence/obligation, and explicitly names `#2465` as the follow-through issue
- [ ] contract explicitly states that `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` may be cited as local attestation but must not be required canonical authority
- [ ] `docs/standards/TIER1_INDEXING_CHECKLIST.md` exists and covers workspace-hub, digitalmodel, assetutilities, and aceengineer-website
- [ ] checklist links repo-specific implementation follow-through issues `#2461`-`#2464`
- [ ] `docs/README.md` links the new contract/checklist from a trusted discovery surface
- [ ] `docs/plans/README.md` includes the #2460 index row
- [ ] targeted regression tests pass: `uv run pytest tests/docs/test_tier1_indexing_contract.py -v`
- [ ] existing curated-doc stale-reference guard still passes: `uv run pytest tests/docs/test_banned_stale_references.py -v`
- [ ] review artifacts are posted to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | Remaining concerns are pattern-level specificity for the legacy-retirement rule, literal `/mnt/ace/data` scope across all tier-1 repos, coarse checklist validation, and text-presence-heavy tests |
| Codex | MAJOR | Daily freshness is still not independently validated as a daily cadence/obligation; local-attestation treatment of the scorecard is explained but not yet enforced by a dedicated negative guard |
| Gemini | APPROVE | Revised plan judged approval-ready; indexing/code-placement scope, routing surfaces, data-placement rule, and local-attestation handling all accepted |

**Overall result:** FAIL — mixed verdicts with a remaining Codex MAJOR mean the plan is still not approval-ready for GitHub `status:plan-review`.

Revisions required based on the latest review wave:
- Add a dedicated test and acceptance criterion that the contract states a daily freshness cadence/obligation, not just that it names `#2465`.
- Add a dedicated negative guard or acceptance criterion that the contract/checklist must not depend on `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` as required canonical authority.
- Tighten the legacy-retirement rule to include at least one concrete banned-pattern list/example rather than only abstract allowed/banned prose.
- Clarify whether `/mnt/ace/data` is literal tier-1-wide policy or an example of a broader bulk-artifact-store boundary.
- Strengthen checklist validation so it verifies per-repo coverage of operator-map, registry, and data-placement status rather than only repo presence and child-issue links.

---

## Risks and Open Questions

- **Risk:** The broader `docs/standards/CONTROL_PLANE_CONTRACT.md` still contains historical legacy-path discussion; implementation for #2460 should avoid copying that legacy language into the new contract except where absolutely necessary to define retirement boundaries.
- **Risk:** It is easy to let #2460 grow into automation or repo-specific remediation. Automation belongs to `#2465`; repo-specific changes belong to `#2461`-`#2464`.
- **Risk:** If the contract is too abstract, it will not be implementable; if it is too specific, it will duplicate the child issues. The implementation should define a minimum reusable contract plus repo-specific checklist, not solve every child issue.
- **Open:** Should the contract state the universal policy as repo-vs-bulk-artifact-store with `/mnt/ace/data` documented as the current workspace-hub implementation example? That wording would preserve the durable rule without overfitting a workspace-specific mount path.
- **Open:** Should the contract live only in `docs/standards/` or also be summarized in `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`? The plan keeps the implementation narrow by requiring only a `docs/README.md` link in this issue.
- **Open:** Should “machine-readable registry” be standardized on one exact filename across all tier-1 repos, or only standardized as one canonical registry per repo? This issue should define the rule; child issues can pick the per-repo file path where needed.
- **Risk:** The scorecard is currently treated as local attestation for plan drafting; the contract/checklist must not promote it into required canonical authority.

---

## Complexity: T2

**T2** — documentation contract plus a derived checklist, one trusted discovery-surface update, and focused regression tests. This is broader than a trivial docs edit but does not require multi-module implementation or deep runtime changes.
