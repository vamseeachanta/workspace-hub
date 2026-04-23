# Plan for #2464: Split curated tier-1 routing index from raw inventory and clean routing noise

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2464
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2464-claude.md (terminal-1 self-review; Codex/Gemini reruns to dispatch after #2460 approval)

---

## Resource Intelligence Summary

<!-- This issue is labeled cat:documentation + cat:harness + domain:repo-organization.
     Per docs/plans/README.md, multi-class issues require the UNION of class bundles:
     - Universal minimum: prior plans, existing code in affected paths, recent related issues
     - Documentation-class: governance docs in target dir, CONTROL_PLANE_CONTRACT.md, durable-vs-transient boundary (#2209)
     - Harness-class: CONTROL_PLANE_CONTRACT.md, config/agents/ settings, .claude/rules/
     All three bundles consulted below. -->

### Existing repo code

- Found: `docs/CONTENT_INDEX.md` — **30,084 lines** (verified via `wc -l`). This is the artifact the scorecard and issue body call out as "too broad/noisy to serve as a trusted issue-routing index." Scale confirms it is functioning as a raw repo-content inventory, not a curated routing surface.
- Found: `scripts/search/build_content_index.py` — this is the generator that walks the repo broadly with only a narrow `ignore_dirs` set (`.git`, `node_modules`, `.venv`, `__pycache__`, `dist`, `build`, `htmlcov`, `.tox`, `.pytest_cache`, `.ruff_cache`). Explains why the output is large; this plan does not modify the generator (its raw-inventory role is legitimate), but marks its output as raw-inventory-class in `CONTENT_INDEX.md` preamble.
- Found: `docs/README.md` (300 lines) — current canonical docs entry point; does not yet link a curated tier-1 routing surface or map issue-type → repo → path.
- Found: `docs/SKILLS_INDEX.md` (385 lines) — a model of a curated, trusted discovery surface; routing-index design should mirror its density and scope discipline, not `CONTENT_INDEX.md`'s.
- Found: `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` — the one existing high-value operator map per the scorecard; its shape and density are a useful reference.
- Found: `data/document-index/intelligence-accessibility-registry.yaml` — referenced in the scorecard as explicitly recording discoverability gaps; the curated routing index should cross-link here.
- Found: `tests/docs/test_banned_stale_references.py` with hardcoded `STRICT_FILES` list (see `tests/docs/test_banned_stale_references.py:7`) — existing pattern for curated-doc regression tests. The new routing index must be added to `STRICT_FILES`, same pattern as #2460.
- Gap: no `docs/TIER1_ROUTING_INDEX.md` or equivalent curated tier-1 routing surface currently exists in `docs/`.
- Gap: no preamble on `docs/CONTENT_INDEX.md` declares its raw-inventory role and explicitly demotes it from "curated routing surface" status.
- Gap: 10 literal non-file-named noise artifacts tracked at repo root (enumerated in Evidence below).

### Standards

| Standard | Status | Source |
|---|---|---|
| Tier-1 indexing and code-placement contract (prerequisite — the contract this plan implements against) | pending landing of #2460 | `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` (to be created by #2460) |
| Control-plane repo discovery contract | existing baseline | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Starter repo taxonomy expectations | existing baseline | `docs/standards/FILE_STRUCTURE_TAXONOMY.md` |
| Data placement decision rule (≥10 MB / ≥1000 files → bulk-artifact-store) | existing baseline | `docs/standards/DATA_PLACEMENT.md` |

### LLM Wiki pages consulted

- Not applicable as direct wiki content — this is a documentation + harness control-plane issue. However, per the llm-wiki operating model (`docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` §2 worked examples), normative architecture documents including control-plane contracts are classified as **L3 durable knowledge**. The curated tier-1 routing index created by this issue is L3-class under that classification. §8.1 frontmatter-schema authority applies only to pages under `knowledge/wikis/**`, so `docs/TIER1_ROUTING_INDEX.md` is NOT subject to `doc_key` frontmatter.

### Documents consulted

- GitHub issue #2464 body (verified 2026-04-22 via `gh issue view 2464`) — defines exact scope: curated vs raw inventory separation, CONTENT_INDEX.md split/replace, top-level noise cleanup, docs/README.md discoverability, tier-1 issue-type routing matrix.
- **#2460 canonical plan** (`docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md`) — the prerequisite contract. This plan (#2464) is the workspace-hub-specific implementation of the contract for one tier-1 repo. All "what a curated routing surface requires" comes from the #2460 contract; this plan does NOT redefine those rules.
- **#2390 epic(knowledge): llm-wiki strengthening roadmap** (live issue body verified 2026-04-22) — Work Stream G names #2464 as the workspace-hub remediation in the sequence #2460 → #2461 → #2462 → #2463 → **#2464** → #2465. This plan intentionally slots into that position and does not pre-empt the predecessors.
- **`docs/reports/2026-04-22-tier-1-indexing-scorecard.md`** — the scorecard that generated this issue set. Specifically cites: (a) `docs/CONTENT_INDEX.md` is too noisy for routing; (b) 10 literal noise filenames at root; (c) intelligence-accessibility-registry.yaml records discoverability gaps. These findings drive the Files-to-Change list below.
- **#2209 durable-vs-transient knowledge boundary policy** (documentation-class retrieval contract source, `docs/plans/2026-04-16-issue-2209-durable-vs-transient-knowledge-boundary.md`) — the curated routing index is durable L3 content; session/handoff artifacts that accumulated at repo root are transient L6 that should never have been tracked. This plan's cleanup is justified by the L3/L6 boundary rule.
- **`.claude/rules/coding-style.md`** (harness-class retrieval contract source) — "Path Handling" rule requires relative paths in scripts; the new regression test for this plan must not hardcode absolute paths. "Agent Harness Files" rule caps CLAUDE.md/AGENTS.md/MEMORY.md at 20 lines — confirms minimalism posture; the curated routing index follows that posture by linking out rather than duplicating content.
- **`.claude/rules/patterns.md`** (harness-class retrieval contract source) — "Enforcement Gradient" (Level 0 prose → Level 1 micro-skill → Level 2 script → Level 3 hook). The new routing index starts at Level 0; the regression test promotes it to Level 2. This plan does NOT add a Level 3 hook.
- **`config/agents/` (ai-agents-registry.json, routing-config.yaml, behavior-contract.yaml)** (harness-class retrieval contract source) — verified 2026-04-22: no agent-routing or provider config references the workspace-hub curated routing index. Creating it therefore does NOT require cross-wiring into agent config; this is a documentation-only change from the harness perspective.
- **Related issues:** #2397 (canonical folder structure + refactor contract) and #1962 (tier-1 refactor umbrella) — both are broader parents; #2464 is intentionally narrow and lives under their umbrellas without absorbing their scope.

### Gaps identified

- No curated, low-density, tier-1-focused routing surface exists to answer "for issue type X in repo Y, what is the canonical path?"
- `docs/CONTENT_INDEX.md` is the only large auto-generated index but is mistakenly treated by workers as authoritative routing (per scorecard).
- 10 literal non-file-named tracked artifacts at repo root (proof below) — these weaken root trust and should not be tracked.
- `docs/README.md` does not link the intelligence accessibility registry, the curated routing index (which does not exist yet), or the tier-1 routing matrix.
- No regression test asserts the curated/raw split is maintained or that the noise files stay deleted.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-22 via `gh issue view`):

- `#2390` — OPEN — `epic(knowledge): llm-wiki strengthening roadmap and execution waves` — Work Stream G explicitly names `#2464` as workspace-hub remediation in the recommended sequence.
- `#2460` — OPEN — `feat(repo-organization): tier-1 indexing and code-placement contract` — prerequisite contract; local plan exists at `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` with r3 + r6 review history and post-r6 tightening applied, status `draft`.
- `#2461` — OPEN — `chore(assetutilities): canonical routing surfaces and source-hygiene cleanup for tier-1 issue work`.
- `#2462` — OPEN — `feat(digitalmodel): repo-wide operator map and canonical routing surfaces beyond OrcaWave/OrcaFlex`.
- `#2463` — OPEN — `chore(aceengineer-website): canonical routing surfaces and legacy product-doc reference cleanup`.
- `#2464` — OPEN — `chore(workspace-hub): split curated tier-1 routing index from raw inventory and clean routing noise` (this issue).
- `#2465` — OPEN — `feat(automation): daily tier-1 indexing freshness audit and scorecard refresh`.

**File existence** (verified 2026-04-22 via `ls` / `wc -l`):

- EXISTS: `docs/CONTENT_INDEX.md` — **30,084 lines** (too large for curated routing by inspection)
- EXISTS: `docs/README.md` — 300 lines
- EXISTS: `docs/SKILLS_INDEX.md` — 385 lines (model of a curated surface)
- EXISTS: `scripts/search/build_content_index.py` — raw-inventory generator
- EXISTS: `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` — existing operator-map template
- EXISTS: `data/document-index/intelligence-accessibility-registry.yaml`
- EXISTS: `tests/docs/test_banned_stale_references.py` (STRICT_FILES at line 7)
- MISSING (this issue creates): `docs/TIER1_ROUTING_INDEX.md` (proposed canonical name; final name subject to #2460 contract's required-surface naming rule)
- MISSING (this issue creates): `tests/docs/test_workspace_hub_curated_routing_index.py`
- MISSING (prerequisite, created by #2460): `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`

**Top-level noise files** (verified 2026-04-22 via `git ls-files -- ':!:*/*'`) — 10 literal non-file-named tracked artifacts that should be removed:

```
**Complexity:**
**Date:**
**Issue:**
**Review
**Source
**Status:**
-
Compatibility
Comprehensive
This
```

These are fragments of markdown formatting captured as filenames and committed, almost certainly by automation or redirect mishaps. None is a legitimate tracked artifact.

**Additional top-level artifacts of concern** (tracked at root, stronger cleanup but not in this issue's minimum scope):

- `nohup.out`, `transcript_raw.json`, `claude_smoke_prompt.txt` — runtime byproducts
- `ace_cfp_sending_kit_2026-04-09.md`, `gmail_*_2026-04-09.*` (8 files), `skestates_gmail_triage_2026-04-09.md`, `personal_gmail_triage_2026-04-09.txt`, `daily_gmail_action_digest_2026-04-09.md` — dated operational artifacts
- `draft_skestates_*_email.md` (3 files), `final_skestates_*_email.md` (3 files), `sendready_skestates_*_email.md` (3 files) — draft email workflow byproducts
- `issue-1839-*.{md,diff}` (4 files), `issue-1858-*.{md,diff}` (2 files), `terminal-2-*.{md,diff}` (2 files) — per-issue scratch artifacts

This plan removes ONLY the 10 literal non-file-named noise files. The broader dated-artifact cleanup is flagged but left to a follow-up issue to avoid scope drift — see Risks → Not in scope.

**Gap proofs**:

- `test -e docs/TIER1_ROUTING_INDEX.md && echo EXISTS || echo MISSING` → `MISSING` → confirms curated routing index does not yet exist.
- `test -e tests/docs/test_workspace_hub_curated_routing_index.py && echo EXISTS || echo MISSING` → `MISSING` → confirms regression test does not yet exist.
- `grep -q 'raw.inventory' docs/CONTENT_INDEX.md || echo NO_PREAMBLE` → `NO_PREAMBLE` → confirms CONTENT_INDEX.md has no preamble declaring its raw-inventory role.
- `grep -q 'TIER1_ROUTING_INDEX' docs/README.md || echo NOT_LINKED` → `NOT_LINKED` → confirms docs/README.md does not link the (yet-to-exist) curated index.

<!-- Verification: count distinct sources above (across all sub-sections).
     Minimum 3 required (issue body + 2 others). Current count: 13.
     Retrieval-contract class union (cat:documentation + cat:harness): fully satisfied —
     - Universal minimum: ✓ (prior plans #2460 + #2390 Work Stream G; existing code docs/CONTENT_INDEX.md, scripts/search/build_content_index.py; recent issues #2397 #1962 #2460-#2465)
     - Documentation-class: ✓ (CONTROL_PLANE_CONTRACT.md, FILE_STRUCTURE_TAXONOMY.md, DATA_PLACEMENT.md, #2209)
     - Harness-class: ✓ (.claude/rules/coding-style.md, .claude/rules/patterns.md, config/agents/*) -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2464-workspace-hub-curated-routing-index.md` |
| Curated routing index (new) | `docs/TIER1_ROUTING_INDEX.md` — proposed canonical name; subject to #2460 contract's final naming rule |
| Raw inventory (modified with preamble only) | `docs/CONTENT_INDEX.md` |
| Docs entry point update | `docs/README.md` |
| Regression test | `tests/docs/test_workspace_hub_curated_routing_index.py` |
| Stale-reference guard extension | `tests/docs/test_banned_stale_references.py` |
| Top-level noise cleanup | `git rm` of 10 literal non-file-named artifacts enumerated in Evidence |
| Plan index update | `docs/plans/README.md` |
| Plan review — Claude (terminal-1 self-review) | `scripts/review/results/2026-04-23-plan-2464-claude.md` |
| Plan review — Codex (to dispatch after #2460 approval) | `scripts/review/results/YYYY-MM-DD-plan-2464-codex.md` |
| Plan review — Gemini (to dispatch after #2460 approval) | `scripts/review/results/YYYY-MM-DD-plan-2464-gemini.md` |

---

## Deliverable

A curated workspace-hub tier-1 routing index at `docs/TIER1_ROUTING_INDEX.md` linked from `docs/README.md`, containing an issue-type → repo → path matrix, with `docs/CONTENT_INDEX.md` explicitly demoted to its raw-inventory role via a preamble, 10 literal non-file-named noise artifacts deleted from repo root, and a regression test preventing reintroduction of those noise patterns and ensuring the curated/raw split stays intact.

---

## Pseudocode

```text
function build_curated_tier1_routing_index():
    # Subordinate to #2460 contract once it lands
    read #2460 TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md for required-surface rules
    for each tier-1 repo in {workspace-hub, digitalmodel, assetutilities, aceengineer-website}:
        record repo name, AGENTS.md path, docs/README.md path, operator_map path, registry path
        record concise "what belongs here" sentence
        link the scorecard status row for this repo
    build issue-type → repo → path matrix with rows for at least:
        "engineering calculation", "OrcaFlex/OrcaWave modeling", "harness/infrastructure",
        "documentation", "website/GTM", "knowledge/intelligence", "data pipeline",
        "CI/CD", "cross-repo coordination"
    link intelligence-accessibility-registry.yaml as cross-reference
    link #2460 contract as the source of truth

function demote_content_index_to_raw_inventory():
    prepend preamble to docs/CONTENT_INDEX.md declaring:
        - this file is the RAW repo-content inventory produced by scripts/search/build_content_index.py
        - it is NOT the curated tier-1 routing surface
        - for curated routing, see docs/TIER1_ROUTING_INDEX.md
        - per #2460 contract: MUST NOT be treated as active routing authority
    do not truncate or restructure the inventory body; scope is preamble only

function clean_top_level_noise():
    for each path in 10 enumerated literal noise filenames:
        verify path is one of the 10 enumerated; refuse to delete anything else
        git rm the path
    do not touch dated operational artifacts (see Risks → Not in scope)

function update_docs_readme():
    add a "Tier-1 routing" section that links:
        - docs/TIER1_ROUTING_INDEX.md (primary)
        - docs/SKILLS_INDEX.md (sibling curated surface)
        - data/document-index/intelligence-accessibility-registry.yaml (cross-reference)
        - docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md (#2460 contract)
        - docs/standards/TIER1_INDEXING_CHECKLIST.md (#2460 checklist)
    add a negative link: "docs/CONTENT_INDEX.md is NOT a curated routing surface"

function implement_with_tdd():
    write tests/docs/test_workspace_hub_curated_routing_index.py first
    extend tests/docs/test_banned_stale_references.py STRICT_FILES with the new routing index
    run both test files; confirm failure before any doc edits
    then create docs/TIER1_ROUTING_INDEX.md
    then prepend CONTENT_INDEX.md preamble
    then git rm the 10 literal noise files
    then edit docs/README.md
    then update docs/plans/README.md
    rerun targeted tests until green

function validate_deliverable():
    assert docs/TIER1_ROUTING_INDEX.md exists
    assert docs/TIER1_ROUTING_INDEX.md contains an issue-type → repo → path matrix
        with at least 9 issue types covered and all 4 tier-1 repos referenced
    assert docs/TIER1_ROUTING_INDEX.md links the #2460 contract explicitly
    assert docs/CONTENT_INDEX.md has a preamble that:
        - declares its raw-inventory role
        - cross-links to the curated routing index
        - repeats the #2460 negative-authority rule
    assert none of the 10 enumerated literal noise filenames remain tracked at repo root
    assert docs/README.md links TIER1_ROUTING_INDEX.md, the accessibility registry,
        the #2460 contract, and the #2460 checklist
    assert docs/README.md contains a negative statement that CONTENT_INDEX.md is raw-inventory only
    assert tests/docs/test_banned_stale_references.py STRICT_FILES includes docs/TIER1_ROUTING_INDEX.md
    assert docs/plans/README.md contains the #2464 index row
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/TIER1_ROUTING_INDEX.md` | curated tier-1 routing surface; issue-type → repo → path matrix; single trusted entry for workers routing future issue work |
| Modify | `docs/CONTENT_INDEX.md` | prepend preamble declaring raw-inventory role, cross-linking curated index, repeating #2460 negative-authority rule; body unchanged |
| Delete | `**Complexity:**` (repo root) | top-level non-file-named noise per scorecard |
| Delete | `**Date:**` (repo root) | top-level non-file-named noise per scorecard |
| Delete | `**Issue:**` (repo root) | top-level non-file-named noise per scorecard |
| Delete | `**Review` (repo root) | top-level non-file-named noise per scorecard |
| Delete | `**Source` (repo root) | top-level non-file-named noise per scorecard |
| Delete | `**Status:**` (repo root) | top-level non-file-named noise per scorecard |
| Delete | `-` (repo root) | top-level non-file-named noise per scorecard |
| Delete | `Compatibility` (repo root) | top-level non-file-named noise per scorecard |
| Delete | `Comprehensive` (repo root) | top-level non-file-named noise per scorecard |
| Delete | `This` (repo root) | top-level non-file-named noise per scorecard |
| Modify | `docs/README.md` | link TIER1_ROUTING_INDEX.md, accessibility registry, #2460 contract + checklist; negative statement about CONTENT_INDEX.md |
| Create | `tests/docs/test_workspace_hub_curated_routing_index.py` | regression coverage for every validate_deliverable assertion above |
| Modify | `tests/docs/test_banned_stale_references.py` | add `docs/TIER1_ROUTING_INDEX.md` to STRICT_FILES |
| Update | `docs/plans/README.md` | add this #2464 plan row |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_tier1_routing_index_exists` | curated index is present at `docs/TIER1_ROUTING_INDEX.md` | path | file exists |
| `test_tier1_routing_index_contains_issue_type_to_repo_to_path_matrix` | matrix covers at least 9 issue types AND references all 4 tier-1 repos (workspace-hub, digitalmodel, assetutilities, aceengineer-website) | index text | matrix present with required coverage |
| `test_tier1_routing_index_links_2460_contract` | index explicitly links `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` as the source-of-truth contract | index text | link present |
| `test_tier1_routing_index_links_accessibility_registry` | index cross-references `data/document-index/intelligence-accessibility-registry.yaml` | index text | link present |
| `test_content_index_has_raw_inventory_preamble` | CONTENT_INDEX.md starts with a preamble declaring raw-inventory role, cross-linking TIER1_ROUTING_INDEX.md, and repeating the #2460 negative-authority rule | CONTENT_INDEX.md text | preamble + negative-authority sentence present |
| `test_content_index_is_not_linked_as_curated_routing_surface` | `docs/README.md` does not link CONTENT_INDEX.md under a heading that implies it is a curated routing surface | README.md text | CONTENT_INDEX.md absent from curated-routing sections |
| `test_no_literal_noise_files_at_repo_root` | none of the 10 enumerated literal filenames ``**Complexity:**``, ``**Date:**``, ``**Issue:**``, ``**Review``, ``**Source``, ``**Status:**``, ``-``, ``Compatibility``, ``Comprehensive``, ``This`` remain tracked at repo root | `git ls-files --error-unmatch` for each path | all error (not tracked) |
| `test_docs_readme_links_tier1_routing_index` | README.md links TIER1_ROUTING_INDEX.md | README.md text | link present |
| `test_docs_readme_links_intelligence_accessibility_registry` | README.md links `data/document-index/intelligence-accessibility-registry.yaml` (scorecard-cited discoverability gap) | README.md text | link present |
| `test_docs_readme_links_2460_contract_and_checklist` | README.md links both the #2460 contract doc and checklist from the tier-1 routing section | README.md text | both links present |
| `test_docs_readme_negative_statement_about_content_index` | README.md explicitly states CONTENT_INDEX.md is raw-inventory only, not curated routing | README.md text | negative statement present |
| `test_routing_index_under_strict_files_guard` | `tests/docs/test_banned_stale_references.py` STRICT_FILES includes `docs/TIER1_ROUTING_INDEX.md` | test source | path present in STRICT_FILES |
| `test_plans_readme_indexes_2464_plan` | plan index includes #2464 row | `docs/plans/README.md` | row present |
| `test_tdd_sequence_requires_tests_fail_before_doc_edits` | implementation notes require writing the new test + extending STRICT_FILES first, confirming both fail, before creating routing index / editing CONTENT_INDEX.md / deleting noise files / editing README.md | plan text | explicit test-first sequence present |

---

## Acceptance Criteria

- [ ] `docs/TIER1_ROUTING_INDEX.md` exists as the curated workspace-hub tier-1 routing surface
- [ ] routing index contains an issue-type → repo → path matrix covering at least 9 issue types and referencing all 4 tier-1 repos (workspace-hub, digitalmodel, assetutilities, aceengineer-website)
- [ ] routing index links `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` (the #2460 contract) as its source of truth
- [ ] routing index cross-references `data/document-index/intelligence-accessibility-registry.yaml`
- [ ] `docs/CONTENT_INDEX.md` begins with a preamble that (a) declares its raw-inventory role, (b) cross-links the curated routing index, (c) repeats the sentence `MUST NOT treat any tier-1 indexing scorecard under docs/reports/ as required canonical authority` from the #2460 contract (adapted as a negative-authority rule that applies to CONTENT_INDEX.md itself too)
- [ ] 10 literal non-file-named noise artifacts are removed from repo root: ``**Complexity:**``, ``**Date:**``, ``**Issue:**``, ``**Review``, ``**Source``, ``**Status:**``, ``-``, ``Compatibility``, ``Comprehensive``, ``This``
- [ ] `docs/README.md` links the curated routing index, the intelligence accessibility registry, and both the #2460 contract doc and checklist
- [ ] `docs/README.md` contains an explicit negative statement that `docs/CONTENT_INDEX.md` is a raw-inventory surface, not a curated routing surface
- [ ] `tests/docs/test_banned_stale_references.py` STRICT_FILES list includes `docs/TIER1_ROUTING_INDEX.md`
- [ ] `docs/plans/README.md` includes the #2464 index row
- [ ] targeted regression tests pass: `uv run pytest tests/docs/test_workspace_hub_curated_routing_index.py -v`
- [ ] existing curated-doc stale-reference guard still passes: `uv run pytest tests/docs/test_banned_stale_references.py -v`
- [ ] full docs-test suite passes: `uv run pytest tests/docs/ -v`
- [ ] implementation sequencing: the new test file AND the `STRICT_FILES` extension are written first and confirmed failing before any doc creation / CONTENT_INDEX.md edit / noise-file deletion / README.md edit
- [ ] review artifacts are posted to `scripts/review/results/` (initial Claude self-review at `2026-04-23-plan-2464-claude.md`; Codex and Gemini reruns dispatched after #2460 approval lands)

---

## Adversarial Review Summary

Terminal-1 (Claude-only) overnight self-review is recorded for traceability. External Codex and Gemini reruns must be dispatched after #2460 approval lands, since this plan's implementation is gated by the #2460 contract's final shape.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (terminal-1 self-review, 2026-04-23) | MINOR | See `scripts/review/results/2026-04-23-plan-2464-claude.md`. Main residuals: (a) final routing-index filename is proposed, not locked, pending #2460 contract; (b) broader top-level cleanup deliberately out of scope may leave ~20 dated artifacts at root. |
| Codex | PENDING | Dispatch after #2460 status:plan-approved lands. Scope this reviewer will focus on: retrieval-contract class union and alignment with the #2460 contract's finalized required-surface rules. |
| Gemini | PENDING | Dispatch after #2460 status:plan-approved lands. Scope this reviewer will focus on: internal consistency between TDD tests, acceptance criteria, and pseudocode (its historical strength on #2460). |

**Current draft state:** PENDING EXTERNAL REVIEW — this plan is dependency-gated on #2460. Implementation must not begin until both (1) #2460 is `status:plan-approved` AND (2) external Codex+Gemini review of this plan has run and been resolved. Posting this plan to GitHub as `status:plan-review` is permitted before #2460 approval so users can see the dependency chain.

---

## Risks and Open Questions

### Not in scope (delegated)

- **Broader top-level cleanup** — the ~30+ additional top-level tracked artifacts (dated gmail/skestates/issue scratch files, runtime byproducts like `nohup.out` and `transcript_raw.json`) are flagged in Evidence but NOT included in this issue's `git rm` list. Scope is limited to the 10 literal non-file-named noise artifacts because those are the ones the scorecard explicitly enumerates as routing-noise. A follow-up issue should handle the dated/operational artifact cleanup.
- **`scripts/search/build_content_index.py` behavior** — the generator's ignore-list is narrow, which is why CONTENT_INDEX.md is large. Tightening the generator is out of scope; this plan only preambles the output.
- **Tier-1 repo-specific remediation** — for assetutilities (#2461), digitalmodel (#2462), aceengineer-website (#2463), and the daily-freshness loop (#2465). This plan addresses only workspace-hub.
- **`docs/CONTENT_INDEX.md` restructuring or truncation** — preamble-only. Body restructuring would be a separate issue.

### Dependencies

- **Hard prerequisite:** `#2460` tier-1 indexing and code-placement contract must land as `status:plan-approved` and its contract doc must exist at `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` before implementation of #2464 begins. This plan explicitly references the contract doc and checklist; attempting to implement without the contract means the routing index's "what counts as a curated surface" definition has no source of truth.
- **Upstream:** `#2390` epic llm-wiki strengthening roadmap Work Stream G — names this issue as workspace-hub remediation step (5/6 in the sequence #2460 → #2461 → #2462 → #2463 → **#2464** → #2465).
- **Soft prerequisite (ordering preference, not a hard gate):** #2461, #2462, #2463 remediations should ideally complete before #2464 so the routing index's rows for those repos reflect their post-remediation state. If #2464 lands before #2461-#2463, the routing index will need a follow-up update.

### Risks

- **Risk:** The final canonical name for the curated routing index (`docs/TIER1_ROUTING_INDEX.md` proposed here) is subject to the #2460 contract's required-surface naming rule. If #2460 locks a different filename (e.g., the contract's "docs/README.md routing table" vs. a dedicated file), this plan's acceptance criteria and test names must be updated in the same PR. Flagged for reviewer attention.
- **Risk:** Deleting tracked files with unusual names (`**Complexity:**`, `-`, etc.) may require careful shell quoting; implementation must verify `git rm` completes for each exact literal before proceeding. A wrong glob could delete legitimate files.
- **Risk:** `docs/CONTENT_INDEX.md` is 30,084 lines and is regenerated by `scripts/search/build_content_index.py`; the generator may overwrite the preamble on next run unless it is taught to preserve leading comment blocks. Mitigation: the test asserts preamble presence, so a regeneration that strips it would fail CI. Implementation should also verify the generator's overwrite behavior and, if necessary, file a follow-up to teach it to preserve the preamble.
- **Risk:** The negative statement in README.md about CONTENT_INDEX.md is easy to soften during review; the regression test pins the exact semantics (test_content_index_is_not_linked_as_curated_routing_surface and test_docs_readme_negative_statement_about_content_index).
- **Open:** Should the tier-1 routing matrix live in `docs/TIER1_ROUTING_INDEX.md` body or be a linked YAML under `data/document-index/` that the routing index renders from? This plan keeps it in-body for simplicity; converting to a YAML-sourced matrix can be a follow-up.
- **Open:** Should root-level `AGENTS.md` and `CLAUDE.md` also link TIER1_ROUTING_INDEX.md, or is `docs/README.md` sufficient? Per `.claude/rules/coding-style.md` Agent Harness Files cap (≤20 lines), both are already size-constrained; linking from docs/README.md is minimal and sufficient. Flagged for reviewer.

---

## Complexity: T2

**T2** — one new curated document, one documentation file modified (preamble only), 10 file deletions, one docs index update, one test-suite extension, two new regression tests. Not a trivial docs edit (multi-file, dependency-gated on #2460) but no runtime or module implementation. TDD required.
