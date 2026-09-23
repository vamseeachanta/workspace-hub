# Plan for [#3430](https://github.com/vamseeachanta/workspace-hub/issues/3430): Replayable Public Input and Source Snapshot Contract

> **Status:** adversarial-reviewed (r1 BLOCK remediated; ready for user review)
> **Complexity:** T2
> **Date:** 2026-07-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3430
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** `scripts/review/results/2026-07-11-plan-3430-{claude,codex,gemini}.md`

---

## Resource Intelligence Summary

### Existing repo code

- `assetutilities/src/assetutilities/workflow_api/envelope.py` — `input_hash(cfg)` computes a
  SHA-256 over the caller cfg with **volatile top-level keys pruned**
  (`VOLATILE_TOP_KEYS = {"Analysis", "default", "cfg_array"}`, line 35) because those carry absolute
  paths / machine state. This is **execution evidence, not a replay input set**: it prunes real
  replay-critical inputs, has no per-input structure (role, schema version, redistribution evidence),
  and cannot distinguish a parameter from a dataset snapshot. `make_provenance(...)` (line 81) records
  a single flat `data_as_of` string (line 92) and no snapshot identity, selection, or license. The
  input contract re-derives a **structured, per-input** replay set and references `input_hash` only as
  evidence, never as the canonical input-set identity.
- `worldenergydata/src/worldenergydata/workflow_api/runner.py:238` calls
  `make_provenance(ihash, package_name=PACKAGE_NAME, data_as_of=utc_now_iso())` — i.e. `data_as_of` is
  stamped as a **run wall-clock timestamp** (`utc_now_iso()`), *not* a pinned source-data snapshot. A
  dataset-backed run therefore records *when the code ran*, not *which version of the source data it
  read*, with no selection/query/filter and no redistribution evidence. **This is the substrate gap
  this contract closes: such an input must FAIL public admission.**
- `digitalmodel/docs/registry/workflows.yaml` (`schema_version: 2`) and the dm runner supply the
  landed execution path whose configs become parameter/configuration inputs here; they are consumed,
  not modified.
- **Gap:** no normative Input record separating input *kinds*, no per-input schema-version + canonical
  representation + digest + role + required-for-replay binding, no dataset snapshot-identity /
  selection / redistribution-evidence fields, and no fail-closed admission rule anywhere.

### Standards

| Standard | Status | Source |
|---|---|---|
| Deterministic run identity contract (`canonical_json`, SHA-256, `canonical_input_set_digest`) | binding, consumed | `#3428` plan (this session) |
| Content-addressed artifact + HF residency contract (artifact identity by digest) | binding, consumed | `#3429` (OPEN) |
| Parent run-dataset contract (strict public input policy) | binding, extended here | `#3427` plan + `docs/architecture/algorithm-run-dataset-contract.yaml` (in **draft PR #3452**, not on `main`) |
| Publication projection + egress Gate A (per-input license admission) | binding, downstream consumer | `#3433` plan (this session) |
| Legal / abs-path scans | binding | `scripts/legal/legal-sanity-scan.sh`, `scripts/enforcement/check-no-abs-paths.sh` |
| Issue lifecycle + approval | binding | `AGENTS.md`, `docs/plans/README.md` |

No engineering-calculation standard applies to this input-record contract.

### Documents consulted

- Issue [#3430](https://github.com/vamseeachanta/workspace-hub/issues/3430): distinguishes parameter
  sets, configuration documents, dataset snapshots, public external resources, upstream runs, and
  artifact references; every replay-critical input binds schema version + canonical representation +
  digest + role + required-for-replay; dataset/API inputs additionally record source authority, public
  locator, data-as-of/retrieval time, exact selection/query/filter, snapshot identity, and
  redistribution evidence; canonically-equivalent JSON/YAML yields identical input-set identity;
  missing/mutable-unpinned/restricted/ambiguous-license/private/client-specific/unretrievable inputs
  fail public eligibility; admitted runs reconstruct the complete replay set with no local absolute
  paths or undocumented machine state. Acceptance criteria copied verbatim below.
- Sibling identity contract [#3428](https://github.com/vamseeachanta/workspace-hub/issues/3428) plan
  (read this session): defines `canonical_json` (UTF-8, sorted keys, normalized numbers with explicit
  unit tags, explicit `null`/`NA`) and SHA-256 digests, and binds `run_id` to a
  `canonical_input_set_digest` **owned by this contract (#3430)** — so this contract's canonicalization
  *is* the thing that makes `run_id` deterministic. This plan reuses #3428's `canonical_json`/digest
  verbatim and does not fork it.
- Sibling artifact contract [#3429](https://github.com/vamseeachanta/workspace-hub/issues/3429)
  (OPEN — verified title "standard: content-addressed artifact and Hugging Face residency contract"):
  inputs may **reference** content-addressed artifacts by digest; this contract references artifact
  identity, it does not redefine it.
- Publication child [#3433](https://github.com/vamseeachanta/workspace-hub/issues/3433) plan (read this
  session): its egress **Gate A** does per-input license/redistribution admission and fails closed on
  restricted/pointer-only/unlicensed/unpinned/unhashed/incomplete inputs, and its
  `test_dataset_backed_data_as_of_run_timestamp_fails` asserts the worldenergydata `data_as_of`
  substrate gap is rejected. This contract **defines** those admission rules; the reference impl is
  importable by #3433.
- Parent [#3427](https://github.com/vamseeachanta/workspace-hub/issues/3427) plan: public publication
  requires every replay-critical input to be redistributable, versioned or snapshot-pinned,
  content-hashed, schema-valid, and included in the per-repo HF dataset or publicly retrievable;
  pointer-only restricted inputs do NOT qualify a run for public publication.
- **worldenergydata `data_as_of` gap** (verified in code, see Evidence): the concrete failing example
  that motivates the dataset/API snapshot fields.

### Gaps identified

- No normative Input record enumerates the six input kinds or binds each replay-critical input to
  schema version + canonical representation + digest + role + required-for-replay.
- No dataset/API input records source authority, public locator, data-as-of/retrieval time, exact
  selection/query/filter, snapshot identity, and redistribution evidence — `data_as_of` is a run
  timestamp today.
- No canonical **input-set** digest that (a) equals #3428's `canonical_json`/SHA-256 and (b) makes
  canonically-equivalent JSON/YAML/config produce identical input-set identity.
- No fail-closed admission rule enumerating the disqualifiers, and no valid/invalid fixtures covering
  ordering, numeric canonicalization, missing units, unstable locators, incomplete snapshots,
  forbidden pointer-only, and `data_as_of`-is-run-timestamp.

### Evidence (verified 2026-07-11)

```text
EXISTS  assetutilities …/workflow_api/envelope.py
        input_hash() prunes VOLATILE_TOP_KEYS={"Analysis","default","cfg_array"} (line 35); evidence, not input set
        make_provenance(..., data_as_of=None) flat string; no snapshot/selection/license (lines 81-92)
CONFIRM worldenergydata …/workflow_api/runner.py:238  data_as_of=utc_now_iso()  -> RUN TIMESTAMP, not snapshot  (the gap)
404 @main  docs/architecture/algorithm-run-dataset-contract.yaml   (parent contract in DRAFT PR #3452, not on main)
#3430    OPEN status:needs-plan lane:claude — Blocked by #3428, #3429
#3428    OPEN (identity; owns canonical_json/digest; run_id binds THIS contract's canonical_input_set_digest)
#3429    OPEN "content-addressed artifact and Hugging Face residency contract" (artifact identity referenced here)
#3433    plan-approved — egress Gate A consumes this contract's admission rules
```

Distinct sources: issue #3430; parent #3427 plan; sibling #3428 identity plan; sibling #3429 artifact
issue; publication child #3433 plan; the `envelope.py` `input_hash`/`make_provenance` implementation;
the worldenergydata runner `data_as_of` gap — more than the required three.

---

## Deliverable

A normative, machine-validated **replayable public input + source snapshot contract**: the Input
record shapes for all six input kinds; a per-input binding of schema version + canonical
representation + digest + role + required-for-replay; the additional dataset/API snapshot fields
(source authority, public locator, data-as-of/retrieval time, exact selection/query/filter, snapshot
identity, redistribution evidence); the **`canonical_input_set_digest`** that #3428's `run_id`
consumes; a fail-closed public-admission rule; valid/invalid fixtures; and decision-manual admission +
canonicalization examples. A reference implementation proves canonical-equivalence and admission; the
contract does not build the uploader, the report, or any dataset.

---

## Design

### Input kinds (closed enumeration)

```text
parameter_set          canonical scalar/struct parameters authored for the run (e.g. VIV sweep params) — replay DATA (sweep values, physical parameters); flows through canonical_input_set_digest. DISTINCT from #3428 execution_parameters (run-control knobs); see boundary rule below
configuration_document a config file/document driving the run (dm workflows.yaml row, YAML/JSON cfg)
dataset_snapshot       an IMMUTABLE pinned slice of a source dataset (BSEE, public registries) — snapshot fields REQUIRED; API-backed inputs (data fetched from a live API) are classified HERE, not as a separate kind, so the six kinds stay a CLOSED enumeration and the snapshot-field trigger is well-defined
public_external_resource a stable public resource fetched by URL/DOI (spec, standard table, public file)
upstream_run_reference reference to an already-public upstream run_id in a per-repo HF dataset
artifact_reference     reference to a content-addressed artifact by digest (identity owned by #3429)
```

### Per-input binding (every replay-critical input)

```text
Input
  input_id            stable within the run: "<role>:<slug>"
  kind                one of the six kinds above
  role                semantic role in replay (e.g. "sweep_params", "mesh", "source_dataset")
  required_for_replay bool — if true, its absence/failure fails public admission
  schema_version      pinned schema id+version validating this input's canonical representation
  canonical_repr      canonical_json bytes (#3428) OR, for large payloads, an artifact_reference digest (#3429)
  digest              sha256 over canonical_repr (or the referenced artifact/object digest)   # #3428 algorithm
  license             { spdx | declared_terms, redistribution: allowed|restricted|unknown }   # admission input
```

### `dataset_snapshot` inputs (incl. API-backed) — additional REQUIRED fields (close the `data_as_of` gap)

API-backed inputs are `dataset_snapshot` inputs (see closed enumeration); there is no separate `api`
kind. Every `dataset_snapshot` input additionally REQUIRES:

```text
dataset_snapshot input additionally REQUIRES:
  source_authority    who is authoritative for the data (e.g. "BSEE", "EIA")
  public_locator      STABLE public locator (versioned URL / DOI / dataset revision) — moving/`latest` refs REJECTED
  data_as_of          the SOURCE-DATA snapshot instant/version the slice reflects  (NOT the run wall-clock time)
  retrieval_time      when the slice was retrieved (distinct from data_as_of; both recorded)
  selection           EXACT selection/query/filter that produced the slice (canonicalized: sorted keys, normalized)
  snapshot_identity   content digest of the retrieved slice bytes (pins the immutable snapshot)
  redistribution_evidence  license/terms proving the slice may be publicly redistributed
```

**Admission rule (fail-closed):** the OPERATIVE predicate is **absence of a verifiable pinned
snapshot** — defined as (`snapshot_identity` byte-digest of the retrieved slice ∧ a versioned
`public_locator`). A `dataset_snapshot` input that lacks either — or that lacks `selection` or
`redistribution_evidence` — **FAILS admission**. The `data_as_of == retrieval_time` timestamp
comparison is a **SYMPTOM, not the rule** (a timestamp is spoofable — an input can carry
`data_as_of != retrieval_time` yet still have no pinned snapshot). The worldenergydata
`data_as_of=utc_now_iso()` input is rejected because it has **no `snapshot_identity` and no versioned
`public_locator`** (the missing pinned snapshot), not merely because its timestamp equals the run time.
This is exactly the worldenergydata substrate gap.

### `parameter_set` vs `execution_parameters` boundary (cross-plan seam with #3428)

Adopt the boundary rule now defined in **#3428**: `execution_parameters` = run-**CONTROL** knobs
(tolerances, iteration/step caps, solver flags, seed-adjacent controls) that enter `run_id` **directly**
(via #3428, not through this contract); `parameter_set` (a #3430 Input kind) = replay **DATA** (sweep
values, physical parameters) that flow through `canonical_input_set_digest`. A given parameter is
assigned to **EXACTLY ONE** side by the **algorithm descriptor** — it is never double-counted (never
both a #3428 `execution_parameter` and a #3430 `parameter_set` member). This is a strict partition:
the descriptor is the single source of truth for the assignment. Cross-reference **#3428** for the
`execution_parameters` half of the seam.

### `canonical_input_set_digest` (owned here; consumed by #3428's `run_id`)

The digest is computed over the **identity-bearing dataset subset only** — the fields that establish
*which immutable snapshot* the input is — and EXCLUDES fetch-volatile fields:

```text
identity-bearing dataset subset (enters digest):
  { source_authority, public_locator, data_as_of (source snapshot version), selection, snapshot_identity }

EXPLICITLY EXCLUDED from the digest (recorded on the record, but MUST NOT affect identity):
  retrieval_time            # wall-clock of the fetch — varies per re-fetch of the SAME immutable snapshot
  redistribution_evidence   # license/terms provenance — not part of what the snapshot IS

canonical_input_set_digest = sha256(canonical_json(
    sorted-by-input_id list of { input_id, kind, role, required_for_replay,
                                 schema_version, digest,
                                 [identity-bearing dataset subset above for dataset kinds] }))
```

Including `retrieval_time` or `redistribution_evidence` in the digest would make **re-fetching the same
immutable snapshot produce a new `run_id`**, breaking **#3428** determinism — so both are excluded by
rule. Uses #3428's `canonical_json` verbatim (UTF-8, sorted keys, normalized numbers with explicit unit
tags, explicit `null`/`NA`, declared array order). Therefore **canonically-equivalent JSON/YAML/config
values (key order, whitespace, `1.0` vs `1`) produce an identical `canonical_input_set_digest`** — the
property that makes `run_id` deterministic. A units-bearing numeric input without its unit tag is
**rejected**, not silently hashed (parity with #3428).

### Fail-closed public admission (the rules #3433 Gate A enforces)

An input fails public eligibility (no run is publicly admitted) if it is:
missing / not retrievable; mutable-unpinned (moving/`latest` locator, no snapshot identity);
restricted, ambiguous-license, or unknown-license redistribution; private / client-specific;
pointer-only to a restricted source (a pointer without a redistributable, hashed, retrievable payload);
schema-invalid; missing a required unit tag; or (dataset/API) `data_as_of` is a run timestamp. A
**dataset-level** license never grants rights absent from a specific input's source.

### Complete replay reconstruction (no local state)

An admitted run's complete replay input set reconstructs from the Input records alone — with **no local
absolute paths and no undocumented machine state** (enforced by `check-no-abs-paths.sh` + the canonical
representation excluding host fields).

**Replay-critical input BYTES must be MATERIALIZED** — either as an HF-resident content object
(per **#3429**, artifact identity by digest) or embedded in the record's `canonical_repr`. A stable
public locator is **PROVENANCE, not the reconstruction source**: a locator-only input can rot (404) or
silently mutate, in which case the digest can only **verify** a re-fetch, it cannot **rebuild** the
input. Therefore a `required_for_replay` input is admitted only when its replay bytes are materialized
(HF-resident object or embedded `canonical_repr`); the stable locator is recorded alongside as
provenance. Aligns with **#3429** (HF-resident artifacts).

### Report rendering (#3431 consumer)

The rolling HTML report (#3431) renders, from these records only: a **concise input summary**
(counts by kind, required-for-replay count, dataset snapshots + their `data_as_of`) and a **complete
input inventory** (every Input record with role, digest, locator/snapshot, license). No new data is
introduced at report time.

### Crosswalk (evidence, never identity)

`ResultEnvelope.input_hash` (volatile-key-pruned) is retained as *execution evidence*; it is never
the `canonical_input_set_digest` and never enters `run_id`.

---

## Pseudocode

```text
for each declared input:
    require kind in {parameter_set, configuration_document, dataset_snapshot,
                     public_external_resource, upstream_run_reference, artifact_reference}
    require role, required_for_replay, schema_version
    canonical_repr = canonical_json(value)            # #3428; large payload -> artifact_reference (#3429)
    validate against schema_version                    # fail closed if invalid
    reject if numeric input carries units but no unit tag
    digest = sha256(canonical_repr) OR referenced artifact/object digest
    # parameter vs execution_parameter partition: descriptor assigns EXACTLY ONE side; never both (#3428)
    assert param not in both #3428 execution_parameters and #3430 parameter_set
    if required_for_replay:
        require replay bytes MATERIALIZED (HF-resident object #3429 OR embedded canonical_repr);
                locator-only is provenance, NOT a reconstruction source -> reject if bytes not materialized
    if kind == dataset_snapshot:   # incl. API-backed; no separate `api` kind
        require source_authority, public_locator (versioned, not moving/`latest`),
                data_as_of (SOURCE snapshot version), retrieval_time,
                selection (canonicalized), snapshot_identity (slice byte-digest), redistribution_evidence
        # OPERATIVE predicate: absence of a verifiable pinned snapshot
        FAIL CLOSED if NOT (snapshot_identity byte-digest AND versioned public_locator)
        # data_as_of == retrieval_time is a SYMPTOM (spoofable), not the rule
    admission: FAIL if missing | mutable-unpinned | restricted | ambiguous/unknown license |
               private | client-specific | pointer-only-restricted | schema-invalid | unretrievable
# digest EXCLUDES fetch-volatile retrieval_time + redistribution_evidence (else re-fetch breaks #3428 run_id)
canonical_input_set_digest = sha256(canonical_json(sorted input records
        with dataset identity subset = {source_authority, public_locator, data_as_of, selection, snapshot_identity}))   # -> #3428 run_id
assert reconstructable with NO local absolute paths / undocumented machine state
envelope input_hash recorded as evidence only (never the input-set identity)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Update | `docs/architecture/algorithm-run-dataset-contract.yaml` (STACKED ON parent PR #3452 — the YAML + decision manual 404 on `main`, exist only in #3452) | add the normative Input record schema, six kinds, dataset snapshot fields, `canonical_input_set_digest`, admission rules — as a STRICTLY ADDITIVE, NON-OVERLAPPING section (all five sibling contracts edit this one YAML; land in dependency order or via one integration PR) |
| Create | `assetutilities/src/assetutilities/workflow_api/inputs.py` (reference-impl home DECIDED — inherits #3433's owner-confirmed `assetutilities.workflow_api` placement) | build/validate Input records; compute `canonical_input_set_digest` via #3428 `canonical_json`; fail-closed admission; importable by #3433 |
| Create | `assetutilities/tests/workflow_api/test_inputs.py` + `fixtures/inputs/{valid,invalid}/…` | valid/invalid + canonical-equivalence + admission fixtures |
| Update | `docs/governance/2026-07-10-algorithm-run-dataset-decision-manual.html` (in PR #3452) | input admission + canonicalization examples |
| Create | `tests/architecture/test_input_contract_parity.py` | assert the decision-manual input section matches the contract YAML |
| Update | `docs/plans/README.md` | plan index status |

No source-repository algorithm code, workflow registry, runner, dataset, or credential is modified.
The `assetutilities` and `worldenergydata` runners are consumed/described, not edited under this issue.

---

## TDD Test List

| Test | Verifies (acceptance criterion) | Expected |
|---|---|---|
| `test_input_kinds_are_the_closed_six` | AC1: parameter/config/dataset/public-resource/upstream-run/artifact distinguished | unknown kind rejected; six accepted |
| `test_every_replay_input_binds_schema_repr_digest_role_flag` | AC2: schema version + canonical repr + digest + role + required-for-replay bound | omit any binding → rejected |
| `test_dataset_input_records_snapshot_selection_license` | AC3: source authority, public locator, data-as-of/retrieval, selection, snapshot identity, redistribution evidence | missing any dataset field → rejected |
| `test_data_as_of_run_timestamp_fails_admission` | AC3/AC5: `data_as_of == run timestamp` (wed substrate gap) rejected via MISSING pinned snapshot (no `snapshot_identity`/versioned locator), not the timestamp symptom | rejected (must be pinned source snapshot) |
| `test_refetch_same_snapshot_yields_same_run_id` | AC4/MAJOR-1: re-fetch same immutable snapshot with a DIFFERENT `retrieval_time` (and different `redistribution_evidence` provenance) → identical `run_id` (digest excludes fetch-volatile fields) | identical `run_id` |
| `test_ambiguous_or_unknown_license_fails_admission` | AC5/MAJOR-2: license-ambiguous AND license-absent inputs both rejected (fail-closed) | each rejected |
| `test_parameter_not_double_counted_across_contracts` | MAJOR-3: a param assigned by the algorithm descriptor to EXACTLY ONE side — never both a #3428 `execution_parameter` and a #3430 `parameter_set` member | double-counted param rejected |
| `test_schema_invalid_input_fails_closed` | AC5/MINOR: a present-but-schema-failing input rejected (distinct from missing-binding cases) | rejected |
| `test_canonical_equivalent_json_yaml_same_input_set_identity` | AC4: key order / whitespace equivalence → identical `canonical_input_set_digest` | equal digests |
| `test_numeric_canonicalization_and_missing_unit_rejected` | AC4/AC7: `1.0`==`1`; units-bearing numeric without unit tag rejected | equal digest; unit-less numeric rejected |
| `test_input_ordering_does_not_change_identity` | AC4/AC7: input records sorted by `input_id` before hashing | reordered inputs → same digest |
| `test_missing_mutable_restricted_private_clientspecific_unretrievable_fail` | AC5: each disqualifier fails public eligibility | each rejected |
| `test_unstable_locator_fails` | AC5/AC7: moving/`latest` locator (no snapshot identity) rejected | rejected |
| `test_incomplete_snapshot_fails` | AC7: dataset input missing snapshot identity/selection | rejected |
| `test_pointer_only_restricted_input_forbidden` | AC5/AC7: pointer to restricted source, no redistributable hashed payload | rejected |
| `test_reconstruct_replay_set_has_no_abs_paths_or_machine_state` | AC6: complete replay set reconstructs; no local absolute paths / undocumented machine state | reconstructs; abs-path/host field → fail |
| `test_input_set_digest_feeds_run_id_deterministically` | AC4: digest equals #3428 `canonical_json`/SHA-256 and is what `run_id` binds | identical digest across machines |
| `test_report_renders_summary_and_full_inventory_from_records` | AC8: concise summary + complete inventory rendered from records only | both render; no new data introduced |
| `test_decision_manual_matches_input_contract` | AC9: manual admission/canonicalization examples ↔ contract YAML parity | structure + examples agree |
| `test_valid_and_invalid_fixtures_cover_all_named_cases` | AC7: ordering, numeric canon, missing units, unstable locators, incomplete snapshots, forbidden pointer-only | fixtures present and each asserted |
| `test_envelope_input_hash_is_evidence_not_input_set_identity` | crosswalk: `input_hash` never the `canonical_input_set_digest` | identity independent of `input_hash` |

Tests are written first and fail before implementation exists.

---

## Acceptance Criteria

Verbatim from issue #3430:

- [ ] The Input contract distinguishes parameter sets, configuration documents, dataset snapshots, public external resources, upstream runs, and artifact references.
- [ ] Every replay-critical input binds to a schema version, canonical representation, digest, role, and required-for-replay flag.
- [ ] Dataset and API inputs record source authority, public locator, data-as-of or retrieval time, exact selection/query/filter, snapshot identity, and redistribution evidence.
- [ ] Canonically equivalent JSON/YAML/configuration values produce identical input-set identities.
- [ ] Any missing, mutable-unpinned, restricted, ambiguous-license, private, client-specific, or unretrievable replay input fails public eligibility.
- [ ] Every admitted run can reconstruct its complete replay input set without local absolute paths or undocumented machine state.
- [ ] Valid/invalid fixtures cover ordering, numeric canonicalization, missing units, unstable locators, incomplete snapshots, and forbidden pointer-only cases.
- [ ] The rolling HTML report can render a concise input summary and complete input inventory from these records.
- [ ] The decision manual documents input admission and canonicalization examples.

Plus process gates:

- [ ] Tests are written first; the suite, the legal scan (`scripts/legal/legal-sanity-scan.sh --diff-only`), and `scripts/enforcement/check-no-abs-paths.sh` pass on changed files.
- [ ] Per-input license/redistribution admission fails closed on restricted / ambiguous / unknown / pointer-only inputs (the rules #3433 egress Gate A enforces).

---

## Sequencing & Gate

**Blocked by #3428** (owns `canonical_json` + SHA-256 + the `canonical_input_set_digest` this contract
computes, and the `execution_parameters` half of the parameter boundary) **and #3429** (owns artifact
identity that `artifact_reference` inputs cite). Implementation is **STACKED ON parent PR #3452**: the
contract YAML (`algorithm-run-dataset-contract.yaml`) and the decision manual **404 on `main`** and
exist only in #3452, so this work branches from #3452, not `main`. All **five sibling contracts** edit
that one YAML; each adds a **STRICTLY ADDITIVE, NON-OVERLAPPING** section, and they land **in dependency
order or via a single integration PR** to avoid overlapping edits. This plan coordinates the Input
schema with #3452 and must not fork the closed-schema behavior. Downstream, #3433's egress Gate A and
#3431's report consume this contract; the reference implementation is importable by #3433. Requires its
own reviewed plan and **explicit user approval (HITL contract work)** — parent #3427 approval does not
authorize it.

---

## Adversarial Review Summary

| Round | Reviewer | Verdict | Result |
|---|---|---|---|
| r1 | Claude | BLOCK | 3 MAJOR (digest field membership excludes fetch-volatile `retrieval_time`/`redistribution_evidence`; ambiguous/unknown-license admission test; `parameter_set`↔`execution_parameters` boundary + no-double-count) + MINORs (data_as_of admission teeth = missing pinned snapshot; API-backed = `dataset_snapshot`; schema-invalid fail-closed; replay-byte materialization) — **all remediated** |

No unavailable provider counts as approval; any depth reduction is disclosed for owner acceptance.

---

## Risks and Open Questions

- **`data_as_of` semantic-overload risk:** the field currently means "run time" in the wed runner;
  reusing the name for a *source snapshot* invites confusion. Mitigation: the contract records
  `data_as_of` (source snapshot version) **and** `retrieval_time` (fetch instant) as *distinct*
  fields, and admission fails closed when they are indistinguishable — the run timestamp is never a
  valid snapshot.
- **Selection-canonicalization risk:** an "exact selection/query/filter" can be expressed many
  equivalent ways (SQL vs param dict, key order). Mitigation: `selection` is canonicalized with the
  same #3428 `canonical_json` so equivalent queries yield one identity; free-form query strings that
  cannot be canonicalized are rejected as ambiguous.
- **Pointer-vs-payload boundary risk:** an `upstream_run_reference` / `artifact_reference` is a pointer
  by design, yet the contract forbids pointer-only restricted inputs. Mitigation: a reference is
  admissible **only** when its target is itself publicly retrievable and hashed (already-public HF run
  / content-addressed object per #3429); a pointer to a restricted or private source fails.
- **Parent-contract coupling / stacked-PR risk:** the contract YAML and decision manual exist only in
  **draft PR #3452** (404 on `main`); this work is STACKED ON #3452. All five sibling contracts edit
  that one YAML. Mitigation: each contributes a **strictly additive, non-overlapping** section; land in
  dependency order or fold into **one integration PR**; branch from #3452 (not `main`); coordinate the
  Input schema with #3452 and fail closed on schema drift.
- **Reference-implementation home — DECIDED:** `assetutilities.workflow_api.inputs` (inherits #3433's
  owner-confirmed `assetutilities.workflow_api` placement; #3433's publication module and #3431's report
  import one implementation, matching #3428's `identity.py` sibling). No longer an open question.

---

## Complexity: T2

A normative contract slice with a small deterministic reference implementation + fixtures. Not T3:
single-domain, no external platform commit, no cross-system transaction — but it owns the
`canonical_input_set_digest` that makes `run_id` deterministic and defines the fail-closed admission
rules #3433's egress Gate A enforces, so its canonicalization and admission proofs are load-bearing
for every downstream public publication.
