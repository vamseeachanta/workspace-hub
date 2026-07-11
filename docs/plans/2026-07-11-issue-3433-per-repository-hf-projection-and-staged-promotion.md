# Plan for [#3433](https://github.com/vamseeachanta/workspace-hub/issues/3433): Per-Repository Hugging Face Projection and Staged Promotion

> **Status:** plan-review (adversarial self-review r1 remediated + r2-verified NO-MAJOR; owner-reviewed the two placement/namespace decisions)
> **Complexity:** T3
> **Date:** 2026-07-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3433
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** `scripts/review/results/2026-07-11-plan-3433-claude.md` | `...-codex.md` | `...-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- **Parent contract source (not yet on `main`).** `docs/plans/2026-07-10-issue-3427-repository-linked-algorithm-run-datasets.md`,
  `docs/governance/2026-07-10-algorithm-run-dataset-decision-manual.html`, and the planned
  `docs/architecture/algorithm-run-dataset-contract.yaml` exist at commit
  `01054d8d7a499e54c70abfdf0317b7c8b0463a92` but that commit has **diverged** from
  `origin/main` (verified `2026-07-11` via `gh api .../compare/01054d8d...HEAD` → `diverged`;
  `gh api .../contents/...@main` → `404` for all three). This publication child **consumes**
  those contracts, so its implementation is sequenced *after* the parent contract and the
  record-schema children (#3428–#3432) land on `main`. The plan therefore fixes the record
  *shape* it depends on and adds a version-pinned compatibility check rather than assuming
  the schemas are present.
- `assetutilities/src/assetutilities/workflow_api/envelope.py` supplies the shared
  `ResultEnvelope`, `code_version()` (`{package_version, git_sha}`), a volatile-key-pruned
  `input_hash` (`VOLATILE_TOP_KEYS = {"Analysis", "default", "cfg_array"}`), a location-
  independent content `result_hash` for `kind: files`, and `reproducible` (`None` unless an
  opt-in double run is requested). **Gap:** `git_sha` does not prove a clean tree and
  `input_hash` prunes real top-level inputs, so these are *execution evidence*, not strict
  public identity. The projection envelope will re-bind identity and reference these values
  as evidence only — never alias them.
- `digitalmodel/src/digitalmodel/workflow_api/{runner,provenance,golden}.py` and
  `docs/registry/workflows.yaml` (`schema_version: 2`, versioned `<repo>:<id>@N` routing,
  `status`/`latest` triple) supply the landed runner, the `stamp_provenance` assembler
  (delegates to `assetutilities…make_provenance`, parameterized by `package_name`), the
  golden harness, and workflow goldens. The publisher will **crosswalk** these surfaces as
  evidence inputs; it will not re-create a runner or alias the integer registry `version`
  as the semantic algorithm version.
- `worldenergydata/src/worldenergydata/workflow_api/runner.py` consumes the same envelope but
  currently stamps `data_as_of` as a run timestamp, not a pinned source-data snapshot; the
  public input contract (#3430) requires the snapshot form. The publisher fails closed when
  `data_as_of` is a run timestamp for a dataset-backed algorithm.
- **Gap:** no reusable projection, dataset-schema writer, staged-promotion state machine,
  HF client with post-upload object verification, egress/legal/secret gate composition,
  report-pin, or append-only Publication record exists anywhere in the ecosystem.

### Standards

| Standard | Status | Source |
|---|---|---|
| Issue lifecycle and user approval | binding | `AGENTS.md`, `docs/plans/README.md` |
| Parent run-dataset contract (identity, records, states, exclusions) | binding, consumed | `#3427` plan + `docs/architecture/algorithm-run-dataset-contract.yaml` (pending merge) |
| Record-schema children (identity/artifact/input/output/metric) | binding, consumed | `#3428`, `#3429`, `#3430`, `#3431`, `#3432` |
| Data/execution/report boundaries | reusable, extension required | `docs/architecture/execution-manifest.schema.yaml`, `docs/architecture/report-evidence-bundle.schema.yaml` |
| Legal/public-egress scan | binding | `scripts/legal/legal-sanity-scan.sh`, `.legal-deny-list.yaml` |
| No-absolute-paths enforcement | binding | `scripts/enforcement/check-no-abs-paths.sh` |
| Ecosystem public-egress validator | consumed **when available**; bounded compatibility dependency until then | `#3013` (Phase B validator) under `#2975` (Phase A contract) |
| Control-plane discovery | applicable | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Hugging Face upload / commit / revision semantics | applicable external platform contract | <https://huggingface.co/docs/huggingface_hub/guides/upload>, <https://huggingface.co/docs/hub/datasets-cards> |

No engineering calculation standard applies to this publication-infrastructure issue; the
pilot algorithms (dm #1505, wed #927) retain their own calculation citation obligations.

### LLM Wiki pages consulted

- No domain wiki page governs cross-repository run publication. Per the durable/transient
  boundary, the normative architecture is the parent contract YAML + decision manual; GitHub
  issues, this plan, and review artifacts are execution-state evidence.

### Documents consulted

- Issue [#3433](https://github.com/vamseeachanta/workspace-hub/issues/3433) body + owner
  comment: fixes the emit→validate→replay→draft→review→HF-candidate→pin→verify→append-only
  acceptance sequence, the "acceptance not visibility" atomicity rule, the candidate-
  ineligibility invariant, the HF-success-then-pin/verify-failure recovery requirement, the
  "no unavailable review channel counts as approval" rule, and the independent child gate.
- Parent [#3427](https://github.com/vamseeachanta/workspace-hub/issues/3427) plan (read at
  `01054d8d`): one dataset per repo, catalog-only aggregation, strict public input policy,
  failed-run analysis-ineligibility, byte identity vs versioned semantic equality digest,
  ResultEnvelope-as-evidence crosswalk, HF-as-storage-only for replay-critical inputs +
  curated outputs.
- Blocking children [#3428](https://github.com/vamseeachanta/workspace-hub/issues/3428)
  (deterministic run identity + algorithm version), [#3429](https://github.com/vamseeachanta/workspace-hub/issues/3429)
  (content-addressed artifact + HF residency), [#3430](https://github.com/vamseeachanta/workspace-hub/issues/3430)
  (replayable public input + snapshot), [#3431](https://github.com/vamseeachanta/workspace-hub/issues/3431)
  (curated output + rolling HTML report), [#3432](https://github.com/vamseeachanta/workspace-hub/issues/3432)
  (algorithm-scoped metric): supply the record shapes the projection serializes. **All five
  are `status:needs-plan`** — an explicit ordering constraint recorded below.
- Ecosystem [#2975](https://github.com/vamseeachanta/workspace-hub/issues/2975) (flywheel
  manifest/provenance/routing) and [#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013)
  (public-egress validator + allowlist-only public projection, deny-list-inside-allowed-values,
  public identity registry): the publisher composes these controls when present and records a
  bounded shim until then, per #3433 acceptance criterion 10.
- Pilots [digitalmodel #1505](https://github.com/vamseeachanta/digitalmodel/issues/1505)
  (public synthetic VIV parametric: ≥3 variations + 1 exact replay, clean-room reproduce) and
  [worldenergydata #927](https://github.com/vamseeachanta/worldenergydata/issues/927) (public
  BSEE): both are `Blocked by #3433` and are the first consumers of the workflow this plan
  designs. dm [#1528](https://github.com/vamseeachanta/digitalmodel/issues/1528) (coupled
  sloshing CFD, `status:plan-approved`) is a *future producer* whose per-run machine-readable
  manifest (input hashes, solver version, case hash, output files, report hash) is a concrete
  test of the projection envelope's domain-native output handling.
- Hugging Face upload docs: `create_commit` gives a single atomic commit returning an exact
  revision; `preupload_lfs`/large-file handling and content-addressed storage support the
  additive-shard + blob-store layout; dataset cards carry machine-readable metadata.

### Gaps identified

- No projection record binds the strict public identity (clean commit, input/output schema
  versions, environment digest, seed, execution params) to the five domain-native record
  categories in one machine-readable, serialize-ready envelope.
- No dataset-schema writer emits per-repository Parquet/JSONL tables plus a deduplicated
  content-addressed object store, and no reader re-validates artifact integrity from dataset
  bytes without trusting the manifest.
- No promotion state machine enforces the nine gates, keeps Run records immutable across
  candidate→accepted, and treats a visible HF candidate as analysis-ineligible until an
  append-only Publication record accepts it.
- No HF client authenticates from the environment, creates an immutable single-commit
  revision, re-downloads and re-hashes every content-addressed object post-upload, and
  guarantees tokens never reach logs or reports.
- No egress gate composes legal + secret + absolute-path + per-input license resolution and
  defers to the #3013 ecosystem validator when available with a recorded bounded shim.
- No promotion journal makes an interrupted promotion resumable or safely rolled back,
  including the HF-success-then-pin/verify-failure recovery paths.

### Evidence (embedded verification)

**Issue / ref statuses** (verified `2026-07-11` via `gh`):

```text
#3433                    OPEN  status:needs-plan, lane:codex, publication child (this plan)
#3428..#3432             OPEN  status:needs-plan  (record-schema contracts this plan consumes)
#3427                    OPEN  status:plan-approved (parent); contract artifacts diverged from main
digitalmodel #1505       OPEN  status:needs-plan  Blocked by #3433 (synthetic pilot, first consumer)
worldenergydata #927     (parent-plan-referenced public BSEE pilot, Blocked by #3433)
digitalmodel #1528       OPEN  status:plan-approved (future producer: CFD run manifest)
#2975 / #3013            OPEN  ecosystem flywheel contract + public-egress validator
```

**Ref existence / divergence** (verified `2026-07-11`):

```text
DIVERGED  workspace-hub 01054d8d...origin/main  (parent contract commit not on main)
404 @main docs/plans/2026-07-10-issue-3427-...md
404 @main docs/governance/2026-07-10-algorithm-run-dataset-decision-manual.html
404 @main docs/architecture/algorithm-run-dataset-contract.yaml
EXISTS    docs/architecture/execution-manifest.schema.yaml (on main)
EXISTS    scripts/legal/legal-sanity-scan.sh, scripts/enforcement/check-no-abs-paths.sh (on main)
EXISTS    assetutilities …/workflow_api/envelope.py  (ResultEnvelope, make_provenance)
EXISTS    digitalmodel …/workflow_api/{runner,provenance,golden}.py; docs/registry/workflows.yaml (schema_version 2)
```

**Reproduction proofs:** N/A. This is a publication-infrastructure design; it alleges no
runtime regression. The divergence check above is a read-only sequencing probe.

Distinct sources: issue #3433 + owner comment; parent #3427 plan; five record-schema children;
two ecosystem controls; two pilots + one future producer; ResultEnvelope + provenance
implementations; dm registry; three official Hugging Face pages — more than the required three.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-11-issue-3433-per-repository-hf-projection-and-staged-promotion.md` |
| Publication decision note (design companion) | `docs/governance/2026-07-11-hf-projection-staged-promotion-notes.md` |
| Reusable projection + promotion library | `assetutilities/src/assetutilities/workflow_api/publication/` (DECIDED home — owner-confirmed 2026-07-11) |
| Per-repository publication config | `<repo>/docs/registry/publication.yml` (dataset target + algorithm→report mappings; no creds/paths) |
| Projection record schema | `assetutilities/src/assetutilities/workflow_api/publication/schemas/*.schema.json` |
| Contract / behavior tests | `assetutilities/tests/workflow_api/publication/` |
| Plan review — Claude / Codex / Gemini | `scripts/review/results/2026-07-11-plan-3433-{claude,codex,gemini}.md` |

The unsuffixed provider paths hold the latest review used for the live gate; immutable round
snapshots use `-<provider>-rN.md` and name the exact revision reviewed.

---

## Deliverable

A reusable, credential-free, machine-validated **projection and staged-promotion workflow**
that takes an owning repository's locally emitted run envelopes, admits only public-safe
reproducible runs, publishes them to that repository's dedicated Hugging Face dataset at an
immutable verified revision, pins the source-repository rolling report to that revision, and
records acceptance in an append-only Publication log — resumable or safely rolled back at every
stage, with no run ever visible as "accepted" until cross-system verification passes.

**This plan does not implement the uploader.** It defines the run envelope, the dataset schema,
the promotion state machine, the immutable-revision + object-verification behavior, the
egress/legal/secret gate, and the rollback/resume behavior, plus a first-fail TDD list. Code
lands only after this plan is adversarially reviewed and explicitly approved, and after the
parent contract (#3427) and the record-schema children (#3428–#3432) are on `main`.

---

## Design

### 1. Projection-ready run envelope

A `RunProjection` record is the local, pre-publication, serialize-ready superset of the
execution `ResultEnvelope`. It binds **strict public identity** and the five domain-native
record categories, and references execution-evidence hashes without aliasing them as identity.

```text
RunProjection
  identity:
    repository            {repo, owning_dataset}          # one dataset per repo; catalog indexes, never combines
    algorithm_id          stable id (e.g. "digitalmodel:viv-parametric")
    algorithm_version_id  = H(semver, clean_git_commit, input_schema_ver, output_schema_ver, env_digest)   # #3428
    run_id                = H(algorithm_version_id, canonical_input_set_digest, seed, exec_params)          # #3428, excludes outputs
    output_equality_digest  versioned: raw-byte by default; explicit declared canonicalizer otherwise      # #3427/#3431
  status                  succeeded | reproducible_failure   # failed carries normalized failure evidence; never enters metrics
  inputs[]   -> Input records (#3430): role, schema_ver, canonical repr, digest, required_for_replay,
                                        redistribution evidence, public locator | HF-resident artifact ref
  outputs[]  -> Output records (#3431): role, native schema, units/convention, validation/review state,
                                         curated-vs-excluded flag, artifact refs
  metrics[]  -> Metric observations (#3432): definition_ver, value, quality, uncertainty  (succeeded runs only)
  artifacts[] -> Artifact records (#3429): sha256, size, media type, native format, schema ref, residency policy
  evidence:   result_envelope excerpt (input_hash, result_hash, code_version, reproducible)  # evidence ONLY, not identity
```

Invariants: `run_id` excludes outputs (an exact rerun with mismatched curated output digests is
a reproducibility defect that fails publication, never a new revision). Exact repeats resolve to
the same `run_id` and create **no** attempt record and **no** overwrite. `git_sha` from the
ResultEnvelope is retained under `evidence` but a *dirty* tree fails the `algorithm_version_id`
clean-commit check — the projection re-derives identity from a verified clean commit, not from
the envelope's best-effort `git_sha`.

### 2. Dataset schema (per-repository Hugging Face layout)

One dataset per source repo (`aceengineer/digitalmodel-runs`, `aceengineer/worldenergydata-runs`);
a separate global catalog **indexes** datasets and never merges domain-native records.

```text
<dataset-root>/
  README.md                      # dataset card: metadata, schema versions, license summary
  runs/       part-*.parquet      # append-only shards, one row per run (identity + status + refs); eligibility gated by publications/
  inputs/     part-*.parquet      # replay-critical inputs (JSONL fallback for deeply nested payloads)
  outputs/    part-*.parquet      # curated native outputs (JSONL where schema is non-tabular)
  metrics/    part-*.parquet      # metric observations (succeeded runs only)
  publications/ part-*.jsonl      # append-only Publication acceptance records (see §3)
  objects/<sha256[:2]>/<sha256>   # content-addressed blob store; deduplicated within dataset
  catalog-index.json (global catalog side) # points at each dataset revision; no combined run table
```

Parquet is the default (columnar, HF-recommended); JSONL is the escape hatch for nested
engineering payloads that would lose meaning if flattened (e.g. dm #1528's synchronized
time-history traces). Every `objects/` entry is addressed and named by its SHA-256 so identical
bytes referenced by multiple runs/roles resolve to one object. A reader re-hashes object bytes to
revalidate integrity **without trusting** the row's asserted digest.

### 3. Staged promotion state machine

Acceptance is atomic; **visibility is not**. GitHub and HF cannot commit together, so a visible
HF candidate is authoritative for *nothing* until the append-only Publication record accepts it.

```text
(0) EMITTED         local RunProjection written                          -> analysis-INELIGIBLE
(1) VALIDATED       schemas + identity + hashes + license + egress Gate A (source bytes) all pass (fail-closed)
(2) REPLAYED        deterministic reproduce / exact-equality verify pass; failed runs get normalized evidence
(3) REPORT_DRAFTED  rolling HTML report draft rendered (NOT pinned); egress Gate B re-scans the report (fail-closed)
(4) REVIEW_APPROVED explicit human promotion review recorded; UNAVAILABLE review channel != approval
(5) HF_CANDIDATE    egress Gate C re-scans dataset card + all upload bytes (fail-closed) BEFORE commit;
                    immutable single-commit HF revision created; exact commit sha captured;
                    EVERY content-addressed object re-downloaded + re-hashed                -> still INELIGIBLE
(6) REPORT_PINNED   source-repo rolling report updated to pin the EXACT verified revision
(7) CROSS_VERIFIED  cross-system check: HF objects resolve at the revision AND report links resolve to it
(8) ACCEPTED        append-only Publication record written                                  -> analysis-ELIGIBLE
```

Run records are written once and **never mutate** from candidate to accepted; acceptance is a
*separate* append-only Publication row. Only the Publication record confers analysis eligibility.
Every transition requires its predecessor — there is no bypass edge to ACCEPTED.

### 4. Immutable HF revision + object verification

- `create_commit` produces a single commit whose returned revision (commit SHA) is captured
  verbatim into the candidate record. The publisher **never** force-pushes, deletes, or
  overwrites; new runs are additive shards + new content objects.
- Immediately after upload, every content-addressed object referenced by the candidate is
  re-fetched from the dataset revision and re-hashed; any mismatch fails the candidate before
  REPORT_PINNED (the candidate stays ineligible; see recovery below).
- The source-repo rolling report is finalized only after it pins the exact verified revision;
  a moving/`main` reference (not an immutable revision) fails CROSS_VERIFIED.

### 5. Public-egress / legal / secret validation

The egress gate is one composed check invoked at **three** enforcement points, because the bytes
it must cover are produced at different states: source records exist at state 1, the rolling report
is rendered at state 3, and the dataset card + upload shards are assembled at state 5. Scanning
only at state 1 would let a secret introduced during report rendering or card assembly reach
Hugging Face. Every invocation fails closed:

- **Gate A — at VALIDATED (state 1):** over projection records, every replay-critical input, and
  every content-addressed artifact (the source bytes).
- **Gate B — immediately after REPORT_DRAFTED (state 3):** over the rendered rolling HTML report.
- **Gate C — immediately before `create_commit` (state 5):** over the dataset card/README and
  **every byte staged for upload** (shards + new content objects), so nothing unscanned is committed.

The composed check runs, at each point:

- **Legal:** `scripts/legal/legal-sanity-scan.sh` (deny-list) over the in-scope bytes + text.
- **Secret:** token/credential pattern scan; HF/GitHub tokens are read from the environment only
  and are redacted from all emitted text (projection, report, logs, dataset card).
- **Absolute paths / machine state:** `scripts/enforcement/check-no-abs-paths.sh`; any local
  absolute path or undocumented machine state fails public eligibility.
- **Per-input license (Gate A):** each replay-critical input carries redistribution evidence;
  restricted, ambiguous-license, private, client-specific, or pointer-only inputs fail (a
  dataset-level license cannot grant rights absent from a source).
- **Ecosystem public-egress validator (#3013) when available:** the gate composes it (allowlist-
  only public projection, deny-list-inside-allowed-values, public-identity-registry-backed ID
  validation, deterministic ID pattern). Until #3013 lands, a **bounded compatibility shim**
  enforces the local subset **fail-closed** and records `egress_validator: {available: false,
  compat_shim_version, uncovered: [public_identity_registry_id_check, ...]}` — the marker both
  makes the reduced coverage visible (per #3433 AC 10) and **names what the shim cannot verify**
  (e.g. registry-backed ID validation, which has no substrate until #2975/#3013 land) rather than
  passing runs through under a bare "unavailable" flag.

Scripts note: `legal-sanity-scan.sh` and `check-no-abs-paths.sh` are workspace-hub-resident. For
code that lands outside workspace-hub (see Open Question 1), the gate invokes them via a pinned,
vendored copy or a cross-repo call resolved by the control-plane; the library-home decision must
settle this before implementation so "scans pass on changed files" is enforceable in the code's
actual repo.

### 6. Rollback / resume behavior

A durable append-only **promotion journal** (local, per run) records each stage's completion and
an idempotency key. On restart the workflow replays from the last completed stage; every stage is
idempotent (re-running EMITTED/VALIDATED/REPLAYED recomputes deterministically; re-running
HF_CANDIDATE reuses the captured revision rather than committing twice).

- **Failure before HF_CANDIDATE:** no HF write occurred; quarantine locally and resume/abort. No
  partially-accepted run is ever exposed.
- **HF_CANDIDATE succeeds, then REPORT_PINNED fails, or CROSS_VERIFIED fails (either sub-check:
  HF objects not resolving at the revision, or report links not resolving to it):** the candidate
  revision is immutable and cannot be deleted atomically, so it **remains** but no Publication
  record is written → it stays analysis-ineligible. Because the `runs/` row for this deterministic
  `run_id` is already committed at revision R1, recovery is **retry pin/verify against R1 only** —
  it does **not** create a second candidate, which would either duplicate the `run_id` row across
  shards (violating the no-attempt-record / no-overwrite invariant) or be blocked by no-overwrite.
  Supersession is reserved for failures **before** a successful `create_commit`. The dataset reader
  deduplicates run rows by `run_id` across shards, and the Publication record is the **sole**
  authority for "accepted", so an un-accepted R1 is inert regardless of visibility.
- **Interrupted mid-stage:** the journal + idempotency keys guarantee replay never double-commits
  and never advances past an unverified gate.

---

## Pseudocode

```text
load per-repo publication.yml (dataset target, algorithm->report map)   # no creds, no abs paths
resolve HF + GitHub tokens from environment ONLY; assert namespace ownership preflight (no secret persisted)

for each locally emitted RunProjection:
    journal = open_or_resume_journal(run_id)                # idempotent replay
    if journal.stage < VALIDATED:
        assert strict identity (clean commit, schema vers, env digest, seed, exec params)   # #3428
        assert inputs public-admissible (redistributable, pinned, hashed, schema-valid, complete)  # #3430
        assert artifacts content-addressed + residency-legal (#3429); outputs curated + native (#3431)
        egress GATE A: legal + secret + abs-path + per-input license (+ #3013 validator | fail-closed shim) over source bytes
        FAIL CLOSED on any miss
    if journal.stage < REPLAYED:
        deterministic reproduce OR exact-equality verify; mismatch -> reject (no overwrite)
        failed-but-reproducible -> normalized failure evidence; EXCLUDE from metrics/insights/decisions
    if journal.stage < REPORT_DRAFTED:
        render rolling HTML draft (unpinned)
        egress GATE B: legal + secret + abs-path over the rendered report; FAIL CLOSED
    if journal.stage < REVIEW_APPROVED: require explicit human review; UNAVAILABLE channel != approval -> stop
    if journal.stage < HF_CANDIDATE:
        egress GATE C: legal + secret + abs-path over dataset card + EVERY byte staged for upload; FAIL CLOSED
        rev = hf.create_commit(dataset_target, additive shards + new content objects)   # immutable single commit
        capture rev verbatim; re-download + re-hash EVERY content object; mismatch -> fail (candidate stays ineligible)
    if journal.stage < REPORT_PINNED:   update source report to pin EXACT rev (moving ref -> fail)
    if journal.stage < CROSS_VERIFIED:  verify HF objects @rev AND report links @rev
    append Publication acceptance record (append-only) -> run becomes analysis-ELIGIBLE
    # Run record itself never mutated candidate->accepted
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `assetutilities/…/workflow_api/publication/projection.py` (DECIDED home) | build `RunProjection` from `ResultEnvelope` + record contracts; bind strict identity |
| Create | `…/publication/dataset_schema.py` | Parquet/JSONL table writers + content-addressed object store + integrity re-reader |
| Create | `…/publication/promotion.py` | nine-state machine + durable idempotent promotion journal |
| Create | `…/publication/hf_client.py` | env-backed auth, single-commit revision, post-upload object re-verification, token redaction |
| Create | `…/publication/egress.py` | compose legal + secret + abs-path + license gate; #3013 validator or bounded shim |
| Create | `…/publication/report_pin.py` | pin source-repo rolling report to the exact verified revision |
| Create | `…/publication/publication_record.py` | append-only Publication acceptance log; sole eligibility authority |
| Create | `…/publication/cli.py` | thin CLI; policy in helper modules |
| Create | `…/publication/schemas/*.schema.json` | projection/dataset record schemas |
| Create | `<repo>/docs/registry/publication.yml` (dm, wed) | dataset target + algorithm→report mappings; credential-free |
| Create | `assetutilities/tests/workflow_api/publication/` | TDD suite (below) |
| Create | `workspace-hub docs/governance/2026-07-11-hf-projection-staged-promotion-notes.md` | design companion, bound to parent contract version |
| Update | `docs/plans/README.md` | plan index status |

No source-repository algorithm code, existing runner, workflow registry, or credential store is
modified by this issue. HF datasets are created/appended only during pilot execution (dm #1505 /
wed #927), each under its own approval gate — **not** under this planning issue.

---

## TDD Test List

| Test | Verifies | Input | Expected |
|---|---|---|---|
| `test_projection_binds_strict_identity_not_envelope_alias` | identity re-bound; envelope hashes are evidence only | envelope + clean/dirty fixtures | dirty tree rejected; identity ≠ `input_hash`/`git_sha` |
| `test_run_id_excludes_outputs_and_is_deterministic` | same version+inputs+seed → same `run_id` across machines; outputs not in `run_id` | repeat fixtures | identical `run_id`; output change keeps `run_id` |
| `test_exact_rerun_output_mismatch_fails_closed` | curated-output digest mismatch rejects, no overwrite | matched/mismatched reruns | mismatch rejected; prior record intact |
| `test_public_input_admission_is_strict` | restricted/pointer-only/unlicensed/unpinned/unhashed/incomplete fail | input policy cases | each unsafe case rejected |
| `test_dataset_is_per_repository_and_content_addressed` | one dataset per repo; identical bytes dedupe to one object; catalog never combines | two-repo fixtures | distinct targets; single object id; no combined table |
| `test_artifact_integrity_revalidated_from_bytes` | reader re-hashes objects, ignores asserted digest | tampered-byte fixture | tamper detected |
| `test_promotion_state_machine_has_no_bypass_to_accepted` | ACCEPTED reachable only through all gates | transition graph | no shortcut edge |
| `test_candidate_is_analysis_ineligible_until_publication_record` | visible HF candidate confers nothing until append-only accept | candidate w/o Publication row | ineligible |
| `test_run_record_never_mutates_candidate_to_accepted` | Run row immutable; acceptance is separate append | before/after accept | Run bytes unchanged |
| `test_unavailable_review_channel_is_not_approval` | missing review ≠ approval | unavailable-channel fixture | promotion stops |
| `test_hf_revision_is_captured_and_objects_verified` | exact revision captured; every object re-verified post-upload | mock HF commit + object fetch | revision pinned; mismatch fails candidate |
| `test_report_pins_exact_immutable_revision` | moving/`main` ref fails; exact revision passes | report-pin fixtures | moving ref rejected |
| `test_failed_runs_excluded_from_metrics` | reproducible failures visible but analysis-ineligible | failed-run fixture | no metric contribution |
| `test_resume_replays_from_last_stage_idempotently` | interrupted promotion resumes; no double-commit | journal at each stage | single commit; correct resume |
| `test_hf_success_then_pin_failure_recovers_by_retry_against_R1` | pin-failure recovery retries R1, no second candidate, no acceptance | pin-failure fixture | no Publication row; retry against captured rev; no duplicate run row |
| `test_hf_success_then_cross_verify_failure_recovers_without_acceptance` | verify-failure (objects@rev / report-links@rev) recovery distinct from pin-failure | cross-verify-failure fixture | no Publication row; candidate inert |
| `test_egress_regate_on_report_and_upload_bytes_before_commit` | secret injected at report (state 3) or card/shard (state 5) is caught pre-upload | secret-in-report + secret-in-card fixtures | Gate B / Gate C fail closed; no `create_commit` |
| `test_publication_config_rejects_credentials_and_abs_paths` | `publication.yml` with an embedded token or machine path is rejected | bad-config fixtures | config load fails closed |
| `test_projection_roundtrips_all_five_record_categories` | inputs/outputs/metrics/artifacts + envelope serialize→read back preserving native meaning | full-record fixture | lossless round-trip; native schema intact |
| `test_tokens_never_reach_logs_or_reports` | env-backed auth; redaction | token in env | absent from all emitted text |
| `test_egress_validator_composes_when_present_and_shims_fail_closed_when_absent` | #3013 present → composed; absent → shim enforces covered subset fail-closed + names uncovered checks | validator-present + validator-absent fixtures | present: real validator invoked; absent: `egress_validator.available=false`, `uncovered[...]` recorded, covered subset still fails closed |
| `test_legal_and_abs_path_scans_pass` | no restricted ids/secrets/machine paths | changed paths | scanners exit 0 |

Tests are written first and fail before implementation exists.

---

## Acceptance Criteria

- [ ] A repository configures its dataset target + algorithm→report mappings via
      `publication.yml` with no embedded credentials or machine-specific paths.
- [ ] Projection preserves the common run envelope and domain-native input/output/metric/artifact
      records in machine-readable Parquet or JSONL, binding strict identity distinct from the
      execution envelope's evidence hashes.
- [ ] Public admission fails closed for dirty source, missing replay inputs, invalid schemas,
      unresolved licenses, bad hashes, nondeterministic exact reruns, or unapproved promotion.
- [ ] Validated reproducible failures publish with normalized failure evidence and are excluded
      from metrics, insights, and decisions.
- [ ] Exact repeats resolve to the deterministic `run_id`, create no attempt record, and never
      overwrite immutable outputs.
- [ ] Publication captures the exact HF commit/revision and re-verifies every content-addressed
      object after upload.
- [ ] The source-repository rolling HTML report is finalized only after it pins the exact verified
      dataset revision.
- [ ] Interrupted promotion is resumable or rolls back without exposing a partially accepted run,
      including the HF-success-then-pin/verify-failure recovery paths.
- [ ] Authentication is environment-backed; logs and reports cannot disclose tokens.
- [ ] The workflow composes the #3013 ecosystem public-egress validator when available and records
      a bounded compatibility dependency until then.
- [ ] Run records never mutate candidate→accepted; a visible HF candidate is analysis-ineligible
      until the append-only Publication record accepts it.
- [ ] TDD tests are written first and fail before implementation; the full suite, the legal scan
      (`--diff-only`), and `check-no-abs-paths.sh` pass on changed files.
- [ ] Final Claude and Codex review artifacts contain substantive reviews with no unresolved MAJOR
      finding; any unavailable provider is recorded as unavailability, not approval, and the reduced
      review depth is disclosed in the approval packet.

---

## Sequencing & Gate

**This child requires its own reviewed plan and explicit user approval; parent #3427 approval does
not authorize it.** Implementation is additionally sequenced behind:

1. Parent contract (#3427) YAML + decision manual merged to `origin/main` (currently diverged).
2. Record-schema children #3428–#3432 planned, approved, and their record shapes merged.
3. Authenticated HF namespace ownership preflight (no persisted secret) — owned here, run at
   implementation start, not during planning.

The issue stays at `status:needs-plan` until adversarial review completes and the user approves.
The uploader is **not** implemented under this plan.

---

## Adversarial Review Summary

| Round | Reviewer | Verdict | Findings | Result |
|---|---|---|---|---|
| r1 | Claude (adversarial self-review) | **BLOCK → remediated** | 1 MAJOR (egress gate scanned report + upload bytes before they existed; no pre-upload re-gate), 5 MINOR (untested cross-verify recovery; supersession vs deterministic `run_id` conflict; missing tests for AC1/AC2/AC10 compose-when-present; cross-repo scan location; #3013 shim must fail-closed on covered subset) | All applied in this revision: three-point egress gate (A/B/C); retry-against-R1-only recovery + reader dedup by `run_id`; four new failing-first tests; library-home made a hard precondition covering scan invocation; shim fails closed + names uncovered checks |

r1 was a single-provider adversarial self-review. Before implementation, the plan targets the
standard multi-provider gate (Claude + Codex substantive; Gemini subject to noninteractive-auth
availability on this machine). **No unavailable provider result will be interpreted as approval**,
and any T3→T2 review-depth reduction will be disclosed in the approval packet for explicit owner
acceptance, consistent with the parent.

---

## Risks and Open Questions

- **Cross-system transaction risk:** GitHub + HF cannot commit atomically. Mitigation: candidate
  visibility is non-authoritative; acceptance gates on verified HF objects + a pinned report + an
  append-only Publication record.
- **Dependency-ordering risk:** the parent contract and record-schema children are not yet on
  `main`. Mitigation: implementation is explicitly sequenced behind their merge; the plan pins the
  record shapes and adds a version-compatibility check that fails closed on drift.
- **Egress-coverage risk:** #3013 is unbuilt. Mitigation: bounded compatibility shim + an explicit,
  visible dependency marker; no silent reduction of egress coverage.
- **Scale risk:** many small objects degrade HF usability. Mitigation: append-only Parquet shard +
  content-object thresholds tuned against current HF limits at implementation.
- **Namespace/auth risk:** the final HF organization and credentials are unverified by this planning
  issue. Mitigation: authenticated ownership preflight at implementation start; no secret written to
  any repo or log.

**Resolved decisions (owner-confirmed 2026-07-11):**

1. **Library home — DECIDED: `assetutilities.workflow_api.publication`.** Both pilots already import
   `assetutilities.workflow_api`, so one shared implementation serves dm + wed. Because
   `legal-sanity-scan.sh` and `check-no-abs-paths.sh` are workspace-hub-resident, the egress gate
   will invoke them from assetutilities via a **pinned, vendored copy** (checksum-pinned to the
   workspace-hub source, refreshed by a control-plane check) so "scans pass on changed files"
   (AC 12) is enforceable in the code's own repo. This is now a fixed implementation constraint,
   not an open question.
2. **HF organization/namespace — DECIDED: `aceengineer/*`** (`aceengineer/digitalmodel-runs`,
   `aceengineer/worldenergydata-runs`); credentials supplied via **environment at run time**, never
   persisted to any repo or log. The authenticated namespace-ownership preflight (no persisted
   secret) runs at implementation start.

---

## Complexity: T3

Systemic, cross-repository publication architecture with legal, identity, determinism, external-
platform, and recovery consequences, consumed by two independently gated pilots. Targets a three-
provider adversarial plan review; provider availability will be recorded truthfully and any depth
reduction disclosed for explicit owner acceptance.
