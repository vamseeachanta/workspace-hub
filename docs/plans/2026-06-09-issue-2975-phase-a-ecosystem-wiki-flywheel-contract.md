# Plan for #2975 Phase A: Ecosystem Wiki Flywheel Contract Surfaces

> **Status:** blocked-needs-decision-after-r8
> **Complexity:** T2
> **Date:** 2026-06-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2975
> **Client:** N/A
> **Project:** N/A
> **Review artifacts:** r1-r8 returned MAJOR or APPROVE/NO_OUTPUT split; implementation remains blocked pending owner decision on schema-valid vocabulary before Phase B enforcement.

---

## Resource Intelligence Summary

This Phase A plan narrows [workspace-hub#2975](https://github.com/vamseeachanta/workspace-hub/issues/2975) after the prior omnibus plan's r1-r8 adversarial review found the original single approval unit too large. Phase A will land only the contract surfaces that downstream validator work can consume: standard, governance decision, config, templates, additive schema enum, enum/config sync check, and schema regression tests.

### Existing repo code

- Found: `docs/architecture/execution-manifest.schema.yaml` — already defines `output_residency` for execution manifests but has no explicit public-federal wiki route.
- Found: `docs/architecture/report-evidence-bundle.schema.yaml` — already defines report evidence `output_residency`, fail-closed public output rules, and `sources[].source_class`; Phase A will not overload `source_class`.
- Found: `tests/architecture/test_report_layer_contract.py` — existing regression surface for report-layer schema behavior.
- Found: `tests/architecture/test_execution_layer_contract.py` — existing regression surface for execution-layer schema behavior.
- Found: `.gitattributes` — already enforces LF for `*.yml`, `*.yaml`, and `*.json`; Phase A will add only `*.jsonl text eol=lf`.
- Gap: no `config/ecosystem-wiki-flywheel/source-classification.yaml` exists.
- Gap: no `templates/ecosystem-wiki-flywheel/` examples exist.
- Gap: no standard/generation check keeps a standard fenced YAML block in sync with config.

### Standards

| Standard | Status | Source |
|---|---|---|
| Wiki sibling routing | active | `.claude/rules/wiki-sibling-routing.md` |
| Public federal/vendor data routing | active | `.claude/rules/codes-standards-data-routing.md` |
| Data/execution/report boundary | active | `docs/architecture/data-execution-report-layer-contract.md` |
| Report-derived learning routing | active | `docs/architecture/report-derived-learning-routing.md` |

### LLM Wiki pages consulted

No wiki content will be modified. This is a workspace-hub standard/config/template/schema plan only.

### Documents consulted

- [workspace-hub#2975](https://github.com/vamseeachanta/workspace-hub/issues/2975) — parent issue and governing decision source.
- [workspace-hub#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013) — Phase B child issue for manual validator, helper modules, fixtures, and public-egress enforcement tests.
- `docs/plans/2026-06-08-issue-2975-ecosystem-wiki-flywheel-contract.md` — r8 omnibus draft preserved as historical blocked evidence.
- `scripts/review/results/20260609T160108Z-2026-06-08-issue-2975-ecosystem-wiki-flywheel-contract.md-plan-claude.md` — r8 review finding that Phase A/Phase B split is needed.
- `scripts/review/results/20260609T160108Z-2026-06-08-issue-2975-ecosystem-wiki-flywheel-contract.md-plan-codex.md` — r8 review finding that the non-cuttable validator floor is too large for one approval unit.

### Gaps identified

- No Phase A contract surface exists for source publication class, license terms class, publication state, review state, ledger event type, scheduler state, public identity, and staged publishing order.
- No explicit `public_federal_wiki` output residency exists for BSEE/NOAA/USGS/MMS public-domain data routed to `worldenergydata-wiki`.
- No template family exists for run manifest, run history record, wiki frontmatter, routing ledger events, public projection, quick-reference index entry, and insight bundle metadata.
- No sync/check command exists to keep the standard's machine-readable YAML block aligned with config.

### Evidence

**Issue statuses** verified 2026-06-09 via `gh issue view`:

- `workspace-hub#2975` — OPEN — standard: ecosystem wiki flywheel manifest, provenance, and routing contract
- `workspace-hub#3013` — OPEN — standard: ecosystem wiki flywheel validator and public-egress gate

**File existence** verified by local reads/search:

- EXISTS: `docs/architecture/execution-manifest.schema.yaml`
- EXISTS: `docs/architecture/report-evidence-bundle.schema.yaml`
- EXISTS: `tests/architecture/test_report_layer_contract.py`
- EXISTS: `tests/architecture/test_execution_layer_contract.py`
- EXISTS: `.gitattributes`
- EXISTS: 19 current markdown files under `docs/standards/` and no `docs/standards/README.md`; Phase A standards index creation must index the current set plus the new contract.
- MISSING: `config/ecosystem-wiki-flywheel/source-classification.yaml`
- MISSING: `templates/ecosystem-wiki-flywheel/`
- MISSING: `docs/standards/ECOSYSTEM_WIKI_FLYWHEEL_CONTRACT.md`
- MISSING: `docs/standards/README.md`
- MISSING: `docs/governance/2026-06-09-ecosystem-wiki-flywheel-routing-decision.md`

**Final review evidence requirement**:

Before moving this issue to `status:plan-review`, the final no-MAJOR review wave and GitHub evidence comment must cite fresh output from `scripts/review/attest-plan-claims.sh docs/plans/2026-06-09-issue-2975-phase-a-ecosystem-wiki-flywheel-contract.md`, including issue state for [workspace-hub#2975](https://github.com/vamseeachanta/workspace-hub/issues/2975) and [workspace-hub#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013), file existence/missing-state evidence, reviewed commit SHA, and final review artifact paths.

Current attestation tooling omits `.jsonl` paths; [workspace-hub#3015](https://github.com/vamseeachanta/workspace-hub/issues/3015) tracks that reusable extractor defect. Before moving this plan to `status:plan-review`, the evidence comment must include explicit plan-review proof that `templates/ecosystem-wiki-flywheel/run-history-record.example.jsonl` is `EXPECTED_MISSING` because it is a Phase A deliverable, not an existing artifact. After implementation, code-review/closeout evidence must include explicit `EXISTS` proof for that same JSONL file. The plan-review evidence comment must also include explicit `.gitattributes` proof: `ls -la -- .gitattributes` plus the relevant LF-rule excerpt for `*.yml`, `*.yaml`, and `*.json`; after implementation closeout it must also show the new `*.jsonl` LF rule.

### Phase A Contract Values

`source-classification.yaml` is the contract source of truth. The standard's fenced YAML block is generated from this config; the sync script verifies exact standard/config equality rather than carrying an independent policy copy.

| Group | Values | Public-safe values |
|---|---|---|
| `source_publication_class` | `public-federal-data`, `public-commercial-open`, `open-academic`, `vendor-licensed`, `client-private`, `user-provided-private`, `locally-cached-uncertain`, `mixed`, `blocked` | `public-federal-data`, `public-commercial-open`, `open-academic` |
| `license_terms_class` | `public-domain`, `open-license`, `public-terms-review-required`, `vendor-license`, `client-confidential`, `unknown`, `blocked` | `public-domain`, `open-license` |
| `publication_state` | `public_publishable`, `private_publishable`, `blocked`, `superseded`, `deprecated` | N/A |
| `review_state` | `unreviewed`, `review-required`, `approved`, `approved-with-notes`, `rejected` | N/A |
| `ledger_event_type` | `created`, `linked`, `promoted`, `moved`, `blocked`, `deprecated`, `redacted`, `superseded` | N/A |
| `scheduler_state` | `manual-only`, `eligible-after-two-clean-runs`, `scheduled-enabled`, `scheduled-blocked` | N/A |
| `public_identity.authority_codes` | `bsee`, `noaa`, `usgs`, `mms` | N/A |
| `public_identity.bsee.dataset_slugs` | `well-activity-report`, `production`, `incidents` | N/A |
| `public_identity.id_pattern` | `<authority>:<dataset_slug>:<stable_public_id>` | N/A |
| `publication_sequence.stage_ids` | `public-federal-first`, `fdas-classified`, `hse-marine-segregated` | N/A |
| `freshness_defaults.max_age_days` | `source_retrieval: 180`, `license_terms_review: 365`, `quick_reference_pointer: 30` | N/A |

These values are approval-time seed values for the first version of `source-classification.yaml`. After implementation, `source-classification.yaml` is the only authoritative policy source; the standard's fenced YAML block is generated from it, and this plan is historical approval evidence rather than a future policy authority.

The public-safe subset is single-sourced inside `source-classification.yaml`. The config must carry machine-readable policy lists such as `public_safe_source_publication_classes` and `public_safe_license_terms_classes`; each enum value's `public_safe` flag must match those lists. The sync script may validate config internal consistency, but it must not hardcode an independent public-safe allowlist.

`public_identity` is BSEE-enabled in Phase A: `bsee` dataset slugs are `well-activity-report`, `production`, and `incidents`. `noaa`, `usgs`, and `mms` are present as explicit empty authority entries and structurally blocked until future config edits populate dataset slugs.

`publication_sequence` is machine-readable in config and standard, with stage order:

1. `public-federal-first` -> `public_federal_wiki` -> `worldenergydata-wiki`.
2. `fdas-classified` -> `public_llm_wiki` only after classification, citation, license review, and public projection checks.
3. `hse-marine-segregated` -> private/domain corpus only until segregation, redaction, and legal/security checks are complete.

Each `publication_sequence` stage record must use this schema:

| Key | Required | Contract |
|---|---|---|
| `stage_id` | yes | one of the staged IDs listed above |
| `order` | yes | positive integer; records must sort strictly increasingly by this field |
| `source_publication_class` | yes | enum value from `source_publication_class` |
| `target_output_residency` | yes | `public_federal_wiki`, `public_llm_wiki`, or private/domain corpus value |
| `target_wiki` | conditional | required for public wiki targets; `worldenergydata-wiki` for `public-federal-first` |
| `required_gates` | yes | list of gate IDs required before promotion to the target |
| `blocked_until` | optional | human-readable condition for blocked or future stages |

**Reproduction proofs**:

N/A — this is documentation/governance/schema planning, not a runtime failure report. Implementation still uses TDD for schema/config/template checks.

Source count: 11 distinct issue/file/review sources.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-09-issue-2975-phase-a-ecosystem-wiki-flywheel-contract.md` |
| Historical blocked plan | `docs/plans/2026-06-08-issue-2975-ecosystem-wiki-flywheel-contract.md` |
| Plan index | `docs/plans/README.md` |
| Standard | `docs/standards/ECOSYSTEM_WIKI_FLYWHEEL_CONTRACT.md` |
| Standards index | `docs/standards/README.md` |
| Governance decision | `docs/governance/2026-06-09-ecosystem-wiki-flywheel-routing-decision.md` |
| Config | `config/ecosystem-wiki-flywheel/source-classification.yaml` |
| Enum sync/check script | `scripts/knowledge/sync-ecosystem-wiki-flywheel-standard.py` |
| Templates | `templates/ecosystem-wiki-flywheel/` |
| Architecture schemas | `docs/architecture/execution-manifest.schema.yaml`, `docs/architecture/report-evidence-bundle.schema.yaml` |
| Architecture tests | `tests/architecture/test_report_layer_contract.py`, `tests/architecture/test_execution_layer_contract.py` |
| Phase A tests | `tests/governance/test_ecosystem_wiki_flywheel_phase_a.py` |

---

## Deliverable

Phase A will produce the reusable ecosystem wiki flywheel contract surfaces and leave executable validator behavior to [workspace-hub#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013).

---

## Pseudocode

```text
function sync_standard_from_config(config_path, standard_path, mode):
    load source-classification.yaml
    validate required enum groups, public_identity, and publication_sequence exist
    validate public_safe flags match the config-declared public_safe policy lists
        without hardcoding a separate source/license allowlist in the script
    validate config-to-standard synchronization only; do not validate
        generated bundles, public egress, ledger projections, or legal
        attestation wrappers in Phase A
    render one fenced yaml block rooted at ecosystem_wiki_flywheel_enums
    in --check mode, fail if standard block differs from rendered block
    in --write mode, replace only the fenced block
    after --write mode, a subsequent --check against the same files must pass
```

```text
function extend_output_residency_schemas():
    add public_federal_wiki to execution-manifest output_residency enum
    add public_federal_wiki to report-evidence output_residency enum
    in execution-manifest.schema.yaml:
        leave input_residency unchanged; public_federal_wiki is not an
            execution input/source residency in Phase A
        replace public-output condition predicates that use
            output_residency const public_llm_wiki
        with equivalent enum [public_llm_wiki, public_federal_wiki]
        for both top-level output_residency and nested outputs[].output_residency
        leave the existing promotion_gates contains requirements unchanged
    in report-evidence-bundle.schema.yaml:
        leave sources[].input_residency unchanged; public_federal_wiki is not
            a source/input residency in Phase A
        replace public-output condition predicates that use
            output_residency const public_llm_wiki
        with enum [public_llm_wiki, public_federal_wiki]
        broaden public source-mix and source output constraints from const public_llm_wiki
            to enum [public_llm_wiki, public_federal_wiki]
        leave legal_scan, audience_classification, promotion gate,
            sanitization, and review verdict requirements unchanged
    execution schema rejects public_federal_wiki top-level or nested outputs
        unless full public promotion gates are present
    report evidence schema rejects public_federal_wiki when audience,
        legal scan, claim gates, source residency, or source promotion gates
        would fail the current public_llm_wiki guard
    preserve existing enum values and fail-closed public output constraints
    update execution-layer and report-layer contract tests to prove the
        public_federal_wiki guard with negative validation fixtures, not only
        enum acceptance
```

### Schema Guard Structural Disposition

Before editing either schema, implementation must parse the two schema YAML files and confirm the current structural paths below still hold. Raw text occurrence counts are only a secondary sanity signal; they must not be the pass/fail authority because prose descriptions and comments can mention the same tokens. If any structural path differs, implementation stops and the plan is revised rather than guessing.

`source_class_mix` is a legacy field name but its current enum values are residency/corpus values (`public_llm_wiki`, `domain_private_corpus`, `registered_client_private_corpus`, `ignored_internal_run_artifact`, `no_preserve`), so adding `public_federal_wiki` there is type-consistent. It is not the same field as `sources[].source_class`.

| File | Structural path | Current role | Disposition |
|---|---|---|---|
| `docs/architecture/execution-manifest.schema.yaml` | `properties.input_residency.enum` | input residency enum | Leave unchanged; assert `public_federal_wiki` absent. |
| `docs/architecture/execution-manifest.schema.yaml` | `properties.output_residency.enum` | top-level output residency enum | Add `public_federal_wiki`. |
| `docs/architecture/execution-manifest.schema.yaml` | `properties.outputs.items.properties.output_residency.enum` | output item residency enum | Add `public_federal_wiki`. |
| `docs/architecture/execution-manifest.schema.yaml` | public-output guard for top-level `output_residency` | public-output guard predicate | Replace single-value `const: public_llm_wiki` predicate with `enum: [public_llm_wiki, public_federal_wiki]`; leave `promotion_gates` requirements unchanged. |
| `docs/architecture/execution-manifest.schema.yaml` | public-output guard for nested `outputs[].output_residency` | nested public-output guard predicate | Replace single-value `const: public_llm_wiki` predicate with `enum: [public_llm_wiki, public_federal_wiki]`; leave `promotion_gates` requirements unchanged. |
| `docs/architecture/report-evidence-bundle.schema.yaml` | `properties.output_residency.enum` | top-level output residency enum | Add `public_federal_wiki`. |
| `docs/architecture/report-evidence-bundle.schema.yaml` | `properties.source_class_mix.items.enum` | residency/corpus mix enum despite legacy field name | Add `public_federal_wiki`. |
| `docs/architecture/report-evidence-bundle.schema.yaml` | `properties.sources.items.properties.input_residency.enum` | source input residency enum | Leave unchanged; assert `public_federal_wiki` absent. |
| `docs/architecture/report-evidence-bundle.schema.yaml` | `properties.sources.items.properties.output_residency.enum` | source output residency enum | Add `public_federal_wiki`. |
| `docs/architecture/report-evidence-bundle.schema.yaml` | `properties.published_claims.items.properties.output_residency.enum` | claim output residency enum | Add `public_federal_wiki`. |
| `docs/architecture/report-evidence-bundle.schema.yaml` | claim-level public-output guard predicate under `published_claims.items` | claim public-output guard predicate | Replace single-value `const: public_llm_wiki` predicate with `enum: [public_llm_wiki, public_federal_wiki]`; leave promotion-gate requirements unchanged. |
| `docs/architecture/report-evidence-bundle.schema.yaml` | top-level public-output guard predicate under root `allOf` | top-level public-output guard predicate | Replace single-value `const: public_llm_wiki` predicate with `enum: [public_llm_wiki, public_federal_wiki]`; leave audience/legal/source/claim gate requirements unchanged. |
| `docs/architecture/report-evidence-bundle.schema.yaml` | public-output guard then-branch `source_class_mix.items` constraint | guarded public residency/corpus mix constraint | Replace single-value `const: public_llm_wiki` constraint with `enum: [public_llm_wiki, public_federal_wiki]`; do not admit private/internal residencies. |
| `docs/architecture/report-evidence-bundle.schema.yaml` | public-output guard then-branch `sources.items.properties.input_residency` constraint | guarded public source input constraint | Leave as `const: public_llm_wiki`; Phase A does not admit `public_federal_wiki` as source/input residency. |
| `docs/architecture/report-evidence-bundle.schema.yaml` | public-output guard then-branch `sources.items.properties.output_residency` constraint | guarded public source output constraint | Replace single-value `const: public_llm_wiki` constraint with `enum: [public_llm_wiki, public_federal_wiki]`; do not admit private/internal residencies. |
| `docs/architecture/report-evidence-bundle.schema.yaml` | `registry_backing.public_llm_wiki` | registry backing description | Leave existing key unchanged and add sibling `registry_backing.public_federal_wiki`. |

Regression tests must parse YAML and assert the structural paths above, not grep raw text. The post-edit structural test must prove no `public_llm_wiki` enum value was removed, `public_federal_wiki` is absent from input/source residency paths, and public-output guard predicates include both `public_llm_wiki` and `public_federal_wiki`. A raw text count may be logged as diagnostic output only.

Phase A will not implement the manual validator, generated bundle fixture validation, legal attestation rehashing, wrapper gates, public projection checks, hook/CI wiring, or helper modules beyond the Phase A config-to-standard synchronization check. The sync script is limited to rendering/checking the standard block from config plus config-internal consistency needed for that render. Generated bundle validation, public-egress validation, ledger projection validation, and legal/source wrapper validation belong to [workspace-hub#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013) and Phase C follow-up work.

No Phase A consumer will publish directly to `worldenergydata-wiki`; Phase A only defines the route, adds schema vocabulary, and pins public-residency guard semantics in the existing JSON Schema validators. Executable routing, generated-bundle validation, and public-egress enforcement remain blocked into [workspace-hub#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013). The standard and governance decision must include a consumer-blocking note: `output_residency: public_federal_wiki` is not publication authorization until [workspace-hub#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013) lands.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/ECOSYSTEM_WIKI_FLYWHEEL_CONTRACT.md` | Normative contract surface for enum/config/template/schema consumers |
| Create | `docs/governance/2026-06-09-ecosystem-wiki-flywheel-routing-decision.md` | Decision rationale for public/private wiki flywheel routing |
| Create | `config/ecosystem-wiki-flywheel/source-classification.yaml` | Source of truth for enums, public-safe flags, public identity registry, staged order, and freshness thresholds |
| Create | `scripts/knowledge/sync-ecosystem-wiki-flywheel-standard.py` | Render/check the standard fenced YAML block from config |
| Create | `templates/ecosystem-wiki-flywheel/run-manifest.example.yml` | Canonical run manifest example consumed by Phase B |
| Create | `templates/ecosystem-wiki-flywheel/run-history-record.example.jsonl` | Canonical run history record example consumed by Phase B |
| Create | `templates/ecosystem-wiki-flywheel/wiki-frontmatter.example.yml` | Canonical wiki frontmatter example consumed by Phase B |
| Create | `templates/ecosystem-wiki-flywheel/routing-ledger-event.example.yml` | Canonical private/full ledger event example consumed by Phase B |
| Create | `templates/ecosystem-wiki-flywheel/routing-ledger-public-projection.example.yml` | Canonical public projection example consumed by Phase B |
| Create | `templates/ecosystem-wiki-flywheel/quick-reference-index-entry.example.yml` | Canonical quick-reference index entry example consumed by Phase B |
| Create | `templates/ecosystem-wiki-flywheel/insight-bundle-metadata.example.yml` | Canonical insight bundle metadata example consumed by Phase B |
| Modify | `.gitattributes` | Add only `*.jsonl text eol=lf`; existing yml/yaml/json LF rules remain unchanged |
| Modify | `docs/architecture/execution-manifest.schema.yaml` | Add `public_federal_wiki` output residency |
| Modify | `docs/architecture/report-evidence-bundle.schema.yaml` | Add `public_federal_wiki` output residency without weakening existing gates |
| Modify | `tests/architecture/test_report_layer_contract.py` | Regression proof for the additive schema enum |
| Modify | `tests/architecture/test_execution_layer_contract.py` | Regression proof for the additive execution schema enum |
| Create | `tests/governance/test_ecosystem_wiki_flywheel_phase_a.py` | TDD checks for config, standard sync, templates, and .gitattributes scope |
| Create | `docs/standards/README.md` | Create a complete standards index covering all current `docs/standards/*.md` files plus the new contract |
| Modify | `docs/plans/README.md` | Point #2975 at this Phase A plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_config_defines_required_enum_groups` | config carries source/license/publication/review/ledger/scheduler enums | source-classification config | pass |
| `test_config_defines_exact_enum_values` | config uses the exact Phase A contract values listed in this plan | source-classification config | pass |
| `test_public_safe_flags_match_config_declared_policy_lists` | public-safe flags match config-declared public-safe source/license lists and the sync script has no separate allowlist constant | config with bad flag fixture | fail |
| `test_public_identity_registry_is_bsee_mvp_scoped` | BSEE datasets are enabled; NOAA/USGS/MMS are present but empty/blocked until populated | config | pass |
| `test_publication_sequence_is_machine_readable` | staged order has required keys and strictly increasing order | config | pass |
| `test_publication_sequence_stage_schema_is_defined` | every stage record has `stage_id`, `order`, `source_publication_class`, `target_output_residency`, `required_gates`, and conditional `target_wiki`; order values are positive and unique | config | pass |
| `test_config_defines_exact_freshness_defaults` | freshness defaults match the Phase A contract values and are positive integer day counts | source-classification config | pass |
| `test_standard_yaml_block_matches_config` | standard fenced YAML block is generated from config | standard + config | pass |
| `test_sync_script_check_fails_on_drift` | check mode detects hand-edited standard/config drift | modified temp standard block | fail |
| `test_sync_script_write_then_check_roundtrip` | write mode renders the generated block and immediate check mode passes | temp standard + config | pass |
| `test_template_family_has_required_example_names` | exact seven required template filenames exist and use `.example` naming | templates dir | pass |
| `test_template_family_examples_are_parseable` | six YAML examples parse as mappings and the JSONL run-history example parses as one JSON object line | templates dir | pass |
| `test_jsonl_gitattributes_scope_is_narrow` | only `*.jsonl text eol=lf` is newly required; existing yml/yaml/json LF rules are recognized as pre-existing | `.gitattributes` | pass |
| `test_public_federal_wiki_in_execution_manifest_schema` | execution schema accepts new residency | schema fixture | pass |
| `test_public_federal_wiki_in_report_evidence_schema` | report evidence schema accepts new residency without weakening public gates | schema fixture | pass |
| `test_public_federal_wiki_is_public_guarded_residency` | execution/report schema validators reject `public_federal_wiki` with incomplete gates or private-source inputs exactly as they reject `public_llm_wiki` | schema negative fixtures | fail |
| `test_public_federal_wiki_accepts_fully_gated_public_paths` | fully gated `public_federal_wiki` execution/report fixtures validate successfully | schema positive fixtures | pass |
| `test_schema_public_llm_wiki_pre_edit_structural_contract` | parsed pre-edit schemas match the structural paths in the disposition table before implementation edits begin | parsed schema YAML before edit | pass |
| `test_public_federal_wiki_schema_structural_disposition_is_complete` | parsed post-edit schemas keep every existing `public_llm_wiki` enum value, add `public_federal_wiki` only to output/public paths, keep it absent from input/source residency paths, and broaden public-output guard predicates structurally | parsed schema YAML | pass |
| `test_report_layer_contract_regression_suite_passes` | existing report-layer contract remains green | `tests/architecture/test_report_layer_contract.py` | pass |
| `test_execution_layer_contract_regression_suite_passes` | existing execution-layer contract remains green | `tests/architecture/test_execution_layer_contract.py` | pass |
| `test_standards_readme_indexes_existing_standards_and_contract` | standards index links every current `docs/standards/*.md` file except `docs/standards/README.md` itself, plus the new contract | standards README + standards directory | pass |
| `test_public_federal_wiki_consumer_blocking_note_present` | standard and governance decision both state that `public_federal_wiki` vocabulary is not publication authorization until [workspace-hub#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013) lands | standard + governance decision | pass |
| `test_phase_b_issue_linked` | standard or governance decision links [workspace-hub#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013) as validator follow-up | docs | pass |

---

## Acceptance Criteria

- [ ] Phase A leaves [workspace-hub#2975](https://github.com/vamseeachanta/workspace-hub/issues/2975) as a standard/config/template/schema plan only; no manual validator or helper modules are implemented here.
- [ ] `source-classification.yaml` defines all required enum groups, fixed public-safe source/license subsets, BSEE-scoped public identity registry, staged publishing order, and exact freshness threshold defaults: `source_retrieval: 180`, `license_terms_review: 365`, and `quick_reference_pointer: 30` days.
- [ ] `source-classification.yaml` single-sources public-safe policy lists and per-value public-safe flags; the sync script validates internal config consistency and carries no independent public-safe source/license allowlist.
- [ ] `publication_sequence` stages use the defined record schema: `stage_id`, positive integer `order`, `source_publication_class`, `target_output_residency`, `required_gates`, and conditional `target_wiki`; stage `order` values are unique and strictly increasing.
- [ ] The standard includes one generated fenced `yaml` block rooted at `ecosystem_wiki_flywheel_enums`; `scripts/knowledge/sync-ecosystem-wiki-flywheel-standard.py --check` fails on drift.
- [ ] `scripts/knowledge/sync-ecosystem-wiki-flywheel-standard.py --write` followed by `--check` passes against the same config and standard.
- [ ] `public_federal_wiki` is added additively to execution and report evidence schemas without removing existing enum values or weakening public-output fail-closed rules.
- [ ] `public_federal_wiki` is explicitly treated as a public-output guarded residency wherever Phase A schema/contract tests already guard `public_llm_wiki`; negative fixtures prove incomplete public gates and private-source inputs fail validation.
- [ ] Fully gated `public_federal_wiki` execution/report fixtures validate successfully, proving the guard is usable and not reject-all.
- [ ] The schema edit follows the structural disposition table in this plan; tests parse YAML and fail if pre-edit schema paths drift before implementation, if `public_federal_wiki` appears as an input/source residency, or if a public-output condition predicate remains single-value `const: public_llm_wiki`.
- [ ] Existing execution/report architecture regression suites cover the additive schema enum: `uv run pytest tests/architecture/test_execution_layer_contract.py tests/architecture/test_report_layer_contract.py -v`.
- [ ] Phase A templates exist for run manifest, run history record, wiki frontmatter, routing ledger event, public ledger projection, quick-reference index entry, and insight bundle metadata.
- [ ] Phase A template examples are structurally parseable before Phase B consumes them: YAML templates parse as mappings and `run-history-record.example.jsonl` parses as exactly one JSON object line.
- [ ] `docs/standards/README.md` indexes every current `docs/standards/*.md` file except `docs/standards/README.md` itself, plus `docs/standards/ECOSYSTEM_WIKI_FLYWHEEL_CONTRACT.md`, so the new index is not a misleading single-entry index.
- [ ] The standard and governance decision include the exact consumer-blocking warning that `output_residency: public_federal_wiki` is not publication authorization until [workspace-hub#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013) lands.
- [ ] `.gitattributes` adds only the `.jsonl` LF rule needed by run-history examples; no broad renormalization is introduced.
- [ ] [workspace-hub#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013) is linked as the blocked Phase B validator issue.
- [ ] Tests pass: `uv run pytest tests/governance/test_ecosystem_wiki_flywheel_phase_a.py -v`.
- [ ] Existing schema regressions pass: `uv run pytest tests/architecture/test_execution_layer_contract.py tests/architecture/test_report_layer_contract.py -v`.
- [ ] Completeness gate before closeout follows [#2798](https://github.com/vamseeachanta/workspace-hub/issues/2798): the closeout uses the auto-derived completeness class and server-side threshold, not a plan-selected class. Because Phase A creates a Python sync script and test module, implementation should expect `code` class and threshold 90 unless the live local check derives otherwise. The computed record includes `issue_number: 2975`, is stamped in the issue body as a ```completeness {json}``` block, is rendered to `docs/reports/<date>-2975-completeness.html` with `scripts/workflow/render_completeness_html.py`, is verified locally with `scripts/enforcement/check-completeness-before-close.sh 2975`, and the owner-only `status:completeness-verified` label is applied by an authorized owner before close. If the auto-derived class is `code`, the required threshold is 90; if it is `evidence`, the required threshold is 80.
- [ ] Legal/security scan passes: `scripts/legal/legal-sanity-scan.sh`.

---

## Adversarial Review Summary

The prior omnibus plan used its own r1-r8 review history and remains only historical blocked evidence; those reviews do not approve this narrowed Phase A plan. Phase A has an independent review sequence: r1 returned Claude MAJOR, Codex MINOR, Gemini NO_OUTPUT; r2 returned Claude MAJOR, Codex MINOR, Gemini NO_OUTPUT; r3 returned Claude MAJOR, Codex MINOR, Gemini NO_OUTPUT; r4 returned Claude MAJOR, Codex APPROVE, Gemini NO_OUTPUT; r5 returned Claude MAJOR, Codex APPROVE, Gemini NO_OUTPUT; r6 returned Claude MAJOR, Codex MAJOR, Gemini NO_OUTPUT; r7 returned Claude MAJOR, Codex MAJOR, Gemini NO_OUTPUT; r8 returned Claude MAJOR, Codex MAJOR, Gemini NO_OUTPUT.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude r1 | MAJOR | execution-schema regression coverage, governance filename date, explicit template list, manual drift window, single public-safe authority |
| Codex r1 | MINOR | exact enum values, standards README indexing, `.gitattributes` evidence |
| Gemini r1 | NO_OUTPUT | provider unavailable |
| Claude r2 | MAJOR | freshness defaults lacked contract/test, `public_federal_wiki` public-guard behavior was under-tested, final attestation needed, standards README create path needed reconciliation |
| Codex r2 | MINOR | header/review artifact authority needed fresh final-round clarity |
| Gemini r2 | NO_OUTPUT | provider unavailable |
| Claude r3 | MAJOR | complete standards index required; `public_federal_wiki` guard landing point needed explicit JSON Schema semantics |
| Codex r3 | MINOR | `.jsonl` attestation gap, completeness closeout details, sync script/helper wording |
| Gemini r3 | NO_OUTPUT | provider unavailable |
| Claude r4 | MAJOR | completeness class must be auto-derived, public-safe policy must be config-single-sourced, schema conditional mechanics needed exact edit shape, templates needed parseability checks |
| Codex r4 | APPROVE | final evidence should include `.gitattributes` proof |
| Gemini r4 | NO_OUTPUT | provider unavailable |
| Claude r5 | MAJOR | schema occurrence disposition needed exhaustive per-occurrence table; positive fully gated public-federal acceptance needed |
| Codex r5 | APPROVE | final evidence should include `.gitattributes` proof |
| Gemini r5 | NO_OUTPUT | provider unavailable |
| Claude r6 | MAJOR | `public_federal_wiki` input residency was fail-open; publication sequence schema under-specified |
| Codex r6 | MAJOR | `public_federal_wiki` input residency was internally inconsistent; pre-edit occurrence gate needed TDD enforcement; sync script scope needed sharper wording |
| Gemini r6 | NO_OUTPUT | provider unavailable |
| Claude r7 | MAJOR | schema guard verification needed parsed structural paths, `source_class_mix` type needed clarification, README self-index exclusion needed specification |
| Codex r7 | MAJOR | plan-review evidence must expect JSONL template missing before implementation; consumer-blocking note needed explicit test/checklist |
| Gemini r7 | NO_OUTPUT | provider unavailable |
| Claude r8 | MAJOR | sustained review-loop risk; schema-valid `public_federal_wiki` before #3013 enforcement needs stronger machine-readable control; pre-edit structural check should be a preflight artifact |
| Codex r8 | MAJOR | pre-edit structural check should not be a persistent TDD test; closeout completeness evidence and standards-count wording need cleanup |
| Gemini r8 | NO_OUTPUT | provider unavailable |

Gemini has returned `NO_OUTPUT` across Phase A r1-r8; this is treated as provider `UNAVAILABLE` degradation, not a skipped gate. T2 coverage remains Claude + Codex. If the owner requires a third-provider signal despite Gemini unavailability, this plan should remain draft until another provider can review it.

**Overall result:** FAIL through r8. Stop auto-cycling; owner decision is required before another plan-review wave.

### Decision Gate

The active unresolved design decision is whether Phase A may add schema-valid `public_federal_wiki` vocabulary before [workspace-hub#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013) lands executable public-egress enforcement.

Recommended decision: split Phase A again so the next approval unit lands non-routing surfaces first: standard, governance decision, config, templates, standards index, sync script, and tests, but defers `public_federal_wiki` schema enum/guard changes to the Phase B enforcement issue or a new Phase A2 issue with machine-readable `authorization_pending` semantics. This avoids schema-valid outputs being misread as publication-authorized.

Alternate decision: keep schema changes in Phase A, but require a machine-readable pending-authorization marker in the schema/config/standard, with tests proving any `public_federal_wiki` output is marked `authorization_pending: workspace-hub#3013` and cannot be interpreted as publish-authorized.

---

## Risks and Open Questions

- **Risk:** Phase A could accidentally re-expand into validator work. Mitigation: manual validator, helper modules, generated bundle fixture validation, legal attestation rehashing, and projection enforcement are explicitly blocked into [workspace-hub#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013).
- **Risk:** `public_federal_wiki` schema changes could regress existing report-layer behavior. Mitigation: update and run `tests/architecture/test_report_layer_contract.py` with negative public-guard fixtures, not only enum acceptance.
- **Risk:** Phase A creates `public_federal_wiki` vocabulary before Phase B routing enforcement. Mitigation: no Phase A consumer publishes to `worldenergydata-wiki`; the standard/governance decision carries a consumer-blocking note; JSON Schema guards reject public-federal outputs that lack the same public gate posture as `public_llm_wiki`.
- **Risk:** `public_federal_wiki` could be misused as a source/input residency. Mitigation: Phase A explicitly leaves execution/report input-residency positions unchanged and tests that `public_federal_wiki` does not appear as input/source residency.
- **Risk:** Schema guard verification could be brittle if based on line numbers or raw grep counts. Mitigation: structural tests parse YAML and assert named schema paths; text counts are diagnostic only.
- **Risk:** Plan-review evidence could accidentally expect Phase A deliverables to exist before implementation. Mitigation: plan-review evidence records those artifacts as expected missing; post-implementation evidence records them as existing.
- **Risk:** Standard/config drift could return if the standard block is hand-edited. Mitigation: require the sync/check script in verification.
- **Risk:** Closeout completeness class could be mis-selected by the plan. Mitigation: do not select the class in this plan; use the auto-derived server-side class and threshold, then run the local advisory closeout check before attempting close.
- **Open:** None for Phase A. Phase B validator details are tracked in [workspace-hub#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013).

---

## Complexity: T2

T2 because Phase A touches multiple documentation/config/schema/test surfaces, but no runtime validator or cross-repo implementation.
