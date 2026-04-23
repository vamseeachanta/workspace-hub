# Adversarial Plan Review Request: Issue #2460 (rerun after stale-reference and threshold patch)
You are an adversarial reviewer. Assume the plan has defects until proven otherwise.
Do not praise. Do not restate the plan. Focus only on what is wrong, missing, risky, contradictory, or insufficiently evidenced.
Return APPROVE only after affirmatively verifying correctness-critical claims. When in doubt, return MINOR or MAJOR.
Each finding must cite a specific file path, plan section, quoted claim, or missing artifact.
If you find no problems, explicitly state what you checked.

Review focus:
1. stale-reference guard coverage for the new docs is now explicitly included
2. DATA_PLACEMENT thresholds are now explicitly carried forward
3. BUSINESS_BRAIN-backed tier-1 scope is justified
4. TDD sequencing is explicit and test-first
5. current draft is approval-ready overall

Required output format:
Verdict: APPROVE | MINOR | MAJOR
Findings:
- [severity] <concise title> — <why it matters, citing file path/section/claim>
Checks performed:
- <what you verified>

Plan under review:
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
- `docs/BUSINESS_BRAIN.md` — canonical current tier-1 repo scope used by this plan: `workspace-hub`, `digitalmodel`, `assetutilities`, and `aceengineer-website`. This is the authority for why the checklist covers those four repos rather than the older starter-repo examples in `FILE_STRUCTURE_TAXONOMY.md`.
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — establishes `AGENTS.md` as canonical repo entry point and provider adapters as supporting surfaces.
- `docs/standards/FILE_STRUCTURE_TAXONOMY.md` — defines expected starter-repo top-level anatomy (`AGENTS.md`, `README.md`, `src/`, `tests/`, `docs/`, `pyproject.toml`).
- `docs/standards/DATA_PLACEMENT.md` — gives the durable rule for what belongs in repo versus on `/mnt/ace/data/`, which must be incorporated into tier-1 routing guidance.
- `docs/plans/README.md` — confirms no #2460 plan is currently indexed and provides the canonical plan-index format to update.
- Related issues #2397 and #1962 — broader repo-organization and tier-1 refactor umbrellas; #2460 is intentionally narrower and should define the routing/index contract that child issues #2461-#2465 implement.
- **#2209 durable-vs-transient knowledge boundary** (`docs/plans/2026-04-16-issue-2209-durable-vs-transient-knowledge-boundary.md`) — documentation-class source required by the retrieval contract union (this issue is labeled `cat:documentation` AND `cat:harness`). The tier-1 indexing contract is a durable normative document per the llm-wiki operating model (#2205 §2 worked examples: "Normative architecture documents … control-plane contracts" are L3). Its retirement/supersedes rules follow #2209 durable-surface conventions (see the §7 promotion/retirement rules for L3 durable docs), not transient-session rules. The checklist lives alongside the contract and inherits the same L3 durable posture.
- **`.claude/rules/` (coding-style.md, patterns.md, README.md)** — harness-class source required by the retrieval contract union. Current `patterns.md` "Enforcement Gradient" (Level 0 prose → Level 1 micro-skill → Level 2 script → Level 3 hook) informs the tier-1 contract's enforcement posture: the new doc/checklist start at Level 0 and the new `tests/docs/test_tier1_indexing_contract.py` promotes the rule to Level 2 (script/regression) without inventing a hook.
- **`config/agents/` (ai-agents-registry.json, behavior-contract.yaml, routing-config.yaml, provider-capabilities.yaml, model-registry.yaml, drift-policy.yaml)** — harness-class source required by the retrieval contract union. Confirmed no agent-routing configuration depends on a per-repo "tier-1 indexing contract" surface; the new contract therefore does not need cross-wiring into `config/agents/` as part of this issue. Evidence: `grep -rni "tier.1.indexing\|TIER1_INDEXING\|tier-1.indexing" config/agents/ .claude/rules/` returned zero matches on 2026-04-22 (before this plan's contract doc exists, as expected).
- **`#2390` llm-wiki strengthening roadmap (live issue body)** — Work Stream G names #2460 explicitly as the portfolio-wide routing contract that gates repo-specific remediation. The umbrella's recommended sequence is: #2460 (this contract) → #2461 (assetutilities) → #2462 (digitalmodel) → #2463 (aceengineer-website) → #2464 (workspace-hub curation) → #2465 (sustaining daily freshness loop). This plan intentionally locks to that sequence rather than re-deriving it.

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
     Minimum 3 required (issue body + 2 others). Current count: 12.
     Retrieval-contract class union: issue is labeled cat:documentation AND cat:harness,
     so per docs/plans/README.md the plan must consult the UNION of both class bundles:
     - Universal minimum: prior plans, existing code in affected paths, recent related issues (covered above)
     - Documentation-class: governance docs in target dir, CONTROL_PLANE_CONTRACT.md, #2209 (covered above)
     - Harness-class: CONTROL_PLANE_CONTRACT.md, config/agents/, .claude/rules/ (covered above)
     Union fully satisfied. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` |
| Contract doc | `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` |
| Checklist doc | `docs/standards/TIER1_INDEXING_CHECKLIST.md` |
| Docs index update | `docs/README.md` |
| Tests | `tests/docs/test_tier1_indexing_contract.py` |
| Plan review — Claude | `scripts/review/results/2026-04-22-plan-2460-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-22-plan-2460-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-22-plan-2460-gemini.md` |

---

## Deliverable

A canonical tier-1 indexing and code-placement contract plus derived checklist under `docs/standards/`, linked from `docs/README.md`, that makes each issue-required routing surface independently testable: `AGENTS.md`, `README.md`, `docs/README.md`, repo operator maps, one canonical machine-readable registry per repo, code/tests/docs routing tables, source-hygiene rules, the repo-vs-bulk-artifact-store placement boundary (where bulk-artifact-store means a non-repo storage target for large, generated, or fast-growing artifacts; `/mnt/ace/data` is the current workspace-hub implementation example), and explicit retirement guidance for legacy product-doc reference patterns.

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
        repo-vs-bulk-artifact-store placement rule
    define optional repo-specific extensions separately
    define curated-vs-raw inventory boundary
    define explicit legacy product-doc retirement rule:
        allowed = retirement/migration note pointing to canonical surfaces
        banned examples = enumerate AT LEAST 3 DISTINCT CATEGORIES of concrete signatures,
            including at minimum:
                (a) literal legacy filenames (e.g., specific product-doc filenames no longer authoritative)
                (b) legacy path fragments (e.g., retired product-doc directory prefixes)
                (c) legacy reference blocks used as active navigation authority (e.g., sections that
                    route readers back to retired product-doc conventions instead of canonical surfaces)
        banned = using legacy product-doc references as active navigation authority
    define freshness rule with exact required wording and obligation:
        contract must state "daily freshness review"
        contract must state either "every 24 hours" or "once per day"
        contract must require refreshing or regenerating `docs/reports/tier-1-indexing-freshness-latest.md`
        contract must name #2465 in the same freshness section as the follow-through issue
    define negative authority rule with exact required wording:
        contract/checklist may cite tier-1 indexing scorecards as local attestation only
        contract/checklist must include "MUST NOT treat any tier-1 indexing scorecard under docs/reports/ as required canonical authority"
    define data-placement scope explicitly:
        universal rule = repo-vs-bulk-artifact-store
        bulk-artifact-store = non-repo storage target for large, generated, or fast-growing artifacts
        workspace-hub example = `/mnt/ace/data` as the current implementation example

function define_tier1_checklist(contract):
    for each tier-1 repo in scope from docs/BUSINESS_BRAIN.md:
        record repo_name
        record operator_map_status using one of: present | partial | missing | not-applicable
        record registry_status using one of: present | partial | missing | not-applicable
        record data_placement_status using one of: present | partial | missing | not-applicable
        record evidence_source as a concrete path, issue number, or report path
        repeat the negative-authority rule for scorecards in the checklist preamble
        link the corresponding remediation issue

function implement_with_tdd():
    write `tests/docs/test_tier1_indexing_contract.py` first
    extend `tests/docs/test_banned_stale_references.py` so the new contract/checklist docs are covered by the curated-doc stale-reference guard
    run the targeted test file and curated stale-reference test and confirm failure before editing docs
    then edit `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`
    then edit `docs/standards/TIER1_INDEXING_CHECKLIST.md`
    then edit `docs/README.md`
    then update `docs/plans/README.md`
    rerun targeted tests until green

function validate_contract_docs():
    assert contract doc exists
    assert checklist doc exists
    assert docs index links both
    assert contract doc names every required surface independently
    assert contract doc names the repo-vs-bulk-artifact-store rule explicitly
    assert contract doc defines bulk-artifact-store in concrete terms
    assert contract doc cites `/mnt/ace/data` only as the current workspace-hub example
    assert contract doc contains the exact daily freshness wording requirement
    assert contract doc requires refreshing or regenerating `docs/reports/tier-1-indexing-freshness-latest.md`
    assert contract doc names #2465 as the daily-freshness follow-through issue in that same section
    assert contract doc contains the exact negative-authority sentence for tier-1 indexing scorecards
    assert legacy retirement rule allows explicit migration language and enumerates AT LEAST 3 DISTINCT
        CATEGORIES of concrete banned-pattern signatures (literal legacy filenames, legacy path fragments,
        legacy reference blocks used as active navigation authority) while banning legacy product-doc
        references as active routing authority
    assert checklist covers the four current tier-1 repos from docs/BUSINESS_BRAIN.md and links #2461-#2464
    assert checklist's repo set is computed against a live parse of docs/BUSINESS_BRAIN.md tier-1 section,
        not just a hardcoded literal list (drift-detection)
    assert each child issue number appears alongside its scope clause in the contract/checklist:
        #2461 near "assetutilities", #2462 near "digitalmodel", #2463 near "aceengineer-website",
        #2464 near "workspace-hub", #2465 in the daily-freshness section
    assert #2390 llm-wiki strengthening roadmap dependency is named explicitly
    assert checklist repeats the exact negative-authority sentence for tier-1 indexing scorecards in its preamble
    assert checklist records repo_name, operator_map_status, registry_status, data_placement_status, and evidence_source for each repo using the allowed status values
    assert TDD sequencing requires tests to fail before contract/checklist doc edits begin
    assert docs/plans/README.md contains the #2460 index row
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` | canonical written contract for trusted routing surfaces, code-placement boundary, required-vs-optional inventory, freshness rule, and validation rules |
| Create | `docs/standards/TIER1_INDEXING_CHECKLIST.md` | per-repo checklist derived from the contract for workspace-hub, digitalmodel, assetutilities, and aceengineer-website |
| Modify | `docs/README.md` | add the new contract/checklist to a trusted discovery surface |
| Create | `tests/docs/test_tier1_indexing_contract.py` | regression tests for each required routing surface, data-placement rule, daily-freshness linkage, explicit legacy-retirement rule, checklist/index coverage, and scope guards |
| Modify | `tests/docs/test_banned_stale_references.py` | bring the new contract/checklist docs under the curated-doc stale-reference guard |
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
| `test_tier1_contract_requires_repo_vs_bulk_artifact_store_rule` | contract explicitly defines the universal repo-vs-bulk-artifact-store placement rule, defines bulk-artifact-store concretely using the `>= 10 MB` or `>= 1000 files` decision thresholds from `docs/standards/DATA_PLACEMENT.md`, and treats `/mnt/ace/data` only as the current workspace-hub example | contract text | universal rule, threshold definition, and example language present |
| `test_tier1_contract_defines_curated_vs_raw_inventory_boundary` | contract distinguishes curated routing surfaces from raw inventory surfaces | contract text | boundary rule present |
| `test_tier1_contract_defines_legacy_retirement_rule` | contract explicitly defines allowed migration language, bans active legacy product-doc routing authority, and enumerates at least 3 distinct categories of concrete banned-pattern signatures — literal legacy filenames, legacy path fragments, and legacy reference blocks used as active navigation authority | contract text | allowed rule, banned rule, and ≥3 distinct categories present |
| `test_tier1_contract_links_child_issues` | each child issue number appears in the contract alongside its scope clause (not merely as a standalone number): `#2461` within the same section as "assetutilities"; `#2462` within the same section as "digitalmodel"; `#2463` within the same section as "aceengineer-website"; `#2464` within the same section as "workspace-hub"; `#2465` within the daily-freshness section | contract text | each child issue co-located with its scope clause |
| `test_tier1_contract_names_llm_wiki_roadmap_dependency` | contract doc explicitly names `#2390` llm-wiki strengthening roadmap Work Stream G as the upstream umbrella that depends on this contract | contract text | `#2390` dependency statement present |
| `test_tier1_contract_marks_2465_as_daily_freshness_followthrough` | contract explicitly names `#2465` as the daily-freshness follow-through issue | contract text | linkage present |
| `test_tier1_contract_requires_daily_freshness_cadence` | contract includes the exact wording `daily freshness review`, includes either `every 24 hours` or `once per day`, and requires refreshing or regenerating `docs/reports/tier-1-indexing-freshness-latest.md` in the same freshness section | contract text | exact cadence wording and refresh obligation present |
| `test_tier1_contract_forbids_scorecard_as_required_canonical_authority` | contract contains the sentence `MUST NOT treat any tier-1 indexing scorecard under docs/reports/ as required canonical authority` | contract text | exact negative-authority sentence present |
| `test_tier1_checklist_covers_all_scope_repos` | checklist covers the four current tier-1 repos defined in `docs/BUSINESS_BRAIN.md`: workspace-hub, digitalmodel, assetutilities, and aceengineer-website | checklist text | exact repo set present |
| `test_tier1_checklist_repo_set_matches_business_brain_tier1_section` | at test runtime, parse `docs/BUSINESS_BRAIN.md` by extracting text between the `### Tier-1` header and the next `### Tier-` header, taking the **leading pipe-delimited cell** of each row (ignoring the header/separator rows), and assert the checklist's repo set exactly equals the parsed set (drift-detection: if BUSINESS_BRAIN ever adds, removes, or renames a tier-1 repo, this test fails so the checklist gets updated in the same PR). Must NOT do a loose whole-document grep — that would silently pass if a repo was moved to Tier-2 but still mentioned elsewhere in the file. | live parse of BUSINESS_BRAIN + checklist text | parsed tier-1 set equals checklist repo set |
| `test_tier1_checklist_links_repo_specific_child_issues` | checklist links #2461-#2464 to the relevant repos, each child issue co-located with its repo row or scope clause (not merely present somewhere in the document) | checklist text | each repo-specific child issue co-located with its repo |
| `test_tier1_checklist_repeats_scorecard_negative_authority_rule` | checklist preamble repeats the sentence `MUST NOT treat any tier-1 indexing scorecard under docs/reports/ as required canonical authority` | checklist text | exact negative-authority sentence present |
| `test_tier1_checklist_records_surface_status_per_repo` | checklist records `repo_name`, `operator_map_status`, `registry_status`, `data_placement_status`, and `evidence_source` for each repo, with status values drawn from the allowed set `present`, `partial`, `missing`, `not-applicable` (enumerated as separate inline-code tokens rather than a pipe-delimited code span, to avoid GFM table rendering ambiguity) | checklist text | exact field names and allowed status values present |
| `test_tdd_sequence_requires_tests_fail_before_doc_edits` | implementation notes require writing `tests/docs/test_tier1_indexing_contract.py` first, extending `tests/docs/test_banned_stale_references.py`, and confirming both targeted tests fail before editing any contract/checklist/discovery docs | plan text | explicit test-first sequence present |
| `test_new_contract_docs_are_under_curated_stale_reference_guard` | `tests/docs/test_banned_stale_references.py` must include the new contract/checklist docs in its strict-file coverage set | test text | contract/checklist paths present in strict guard |
| `test_docs_readme_links_tier1_contract_and_checklist` | docs index exposes both contract and checklist for discovery | `docs/README.md` | link text/path present |
| `test_plans_readme_indexes_2460_plan` | planning index includes the #2460 row | `docs/plans/README.md` | row present |

---

## Acceptance Criteria

- [ ] `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` exists and defines the minimum trusted routing/index surfaces for tier-1 repos
- [ ] contract explicitly and independently requires: `AGENTS.md`, `README.md`, `docs/README.md`, repo operator maps, one canonical machine-readable registry per repo, code/tests/docs routing tables, and source-hygiene rules
- [ ] contract explicitly encodes the universal repo-vs-bulk-artifact-store placement rule, defines bulk-artifact-store concretely using the `>= 10 MB` or `>= 1000 files` thresholds from `docs/standards/DATA_PLACEMENT.md`, and documents `/mnt/ace/data` only as the current workspace-hub implementation example
- [ ] contract explicitly separates curated routing surfaces from raw inventory surfaces
- [ ] contract explicitly defines retirement of legacy product-doc reference patterns by allowing migration/retirement language, banning their use as active routing authority, and enumerating at least 3 distinct categories of concrete banned-pattern signatures (literal legacy filenames, legacy path fragments, and legacy reference blocks used as active navigation authority)
- [ ] contract includes a daily freshness rule, contains the exact phrase `daily freshness review`, includes either `every 24 hours` or `once per day`, requires refreshing or regenerating `docs/reports/tier-1-indexing-freshness-latest.md`, and explicitly names `#2465` as the follow-through issue
- [ ] contract includes the sentence `MUST NOT treat any tier-1 indexing scorecard under docs/reports/ as required canonical authority`
- [ ] `docs/standards/TIER1_INDEXING_CHECKLIST.md` exists and covers the four current tier-1 repos defined in `docs/BUSINESS_BRAIN.md`: workspace-hub, digitalmodel, assetutilities, and aceengineer-website
- [ ] a test parses `docs/BUSINESS_BRAIN.md` at runtime and asserts the checklist's repo set equals the parsed tier-1 set (drift-detection — if BUSINESS_BRAIN changes, the checklist must change in the same PR)
- [ ] checklist links repo-specific implementation follow-through issues `#2461`-`#2464`, with each issue number co-located with its corresponding repo row (not merely present somewhere in the document)
- [ ] contract explicitly names `#2390` llm-wiki strengthening roadmap Work Stream G as the upstream umbrella that depends on this contract landing first
- [ ] checklist repeats the sentence `MUST NOT treat any tier-1 indexing scorecard under docs/reports/ as required canonical authority` in its preamble
- [ ] checklist records `repo_name`, `operator_map_status`, `registry_status`, `data_placement_status`, and `evidence_source` for each repo, with status values constrained to the set of four tokens `present`, `partial`, `missing`, `not-applicable` — each token MUST appear inside its own backtick span (four separate inline-code spans per status enumeration; no commas, slashes, or pipes inside any single span); the `test_tier1_checklist_records_surface_status_per_repo` test must assert the count of independent backtick spans, not just textual presence
- [ ] implementation notes require writing `tests/docs/test_tier1_indexing_contract.py` first, extending `tests/docs/test_banned_stale_references.py`, and confirming both targeted tests fail before editing any contract/checklist/discovery docs
- [ ] `tests/docs/test_banned_stale_references.py` is updated so the new contract/checklist docs are under the curated-doc stale-reference guard
- [ ] `docs/README.md` links the new contract/checklist from a trusted discovery surface
- [ ] `docs/plans/README.md` includes the #2460 index row
- [ ] targeted regression tests pass: `uv run pytest tests/docs/test_tier1_indexing_contract.py -v`
- [ ] existing curated-doc stale-reference guard still passes: `uv run pytest tests/docs/test_banned_stale_references.py -v`
- [ ] review artifacts are posted to `scripts/review/results/`

---

## Adversarial Review Summary

Three review waves have run (r3, r6, r7). The binding state is the r7 wave — a single-author Claude review under the documented permission-gate fallback (`feedback_permission_gate_blocks_cross_review.md` in memory). Cross-provider independence is inherited transitively from r6: Gemini APPROVE stands because every r7 patch was strictly additive/tightening, and Codex's r6 MAJORs are each addressed with line-level traceability. A future dispatch-capable session must redispatch Codex before `status:plan-approved`.

### r3 wave (historical — superseded)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | Prior draft still self-declared FAIL, kept `/mnt/ace/data` scope unresolved, and carried stale revisions-required language |
| Codex | MAJOR | Prior draft still treated daily freshness and the scorecard negative-authority guard as too weakly specified |
| Gemini | MINOR | Prior draft still had a contradiction between generalized bulk-artifact-store intent and literal `/mnt/ace/data` wording |

### r6 wave (real cross-provider CLI dispatch — raw outputs at `.planning/quick/review-2460-r6-*.out`)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | (1) Pipe-rendering hazard in TDD/acceptance status-values cells; (2) BUSINESS_BRAIN scope coupling was narrative-only (hardcoded list, not parsed); (3) "multiple concrete banned-pattern signatures" unquantified; (4) Artifact Map bled scope with an "optional follow-up" row; (5) `test_tier1_contract_links_child_issues` under-specified placement (just presence, not co-location with scope clause) |
| Codex | MAJOR | (1) Retrieval-contract union not satisfied — issue is `cat:documentation` AND `cat:harness`, so the plan must consult BOTH class bundles; missing #2209 durable-vs-transient boundary and harness-class sources (`config/agents/`, `.claude/rules/`). (2) Plan cites `tests/docs/test_banned_stale_references.py` as the pattern but did not add the new docs to `STRICT_FILES`. (3) [MINOR] Bulk-artifact-store wording did not reference the `≥ 10 MB` / `≥ 1000 files` thresholds from `docs/standards/DATA_PLACEMENT.md`. |
| Gemini | APPROVE | No findings. Verified: BUSINESS_BRAIN authority, scorecard negative-authority guard, TDD sequencing, placement-rule consistency, wording constraints. |

### Post-r6 patches applied (addressed each r6 finding)

- **Codex MAJOR #1 (retrieval contract):** added `#2209`, `config/agents/`, and `.claude/rules/` to Documents consulted; added explicit `cat:documentation + cat:harness` class-union annotation; raised the source count to 12.
- **Codex MAJOR #2 (STRICT_FILES coverage):** Files-to-Change added `Modify | tests/docs/test_banned_stale_references.py`; TDD list added `test_new_contract_docs_are_under_curated_stale_reference_guard`; acceptance criterion added at line 312.
- **Codex MINOR (thresholds):** `≥ 10 MB` or `≥ 1000 files` threshold added to TDD row (line 276) and acceptance criterion (line 300).
- **Claude r6 MINOR #1 (pipe rendering):** replaced pipe-delimited inline code in TDD/acceptance status-values cells with comma-separated tokens.
- **Claude r6 MINOR #2 (BUSINESS_BRAIN drift):** added `test_tier1_checklist_repo_set_matches_business_brain_tier1_section` that parses the tier-1 section at test time.
- **Claude r6 MINOR #3 (quantify "multiple"):** legacy-retirement rule now requires AT LEAST 3 DISTINCT CATEGORIES with named minimums.
- **Claude r6 MINOR #4 (Artifact Map scope bleed):** removed the "Optional script/docs drift follow-up" row; this is captured in Risks → Not in scope.
- **Claude r6 MINOR #5 (child-issue placement):** `test_tier1_contract_links_child_issues` and the checklist acceptance criterion now require each child issue number to appear co-located with its scope clause.
- **llm-wiki dependency (new):** added `test_tier1_contract_names_llm_wiki_roadmap_dependency` and an acceptance-criterion requiring `#2390` Work Stream G to be named as the upstream umbrella that depends on this contract.

### r7 wave (single-author Claude, post-r6 re-verification — permission-gate fallback)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (in-session) | MINOR | (1) negative claim on line 42 lacks inline proof; (2) BUSINESS_BRAIN drift-detection test under-specifies the parse (row-leading vs inline); (3) pipe-rendering acceptance criterion describes intent without a sentinel; (4) `#2209` cite needs a section pin, not just a path; (5) plan still self-labels `PENDING RE-REVIEW`. |
| Codex | NOT REDISPATCHED | Permission gate blocks subprocess CLI dispatch. r6 MAJORs traceably addressed; fresh Codex run required before `status:plan-approved`. |
| Gemini | APPROVE (inherited from r6) | All post-r6 patches are strictly tightening; none invalidates any check Gemini performed at r6. |

### r7 patch list (addressing r7 MINOR findings)

- **r7 MINOR #1 (negative-claim proof):** added inline `grep -rni` evidence alongside the `config/agents/` statement on line 42.
- **r7 MINOR #2 (BUSINESS_BRAIN parser brittleness):** tightened `test_tier1_checklist_repo_set_matches_business_brain_tier1_section` to require extracting from the `### Tier-1` section header up to the next `### Tier-` header and matching on leading `|` table-row cells only.
- **r7 MINOR #3 (pipe-rendering sentinel):** tightened acceptance criterion to require each of the four tokens in its own backtick span (four separate spans, no commas inside any single span).
- **r7 MINOR #4 (`#2209` section pin):** added a section-level citation for #2209.
- **r7 MINOR #5 (self-label):** replaced `PENDING RE-REVIEW` self-label with the r7 verdict record below.

**Current draft state:** PLAN-REVIEW READY — r7 MINOR findings are patched; one future cross-review session should redispatch Codex to confirm MAJOR-addressed → APPROVE before `status:plan-approved`. No MAJOR defect is outstanding. Progression to `status:plan-review` is supported by r7; user approval to `status:plan-approved` should wait for fresh Codex sign-off.

---

## Risks and Open Questions

### Not in scope (delegated to child issues)

- Any `scripts/` work that enforces the contract at CI time beyond the regression tests in this issue — delegated to `#2465` (daily tier-1 indexing freshness audit).
- Per-repo remediation edits (operator maps, registry files, source-hygiene cleanup inside each tier-1 repo) — delegated to `#2461` (assetutilities), `#2462` (digitalmodel), `#2463` (aceengineer-website), `#2464` (workspace-hub curation).
- Automation that regenerates `docs/reports/tier-1-indexing-freshness-latest.md` on a schedule — delegated to `#2465`.

### Dependencies

- **Upstream:** `#2390` epic(knowledge): llm-wiki strengthening roadmap — Work Stream G names this issue (#2460) as the portfolio-wide routing contract that gates Wave-G execution. Until this contract is approved and implemented, repo-specific remediations (#2461-#2464) should not execute, and the sustaining freshness audit (#2465) has no contract surface to audit against.
- **Downstream gate for:** #2461, #2462, #2463, #2464, #2465. Recommended sequence per #2390 Work Stream G: #2460 → #2461 → #2462 → #2463 → #2464 → #2465 (sustaining).

### Risks

- **Risk:** The broader `docs/standards/CONTROL_PLANE_CONTRACT.md` still contains historical legacy-path discussion; implementation for #2460 should avoid copying that legacy language into the new contract except where absolutely necessary to define retirement boundaries.
- **Risk:** It is easy to let #2460 grow into automation or repo-specific remediation. Automation belongs to `#2465`; repo-specific changes belong to `#2461`-`#2464`.
- **Risk:** If the contract is too abstract, it will not be implementable; if it is too specific, it will duplicate the child issues. The implementation should define a minimum reusable contract plus repo-specific checklist, not solve every child issue.
- **Resolved design choice:** The universal placement rule is repo-vs-bulk-artifact-store; `/mnt/ace/data` is documented only as the current workspace-hub implementation example.
- **Open:** Should the contract live only in `docs/standards/` or also be summarized in `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`? The plan keeps the implementation narrow by requiring only a `docs/README.md` link in this issue.
- **Open:** Should "machine-readable registry" be standardized on one exact filename across all tier-1 repos, or only standardized as one canonical registry per repo? This issue should define the rule; child issues can pick the per-repo file path where needed.
- **Risk:** The scorecard is currently treated as local attestation for plan drafting; the contract/checklist must not promote any tier-1 indexing scorecard into required canonical authority.

---

## Complexity: T2

**T2** — documentation contract plus a derived checklist, one trusted discovery-surface update, and focused regression tests. This is broader than a trivial docs edit but does not require multi-module implementation or deep runtime changes.
