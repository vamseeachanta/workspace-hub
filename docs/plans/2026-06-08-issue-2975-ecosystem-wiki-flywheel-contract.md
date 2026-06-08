# Plan for #2975: Ecosystem Wiki Flywheel Manifest, Provenance, and Routing Contract

> **Status:** draft-needs-revision
> **Complexity:** T3
> **Date:** 2026-06-08
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2975
> **Client:** N/A
> **Project:** N/A
> **Review artifacts:** scripts/review/results/2026-06-08-plan-2975-claude.md | scripts/review/results/2026-06-08-plan-2975-codex.md | scripts/review/results/2026-06-08-plan-2975-gemini.md

---

## Resource Intelligence Summary

This issue will create a reusable workspace-hub contract for the repo-ecosystem flywheel:

```text
source repo outputs -> run manifest/history -> generated insight/report -> canonical wiki page -> llm-wiki quick-reference index -> routing/promotion ledger -> future agent retrieval
```

The work will compose existing architecture, wiki routing, citation, and publication-gate contracts instead of replacing them.

### Existing repo code

- Found: `scripts/enforcement/check-wiki-sibling-frontmatter.py` — validates wiki frontmatter visibility/client/project fields for `llm-wiki` and `llm-wiki-<client>` repos.
- Found: `tests/enforcement/test_check_wiki_sibling_frontmatter.py` — provides the hermetic fixture pattern for wiki-shaped validation tests.
- Found: `scripts/enforcement/check-client-wiki-registry.sh` — validates `config/client-wikis.yml` shape and registry hygiene.
- Found: `scripts/knowledge/registry-freshness-check.py` — provides a JSON-reporting pattern for stale/dead URL checks.
- Found: `scripts/legal/legal-sanity-scan.sh` and `.legal-deny-list.yaml` — provide the legal/security scan gate that public publishing will reference.
- Found: `docs/architecture/execution-manifest.schema.yaml` — already defines execution manifest fields including `source_ids`, `input_residency`, `output_residency`, `legal_scan_evidence`, `review_artifact_paths`, `promotion_gates`, and `report_eligible`.
- Found: `docs/architecture/report-evidence-bundle.schema.yaml` — already defines report/evidence bundle fields including `run_id`, `source_class`, `output_residency`, legal scan, public/client gates, and fail-closed public-output rules.
- Gap: no unified flywheel validator composes execution manifests, report evidence bundles, run history, wiki frontmatter, quick-reference index entries, and routing ledgers into one end-to-end generated insight bundle check.
- Gap: no machine-readable config-tier `source_publication_class` enum or license/terms-classification enum exists for repo-ecosystem wiki publishing beyond the narrower existing report evidence `source_class` and `output_residency` fields.
- Gap: no validator currently checks citation sidecars, cross-sibling link direction, stale wiki pointers, duplicate ledger entries, or public-federal-data frontmatter beyond the existing basic visibility field.

### Standards

| Standard | Status | Source |
|---|---|---|
| Wiki sibling routing | active | `.claude/rules/wiki-sibling-routing.md` |
| Public federal/vendor data routing | active | `.claude/rules/codes-standards-data-routing.md` |
| Calc citation sidecar contract | active | `.claude/rules/calc-citation-contract.md`, `docs/standards/calc-output-citation.md` |
| Data/execution/report/curated-learning boundary | active | `docs/architecture/data-execution-report-layer-contract.md` |
| Report-derived learning routing | active | `docs/architecture/report-derived-learning-routing.md` |
| Execution manifest schema | active — extend/compose, do not fork | `docs/architecture/execution-manifest.schema.yaml` |
| Report evidence bundle schema | active — extend/compose, do not fork | `docs/architecture/report-evidence-bundle.schema.yaml` |

### LLM Wiki pages consulted

- No wiki content will be modified by this issue. The plan will set `Client: N/A` and will only define workspace-hub standards, templates, and validators.
- Wiki routing rules will be consulted through `.claude/rules/wiki-sibling-routing.md`; any future sibling-wiki implementation will still need its own issue/plan/approval gate.

### Documents consulted

- `docs/architecture/data-execution-report-layer-contract.md` — defines A-DATA, A-EXEC, A-REPORT, and A-CURATED-LEARNING boundaries plus promotion gates.
- `docs/architecture/report-derived-learning-routing.md` — defines `output_residency` values and forbids private/client raw data from routing directly to public llm-wiki.
- `docs/architecture/llm-wiki-data-promotion-gates.md` — defines staged promotion gates from raw/private staging to public or client/private publication.
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — defines L1 source docs, L2 registry/provenance, L3 durable knowledge, L5 execution state, and L6 transient session boundaries.
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` — provides the strongest existing identity/provenance model and reuse-vs-reparse pattern.
- `.claude/rules/wiki-sibling-routing.md` — governs sibling wiki visibility, client/project metadata, citation sidecar sibling identity, and cross-sibling linking.
- `.claude/rules/codes-standards-data-routing.md` — governs vendor/licensed standards routing and public-domain federal-data routing to `worldenergydata-wiki`.
- `docs/governance/2026-05-20-public-data-corpus-routing-decision.md` — records prior public sibling wiki decision for public-domain federal data.
- `docs/governance/2026-05-20-client-llm-wiki-feature-and-acma-instance-design.md` — defines private client wiki factory, `config/client-wikis.yml`, privacy firewall, and promotion ledger concept.
- `templates/client-llm-wiki/` — provides existing private client wiki templates, including `DATA-CYCLE.md`, `REDACTION-POSTURE.md`, and a promotion-ledger example.
- `data/document-index/registry.yaml` — provides aggregate corpus counts and repo/domain source-discovery context for data-pipeline planning.
- `data/document-index/resource-intelligence-maturity.yaml` — records resource-intelligence maturity metrics and confirms YAML is the source of truth for that registry surface.
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — defines `AGENTS.md` as the universal repository entry point and provider adapters as non-contradictory adapters.
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` — defines promotion rules for transient artifacts graduating to durable knowledge.
- `docs/document-intelligence/intelligence-accessibility-map.md` — identifies L3 durable wiki knowledge, L2 registries, and accessibility gaps for promotion/retrieval surfaces.
- `docs/governance/2026-04-25-cradle-to-grave-engineering-flywheel-design.md` — provides the strategic public-by-default flywheel pattern.
- `docs/plans/2026-06-02-issue-2945-repo-ecosystem-flywheel.md` — provides a related repo-ecosystem flywheel plan that #2975 will not duplicate.
- [workspace-hub#2975](https://github.com/vamseeachanta/workspace-hub/issues/2975) — defines the governing standard request and links the worldenergydata trigger issues.
- [worldenergydata#450](https://github.com/vamseeachanta/worldenergydata/issues/450), [worldenergydata#451](https://github.com/vamseeachanta/worldenergydata/issues/451), [worldenergydata#452](https://github.com/vamseeachanta/worldenergydata/issues/452), and [worldenergydata#453](https://github.com/vamseeachanta/worldenergydata/issues/453) — carry the tightened decisions from the failed adversarial review of the initial worldenergydata flywheel decision set.
- `worldenergydata#450` tightened decision — preserve YAML per-run manifest plus append-only JSONL history, with `run_id`, `attempt_id`, `schema_version`, `code_ref`, `catalog_ref`, dataset versions, source URLs, retrieval timestamps, content hashes, output hashes, and rerun/supersession lineage.
- `worldenergydata#451` tightened decision — stage BSEE first, FDAS second only after FDAS source classification and citation coverage are proven, and keep uncertain/mixed sources private or blocked.
- `worldenergydata#452` tightened decision — make the first public workflow an all-public-BSEE available-data summary; defer HSE/marine until segregation, redaction, and legal/security checks are proven.
- `worldenergydata#453` tightened decision — route public federal outputs to `worldenergydata-wiki`, keep `llm-wiki` as a quick-reference hub, separate public/private/full ledgers, and start scheduled publishing only after two clean manual runs.

### Gaps identified

- No single workspace-hub standard will bind run manifests, append-only run history, wiki publication metadata, quick-reference indexes, and routing ledgers.
- No template family will give source repos a reusable manifest/history/frontmatter/ledger/index shape.
- No `source_publication_class` schema will distinguish public federal, public commercial, open academic, vendor/licensed, client/private, user-provided, locally cached uncertain, mixed, and blocked sources.
- No license/terms-classification schema will fail closed for missing or ambiguous reuse rights.
- Existing `execution-manifest.schema.yaml` and `report-evidence-bundle.schema.yaml` will need to be composed by reference; #2975 will not create conflicting replacement vocabularies for `input_residency`, `output_residency`, or `promotion_gates`.
- No validator will currently prove provenance completeness, citation coverage, public/private contamination, duplicate logical runs, duplicate ledger events, broken wiki links, stale quick-reference pointers, or legal/security scan applicability for a generated insight bundle.
- No generated `llm-wiki` quick-reference entry contract will prevent `llm-wiki` from becoming a duplicate raw-content store.

### Required enum contract

The implementation will make `config/ecosystem-wiki-flywheel/source-classification.yaml` the validator source of truth, following the existing validator precedent that production enforcement reads config/registry files rather than `tests/fixtures/`. Unknown or alias-only values will fail closed unless explicitly mapped in that config file.

| Enum | Required values |
|---|---|
| `source_publication_class` | `public-federal-data`, `public-commercial-open`, `open-academic`, `vendor-licensed`, `client-private`, `user-provided-private`, `locally-cached-uncertain`, `mixed`, `blocked` |
| `license_terms_class` | `public-domain`, `open-license`, `public-terms-review-required`, `vendor-license`, `client-confidential`, `unknown`, `blocked` |
| `publication_state` | `public_publishable`, `private_publishable`, `blocked`, `superseded`, `deprecated` |
| `review_state` | `unreviewed`, `review-required`, `approved`, `approved-with-notes`, `rejected` |
| `ledger_event_type` | `created`, `linked`, `promoted`, `moved`, `blocked`, `deprecated`, `redacted`, `superseded` |
| `scheduler_state` | `manual-only`, `eligible-after-two-clean-runs`, `scheduled-enabled`, `scheduled-blocked` |

Public ledger projections will be allowlist-only. They may include only public-safe event identity, public source class, public destination URL/path, citation coverage status, freshness timestamps, and review state. They must not include `client`, `project`, private repository URLs, private issue URLs, local absolute paths, raw source snippets, citation sidecar paths, log paths, private artifact paths, or private source titles.

`source_publication_class` will be an additive flywheel/publication-safety field. It will not replace or overload `report-evidence-bundle.schema.yaml` `sources[].source_class`, which remains a source-reference-kind field with values such as `source-doc-key`, `promotion-ledger-entry`, `private-wiki-page`, `execution-manifest`, and `internal-note`. Enhanced legal scan attestation will also live in a flywheel wrapper field, not inside existing `legal_scan_evidence` or `legal_scan` objects, because those existing schemas use `additionalProperties: false`.

Public publication will require both a public-safe publication class and a public-safe license/terms class. The public-safe publication classes will be `public-federal-data`, `public-commercial-open`, and `open-academic`. The public-safe license/terms classes will be `public-domain` and `open-license`; `public-terms-review-required` will block public publication until review changes it to a public-safe class. Existing `legal_scan_evidence` / `legal_scan` fields will still be populated with their closed-schema `command` and `result` fields; the enhanced `legal_scan_attestation` wrapper will bind those closed-schema fields to command hash, deny-list hash, scanned artifact hashes, timestamp, and exit code.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-08T15:56:04Z via `gh issue view` and subagent issue scan):
- [workspace-hub#2975](https://github.com/vamseeachanta/workspace-hub/issues/2975) — OPEN — `standard: ecosystem wiki flywheel manifest, provenance, and routing contract`
- [worldenergydata#450](https://github.com/vamseeachanta/worldenergydata/issues/450) — OPEN — `feat(flywheel): define catalog-to-workflow manifest for well-operations insight runs`
- [worldenergydata#451](https://github.com/vamseeachanta/worldenergydata/issues/451) — OPEN — `feat(flywheel): integrate BSEE and FDAS source readiness for well-operations runs`
- [worldenergydata#452](https://github.com/vamseeachanta/worldenergydata/issues/452) — OPEN — `feat(flywheel): run well-operations insight workflow from WAR, production, FDAS, and HSE inputs`
- [worldenergydata#453](https://github.com/vamseeachanta/worldenergydata/issues/453) — OPEN — `feat(flywheel): publish well-operations insight outputs to wiki with provenance and routing gates`

**File existence** (`ls` and bounded reads, 2026-06-08T15:56:04Z):
- EXISTS: `docs/architecture/data-execution-report-layer-contract.md`
- EXISTS: `docs/architecture/report-derived-learning-routing.md`
- EXISTS: `docs/architecture/llm-wiki-data-promotion-gates.md`
- EXISTS: `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- EXISTS: `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- EXISTS: `.claude/rules/wiki-sibling-routing.md`
- EXISTS: `.claude/rules/codes-standards-data-routing.md`
- EXISTS: `scripts/enforcement/check-wiki-sibling-frontmatter.py`
- EXISTS: `tests/enforcement/test_check_wiki_sibling_frontmatter.py`
- EXISTS: `docs/architecture/execution-manifest.schema.yaml`
- EXISTS: `docs/architecture/report-evidence-bundle.schema.yaml`
- EXISTS: `data/document-index/registry.yaml`
- EXISTS: `data/document-index/resource-intelligence-maturity.yaml`
- EXISTS: `docs/standards/CONTROL_PLANE_CONTRACT.md`
- EXISTS: `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- EXISTS: `docs/document-intelligence/intelligence-accessibility-map.md`
- EXISTS: `templates/client-llm-wiki/README.md`
- MISSING (new — this plan will create): `docs/standards/ECOSYSTEM_WIKI_FLYWHEEL_CONTRACT.md`
- MISSING (new — this plan will create): `docs/governance/2026-06-08-ecosystem-wiki-flywheel-routing-decision.md`
- MISSING (new — this plan will create): `templates/ecosystem-wiki-flywheel/`
- MISSING (new — this plan will create): `scripts/enforcement/check-ecosystem-wiki-flywheel.py`
- MISSING (new — this plan will create): `tests/enforcement/test_check_ecosystem_wiki_flywheel.py`

**Line excerpts**:

`docs/architecture/data-execution-report-layer-contract.md` defines the parent lifecycle and transition gates:

```text
inputs -> execution -> reports/chatbots -> curated output learnings -> corpus tier
```

```text
Any private/restricted source -> public llm-wiki/public chatbot/public report | explicit legal and sanitization gate; fail closed by default
```

`docs/architecture/report-derived-learning-routing.md` states:

```text
Report-derived learning must carry source-class and citation separation. Private/client raw or readable data cannot route directly into public llm-wiki.
```

`.claude/rules/wiki-sibling-routing.md` defines the sibling-wiki visibility set:

```text
visibility: value ... {private-llm-wiki, private-client-llm-wiki, public-federal-data}
```

`scripts/enforcement/check-wiki-sibling-frontmatter.py` confirms current enforcement scope is frontmatter-only for wiki repos:

```text
Validates YAML frontmatter on staged (pre-commit) or committed (CI) wiki content
inside `llm-wiki` (generic) and `llm-wiki-<client>` (per-client) sibling repos.
```

`docs/architecture/execution-manifest.schema.yaml` already defines the execution layer fields this issue must compose:

```text
required: manifest_id, issue, source_ids, source_registry_kind, source_registry_ref,
input_residency, output_residency, legal_scan_evidence, review_artifact_paths,
promotion_gates, report_eligible
```

`docs/architecture/report-evidence-bundle.schema.yaml` already defines public-output fail-closed rules:

```text
output_residency: public_llm_wiki -> audience_classification: public-safe
legal_scan.result: pass
```

**Gap proofs**:
- `rg -n "source_class|license_terms_class|publication_state|routing-ledger|run_id|attempt_id" docs scripts tests templates` finds related concepts but no unified manifest/history/ledger validator.
- `find templates -maxdepth 2 -type d -name '*flywheel*'` returns no existing `templates/ecosystem-wiki-flywheel/` directory.
- `find scripts -path '*ecosystem*wiki*flywheel*' -o -path '*wiki*manifest*'` returns no existing validator for this contract.
- `rg -n "source_class|license_terms_class|publication_state" config tests/fixtures docs/architecture scripts/enforcement` shows existing partial schema vocabulary, including `report-evidence-bundle.schema.yaml` `source_class`; no shared config-tier enum file exists for the required flywheel `source_publication_class`, license, and publication states in this plan.

**Reproduction proofs**:

N/A — this is a documentation/governance/enforcement-contract issue, not a runtime failure report. Implementation will still use TDD for validators and generated-template checks.

Source count: 15 distinct issue/file/template sources.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-08-issue-2975-ecosystem-wiki-flywheel-contract.md` |
| Plan index | `docs/plans/README.md` |
| Standard | `docs/standards/ECOSYSTEM_WIKI_FLYWHEEL_CONTRACT.md` |
| Governance decision | `docs/governance/2026-06-08-ecosystem-wiki-flywheel-routing-decision.md` |
| Templates | `templates/ecosystem-wiki-flywheel/` |
| Source-classification config | `config/ecosystem-wiki-flywheel/source-classification.yaml` |
| Valid example fixture | `tests/fixtures/ecosystem_wiki_flywheel/valid-public-bsee/` |
| Invalid mixed-provenance fixture | `tests/fixtures/ecosystem_wiki_flywheel/invalid-mixed-provenance/` |
| Invalid ledger-leak fixture | `tests/fixtures/ecosystem_wiki_flywheel/invalid-ledger-leak/` |
| Validator | `scripts/enforcement/check-ecosystem-wiki-flywheel.py` |
| Validator tests | `tests/enforcement/test_check_ecosystem_wiki_flywheel.py` |
| Hook/CI rollout follow-up | separate follow-up issue; #2975 will land a manual validator plus tests only |
| Plan review — Claude | `scripts/review/results/2026-06-08-plan-2975-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-06-08-plan-2975-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-06-08-plan-2975-gemini.md` |

---

## Deliverable

A workspace-hub standard, governance decision, template family, and focused validator/test suite will define how repo outputs become durable wiki-backed insight flywheels without leaking private/vendor/client data or bypassing issue/plan/review gates.

---

## Pseudocode

```text
function validate_manifest_bundle(bundle_path):
    load generated bundle files: run_manifest.yml, run_history.jsonl,
        insight_bundle_metadata.yml, routing_ledger.yml,
        routing_ledger_public_projection.yml
    load example templates only in --validate-template mode:
        templates/ecosystem-wiki-flywheel/*.example.*
    validate schema_version is supported
    validate run_id, attempt_id, code_ref, catalog_ref, input hashes, output hashes
    validate every source has source_publication_class, license_terms_class, citation, retrieval timestamp, content hash
    validate source_publication_class and license_terms_class against source-classification.yaml
    validate report evidence source_class remains the existing source-reference-kind field
    validate unknown enum values fail closed
    validate execution-manifest.schema.yaml and report-evidence-bundle.schema.yaml compatibility
    validate public outputs contain only public-safe source_publication_class values
    validate public outputs contain only public-safe license_terms_class values
    validate report-evidence source_class=private-wiki-page is blocked for public output
        unless the flywheel wrapper binds it to a public-safe source_publication_class,
        public-safe license_terms_class, public release clearance, and sanitized projection
    validate ambiguous, mixed, vendor, client, or locally uncertain sources fail closed
    validate every wiki target has required frontmatter fields for its destination sibling
    validate llm-wiki quick-reference entries are index pointers with classification/freshness metadata
    validate public ledger projection uses allowlist-only schema
    validate private/full ledger and public sanitized projection are distinct when private artifacts exist
    validate duplicate logical runs are rejected, superseded, or recorded as attempts
    validate no duplicate ledger event identity exists
    validate flywheel legal_scan_attestation command, deny-list hash, artifact hashes, timestamp, and exit code match current bundle when publication_state is public_publishable
    validate scheduler_state requires two clean manual run records before scheduled-enabled
    emit deterministic JSON result with errors and warnings
```

```text
function classify_publication_state(sources, outputs, review_state):
    public_safe_source_classes = {public-federal-data, public-commercial-open, open-academic}
    public_safe_license_terms = {public-domain, open-license}
    if any source lacks source_publication_class, citation, license/terms class, or hash:
        return blocked
    if any source has source_publication_class not in public_safe_source_classes:
        return private_publishable or blocked, never public_publishable
    if any source has license_terms_class not in public_safe_license_terms:
        return blocked
    if all sources are public-safe and review_state is approved:
        return public_publishable
    return blocked
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/ECOSYSTEM_WIKI_FLYWHEEL_CONTRACT.md` | Normative reusable contract for manifests, history, source classification, publication states, ledgers, and quick-reference indexes |
| Create | `docs/governance/2026-06-08-ecosystem-wiki-flywheel-routing-decision.md` | ADR-style rationale and relationship to worldenergydata #450-#453 |
| Create | `config/ecosystem-wiki-flywheel/source-classification.yaml` | Config-tier enum source of truth for validator |
| Create | `templates/ecosystem-wiki-flywheel/run-manifest.example.yml` | Canonical YAML per-run manifest template |
| Create | `templates/ecosystem-wiki-flywheel/run-history-record.example.jsonl` | Canonical append-only history record template |
| Create | `templates/ecosystem-wiki-flywheel/wiki-frontmatter.example.yml` | Canonical page frontmatter template for generated insight pages |
| Create | `templates/ecosystem-wiki-flywheel/routing-ledger-event.example.yml` | Canonical private/full ledger event template |
| Create | `templates/ecosystem-wiki-flywheel/routing-ledger-public-projection.example.yml` | Sanitized public projection template that cannot leak private paths or client/project names |
| Create | `templates/ecosystem-wiki-flywheel/quick-reference-index-entry.example.yml` | `llm-wiki` index-entry template with classification and freshness metadata |
| Create | `templates/ecosystem-wiki-flywheel/insight-bundle-metadata.example.yml` | Output bundle metadata template tying generated reports/pages back to manifest/history |
| Create | `tests/fixtures/ecosystem_wiki_flywheel/` | Hermetic valid/invalid bundle fixtures |
| Create | `tests/enforcement/test_check_ecosystem_wiki_flywheel.py` | TDD suite for validator behavior |
| Create | `scripts/enforcement/check-ecosystem-wiki-flywheel.py` | Validator for bundle templates and generated flywheel artifacts |
| Modify | `docs/plans/README.md` | Add this plan to the planning index |
| Create or update | `docs/standards/README.md` | Link the new standard from a stable standards index |
| Update | relevant runbook/index docs only if existing conventions require it | Document manual validator invocation; hook/CI rollout will be a follow-up issue, not #2975 scope |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_valid_public_bsee_bundle_passes` | all-public BSEE federal bundle with citations and hashes passes | `valid-public-bsee/` fixture | exit 0, no errors |
| `test_config_enum_file_is_source_of_truth` | source/license/publication/review/ledger/scheduler enums load from config YAML | `config/ecosystem-wiki-flywheel/source-classification.yaml` | exit 0 |
| `test_standard_enum_table_matches_config` | doc enum table cannot drift from config enum values | standard doc and config YAML | exit 0 |
| `test_unknown_enum_value_fails_closed` | unknown enum values are rejected rather than accepted as strings | `source_publication_class: maybe-public` | exit 1 |
| `test_missing_source_publication_class_fails_closed` | missing source publication classification blocks publishing | manifest source without `source_publication_class` | exit 1 with source-publication-class error |
| `test_missing_license_terms_class_fails_closed` | missing license/terms classification blocks publishing | manifest source without `license_terms_class` | exit 1 |
| `test_ambiguous_provenance_blocks_public_state` | ambiguous provenance cannot be public | `source_publication_class: locally-cached-uncertain` with public state | exit 1 |
| `test_mixed_private_public_blocks_public_state` | mixed public/private inputs cannot publish publicly | public federal + client-private inputs | exit 1 |
| `test_vendor_source_routes_private_or_blocked` | vendor/licensed source never routes public | vendor fixture | exit 1 for public, pass for blocked/private fixture |
| `test_open_public_source_classes_can_publish_with_open_license` | public commercial/open academic sources are reachable when license terms are public-safe | `public-commercial-open` or `open-academic` plus `open-license` | exit 0 |
| `test_public_source_with_private_license_blocks` | public-looking source cannot publish when license/terms are private or unknown | `public-federal-data` plus `client-confidential` | exit 1 |
| `test_public_terms_review_required_blocks_publication` | review-required terms do not publish until reclassified | `public-terms-review-required` | exit 1 |
| `test_public_projection_is_allowlist_only` | public ledger projection rejects any non-allowlisted key | projection with `client`, `project`, private repo URL, local path, or log path | exit 1 |
| `test_quick_reference_rejects_private_source_facts` | quick-reference entry cannot leak restricted facts or private source titles | public index entry with private/vendor fact | exit 1 |
| `test_public_to_private_markdown_link_fails` | public or generic entries cannot point to private/client wiki content | Markdown link to private/client target | exit 1 |
| `test_full_and_public_ledgers_are_distinct_when_private_exists` | private/full ledger separation is enforced | same file path used for both ledgers | exit 1 |
| `test_duplicate_logical_run_requires_attempt_or_supersession` | duplicate run IDs are deterministic | repeated `run_id` without `attempt_id`/supersession | exit 1 |
| `test_duplicate_ledger_event_identity_fails` | duplicate ledger events are rejected | repeated event identity | exit 1 |
| `test_llm_wiki_index_entry_is_pointer_only` | quick-reference entry cannot become raw-content duplicate | index fixture with source facts but no provenance/freshness | exit 1 |
| `test_public_federal_frontmatter_requires_authority_and_license` | public federal page frontmatter includes required adjacent fields | missing `source_authority` or `license` | exit 1 |
| `test_citation_sidecar_requires_source_sibling_and_project` | citation sidecars include route identity | missing `source_sibling` | exit 1 |
| `test_broken_wiki_target_fails` | stale/broken wiki pointer detection works in fixtures | missing target page path | exit 1 |
| `test_stale_pointer_existing_target_fails` | existing target with stale commit/hash/freshness metadata fails | superseded run or expired `last_checked_at` | exit 1 |
| `test_legal_scan_evidence_required_for_public_publishable` | public state requires legal/security scan evidence | public bundle without scan evidence | exit 1 |
| `test_forged_or_stale_legal_scan_evidence_fails` | scan evidence must match command, deny-list hash, artifact hashes, timestamp, and exit code | mutated artifact after claimed scan pass | exit 1 |
| `test_self_artifacts_are_validator_safe` | created plan, standard, templates, and valid fixtures do not block their own validator/legal checks | generated #2975 artifact paths | exit 0 |
| `test_invalid_fixtures_are_sentinel_scoped` | intentionally invalid fixtures are allowed only in fixture paths with explicit sentinel metadata | invalid fixture outside sentinel scope | exit 1 |
| `test_two_clean_manual_runs_required_before_scheduling` | scheduler eligibility requires two clean run records | one clean run or one dirty run | exit 1 |
| `test_clean_run_requires_reviewed_generated_diff` | clean-run status requires reviewed generated diff evidence | clean marker without review artifact | exit 1 |
| `test_execution_and_report_schema_compatibility` | flywheel bundle composes existing execution/report schemas | valid bundle missing existing schema field | exit 1 |
| `test_source_class_name_collision_is_prevented` | existing report evidence `source_class` is not overloaded by flywheel publication class | `source_class: public-federal-data` in report evidence source | exit 1 |
| `test_private_wiki_page_reference_requires_public_wrapper_for_public_output` | stricter flywheel wrapper closes existing schema allowance for public `private-wiki-page` references | public output with unwrapped `private-wiki-page` | exit 1 |
| `test_enhanced_legal_attestation_uses_wrapper_field` | enhanced scan evidence does not violate existing `additionalProperties: false` legal scan schemas | extra keys inside existing `legal_scan` object | exit 1 |
| `test_generated_bundle_filenames_are_required` | real bundle validation uses canonical generated filenames, not `.example` names | bundle missing `run_manifest.yml` | exit 1 |
| `test_template_mode_validates_example_filenames` | template validation mode checks `.example` files explicitly | template directory | exit 0 |
| `test_invalid_fixtures_use_synthetic_identifiers` | intentionally invalid fixtures avoid real deny-listed client/vendor names | invalid fixture with real deny-listed pattern | exit 1 |
| `test_validator_json_output_is_deterministic` | repeated validation emits stable JSON ordering | same fixture twice | byte-identical JSON |

---

## Acceptance Criteria

- [ ] `docs/standards/ECOSYSTEM_WIKI_FLYWHEEL_CONTRACT.md` will define source publication classes, license/terms classes, publication states, review states, run identity fields, ledger event types, and clean-run criteria.
- [ ] The source/license/publication/review/ledger/scheduler enums will live in `config/ecosystem-wiki-flywheel/source-classification.yaml`, and unknown values will fail closed.
- [ ] The standard doc enum table will be generated from or tested against the config enum file to prevent drift.
- [ ] The standard will keep existing `report-evidence-bundle.schema.yaml` `sources[].source_class` semantics intact and will add `source_publication_class` only as a separate publication-safety classification.
- [ ] `docs/governance/2026-06-08-ecosystem-wiki-flywheel-routing-decision.md` will explain why the standard composes existing layer/routing/citation contracts instead of replacing them.
- [ ] Templates will exist for run manifest, JSONL history record, wiki frontmatter, routing ledger event, public ledger projection, quick-reference index entry, and insight-bundle metadata.
- [ ] Validator tests will be written before implementation and will cover all failure classes from the worldenergydata adversarial decision review.
- [ ] `scripts/enforcement/check-ecosystem-wiki-flywheel.py` will validate provenance completeness, public/private contamination, citation coverage, duplicate run/history semantics, duplicate ledger events, broken wiki links, stale quick-reference pointers, and legal/security scan applicability.
- [ ] The validator will compose `docs/architecture/execution-manifest.schema.yaml` and `docs/architecture/report-evidence-bundle.schema.yaml`; it will not create incompatible replacements for `input_residency`, `output_residency`, or `promotion_gates`.
- [ ] Existing closed-schema `legal_scan_evidence` / `legal_scan` fields will still carry their required `command` and `result` values; enhanced scan evidence will live only in the flywheel wrapper field.
- [ ] Enhanced legal/security scan attestation will live in a new flywheel wrapper field and will be considered valid only when command, deny-list hash, scanned artifact hashes, timestamp, and exit code match the current bundle.
- [ ] Public publication will require `source_publication_class` in `{public-federal-data, public-commercial-open, open-academic}` and `license_terms_class` in `{public-domain, open-license}`; all other combinations will fail closed for public output.
- [ ] `llm-wiki` quick-reference entries will be defined as pointer/index artifacts only, with classification and freshness metadata, and will not duplicate raw source content.
- [ ] Public sanitized ledger projections will be explicitly separated from private/full ledgers.
- [ ] Public sanitized ledger projections will be allowlist-only and will reject client/project identifiers, private repo URLs, private issue URLs, local absolute paths, raw source snippets, citation sidecar paths, log paths, private artifact paths, and private source titles.
- [ ] The staged publishing order will be encoded: public BSEE/federal first; FDAS only after classification and citation coverage; HSE/marine only after segregation, redaction, and legal/security checks.
- [ ] Weekly/scheduled publishing will require two clean manual runs, where clean will mean no extraction errors, no citation gaps, no private contamination, deterministic manifest/history writes, no duplicate ledger entries, no broken wiki links, legal/security scan pass when applicable, and reviewed generated diffs.
- [ ] Invalid fixtures will use fabricated identifiers only, or will carry a narrowly scoped fixture sentinel that does not weaken legal/security scans outside `tests/fixtures/ecosystem_wiki_flywheel/`.
- [ ] Validator JSON output will not include wall-clock runtime values; deterministic output will use only fixture/bundle-derived timestamps and hashes.
- [ ] The standard will preserve issue -> plan -> adversarial review -> user approval -> TDD -> implementation -> code/artifact review for every consuming repo.
- [ ] worldenergydata #450-#453 will be linked back to the created standard after implementation lands.
- [ ] #2975 will land manual validator invocation and tests only; hook/CI rollout will be split to a follow-up issue after the standard and validator are approved.
- [ ] Verification will pass: `uv run pytest tests/enforcement/test_check_ecosystem_wiki_flywheel.py -v`.
- [ ] Relevant existing enforcement tests will pass: `uv run pytest tests/enforcement/test_check_wiki_sibling_frontmatter.py -v`.
- [ ] Legal/security scan will pass: `scripts/legal/legal-sanity-scan.sh`.

---

## Adversarial Review Summary

Subagent adversarial review has been completed for the decision/plan content. Formal provider review on 2026-06-08 returned MAJOR and this plan has been revised again; implementation remains blocked until fresh no-MAJOR review, explicit user approval, and `status:plan-approved`.

| Provider | Verdict | Key findings |
|---|---|---|
| Subagent Arendt | MAJOR | Existing schemas not reconciled; issue-class resource intel gaps; self-blocking and scheduling tests missing; manual/hook boundary ambiguous; leak tests too narrow |
| Subagent Feynman | MAJOR | Enums underspecified; legal scan evidence could be forged/stale; public projection leak tests too narrow; stale-pointer coverage incomplete; self-blocking tests missing; hook/CI boundary unresolved |
| Subagent Halley | MAJOR | r2 found remaining `source_class` collision and partial issue-decision evidence |
| Subagent Archimedes | MAJOR | r2 independently found `source_class` collision and enhanced legal-scan attestation incompatibility with existing closed schemas |
| Subagent Kant | APPROVE | focused r3 found the two remaining schema blockers resolved |
| Claude formal r1 | MAJOR | provider artifacts/review state, enum config under tests, enum drift, fixture/legal scan, determinism, missing standards index; general SKILL.md YAML defect filed as [workspace-hub#2981](https://github.com/vamseeachanta/workspace-hub/issues/2981) |
| Codex formal r1 | MAJOR | public-open classes unreachable, license terms ignored, enum config under tests, `private-wiki-page` wrapper gap, bundle/template filename ambiguity |
| Gemini formal r1 | MAJOR | false-positive file existence due provider workspace, plus publication logic, license terms, legal scan wrapper, sentinel pseudocode gaps |

**Overall result:** FAIL formal r1; plan remains draft-needs-revision until fresh review clears.

Revisions made based on review:
- Added existing execution/report schema reconciliation and issue-class resource-intel sources.
- Added required enum contract and fail-closed unknown-value behavior.
- Made public ledger projections allowlist-only.
- Added legal scan freshness/hash/deny-list evidence checks.
- Added stale pointer, self-artifact, invalid-fixture sentinel, two-clean-run, reviewed-diff, and existing-schema compatibility tests.
- Scoped #2975 to manual validator plus tests; hook/CI rollout will be a follow-up issue.
- Renamed the new classification field to `source_publication_class` to avoid overloading existing report evidence `source_class`.
- Moved enhanced legal scan attestation into a flywheel wrapper field instead of extending existing closed `legal_scan` objects.
- Moved enum source of truth from `tests/fixtures/` to config-tier `config/ecosystem-wiki-flywheel/source-classification.yaml`.
- Added public-source and license-term allowlist logic.
- Added wrapper rule for existing report evidence `source_class=private-wiki-page` in public outputs.
- Split generated bundle filenames from `.example` template validation mode.
- Added synthetic-fixture and deterministic-output constraints.

---

## Risks and Open Questions

- **Risk:** The new standard could duplicate `.claude/rules/wiki-sibling-routing.md`. The implementation will reference it as routing authority and only add the missing manifest/history/ledger/index layer.
- **Risk:** A validator that scans staged content could block its own fixtures/templates. The TDD suite will include self-artifact compatibility and fixture-local sentinel tests before any hook wiring follow-up is proposed.
- **Risk:** `llm-wiki` quick-reference index entries could leak private artifacts by naming paths, clients, projects, or source facts. The public projection template and validator will reject those fields in public projections.
- **Risk:** Public federal data publishing could drift as source terms change. Templates will require `source_authority`, `license_terms_class`, retrieval timestamp, and last license/terms check.
- **Risk:** Existing worldenergydata issues could be edited prematurely. This issue will only add backlinks after the standard is created and verified.
- **Resolved recommendation:** #2975 will include manual validator invocation and tests only. Hook/CI rollout will be split to a follow-up issue after this standard and validator land.
- **Resolved recommendation:** `source_publication_class` and related license/publication/review/ledger/scheduler enums will live in `config/ecosystem-wiki-flywheel/source-classification.yaml`; standard-doc tables will be generated from or tested against that config source of truth.

---

## Complexity: T3

**T3** — cross-repo governance standard with templates, validator, tests, wiki/public-private routing implications, and downstream consumers across `worldenergydata`, `llm-wiki`, `worldenergydata-wiki`, and future sibling wikis.
