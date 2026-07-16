# Plan for worldenergydata #1045: Deterministic exact-revision HF browser snapshot

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-16
> **Issue:** https://github.com/vamseeachanta/worldenergydata/issues/1045
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:codex
> **Execution mode:** planning/review `parallel-readonly`; implementation `parallel-worktree` for pure builder/tests, serialized single-lane for live publication
> **Review artifacts:** `scripts/review/results/2026-07-16-plan-1045-claude.md` | `scripts/review/results/2026-07-16-plan-1045-codex.md` | `scripts/review/results/2026-07-16-plan-1045-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/hf_export/build_explorer_results_bundle.py` currently combines `_explorer.json` and `_atlas_feed.json`, sanitizes non-finite numbers, and writes source hashes. It currently declares obsolete dataset identity `worldenergydata`, does not record a clean source Git SHA, and does not emit the proposed relational browser contract.
- `scripts/hf_export/publish_explorer_refresh_to_hf.py` currently downloads floating `fields.parquet`, patches it, and uploads only `fields.parquet`, `parametric_economics.parquet`, and `README.md`. It will not rebuild wells/countries, use expected-parent protection, capture the returned SHA, or exact-SHA read back bytes.
- `tests/unit/site/test_explorer_results_bundle.py` currently tests strict JSON/counts but preserves the obsolete identity and has no publication transaction or browser-manifest coverage.
- `config/fields.yml` is the canonical field identity registry. It separates stable canonical IDs from labels, aliases, leases, and FDP slugs.
- `packages/worldenergydata-core/src/worldenergydata_core/fields_registry.py` supplies fail-closed canonical resolution and duplicate checks.
- `reports/lower_tertiary/lifecycle/_explorer.json` contains ten field records and 56 unique 12-digit API wells. Seven fields have wells and three have explicit zero-well coverage.
- `reports/field-atlas/_atlas_feed.json` contains 84 countries and 2,032 catalog field records; catalog records will not become drill-down-ready by implication.
- `reports/lower_tertiary/parametric/lt_economics_parametric.csv` contains 120 local sweep rows. The current publisher filters to surfaced economics; the new projection will declare and test that policy explicitly instead of inheriting live HF state.

### Standards

| Contract | Status | Source |
|---|---|---|
| Parent lifecycle and external SHA ownership | binding | [workspace-hub #3559](https://github.com/vamseeachanta/workspace-hub/issues/3559) |
| Canonical field identity | binding | `config/fields.yml` |
| Public-egress/legal scan | binding | workspace `scripts/legal/legal-sanity-scan.sh`, `.legal-deny-list.yaml` |
| HF repository-specific projection | related precedent | [#927](https://github.com/vamseeachanta/worldenergydata/issues/927), [workspace-hub #3427](https://github.com/vamseeachanta/workspace-hub/issues/3427) |
| Engineering calculation citation | N/A | This issue will package existing results and will not introduce standards-derived constants. |

### Documents consulted

- [#1045](https://github.com/vamseeachanta/worldenergydata/issues/1045) owns deterministic construction, schema/identity, legal admission, HF commit/readback, and receipt.
- [workspace-hub #3559](https://github.com/vamseeachanta/workspace-hub/issues/3559) owns the cross-repository lifecycle; it will not implement publisher code.
- [aceengineer-website #74](https://github.com/vamseeachanta/aceengineer-website/issues/74) will consume the reviewed manifest fixture and later the real receipt/SHA.
- [#939](https://github.com/vamseeachanta/worldenergydata/issues/939), closed [#946](https://github.com/vamseeachanta/worldenergydata/issues/946), [#947](https://github.com/vamseeachanta/worldenergydata/issues/947), [#948](https://github.com/vamseeachanta/worldenergydata/issues/948), and [#965](https://github.com/vamseeachanta/worldenergydata/issues/965) supply the Explorer shell/feed/well/export lineage.
- [#966](https://github.com/vamseeachanta/worldenergydata/issues/966) and [#972](https://github.com/vamseeachanta/worldenergydata/issues/972) will remain cross-links; no HF Space or server-rendered visualization will be required.
- Drive-index search returned no relevant external document; unrelated oil-field/CAD token matches will not govern publication.
- No relevant LLM-wiki page was found or will be modified.

### Gaps identified

- No canonical browser manifest/schema/shards or source-to-browser normalization module exists.
- No stable namespaced well identity or explicit `parent_field_id` browser contract exists.
- No full four-config deterministic local build exists; current publication depends on floating HF bytes.
- No legal/source classification gate reconciles `license: other` with the live CC-BY-4.0 claim.
- No expected-parent atomic HF commit, exact-SHA raw readback, or verified receipt exists.

### Evidence

Inspection was against clean `worldenergydata/main` at `a26881d49d064ea6ae6c8200ae1a874bf944e1bb`.

```text
current _explorer.json sha256: 29ae5ea119ac28f0a24c8f1107d5b74b14bb99c2c56e94a70efb9b6d8ae07082
bundle-recorded explorer sha:   fc79569c7417d2b7f3239d8d14d96e2076145751ac1e63ef19273c17e2c3e92e
current _atlas_feed.json sha:   50e039377705d8ee71ba520b55ea2583317d90b88eb0e41924d96fe0cb8ba32c
bundle dataset identity:        worldenergydata
canonical live dataset:         aceengineer/worldenergydata-explorer
```

Current well proof: 56 wells, 56 unique `api` values, every API is 12 digits, and field counts are Jack/St. Malo 24, Stones 10, Big Foot 8, Julia 4, Shenandoah 4, Anchor 3, Cascade/Chinook 3.

**Immutable-read reproduction:** datasets-server returned identical HTTP 200 bytes for the real HF SHA and a fabricated all-zero SHA; raw `resolve/<fake-sha>/...` returned 404. Immutable verification will therefore use raw exact-SHA files only.

**Reproduction time:** 2026-07-16. **Issue claim matched:** YES — the current publisher cannot prove or supply an atomic exact-revision browser snapshot.

Distinct sources: issue body, parent/consumer issues, two current exporter scripts, identity registry/loader, three generated data products, related issue lineage, HF probe, and drive search.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-16-issue-1045-wed-hf-browser-snapshot.md` |
| Pure snapshot builder | `scripts/hf_export/explorer_snapshot.py` |
| Publisher/orchestrator | `scripts/hf_export/publish_explorer_snapshot_to_hf.py` |
| Publisher configuration | `config/hf_export/field_explorer_snapshot.yml` |
| Manifest schema | `config/schemas/field_explorer_browser_manifest.schema.json` |
| Record schema | `config/schemas/field_explorer_browser_records.schema.json` |
| Publish-receipt schema | `config/schemas/field_explorer_publish_receipt.schema.json` |
| Existing bundle builder | `scripts/hf_export/build_explorer_results_bundle.py` |
| Deprecated publisher | `scripts/hf_export/publish_explorer_refresh_to_hf.py` |
| Human contract | `docs/data/field-explorer-hf-browser-snapshot.html` |
| Tests | `tests/unit/site/test_explorer_snapshot.py`, `tests/unit/site/test_explorer_snapshot_publisher.py`, existing bundle tests |
| Contract fixtures | `tests/fixtures/hf_export/field_explorer_browser/` |
| Tracked bundle/card | `reports/field-atlas/results/explorer_results_bundle.json`, `README.md` |
| Post-publish receipt | `reports/field-atlas/results/explorer_publish_receipt.json` |
| Protected publisher workflow | `.github/workflows/publish-field-explorer-snapshot.yml` |
| Attested CI evidence bundle | GitHub Actions artifact bound in the publish receipt |

---

## Deliverable

A deterministic publisher will build normalized fields, wells, countries, economics, bounded browser JSON shards, Parquet tables, card, and manifest from one clean worldenergydata commit; publish all bytes in one expected-parent HF commit; raw-read every declared artifact by the returned SHA; and emit a receipt only after full verification.

The live mutation will run only from the protected manual GitHub Actions publisher workflow on the reviewed repository commit and environment. The receipt will record the run/workflow IDs, workflow blob, head SHA, artifact ID/digest, environment, and conclusion. Parent #3559 will live-fetch that run and rehash the downloaded evidence artifact; a locally fabricated receipt will not satisfy promotion.

## Artifact and Identity Contract

```text
README.md
fields.parquet
wells.parquet
countries.parquet
parametric_economics.parquet
browser/manifest.json
browser/snapshots/<content_snapshot_id>/fields/part-00000.json
browser/snapshots/<content_snapshot_id>/wells/part-00000.json
browser/snapshots/<content_snapshot_id>/countries/part-00000.json
browser/snapshots/<content_snapshot_id>/parametric_economics/part-00000.json
```

The content snapshot ID will be derived from canonical logical record bytes before paths/manifest serialization. The manifest will contain schema version, dataset ID, clean source Git SHA, generator version, source hashes, every artifact path/hash/bytes/media type/records/schema, primary/foreign keys, declared sorting, readiness, provenance, license classification, and explicit zero-well representation. It will not contain its own HF commit SHA. The closed publish-receipt schema will bind source Git SHA, HF parent/returned SHA, manifest path/hash, operation set, exact-readback results, counts, generator/tool versions, timestamps, verification status, and referenced evidence hashes; unknown fields and schema majors will fail.

- `field_id`: stable canonical ID from `config/fields.yml`.
- `well_id`: `bsee-api12:<api>` for V1; API remains a string.
- `parent_field_id`: canonical field ID.
- label, aliases, slug, and slot: mutable/display attributes, never identity.
- browser payload: data only; no embedded HTML or executable strings.

Browser JSON shards will be regular, bounded Git blobs (not LFS/CAS objects), each below the configured byte limit, so the website can resolve them through exact-SHA same-origin HF cache redirects. Parquet may use HF's normal large-file storage but will not be a browser dependency.

---

## Pseudocode

```text
build_snapshot(config):
    require clean tracked worktree and exact source_git_sha
    load committed explorer, atlas, parametric and identity inputs
    validate source hashes, dataset identity and approved license classes
    resolve every field through canonical registry
    normalize fields/wells/countries/economics; derive namespaced well IDs
    reject nonfinite values, HTML, unsafe paths, duplicates and orphans
    sort by declared code-point keys; serialize strict canonical JSON
    derive content_snapshot_id; shard by configured record+byte bounds
    write deterministic Parquet and card; assert logical JSON/Parquet parity
    build and schema-validate manifest without an HF SHA
    return immutable staged artifact inventory
```

```text
publish(stage, dry_run):
    if dry_run: print proposed parent/counts/hashes; perform no mutation
    remote_parent = read current HF head
    result = create_commit(all_artifacts, parent_commit=remote_parent)
    returned_sha = validate_40_hex(result.oid)
    for artifact in manifest: raw-read at returned_sha and revalidate bytes/hash/schema/count
    write receipt atomically only after every check passes
```

If upload succeeds but readback fails, the immutable commit will remain an unpromoted orphan: no receipt, website pin, automatic retry, deletion, or history rewrite will occur.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/hf_export/explorer_snapshot.py` | pure load/normalize/validate/shard/hash/manifest logic |
| Create | `scripts/hf_export/publish_explorer_snapshot_to_hf.py` | dry-run/live transaction, expected parent, readback, receipt |
| Create | `.github/workflows/publish-field-explorer-snapshot.yml` | protected manual live publish, secret isolation and durable run provenance |
| Create | `config/hf_export/field_explorer_snapshot.yml` | dataset, inputs, license classes, versions, shard limits |
| Create | three JSON schemas under `config/schemas/` | closed record, manifest, and publish-receipt contracts |
| Modify | `build_explorer_results_bundle.py` | delegate to canonical normalization and repair identity/hash/card drift |
| Deprecate or delete | `publish_explorer_refresh_to_hf.py` | prevent a second floating supported path |
| Regenerate | tracked bundle and card | current deterministic source artifact |
| Create | `docs/data/field-explorer-hf-browser-snapshot.html` | human contract and publish/rollback instructions |
| Create/modify | focused unit tests and fixtures | TDD and compatibility |
| Create after live verification | publish receipt | downstream pin handoff |

Python files will remain at most 400 lines and functions at most 50 lines; pure builder responsibilities will split before exceeding those limits.

---

## TDD Test List

### Pure builder

1. repeated builds under different paths/locales produce byte-identical artifacts;
2. dirty tree, stale source hash, wrong dataset ID, or non-40-hex source SHA fails;
3. unresolved/conflicting license classification fails before staging;
4. NaN/Infinity, HTML/script strings, absolute/traversal/backslash/NUL paths fail;
5. unknown schema major and unknown record fields fail;
6. canonical field IDs resolve only through the registry;
7. namespaced well IDs are unique and API values remain strings;
8. every `parent_field_id` exists exactly once; duplicates/orphans fail;
9. explicit zero-well fields remain ready/selectable;
10. stable ordering and canonical serialization are environment-independent;
11. synthetic >100 records shard deterministically without loss/duplication;
12. record and byte shard bounds are enforced; browser shards remain regular-blob sized;
13. manifest hashes/bytes/media/counts/schema match staged files;
14. manifest schema rejects any HF commit SHA property;
15. JSON and Parquet have logical parity for all four configs;
16. surfaced-economics filtering is explicit and discovered counts match policy;
17. existing analytical columns remain or carry a versioned migration.

### Publisher

18. dry-run uses no token, writes no network state, and emits no receipt;
19. live mode invokes one `create_commit` containing every artifact;
20. `parent_commit` equals the preflight head; a race fails with no receipt;
21. invalid/missing returned SHA fails closed;
22. every verification URL contains the returned exact SHA and no floating ref;
23. no code path uses datasets-server for immutable verification;
24. missing/tampered/recount/schema/readback failures emit no receipt;
25. same-origin raw cache redirect is bounded and preserves the exact SHA; off-origin browser-JSON redirects fail;
26. token/auth values never enter logs, exceptions, manifest, or receipt;
27. success writes exactly one complete receipt; post-upload failure records only an unpromoted orphan;
28. live mode refuses execution outside the protected workflow/environment contract;
29. receipt binds GitHub run/workflow/head/artifact identity and parent verification rejects a fabricated or fork run;
28. expected-parent conflict requires a fresh explicit run, not automatic retry.

---

## Acceptance Criteria

- [ ] Failing tests will precede each implementation slice.
- [ ] Same committed inputs will produce byte-identical JSON, manifest, Parquet, and card under the pinned toolchain.
- [ ] Source/git/dataset/license/numeric/HTML/path/schema/PK/FK/count/order failures will fail closed.
- [ ] V1 will discover ten ready fields and 56 wells, including seven populated and three zero-well fields, without production hardcoding.
- [ ] Stable field/well identities will be separate from labels/slugs/slots.
- [ ] All four complete configs and browser artifacts will be generated locally; no floating HF file will be an input.
- [ ] Sharding will be deterministic, bounded, and complete above 100 rows.
- [ ] One expected-parent HF commit will contain the entire declared snapshot.
- [ ] The returned exact SHA will be captured and every raw artifact will be revalidated by that SHA.
- [ ] The manifest will not self-reference an HF SHA; the receipt and website registry will bind it externally.
- [ ] Any preflight/upload/race/readback failure will prevent receipt and website promotion.
- [ ] Live publication will run only through the protected manual GitHub Actions environment and will emit evidence that parent #3559 can verify against the live Actions API and artifact digest.
- [ ] Dry-run will make no external writes; live auth will be environment/client backed and redacted.
- [ ] Browser JSON will be bounded regular Git blobs; website exact-SHA delivery behavior will be fixture-tested.
- [ ] Dataset card/source classifications will not claim CC-BY-4.0 unless evidence authorizes it; unresolved rights will block publication.
- [ ] Existing consumers will remain compatible or receive an explicit versioned migration.
- [ ] Legal/security scans, focused/full tests, code review, implementation issue comment, cleanup audit, and completeness gate will pass.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | review not run |
| Codex | PENDING | review not run |
| Gemini | PENDING | review not run |

**Overall result:** PENDING. The issue will remain `status:needs-plan` until no unresolved MAJOR remains.

---

## Risks and Open Questions

- **License admission:** implementation may proceed through local fixtures, but live upload will remain fail-closed until explicit source/redistribution classification is recorded.
- **Parquet determinism:** serializer/version, column order/types/index/compression/metadata will be pinned; browser JSON will remain the authoritative browser contract.
- **Post-upload failure:** HF history cannot be rolled back atomically. Failed candidates will remain unpromoted and unreferenced.
- **Source self-reference:** generated HF manifest will be staged after the clean source commit and will not be committed back into that source revision.
- **Publisher drift:** the old floating entrypoint will not remain a supported alternative.
- **Scale:** shard record, byte, and operation-count limits will be configured and verified before mutation.
- **Coverage honesty:** 2,032 catalog records and 115 FDP pages will not be described as analyzed drill-down fields.

## Complexity: T3

This issue will cross identity modeling, deterministic serialization, schema evolution, public-egress/licensing, external HF mutation, race protection, exact-revision verification, security, and a downstream website contract.
