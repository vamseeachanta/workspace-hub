# Plan for #2975: Ecosystem Wiki Flywheel Manifest, Provenance, and Routing Contract

> **Status:** superseded-by-phase-a-split
> **Complexity:** T3
> **Date:** 2026-06-08
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2975
> **Client:** N/A
> **Project:** N/A
> **Review artifacts:** scripts/review/results/2026-06-08-plan-2975-claude.md | scripts/review/results/2026-06-08-plan-2975-codex.md | scripts/review/results/2026-06-08-plan-2975-gemini.md | r2/r3/r4/r5/r6/r7/r8 timestamped artifacts in scripts/review/results/ | superseded by `docs/plans/2026-06-09-issue-2975-phase-a-ecosystem-wiki-flywheel-contract.md`

---

**Supersession note:** r8 review found this omnibus plan too large for one approval unit. It is preserved as historical blocked evidence. Current #2975 planning continues in `docs/plans/2026-06-09-issue-2975-phase-a-ecosystem-wiki-flywheel-contract.md`; validator implementation moved to [workspace-hub#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013).

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
- [workspace-hub#2945](https://github.com/vamseeachanta/workspace-hub/issues/2945) — related repo-ecosystem flywheel closeout work; no local #2945 plan file is cited because `docs/plans/2026-06-02-issue-2945-repo-ecosystem-flywheel.md` is not present on this branch.
- [workspace-hub#2975](https://github.com/vamseeachanta/workspace-hub/issues/2975) — defines the governing standard request and links the worldenergydata trigger issues.
- [workspace-hub#2975](https://github.com/vamseeachanta/workspace-hub/issues/2975) — governing issue body carries the tightened decisions this plan must satisfy: public publishing only for cited/classified/reviewed public inputs; missing/mixed/ambiguous provenance fails closed; public ledger projections are separate from private/full ledgers; `llm-wiki` is a pointer/index layer; indexes carry classification/freshness metadata; scheduled publishing starts only after two clean manual runs.
- [worldenergydata#450](https://github.com/vamseeachanta/worldenergydata/issues/450), [worldenergydata#451](https://github.com/vamseeachanta/worldenergydata/issues/451), [worldenergydata#452](https://github.com/vamseeachanta/worldenergydata/issues/452), and [worldenergydata#453](https://github.com/vamseeachanta/worldenergydata/issues/453) — background trigger issues for downstream adoption only. Their bodies/titles are not the normative source for #2975's enum set or staged-publishing order.

### Gaps identified

- No single workspace-hub standard will bind run manifests, append-only run history, wiki publication metadata, quick-reference indexes, and routing ledgers.
- No template family will give source repos a reusable manifest/history/frontmatter/ledger/index shape.
- No `source_publication_class` schema will distinguish public federal, public commercial, open academic, vendor/licensed, client/private, user-provided, locally cached uncertain, mixed, and blocked sources.
- No license/terms-classification schema will fail closed for missing or ambiguous reuse rights.
- Existing `execution-manifest.schema.yaml` and `report-evidence-bundle.schema.yaml` will need to be composed by reference and additively extended for the public-federal wiki route. #2975 will add `output_residency: public_federal_wiki` so BSEE/NOAA/USGS/MMS public-domain outputs do not get collapsed into generic `public_llm_wiki`; it will not otherwise fork `input_residency`, `output_residency`, or `promotion_gates`.
- No validator will currently prove provenance completeness, citation coverage, public/private contamination, duplicate logical runs, duplicate ledger events, broken wiki links, stale quick-reference pointers, or legal/security scan applicability for a generated insight bundle.
- No generated `llm-wiki` quick-reference entry contract will prevent `llm-wiki` from becoming a duplicate raw-content store.

### Required enum contract

The implementation will make `config/ecosystem-wiki-flywheel/source-classification.yaml` the validator source of truth, following the existing validator precedent that production enforcement reads config/registry files rather than `tests/fixtures/`. Unknown or alias-only values will fail closed unless explicitly mapped in that config file. The config will carry `public_safe` flags for source and license classes, but those flags are not editable policy: schema tests will reject any config where the `public_safe: true` set differs from the standard-defined source subset `{public-federal-data, public-commercial-open, open-academic}` or license subset `{public-domain, open-license}`.

The standard will copy the config values into one fenced `yaml` block whose root key is `ecosystem_wiki_flywheel_enums`. `test_standard_enum_table_matches_config` will parse only that block and compare it exactly against `source-classification.yaml`; prose tables may summarize the values but will not be parser targets.

| Enum | Required values |
|---|---|
| `source_publication_class` | `public-federal-data`, `public-commercial-open`, `open-academic`, `vendor-licensed`, `client-private`, `user-provided-private`, `locally-cached-uncertain`, `mixed`, `blocked` |
| `license_terms_class` | `public-domain`, `open-license`, `public-terms-review-required`, `vendor-license`, `client-confidential`, `unknown`, `blocked` |
| `publication_state` | `public_publishable`, `private_publishable`, `blocked`, `superseded`, `deprecated` |
| `review_state` | `unreviewed`, `review-required`, `approved`, `approved-with-notes`, `rejected` |
| `ledger_event_type` | `created`, `linked`, `promoted`, `moved`, `blocked`, `deprecated`, `redacted`, `superseded` |
| `scheduler_state` | `manual-only`, `eligible-after-two-clean-runs`, `scheduled-enabled`, `scheduled-blocked` |
| `output_residency` extension | `public_federal_wiki` added to the existing schema enum; `public_llm_wiki` remains for other public-safe generic outputs |

Public ledger projections will be allowlist-only. They may include only public-safe event identity, public source class, a closed destination object, citation coverage status, freshness timestamps, and review state. They must not include `client`, `project`, private repository URLs, private issue URLs, local absolute paths, raw source snippets, citation sidecar paths, log paths, private artifact paths, private source titles, or any string value matching the legal deny-list. Public projection identifiers (`event_id`, `run_id`, and supersession references) must be minted from public tokens only: source authority, public dataset slug, generated date, attempt number, and a short content hash. Arbitrary source titles, client/project slugs, local folder names, and issue URLs are invalid inside allowed public keys.

The positive identity rule is structural, not deny-list-only. `source-classification.yaml` will include:

```yaml
public_identity:
  authority_codes: [bsee, noaa, usgs, mms]
  dataset_slugs:
    bsee: [well-activity-report, production, incidents]
    noaa: []
    usgs: []
    mms: []
  id_pattern: "^(bsee|noaa|usgs|mms)-[a-z0-9][a-z0-9-]*-[0-9]{8}-a[0-9]+-[a-f0-9]{8,12}$"
```

The validator will require the authority code and dataset slug to appear in that registry before accepting a public `run_id`, `event_id`, or supersession reference. Deny-list/private-path scans still run over the resulting strings as a second line of defense.

The standard will include a threat-model checklist table mapping each public-egress field to a closing test:

| Public egress path | Closing test |
|---|---|
| `run_id`, `event_id`, `supersedes_event_id` | `test_public_projection_ids_match_public_identity_registry` + `test_public_projection_string_values_are_denylist_scanned` |
| `destination.repo`, `destination.path`, `destination.visibility` | `test_public_projection_destination_schema_is_closed` + `test_public_projection_string_values_are_denylist_scanned` |
| `freshness.*` timestamps | `test_validator_json_output_is_deterministic` |
| public wiki frontmatter | `test_public_federal_frontmatter_requires_authority_and_license` |
| quick-reference index entry | `test_llm_wiki_index_entry_is_pointer_only` + `test_quick_reference_rejects_private_source_facts` |
| public ledger keys/nested objects | `test_public_projection_is_allowlist_only` + `test_public_projection_allowed_keys_are_exact` |
| legal scan artifact references | `test_legal_attestation_rejects_absolute_path`, `test_legal_attestation_rejects_traversal_path`, `test_legal_attestation_rejects_symlink_path` |

The staged publishing order will live in the same config and the standard's fenced YAML block:

```yaml
publication_sequence:
  - stage_id: public-federal-first
    order: 1
    source_publication_classes: [public-federal-data]
    license_terms_classes: [public-domain]
    allowed_output_residency: public_federal_wiki
    allowed_destination_repos: [worldenergydata-wiki]
    required_checks:
      - citation_coverage_complete
      - legal_scan_pass
      - public_identity_registry_match
      - public_projection_value_scan
  - stage_id: fdas-classified
    order: 2
    source_publication_classes: [public-commercial-open, open-academic]
    license_terms_classes: [open-license]
    allowed_output_residency: public_llm_wiki
    required_checks:
      - source_classification_complete
      - citation_coverage_complete
      - license_terms_review_complete
      - public_projection_value_scan
  - stage_id: hse-marine-segregated
    order: 3
    source_publication_classes: [mixed]
    license_terms_classes: [public-terms-review-required]
    allowed_output_residency: domain_private_corpus
    required_checks:
      - source_segregation_complete
      - redaction_review_complete
      - legal_scan_pass
```

`test_staged_publishing_order_is_machine_readable` will fail if any stage, order value, required key, or required check is missing or if the stages are not strictly increasing.

`source_publication_class` will be an additive flywheel/publication-safety field. It will not replace or overload `report-evidence-bundle.schema.yaml` `sources[].source_class`, which remains a source-reference-kind field with values such as `source-doc-key`, `promotion-ledger-entry`, `private-wiki-page`, `execution-manifest`, and `internal-note`. Enhanced legal scan attestation will also live in a flywheel wrapper field, not inside existing `legal_scan_evidence` or `legal_scan` objects, because those existing schemas use `additionalProperties: false`.

Public publication will require both a public-safe `source_publication_class` and a public-safe `license_terms_class`. The public-safe publication classes will be `public-federal-data`, `public-commercial-open`, and `open-academic`. The public-safe `license_terms_class` values will be `public-domain` and `open-license`; `public-terms-review-required` will block public publication until review changes it to a public-safe class. Existing `legal_scan_evidence` / `legal_scan` fields will still be populated with their closed-schema `command` and `result` fields; the enhanced `legal_scan_attestation` wrapper will bind those closed-schema fields to command hash, deny-list hash, scanned artifact hashes, timestamp, and exit code.

For report evidence bundles whose existing `sources[].source_class` is `private-wiki-page`, public output will remain blocked unless the flywheel wrapper contains all of:

- `wrapped_source_ref_id` that points at the report-evidence source record.
- `source_publication_class` whose config entry is public-safe.
- `license_terms_class` whose config entry is public-safe.
- `public_release_clearance_id` that references a review artifact or routing-ledger event.
- `sanitized_projection_ref` that points at the public allowlist-only projection, not the private/full ledger.
- `citation_coverage_status: complete`.

The wrapper does not change the legacy report-evidence `source_class`; it only proves that the public output is derived from a separately cleared public-safe projection. Missing any wrapper field fails closed for public output.

### Evidence (embedded verification)

**Issue references** (inspected 2026-06-09 via repo-qualified local `gh issue view --repo vamseeachanta/worldenergydata` and GitHub connector because `scripts/review/attest-plan-claims.sh` is same-repo-only and cannot distinguish cross-repo issue numbers):
- [workspace-hub#2975](https://github.com/vamseeachanta/workspace-hub/issues/2975) — OPEN — `standard: ecosystem wiki flywheel manifest, provenance, and routing contract`
- [worldenergydata#450](https://github.com/vamseeachanta/worldenergydata/issues/450) — OPEN — `feat(flywheel): define catalog-to-workflow manifest for well-operations insight runs`
- [worldenergydata#451](https://github.com/vamseeachanta/worldenergydata/issues/451) — OPEN — `feat(flywheel): integrate BSEE and FDAS source readiness for well-operations runs`
- [worldenergydata#452](https://github.com/vamseeachanta/worldenergydata/issues/452) — OPEN — `feat(flywheel): run well-operations insight workflow from WAR, production, FDAS, and HSE inputs`
- [worldenergydata#453](https://github.com/vamseeachanta/worldenergydata/issues/453) — OPEN — `feat(flywheel): publish well-operations insight outputs to wiki with provenance and routing gates`

The `worldenergydata` issue live state is context, not a #2975 implementation gate. The contract is triggered by their decision content and titles; if any of #450-#453 closes, reopens, or is superseded before #2975 implementation, the standard and validator scope do not change. Backlinking after #2975 lands will re-check the issue state at closeout time.

Repo-qualified local `gh` transcript captured 2026-06-09 with:

```bash
for n in 450 451 452 453; do
  gh issue view "$n" --repo vamseeachanta/worldenergydata \
    --json number,state,title \
    --jq '"- worldenergydata#\(.number) \(.state) \(.title)"'
done
```

```text
- worldenergydata#450 OPEN feat(flywheel): define catalog-to-workflow manifest for well-operations insight runs
- worldenergydata#451 OPEN feat(flywheel): integrate BSEE and FDAS source readiness for well-operations runs
- worldenergydata#452 OPEN feat(flywheel): run well-operations insight workflow from WAR, production, FDAS, and HSE inputs
- worldenergydata#453 OPEN feat(flywheel): publish well-operations insight outputs to wiki with provenance and routing gates
```

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
- EXISTS: `tests/architecture/test_report_layer_contract.py`
- EXISTS: `docs/architecture/execution-manifest.schema.yaml`
- EXISTS: `docs/architecture/report-evidence-bundle.schema.yaml`
- EXISTS: `data/document-index/registry.yaml`
- EXISTS: `data/document-index/resource-intelligence-maturity.yaml`
- EXISTS: `docs/standards/CONTROL_PLANE_CONTRACT.md`
- EXISTS: `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- EXISTS: `docs/document-intelligence/intelligence-accessibility-map.md`
- EXISTS: `templates/client-llm-wiki/README.md`
- MISSING (new — this plan will create): `config/ecosystem-wiki-flywheel/source-classification.yaml`
- MISSING (new — this plan will create): `docs/standards/ECOSYSTEM_WIKI_FLYWHEEL_CONTRACT.md`
- MISSING (new — this plan will create): `docs/standards/README.md`
- MISSING (new — this plan will create): `docs/governance/2026-06-08-ecosystem-wiki-flywheel-routing-decision.md`
- MISSING (new — this plan will create): `templates/ecosystem-wiki-flywheel/`
- MISSING (new — this plan will create): `tests/fixtures/ecosystem_wiki_flywheel/`
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

`docs/architecture/report-evidence-bundle.schema.yaml` already defines public-output fail-closed rules and will receive the same additive `public_federal_wiki` enum extension as the execution manifest schema:

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

**Attested same-repo evidence:** `scripts/review/attest-plan-claims.sh docs/plans/2026-06-08-issue-2975-ecosystem-wiki-flywheel-contract.md` must be rerun immediately before the review that moves this plan to `status:plan-review`; the attestation hash is intentionally not embedded in this changing draft. The helper verifies same-repo workspace-hub issue/path evidence only. It will report same-number workspace-hub issues #450-#453 as closed; that is not contradictory because the `worldenergydata` issues are background adoption links, not normative evidence for this plan.

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
| Execution manifest schema extension | `docs/architecture/execution-manifest.schema.yaml` |
| Report evidence bundle schema extension | `docs/architecture/report-evidence-bundle.schema.yaml` |
| Valid example fixture | `tests/fixtures/ecosystem_wiki_flywheel/valid-public-bsee/` |
| Invalid mixed-provenance fixture | `tests/fixtures/ecosystem_wiki_flywheel/invalid-mixed-provenance/` |
| Invalid ledger-leak fixture | `tests/fixtures/ecosystem_wiki_flywheel/invalid-ledger-leak/` |
| Validator CLI | `scripts/enforcement/check-ecosystem-wiki-flywheel.py` |
| Validator helpers | `scripts/enforcement/ecosystem_wiki_flywheel/` |
| Validator tests | `tests/enforcement/test_check_ecosystem_wiki_flywheel.py` |
| Hook/CI rollout follow-up | separate follow-up issue; #2975 will land a manual validator plus tests only |
| Plan review — Claude | `scripts/review/results/2026-06-08-plan-2975-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-06-08-plan-2975-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-06-08-plan-2975-gemini.md` |
| Plan review r2 | `scripts/review/results/<timestamp>-2026-06-08-issue-2975-ecosystem-wiki-flywheel-contract.md-plan-*.md` |

---

## Deliverable

A workspace-hub standard, governance decision, template family, and focused validator/test suite will define how repo outputs become durable wiki-backed insight flywheels without leaking private/vendor/client data or bypassing issue/plan/review gates.

### MVP Boundary

| Capability | #2975 scope | Follow-up scope |
|---|---|---|
| Validator target | Hermetic local fixture bundles and template examples | Live sibling-repo scans, staged-content hooks, CI enforcement |
| Link/stale checks | Standard-only machine-readable freshness and pointer criteria; validator checks destination shape only | Fixture-local target existence, stale-pointer validation, network or cross-repo live link crawling |
| Legal scan evidence | Deterministic fixture attestation and diff-safe artifact hashing | Repository-wide or scheduled legal/security gates |
| Scheduler readiness | Standard-only machine-readable clean-run criteria and staged order | Validate two-clean-run readiness and enable scheduler readiness |
| Ledger projection | Template and fixture validation for allowlist-only public projections | Central workspace-hub ledger aggregation |
| worldenergydata linkage | Standard defines the backlink contract | Edit/comment #450-#453 after implementation lands |

MVP validator enforcement is limited to local fixture bundles and templates, but it includes every validator behavior listed in the #2975 acceptance criteria: config enum loading and shape checks, public-safe config invariants, generated-bundle vs template-mode filename separation, publication-state classification, public-federal `worldenergydata-wiki` output routing, provenance completeness, citation coverage, public/private contamination, duplicate run/history semantics, duplicate ledger events, report-evidence `private-wiki-page` wrapper gates, stable wrapper source IDs, public projection key allowlist and value-level leakage scans, closed destination schema, legal-scan attestation path/hash/freshness checks for public output, staged publishing order encoding, deterministic JSON output, and existing execution/report schema validation against local fixtures. The #2975 validator will not check target-page existence, stale target content, or two-clean-run scheduler readiness; the standard will define those requirements machine-readably and follow-up hardening issues will enforce them.

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
        using PyYAML + jsonschema Draft202012Validator, matching existing
        tests/architecture/test_report_layer_contract.py dependency pattern
    validate public-federal outputs use output_residency=public_federal_wiki and
        destination.repo=worldenergydata-wiki, not generic public_llm_wiki
    validate public outputs contain only public-safe source_publication_class values
    validate public outputs contain only public-safe license_terms_class values
    validate report-evidence source_class=private-wiki-page is blocked for public output
        unless the flywheel wrapper binds it to a public-safe source_publication_class,
        public-safe license_terms_class, public release clearance, and sanitized projection
    validate ambiguous, mixed, vendor, client, or locally uncertain sources fail closed
    validate every wiki target has required frontmatter fields for its destination sibling
    validate llm-wiki quick-reference entries are index pointers with classification/freshness metadata
    validate public ledger projection uses allowlist-only schema
    validate every public projection identity matches the public_identity registry and every public projection string value is deny-list clean
    validate private/full ledger and public sanitized projection are distinct when private artifacts exist
    validate duplicate logical runs are rejected, superseded, or recorded as attempts
    validate no duplicate ledger event identity exists
    validate legal_scan_attestation structure and deterministic hashes when present
    record scheduler_state criteria in the standard; full scheduler eligibility
        enforcement is follow-up hardening
    emit deterministic JSON result with errors and warnings
```

Validation order is fixed:

1. Load `run_manifest.yml` and validate it against `docs/architecture/execution-manifest.schema.yaml`.
2. Load the referenced report evidence bundle and validate it against `docs/architecture/report-evidence-bundle.schema.yaml`.
3. Load `insight_bundle_metadata.yml` and validate the flywheel envelope there.
4. Validate cross-reference constraints from `insight_bundle_metadata.yml` into the already-valid manifest and report evidence bundle.

The flywheel wrapper lives only in `insight_bundle_metadata.yml`:

```yaml
flywheel_wrapper:
  report_evidence_refs:
    - ref_id: report-source-1
      wrapped_source_ref_id: bsee-war-public-source
      source_publication_class: public-federal-data
      license_terms_class: public-domain
      public_release_clearance_id: review-or-ledger-event-id
      sanitized_projection_ref: routing_ledger_public_projection.yml#event-id
      citation_coverage_status: complete
      approved_with_notes_gate_status: all-gates-resolved
```

No flywheel wrapper fields are added inside existing closed-schema objects. `wrapped_source_ref_id` must equal a stable `report-evidence-bundle.schema.yaml` `sources[].source_id`; array ordinals such as `sources[0]` are invalid because source ordering is not an identity. Missing, dangling, or order-dependent references fail closed.

Bundle mode and template mode are intentionally separate:

| Validator mode | Required names | Purpose |
|---|---|---|
| Bundle mode | `run_manifest.yml`, `run_history.jsonl`, `insight_bundle_metadata.yml`, `routing_ledger.yml`, `routing_ledger_public_projection.yml` | Validate generated run outputs from source repos. `.example` names are rejected in this mode. |
| Template mode (`--validate-template`) | `run-manifest.example.yml`, `run-history-record.example.jsonl`, `insight-bundle-metadata.example.yml`, `routing-ledger-event.example.yml`, `routing-ledger-public-projection.example.yml`, `wiki-frontmatter.example.yml`, `quick-reference-index-entry.example.yml` | Validate reusable examples under `templates/ecosystem-wiki-flywheel/`. Generated bundle names are not required in this mode. |

```text
function classify_publication_state(sources, output_residency, review_state, approved_with_notes_gate_status, destination, frontmatter, config):
    public_safe_source_classes = config.source_publication_classes where public_safe is true
    public_safe_license_terms = config.license_terms_classes where public_safe is true
    if public_safe_source_classes != {public-federal-data, public-commercial-open, open-academic}:
        return blocked
    if public_safe_license_terms != {public-domain, open-license}:
        return blocked
    if any source lacks source_publication_class, citation, license_terms_class, or hash:
        return blocked
    if any source has source_publication_class == blocked or license_terms_class == blocked:
        return blocked
    if output_residency == public_federal_wiki:
        if review_state != approved:
            return blocked
        if any source has source_publication_class != public-federal-data:
            return blocked
        if any source has license_terms_class != public-domain:
            return blocked
        if destination.repo != worldenergydata-wiki or frontmatter.visibility != public-federal-data:
            return blocked
        return public_publishable
    if output_residency == public_llm_wiki:
        if review_state != approved:
            return blocked
        if any source has source_publication_class not in public_safe_source_classes:
            return blocked
        if any source has license_terms_class not in public_safe_license_terms:
            return blocked
        return public_publishable
    if output_residency in {private_llm_wiki, private_client_wiki}:
        if review_state == approved:
            if no source has source_publication_class in {mixed, locally-cached-uncertain, blocked}:
                return private_publishable
        if review_state == approved-with-notes:
            if approved_with_notes_gate_status == all-gates-resolved:
                if no source has source_publication_class in {mixed, locally-cached-uncertain, blocked}:
                    return private_publishable
        if review_state == approved-with-notes and approved_with_notes_gate_status != all-gates-resolved:
            return blocked
    return blocked
```

The `approved_with_notes_gate_status` field is structured, not parsed from free text. Allowed values are `all-gates-resolved` and `gates-open`; missing values fail closed when `review_state: approved-with-notes`.

Public ledger projection schema is allowlist-only:

| Key | Required | Type | Rule |
|---|---|---|---|
| `event_id` | yes | string | Stable public event identity matching the positive `public_identity` registry and pattern; no private issue IDs. |
| `event_type` | yes | enum | Must use `ledger_event_type` from config. |
| `run_id` | yes | string | Public-safe run identity matching the positive `public_identity` registry and pattern. |
| `source_publication_class` | yes | enum | Must be public-safe per config for public projections. |
| `publication_state` | yes | enum | Public projection may expose only `public_publishable`, `blocked`, `superseded`, or `deprecated`. |
| `destination` | yes | object | Closed object: `repo`, `path`, `visibility`. In `routing_ledger_public_projection.yml`, `repo` must be `worldenergydata-wiki` for `public_federal_wiki`; private `llm-wiki` quick-reference pointers are represented only in the private/full ledger or `quick-reference-index-entry.example.yml`, not in the public projection. `path` must be a normalized repo-relative POSIX path under config allowlisted public prefixes; absolute paths, `..`, symlinks, private prefixes, and arbitrary external URLs are rejected. `visibility` must match the wiki frontmatter visibility. |
| `citation_coverage_status` | yes | enum | `complete`, `partial`, or `missing`; public publishable requires `complete`. |
| `freshness` | yes | object | `data_as_of`, `generated_at`, `last_checked_at`; ISO-8601 UTC. |
| `review_state` | yes | enum | Same config enum. |

Any nested object not listed above fails. Free-text fields and arbitrary URL fields are not allowed in the public projection MVP; follow-up hardening may add redacted summaries or URL rendering with explicit tests. The validator will apply the legal deny-list and private-path/private-URL regexes to every string value in the public projection, including allowed keys, so leaking a client slug through `run_id`, `event_id`, `destination.path`, or `destination.repo` fails closed.

Legal scan attestation canonicalization for the MVP:

```text
path normalization:
    accept only repo-relative POSIX paths; reject absolute paths, '..', and symlinks
artifact hash:
    sha256(raw file bytes); no YAML canonicalization and no newline normalization
fixture hash stability:
    committed fixture files with recorded hashes must be covered by .gitattributes
    LF normalization (`*.yml`, `*.yaml`, `*.json`, and new `*.jsonl text eol=lf`);
    tests verify the checked-out raw bytes match the recorded fixture hashes
deny-list hash:
    sha256(raw .legal-deny-list.yaml bytes)
command hash:
    sha256(exact command string stored in manifest)
timestamp window:
    max(input.checked_at, output.generated_at) <= legal_scan.completed_at <= reference_time
forgery check:
    validator re-reads the on-disk fixture/bundle artifact paths at validation time
    and compares freshly computed hashes to recorded hashes; recorded hashes alone
    are never trusted
missing file:
    fail closed
file mode:
    ignored for content hash; executable-bit policy is outside #2975
```

`reference_time`, `checked_at`, `generated_at`, and `completed_at` must be fixture/bundle fields in UTC ISO-8601 format. The validator does not call the wall clock.

Real-run freshness anchoring path for the standard: non-fixture public-publish bundles must record `reference_time_source` as `ci-run`, `git-commit`, or `external-attestation`; `fixture` is allowed only in test fixtures. #2975 validates the field and documents the policy; hook/CI follow-up will enforce trusted timestamp injection for non-fixture runs.

Ledger event identity is the tuple `(event_id, run_id, event_type)`. Duplicating that tuple fails. Reusing `event_id` with a different run or event type emits an error unless the event type is `superseded` and the record includes `supersedes_event_id`.

Stale-pointer thresholds are standard-defined but not validator-blocking in #2975. The standard will define `freshness.max_age_days` in `source-classification.yaml`; follow-up live-link/stale-pointer validation will enforce it against sibling repositories.

Implementation phases inside #2975:

| Phase | Required in #2975 | Deferred |
|---|---|---|
| Phase A | TDD first: failing tests/fixtures for config shape, fenced enum block, template filenames, standards index, and governance decision; then standard, governance decision, config schema, templates | None |
| Phase B | TDD first: failing blocking validator tests; then MVP validator and helper modules for config, bundle/template mode, publication state, wrapper gates, projection allowlist, legal attestation, ledger identity, schema composition, deterministic output | Live-link crawling, scheduler enablement, central ledger aggregation |
| Phase C | Document follow-up issues for hardening gaps found during implementation | Hook/CI rollout and weekly publishing enablement |

Implementation cutoff rule: all tests listed in the non-cuttable blocking subset are required for #2975 approval-to-close. If implementation complexity threatens reviewability, the implementer must stop and replan rather than silently deferring any current blocking test. The public-output gates are non-deferrable in this issue: source/license classification, public-safe config invariants, public-federal routing, public projection key/value/destination checks, legal attestation, stable wrapper source IDs, and schema compatibility.

Helper-module review map:

| Helper module | Primary tests |
|---|---|
| `enums.py` | enum source, fenced YAML sync, public-safe invariant, staged publishing order |
| `schema_validation.py` | execution/report schema compatibility and `public_federal_wiki` regression tests |
| `publication_state.py` | public/private state, review-state, license/source gating |
| `projection.py` | public projection key schema, positive identity registry, deny-list value scan, destination schema |
| `legal_attestation.py` | path normalization, symlink rejection, fixture hash stability, raw-byte hash recheck |
| `ledger.py` | duplicate logical runs and duplicate ledger event identity |
| `wrapper.py` | private-wiki-page wrapper gates and stable source-id binding |
| `determinism.py` | deterministic JSON output and runtime timestamp exclusion |

Future stale-pointer enforcement will use a fixture or bundle `reference_time` field, not wall-clock time. The #2975 validator JSON will echo only bundle-derived timestamps/hashes and sorted error/warning records; it will not include runtime `now`.

Legal scan attestation checks in #2975 will use the exact canonicalization table above: repo-relative POSIX paths only, symlinks rejected, SHA-256 over raw file bytes, SHA-256 over raw `.legal-deny-list.yaml` bytes, SHA-256 over the exact command string, and the deterministic timestamp window `max(input.checked_at, output.generated_at) <= legal_scan.completed_at <= reference_time`. These checks are hermetic for #2975 fixtures; live sibling-repo scans, hooks, and CI gates are follow-up scope.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/ECOSYSTEM_WIKI_FLYWHEEL_CONTRACT.md` | Normative reusable contract for manifests, history, source classification, publication states, ledgers, and quick-reference indexes |
| Create | `docs/governance/2026-06-08-ecosystem-wiki-flywheel-routing-decision.md` | ADR-style rationale and relationship to worldenergydata #450-#453 |
| Create | `config/ecosystem-wiki-flywheel/source-classification.yaml` | Config-tier enum source of truth for validator |
| Modify | `.gitattributes` | Add `*.jsonl text eol=lf` so committed run-history fixtures have stable raw-byte hashes across checkout environments |
| Modify | `docs/architecture/execution-manifest.schema.yaml` | Add `public_federal_wiki` as an output-residency enum value for public-domain federal outputs routed to `worldenergydata-wiki` |
| Modify | `docs/architecture/report-evidence-bundle.schema.yaml` | Add the same `public_federal_wiki` value and public-output fail-closed constraints so report bundles and execution manifests agree |
| Create | `templates/ecosystem-wiki-flywheel/run-manifest.example.yml` | Canonical YAML per-run manifest template |
| Create | `templates/ecosystem-wiki-flywheel/run-history-record.example.jsonl` | Canonical append-only history record template |
| Create | `templates/ecosystem-wiki-flywheel/wiki-frontmatter.example.yml` | Canonical page frontmatter template for generated insight pages |
| Create | `templates/ecosystem-wiki-flywheel/routing-ledger-event.example.yml` | Canonical private/full ledger event template |
| Create | `templates/ecosystem-wiki-flywheel/routing-ledger-public-projection.example.yml` | Sanitized public projection template that cannot leak private paths or client/project names |
| Create | `templates/ecosystem-wiki-flywheel/quick-reference-index-entry.example.yml` | `llm-wiki` index-entry template with classification and freshness metadata |
| Create | `templates/ecosystem-wiki-flywheel/insight-bundle-metadata.example.yml` | Output bundle metadata template tying generated reports/pages back to manifest/history |
| Create | `tests/fixtures/ecosystem_wiki_flywheel/` | Hermetic valid/invalid bundle fixtures |
| Create | `tests/enforcement/test_check_ecosystem_wiki_flywheel.py` | TDD suite for validator behavior |
| Create | `scripts/enforcement/check-ecosystem-wiki-flywheel.py` | Thin validator CLI for bundle templates and generated flywheel artifacts |
| Create | `scripts/enforcement/ecosystem_wiki_flywheel/` | Helper modules split by concern: enums, schema validation, publication state, projection schema, legal attestation, ledger checks |
| Modify | `docs/plans/README.md` | Add this plan to the planning index |
| Create | `docs/standards/README.md` | Minimal standards index with: title, one-line purpose, table of standard path/title/status/date, and link to `ECOSYSTEM_WIKI_FLYWHEEL_CONTRACT.md`; no ownership or policy changes beyond indexability |
| Update | relevant runbook/index docs only if existing conventions require it | Document manual validator invocation; hook/CI rollout will be a follow-up issue, not #2975 scope |

---

## TDD Test List and Hardening Inventory

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_valid_public_bsee_bundle_passes` | all-public BSEE federal bundle with citations and hashes passes | `valid-public-bsee/` fixture | exit 0, no errors |
| `test_config_enum_file_is_source_of_truth` | source/license/publication/review/ledger/scheduler enums load from config YAML | `config/ecosystem-wiki-flywheel/source-classification.yaml` | exit 0 |
| `test_standard_enum_table_matches_config` | fenced `yaml` block rooted at `ecosystem_wiki_flywheel_enums` in the standard is parsed and compared exactly against config enum values | standard doc and config YAML | exit 0 |
| `test_unknown_enum_value_fails_closed` | unknown enum values are rejected rather than accepted as strings | `source_publication_class: maybe-public` | exit 1 |
| `test_missing_source_publication_class_fails_closed` | missing source publication classification blocks publishing | manifest source without `source_publication_class` | exit 1 with source-publication-class error |
| `test_missing_license_terms_class_fails_closed` | missing license/terms classification blocks publishing | manifest source without `license_terms_class` | exit 1 |
| `test_ambiguous_provenance_blocks_public_state` | ambiguous provenance cannot be public | `source_publication_class: locally-cached-uncertain` with public state | exit 1 |
| `test_mixed_private_public_blocks_public_state` | mixed public/private inputs cannot publish publicly | public federal + client-private inputs | exit 1 |
| `test_vendor_source_routes_private_or_blocked` | vendor/licensed source never routes public | vendor fixture | exit 1 for public, pass for blocked/private fixture |
| `test_open_public_source_classes_can_publish_with_open_license` | public commercial/open academic sources are reachable when license terms are public-safe | `public-commercial-open` or `open-academic` plus `open-license` | exit 0 |
| `test_public_safe_flags_match_standard_subset` | config carries public-safe flags but cannot expand or shrink the standard-defined public-safe source/license subsets | config fixture marks `vendor-licensed` public-safe or removes `public-federal-data` public-safe | exit 1 |
| `test_each_non_public_safe_license_blocks_public_output` | every non-allowlisted license class blocks public publication | `public-terms-review-required`, `vendor-license`, `client-confidential`, `unknown`, `blocked` | exit 1 for each |
| `test_public_source_with_private_license_blocks` | public-looking source cannot publish when license/terms are private or unknown | `public-federal-data` plus `client-confidential` | exit 1 |
| `test_public_terms_review_required_blocks_publication` | review-required terms do not publish until reclassified | `public-terms-review-required` | exit 1 |
| `test_public_federal_output_residency_routes_worldenergydata_wiki` | BSEE/NOAA/USGS/MMS public-domain outputs use the explicit public-federal residency and public federal sibling | `public-federal-data` + `public-domain` + `output_residency: public_federal_wiki` + `destination.repo: worldenergydata-wiki` | exit 0 |
| `test_public_federal_cannot_route_to_generic_public_llm_wiki` | public federal output does not silently collapse into generic public llm-wiki routing | same source classes with `output_residency: public_llm_wiki` or `destination.repo: llm-wiki` | exit 1 |
| `test_publication_state_matches_output_residency` | public/private publication states align with target output residency | public state with private target or private state with public target | exit 1 |
| `test_private_publication_state_is_deterministic` | non-public sources either become private publishable or blocked by explicit table rules | private wiki target and reviewed source classes | deterministic state |
| `test_public_review_state_policy_is_explicit` | `approved-with-notes` does not publish publicly | public target with `approved-with-notes` | exit 1 |
| `test_private_approved_with_notes_requires_all_gates_resolved` | private publish with notes requires structured gate closure | `approved-with-notes` plus `gates-open` | exit 1 |
| `test_public_projection_is_allowlist_only` | public ledger projection rejects any non-allowlisted key | projection with `client`, `project`, private repo URL, local path, or log path | exit 1 |
| `test_public_projection_allowed_keys_are_exact` | public projection cannot add undeclared nested keys or free-text fields | projection with extra nested key or summary | exit 1 |
| `test_public_projection_ids_match_public_identity_registry` | public `run_id`, `event_id`, and supersession refs match the authority/dataset/date/attempt/hash pattern and registry | ID with unknown dataset slug or malformed authority/date/hash | exit 1 |
| `test_public_projection_string_values_are_denylist_scanned` | allowed public projection keys cannot carry private values | `run_id`, `event_id`, or `destination.path` containing a client slug, private issue URL, local path, or deny-list hit | exit 1 |
| `test_public_projection_destination_schema_is_closed` | destination is a closed repo/path/visibility object with allowlisted repos and normalized paths only | destination with arbitrary URL, unlisted repo, absolute path, `..`, private prefix, or extra key | exit 1 |
| `test_quick_reference_rejects_private_source_facts` | quick-reference entry cannot leak restricted facts or private source titles | public index entry with private/vendor fact | exit 1 |
| `test_public_to_private_markdown_link_fails` | public or generic entries cannot point to private/client wiki content | Markdown link to private/client target | exit 1 |
| `test_full_and_public_ledgers_are_distinct_when_private_exists` | private/full ledger separation is enforced | same file path used for both ledgers | exit 1 |
| `test_duplicate_logical_run_requires_attempt_or_supersession` | duplicate run IDs are deterministic | repeated `run_id` without `attempt_id`/supersession | exit 1 |
| `test_duplicate_ledger_event_identity_fails` | duplicate ledger events are rejected | repeated event identity | exit 1 |
| `test_llm_wiki_index_entry_is_pointer_only` | quick-reference entry cannot become raw-content duplicate | index fixture with source facts but no provenance/freshness | exit 1 |
| `test_public_federal_frontmatter_requires_authority_and_license` | public federal page frontmatter includes required adjacent fields | missing `source_authority` or `license` | exit 1 |
| `test_citation_sidecar_requires_source_sibling_and_project` | citation sidecars include route identity | missing `source_sibling` | exit 1 |
| `test_legal_scan_evidence_required_for_public_publishable` | public state requires legal/security scan evidence | public bundle without scan evidence | exit 1 |
| `test_forged_or_stale_legal_scan_evidence_fails` | scan evidence must match command, deny-list hash, artifact hashes, timestamp, and exit code | mutated artifact after claimed scan pass | exit 1 |
| `test_legal_attestation_rejects_absolute_path` | legal attestation artifact paths cannot escape repo-relative form | `/tmp/source.yml` in attestation | exit 1 |
| `test_legal_attestation_rejects_traversal_path` | legal attestation artifact paths reject `..` traversal | `../private/source.yml` in attestation | exit 1 |
| `test_legal_attestation_rejects_symlink_path` | legal attestation rehashing refuses symlinked artifact paths | repo-relative symlink to outside fixture root | exit 1 |
| `test_legal_attestation_accepts_normalized_repo_relative_path` | legal attestation accepts a normal repo-relative POSIX path after rehashing | `tests/fixtures/ecosystem_wiki_flywheel/valid-public-bsee/run_manifest.yml` | exit 0 |
| `test_fixture_hashes_are_stable_under_gitattributes` | committed fixture files with recorded raw-byte hashes are LF-normalized by `.gitattributes`, including `.jsonl` | fixture paths checked with `git check-attr eol` and rehashed | exit 0 |
| `test_self_artifacts_are_validator_safe` | created plan, standard, templates, and valid fixtures do not block their own validator/legal checks | generated #2975 artifact paths | exit 0 |
| `test_invalid_fixtures_are_sentinel_scoped` | intentionally invalid fixtures are allowed only in fixture paths with explicit sentinel metadata | invalid fixture outside sentinel scope | exit 1 |
| `test_staged_publishing_order_is_machine_readable` | the BSEE -> FDAS -> HSE/marine staged publishing order and preconditions are encoded in the standard/config, not prose-only | fenced standard block missing a stage or prerequisite | exit 1 |
| `test_execution_and_report_schema_compatibility` | flywheel bundle composes existing execution/report schemas | valid bundle missing existing schema field | exit 1 |
| `test_report_layer_contract_accepts_public_federal_wiki` | existing architecture/report contract tests cover the additive schema enum without regressing existing public/private gates | `tests/architecture/test_report_layer_contract.py` with `public_federal_wiki` fixture | exit 0 |
| `test_source_class_name_collision_is_prevented` | existing report evidence `source_class` is not overloaded by flywheel publication class | `source_class: public-federal-data` in report evidence source | exit 1 |
| `test_private_wiki_page_reference_requires_public_wrapper_for_public_output` | stricter flywheel wrapper closes existing schema allowance for public `private-wiki-page` references | public output with unwrapped `private-wiki-page` | exit 1 |
| `test_private_wiki_page_wrapper_missing_each_gate_fails` | each wrapper field is independently required for public-safe projection | parameterized missing wrapper fields | exit 1 for each |
| `test_wrapper_uses_stable_source_id_not_array_index` | wrapper references bind to report-evidence `sources[].source_id`, not source array order | wrapper using `sources[0]` or reordered source fixture | exit 1 for ordinal, stable binding preserved after reorder |
| `test_enhanced_legal_attestation_uses_wrapper_field` | enhanced scan evidence does not violate existing `additionalProperties: false` legal scan schemas | extra keys inside existing `legal_scan` object | exit 1 |
| `test_generated_bundle_filenames_are_required` | real bundle validation uses canonical generated filenames, not `.example` names | bundle missing `run_manifest.yml` | exit 1 |
| `test_bundle_mode_rejects_example_filenames` | generated bundle validation cannot accidentally pass reusable examples | `.example` files in bundle mode | exit 1 |
| `test_template_mode_validates_example_filenames` | template validation mode checks `.example` files explicitly | template directory | exit 0 |
| `test_invalid_fixtures_use_synthetic_identifiers` | intentionally invalid fixtures avoid real deny-listed client/vendor names | invalid fixture with real deny-listed pattern | exit 1 |
| `test_legal_scan_passes_with_invalid_synthetic_fixtures` | intentionally invalid fixtures do not self-block legal scan when they use fabricated identifiers | invalid fixture set plus legal scan | exit 0 |
| `test_validator_json_output_is_deterministic` | repeated validation emits stable JSON ordering | same fixture twice | byte-identical JSON |

### Blocking Tests

The non-cuttable #2975 blocking subset is:

- `test_config_enum_file_is_source_of_truth`
- `test_standard_enum_table_matches_config`
- `test_unknown_enum_value_fails_closed`
- `test_missing_source_publication_class_fails_closed`
- `test_missing_license_terms_class_fails_closed`
- `test_open_public_source_classes_can_publish_with_open_license`
- `test_public_safe_flags_match_standard_subset`
- `test_each_non_public_safe_license_blocks_public_output`
- `test_public_source_with_private_license_blocks`
- `test_public_terms_review_required_blocks_publication`
- `test_public_federal_output_residency_routes_worldenergydata_wiki`
- `test_public_federal_cannot_route_to_generic_public_llm_wiki`
- `test_publication_state_matches_output_residency`
- `test_private_publication_state_is_deterministic`
- `test_public_review_state_policy_is_explicit`
- `test_private_approved_with_notes_requires_all_gates_resolved`
- `test_public_projection_is_allowlist_only`
- `test_public_projection_allowed_keys_are_exact`
- `test_public_projection_ids_match_public_identity_registry`
- `test_public_projection_string_values_are_denylist_scanned`
- `test_public_projection_destination_schema_is_closed`
- `test_quick_reference_rejects_private_source_facts`
- `test_public_to_private_markdown_link_fails`
- `test_full_and_public_ledgers_are_distinct_when_private_exists`
- `test_duplicate_logical_run_requires_attempt_or_supersession`
- `test_duplicate_ledger_event_identity_fails`
- `test_llm_wiki_index_entry_is_pointer_only`
- `test_public_federal_frontmatter_requires_authority_and_license`
- `test_citation_sidecar_requires_source_sibling_and_project`
- `test_legal_scan_evidence_required_for_public_publishable`
- `test_forged_or_stale_legal_scan_evidence_fails`
- `test_legal_attestation_rejects_absolute_path`
- `test_legal_attestation_rejects_traversal_path`
- `test_legal_attestation_rejects_symlink_path`
- `test_legal_attestation_accepts_normalized_repo_relative_path`
- `test_fixture_hashes_are_stable_under_gitattributes`
- `test_self_artifacts_are_validator_safe`
- `test_invalid_fixtures_are_sentinel_scoped`
- `test_staged_publishing_order_is_machine_readable`
- `test_execution_and_report_schema_compatibility`
- `test_report_layer_contract_accepts_public_federal_wiki`
- `test_source_class_name_collision_is_prevented`
- `test_private_wiki_page_reference_requires_public_wrapper_for_public_output`
- `test_private_wiki_page_wrapper_missing_each_gate_fails`
- `test_wrapper_uses_stable_source_id_not_array_index`
- `test_enhanced_legal_attestation_uses_wrapper_field`
- `test_generated_bundle_filenames_are_required`
- `test_bundle_mode_rejects_example_filenames`
- `test_template_mode_validates_example_filenames`
- `test_invalid_fixtures_use_synthetic_identifiers`
- `test_legal_scan_passes_with_invalid_synthetic_fixtures`
- `test_validator_json_output_is_deterministic`

Any deferral from this blocking subset must be recorded as a named follow-up issue before #2975 closeout and must not weaken public-output gating. Remaining tests in the table are hardening inventory and may be promoted to follow-up issues.

Explicit follow-up hardening tests, not blocking for #2975:

- `test_broken_wiki_target_fails`
- `test_stale_pointer_existing_target_fails`
- `test_stale_pointer_uses_reference_time`
- `test_two_clean_manual_runs_required_before_scheduling`
- `test_clean_run_requires_reviewed_generated_diff`

Required follow-up issues before #2975 closeout if not already filed by implementation:

| Follow-up title | Labels | Closeout trigger |
|---|---|---|
| `follow-up: ecosystem wiki flywheel hook and CI rollout` | `cat:automation`, `cat:data-pipeline`, `domain:knowledge` | Manual validator merged and green. |
| `follow-up: ecosystem wiki live sibling-link and stale-pointer validation` | `cat:data-pipeline`, `domain:knowledge` | Fixture-local link checks merged. |
| `follow-up: ecosystem wiki central ledger aggregation` | `cat:data-pipeline`, `domain:audit-trail` | Local ledger/public projection schema merged. |
| `follow-up: ecosystem wiki scheduled publishing enablement` | `cat:automation`, `domain:reports` | Two-clean-run fixture contract merged. |
| `follow-up: repo-qualified plan attestation for cross-repo issue links` | `cat:automation`, `domain:review` | #2975 documents same-repo attestation limitation. |

---

## Acceptance Criteria

- [ ] `docs/standards/ECOSYSTEM_WIKI_FLYWHEEL_CONTRACT.md` will define source publication classes, license/terms classes, publication states, review states, run identity fields, ledger event types, and clean-run criteria.
- [ ] The source/license/publication/review/ledger/scheduler enums will live in `config/ecosystem-wiki-flywheel/source-classification.yaml`, and unknown values will fail closed.
- [ ] Public-safe source and license flags will be read from `config/ecosystem-wiki-flywheel/source-classification.yaml`, and the validator will fail config validation unless those flags exactly match the standard-defined public-safe subsets `{public-federal-data, public-commercial-open, open-academic}` and `{public-domain, open-license}`.
- [ ] `docs/architecture/execution-manifest.schema.yaml` and `docs/architecture/report-evidence-bundle.schema.yaml` will add `output_residency: public_federal_wiki` for public-domain federal outputs routed to `worldenergydata-wiki`, while preserving existing enum values and fail-closed public-output rules.
- [ ] The standard doc enum section will include one fenced `yaml` block rooted at `ecosystem_wiki_flywheel_enums`, parsed by `test_standard_enum_table_matches_config` and compared exactly against the config enum file to prevent brittle Markdown-table parsing.
- [ ] The standard will keep existing `report-evidence-bundle.schema.yaml` `sources[].source_class` semantics intact and will add `source_publication_class` only as a separate publication-safety classification.
- [ ] `docs/governance/2026-06-08-ecosystem-wiki-flywheel-routing-decision.md` will explain why the standard composes existing layer/routing/citation contracts instead of replacing them.
- [ ] Templates will exist for run manifest, JSONL history record, wiki frontmatter, routing ledger event, public ledger projection, quick-reference index entry, and insight-bundle metadata.
- [ ] Validator tests will be written before implementation and will cover the blocking MVP subset from the worldenergydata adversarial decision review; broader hardening tests will remain documented for follow-up promotion.
- [ ] `scripts/enforcement/check-ecosystem-wiki-flywheel.py` will validate the #2975 MVP subset: provenance completeness, public/private contamination, citation coverage, duplicate run/history semantics, duplicate ledger events, public projection schema, and fixture-local wrapper gates.
- [ ] The standard will define stale quick-reference pointer and scheduler-clean-run requirements as future hardening criteria; full live enforcement for those checks will be follow-up work and not a #2975 validator acceptance condition.
- [ ] The validator will compose `docs/architecture/execution-manifest.schema.yaml` and `docs/architecture/report-evidence-bundle.schema.yaml` with PyYAML and `jsonschema` `Draft202012Validator`; it will not create incompatible replacements for `input_residency`, `output_residency`, or `promotion_gates`.
- [ ] The validator implementation will split concerns under `scripts/enforcement/ecosystem_wiki_flywheel/` so the top-level CLI stays thin and each policy surface has focused tests.
- [ ] Existing closed-schema `legal_scan_evidence` / `legal_scan` fields will still carry their required `command` and `result` values; enhanced scan evidence will live only in the flywheel wrapper field.
- [ ] Enhanced legal/security scan attestation will live in a new flywheel wrapper field and will use the canonicalization/window rules specified in this plan.
- [ ] Public publication will require `source_publication_class` in `{public-federal-data, public-commercial-open, open-academic}` and `license_terms_class` in `{public-domain, open-license}`; all other combinations will fail closed for public output.
- [ ] Public publication will require `review_state: approved`; `approved-with-notes` will be allowed only for private targets when `approved_with_notes_gate_status: all-gates-resolved`.
- [ ] `source_class: private-wiki-page` in existing report evidence will require the flywheel wrapper fields listed in this plan before any public output can pass.
- [ ] `llm-wiki` quick-reference entries will be defined as pointer/index artifacts only, with classification and freshness metadata, and will not duplicate raw source content.
- [ ] Public sanitized ledger projections will be explicitly separated from private/full ledgers.
- [ ] Public sanitized ledger projections will be allowlist-only using the exact key schema in this plan and will reject client/project identifiers, private repo URLs, private issue URLs, local absolute paths, raw source snippets, citation sidecar paths, log paths, private artifact paths, private source titles, deny-list hits inside allowed string values, unlisted nested keys, arbitrary URLs, and free-text summary fields.
- [ ] The standard will include a public-egress threat-model checklist that maps every exposed field in the public projection/frontmatter/quick-reference surfaces to at least one blocking test.
- [ ] Public projection `destination` will be a closed `repo`/`path`/`visibility` object with allowlisted repo names and normalized repo-relative paths; arbitrary external URLs will be out of scope for the #2975 MVP.
- [ ] The staged publishing order will be encoded in the standard/config and validated by a blocking test: public BSEE/federal first; FDAS only after classification and citation coverage; HSE/marine only after segregation, redaction, and legal/security checks.
- [ ] The standard will document that weekly/scheduled publishing requires two clean manual runs, where clean means no extraction errors, no citation gaps, no private contamination, deterministic manifest/history writes, no duplicate ledger entries, no broken wiki links, legal/security scan pass when applicable, and reviewed generated diffs; scheduler enablement remains follow-up work.
- [ ] Invalid fixtures will use fabricated identifiers only. Fixture sentinels may mark intentionally-invalid validator scenarios but will not bypass legal/security scans.
- [ ] Validator JSON output will not include wall-clock runtime values; deterministic output will use only fixture/bundle-derived timestamps and hashes. Follow-up stale-pointer checks will use fixture/bundle-derived `reference_time`, not wall clock.
- [ ] The standard will preserve issue -> plan -> adversarial review -> user approval -> TDD -> implementation -> code/artifact review for every consuming repo.
- [ ] The standard will define the backlink contract for worldenergydata #450-#453; actual issue comments/edits after implementation lands are follow-up operational closeout, not a blocking code deliverable for the #2975 validator PR, and will re-check issue state at closeout time.
- [ ] Required follow-up issue titles, labels, and closeout triggers listed in this plan will be filed or linked before #2975 closes if their enforcement is not included in the implementation PR.
- [ ] #2975 will land manual validator invocation and tests only; hook/CI rollout will be split to a follow-up issue after the standard and validator are approved.
- [ ] Verification will pass: `uv run pytest tests/enforcement/test_check_ecosystem_wiki_flywheel.py -v`.
- [ ] Existing architecture/report schema verification will pass after the `public_federal_wiki` enum extension: `uv run pytest tests/architecture/test_report_layer_contract.py -v`.
- [ ] Relevant existing enforcement tests will pass: `uv run pytest tests/enforcement/test_check_wiki_sibling_frontmatter.py -v`.
- [ ] Legal/security scan will pass: `scripts/legal/legal-sanity-scan.sh`.

---

## Adversarial Review Summary

Subagent adversarial review has been completed for the decision/plan content. Formal provider review on 2026-06-08 returned MAJOR, and 2026-06-09 r2/r3/r4/r5/r6/r7/r8 repair reviews also returned MAJOR/NO_OUTPUT. Implementation remains blocked until the scope decision below is resolved, fresh no-MAJOR review passes, explicit user approval is given, and `status:plan-approved` is applied by the user.

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
| Subagent Schrodinger r2-prep | MAJOR | deterministic publication-state table, exact `license_terms_class`, private-wiki wrapper schema, bundle/template mode mapping, synthetic fixtures, fresh r2 evidence, and missing tests required |
| Claude/Codex/Gemini 2026-06-09 stale rerun | MAJOR/NO_OUTPUT | run happened before the r2-prep repair; kept as historical evidence only |
| Claude/Codex/Gemini r2 | MAJOR/NO_OUTPUT | repo-qualified evidence, MVP scope, legal attestation, schema composition, public projection, approved-with-notes, and backlink scope gaps |
| Subagent Leibniz final blocker sweep | APPROVE | no blocker-level findings after r2 repairs |
| Claude/Codex/Gemini r3 | MAJOR/NO_OUTPUT | legal-scan tests not in blocking floor, enum sync mechanism ambiguity, incomplete evidence list, soft scope cuts, standards index shape |
| Claude/Codex/Gemini r4 | MAJOR/NO_OUTPUT | cross-repo state dependency, AC/blocking-test mismatch, wrapper location/order, real-run timestamp anchoring, follow-up issue specificity, validator complexity |
| Claude/Codex/Gemini r5 | MAJOR/NO_OUTPUT | cross-repo decision-source ambiguity, approved-with-notes classifier input, stale/scheduler follow-up boundary, legal-scan rehashing, ledger identity, TDD sequencing, stale attestation hash |
| Claude/Codex/Gemini r6 | MAJOR/NO_OUTPUT | public-federal output residency missing, public projection value-level leakage, staged publishing order untested, public-safe config invariant, legal-attestation path tests, destination schema |
| Claude/Codex/Gemini r7 | MAJOR/NO_OUTPUT | shared-schema regression verification, positive public identity registry, fixture hash line-ending stability, stale/scheduler scope contradictions, public projection destination semantics, staged publishing schema |
| Claude/Codex/Gemini r8 | MAJOR/NO_OUTPUT | classifier still allowed federal data to generic public llm-wiki, private-corpus output residency mismatch, schema-consumer enumeration missing, `.gitattributes` blast-radius wording, symlink component-depth, BSEE-only MVP, append-only scope, enum/config block scope, and single-PR validator reviewability |

**Overall result:** FAIL through r8; plan remains draft-r8-major-needs-scope-decision until the user chooses whether #2975 stays one large implementation plan or splits into staged child plans.

### Scope Decision Required

r8 review converged on a scope/reviewability blocker. The recommended path is to split #2975 into staged child plans:

1. Phase A / #2975: standard, governance decision, config, templates, additive `public_federal_wiki` schema enum, enum/config generation or sync check, and existing schema regression verification.
2. Phase B / child issue: manual validator, helper modules, fixtures, blocking public-egress/legal/wrapper/ledger tests, deterministic output, and follow-up issue filing.
3. Phase C / child issues already listed: live sibling-link/stale-pointer validation, hook/CI rollout, central ledger aggregation, and scheduled publishing enablement.

Keeping all 50+ blocking validator tests plus schema edits/templates/docs in one approval unit is technically possible but has produced repeated MAJOR review findings and high implementation-review risk. The next review should happen only after this split-or-keep decision is applied.

Revisions made based on review:
- Added existing execution/report schema reconciliation and issue-class resource-intel sources.
- Added required enum contract and fail-closed unknown-value behavior.
- Made public ledger projections allowlist-only.
- Added legal scan freshness/hash/deny-list evidence checks.
- Added self-artifact, invalid-fixture sentinel, and existing-schema compatibility tests; stale-pointer, two-clean-run, and reviewed-diff tests are now explicitly follow-up hardening, not #2975 blocking tests.
- Scoped #2975 to manual validator plus tests; hook/CI rollout will be a follow-up issue.
- Renamed the new classification field to `source_publication_class` to avoid overloading existing report evidence `source_class`.
- Moved enhanced legal scan attestation into a flywheel wrapper field instead of extending existing closed `legal_scan` objects.
- Moved enum source of truth from `tests/fixtures/` to config-tier `config/ecosystem-wiki-flywheel/source-classification.yaml`.
- Added public-source and license-term allowlist logic.
- Added wrapper rule for existing report evidence `source_class=private-wiki-page` in public outputs.
- Split generated bundle filenames from `.example` template validation mode.
- Added synthetic-fixture and deterministic-output constraints.
- Added deterministic publication-state table tied to `output_residency` and `review_state`.
- Added config-driven public-safe source/license subset requirement.
- Added exact wrapper fields for public use of `private-wiki-page` report-evidence references.
- Added deterministic `reference_time` handling for stale pointers and legal scan freshness.
- Added repo-qualified local `gh --repo vamseeachanta/worldenergydata` transcript for #450-#453.
- Added exact standards README shape and all create-targets to evidence.
- Made public-output legal scan required/forgery tests part of the non-cuttable blocking floor.
- Replaced soft budget language with named-follow-up requirement for any blocking-test deferral.
- Chose a concrete enum sync mechanism: fenced machine-readable standard block parsed and compared against config.
- Removed live `worldenergydata` issue state as an implementation gate; issue state is re-checked only at backlink closeout time.
- Added exact flywheel wrapper location in `insight_bundle_metadata.yml` and validation order.
- Added non-fixture `reference_time_source` policy path.
- Added helper-module split under `scripts/enforcement/ecosystem_wiki_flywheel/`.
- Added required follow-up issue titles, labels, and closeout triggers.
- Added additive `public_federal_wiki` schema extension for `worldenergydata-wiki` public-domain federal outputs.
- Replaced editable public-safe config policy with invariant tests against the standard-defined public-safe source/license subsets.
- Added value-level deny-list scanning for public projection string values and a closed repo/path/visibility destination schema.
- Promoted self-artifact, sentinel, legal path-hardening, staged-order, and stable wrapper-source-ID checks into the blocking floor.
- Added positive public identity registry and pattern checks for public projection IDs.
- Split stale-pointer/link and scheduler readiness into standard-only definitions plus follow-up live enforcement.
- Added shared schema regression verification, `.jsonl` LF fixture stability, public-egress threat-model checklist, staged publishing YAML schema, and helper-module review map.

---

## Risks and Open Questions

- **Risk:** The new standard could duplicate `.claude/rules/wiki-sibling-routing.md`. The implementation will reference it as routing authority and only add the missing manifest/history/ledger/index layer.
- **Risk:** A validator that scans staged content could block its own fixtures/templates. The TDD suite will include self-artifact compatibility and fixture-local sentinel tests before any hook wiring follow-up is proposed.
- **Risk:** `llm-wiki` quick-reference index entries could leak private artifacts by naming paths, clients, projects, or source facts. The public projection template and validator will reject those fields in public projections.
- **Risk:** Public federal data publishing could drift as source terms change. Templates will require `source_authority`, `license_terms_class`, retrieval timestamp, and last license/terms check.
- **Risk:** Existing worldenergydata issues could be edited prematurely. This issue will only add backlinks after the standard is created and verified.
- **Risk:** The MVP validator is still broad enough to become difficult to review. Mitigation: keep the CLI thin, split concerns under `scripts/enforcement/ecosystem_wiki_flywheel/`, keep live scans/hooks/network checks out of #2975, and require each helper surface to have focused tests.
- **Risk:** The standard and config both carry enum data. Mitigation: config is the single writer; the standard carries a copied fenced block only for human-readable docs, and `test_standard_enum_table_matches_config` fails any drift.
- **Resolved recommendation:** #2975 will include manual validator invocation and tests only. Hook/CI rollout will be split to a follow-up issue after this standard and validator land.
- **Resolved recommendation:** `source_publication_class` and related license/publication/review/ledger/scheduler enums will live in `config/ecosystem-wiki-flywheel/source-classification.yaml`; the standard's fenced machine-readable enum block will be parsed and compared exactly against that config source of truth.
- **Resolved recommendation:** `docs/plans/2026-06-02-issue-2945-repo-ecosystem-flywheel.md` is not present on the current branch; implementation will reference live issue/PR evidence for #2945 only if needed instead of citing a missing local plan.

---

## Complexity: T3

**T3** — cross-repo governance standard with templates, validator, tests, wiki/public-private routing implications, and downstream consumers across `worldenergydata`, `llm-wiki`, `worldenergydata-wiki`, and future sibling wikis.
