# Plan for #3533: Standards registry authority contract

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3533
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** round 1 in `scripts/review/results/2026-07-14-plan-3533-*`; round 2 in `scripts/review/results/r2/2026-07-14-plan-3533-*`

---

## Resource Intelligence Summary

### Existing repo code

- `data/design-codes/code-registry.yaml:19-28` currently represents DNV-RP-C203 with `our_edition: "2016-04"`, `latest_known_edition: "2024-07"`, and `status: check`; those names conflate an implementation basis with publisher currentness.
- `data/document-index/standards-transfer-ledger.yaml:2045-2060` currently marks BS-7608 `done` with empty `doc_path` and `doc_paths`. The ledger has no DNV-RP-C203 row. A YAML parse on 2026-07-14 finds 142 of 435 `done` rows without either path, 436 of 436 rows without `doc_key`, and no per-row provenance or rights state.
- `scripts/data/document-index/build-ledger.py:193-247,268-353` currently derives `done` from upstream `implemented` state or a completed work item and rewrites the whole YAML from a legacy-only mapping. An unmodified generator would erase hand-added enrichment.
- `scripts/document-intelligence/batch-process-standards.py:134-177` currently excludes `done` rows and can mark a candidate `done` without a positive file-existence result. `tests/document-intelligence/test_marine_standards_batch.py:179-215` currently encodes that behavior.
- `scripts/readiness/code-version-guard.sh:35-116` currently uses a scalar-only parser, checks four legacy keys, reports informational output, and exits zero. Nested canonical fields would be invisible without a consumer migration.
- `query-ledger.py`, `generate-coverage-report.py`, `scripts/knowledge/doc-key-lookup.py`, `scripts/document-intelligence/cross-reference-registries.py`, and `marine-taxonomy-classifier.py` consume legacy porting status and/or paths. `research-domain.py` maps several statuses to `available`; `generate-domain-resource-views.py` renders `done` as acquired. These consumers will stop inferring possession/authority from porting state.

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
- `docs/reports/intelligence-metric-source-of-truth-map.md:8-31` makes ledger totals and per-row legacy state canonical metrics; migration will rename its actual porting/implementation semantics and update downstream counts explicitly.
- `data/document-index/intelligence-accessibility-registry.yaml:218-268` records asset-level reachability and is already stale at 425 ledger records versus 436 live rows; it cannot stand in for record-level verification.
- `config/drive-index-registry.yml:48-97` records the O&G inventory as 2025-12-28 with no refresh and the frozen master index as 2026-04-17. Those catalogs will remain discovery evidence only.
- `DRIVE_SEARCH_NO_METRICS=1 timeout 45 uv run python scripts/data/drive-index-search/search.py "DNV-RP-C203 BS 7608" --json --caller plan-resource-intel` completed on 2026-07-14. It queried six registered indexes, returned older C203/BS filename families plus unrelated token matches, and warned that O&G (198 days), CAD (18 days), and master index (88 days) exceeded thresholds. Per the playbook, this plan records aggregate/de-identified findings only; paths, hashes, OCR artifacts, and bodies are not authority evidence.
- [#2207](https://github.com/vamseeachanta/workspace-hub/issues/2207) owns the existing provenance contract; [#2250](https://github.com/vamseeachanta/workspace-hub/issues/2250) owns canonical ledger metrics.
- Open [#2362](https://github.com/vamseeachanta/workspace-hub/issues/2362) proposes broad `doc_key` backfill and an `unreachable` ledger status. #3533 will not absorb the broad backfill and will prevent access/reachability from overloading porting state. Its `dispatch:ready` label is removed and a coordination comment requires re-planning.
- [#3538](https://github.com/vamseeachanta/workspace-hub/issues/3538) will own any amendment or exact-source extension to the calculation citation contract.

### Gaps identified

- No machine-validated public schema currently separates publisher currentness, implementation state, and blocked authority while excluding private evidence.
- No durable producer path currently round-trips per-standard enrichment through a ledger rebuild.
- No validator currently rejects malformed content identities such as a 32-hex digest mislabeled `sha256:`. A machine-local, gitignored `data/document-index/index.jsonl` sample contains this defect class; CI will use a hermetic synthetic fixture instead.
- Public consumers currently infer availability from porting status even though public data cannot establish engineering usability.
- No existing artifact establishes lawful access, reuse rights, or qualified acceptance for the DNV-RP-C203 or BS 7608 holdings. Those values will remain `unknown` or `pending`.

### Evidence (embedded verification)

**Issue status, verified 2026-07-14:** #3533, #2362, and #3538 are OPEN; #2207 and #2250 are CLOSED.

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

`code-registry.yaml` will own public-safe logical identity, publisher metadata, implementation-basis metadata, and a blocked resolution gate. The historically named transfer ledger will retain legacy engineering-code porting/migration state and discovery aliases; it will not be relabeled as physical transfer history, possession, or authority. Exact holdings, fingerprints, access, permissions, and qualified-review evidence will not enter this public repository; private ownership will be planned under [llm-wiki #840](https://github.com/vamseeachanta/llm-wiki/issues/840).

Legacy `our_edition`, `latest_known_edition`, and `status` will remain deprecated read fields for one wave; they will not be equality mirrors because their current vocabularies conflate meanings. Canonical fields will be `implementation_basis`, `publisher_current`, `resolution_gate`, and `implementation_status`. The ledger's legacy `status` will be treated only as historical porting/migration input.

At migration, all 436 legacy row IDs and a canonical input hash will be captured in a grandfather manifest. Existing `done` values will remain only as `legacy_status`; canonical `implementation_status` will default to `unknown` unless a public code/test evidence reference proves implementation. After the cutoff, the producer and every writer will be forbidden from synthesizing `done` or grandfathering new rows from `implemented` sources or completed work items. No public status will imply rights or engineering usability.

Public logical and publisher records will join only by canonical edition-independent `code_id`. Exact holding/permission/review joins are outside [#3533](https://github.com/vamseeachanta/workspace-hub/issues/3533) and will be defined privately by [llm-wiki #840](https://github.com/vamseeachanta/llm-wiki/issues/840); this plan will not validate or derive private usability.

The public cross-repo interface name/version will be finalized by this implementation rather than pre-authorized downstream. Its allowlist will expose only canonical code identity, official publisher metadata, evidence URL/time/type, and `resolution_gate: blocked | metadata-only`. It will expose no fingerprint, holding, path, access fact, permission decision, reviewer state, or private evidence reference. LLM-wiki #837 will consume the landed schema through an adapter. Missing, stale, unsupported-version, or identity-mismatched records will fail closed.

### Canonical registry schema (`standards-registry.schema.json`)

```yaml
schema_version: "1"
codes:
  - standard_identity: {code_id: <canonical id>, publisher: <publisher>}
    publisher_current:
      designation: <publisher designation>
      edition: <quoted value or unknown>
      edition_published_at: <date or unknown>
      amendment: <quoted value or none/unknown>
      amendment_published_at: <date or none/unknown>
      amendment_parent_edition: <edition or none/unknown>
      lifecycle: current | withdrawn | superseded | unknown
      evidence: {kind: publisher_catalog, url: <official URL>, verified_at: <RFC3339>}
    implementation_basis:
      edition: <quoted value or unknown>
      amendment: <quoted value or none/unknown>
      evidence_ref: <public code/test/decision reference or none>
    implementation_status: implemented | not-implemented | unknown
    resolution_gate: blocked | metadata-only
```

The ledger and curated input will each receive their own closed schema matching their live top-level envelopes. The ledger schema will carry `legacy_status`, canonical `implementation_status`, public evidence references, and grandfather-manifest membership; it will carry no authority or usability field. Dates will be quoted. Chronology will use publication dates and explicit amendment-parent identity, never lexical edition ordering.

### Public export schema (`standards-authority-public.schema.json`)

The export allowlist will contain only `schema_version`, `generated_at`, `standard_identity`, `publisher_current` (including its official evidence), and `resolution_gate`. It will exclude implementation basis/status, all ledger fields, private-state hints, free-text notes, fingerprints, holdings, paths, permissions, reviews, and private references. Unknown keys and free-text payload fields will fail validation.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Plan | `docs/plans/2026-07-14-issue-3533-standards-registry-authority-contract.md` |
| Human review companion | `docs/plans/2026-07-14-issue-3533-standards-registry-authority-contract.html` |
| Registry schema | `data/design-codes/standards-registry.schema.json` |
| Curated enrichment input | `data/document-index/standards-authority-metadata.yaml` |
| Ledger/input schemas and cutoff | `data/document-index/standards-ledger.schema.json`; `data/document-index/standards-authority-metadata.schema.json`; `data/document-index/standards-ledger-grandfather.json` |
| Public cross-repo schema/export | `data/design-codes/standards-authority-public.schema.json`; `data/design-codes/standards-authority-public.json` |
| Validator | `scripts/data/document-index/validate-standards-registries.py` |
| Tests | `tests/data/document-index/test_standards_registry_contract.py` |
| Review artifacts | round 1 under `scripts/review/results/`; round 2 under `scripts/review/results/r2/` |

---

## Deliverable

A versioned public contract and producer/consumer migration will distinguish publisher currentness, implementation/porting state, and blocked authority without publishing or inferring private holdings, access, permissions, or technical acceptance.

---

## Pseudocode

```text
function validate_public_record(record, registry_kind):
    validate schema version and allowed state vocabularies
    validate publisher chronology, amendment parent, and official evidence
    require implementation evidence for canonical implemented status
    require resolution_gate blocked when private authority is unavailable
    reject private/free-text fields from the public export

function build_ledger(base_sources, curated_authority_metadata, as_of, output_path):
    reject normalized-id collisions and orphan curated records
    preserve grandfathered legacy_status only for manifest members
    reject any post-cutoff synthesis of done from upstream/work-item state
    join logical metadata by canonical code_id
    never synthesize holding, authority, permission, or review evidence
    reject destructive overwrite of unmatched curated metadata
    validate candidate before write
    on dry run, emit candidate to output_path without mutating canonical file
    on apply, fsync a temporary sibling and replace atomically

function report_public_state(record):
    report legacy porting, canonical implementation, publisher currentness,
        and resolution gate as distinct fields
    never report engineering usability from public data
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `data/design-codes/standards-registry.schema.json` | Define the first canonical schema, enums, evidence, and constraints. |
| Create | `data/design-codes/standards-authority-public.schema.json` | Define the disclosure-minimized public #3533 → #837 interface. |
| Create | `data/design-codes/standards-authority-public.json` | Publish publisher metadata and blocked state only. |
| Create | `data/document-index/standards-authority-metadata.yaml` | Provide a curated, generator-safe enrichment input rather than hand-edit-only state. |
| Create | `data/document-index/standards-ledger.schema.json`, `standards-authority-metadata.schema.json`, `standards-ledger-grandfather.json` | Define separate envelopes and freeze the pre-migration row set. |
| Create | `scripts/data/document-index/validate-standards-registries.py` | Validate public schemas and forbid authority/usability inference. |
| Create | `tests/data/document-index/test_standards_registry_contract.py` | Add hermetic contract, migration, generator, and consumer tests before implementation. |
| Modify | `data/design-codes/code-registry.yaml` | Add schema version and evidence-bounded C203 publisher/current, implementation-basis, and pending-review data. |
| Modify | `data/document-index/standards-transfer-ledger.yaml` | Preserve legacy porting state, add canonical implementation state, and remove authority inference. |
| Modify | `scripts/data/document-index/build-ledger.py` | Deterministically merge curated enrichment and validate pre/post write. |
| Modify | `scripts/document-intelligence/batch-process-standards.py` | Stop creating canonical `done`; require explicit implementation evidence and validated writer flow. |
| Modify | `scripts/data/document-index/query-ledger.py` | Expose legacy porting and canonical implementation without authority claims. |
| Modify | `scripts/data/document-index/generate-coverage-report.py` | Report legacy porting and evidenced implementation separately. |
| Modify | `scripts/document-intelligence/cross-reference-registries.py` | Replace “publish candidate” claims when authority is unknown with neutral reconciliation output. |
| Modify | `scripts/knowledge/doc-key-lookup.py` | Treat legacy paths as discovery aliases, not holding or authority evidence. |
| Modify | `scripts/document-intelligence/marine-taxonomy-classifier.py` | Consume schema-versioned fields without changing classification semantics. |
| Modify | `scripts/data/research-literature/research-domain.py` | Stop mapping transfer state directly to source availability. |
| Modify | `scripts/data/generate-domain-resource-views.py` | Render porting/implementation state without possession/usability inference. |
| Modify | `scripts/data/document-index/mark-exhausted.py`, `scripts/data/document-index/reclassify-domains.py` | Route full-ledger rewrites through shared validation and atomic replacement. |
| Modify | `scripts/data/ace_resource_audit.py`, `scripts/data/document-index/mkt_a_wiki_unblock.py` | Stop treating porting counts/scalar paths as disk coverage or authority. |
| Modify | `scripts/readiness/code-version-guard.sh` | Consume validated nested fields while preserving a documented warn-only startup mode. |
| Modify | `tests/document-intelligence/test_marine_standards_batch.py` | Replace unsafe completion expectations with evidence-gated behavior. |
| Modify | `docs/reports/intelligence-metric-source-of-truth-map.md` | Define separate canonical metrics and migration effects. |
| Modify | `data/document-index/intelligence-accessibility-registry.yaml` | Refresh asset record count and point to the validated contract without implying per-row rights. |
| Existing | `docs/plans/2026-07-14-issue-3533-standards-registry-authority-contract.html` | HTML companion exists and passed Chrome full-page visual QA. |
| Existing | `docs/plans/README.md` | Draft row exists; its status will update after review. |

---

## TDD Test List

| Test | Verification |
|---|---|
| `test_legacy_done_is_porting_input_not_transfer_or_authority` | Historical `done` remains only `legacy_status`; canonical implementation defaults unknown without evidence. |
| `test_post_cutoff_done_synthesis_fails` | New upstream/work-item rows cannot enter the grandfather set or synthesize canonical completion. |
| `test_publisher_update_does_not_create_holding_claim` | Publisher-current metadata cannot synthesize possession, access, rights, or review. |
| `test_edition_chronology_and_amendment_parent` | Impossible dates and amendments without their parent edition fail. |
| `test_filename_does_not_promote_amendment` | `BS_7608-2014.pdf` cannot become 2014+A1:2015; C203 2011 cannot become 2016/2024/current amendment. |
| `test_stale_index_and_wiki_are_discovery_only` | Stale indexes and resolver pages cannot promote authority states. |
| `test_public_schema_has_no_private_authority_fields` | Public schemas reject holdings, digests, access, permissions, review state, paths, notes, and free-text payloads. |
| `test_generator_round_trip_preserves_enrichment` | Rebuilds preserve validated curated fields and deterministic ordering. |
| `test_generator_injected_clock_and_repeated_bytes` | Two builds with identical inputs/as-of are byte-identical. |
| `test_generator_atomic_replace_and_interruption` | Failed validation/write never changes the canonical ledger. |
| `test_generator_rejects_orphan_and_id_collision` | Orphan curated records and normalized-ID collisions fail closed. |
| `test_generator_cannot_synthesize_authority_or_completion` | `implemented` sources/completed work items cannot create canonical completion or authority claims. |
| `test_deprecated_fields_are_not_canonical_mirrors` | Legacy readers remain available for one wave while canonical semantics remain independently validated. |
| `test_every_ledger_writer_validates_and_replaces_atomically` | Builder, batch, exhaustion, and reclassification writers share the gate. |
| `test_reports_separate_porting_from_authority` | Query, coverage, and readiness outputs make no possession/usability claim. |
| `test_authority_export_contract` | Export is deterministic, versioned, publisher-evidence-only, and blocked absent private authority. |
| `test_public_export_disclosure_allowlist` | Exact key equality rejects implementation, ledger, free-text, digest, holding, path, access, permission, review, and private-reference fields. |
| `test_research_and_domain_views_do_not_infer_availability` | Research/resource views stop mapping porting state to possession/usability. |
| `test_cross_reference_never_implies_publish_rights` | Unknown-rights rows are reconciliation candidates, never publish candidates. |
| `test_export_values_are_bounded_metadata` | IDs/enums/dates/official URLs are format- and size-bounded; no general notes/body field exists. |

---

## Acceptance Criteria

- [ ] TDD will begin with the tests above failing for the documented reasons.
- [ ] Preflight will extend sparse checkout with `scripts/document-intelligence scripts/knowledge scripts/legal`, verify/recreate the local `uv` environment if invalid, and include every named writer/consumer.
- [ ] Exact suites will include the new contract test plus existing/focused tests for builder, query, coverage, batch, cross-reference, lookup, taxonomy, research-domain, domain views, resource audit, wiki unblock, exhaustion, reclassification, readiness guard, and legal scan; no “focused tests” placeholder will remain before approval.
- [ ] The validator will pass both canonical registries and fail every negative fixture.
- [ ] A dry run with injected `as_of` will emit a candidate artifact; repeated runs will be byte-identical, and atomic replacement will prevent partial writes.
- [ ] Historical `done` will remain only legacy porting/migration input. The grandfather manifest will freeze the cutoff set, new `done` synthesis will fail, and canonical implementation will require public code/test evidence.
- [ ] DNV-RP-C203 will record official publisher currentness separately from filename evidence. No holding row will be created until exact private evidence exists; no public access/permission/review fact will be emitted.
- [ ] BS 7608 will not claim A1:2015 possession or engineering usability from a 2014 filename or legacy `done` row.
- [ ] Legacy porting counts, canonical implementation counts, and publisher-current counts will be separately named; public data will expose no usability count.
- [ ] No wiki page, index status, path, possession, or subscription will be treated as reuse authority.
- [ ] Permissions and qualified review will be absent from the public schema; #840 will own their private contract without pre-authorization here.
- [ ] The public export will use the exact publisher-metadata allowlist; downstream compatibility/freshness will be planned after the schema lands, not self-tested against an invented #837 fixture.
- [ ] New export values will be limited to bounded IDs, enums, dates, and official URLs; legal scan will separately guard prohibited content. Existing free-text ledger notes are legacy data, not evidence or export fields.
- [ ] #2362 will remain without `dispatch:ready`; its coordination comment will link this plan, and it will be re-planned before overlap.
- [ ] [#3538](https://github.com/vamseeachanta/workspace-hub/issues/3538) and [llm-wiki #837](https://github.com/vamseeachanta/llm-wiki/issues/837) will remain separate owners of citation and resolver changes.
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

**Overall result:** FAIL. Round 2 returned Claude MAJOR and Codex MAJOR; the required r3 inline corrections are incorporated, but the plan remains `status:needs-plan` and will not advance without a fresh approved review state.

R3 inline corrections separate porting from transfer/authority, define three schema envelopes and an exact public allowlist, remove private-usability scope, freeze a grandfather cutoff, close all known writer/consumer bypasses, add drive-search evidence, qualify dependency URLs, and make sparse/legal/environment preflight explicit. The HTML companion passed full-page Chrome visual QA on 2026-07-14.

---

## Risks and Human Decisions

- **Human decision:** approval of this plan will authorize only generic schema/producer/consumer work and conservative metadata migration. It will not authorize a DNV numerical basis or licensed-source inspection.
- **Human decision:** any `technical_review.status: accepted` transition will require a qualified reviewer and evidence reference outside automated inference.
- **Risk:** open #2362 can race or overwrite identity work. Its implementation will remain blocked/re-planned until ownership and schema compatibility are explicit.
- **Risk:** a full-file ledger generator can destroy enrichment. Pre/post validation, deterministic merge input, atomic write, and round-trip tests will be acceptance gates.
- **Risk:** changing `done` semantics would corrupt canonical metrics. The migration will preserve it only as explicitly named legacy porting input and introduce evidenced implementation metrics.
- **Risk:** private authority evidence may remain unavailable. Public resolution will stay blocked rather than infer usability.
- **Privacy gate:** exact holdings, fingerprints, access, permissions, and qualified-review evidence will not enter public workspace-hub artifacts. Their private canonical home requires separately approved llm-wiki #840.
- **Dependency order:** #3533 will publish schema plus pending/unknown records; [llm-wiki #839](https://github.com/vamseeachanta/llm-wiki/issues/839) and [workspace-hub #3538](https://github.com/vamseeachanta/workspace-hub/issues/3538) will establish page/source and citation contracts; [llm-wiki #837](https://github.com/vamseeachanta/llm-wiki/issues/837) Stage A will install blocked identities; a qualified [digitalmodel #1588](https://github.com/vamseeachanta/digitalmodel/issues/1588) basis decision will precede activation and calculation implementation. Each issue/stage retains its own user gate.

---

## Complexity: T3

This change will alter two canonical truth surfaces, a full-file generator, multiple consumers, canonical metrics, provenance validation, and legal/technical authority gates. It will therefore require three-provider plan and artifact review.
