# Plan for #2487: Inventory readiness spine — raw data to GTM matrix and dispatch board

> **Status:** draft v3
> **Complexity:** T2
> **Date:** 2026-04-25
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2487

---

## Resource Intelligence Summary

### Existing repo code
- Found: `tools/SCHEMA_COMPARISON.md` — compares `/mnt/ace/.ace-knowledge/index.db` and `/mnt/ace/O&G-Standards/_inventory.db`, including overlap, extracted text, and embedding/chunk counts. This is the source baseline for the readiness matrix.
- Found: `data/document-index/registry.yaml` — existing document-index corpus summary with 1,033,933 total docs, source/domain counts, repo-level standards/gap counts, and domain buckets.
- Found: `data/document-index/resource-intelligence-maturity.yaml` — existing maturity source of truth. It explicitly says YAML is the source of truth and Markdown must not diverge; this plan mirrors that source-of-truth pattern.
- Found: `scripts/data/og-standards/inventory.py` — standards inventory builder surface.
- Found: `scripts/data/document-index/phase-a-index.py`, `scripts/data/document-index/validate-index-metadata.py`, and `scripts/data/document-index/build-index-other-bucket-packs.py` — document-index inventory/validation/bucket-pack surfaces that the readiness matrix should reference rather than duplicate.
- Found: `scripts/knowledge/build-knowledge-index.sh` and `scripts/search/build_content_index.py` — existing knowledge/search index builders.
- Gap: no canonical `config/knowledge/inventory-readiness.yaml`, `scripts/knowledge/validate_inventory_readiness.py`, `tests/knowledge/test_inventory_readiness.py`, or `docs/reports/inventory-readiness-matrix-2026-04-25.md` surface exists.

### Standards / contracts
| Standard / contract | Status | Source |
|---|---|---|
| O&G standards inventory corpus | partial | `tools/SCHEMA_COMPARISON.md` shows `_inventory.db` contains 27,980 standards documents, 26,982 extracted-text rows, and 1,043,616 chunks. |
| Document identity / layer ownership | normative | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` defines L1-L6 layers and canonical `doc_key` rules. |
| Durable-vs-transient boundary | normative | `docs/plans/2026-04-16-issue-2209-durable-vs-transient-knowledge-boundary.md` points to the durable boundary policy and layer ownership constraints. |
| Calculation-output citation bridge | closed issue evidence | #2481 is CLOSED and defines the calculation-output provenance bridge. No local #2481 plan file exists; the matrix must cite #2481 issue/closeout evidence or implemented artifacts, not a nonexistent plan path. |
| Wiki standards-page schema | live issue dependency | #2471 is OPEN and `status:plan-approved` for sanctioned CSA/wiki standards routing. No local #2471 plan file exists; readiness rows must cite the live issue, implemented wiki artifacts, or downgrade affected stages to `PARTIAL`/`BLOCKED`. |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/log.md` — engineering wiki seed inventory and source classes exist, but that state is not yet connected to provider dispatch or calculation/GTM readiness.
- `knowledge/wikis/engineering/CLAUDE.md` — local wiki frontmatter expectations and ingest workflow.
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — parent model requires canonical `doc_key` identity; if a target wiki page lacks parent-required identity fields, the matrix marks the stage as `PARTIAL` or `BLOCKED`, never `READY`.

### Documents and issues consulted
- GitHub issue #2487 — spine issue for the raw-data → llm-wiki → calculation-code → parametric-output → website/GTM control surface.
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` / #2205 — parent operating model and L1-L6 ownership rules.
- `docs/plans/2026-04-13-issue-2096-intelligence-accessibility-map.md` — L4 accessibility/entry-point precedent and machine-readable sibling surface pattern.
- `docs/plans/2026-04-16-issue-2209-durable-vs-transient-knowledge-boundary.md` — durable/transient layer boundary plan and source policy.
- GitHub issue #2481 — closed calculation-output citation contract; use issue/closeout evidence, not a nonexistent local plan file.
- GitHub issue #2471 — open plan-approved sanctioned CSA/wiki standards routing issue; use the live issue as dependency evidence because no local plan file exists.
- GitHub issues #2392, #2389, #2382, #2363, #2362 — existing source/wiki/provenance issues that become dependency rows, not absorbed implementation.
- GitHub issues #2346, #2464, #2465, #2402, #2403 — provider/work-queue/indexing/GTM issues represented in the dispatch board.
- `docs/reports/provider-work-queue.md` — current provider queue is an evidence source, not a target to fabricate. Current ready counts may be below operating targets and must be reported as backlog deficit.
- `docs/plans/README.md` — planning index and hard-stop workflow.

### Gaps identified
- No durable readiness matrix ties raw inventory assets to llm-wiki promotion, calculation-code provenance, parametric output readiness, GTM consumption, owning GitHub issue, and provider lane.
- No machine-readable artifact currently pins stage status as `READY`, `PARTIAL`, `MISSING`, `STALE`, or `BLOCKED` across the whole value chain.
- Existing issues cover many subpieces, but no parent dispatch surface prevents duplicate work or identifies the next Codex/Gemini/Claude packages.
- Existing readiness/status words are scattered across registries, issue labels, reports, and plans; this issue defines one status decision table for this matrix without changing child issue semantics.
- Existing provider-work-queue ready counts are below the target inventory depth; this issue must report the deficit rather than inventing candidates.

### Evidence
**Issue statuses** verified 2026-04-25 via `gh issue view`:
- `#2487` OPEN — inventory readiness spine
- `#2471` OPEN, `status:plan-approved` — sanctioned CSA/wiki standards routing
- `#2481` CLOSED — calculation-output citation contract
- `#2392` OPEN — wiki coverage-gap detector
- `#2389` OPEN — thread `source_doc_key` through promotion pipeline
- `#2382` OPEN — promotion audit-trail checker
- `#2363` OPEN — `wiki_refs` reverse lookup
- `#2362` OPEN — back-populate `doc_key` on standards-transfer ledger
- `#2346` OPEN, `status:plan-approved` — GTM customized-demo pipeline
- `#2465` OPEN, `status:plan-approved` — tier-1 indexing freshness audit
- `#2464` OPEN, `status:plan-approved` — curated tier-1 routing index
- `#2402` OPEN, `status:plan-review` — embeddings index L2+L3 + query CLI
- `#2403` OPEN, `status:plan-approved` — embeddings model-selection spike

**File existence** verified 2026-04-25:
- EXISTS: `tools/SCHEMA_COMPARISON.md`
- EXISTS: `data/document-index/registry.yaml`
- EXISTS: `data/document-index/resource-intelligence-maturity.yaml`
- EXISTS: `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- EXISTS: `docs/plans/2026-04-13-issue-2096-intelligence-accessibility-map.md`
- EXISTS: `docs/plans/2026-04-16-issue-2209-durable-vs-transient-knowledge-boundary.md`
- EXISTS: `scripts/data/og-standards/inventory.py`
- EXISTS: `scripts/data/document-index/phase-a-index.py`
- EXISTS: `scripts/data/document-index/validate-index-metadata.py`
- EXISTS: `scripts/data/document-index/build-index-other-bucket-packs.py`
- EXISTS: `scripts/knowledge/build-knowledge-index.sh`
- EXISTS: `scripts/search/build_content_index.py`
- EXISTS: `knowledge/wikis/engineering/wiki/log.md`
- EXISTS: `docs/reports/provider-work-queue.md`
- ABSENT: `docs/plans/2026-04-24-issue-2481-calc-output-citation-contract.md`; do not cite as local evidence.
- ABSENT: `docs/plans/2026-04-23-issue-2471-wiki-standards-path.md`; do not cite as local evidence.
- MISSING (new): `config/knowledge/inventory-readiness.yaml`
- MISSING (new): `scripts/knowledge/validate_inventory_readiness.py`
- MISSING (new): `tests/knowledge/test_inventory_readiness.py`
- MISSING (new): `docs/reports/inventory-readiness-matrix-2026-04-25.md`

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-25-issue-2487-inventory-readiness-spine.md` |
| Plan index row | `docs/plans/README.md` |
| Canonical machine artifact | `config/knowledge/inventory-readiness.yaml` |
| Validator | `scripts/knowledge/validate_inventory_readiness.py` |
| Tests | `tests/knowledge/test_inventory_readiness.py` |
| Derived human report | `docs/reports/inventory-readiness-matrix-2026-04-25.md` |

---

## Deliverable

A machine-checked inventory-readiness control surface consisting of `config/knowledge/inventory-readiness.yaml`, a validator, tests, and a derived Markdown report that map the raw-data → llm-wiki → calculation-code → parametric-output → website/GTM value chain to existing assets, owning issues, readiness status, backlog deficit, and Gemini/Claude/Codex provider lanes.

---

## Canonical Schema Contract

`config/knowledge/inventory-readiness.yaml` is the single source of truth. `docs/reports/inventory-readiness-matrix-2026-04-25.md` is a derived rendering and must not introduce fields or statuses absent from YAML.

### Top-level shape
```yaml
schema_version: "1.0.0"
generated_at: "2026-04-25T00:00:00Z"
source_of_truth: "config/knowledge/inventory-readiness.yaml"
derived_reports:
  - "docs/reports/inventory-readiness-matrix-2026-04-25.md"
allowed_statuses: [READY, PARTIAL, MISSING, STALE, BLOCKED]
stages: [raw_data, inventory, extraction, llm_wiki, calculation_code, parametric_output, website_gtm]
provider_lanes: [gemini, claude, codex, mixed, none]
readiness_rows: []
dispatch_board:
  operating_targets:
    codex_candidate_target: 8
    gemini_task_target: 5
  current_counts:
    codex_candidates: 0
    gemini_tasks: 0
    claude_reviews: 0
  backlog_deficit:
    codex_candidates: 8
    gemini_tasks: 5
  codex_candidates: []
  gemini_batches: []
  claude_reviews: []
follow_up_candidates: []
```

### `readiness_rows[]` required fields
```yaml
- source_id: "og-standards-inventory"
  source_name: "O&G Standards inventory"
  layer: "L2"
  source_type: "database"
  authority: "canonical"
  authoritative_artifacts:
    - ref: "tools/SCHEMA_COMPARISON.md"
      kind: "path"
      evidence: "documents/chunks baseline"
  freshness:
    last_verified: "2026-04-25"
    cadence: "weekly"
    status: "READY"
    evidence: "manual verification during planning"
  stage_statuses:
    raw_data: {status: "READY", evidence: "...", owning_issue: null, dependency_issues: [], next_action: "none"}
    inventory: {status: "READY", evidence: "...", owning_issue: null, dependency_issues: [], next_action: "none"}
    extraction: {status: "PARTIAL", evidence: "...", owning_issue: 2402, dependency_issues: [2403], next_action: "complete index/query lane"}
    llm_wiki: {status: "PARTIAL", evidence: "#2392 plus wiki/doc_key contract check", owning_issue: 2392, dependency_issues: [2362, 2363, 2389, 2471], next_action: "map coverage and metadata gaps"}
    calculation_code: {status: "PARTIAL", evidence: "#2481 closed issue + implemented artifacts", owning_issue: 2481, dependency_issues: [2471], next_action: "apply citation contract in child packages"}
    parametric_output: {status: "MISSING", evidence: "no mapped output issue", owning_issue: null, dependency_issues: [], next_action: "create candidate or map existing"}
    website_gtm: {status: "PARTIAL", evidence: "#2346", owning_issue: 2346, dependency_issues: [], next_action: "feed GTM package"}
  provider_lane: "mixed"
  package_family: "raw-data-to-gtm"
  next_action: "populate first matrix row"
```

### `dispatch_board` item shape
```yaml
operating_targets:
  codex_candidate_target: 8
  gemini_task_target: 5
current_counts:
  codex_candidates: 3
  gemini_tasks: 1
  claude_reviews: 1
backlog_deficit:
  codex_candidates: 5
  gemini_tasks: 4
codex_candidates:
  - issue: 2464
    readiness: "plan-approved"
    package_family: "inventory"
    rationale: "bounded implementation/test/refactor lane"
    dependency_issues: []
gemini_batches:
  - batch_id: "inventory-scout-001"
    readiness: "ready"
    tasks: ["source inventory"]
    output_artifact: "docs/reports/gemini-inventory-readiness-scout-2026-04-25.md"
    dependency_issues: []
claude_reviews:
  - issue: 2487
    readiness: "plan-review"
    rationale: "synthesis/review lane"
```

### `follow_up_candidates[]` shape
```yaml
- title: "feat(...): ..."
  reason: "unmapped gap found by matrix"
  source_row: "og-standards-inventory"
  stage: "parametric_output"
  duplicate_search: "query used to check existing issues"
  recommended_provider: "codex"
```

### Nullability and omission rules
- Required keys must be present even when values are unknown.
- Unknown dates use `null`, not omitted keys.
- `owning_issue` is `null` only when the associated `next_action` explains why no issue is mapped.
- `dependency_issues` is an empty list when there are no known dependencies.
- Markdown rendering must fail validation if YAML contains a row that cannot render all stage columns.

---

## Readiness Status Decision Rules

| Status | Decision rule |
|---|---|
| `READY` | Required artifact exists, evidence is cited, no open dependency blocks the stage, and the stage has a defined consumer or next action. |
| `PARTIAL` | Some artifacts/evidence exist, but an open issue, missing metadata field, incomplete extraction, or incomplete consumer mapping remains. |
| `MISSING` | No artifact/evidence exists for the stage and no equivalent existing issue/deliverable is mapped. |
| `STALE` | Artifact exists but is older than the declared cadence, contradicted by a newer source, or marked as drifted/stale by a current issue/report. |
| `BLOCKED` | Work cannot proceed until a named dependency issue, machine access, licensing condition, or review/tooling blocker is resolved. |

Open dependency treatment:
- If a stage can produce a useful partial artifact while dependency issues remain open, set `PARTIAL` and list `dependency_issues`.
- If a stage cannot produce any valid artifact without the dependency, set `BLOCKED`.
- If a dependency is only a downstream enhancement, do not downgrade; keep `READY` and list it in `next_action` or follow-up notes.

Wiki metadata contract handling:
- The parent operating model requires canonical `doc_key` identity, while local wiki CLAUDE.md frontmatter guidance may not list `doc_key` among required fields.
- If a row depends on wiki metadata and the target wiki page lacks parent-required `doc_key`/standards identity fields, the `llm_wiki` stage is `PARTIAL` or `BLOCKED`, never `READY`.
- The matrix records this as evidence of contract drift; this issue does not silently change wiki frontmatter rules.

Dispatch target handling:
- Operating targets express desired inventory depth, not validation truth.
- Validator must not fail only because current ready counts are below target.
- Below-target counts render as `backlog_deficit` and `follow_up_candidates`, preserving truthful readiness.

---

## Scope Boundaries

### In scope now
- Create the readiness YAML, validator, tests, and derived Markdown matrix.
- Reuse existing inventory/index artifacts; do not rebuild `_inventory.db` or `.ace-knowledge/index.db`.
- Map existing GitHub issues before proposing new ones.
- Define status rules, provider lanes, current counts, backlog deficits, and next-action candidates.

### Out of scope now
- Implementing #2392, #2389, #2382, #2363, #2362, #2402, #2403, #2346, or other child issues.
- Reprocessing the entire O&G standards corpus.
- Changing llm-wiki frontmatter contracts beyond recording #2471/#2481 dependency effects.
- Shipping website/GTM changes.
- Running a broad Gemini scouting batch as part of implementation; this issue only defines evidenced batch candidates and backlog deficits in `dispatch_board.gemini_batches`.

---

## Pseudocode
```text
load YAML from config/knowledge/inventory-readiness.yaml
require exact top-level keys, canonical stage list, status enum, and provider lane enum
for each readiness row:
    require unique source_id
    require authoritative_artifacts and freshness evidence
    require all seven stage_statuses
    require each stage to have status, evidence, owning_issue, dependency_issues, next_action
    enforce open-dependency treatment, wiki metadata contract handling, and nullability rules
validate dispatch_board:
    record current execution-ready candidates exactly as evidenced by provider-work-queue and issue labels
    record backlog_deficit targets separately from readiness status
    require every Codex/Gemini/Claude entry to have rationale, readiness, and dependency state
    do not fail validation merely because current ready counts are below operating target
validate follow_up_candidates:
    require duplicate_search text before listing any new issue candidate
render Markdown from validated YAML only
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Verify | `docs/plans/2026-04-25-issue-2487-inventory-readiness-spine.md` | canonical plan already drafted; keep synchronized with review findings |
| Update | `docs/plans/README.md` | maintain plan index row |
| Create | `config/knowledge/inventory-readiness.yaml` | canonical machine-readable readiness matrix and dispatch board |
| Create | `scripts/knowledge/validate_inventory_readiness.py` | deterministic validation + Markdown rendering entry point |
| Create | `tests/knowledge/test_inventory_readiness.py` | TDD tests for schema, status semantics, provider dispatch, and report rendering |
| Create | `docs/reports/inventory-readiness-matrix-2026-04-25.md` | derived human-readable report generated from YAML |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_schema_requires_all_top_level_keys` | YAML cannot omit canonical top-level keys | minimal YAML missing `dispatch_board` | validation error naming missing key |
| `test_readiness_rows_require_all_stages` | every row contains all seven value-chain stages | row missing `website_gtm` | validation error |
| `test_status_enum_and_decision_fields` | statuses are allowed and each stage has evidence/next_action/dependency fields | row with `UNKNOWN` status or empty evidence | validation error |
| `test_open_dependency_can_be_partial_or_blocked_only` | dependency issues force `PARTIAL`/`BLOCKED` unless downstream-only | row with dependency issue and `READY` without rationale | validation error |
| `test_wiki_doc_key_contract_blocks_ready` | wiki rows lacking parent-required identity fields cannot be `READY` | wiki-backed row with no `doc_key` evidence | validation error or downgrade evidence |
| `test_dispatch_board_deficit_is_reported_not_fabricated` | low ready counts are represented as backlog deficit, not fake readiness | sample with 3 Codex candidates and 1 Gemini task | validation passes and reports deficit |
| `test_existing_issue_mapping_precedes_followup_candidates` | follow-up candidates require duplicate-search text | follow-up candidate without duplicate_search | validation error |
| `test_markdown_report_renders_from_yaml_only` | report contains all stages and provider groups from YAML | valid sample YAML | Markdown includes all seven stages plus Codex/Gemini/Claude groups |
| `test_repo_fixture_validates_current_inventory_file` | checked-in `config/knowledge/inventory-readiness.yaml` validates | repo fixture | zero validation errors |

Validation commands:
```bash
uv run pytest tests/knowledge/test_inventory_readiness.py -v
uv run --no-project python scripts/knowledge/validate_inventory_readiness.py --config config/knowledge/inventory-readiness.yaml --output docs/reports/inventory-readiness-matrix-2026-04-25.md
```

---

## Acceptance Criteria

- [ ] `config/knowledge/inventory-readiness.yaml` exists and validates against the schema contract in this plan.
- [ ] `scripts/knowledge/validate_inventory_readiness.py` validates YAML and renders the Markdown report from YAML only.
- [ ] `tests/knowledge/test_inventory_readiness.py` includes failing-first coverage for schema keys, stage completeness, status semantics, dependency handling, wiki identity handling, dispatch deficits, duplicate-search requirements, and Markdown rendering.
- [ ] `docs/reports/inventory-readiness-matrix-2026-04-25.md` exists and includes all seven value-chain stage columns plus provider dispatch groups.
- [ ] Every matrix row has evidence, owning issue or null-with-next-action rationale, readiness status, provider lane, and next action.
- [ ] Existing issues are mapped before any new follow-up candidate is listed.
- [ ] Dispatch board records current evidenced Codex/Gemini/Claude candidates, shows backlog deficit versus the operating target of 8 Codex candidates and 5 Gemini tasks, and does not fabricate readiness to satisfy the target.

---

## Adversarial Review Summary

Review evidence is stored outside this plan under `scripts/review/results/`. This section is intentionally not used as implementation acceptance criteria.

---

## Risks and Open Questions

- **Risk:** The issue can become too broad if implementation starts on child packages. Mitigation: this scope is limited to matrix/config/validator/report; child issue implementation remains out of scope.
- **Risk:** Existing DBs may be host-local. Mitigation: rows record evidence, freshness, and authority; validator does not require opening host-local DB files.
- **Risk:** #2392 overlaps with inventory × wiki diff. Mitigation: #2392 is mapped as an owning/dependency issue; this issue does not implement #2392 logic.
- **Risk:** #2471 schema availability affects objective scoring for standards-backed llm-wiki/calculation rows. Mitigation: standards-backed rows must cite #2471 live issue or implemented wiki artifacts, otherwise downgrade to `PARTIAL`/`BLOCKED` per decision rules.

---

## Complexity: T2

**T2** — bounded control-plane implementation with one YAML contract, one validator/rendering script, one focused test file, one derived report, and no child pipeline implementation.
