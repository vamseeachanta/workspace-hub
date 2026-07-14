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
- `scripts/data/document-index/batch-process-standards.py:134-177` currently excludes `done` rows and can mark a candidate `done` without a positive file-existence result. `tests/document-intelligence/test_marine_standards_batch.py:179-215` currently encodes that behavior.
- `scripts/readiness/code-version-guard.sh:35-116` currently uses a scalar-only parser, checks four legacy keys, reports informational output, and exits zero. Nested canonical fields would be invisible without a consumer migration.
- `query-ledger.py`, `generate-coverage-report.py`, `doc-key-lookup.py`, `cross-reference-registries.py`, and `marine-taxonomy-classifier.py` currently consume legacy transfer state and/or paths. Coverage reporting currently equates `done` with implemented; cross-reference output can call unmatched holdings “publish candidates” without rights evidence.

### Standards and source authority

| Standard | Publisher-current metadata | Local evidence boundary | Registry defect |
|---|---|---|---|
| DNV-RP-C203 | DNV catalog: edition 2024-10, amended 2025-10; verified 2026-07-14 | Reachable filenames support 2000, 2005, 2008, 2010, and 2011 only. Filenames do not prove designation, lawful access, rights, or technical fitness. | Code registry states 2016-04 / 2024-07; ledger has no row. |
| BS 7608 | BSI catalog: BS 7608:2014+A1:2015 is Current; verified 2026-07-14 | Reachable filenames support 1993, 1993+A1:1995, and a file named 2014. The 2014 filename does not prove A1:2015. | Ledger says `done` with no paths and no exact identity. |

Official catalog metadata will establish publisher identity and currentness only. It will not establish numerical content, clause locators, possession, access authority, reuse rights, or qualified technical acceptance.

### LLM Wiki pages consulted

- `llm-wiki/wikis/engineering-standards/wiki/standards/dnv-rp-c203.md` currently labels revision 2024-10 while naming only a 2011 local source; it will remain resolver metadata rather than source authority.
- `llm-wiki/wikis/engineering/wiki/standards/dnv-rp-c203.md` currently lacks resolver identity fields.
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
- No validator currently rejects malformed content identities such as a 32-hex digest mislabeled `sha256:`; `data/document-index/index.jsonl:26402-26406` contains this defect class.
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
3. **Access and rights** — access authorization and reuse/derivative permission as separate evidence-backed states. Possession or subscription will not imply either.
4. **Qualified technical review** — accepted/rejected/pending status against an exact basis identity, decision reference, time, and reviewer role. Currentness or possession will not imply fitness for calculations.

`code-registry.yaml` will own curated logical code identity, publisher-current metadata, implementation basis, and qualified-review state for codes used in implementations. The transfer ledger will own transfer state and evidence-backed holdings. Both will reuse the existing `doc_key` and provenance contract; neither will create a parallel content identity.

Legacy `our_edition`, `latest_known_edition`, and `status` fields will remain read-compatible mirrors for one migration wave. The canonical nested fields will define their meaning, and validation will require mirror equality. Ledger `status` will remain transfer state; it will never encode access, rights, publisher currentness, or technical review.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Plan | `docs/plans/2026-07-14-issue-3533-standards-registry-authority-contract.md` |
| Human review companion | `docs/plans/2026-07-14-issue-3533-standards-registry-authority-contract.html` |
| Registry schema | `data/design-codes/standards-registry-v2.schema.json` |
| Curated enrichment input | `data/document-index/standards-authority-metadata.yaml` |
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
        keep reachability, access, and rights as independent states
    if technical review is accepted:
        require exact basis doc_key, decision_ref, reviewer_role, reviewed_at
        reject unavailable, rights-unknown, or identity-mismatched basis
    validate deprecated mirrors equal canonical values

function build_ledger(base_sources, curated_authority_metadata):
    generate deterministic legacy transfer rows
    join schema-validated enrichment by normalized standard identity
    never synthesize evidence, doc_key, access, rights, or acceptance
    reject destructive overwrite of unmatched curated metadata
    validate before atomic write and validate the written result

function derive_engineering_usability(record):
    return true only when exact identity, reachable holding, authorized access,
        permitted reuse, and accepted qualified review all pass
    report transfer status separately
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `data/design-codes/standards-registry-v2.schema.json` | Define canonical fields, enums, mirrors, evidence, and cross-field constraints. |
| Create | `data/document-index/standards-authority-metadata.yaml` | Provide a curated, generator-safe enrichment input rather than hand-edit-only state. |
| Create | `scripts/data/document-index/validate-standards-registries.py` | Validate both registries and derived usability fail closed. |
| Create | `tests/data/document-index/test_standards_registry_contract.py` | Add hermetic contract, migration, generator, and consumer tests before implementation. |
| Modify | `data/design-codes/code-registry.yaml` | Add schema version and evidence-bounded C203 publisher/current, implementation-basis, and pending-review data. |
| Modify | `data/document-index/standards-transfer-ledger.yaml` | Regenerate using the approved schema; preserve transfer state while adding evidence-bounded selected records. |
| Modify | `scripts/data/document-index/build-ledger.py` | Deterministically merge curated enrichment and validate pre/post write. |
| Modify | `scripts/data/document-index/batch-process-standards.py` | Refuse completion/usability transitions without required evidence. |
| Modify | `scripts/data/document-index/query-ledger.py` | Expose transfer, holding, access, rights, review, and usability as distinct filters/output. |
| Modify | `scripts/data/document-index/generate-coverage-report.py` | Report transfer coverage separately from engineering usability. |
| Modify | `scripts/data/document-index/cross-reference-registries.py` | Replace “publish candidate” claims when rights are unknown with neutral reconciliation output. |
| Modify | `scripts/readiness/code-version-guard.sh` | Consume validated nested fields while preserving a documented warn-only startup mode. |
| Modify | `tests/document-intelligence/test_marine_standards_batch.py` | Replace unsafe completion expectations with evidence-gated behavior. |
| Modify | `docs/reports/intelligence-metric-source-of-truth-map.md` | Define separate canonical metrics and migration effects. |
| Modify | `data/document-index/intelligence-accessibility-registry.yaml` | Refresh asset record count and point to the validated contract without implying per-row rights. |
| Modify | `docs/plans/README.md` | Index the reviewed plan. |

---

## TDD Test List

| Test | Verification |
|---|---|
| `test_done_transfer_state_does_not_imply_usable` | A legacy `done` row without exact holding/evidence remains non-usable and is reported separately. |
| `test_publisher_update_does_not_create_holding_claim` | Publisher-current metadata cannot synthesize possession, access, rights, or review. |
| `test_filename_does_not_promote_amendment` | `BS_7608-2014.pdf` cannot become 2014+A1:2015; C203 2011 cannot become 2016/2024/current amendment. |
| `test_stale_index_and_wiki_are_discovery_only` | Stale indexes and resolver pages cannot promote authority states. |
| `test_access_and_reuse_rights_are_independent` | Subscription/local reachability cannot imply reuse permission. |
| `test_accepted_review_requires_exact_basis` | Acceptance requires exact `doc_key`, identity, decision reference, reviewer role, and compatible evidence states. |
| `test_digest_namespace_validation` | `md5:` plus 32 hex and `sha256:` plus 64 hex pass; pseudo-SHA-256 with 32 hex fails; namespaces never join. |
| `test_generator_round_trip_preserves_enrichment` | Rebuilds preserve validated curated fields and deterministic ordering. |
| `test_generator_cannot_synthesize_completion_evidence` | `implemented` sources or completed work items cannot create holding/access/right claims. |
| `test_legacy_mirrors_equal_canonical_fields` | Old readers remain compatible for one wave and inconsistent mirrors fail validation. |
| `test_batch_requires_positive_file_and_authority_evidence` | Batch processing cannot mark evidence-free candidates usable/complete. |
| `test_reports_separate_transfer_from_usability` | Query, coverage, and readiness outputs do not conflate metrics. |
| `test_cross_reference_never_implies_publish_rights` | Unknown-rights rows are reconciliation candidates, never publish candidates. |
| `test_records_contain_metadata_only` | Schema rejects licensed body text, OCR/table payload fields, and embedded coefficient datasets. |

---

## Acceptance Criteria

- [ ] TDD will begin with the tests above failing for the documented reasons.
- [ ] `python -m pytest tests/data/document-index/test_standards_registry_contract.py tests/document-intelligence/test_marine_standards_batch.py -v` will pass.
- [ ] The validator will pass both canonical registries and fail every negative fixture.
- [ ] A dry-run ledger rebuild will be byte-deterministic and will preserve all validated curated enrichment.
- [ ] DNV-RP-C203 will record official publisher currentness separately from unverified local filename evidence; access, rights, and qualified review will remain unknown/pending absent evidence.
- [ ] BS 7608 will not claim A1:2015 possession from a 2014 filename and will not be engineering-usable from an empty-path `done` row.
- [ ] Transfer counts and engineering-usability counts will be separately named and documented.
- [ ] No wiki page, index status, path, possession, or subscription will be treated as reuse authority.
- [ ] No licensed text, tables, OCR bodies, or coefficient datasets will enter tracked artifacts.
- [ ] #2362 will be linked and re-planned against this contract before overlapping implementation.
- [ ] #3538 and llm-wiki #837 will remain separate owners of citation-contract and resolver changes.
- [ ] `scripts/legal/legal-sanity-scan.sh` and the relevant repository test suite will pass.
- [ ] T3 code/artifact review will obtain three-provider adversarial coverage or will explicitly record provider unavailability and residual risk.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | — |
| Codex | pending | — |
| Gemini | pending | — |

**Overall result:** pending

---

## Risks and Human Decisions

- **Human decision:** approval of this plan will authorize only generic schema/producer/consumer work and conservative metadata migration. It will not authorize a DNV numerical basis or licensed-source inspection.
- **Human decision:** any `technical_review.status: accepted` transition will require a qualified reviewer and evidence reference outside automated inference.
- **Risk:** open #2362 can race or overwrite identity work. Its implementation will remain blocked/re-planned until ownership and schema compatibility are explicit.
- **Risk:** a full-file ledger generator can destroy enrichment. Pre/post validation, deterministic merge input, atomic write, and round-trip tests will be acceptance gates.
- **Risk:** changing `done` semantics would corrupt canonical metrics. The migration will preserve transfer state and introduce separately named usability metrics.
- **Risk:** rights evidence may remain unavailable. The system will preserve `unknown` rather than relaxing the gate.

---

## Complexity: T3

This change will alter two canonical truth surfaces, a full-file generator, multiple consumers, canonical metrics, provenance validation, and legal/technical authority gates. It will therefore require three-provider plan and artifact review.
