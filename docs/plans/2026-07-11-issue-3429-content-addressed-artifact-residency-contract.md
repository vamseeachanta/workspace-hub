# Plan for [#3429](https://github.com/vamseeachanta/workspace-hub/issues/3429): Content-Addressed Artifact and Hugging Face Residency Contract

> **Status:** adversarial-reviewed (r1 BLOCK remediated; ready for user review)
> **Complexity:** T2
> **Date:** 2026-07-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3429
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** `scripts/review/results/2026-07-11-plan-3429-{claude,codex,gemini}.md`

---

## Resource Intelligence Summary

### Existing repo code

- `assetutilities/src/assetutilities/workflow_api/envelope.py` — the substrate for this contract.
  `result_hash(payload)` already computes a **location-independent content hash** for `kind: files`
  payloads: the canonical form is `sorted((basename, sha256))` per output file, so a changed output
  byte flips a per-file `sha256` and the aggregate hash, while the **absolute directory is discarded**
  (only `basename` survives). `_sha256_hexdigest` hashes UTF-8 bytes; the module already standardizes
  on SHA-256 hex. `input_hash` prunes `VOLATILE_TOP_KEYS = {"Analysis", "default", "cfg_array"}`
  *because those keys "carry absolute paths"* — direct evidence the ecosystem already treats absolute
  paths as unsafe-to-hash / unsafe-to-publish. **These are execution EVIDENCE, not artifact identity:**
  `result_hash` aggregates a *set* of files under a role-blind digest, whereas this contract needs a
  **per-artifact** identity (one digest per immutable byte-object) so Input and Output records can each
  reference the same object. The artifact contract re-uses the per-file `sha256` as the object digest
  and references `result_hash` only as evidence.
- `digitalmodel/…/workflow_api/provenance.py` (`stamp_provenance` → `make_provenance`) stamps
  `input_hash`/`result_hash` into the envelope; no per-artifact record, media type, native format,
  compression, schema reference, or residency-eligibility field exists anywhere.
- **Gap:** no `Artifact` record separating **artifact identity** (immutable bytes) from **artifact role**
  (Input vs Output, which lives on the *referencing* record); no residency-eligibility policy; no
  integrity-from-bytes revalidation that ignores the manifest; no storage-locator safety check.

### Standards

| Standard | Status | Source |
|---|---|---|
| Sibling identity contract (canonical_json + SHA-256 conventions) | binding, consumed | `#3428` plan (`docs/plans/2026-07-11-issue-3428-deterministic-run-identity-contract.md`) |
| Parent run-dataset contract (residency, dedup, exclusions) | binding, extended here | `#3427` plan + `docs/architecture/algorithm-run-dataset-contract.yaml` (in **draft PR #3452**, not on `main`) |
| Publication object-store consumer (`objects/<sha256[:2]>/<sha256>`, re-hash reader) | binding, consumes this | `#3433` plan |
| Legal / per-input license scan | binding | `scripts/legal/legal-sanity-scan.sh`, `.legal-deny-list.yaml` |
| No-absolute-paths / path-leak enforcement | binding | `scripts/enforcement/check-no-abs-paths.sh` |

No engineering-calculation standard applies to this artifact-identity contract.

### Documents consulted

- Issue [#3429](https://github.com/vamseeachanta/workspace-hub/issues/3429) (verified `2026-07-11`,
  title *"standard: content-addressed artifact and Hugging Face residency contract"*, OPEN,
  `status:needs-plan`, `lane:claude`, **Blocked by #3428**): an Artifact represents immutable physical
  bytes or an immutable structured object *independently of its role*; artifacts are addressed by digest
  and deduplicated within the per-repo dataset; carry format, media type, size, schema, integrity,
  provenance, residency; transient logs/caches/large regenerable dumps stay excluded; integrity
  revalidated from dataset bytes without trusting manifest assertions. Acceptance criteria copied
  verbatim below.
- Sibling identity contract [#3428](https://github.com/vamseeachanta/workspace-hub/issues/3428) plan:
  defines `canonical_json` (UTF-8, lexicographically sorted keys, no insignificant whitespace,
  normalized numbers with explicit unit tags, explicit `null`/`"NA"`), digests are **SHA-256 hex**, and
  the load-bearing rule that ResultEnvelope hashes are **evidence, never identity**. This artifact
  contract **reuses that exact canonicalization/digest convention** so a structured-object artifact
  digest is byte-identical to what #3428 would compute, and treats `result_hash`/`input_hash` as
  evidence only.
- Parent [#3427](https://github.com/vamseeachanta/workspace-hub/issues/3427) (verified `2026-07-11`,
  OPEN, `status:plan-approved`): locks one HF dataset per source repo; HF stores replay-critical public
  inputs + curated native outputs; artifacts addressed by digest, **deduplicated within the dataset**;
  transient logs/caches/large regenerable dumps **excluded**. This contract is the digest + residency +
  exclusion mechanism that realizes those locks.
- Publication child [#3433](https://github.com/vamseeachanta/workspace-hub/issues/3433) plan: its dataset
  carries a content-addressed object store `objects/<sha256[:2]>/<sha256>`, dedups identical bytes to one
  object, and its **reader re-hashes object bytes to revalidate integrity WITHOUT trusting the row's
  asserted digest**. This contract makes that byte-revalidation *normative* and supplies the Artifact
  record #3433 serializes (`artifacts[] -> sha256, size, media type, native format, schema ref,
  residency policy`).
- Substrate implementation `assetutilities/…/workflow_api/envelope.py` (fetched `2026-07-11`):
  `result_hash` `kind: files` canonical form `sorted((basename, sha256))` — a working
  location-independent per-file content hash this contract elevates to a first-class per-artifact digest.

### Gaps identified

- No `Artifact` record fixes stable artifact identity (SHA-256 of immutable bytes / canonical form of an
  immutable structured object) with `digest`, `size_bytes`, `media_type`, `native_format`, `compression`,
  `schema_ref`, `storage_locator`.
- No rule that **role lives on the referencing record**, so identical bytes referenced as an Input in one
  run and an Output in another collapse to **one identity**, not two role-tagged copies.
- No residency-eligibility function admitting only replay-critical public inputs + curated native outputs,
  and failing restricted / ambiguous-license / client-specific / path-leaking / non-redistributable bytes.
- No explicit artifact-role **exclusion** policy for transient logs / caches / large regenerable dumps.
- No integrity-from-bytes revalidation, and no storage-locator safety check rejecting local absolute paths
  and path leakage.

### Evidence (verified 2026-07-11)

```text
#3429            OPEN  status:needs-plan lane:claude  "standard: content-addressed artifact and Hugging Face residency contract"  Blocked by #3428
#3428            OPEN  status:needs-plan lane:claude   (identity contract; canonical_json + SHA-256; hashes=evidence)  — this plan's blocker
#3427            OPEN  status:plan-approved            (parent; one dataset/repo, dedup, exclusions)
DRAFT PR #3452   OPEN  feat: define algorithm run ledger for HF datasets  — parent contract YAML NOT on main
EXISTS           assetutilities …/workflow_api/envelope.py  result_hash kind:files = sorted((basename, sha256)) [location-independent]; VOLATILE_TOP_KEYS pruned "carry absolute paths"
EXISTS @main     scripts/legal/legal-sanity-scan.sh, scripts/enforcement/check-no-abs-paths.sh
```

Distinct sources: issue #3429; sibling #3428 plan; parent #3427; publication #3433 plan; ResultEnvelope
`result_hash` implementation; legal + abs-path scanners — more than the required three.

---

## Deliverable

A normative, machine-validated **content-addressed Artifact contract**: the `Artifact` record shape
(digest, size, media type, native format, compression, schema reference, storage locator); the identity
rule that identical bytes → one artifact regardless of how many runs or roles reference it (role lives on
the referencing Input/Output record, never on the artifact); a fail-closed **residency-eligibility**
function (replay-critical public inputs + curated native outputs are HF-eligible; restricted /
ambiguous-license / client-specific / path-leaking / non-redistributable **fail**); an explicit
**artifact-role exclusion** policy (transient logs / caches / large regenerable dumps); a normative
**integrity-from-bytes** revalidation (re-hash dataset bytes, ignore manifest assertions); a
storage-locator safety check (reject local absolute paths and path leakage); valid/invalid fixtures; and
decision-manual lifecycle / deduplication / retention text. A reference implementation proves the digest
and residency checks; this contract does **not** build the uploader, dataset, or any HF write.

---

## Design

### Artifact identity

```text
Artifact                       # immutable bytes OR immutable structured object; ROLE-FREE; BYTE-INTRINSIC ONLY
  digest            IMMUTABLE identity = sha256(STORED bytes)                 # physical byte payload
                    OR         = sha256(canonical_json(structured_object))    # structured objects ONLY, #3428 form
                    SHA-256 hex, exactly the #3428 digest convention. THIS IS THE ARTIFACT IDENTITY.
  size_bytes        exact STORED byte length (of the addressed bytes as they physically reside)
  media_type        IANA media type (e.g. "application/parquet", "text/csv")
  native_format     domain-native format tag (e.g. "csv", "parquet", "openfoam-case", "json")
  compression       explicit codec or "none"; PURELY DESCRIPTIVE metadata — NEVER triggers a decode-before-hash
  schema_ref        pinned schema id+version the artifact validates against (null only if schemaless-by-policy)
  storage_locator   dataset-relative object path "objects/<digest[:2]>/<digest>"  (NEVER an absolute/local path)
  license_evidence_ref   pointer to redistribution-license evidence (decision inputs, not raw creds)
                    # NOTE: NO residency.class / eligible on the artifact — residency is role-derived and lives
                    #       on the referencing Input(#3430)/Output(#3431) record (see "Residency eligibility")
```

**Digest inputs, restated:** for a physical-byte artifact the digest is `sha256` over the **EXACT immutable
STORED bytes** — the very bytes #3433's object store re-hashes — and `size_bytes` is the stored byte length;
`canonical_json` canonicalization (#3428's UTF-8, sorted keys, normalized numbers with unit tags, explicit
null/NA) is reserved **only** for structured-object artifacts. `size_bytes`, `media_type`, `native_format`,
`compression`, `schema_ref`, `storage_locator` are **descriptive metadata about the identity — never inputs
to it** (two byte-identical CSVs with different filenames are one artifact). `compression` is descriptive
only and **never** causes a decode-before-hash: the stored bytes are hashed as they physically reside.

### Identity is role-free; role lives on the reference

```text
Run A: inputs[]  -> InputRef{  role:"boundary_condition", artifact_digest: D }   # #3430 record
Run B: outputs[] -> OutputRef{ role:"curated_result",     artifact_digest: D }   # #3431 record
                              ^ SAME digest D => ONE Artifact in objects/<D[:2]>/<D>
```

Identical bytes resolve to a single artifact identity even across multiple runs and multiple roles. An
Input record and an Output record reference the same artifact by `digest` with **no duplication and no
role ambiguity**, because the **role is a property of the referencing record, not of the artifact**. The
object store is deduplicated within the dataset: `objects/<digest[:2]>/<digest>` holds one copy;
N references share it.

### Residency eligibility (fail-closed) — computed at projection time, not stamped on the artifact

Eligibility is **not** a field on the role-free Artifact record. It is computed at projection time as
**(byte-intrinsic license) × (per-reference role)**, where the role comes from the referencing
Input(#3430)/Output(#3431) record. The `class` (replay_critical_input / curated_native_output / excluded)
and the resulting `eligible` boolean therefore live on the referencing record (or are derived on the fly),
so identical bytes used as a replay_input in one run and a curated_output in another remain **ONE artifact
record** with two differently-classed references (reconciled with Risk #3 below).

```text
eligible_for_public_HF(artifact, referencing_role) := TRUE  iff
                                                  class(referencing_role) ∈ {replay_critical_input, curated_native_output}
                                              AND artifact.license_evidence_ref proves redistributable
                                              AND artifact.storage_locator is SAFE (no absolute/local path, no leak)
                                              AND not client-specific / restricted / ambiguous-license
                                              AND referencing_role is NOT an excluded role (below)
```

Any of the following **FAILS** public projection (no HF residency; fail closed):
restricted / non-redistributable bytes; ambiguous or missing license evidence; client-specific data;
a `storage_locator` that leaks a path (absolute local path, home dir, UNC/drive, `..` traversal); or a
role in the exclusion set. A dataset-level license **cannot** grant redistribution rights absent from the
artifact's own `license_evidence` (mirrors #3433 Gate A per-input license rule).

### Explicit artifact-role exclusion policy

```text
EXCLUDED_ARTIFACT_ROLES = { transient_log, cache, scratch, large_regenerable_dump }
```

Artifacts whose role is transient logs, caches, or large regenerable dumps are **excluded by explicit
policy** from the dataset regardless of digest (they are regenerable and non-replay-critical). Exclusion is
asserted as `class = excluded` **on the referencing Input/Output record** (not on the role-free artifact)
with a reason; it is not silent omission. Note: this role-tag exclusion of "large regenerable dumps" has
**no size backstop** — there is no byte-count threshold here; the large/regenerable determination defers to
role assignment on the #3430/#3431 referencing record.

### Integrity revalidated from bytes (normative, manifest-untrusted)

```text
revalidate(object_bytes, asserted_digest):
    computed = sha256(object_bytes)          # or sha256(canonical_json(...)) for structured objects
    if computed != object_path_digest:  FAIL (tamper / corruption)     # path IS the digest -> self-verifying
    # the manifest row's asserted digest is NEVER trusted as the source of truth:
    if asserted_digest present and asserted_digest != computed:  FAIL (manifest lies)
    return computed                          # bytes are authoritative
```

A reader recomputes the SHA-256 of the object's actual bytes and compares it against the **digest embedded
in the object path** (`objects/<digest[:2]>/<digest>`), which makes each object **self-verifying** and
makes #3433's "re-hash without trusting the manifest" behavior normative. Tampered bytes → digest mismatch
→ FAIL. A manifest whose asserted digest disagrees with the bytes is rejected; the bytes win.

### Storage-locator safety

`storage_locator` MUST be the dataset-relative content-addressed path `objects/<digest[:2]>/<digest>`.
**Normative locator/digest consistency rule:** `storage_locator == "objects/" + digest[:2] + "/" + digest`
EXACTLY — the shard prefix is the first two hex chars of the record's own `digest` and the trailing segment
is the full `digest`; any deviation (mismatched shard, truncated/foreign digest, extra path segments) is
rejected. Also rejected: any absolute path (`/…`, `C:\…`, `\\host\…`), home-relative (`~`), `..` traversal,
or embedded machine/user state. This reuses the `check-no-abs-paths.sh` intent already encoded in
envelope.py's `result_hash` (which keeps only `basename`, discarding the absolute directory).

### Crosswalk (evidence, never identity)

`ResultEnvelope.result_hash` (role-blind set-of-files aggregate) and `input_hash` are retained as
**execution evidence** referenced by run/output records; neither is the artifact identity. The per-file
`sha256` inside `result_hash`'s canonical form is the value elevated to a per-artifact `digest`.

---

## Pseudocode

```text
build_artifact(payload):
    if payload.kind == "bytes":       digest = sha256(payload.stored_bytes)             # hash the EXACT stored bytes
    elif payload.kind == "object":    digest = sha256(canonical_json(payload.object))   # structured objects ONLY, #3428
    size_bytes  = len(payload.stored_bytes)            # stored byte length; compression NEVER decodes before hashing
    locator     = f"objects/{digest[:2]}/{digest}"
    assert locator == "objects/" + digest[:2] + "/" + digest   # exact locator/digest consistency -> else FAIL CLOSED
    assert locator_is_safe(locator)                    # no abs/local path, no leak -> else FAIL CLOSED
    record = Artifact(digest, size_bytes, media_type, native_format, compression, schema_ref, locator, license_evidence_ref)
    return record   # BYTE-INTRINSIC ONLY; NO residency/role field. Role + class are set by the referencing Input/Output record

# residency is computed at PROJECTION time from (byte-intrinsic license) x (per-reference role) — NOT stored on the artifact
classify(artifact, referencing_role) -> residency:
    if referencing_role in EXCLUDED_ARTIFACT_ROLES:      return {class: excluded, eligible: False, reason}
    if not redistributable(artifact.license_evidence_ref): return {eligible: False, reason: "restricted/ambiguous/non-redistributable"}
    if client_specific(referencing_role) or leaks_path(artifact.storage_locator): return {eligible: False, reason}
    if class(referencing_role) in {replay_critical_input, curated_native_output}: return {eligible: True}
    return {eligible: False, reason: "unclassified -> fail closed"}

dedup_into_dataset(records):
    for r in records:  store objects/<r.digest[:2]>/<r.digest> ONCE   # identical digest -> single object, N refs

revalidate_from_bytes(object):                          # reader side; manifest NOT trusted
    computed = sha256(object.bytes)  # or canonical_json for structured
    FAIL if computed != digest_in_path(object) OR (manifest.asserted_digest and manifest.asserted_digest != computed)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Update | `docs/architecture/algorithm-run-dataset-contract.yaml` (**404 on `main`; exists only in parent PR #3452** — this change STACKS ON #3452 as a strictly-additive, non-overlapping section) | add the normative `Artifact` record schema + residency/exclusion policy + integrity-from-bytes rule |
| Create | `assetutilities/src/assetutilities/workflow_api/artifact.py` (**DECIDED reference-impl home** — inherits #3433's owner-confirmed `assetutilities.workflow_api` placement; imported by #3433's publication module) | per-artifact digest (stored bytes, or `canonical_json` for structured objects), residency classifier, locator-safety check, byte-revalidation |
| Create | `assetutilities/tests/workflow_api/test_artifact.py` + `fixtures/artifact/{valid,invalid}/…` | valid/invalid + tampered-byte / hash-mismatch / **dedicated forbidden-residency** / unsupported-schema / unsafe-locator / locator-digest-mismatch fixtures |
| Update | `docs/governance/2026-07-10-algorithm-run-dataset-decision-manual.html` (**404 on `main`; exists only in PR #3452** — additive, non-overlapping section) | artifact lifecycle, deduplication, and retention behavior section |
| Create | `tests/architecture/test_artifact_contract_parity.py` | assert the decision-manual artifact section matches the contract YAML |
| Update | `docs/plans/README.md` | plan index status |

No source-repository algorithm code, workflow registry, dataset, or credential is modified. The
`canonical_json`/SHA-256 helper is **imported from #3428's DECIDED home `assetutilities.workflow_api.identity`**,
not re-implemented. Both files edited here (the contract YAML and the decision-manual) live only in parent
PR #3452, so this and the four sibling contracts (#3428/#3430/#3431/#3433) each land as **strictly-additive,
non-overlapping sections** stacked on #3452 — merged in dependency order or folded into one integration PR.

---

## TDD Test List

| Test | Verifies (acceptance criterion) | Expected |
|---|---|---|
| `test_artifact_identity_fields_present` | AC1: digest, size, media type, native format, compression, schema ref, storage locator all defined | record rejected if any identity field missing |
| `test_bytes_and_structured_digest_use_3428_convention` | AC1: digest = `sha256(bytes)` / `sha256(canonical_json(object))`, SHA-256 hex, matches #3428 | digest byte-identical to #3428 canonicalization |
| `test_metadata_not_in_identity` | AC1/AC2: media type / filename / compression are metadata, not digest inputs | two byte-identical files, different names → same digest |
| `test_identical_bytes_one_identity_across_runs_and_roles` | AC2: identical bytes → one identity across multiple runs/roles | single object id; no duplicate |
| `test_input_and_output_reference_same_artifact_no_role_ambiguity` | AC3: Input + Output records reference same digest; role on the ref, not the artifact | one artifact; two role-tagged refs; artifact role-free |
| `test_replay_input_and_curated_output_are_hf_eligible` | AC4: replay-critical public input + curated native output eligible | `residency.eligible == True` |
| `test_restricted_ambiguous_client_pathleak_nonredist_fail` | AC5: restricted / ambiguous-license / client-specific / path-leaking / non-redistributable fail | each `eligible == False`, fail closed |
| `test_dataset_license_cannot_grant_missing_input_rights` | AC5: dataset-level license cannot override a non-redistributable artifact | still fails |
| `test_excluded_roles_never_reside` | AC6: transient logs / caches / large regenerable dumps excluded by explicit role policy | `class == excluded`, not silently omitted |
| `test_integrity_revalidated_from_bytes_ignores_manifest` | AC7: reader re-hashes bytes, ignores manifest assertion | manifest-asserted digest ignored; bytes authoritative |
| `test_tampered_bytes_fail_hash_mismatch` | AC8 (tampered bytes / hash mismatch): flipped byte → digest ≠ path digest | FAIL |
| `test_manifest_asserts_wrong_digest_rejected` | AC7/AC8 (hash mismatch): manifest digest ≠ computed | FAIL (bytes win) |
| `test_unsupported_schema_ref_rejected` | AC8 (unsupported schema): unknown/unpinned `schema_ref` | rejected, fail closed |
| `test_unsafe_storage_locator_rejected` | AC8 (unsafe locator): absolute/home/UNC/`..`/non-`objects/` path | rejected |
| `test_storage_locator_matches_record_digest` | AC8 (locator/digest consistency): `storage_locator == "objects/" + digest[:2] + "/" + digest` EXACTLY; mismatched shard or foreign/truncated digest | rejected |
| `test_forbidden_residency_fixture_rejected` | AC8 (forbidden residency): dedicated invalid fixture asserting a forbidden residency projection (separate from the AC5 test) | rejected, fail closed |
| `test_valid_fixtures_admit` | AC8: valid fixtures round-trip and admit | pass |
| `test_decision_manual_matches_artifact_contract` | AC9: manual lifecycle/dedup/retention ↔ contract YAML parity | structure + examples agree |

Tests are written first and fail before implementation exists.

---

## Acceptance Criteria

Verbatim from issue #3429:

- [ ] The Artifact contract defines stable artifact identity, SHA-256 digest, byte size, media type, native format, compression, schema reference, and storage locator.
- [ ] Identical bytes resolve to one artifact identity even when referenced by multiple runs or roles.
- [ ] Input and Output records can reference the same artifact without duplication or role ambiguity.
- [ ] Replay-critical public inputs and curated native outputs are eligible for repository-specific Hugging Face storage.
- [ ] Restricted, ambiguous-license, client-specific, path-leaking, or non-redistributable artifacts fail public projection.
- [ ] Transient logs, caches, and large regenerable dumps are excluded by explicit artifact-role policy.
- [ ] Artifact integrity can be revalidated from dataset bytes without trusting manifest assertions.
- [ ] Valid/invalid fixtures cover tampered bytes, hash mismatch, forbidden residency, unsupported schema, and unsafe locator values.
- [ ] The decision manual documents artifact lifecycle, deduplication, and retention behavior.

Added process criteria:

- [ ] TDD tests are written first and fail before implementation; the full suite, the legal scan (`--diff-only`), and `check-no-abs-paths.sh` pass on changed files.
- [ ] The legal/per-input-license scan and the absolute-path/path-leak scan run over every fixture and the contract, and pass.

---

## Sequencing & Gate

**Blocked by #3428** (this contract reuses #3428's `canonical_json` + SHA-256 digest convention and its
"hashes are evidence, never identity" rule; #3428's reference implementation is imported, not duplicated).
Extends the parent contract structure, which is in **draft PR #3452, not yet on `main`** — the contract
YAML and decision-manual are **404 on `main` and exist only in #3452**, so implementation here is **STACKED
ON parent PR #3452** and must not fork the closed-schema behavior. All five sibling contracts
(#3428/#3430/#3431/#3433 + this) edit that YAML + decision-manual as **strictly-additive, non-overlapping
sections**, landing in dependency order (blocker #3428 first) or folded into one integration PR. Requires
its own reviewed plan and explicit user approval (HITL contract work; parent #3427 approval does not
authorize it). The publication child #3433 consumes this contract (its object store + integrity re-reader);
implementation here lands before #3433 code.

---

## Adversarial Review Summary

| Round | Reviewer | Verdict | Findings | Result |
|---|---|---|---|---|
| r1 | Claude | BLOCK | 2 MAJOR — (1) digest hashed decoded/canonical bytes instead of the STORED bytes #3433 re-hashes (breaks self-verifying re-hash + byte-exact replay); (2) role-derived `residency.class`/`eligible` stamped on the role-free Artifact record (violates one-identity-across-roles). Plus MINORs — locator/digest exact-consistency rule missing; no dedicated forbidden-residency fixture; `canonical_json` import home / reference-impl home / #3452 stacking left as open questions. | All remediated: physical artifacts hash exact stored bytes (`canonical_json` reserved for structured objects); byte-intrinsic-only Artifact record with residency computed at projection time on the referencing record; normative locator==digest rule + `test_storage_locator_matches_record_digest`; dedicated forbidden-residency fixture/test; homes decided (`assetutilities.workflow_api.artifact` / `.identity`); stacked additively on PR #3452. |

No unavailable provider counts as approval; any depth reduction is disclosed for owner acceptance.

---

## Risks and Open Questions

- **Structured-object canonicalization coupling:** an artifact that is an immutable structured object must
  hash via #3428's exact `canonical_json`, or a structured artifact digest will diverge from what the
  identity contract computes. Mitigation: import the single #3428 helper; fail closed on version drift;
  a fixture asserts byte-identical digests across the two modules.
- **Compression is descriptive, digest is over stored bytes (DECIDED — not an owner preference):** the
  digest of a physical-byte artifact is `sha256` of the **EXACT immutable STORED bytes** — the same bytes
  #3433's object store re-hashes to self-verify. A decode-before-hash rule was a **correctness bug**: it
  would break the self-verifying re-hash and byte-exact replay, and it created a spurious lossy-codec
  ambiguity. `compression` is purely descriptive metadata and never triggers a decode. This resolves the
  former "compression vs identity" open question — it is no longer an owner decision; decided = hash stored
  bytes, and the lossy-codec ambiguity disappears. `canonical_json` canonicalization applies only to
  structured-object artifacts.
- **Residency-class must not be stamped on the role-free artifact (reconciled with the Design):**
  `class` (replay_critical_input / curated_native_output / excluded) and the `eligible` boolean are
  role-derived and therefore live on the referencing Input (#3430) / Output (#3431) record, or are computed
  at projection time as (byte-intrinsic license) × (per-reference role) — never on the Artifact record.
  This is what keeps identical bytes used as a replay_input in one run and a curated_output in another as
  **ONE artifact record** with two differently-classed references. Mitigation: the classifier takes the
  referencing role as input; an unclassified reference fails closed.
- **Parent-contract coupling / stacking risk:** both files this plan edits (the contract YAML and the
  decision-manual) are **404 on `main` and exist only in parent PR #3452**. Mitigation: this change stacks
  on #3452 as a **strictly-additive, non-overlapping section**; the five sibling contracts
  (#3428/#3430/#3431/#3433 + this) land in dependency order or via one integration PR; fail closed on schema
  drift. The reference-impl home is DECIDED (`assetutilities.workflow_api.artifact`), no longer an open
  question.

---

## Complexity: T2

A normative contract slice with a small deterministic reference implementation + fixtures, in a single
domain, no external platform write, no cross-system transaction. Not T1: it is a load-bearing shared
contract that both Input (#3430) and Output (#3431) records and the publication object store (#3433) bind
to, and its fail-closed residency + integrity-from-bytes proofs gate what reaches a public Hugging Face
surface. Not T3: it neither publishes nor orchestrates a multi-stage promotion — it defines the artifact
record those systems consume.
