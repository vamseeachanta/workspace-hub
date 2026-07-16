# Plan for worldenergydata #1045: Deterministic exact-revision HF browser snapshot

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-16
> **Issue:** https://github.com/vamseeachanta/worldenergydata/issues/1045
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:codex
> **Execution mode:** planning/review `parallel-readonly`; implementation `parallel-worktree` for pure builder/tests, serialized single-lane for live publication
> **Round 1 artifacts:** `scripts/review/results/issue-1045-round-1/2026-07-16-plan-1045-claude.md` | `...-codex.md` | `...-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/hf_export/build_explorer_results_bundle.py` currently combines `_explorer.json` and `_atlas_feed.json`, sanitizes non-finite numbers, and writes source hashes. It currently declares obsolete dataset identity `worldenergydata`, does not record a clean source Git SHA, and does not emit the proposed relational browser contract.
- `scripts/hf_export/publish_explorer_refresh_to_hf.py` currently downloads floating `fields.parquet`, patches it, and uploads only `fields.parquet`, `parametric_economics.parquet`, and `README.md`. It will not rebuild wells/countries, use expected-parent protection, capture the returned SHA, or exact-SHA read back bytes.
- `tests/unit/site/test_explorer_results_bundle.py` currently tests strict JSON/counts but preserves the obsolete identity and has no publication transaction or browser-manifest coverage.
- `config/fields.yml` is the canonical field identity registry. It separates stable canonical IDs from labels, aliases, leases, and FDP slugs.
- `packages/worldenergydata-core/src/worldenergydata/common/fields_registry.py` supplies fail-closed canonical resolution and duplicate checks through `worldenergydata.common.fields_registry`.
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

The quantitative inventory was inspected at clean baseline `a26881d49d064ea6ae6c8200ae1a874bf944e1bb`. Live `worldenergydata/main` was `090228fb4a1193e4190fc4da90644d9f40a20b5a` at review time, 21 commits ahead; comparison showed none of the named Explorer inputs changed, but implementation will still fetch and re-run every inventory/hash check against fresh `main`.

```text
current _explorer.json sha256: 29ae5ea119ac28f0a24c8f1107d5b74b14bb99c2c56e94a70efb9b6d8ae07082
bundle-recorded explorer sha:   fc79569c7417d2b7f3239d8d14d96e2076145751ac1e63ef19273c17e2c3e92e
current _atlas_feed.json sha:   50e039377705d8ee71ba520b55ea2583317d90b88eb0e41924d96fe0cb8ba32c
bundle dataset identity:        worldenergydata
canonical live dataset:         aceengineer/worldenergydata-explorer
```

Current well proof: 56 wells, 56 unique `api` values, every API is 12 digits, and field counts are Jack/St. Malo 24, Stones 10, Big Foot 8, Julia 4, Shenandoah 4, Anchor 3, Cascade/Chinook 3.

**Immutable-read reproduction:** datasets-server returned identical HTTP 200 bytes for the real HF SHA and a fabricated all-zero SHA; raw `resolve/<fake-sha>/...` returned 404. Immutable verification will therefore use raw exact-SHA files only.

### Embedded commands and captured output

```bash
gh issue view 1045 -R vamseeachanta/worldenergydata --json number,title,state,labels
git -C worldenergydata rev-parse HEAD
git ls-remote https://github.com/vamseeachanta/worldenergydata.git refs/heads/main
test -f worldenergydata/packages/worldenergydata-core/src/worldenergydata/common/fields_registry.py
sha256sum worldenergydata/reports/lower_tertiary/lifecycle/_explorer.json \
  worldenergydata/reports/field-atlas/_atlas_feed.json
```

Captured 2026-07-16: issue `OPEN`, `status:needs-plan`, `lane:codex`; baseline `a26881d...`; live main `090228fb...`; actual registry path existed; hashes were respectively `29ae5ea1...` and `50e03937...`. The exact datasets-server probe commands and `200 / 3928 bytes / f414935f...` omitted-real-fake output are embedded in the parent plan.

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
| Source-license admission registry | `config/hf_export/field_explorer_source_licenses.yml` |
| Manifest schema | `config/schemas/field_explorer_browser_manifest.schema.json` |
| Record schema | `config/schemas/field_explorer_browser_records.schema.json` |
| Publish-receipt schema | `config/schemas/field_explorer_publish_receipt.schema.json` |
| Existing bundle builder | `scripts/hf_export/build_explorer_results_bundle.py` |
| Deprecated publisher | `scripts/hf_export/publish_explorer_refresh_to_hf.py` |
| Human contract | `docs/data/field-explorer-hf-browser-snapshot.html` |
| Tests | `tests/unit/site/test_explorer_snapshot.py`, `tests/unit/site/test_explorer_snapshot_publisher.py`, existing bundle tests |
| Contract fixtures | `tests/fixtures/hf_export/field_explorer_browser/` |
| Tracked bundle/card | `reports/field-atlas/results/explorer_results_bundle.json`, `README.md` |
| Publisher core receipt | `reports/field-atlas/results/explorer_publish_receipt.json` |
| Protected publisher workflow | `.github/workflows/publish-field-explorer-snapshot.yml` |
| Attested CI evidence envelope | Parent #3559 will compose it after run completion from live Actions API metadata and the attested publisher artifact |

---

## Deliverable

A deterministic publisher will build normalized fields, wells, countries, economics, bounded browser JSON shards, Parquet tables, card, and manifest from one clean worldenergydata commit; publish all bytes in one expected-parent HF commit; raw-read every declared artifact by the returned SHA; and emit a receipt only after full verification.

The live mutation will run only from the exact allowlisted `.github/workflows/publish-field-explorer-snapshot.yml` `workflow_dispatch` on the protected target ref, reviewed head SHA, and `field-explorer-publish` environment. The workflow will reject fork/PR events and rerun attempts, pin every action to a full commit SHA, and require the configured automation actor plus protected-environment approval policy. The publisher core receipt will contain only facts available before artifact upload: source/HF identities, operation set, exact readback, counts and hashes. The workflow will upload and attest that receipt/evidence. After the run finishes, parent #3559 will live-fetch the run conclusion, workflow/environment approval, artifact ID/digest and attestation and compose the external provenance envelope; no receipt will self-reference its later artifact or conclusion.

Repository-admin provisioning is a named prerequisite, not implicit code: the worldenergydata owner will create the `field-explorer-publish` environment, required-reviewer policy, automation-actor allowlist and `HF_TOKEN` secret. The workflow will include a read-only preflight that verifies these settings and will stop before local implementation can request live publication if they are absent. Architecture/plan approval will not authorize creating secrets or changing repository settings.

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

The content snapshot ID will be derived from canonical logical record bytes before paths/manifest serialization. Each field/well will carry a safe immutable `field_route_key`/`well_route_key` derived from its stable ID; mutable display slugs will remain aliases and cannot redefine canonical URLs. The manifest will contain schema version, dataset ID, clean source Git SHA, generator version, source hashes, every artifact path/hash/bytes/media type/records/schema, primary/foreign keys, declared sorting, readiness, provenance, license classification, and explicit zero-well representation. It will not contain its own HF commit SHA. The closed publish-receipt schema will bind source Git SHA, HF parent/returned SHA, manifest path/hash, operation set, exact-readback results, counts, generator/tool versions, timestamps, verification status, and referenced evidence hashes; unknown fields and schema majors will fail.

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
    validate source hashes and dataset identity
    require each source/column lineage maps to an owner-reviewed license record
    require authority, source URL, license, redistribution basis/evidence and status
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
    raw-read browser/manifest.json separately at returned_sha
    compare staged bytes; hash, parse and schema-validate exact returned manifest
    for artifact in manifest: raw-read at returned_sha and revalidate bytes/hash/schema/count
    write publisher core receipt atomically only after every check passes
    workflow uploads+attests core receipt; parent composes post-run provenance envelope
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
| Create | `config/hf_export/field_explorer_source_licenses.yml` | source/column lineage, authority, public URL, license, redistribution evidence, reviewer and status |
| Create | three JSON schemas under `config/schemas/` | closed record, manifest, and publish-receipt contracts |
| Modify | `pyproject.toml`, `uv.lock` | declare/pin `huggingface-hub`, Parquet/schema runtime and clean locked install |
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
- Route-key guard: stable-ID-derived route keys remain safe and unchanged across label/display-slug changes;
11. synthetic >100 records shard deterministically without loss/duplication;
12. record and byte shard bounds are enforced; browser shards remain regular-blob sized;
13. manifest hashes/bytes/media/counts/schema match staged files;
14. manifest schema rejects any HF commit SHA property;
15. JSON and Parquet have logical parity for all four configs;
16. surfaced-economics filtering is explicit and discovered counts match policy;
17. existing analytical columns remain or carry a versioned migration.
- Compatibility guard: the live website `field-economics-sensitivity` consumer will receive an unchanged compatible `parametric_economics` config/schema or a separately reviewed migration before publish.

### Publisher

18. dry-run uses no token, writes no network state, and emits no receipt;
19. live mode invokes one `create_commit` containing every artifact;
20. `parent_commit` equals the preflight head; a race fails with no receipt;
21. invalid/missing returned SHA fails closed;
22. exact-SHA manifest bytes equal staging and independently pass hash/schema validation;
23. every verification URL contains the returned exact SHA and no floating ref;
24. no code path uses datasets-server for immutable verification;
25. missing/tampered/recount/schema/readback failures emit no receipt;
26. fixture tests bound the same-origin exact-SHA cache redirect and reject off-origin/multi-hop forms;
27. a non-mutating live HF probe records actual manifest/shard redirect chain, status, revision and timestamp before publication;
28. token/auth values never enter logs, exceptions, manifest, receipt or artifact;
29. success writes one core receipt; post-upload failure records only an unpromoted orphan;
30. live mode refuses execution outside the exact protected workflow/environment policy;
31. parent rejects wrong workflow/event/ref/actor/attempt/action pin/environment, fork run or artifact digest;
32. expected-parent conflict requires a fresh explicit run, not automatic retry;
33. clean `uv sync --locked` imports every declared publisher runtime dependency;
34. missing/unreviewed source-license evidence or output-column lineage fails before staging.

### Executable fixture boundaries

| Slice | Input | Expected output |
|---|---|---|
| identity/join | duplicate, orphan, alias and zero-well fixtures | typed rejection or canonical sorted records |
| deterministic build | same fixture under two paths/locales | byte-identical JSON/Parquet/card/manifest |
| scale | 101+ records and byte-boundary cases | complete deterministic shards with no loss/duplication |
| legal admission | complete vs missing/unreviewed lineage records | staged snapshot vs fail-closed evidence error |
| HF transaction | fake API parent race, SHA, redirect and tamper cases | one commit/core receipt or no receipt |
| immutable readback | staged manifest plus exact returned bytes | separate manifest equality then all declared artifacts verified |
| CI provenance | fake live Actions/environment/artifact responses | exact allowlist accepted; every variant rejected |
| clean environment | fresh locked dependency install | publisher imports and focused tests pass |

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
- [ ] The exact-SHA manifest itself will be fetched, byte-compared, hashed, parsed and schema-validated before any declared artifact loop.
- [ ] The manifest will not self-reference an HF SHA; the receipt and website registry will bind it externally.
- [ ] Any preflight/upload/race/readback failure will prevent receipt and website promotion.
- [ ] Live publication will run only through the protected manual GitHub Actions environment and will emit evidence that parent #3559 can verify against the live Actions API and artifact digest.
- [ ] Repository-admin environment/reviewer/actor/secret setup will be an explicit owner prerequisite and read-only preflight; plan approval will not authorize those settings or secrets.
- [ ] Dry-run will make no external writes; live auth will be environment/client backed and redacted.
- [ ] Browser JSON will be bounded regular Git blobs; redirect validation will include fixtures plus a timestamped non-mutating live probe.
- [ ] Every public source and output-column lineage will have owner-reviewed authority, URL, license and redistribution evidence; scanner exclusions/binary Parquet will not substitute for this registry.
- [ ] `pyproject.toml` and `uv.lock` will declare the publisher runtime and a fresh `uv sync --locked` will pass.
- [ ] Existing consumers will remain compatible or receive an explicit versioned migration.
- [ ] Shared-dataset consumer `field-economics-sensitivity` will pass config/schema/row-policy compatibility checks before the HF commit becomes publishable.
- [ ] Legal/security scans, focused/full tests, code review, implementation issue comment, cleanup audit, and completeness gate will pass.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | wrong registry path, admin prerequisite, redirect evidence, scope/numbering |
| Codex | MAJOR | stale baseline, dependencies, receipt sequence, manifest readback, legal admission, embedded evidence |
| Gemini | UNAVAILABLE | no non-interactive authentication configured |

**Round 1 result:** MAJOR/MINOR split. Findings are absorbed inline, but no second automatic child round will run while parent #3559 remains blocked; this issue remains `status:needs-plan`.

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
