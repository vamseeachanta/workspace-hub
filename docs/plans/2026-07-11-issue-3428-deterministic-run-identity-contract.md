# Plan for [#3428](https://github.com/vamseeachanta/workspace-hub/issues/3428): Deterministic Run Identity and Algorithm Version Contract

> **Status:** adversarial-reviewed (r1 BLOCK remediated; ready for user review)
> **Complexity:** T2
> **Date:** 2026-07-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3428
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** `scripts/review/results/2026-07-11-plan-3428-{claude,codex,gemini}.md`

---

## Resource Intelligence Summary

### Existing repo code

- `assetutilities/src/assetutilities/workflow_api/envelope.py` — `ResultEnvelope` supplies
  `input_hash` (**volatile-key-pruned**: `VOLATILE_TOP_KEYS = {"Analysis", "default", "cfg_array"}`),
  a location-independent content `result_hash`, `code_version()` → `{package_version, git_sha}`
  (`git_sha` is a **best-effort** `git rev-parse HEAD` that returns `None` off a checkout and does
  **not** prove a clean tree), and `reproducible` (`None` unless an opt-in double run runs). **These
  are execution evidence, not identity** — `input_hash` under-specifies (prunes real inputs) and
  `git_sha` cannot certify a clean commit. The identity contract re-derives strict identity and
  references these only as evidence.
- `digitalmodel/docs/registry/workflows.yaml` (`schema_version: 2`) carries a per-row **integer**
  `version` plus `status`/`latest`. This is an execution routing reference, **not** a semantic
  algorithm version; the contract maps it explicitly, never infers one from the other.
- `digitalmodel/src/digitalmodel/workflow_api/provenance.py` — `stamp_provenance` delegates to
  `assetutilities…make_provenance`, parameterized by `package_name`; `data_as_of` is optional and,
  for `worldenergydata`, is currently a run timestamp rather than a pinned snapshot.
- **Gap:** no `algorithm_id` / `algorithm_version_id` / `run_id` definition, no explicit
  canonicalization + digest algorithm, no clean-tree eligibility check, and no cross-machine
  determinism proof exist anywhere.

### Standards

| Standard | Status | Source |
|---|---|---|
| Parent run-dataset contract (identity decisions) | binding, extended here | `#3427` plan + `docs/architecture/algorithm-run-dataset-contract.yaml` (in **draft PR #3452**, not yet on `main`) |
| Data/execution/report boundaries | reusable | `docs/architecture/execution-manifest.schema.yaml` |
| Issue lifecycle + approval | binding | `AGENTS.md`, `docs/plans/README.md` |
| Legal/abs-path scans | binding | `scripts/legal/legal-sanity-scan.sh`, `scripts/enforcement/check-no-abs-paths.sh` |

No engineering-calculation standard applies to this identity contract.

### Documents consulted

- Issue [#3428](https://github.com/vamseeachanta/workspace-hub/issues/3428): distinguishes stable
  `algorithm_id` from immutable `algorithm_version_id`; binds version identity to semver + full clean
  commit + input/output schema versions + environment digest; binds run identity to canonical replay
  inputs + seed + execution parameters; exact reruns resolve to the same `run_id`; output-digest
  mismatch is a reproducibility defect, never a new revision or overwrite; terminal success/failure
  without retry/attempt identities.
- Parent [#3427](https://github.com/vamseeachanta/workspace-hub/issues/3427) plan (read at
  `01054d8d`): locks `algorithm_version_id` = f(semver, clean commit, schema versions, env digest);
  `run_id` = f(version, canonical input set, seed, exec params), excluding outputs; byte identity vs
  a versioned semantic equality digest; ResultEnvelope-as-evidence crosswalk.
- Sibling publication child [#3433](https://github.com/vamseeachanta/workspace-hub/issues/3433) plan
  (this session): consumes this identity contract; its `RunProjection.identity` block is the first
  consumer, so the executable reference implementation should be importable by
  `assetutilities.workflow_api.publication`.
- Dependents [#3429](https://github.com/vamseeachanta/workspace-hub/issues/3429) (artifact),
  [#3430](https://github.com/vamseeachanta/workspace-hub/issues/3430) (input),
  [#3431](https://github.com/vamseeachanta/workspace-hub/issues/3431) (output/report),
  [#3432](https://github.com/vamseeachanta/workspace-hub/issues/3432) (metric) all bind their records
  to `run_id` / `algorithm_version_id`; this contract is their root and is blocked by none.
- Concrete producers: dm workflow registry (integer versions) and dm [#1528](https://github.com/vamseeachanta/digitalmodel/issues/1528)
  (OpenFOAM ESI v2312 pinned toolchain, case/manifest hashes) — a real test of the `environment_digest`
  binding for a solver-backed algorithm.

### Gaps identified

- No normative record schema separates stable `algorithm_id` from immutable `algorithm_version_id`
  and `run_id`, or enumerates their exact hash inputs.
- No explicit, deterministic canonicalization + digest algorithm with valid/invalid fixtures.
- No clean-tree / pinned-schema / explicit-seed eligibility check that fails closed.
- No cross-machine determinism proof, and no crosswalk stating the registry integer version and the
  ResultEnvelope hashes are references/evidence, never identity aliases.

### Evidence (verified 2026-07-11)

```text
DRAFT PR #3452  feat: define algorithm run ledger for Hugging Face datasets (parent #3427 contract; not on main)
404 @main       docs/architecture/algorithm-run-dataset-contract.yaml
EXISTS          assetutilities …/workflow_api/envelope.py (input_hash pruned; git_sha best-effort; reproducible None)
EXISTS          digitalmodel docs/registry/workflows.yaml (schema_version 2; integer version)
#3428           OPEN status:needs-plan lane:claude — Blocked by: none
```

Distinct sources: issue #3428; parent #3427 plan; sibling #3433 plan; four dependent children;
ResultEnvelope implementation; dm registry; dm #1528 producer — more than the required three.

---

## Deliverable

A normative, machine-validated **deterministic run identity contract**: the record shapes for
`algorithm_id`, `algorithm_version_id`, and `run_id`; an explicit, deterministic canonicalization +
SHA-256 digest algorithm; a fail-closed public-eligibility check; valid/invalid fixtures; a
cross-machine determinism proof; and decision-manual identity/collision/mismatch examples. A reference
implementation proves determinism; the contract does not build the uploader or any dataset.

---

## Design

### Identifiers

```text
algorithm_id            stable, human-meaningful: "<source_repo>:<workflow_id>"  (e.g. "digitalmodel:cathodic-protection")
                        stable across versions; NOT a digest.

algorithm_version_id    IMMUTABLE digest = sha256(canonical_json({
                          canonicalization_version,     # pinned scheme id (see above)
                          algorithm_id, semantic_version, source_repo,
                          source_commit,            # full 40-hex, verified CLEAN tree
                          input_schema_version, output_schema_version,
                          environment_digest }))
                        The dm registry INTEGER `version` maps explicitly to `semantic_version`
                        via the descriptor; it is never inferred or aliased.

run_id                  IMMUTABLE digest = sha256(canonical_json({
                          canonicalization_version,
                          algorithm_version_id,
                          canonical_input_set_digest,   # OPAQUE injected value, OWNED + computed by #3430
                          seed,                         # explicit; sentinel "deterministic:no-seed" if none
                          execution_parameters }))      # run-CONTROL knobs only (see boundary below)
                        EXCLUDES outputs. Exact reruns resolve to the same run_id.
                        #3428 assembles run_id from an OPAQUE `canonical_input_set_digest` it does not
                        compute (dependency-injected; #3428 tests use a stand-in); #3430 owns that
                        digest's field membership + canonicalization.

execution_parameters vs parameter_set (boundary, resolves the #3430 seam):
                        execution_parameters = run-CONTROL knobs that steer computation without being
                          replay DATA — tolerances, iteration/step caps, solver flags, seed-adjacent
                          controls. They live in run_id directly.
                        parameter_set (a #3430 Input kind) = replay DATA authored for the run (sweep
                          values, physical parameters). They flow through canonical_input_set_digest.
                        A parameter is assigned to EXACTLY ONE side by the algorithm descriptor; the
                          same parameter can never be double-counted (one run → one run_id).

environment_digest      sha256(canonical_json({ interpreter, interpreter_version, lockfile_hash,
                          toolchain_pins }))  # toolchain_pins e.g. {"openfoam":"ESI-v2312"} for dm#1528;
                        only determinism-relevant fields; declared, not sniffed.

repository_identity     { source_repo, owning_dataset }   # one dataset per repo (#3427)
```

### Canonicalization + digest (pinned, explicit, deterministic)

The canonicalization algorithm is **pinned exactly** (an under-specified scheme would let the
identity root diverge on equivalent inputs or collide on different ones — disqualifying for the
contract every other record binds to):

- **Structure:** RFC 8785 JSON Canonicalization Scheme (JCS) — UTF-8, object keys sorted by UTF-16
  code-unit order, no insignificant whitespace, arrays in declared order.
- **Strings:** Unicode **NFC** normalization before hashing (so `NFC`/`NFD` spellings collapse).
- **Numbers:** parsed and normalized via `decimal.Decimal` in a fixed context and serialized with
  `Decimal.normalize()` — **no float round-trip** (avoids `0.1+0.2` drift); `1e3`==`1000`,
  `5.0`==`5.00`==`5`. Any value carrying a physical unit MUST be an explicit `{value, unit}` pair
  with the `unit` string drawn from a pinned unit vocabulary (`m` and `meter` normalize to one
  token); a bare units-bearing numeric is **rejected**, never silently hashed.
- **Null/NA:** explicit `null` / `"NA"` (never omitted so presence is unambiguous).
- **Digest:** SHA-256 hex over the canonical bytes.
- **Scheme version:** a `canonicalization_version` string is a field of every identity digest input
  (below), so a future rule change mints new identities deterministically and old ones remain
  reproducible under their recorded scheme.

This exact scheme is the single canonicalizer reused by #3430 (`canonical_input_set_digest`), #3429
(structured-object artifacts), and #3431 (`output_equality_digest`) — none forks a second scheme.

### Fail-closed public eligibility

Any of the following fails the public-eligibility check (no identity is minted for publication):
dirty/uncommitted working tree; unknown, shallow, or unresolved `source_commit`; unpinned input or
output schema version; missing/partial `environment_digest`; an implicit (unrecorded) seed; a
registry integer version with no explicit semantic-version mapping.

### Determinism, change-sensitivity, exact rerun, terminal status

- **Determinism:** same canonical version + inputs → identical `run_id` on any machine (identity is
  derived from the verified clean commit + declared env pins + canonical inputs, never from the
  volatile `ResultEnvelope.input_hash` or best-effort `git_sha`).
- **Change-sensitivity:** any change to code (commit), input/output schema, environment, input, seed,
  or a declared execution parameter yields a different `algorithm_version_id` and/or `run_id`.
- **Exact rerun:** resolves to the same `run_id`; output equality is checked against a **separate,
  versioned `output_equality_digest`** that #3431 OWNS and computes. #3428 owns only the *comparison
  policy* — mismatch is a reproducibility defect that fails closed and cannot mutate or overwrite the
  existing run — and injects the output digest as an opaque value (its own tests use a stub); #3431
  fills the computation. run_id excludes outputs, so this is a policy reference, not a cycle.
- **Terminal status:** `succeeded | reproducible_failure` are the two **terminal, ledger-bearing**
  statuses; a `reproducible_failure` requires a passed reproducibility verification (a failure whose
  normalized signature repeats). A flaky/transient failure that has NOT been shown reproducible is
  **`indeterminate_failure`** — a **non-terminal, non-public state that mints no ledger identity** and
  cannot enter the dataset. All three carry no retry/attempt identity: a re-execution of the same
  canonical inputs is the same `run_id`, never a new attempt.

### Crosswalk (evidence, never identity)

`ResultEnvelope.input_hash` and `code_version.git_sha` are retained as *execution evidence*; the
registry integer `version` is an *execution reference*. None is aliased into strict identity.

---

## Pseudocode

```text
require semantic_version, source_repo, clean source_commit (verify tree clean), input/output schema versions, environment_digest
algorithm_version_id = sha256(canonical_json(version components))
inject canonical_input_set_digest (OPAQUE, computed by #3430), explicit seed (or no-seed sentinel), canonical execution_parameters (run-control only)
run_id = sha256(canonical_json(canonicalization_version, algorithm_version_id, input_set_digest, seed, exec_params))   # NO outputs
fail closed if: dirty tree | unknown/shallow commit | unpinned schema | missing env digest | implicit seed | unmapped registry version
on exact rerun: recompute run_id -> must match; compare INJECTED #3431 output_equality_digest -> mismatch => reject, no mutation
terminal status in {succeeded, reproducible_failure}; indeterminate_failure = non-terminal, mints NO identity; never an attempt identity
canonicalization pinned (JCS + decimal.normalize + NFC + canonicalization_version); envelope input_hash/git_sha + registry integer version = evidence only
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Update (in/atop **PR #3452**) | `docs/architecture/algorithm-run-dataset-contract.yaml` | add the normative identity record schema + hash-input enumeration as a strictly additive, non-overlapping section |
| Create | `assetutilities/src/assetutilities/workflow_api/identity.py` (**DECIDED** home — inherits #3433's owner-confirmed `assetutilities.workflow_api` placement) | pinned canonicalization + digest; clean-tree/eligibility checks; importable by #3433 |
| Create | `assetutilities/tests/workflow_api/test_identity.py` + `fixtures/identity/{valid,invalid}/…` | valid/invalid + cross-machine determinism fixtures |
| Update (in **PR #3452**) | `docs/governance/2026-07-10-algorithm-run-dataset-decision-manual.html` | identity examples + collision/mismatch behavior section |
| Extend | `tests/architecture/test_algorithm_run_dataset_contract.py` (the parity test #3452 already ships) | add identity-section parity assertions rather than a second competing parity test |
| Update | `docs/plans/README.md` | plan index status |

No source-repository algorithm code, workflow registry, dataset, or credential is modified. All five
sibling contracts (#3428–#3432) edit `algorithm-run-dataset-contract.yaml` + the decision manual as
**strictly additive, non-overlapping sections**; they land atop PR #3452 in dependency order (or via
one integration PR) so no sibling clobbers another's section (per the "N additive lanes sharing a
file → one integration PR" rule).

---

## TDD Test List

| Test | Verifies | Expected |
|---|---|---|
| `test_algorithm_version_id_binds_all_components` | version digest covers semver + clean commit + input/output schema + env digest | omit any component → different id |
| `test_run_id_binds_inputs_seed_params_excludes_outputs` | run digest covers version + input-set + seed + exec params, not outputs | output change keeps `run_id` |
| `test_canonicalization_equivalent_values_same_digest` | JCS key order / whitespace; `1e3`==`1000`, `5.0`==`5.00`, NFC==NFD; missing unit tag rejected | equal digests; unit-less numeric rejected |
| `test_different_inputs_never_collide` | two genuinely different canonical inputs (incl. a near-collision pair `1.0000000001` vs `1.0`) → different digests | no collision |
| `test_canonicalization_version_in_digests_and_pins_scheme` | `canonicalization_version` is a digest input; a scheme change yields new ids, old ids reproducible | version bound; deterministic |
| `test_algorithm_id_stable_across_versions_and_not_a_digest` | `algorithm_id` unchanged across version bumps; never a digest of version fields | stable, non-digest |
| `test_repository_identity_binds_repo_and_dataset` | `{source_repo, owning_dataset}` binds correctly | binding enforced |
| `test_dirty_or_unpinned_or_implicit_seed_fails_closed` | dirty tree, unknown/shallow commit, unpinned schema, missing env digest, implicit seed all fail | each rejected |
| `test_same_canonical_inputs_same_run_id_cross_machine` | determinism across simulated machine A/B (different cwd, env noise) | identical `run_id` |
| `test_any_component_change_changes_identity` | code/schema/env/input/seed/param change → different id | id differs per change |
| `test_execution_parameter_and_parameter_set_not_double_counted` | a param assigned to exactly one of execution_parameters vs #3430 parameter_set; same run → one `run_id` | no double-count |
| `test_run_id_uses_opaque_injected_input_set_digest` | #3428 assembles run_id from a stand-in `canonical_input_set_digest` (computed by #3430) | opaque injection; no #3430 dependency at #3428 build |
| `test_exact_rerun_output_mismatch_fails_closed_no_mutation` | injected (stub) `#3431` output digest differs → reject, no overwrite | prior record intact |
| `test_terminal_statuses_have_no_attempt_identity` | succeeded + reproducible_failure carry `run_id`; indeterminate_failure mints NO identity; no attempt id | no attempt/retry identity |
| `test_registry_integer_version_not_aliased_to_semantic` | integer version maps explicitly, never inferred | unmapped version rejected; no implicit inference |
| `test_envelope_hashes_are_evidence_not_identity` | `input_hash`/`git_sha` never enter identity digests | identity independent of envelope hashes |
| `test_decision_manual_matches_identity_contract` | manual identity section ↔ contract YAML parity | structure + examples agree |

Tests are written first and fail before implementation exists.

---

## Acceptance Criteria

- [ ] The contract defines `algorithm_id`, `algorithm_version_id`, `run_id`, repository identity,
      source revision, schema versions, environment digest, seed, and execution-parameter bindings.
- [ ] Canonicalization and digest algorithms are explicit, deterministic, and covered by valid/invalid
      fixtures.
- [ ] Dirty, uncommitted, unknown-revision, or schema-unpinned executions fail public eligibility.
- [ ] The same canonical version and inputs produce the same `run_id` across repeated executions and
      machines.
- [ ] Changes to code, schema, environment, input, seed, or declared execution parameters produce a
      different identity.
- [ ] Exact rerun output mismatches fail closed and cannot mutate the existing run.
- [ ] Successful and failed terminal statuses are represented without introducing retry/attempt
      identities.
- [ ] The decision manual documents identity examples and collision/mismatch behavior.
- [ ] Tests are written first; the suite, legal scan (`--diff-only`), and `check-no-abs-paths.sh` pass.

---

## Sequencing & Gate

No **sibling** contract blocks #3428 — but its implementation is **stacked on parent PR #3452**: the
`algorithm-run-dataset-contract.yaml` and decision-manual it edits, and the parity test it extends,
exist ONLY in #3452 (both 404 on `main`), so a branch cut from `main` cannot take the parity test
red→green. #3428 therefore branches from (or co-merges with) #3452, coordinating the identity schema
as an additive section and never forking the closed-schema behavior. The "Blocked by: none" on the
issue refers to sibling contracts; the #3452 stack dependency is an implementation-ordering fact.
Requires its own reviewed plan and explicit user approval (HITL contract work). Dependents #3429–#3432
consume this contract; #3433 consumes its reference implementation.

---

## Adversarial Review Summary

| Round | Reviewer | Verdict | Result |
|---|---|---|---|
| r1 | Claude (adversarial) | **BLOCK → remediated** | 2 MAJOR: (1) under-specified numeric/unit canonicalization could diverge on equivalent inputs / collide on different — **fixed**: pinned RFC 8785 JCS + `decimal.Decimal.normalize()` (no float round-trip) + NFC + `canonicalization_version`; (2) "Blocked by none" false for implementation (parity test depends on unmerged PR #3452) — **fixed**: declared stacked-on-#3452. MINORs fixed: `algorithm_id`/repo-identity/collision tests; opaque-injected input/output digests; `indeterminate_failure` terminal state; `execution_parameters`↔`parameter_set` boundary; parity test folded into #3452's existing test. |

No unavailable provider counts as approval; any depth reduction is disclosed for owner acceptance.
A confirming verification pass before implementation is recommended (single-provider adversarial round).

---

## Risks and Open Questions

- **Environment-digest scope risk:** over-broad env fields make identity brittle (every machine
  differs); too-narrow misses real determinism inputs (solver build). Mitigation: env digest is a
  *declared* allowlist of determinism-relevant pins (interpreter, lockfile hash, toolchain), not a
  sniffed host fingerprint; dm #1528's OpenFOAM pin is the worked example.
- **Parent-contract coupling risk:** the contract YAML + decision manual are in draft PR #3452, and
  all five sibling contracts edit them. Mitigation: strictly additive non-overlapping sections; #3428
  stacks on #3452; siblings land in dependency order or via one integration PR; fail closed on drift.
- **Reference-implementation home — DECIDED:** `assetutilities.workflow_api.identity`, inheriting
  #3433's owner-confirmed `assetutilities.workflow_api` placement so the publication module imports one
  implementation. (No longer an open question.)

---

## Complexity: T2

A normative contract slice with a small deterministic reference implementation + fixtures. Not T3:
single-domain, no external platform, no cross-system transaction — but it is the identity root every
other record contract binds to, so its determinism and fail-closed proofs are load-bearing.
