# Plan for #3533: Standards registry authority contract

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3533
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** `scripts/review/results/2026-07-14-plan-3533-claude.md` | `scripts/review/results/2026-07-14-plan-3533-codex.md` | `scripts/review/results/2026-07-14-plan-3533-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `data/design-codes/code-registry.yaml:19-28` currently represents DNV-RP-C203 with `our_edition: "2016-04"`, `latest_known_edition: "2024-07"`, and `status: check`; those names conflate an implementation basis with publisher currentness.
- `data/document-index/standards-transfer-ledger.yaml:2045-2060` currently marks BS-7608 `done` with empty `doc_path` and `doc_paths`. The ledger has no DNV-RP-C203 row. A YAML parse on 2026-07-14 finds 142 of 435 `done` rows without either path, 436 of 436 rows without `doc_key`, and no per-row provenance or rights state.
- `scripts/data/document-index/build-ledger.py:193-247,268-353` currently derives `done` from upstream `implemented` state or a completed work item and rewrites the whole YAML from a legacy-only mapping. An unmodified generator would erase hand-added enrichment.
- `scripts/document-intelligence/batch-process-standards.py:134-177` currently excludes `done` rows and can mark a candidate `done` without a positive file-existence result. `tests/document-intelligence/test_marine_standards_batch.py:179-215` currently encodes that behavior.
- `scripts/readiness/code-version-guard.sh:35-116` currently uses a scalar-only parser, checks four legacy keys, reports informational output, and exits zero. Nested canonical fields would be invisible without a consumer migration.
- `query-ledger.py`, `generate-coverage-report.py`, `scripts/knowledge/doc-key-lookup.py`, `scripts/document-intelligence/cross-reference-registries.py`, and `marine-taxonomy-classifier.py` consume legacy transfer state and/or paths. `scripts/data/research-literature/research-domain.py` maps several transfer states to `available`; `scripts/data/generate-domain-resource-views.py` renders `done` as acquired. These consumers will migrate or explicitly retain transfer-only behavior.

### Standards and source authority

| Standard | Publisher-current metadata | Local evidence boundary | Registry defect |
|---|---|---|---|
| DNV-RP-C203 | [Official DNV catalog](https://www.dnv.com/energy/standards-guidelines/dnv-rp-c203-fatigue-design-of-offshore-steel-structures/): edition 2024-10, amended 2025-10; publisher-catalog evidence retrieved 2026-07-14 | Reachable filenames support 2000, 2005, 2008, 2010, and 2011 only. Filenames do not prove designation, lawful access, rights, or technical fitness. | Code registry states 2016-04 / 2024-07; ledger has no row. |
| BS 7608 | [Official BSI catalog](https://knowledge.bsigroup.com/products/guide-to-fatigue-design-and-assessment-of-steel-products): BS 7608:2014+A1:2015 is Current; publisher-catalog evidence retrieved 2026-07-14 | Reachable filenames support 1993, 1993+A1:1995, and a file named 2014. The 2014 filename does not prove A1:2015. | Ledger says `done` with no paths and no exact identity. |

Official catalog metadata will establish publisher identity and currentness only. It will not establish numerical content, clause locators, possession, access authority, reuse rights, or qualified technical acceptance.

### LLM Wiki pages consulted

- [llm-wiki DNV resolver](https://github.com/vamseeachanta/llm-wiki/blob/main/wikis/engineering-standards/wiki/standards/dnv-rp-c203.md) currently labels revision 2024-10 while naming only a 2011 local source; it will remain resolver metadata rather than source authority.
- [llm-wiki legacy DNV page](https://github.com/vamseeachanta/llm-wiki/blob/main/wikis/engineering/wiki/standards/dnv-rp-c203.md) currently lacks resolver identity fields.
- BS 7608 pages currently mix 1993, 1993+A1, and 2014 identities. Their repair belongs to [llm-wiki #837](https://github.com/vamseeachanta/llm-wiki/issues/837), not this registry issue.

### Documents and issues consulted

- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md:64-190,407-419` defines `doc_key` as namespaced content identity, paths as aliases, edition-changing content as a new identity, minimum provenance, and ledger `status` as transfer state rather than processing/access/rights state.
- `docs/reports/intelligence-metric-source-of-truth-map.md:8-31` makes ledger totals and per-row transfer state canonical metrics; migration will therefore preserve transfer semantics and update downstream counts explicitly.
- `data/document-index/intelligence-accessibility-registry.yaml:218-268` records asset-level reachability and is already stale at 425 ledger records versus 436 live rows; it cannot stand in for record-level verification.
- `config/drive-index-registry.yml:48-97` records the O&G inventory as 2025-12-28 with no refresh and the frozen master index as 2026-04-17. Those catalogs will remain discovery evidence only.
- [#2207](https://github.com/vamseeachanta/workspace-hub/issues/2207) owns the existing provenance contract; [#2250](https://github.com/vamseeachanta/workspace-hub/issues/2250) owns canonical ledger metrics.
- Open [#2362](https://github.com/vamseeachanta/workspace-hub/issues/2362) proposes broad `doc_key` backfill and an `unreachable` ledger status. #3533 will not absorb the broad backfill and will prevent access/reachability from overloading transfer state. #2362 will require re-planning against this contract before parallel implementation.
- [#3538](https://github.com/vamseeachanta/workspace-hub/issues/3538) will own any amendment or exact-source extension to the calculation citation contract.

### Gaps identified

- No machine-validated schema currently separates publisher currentness, holdings, access, reuse rights, qualified technical review, and transfer state.
- No durable producer path currently round-trips per-standard enrichment through a ledger rebuild.
- No validator currently rejects malformed content identities such as a 32-hex digest mislabeled `sha256:`. A machine-local, gitignored `data/document-index/index.jsonl` sample contains this defect class; CI will use a hermetic synthetic fixture instead.
- No consumer currently calculates “usable for engineering” from all required evidence while keeping legacy transfer metrics distinct.
- No existing artifact establishes lawful access, reuse rights, or qualified acceptance for the DNV-RP-C203 or BS 7608 holdings. Those values will remain `unknown` or `pending`.

### Evidence (embedded verification)

**Issue status, verified 2026-07-14:** #3533, #2362, #2363, and #3538 are OPEN; #2207 and #2250 are CLOSED.

**Empirical record checks:** a safe YAML parse returns 436 ledger rows, 435 with `status: done`, 142 `done` rows without either path, zero rows with `doc_key`, and no DNV-RP-C203 row. The BS-7608 row is `done` with empty paths.

**Reproduction proof:** N/A — this is a governance/schema defect. The contradictory live records and generator/consumer excerpts above are the executable resource-state evidence.

**Distinct sources:** issue #3533; two canonical YAML registries; five producer/consumer scripts; provenance contract; metric map; accessibility registry; drive registry; llm-wiki resolver pages; publisher catalogs; related issues.

---

## Decision Model and Ownership

The implementation will keep four independent questions explicit:

1. **Publisher currentness** — official designation, edition, amendment, catalog evidence, and verification time.
2. **Local holding** — exact content identity when hashed, asserted designation, source/host/path aliases, reachability result, and verification time.
3. **Access and purpose-scoped permissions** — access authorization will remain separate from permission for internal calculation use, metadata storage, derived numeric outputs, and text/table reproduction. Possession or subscription will imply none of them. The existing provenance contract's term “reuse” will remain reserved for reusing L2 outputs instead of reparsing L1; this schema will not overload it as a legal-rights verdict.
4. **Qualified technical review** — accepted/rejected/pending status against an exact basis identity, decision reference, time, and reviewer role. Currentness or possession will not imply fitness for calculations.

`code-registry.yaml` will own public-safe logical code identity, publisher-current metadata, implementation basis, and an opaque pending/blocked authority state. The transfer ledger will own transfer history and public-safe discovery aliases. Exact holdings, fingerprints, access evidence, permissions, and qualified-review evidence will not enter this public repository; private-registry ownership will be planned under [llm-wiki #840](https://github.com/vamseeachanta/llm-wiki/issues/840). Both layers will reuse the existing `doc_key` contract where exact private holdings exist.

Legacy `our_edition`, `latest_known_edition`, and `status` fields will remain read-compatible mirrors for one migration wave. The canonical nested fields will define their meaning, and validation will require mirror equality. Ledger `status` will remain transfer state; it will never encode access, rights, publisher currentness, or technical review.

Transfer completion and engineering usability will use independent evidence. A new transfer will reach `done` only with a positive destination alias plus content identity/reconciliation evidence; it will not require technical acceptance or use permission. Existing `done` rows without that evidence will keep their historical transfer value and receive `transfer_evidence_status: legacy-unverified`; they will not count as verified transfers or engineering-usable records. No migration will rewrite their history to an access or processing status.

Two joins will be explicit. Logical publisher records will join only by canonical edition-independent `code_id`. A holding, access assertion, permission assertion, or accepted technical basis will join only by the full namespaced `doc_key` plus asserted revision/amendment; code ID alone will never attach current metadata to an older edition.

The public cross-repo interface name/version will be finalized by this implementation rather than pre-authorized downstream. Its allowlist will expose only canonical code identity, official publisher metadata, evidence URL/time/type, and `resolution_gate: blocked | metadata-only`. It will expose no fingerprint, holding, path, access fact, permission decision, reviewer state, or private evidence reference. LLM-wiki #837 will consume the landed schema through an adapter. Missing, stale, unsupported-version, or identity-mismatched records will fail closed.

### Concrete public schema

```yaml
schema_version: "1"
standard_identity: {code_id: <canonical id>, publisher: <publisher>}
publisher_current:
  designation: <publisher designation>
  edition: <quoted value or unknown>
  amendment: <quoted value or none/unknown>
  lifecycle: current | withdrawn | superseded | unknown
  evidence: {kind: publisher_catalog, url: <official URL>, verified_at: <RFC3339>}
implementation_basis:
  edition: <quoted value or unknown>
  amendment: <quoted value or none/unknown>
  evidence_ref: <public decision reference or none>
transfer:
  legacy_status: <existing status>
  evidence_status: verified | legacy-unverified | not-applicable
resolution_gate: blocked | metadata-only
private_authority_state: private-record-required | not-applicable
```

The schema will be closed. Dates will be quoted RFC3339 values. Edition/amendment chronology will use explicit publisher dates/evidence, never lexical string order. `unknown`, `none`, and `not-applicable` will remain distinct. A historical qualified decision stored privately will remain valid against its exact `doc_key` if a mount later becomes unreachable; current usability will be a separate transient derivation.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Plan | `docs/plans/2026-07-14-issue-3533-standards-registry-authority-contract.md` |
| Human review companion | `docs/plans/2026-07-14-issue-3533-standards-registry-authority-contract.html` |
| Registry schema | `data/design-codes/standards-registry.schema.json` |
| Curated enrichment input | `data/document-index/standards-authority-metadata.yaml` |
| Public cross-repo schema/export | `data/design-codes/standards-authority-public.schema.json`; `data/design-codes/standards-authority-public.json` |
| Validator | `scripts/data/document-index/validate-standards-registries.py` |
| Tests | `tests/data/document-index/test_standards_registry_contract.py` |
| Review artifacts | `scripts/review/results/2026-07-14-plan-3533-{claude,codex,gemini}.md` |

---

## Deliverable

A versioned, machine-validated standards-record contract and producer/consumer migration will distinguish publisher currentness, exact holdings, access, rights, technical acceptance, and transfer state without claiming facts that available evidence does not establish.

---

## Pseudocode

```text
function validate_record(record, registry_kind):
    validate schema version and allowed state vocabularies
    validate publisher-current evidence independently from holdings
    for each holding:
        validate namespaced digest shape; never cross-join digest namespaces
        require designation assertion and verification metadata
        keep reachability, access, and each purpose-scoped permission independent
    if technical review is accepted:
        require exact basis doc_key, decision_ref, reviewer_role, reviewed_at
        validate the historical decision against its exact identity
    validate deprecated mirrors equal canonical values

function build_ledger(base_sources, curated_authority_metadata, as_of, output_path):
    reject normalized-id collisions and orphan curated records
    generate deterministic legacy transfer rows using injected as_of
    join logical metadata by canonical code_id
    join holding/review evidence only by full doc_key plus revision/amendment
    never synthesize evidence, doc_key, access, rights, or acceptance
    reject destructive overwrite of unmatched curated metadata
    validate candidate before write
    on dry run, emit candidate to output_path without mutating canonical file
    on apply, fsync a temporary sibling and replace atomically

function derive_engineering_usability(public_record, private_record):
    return true only when private exact identity, current reachability, authorized access,
        required purpose-scoped internal use, and accepted qualified review all pass
    report transfer status separately

function derive_transfer_evidence(record):
    preserve historical status only in legacy_status
    verify new completion only from destination alias plus content reconciliation
    classify evidence-free historical completion as legacy-unverified
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `data/design-codes/standards-registry.schema.json` | Define the first canonical schema, enums, evidence, and constraints. |
| Create | `data/design-codes/standards-authority-public.schema.json` | Define the disclosure-minimized public #3533 → #837 interface. |
| Create | `data/design-codes/standards-authority-public.json` | Publish publisher metadata and blocked state only. |
| Create | `data/document-index/standards-authority-metadata.yaml` | Provide a curated, generator-safe enrichment input rather than hand-edit-only state. |
| Create | `scripts/data/document-index/validate-standards-registries.py` | Validate both registries and derived usability fail closed. |
| Create | `tests/data/document-index/test_standards_registry_contract.py` | Add hermetic contract, migration, generator, and consumer tests before implementation. |
| Modify | `data/design-codes/code-registry.yaml` | Add schema version and evidence-bounded C203 publisher/current, implementation-basis, and pending-review data. |
| Modify | `data/document-index/standards-transfer-ledger.yaml` | Regenerate using the approved schema; preserve transfer state while adding evidence-bounded selected records. |
| Modify | `scripts/data/document-index/build-ledger.py` | Deterministically merge curated enrichment and validate pre/post write. |
| Modify | `scripts/document-intelligence/batch-process-standards.py` | Require destination/content evidence for new transfer completion; keep usability separate. |
| Modify | `scripts/data/document-index/query-ledger.py` | Expose transfer, holding, access, rights, review, and usability as distinct filters/output. |
| Modify | `scripts/data/document-index/generate-coverage-report.py` | Report transfer coverage separately from engineering usability. |
| Modify | `scripts/document-intelligence/cross-reference-registries.py` | Replace “publish candidate” claims when authority is unknown with neutral reconciliation output. |
| Modify | `scripts/knowledge/doc-key-lookup.py` | Read canonical holding arrays safely without treating transfer as authority. |
| Modify | `scripts/document-intelligence/marine-taxonomy-classifier.py` | Consume schema-versioned fields without changing classification semantics. |
| Modify | `scripts/data/research-literature/research-domain.py` | Stop mapping transfer state directly to source availability. |
| Modify | `scripts/data/generate-domain-resource-views.py` | Render transfer, possession, and usability separately. |
| Modify | `scripts/readiness/code-version-guard.sh` | Consume validated nested fields while preserving a documented warn-only startup mode. |
| Modify | `tests/document-intelligence/test_marine_standards_batch.py` | Replace unsafe completion expectations with evidence-gated behavior. |
| Modify | `docs/reports/intelligence-metric-source-of-truth-map.md` | Define separate canonical metrics and migration effects. |
| Modify | `data/document-index/intelligence-accessibility-registry.yaml` | Refresh asset record count and point to the validated contract without implying per-row rights. |
| Create | `docs/plans/2026-07-14-issue-3533-standards-registry-authority-contract.html` | Provide the HTML-default review artifact and visual QA target. |
| Existing | `docs/plans/README.md` | Draft row exists; its status will update after review. |

---

## TDD Test List

| Test | Verification |
|---|---|
| `test_done_transfer_state_does_not_imply_usable` | A legacy `done` row without exact holding/evidence remains non-usable and is reported separately. |
| `test_legacy_done_preserves_history_but_is_unverified` | Historical `done` remains transfer history and receives `legacy-unverified`; it is not silently rewritten. |
| `test_new_transfer_done_requires_destination_identity` | New transfer completion requires positive destination alias plus reconciled content identity, not rights/technical review. |
| `test_publisher_update_does_not_create_holding_claim` | Publisher-current metadata cannot synthesize possession, access, rights, or review. |
| `test_edition_chronology_and_amendment_parent` | Impossible dates and amendments without their parent edition fail. |
| `test_filename_does_not_promote_amendment` | `BS_7608-2014.pdf` cannot become 2014+A1:2015; C203 2011 cannot become 2016/2024/current amendment. |
| `test_stale_index_and_wiki_are_discovery_only` | Stale indexes and resolver pages cannot promote authority states. |
| `test_access_and_permissions_are_independent` | Subscription/local reachability cannot imply any purpose-scoped permission. |
| `test_permissions_are_purpose_scoped` | Internal calculation, metadata storage, derived numeric output, and text/table reproduction remain separate and default unknown. |
| `test_accepted_review_requires_exact_basis` | Acceptance requires exact `doc_key`, identity, decision reference, reviewer role, and compatible evidence states. |
| `test_digest_namespace_validation` | `md5:` plus 32 hex and `sha256:` plus 64 hex pass; pseudo-SHA-256 with 32 hex fails; namespaces never join. |
| `test_generator_round_trip_preserves_enrichment` | Rebuilds preserve validated curated fields and deterministic ordering. |
| `test_generator_injected_clock_and_repeated_bytes` | Two builds with identical inputs/as-of are byte-identical. |
| `test_generator_atomic_replace_and_interruption` | Failed validation/write never changes the canonical ledger. |
| `test_generator_rejects_orphan_and_id_collision` | Orphan curated records and normalized-ID collisions fail closed. |
| `test_multi_edition_join_never_uses_code_id_for_holding` | Current publisher metadata cannot attach to an older holding; exact evidence joins by doc_key plus designation. |
| `test_generator_cannot_synthesize_completion_evidence` | `implemented` sources or completed work items cannot create holding/access/right claims. |
| `test_legacy_mirrors_equal_canonical_fields` | Old readers remain compatible for one wave and inconsistent mirrors fail validation. |
| `test_batch_requires_positive_transfer_evidence` | Batch cannot mark a new transfer complete without destination/content evidence; authority remains separate. |
| `test_reports_separate_transfer_from_usability` | Query, coverage, and readiness outputs do not conflate metrics. |
| `test_authority_export_contract` | Export is deterministic, path-free, licensed-content-free, versioned, and compatible with the #837 fixture. |
| `test_public_export_disclosure_allowlist` | Export has no doc_key, holding, path, access/permission/review fact, or private evidence reference. |
| `test_research_and_domain_views_do_not_infer_availability` | Research/resource views separate transfer history from possession/usability. |
| `test_cross_reference_never_implies_publish_rights` | Unknown-rights rows are reconciliation candidates, never publish candidates. |
| `test_records_contain_metadata_only` | Schema rejects licensed body text, OCR/table payload fields, and embedded coefficient datasets. |

---

## Acceptance Criteria

- [ ] TDD will begin with the tests above failing for the documented reasons.
- [ ] Implementation preflight will extend sparse checkout with `scripts/document-intelligence scripts/knowledge` and every named consumer before edits.
- [ ] `uv run --group dev pytest tests/data/document-index/test_standards_registry_contract.py tests/document-intelligence/test_marine_standards_batch.py tests/document-intelligence/test_cross_reference.py -v` plus focused tests for every migrated consumer will pass.
- [ ] The validator will pass both canonical registries and fail every negative fixture.
- [ ] A dry run with injected `as_of` will emit a candidate artifact; repeated runs will be byte-identical, and atomic replacement will prevent partial writes.
- [ ] Historical evidence-free `done` rows will retain transfer history as `legacy-unverified`; new `done` transitions will require destination/content evidence but not technical acceptance or use permission.
- [ ] DNV-RP-C203 will record official publisher currentness separately from filename evidence. No holding row will be created until exact private evidence exists; no public access/permission/review fact will be emitted.
- [ ] BS 7608 will not claim A1:2015 possession from a 2014 filename and will not be engineering-usable from an empty-path `done` row.
- [ ] Transfer counts and engineering-usability counts will be separately named and documented.
- [ ] No wiki page, index status, path, possession, or subscription will be treated as reuse authority.
- [ ] Permission fields will be purpose-scoped and default to unknown; the provenance contract's L2 “reuse” term will not be redefined as a legal clearance.
- [ ] Logical identity will join by canonical `code_id`; holdings, permissions, and accepted bases will join by full `doc_key` plus exact designation.
- [ ] The public export will use its approved final name/version and disclosure allowlist; consumers will fail closed on missing, stale, mismatched, or unsupported versions.
- [ ] No licensed text, tables, OCR bodies, or coefficient datasets will enter tracked artifacts.
- [ ] #2362 will remain without `dispatch:ready`; its coordination comment will link this plan, and it will be re-planned before overlap.
- [ ] #3538 and llm-wiki #837 will remain separate owners of citation-contract and resolver changes.
- [ ] `scripts/legal/legal-sanity-scan.sh` and the relevant repository test suite will pass.
- [ ] T3 code/artifact review will obtain three-provider adversarial coverage or will explicitly record provider unavailability and residual risk.
- [ ] The HTML companion will render without overflow, broken links, or private-path leakage and will receive visual QA.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR (round 1) | Corrected phantom paths, sparse scope, missing consumers, test command, and HTML artifact. |
| Codex | MAJOR (round 1) | Closed schema, transition, provenance, C203, determinism/atomicity, and consumer gaps. |
| Gemini | UNAVAILABLE | No non-interactive authentication; no review signal. |

**Overall result:** FAIL in round 1; revised draft is undergoing round-2 review and remains `status:needs-plan`.

Round-1 revisions will use the public disclosure allowlist, private-evidence issue #840, concrete schema, exact script paths, complete consumer inventory, injected-clock dry runs, atomic replacement, chronology/collision tests, executable `uv` commands, and HTML visual QA.

---

## Risks and Human Decisions

- **Human decision:** approval of this plan will authorize only generic schema/producer/consumer work and conservative metadata migration. It will not authorize a DNV numerical basis or licensed-source inspection.
- **Human decision:** any `technical_review.status: accepted` transition will require a qualified reviewer and evidence reference outside automated inference.
- **Risk:** open #2362 can race or overwrite identity work. Its implementation will remain blocked/re-planned until ownership and schema compatibility are explicit.
- **Risk:** a full-file ledger generator can destroy enrichment. Pre/post validation, deterministic merge input, atomic write, and round-trip tests will be acceptance gates.
- **Risk:** changing `done` semantics would corrupt canonical metrics. The migration will preserve transfer state and introduce separately named usability metrics.
- **Risk:** rights evidence may remain unavailable. The system will preserve `unknown` rather than relaxing the gate.
- **Privacy gate:** exact holdings, fingerprints, access, permissions, and qualified-review evidence will not enter public workspace-hub artifacts. Their private canonical home requires separately approved llm-wiki #840.
- **Dependency order:** #3533 will publish schema plus pending/unknown records; #839 and #3538 will establish page/source and citation blocked-state contracts; #837 Stage A will install blocked identities; a qualified #1588 basis decision will precede accepted-review recording and #837 activation; only then will #1588 calculation implementation proceed. Each issue and activation stage retains its own user gate.

---

## Complexity: T3

This change will alter two canonical truth surfaces, a full-file generator, multiple consumers, canonical metrics, provenance validation, and legal/technical authority gates. It will therefore require three-provider plan and artifact review.
