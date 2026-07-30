# Plan for [#3432](https://github.com/vamseeachanta/workspace-hub/issues/3432): Algorithm-Specific Metric Definition and Observation Contract

> **Status:** adversarial-reviewed (r1 BLOCK remediated; ready for user review)
> **Complexity:** T2
> **Date:** 2026-07-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3432
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** `scripts/review/results/2026-07-11-plan-3432-{claude,codex,gemini}.md`

---

## Resource Intelligence Summary

### Existing repo code

- `assetutilities/src/assetutilities/workflow_api/envelope.py` — the shared `ResultEnvelope`
  produces `result_hash` (location-independent content hash for `kind: files`), a volatile-key-pruned
  `input_hash` (`VOLATILE_TOP_KEYS = {"Analysis", "default", "cfg_array"}`), `code_version()` →
  `{package_version, git_sha}` (best-effort, does **not** prove a clean tree), and `reproducible`
  (`None` unless an opt-in double run runs). It carries **no** metric abstraction: there is no metric
  identifier, no unit/dimension field, no quality state, no not-applicable representation, and no
  observation-to-definition-version binding. Any per-domain scalar an algorithm emits today lands as
  an untyped, unlabeled, unit-less value inside a curated output payload. The metric contract adds the
  missing typed Metric Definition + Metric Observation layer and treats these envelope hashes as
  *execution evidence*, never as metric identity or metric values.
- `digitalmodel/src/digitalmodel/workflow_api/{runner,provenance,golden}.py` +
  `docs/registry/workflows.yaml` (`schema_version: 2`, per-row integer `version` + `status`/`latest`).
  Algorithms are registered and routed here, but the registry has **no** metric declaration surface —
  it routes execution, it does not declare an algorithm's metric vocabulary. The metric definition set
  is a **new, separately versioned** descriptor owned per algorithm; it is *not* the integer registry
  version and is never inferred from it.
- **Gap:** no `metric_id` / `metric_definition_version` / Metric Observation record exists anywhere;
  no machine-validatable unit/dimension, data-type, applicability, directionality, or quality-rule
  field; no not-applicable / null discipline; no mechanism binding a historical observation to the
  exact definition version used; and no rule preventing failed-run values from entering a metric
  population or preventing a report from equating two different algorithms' metrics.

### Standards

| Standard | Status | Source |
|---|---|---|
| Parent run-dataset contract (metrics-algorithm-specific, no cross-algorithm equivalence, successful-runs-only) | binding, extended here | `#3427` plan + `docs/architecture/algorithm-run-dataset-contract.yaml` (in **draft PR #3452** `feature/issue-3427-hf-run-ledger-plan`, **not yet on `main`**) |
| Sibling identity contract (`run_id`, canonical_json + SHA-256, terminal status, failed-run exclusion) | binding, consumed | `#3428` plan (this session) |
| Sibling output/report contract (rolling HTML report renders metric tables/trends/comparisons; failed-run health) | binding, consumed | `#3431` plan/issue |
| Data/execution/report boundaries | reusable | `docs/architecture/execution-manifest.schema.yaml` |
| Issue lifecycle + approval | binding | `AGENTS.md`, `docs/plans/README.md` |
| Legal/abs-path scans | binding | `scripts/legal/legal-sanity-scan.sh`, `scripts/enforcement/check-no-abs-paths.sh` |

No engineering-calculation standard governs the *contract* layer itself. Each algorithm's metric
definitions carry their own domain-standard citation obligation (the metric's `derivation reference`
field is where that citation lands); the contract mandates the field, not any specific standard.

### Documents consulted

- Issue [#3432](https://github.com/vamseeachanta/workspace-hub/issues/3432): metric definitions are
  **algorithm-scoped**; Phase 1 imposes **no** universal engineering-metric vocabulary — each
  algorithm owns its definitions while sharing a common record envelope; only validated successful runs
  contribute observations; failed runs stay visible in run-health reporting but do not enter metric
  populations; metric definitions are versioned **independently** from observations; rolling reports
  render tables/trends/comparisons **without treating unlike algorithm metrics as equivalent**; any
  cross-algorithm ontology is **explicitly deferred** until repeated-run evidence justifies one. (Its
  eight acceptance criteria are copied verbatim below.)
- Parent [#3427](https://github.com/vamseeachanta/workspace-hub/issues/3427): locked decision
  "Metrics remain algorithm-specific; no cross-algorithm equivalence is inferred"; "Reproducible
  successful and failed runs may be public. Failed runs carry normalized failure evidence but cannot
  contribute metrics, insights, or decision conclusions"; applicable domain sections may add metrics,
  plots, comparisons, uncertainty, diagnostics, insights, decision briefs.
- Sibling identity contract [#3428](https://github.com/vamseeachanta/workspace-hub/issues/3428) plan
  (read at `/tmp/wh3433/docs/plans/2026-07-11-issue-3428-...md`): a Metric Observation identifies its
  `run_id` and its metric-definition version; the same `canonical_json` (UTF-8, lexicographic keys,
  explicit `null`/`"NA"`, unit-tagged numerics) + SHA-256 conventions apply; terminal status is
  `succeeded | reproducible_failure`, and only `succeeded` runs (non-rejected, reproducible) may carry
  observations that enter metric populations.
- Sibling output/report contract [#3431](https://github.com/vamseeachanta/workspace-hub/issues/3431):
  one rolling HTML report per algorithm renders **mandatory Inputs/Outputs** plus **applicable**
  Metrics/plots/comparisons/uncertainty; the report separates failed runs into health analysis and
  links each displayed run to an exact HF revision. This metric contract states **how the report
  consumes metric observations** (per-algorithm tables/trends/single-algorithm comparisons); it does
  **not** redefine the report.
- Publication child [#3433](https://github.com/vamseeachanta/workspace-hub/issues/3433) plan (skimmed
  at `/tmp/wh3433/docs/plans/2026-07-11-issue-3433-...md`): the per-repository HF dataset has a
  `metrics/` table populated from **succeeded runs only**; metric observations are projected there, and
  reproducible failures are excluded from metrics **and** insights **and** decisions. This contract
  defines the record shape that the `#3433` projection serializes into that `metrics/` table.

### Gaps identified

- No normative record separates an algorithm-scoped **Metric Definition** (stable id, algorithm owner,
  independently versioned, label, meaning, unit/dimension, data type, derivation reference,
  applicability rule, directionality, quality rule) from a **Metric Observation** (binds `run_id` +
  exact definition version; value, quality state, derivation evidence, optional uncertainty).
- No machine-validatable discipline for **units** and **null / not-applicable** states (a
  not-applicable metric and a genuine measured value must be distinguishable and both must be typed).
- No mechanism binding a **historical observation to the exact definition version** used, and no rule
  that definitions version **independently** from observations.
- No rule keeping **failed/rejected/non-reproducible** run values out of metric populations while
  leaving them visible in run-health.
- No invariant that each metric has **exactly one algorithm owner** and that reports render
  tables/trends/comparisons with **no cross-algorithm equivalence/comparison edge**, plus an explicit
  **deferral** of any cross-algorithm ontology.

### Evidence (verified 2026-07-11)

```text
#3432             OPEN  status:needs-plan lane:claude priority:high — Blocked by #3428, #3431
#3431             OPEN  status:needs-plan lane:claude — Blocked by #3428, #3429
#3428             OPEN  status:needs-plan lane:claude — Blocked by: none (identity root)
#3427             OPEN  status:plan-approved (parent tracker) — "metrics remain algorithm-specific; no cross-algorithm equivalence"
DRAFT PR #3452    feat: define algorithm run ledger for Hugging Face datasets (branch feature/issue-3427-hf-run-ledger-plan; parent contract; NOT on main)
404 @main         docs/architecture/algorithm-run-dataset-contract.yaml (per #3428 + #3433 plans, this session)
EXISTS            assetutilities …/workflow_api/envelope.py (result_hash/input_hash/code_version/reproducible; NO metric layer)
EXISTS            digitalmodel docs/registry/workflows.yaml (schema_version 2; integer version; NO metric declaration surface)
```

Distinct sources: issue #3432; parent #3427; sibling identity plan #3428; sibling output/report
#3431; publication child #3433 plan; ResultEnvelope implementation; dm workflow registry — more than
the required three.

---

## Deliverable

A normative, machine-validated **algorithm-scoped metric contract**: the record shapes for a
**Metric Definition** and a **Metric Observation**; an explicit, machine-validatable unit/dimension +
data-type discipline and an unambiguous **not-applicable / null** representation; an
**independent-versioning** rule that binds every historical observation to the exact definition
version used; a **fail-closed population rule** that admits only observations from validated
successful runs; a **single-algorithm-owner** invariant that forbids any cross-algorithm equivalence
or comparison edge in reports; valid/invalid fixtures spanning scalar, categorical, vector/series
reference, uncertainty, not-applicable, and invalid observations; and a small reference validator
that proves definition/observation validation, population exclusion, and the no-cross-algorithm-edge
rule. **This plan does not implement anything** — it fixes the contract, the fixtures, and a
first-fail TDD list. Code lands only after adversarial review and explicit user approval, and after
the parent contract (#3427) and blocking siblings (#3428, #3431) land on `main`.

---

## Design

### Metric Definition (algorithm-scoped, independently versioned)

```text
MetricDefinition
  metric_id              stable, human-meaningful, algorithm-scoped:
                         "<algorithm_id>/<metric_slug>"   (e.g. "digitalmodel:viv-parametric/max_a_over_d")
                         stable across definition versions; NOT a digest.
  algorithm_id           the SINGLE owning algorithm (#3428 stable id). Exactly ONE owner per metric_id.
                         A metric_id is namespaced under its algorithm_id; two algorithms CANNOT share one.
                         NORMATIVE: metric_id MUST be prefixed by its algorithm_id, validated as
                         definition.algorithm_id == prefix(metric_id) — a whole-prefix match, NOT a
                         split-on-last-"/" (an algorithm_id/workflow_id may itself contain "/").
  definition_version     semantic version of THIS definition, incremented INDEPENDENTLY of any run/observation.
                         A definition change (unit, data type, derivation, applicability, directionality,
                         quality rule, meaning) requires a NEW definition_version; older versions are retained.
  label                  short human display label (report column header).
  meaning                normative prose: what the metric means for THIS algorithm; explicitly non-transferable
                         to any other algorithm.
  unit_or_dimension      machine-validatable: { dimension, unit } for numeric metrics
                         (e.g. {dimension: "length/length", unit: "dimensionless"} or {dimension:"stress", unit:"MPa"});
                         categorical/reference metrics declare unit_or_dimension: "NA" explicitly (never omitted).
                         NOTE: this DEFINITION-level unit_or_dimension: "NA" ("this metric has no dimension
                         concept") is UNRELATED to the OBSERVATION-level quality_state: not_applicable value
                         "NA" ("the metric did not apply this run"). Two distinct meanings share the token by
                         coincidence; a validator MUST NOT conflate them.
  data_type              one of: scalar_number | categorical | vector_series_reference | boolean
                         (vector_series_reference points at a content-addressed artifact (#3429), NOT an inline array).
  derivation_reference   how the value is derived + domain-standard citation (formula id / doc ref / code symbol).
  applicability_rule     machine-checkable predicate over run identity/inputs deciding when the metric APPLIES;
                         when it does not apply, the observation MUST be not_applicable (below), not absent, not null-as-zero.
  directionality         ALWAYS REQUIRED: higher_is_better | lower_is_better | target(<value>) | none.
                         "none" is the explicit value for metrics with no intrinsic better/worse ordering.
                         DELIBERATE STRENGTHENING: AC1 says "directionality when meaningful"; this contract
                         strengthens that to always-required-with-explicit-"none" so applicability is never
                         silently omitted (an absent field cannot be distinguished from "no ordering"). This
                         is intentional, not scope over-reach — reviewers should read it as fail-closed rigor.
  quality_rule           machine-checkable validity predicate (range/domain/enum/monotonicity) the value must satisfy
                         to be quality_state: valid.
```

### Metric Observation (binds run + exact definition version)

```text
MetricObservation
  run_id                 the observed run (#3428). MUST reference a run whose terminal status is `succeeded`
                         (non-rejected, reproducible) to be POPULATION-eligible.
  metric_id              the observed metric (its algorithm_id MUST equal the run's algorithm_id — enforced).
  metric_definition_version  the EXACT MetricDefinition version used at observation time; pinned and immutable.
                             Historical observations retain their original version even after the definition advances.
  value                  typed per data_type; unit-tagged for numerics; canonical_json-encoded (#3428 conventions).
  quality_state          valid | not_applicable | invalid | missing
                           - valid          -> value present, passes quality_rule; POPULATION-eligible
                           - not_applicable -> applicability_rule is false; value MUST be the explicit NA sentinel; NOT in population
                           - invalid        -> value present but fails quality_rule; NOT in population; retained for health/audit
                           - missing        -> value could not be produced; value = null; NOT in population
  derivation_evidence    evidence linking value to its derivation (source artifact ref (#3429), formula inputs,
                          or output-record pointer (#3431)); machine-traceable.
  uncertainty            OPTIONAL: { kind: stddev|interval|distribution_ref, ... } when supplied; absent is explicit.
```

### Units + null / not-applicable (unambiguous + machine-validatable)

- Every numeric metric value carries its **unit tag**; a unit-less numeric where a dimension is
  declared is **rejected**, never silently hashed or averaged (same rule as `#3428`'s canonical_json
  unit discipline).
- **Not-applicable is a first-class typed state**, distinct from a missing value and from a numeric
  zero: `quality_state: not_applicable` with an explicit `"NA"` sentinel value. A report renders it as
  "N/A", never as a blank that could read as zero or as an absent row.
- `null` (`quality_state: missing`) is likewise explicit and distinct from `not_applicable`. The four
  quality states are mutually exclusive and machine-validated.

### Independent versioning (definition ⟂ observation)

- `MetricDefinition.definition_version` increments on any semantic change to the definition and is
  **decoupled** from run/observation timelines. Old versions are never mutated or deleted.
- The definition store is **append-only**: a published `(metric_id, definition_version)` pair is
  **immutable**. Re-registering an existing `(metric_id, definition_version)` with ANY differing field
  (unit/dimension, data type, derivation, applicability, directionality, quality rule, meaning, label)
  **fails closed** — it is never silently overwritten. A semantic change MUST mint a NEW
  `definition_version`; this is what prevents silent mutation of the definition under past observations
  (the AC4 invariant).
- Each `MetricObservation` pins the **exact** `metric_definition_version` used. A definition upgrade
  never rewrites historical observations; a trend chart that spans a version boundary is rendered with
  the version boundary **visible**, never silently splicing incompatible definitions.

### Fail-closed population rule (only validated successful runs)

An observation enters a metric **population** (the set feeding tables/trends/comparisons in reports,
insights, and decisions) **iff** all hold: the run's terminal status is `succeeded`
(non-rejected, reproducible per `#3428`); `quality_state == valid`; the observation's `metric_id`
algorithm owner equals the run's `algorithm_id`; and the pinned definition version validates. Any
observation from a `reproducible_failure` / rejected / non-reproducible run — or with
`quality_state ∈ {not_applicable, invalid, missing}` — is **excluded** from metrics, insights, and
decisions, while remaining **visible in run-health reporting** (per `#3431`). Fail-closed: an
observation of ambiguous provenance is excluded, not admitted.

### Single-algorithm owner + no cross-algorithm equivalence (report consumption)

- Each `metric_id` has **exactly one** owning `algorithm_id`; the contract forbids a metric shared by
  two algorithms and forbids any equivalence/mapping edge asserting "metric X of algorithm A equals
  metric Y of algorithm B."
- The rolling report (owned by `#3431`, **consumed** here) renders **per-algorithm** metric tables,
  per-algorithm trends across that algorithm's immutable historical runs, and comparisons **only among
  runs of the same algorithm**. There is **no** comparison edge, shared axis, or normalization that
  places two different algorithms' metrics on equal footing.
- Any cross-algorithm ontology (a universal engineering-metric vocabulary or equivalence graph) is
  **explicitly deferred** until real repeated-run evidence across algorithms justifies one; Phase 1
  ships none, and the contract records this deferral as a normative non-goal.

### Crosswalk (evidence, never metric identity)

`ResultEnvelope.result_hash` / `input_hash` / `code_version` / `reproducible` are retained as
*execution evidence* and may appear under an observation's `derivation_evidence`; none is a metric
value, a metric identifier, or a definition version.

---

## Pseudocode

```text
# --- definition registration (per algorithm, independently versioned) ---
require metric_id namespaced under exactly one algorithm_id
assert definition.algorithm_id == prefix(metric_id)   # whole-prefix match, NOT split-on-last-"/"
require definition_version, label, meaning, unit_or_dimension (explicit "NA" if categorical/reference),
        data_type in {scalar_number, categorical, vector_series_reference, boolean},
        derivation_reference, applicability_rule, directionality (ALWAYS required; explicit "none" allowed),
        quality_rule
reject if metric_id owner conflicts with an existing owner (no shared / cross-algorithm metric)
# APPEND-ONLY immutable store: a published (metric_id, definition_version) is immutable
if (metric_id, definition_version) already published:
    reject unless EVERY field is byte-identical    # any differing field -> FAIL CLOSED; mint a NEW version
store version immutably; never mutate/delete prior definition_versions

# --- observation admission ---
require run_id (#3428), metric_id, metric_definition_version (pin exact), value, quality_state,
        derivation_evidence; uncertainty optional (absence explicit)
assert observation.metric_id.algorithm_id == run.algorithm_id                    # owner match
assert numeric value carries unit tag matching definition dimension              # else reject (unit discipline)
classify quality_state:
    applicability_rule false            -> not_applicable (value == "NA" sentinel)
    value present & passes quality_rule -> valid
    value present & fails quality_rule  -> invalid
    value unproducible                  -> missing (value == null)

# --- population membership (fail-closed) ---
in_population(obs) := run.terminal_status == succeeded (non-rejected, reproducible)   # #3428
                   AND obs.quality_state == valid
                   AND obs.metric_id.algorithm_id == run.algorithm_id
                   AND definition_version validates
# reproducible_failure / rejected / non-reproducible OR not_applicable/invalid/missing -> EXCLUDED
# excluded observations remain VISIBLE in run-health reporting (#3431), never in metrics/insights/decisions

# --- report consumption (no cross-algorithm equivalence) ---
render per-algorithm tables/trends/comparisons over in_population(obs) grouped by algorithm_id
FORBID any comparison/equivalence edge between distinct algorithm_ids
trend spanning a definition_version boundary -> render boundary visibly; never splice unlike versions
DEFER any cross-algorithm ontology (normative non-goal, Phase 1)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Update | `docs/architecture/algorithm-run-dataset-contract.yaml` (coordinated with parent **PR #3452**, not yet on `main`) | add the normative MetricDefinition + MetricObservation record schemas, unit/quality-state enums, population rule |
| Create | `assetutilities/src/assetutilities/workflow_api/metrics.py` (**reference-impl home DECIDED** — inherits `#3433`'s owner-confirmed `assetutilities.workflow_api` placement) | definition/observation validation, unit + not-applicable discipline, append-only immutable definition store, `in_population` predicate, no-cross-algorithm-edge check; importable by `#3433` projection |
| Create | `assetutilities/tests/workflow_api/test_metrics.py` + `fixtures/metrics/{valid,invalid}/…` | scalar/categorical/vector-series/uncertainty/not-applicable/invalid + failed-run + no-cross-algorithm fixtures |
| Update | `docs/governance/2026-07-10-algorithm-run-dataset-decision-manual.html` (in PR #3452) | metric definition/observation examples, population-exclusion rule, no-cross-algorithm-equivalence + deferral section |
| Create | `tests/architecture/test_metric_contract_parity.py` | assert the decision-manual metric section matches the contract YAML |
| Update | `docs/plans/README.md` | plan index status |

No source-repository algorithm code, workflow registry, dataset, HF revision, or credential is
modified by this issue.

**Stacked on parent PR #3452.** Both `docs/architecture/algorithm-run-dataset-contract.yaml` and
`docs/governance/2026-07-10-algorithm-run-dataset-decision-manual.html` **404 on `main`** — they exist
only in draft **PR #3452** (`feature/issue-3427-hf-run-ledger-plan`). This implementation must be
STACKED ON #3452 (branch from it), not from `main`, or the files to edit will not exist.

**Shared-file merge coordination.** All five sibling contracts (**#3428–#3432**) edit the SAME
`algorithm-run-dataset-contract.yaml` + decision-manual as **strictly additive, non-overlapping**
sections. Since #3432 is blocked only by #3428+#3431, siblings #3429/#3430 may land in any relative
order — so land these edits in **dependency order** (#3428 → #3431 → #3432), or fold them into a single
**integration PR** onto #3452, to avoid clobbering (per the "N additive lanes sharing a file → one
integration PR" rule).

---

## TDD Test List

Every acceptance criterion maps to at least one first-fail test.

| Test | Verifies (AC) | Expected |
|---|---|---|
| `test_metric_definition_carries_all_required_fields` | AC1: id, algorithm id, definition version, label, meaning, unit/dimension, data type, derivation reference, applicability rule, directionality, quality rule | omit any field → definition rejected |
| `test_metric_observation_binds_run_and_definition_version` | AC2: observation records run, definition version, value, quality state, derivation evidence, optional uncertainty | missing run/version/value/quality/evidence → rejected; uncertainty optional |
| `test_units_and_not_applicable_are_machine_validatable` | AC3: unit tag required for numerics; not_applicable/null are explicit, typed, distinct | unit-less numeric rejected; NA ≠ null ≠ 0 all distinguished |
| `test_definition_versions_independently_history_retained` | AC4: definition versions increment independently; historical observation retains exact version | definition upgrade leaves prior observations pinned + intact |
| `test_definition_version_is_immutable_once_published` | AC4: append-only immutable definition store — no silent mutation of the definition under past observations | re-registering an existing `(metric_id, definition_version)` with ANY differing field (e.g. `unit_or_dimension` MPa→ksi) is REJECTED (fail closed); a semantic change MUST mint a NEW version |
| `test_failed_or_rejected_or_nonreproducible_run_excluded_from_population` | AC5: failed/rejected/non-reproducible runs cannot enter metric populations | `reproducible_failure`/rejected/non-reproducible observation excluded; still visible in run-health |
| `test_report_renders_without_cross_algorithm_equivalence` | AC6: tables/trends/comparisons render without treating unlike algorithm metrics as equivalent | per-algorithm grouping only; no comparison edge between distinct `algorithm_id`s |
| `test_fixtures_cover_scalar_categorical_vector_uncertainty_na_invalid` | AC7: fixtures cover scalar, categorical, vector/series reference, uncertainty, not-applicable, invalid | each fixture class validates/rejects as specified |
| `test_cross_algorithm_ontology_is_deferred_non_goal` | AC8: any cross-algorithm ontology explicitly deferred | contract declares deferral; no equivalence graph present; attempt to add a cross-algorithm equivalence edge rejected |
| `test_single_algorithm_owner_per_metric_id` | AC1/AC6 invariant: exactly one owning algorithm per metric | second algorithm claiming same `metric_id` rejected |
| `test_observation_owner_must_match_run_algorithm` | AC5/AC6: observation `metric_id` owner must equal run's `algorithm_id` | owner mismatch rejected |
| `test_quality_states_mutually_exclusive_and_typed` | AC3: valid/not_applicable/invalid/missing exclusive; only `valid` is population-eligible | invalid/missing/NA excluded from population |
| `test_definition_version_boundary_visible_in_trend` | AC4/AC6: trend spanning a version boundary does not splice unlike definitions | boundary rendered visibly, not merged silently |
| `test_envelope_hashes_are_evidence_not_metric_identity` | crosswalk: `result_hash`/`input_hash`/`code_version` never become metric id/value/version | metric records independent of envelope hashes |
| `test_decision_manual_matches_metric_contract` | AC parity: manual metric section ↔ contract YAML | structure + examples agree |

Fixtures explicitly include: a **scalar** numeric with unit; a **categorical** value; a
**vector/series reference** (content-addressed artifact ref, not inline array); an observation **with
uncertainty**; a **not-applicable** observation (applicability_rule false, NA sentinel); an
**invalid** observation (fails quality_rule); a **failed-run** observation (excluded from population,
visible in health); and a **cross-algorithm-equivalence** attempt (rejected). Tests are written first
and fail before implementation exists. Non-testable process gates (full-suite green, legal-scan
closeout, multi-provider review) are enforced at closeout, not silently dropped.

---

## Acceptance Criteria

Verbatim from issue #3432:

- [ ] A metric definition carries a stable identifier, algorithm identifier, definition version,
      label, meaning, unit/dimension, data type, derivation reference, applicability rule,
      directionality when meaningful, and quality rule.
- [ ] A metric observation identifies its run and metric definition version and records value,
      quality state, derivation evidence, and uncertainty when supplied.
- [ ] Units and null/not-applicable states are unambiguous and machine-validatable.
- [ ] Metric definitions are versioned independently from observations; historical observations retain
      the exact definition used.
- [ ] Failed, rejected, or non-reproducible runs cannot enter metric populations.
- [ ] Rolling algorithm reports can render metric tables, trends, and comparisons without treating
      unlike algorithm metrics as equivalent.
- [ ] Contract fixtures cover scalar, categorical, vector/series reference, uncertainty,
      not-applicable, and invalid observations.
- [ ] Scope explicitly defers any cross-algorithm ontology until real repeated-run evidence justifies
      one.

Process gates (this plan):

- [ ] TDD tests are written first and fail before implementation; the full suite passes on changed
      files.
- [ ] The legal scan (`scripts/legal/legal-sanity-scan.sh --diff-only`) passes on changed files.
- [ ] `scripts/enforcement/check-no-abs-paths.sh` passes on changed files.

---

## Sequencing & Gate

**Blocked by [#3428](https://github.com/vamseeachanta/workspace-hub/issues/3428) (run identity —
supplies `run_id`, terminal status, canonical_json + SHA-256 conventions) and
[#3431](https://github.com/vamseeachanta/workspace-hub/issues/3431) (output/report — the report that
consumes these observations and the curated-output/artifact references an observation's
`derivation_evidence` points at).** This contract extends the parent run-dataset contract, which is
in **draft PR #3452** on `feature/issue-3427-hf-run-ledger-plan` and is **not yet on `main`** — the
metric schema must be coordinated with that PR and must not fork its closed-schema behavior;
implementation is sequenced behind the parent contract + #3428 + #3431 landing on `main`. The
publication child [#3433](https://github.com/vamseeachanta/workspace-hub/issues/3433) consumes this
record shape for its succeeded-runs-only `metrics/` table.

**Stacked on PR #3452 + shared-file merge ordering.** The contract YAML and decision-manual exist only
in draft **PR #3452**, not on `main`, so implementation branches from **#3452**, not `main`. All five
siblings (**#3428–#3432**) edit those SAME two files as strictly additive, non-overlapping sections;
#3429/#3430 are unblocked and may land in any relative order, so land these edits in **dependency order**
(#3428 → #3431 → #3432) or via a single **integration PR** onto #3452 to avoid clobbering.

**HITL contract work.** This issue starts at `status:needs-plan`; implementation requires this
reviewed plan plus **explicit owner approval** — parent #3427 approval does not authorize it, and no
child implementation begins from approval of the epic alone.

---

## Adversarial Review Summary

| Round | Reviewer | Verdict | Result |
|---|---|---|---|
| r1 | Claude | BLOCK | 1 MAJOR (immutable-definition-store invariant untested — AC4's "no silent mutation of past observations" had no adversarial rejection test) + MINORs (shared-file merge coordination; `unit_or_dimension: "NA"` vs `quality_state: not_applicable` "NA" token collision; `metric_id` prefix-validation rule; AC1 directionality strengthening; reference-impl home + stacked-on #3452). **ALL REMEDIATED** this revision. |

No unavailable provider counts as approval; any depth reduction is disclosed for explicit owner
acceptance, consistent with the parent and siblings.

---

## Risks and Open Questions

- **Not-applicable-vs-missing conflation risk:** if the four quality states are not enforced
  distinctly, a report could render a genuinely inapplicable metric as a blank read as zero, corrupting
  a trend. Mitigation: `quality_state` is a closed enum with an explicit `"NA"` sentinel and a
  first-fail test asserting NA ≠ null ≠ 0; only `valid` is population-eligible.
- **Definition-drift trend risk:** a silent definition upgrade could splice incompatible values into
  one trend. Mitigation: every observation pins its exact `metric_definition_version`; trends across a
  version boundary render the boundary visibly (tested).
- **Premature cross-algorithm ontology risk:** pressure to unify metrics across algorithms before
  evidence exists would violate the epic's locked "no cross-algorithm equivalence." Mitigation: single
  owner per `metric_id`, no equivalence edge, and an explicit deferral non-goal — a cross-algorithm
  equivalence attempt is a *rejected* test case, not a TODO.
- **Vector/series inline-payload risk:** inlining large series into an observation would bloat the
  `metrics/` table and lose native meaning. Mitigation: `data_type: vector_series_reference` points at
  a content-addressed artifact (#3429); the observation carries the reference, not the array.
- **Silent-definition-mutation risk (AC4 core):** re-registering an existing
  `(metric_id, definition_version)` with a changed field (e.g. `unit_or_dimension` MPa→ksi) would
  retroactively alter the meaning of every past observation pinned to that version. Mitigation: the
  definition store is **append-only / immutable**; `test_definition_version_is_immutable_once_published`
  asserts any differing-field re-registration FAILS CLOSED, forcing a new `definition_version`.
- **Reference-implementation home — DECIDED:** `assetutilities.workflow_api.metrics` (inherits
  `#3433`'s owner-confirmed `assetutilities.workflow_api` placement, so `#3433`'s projection imports one
  implementation). No longer open.
- **Parent-contract coupling + shared-file clobber risk:** the contract YAML and decision-manual are in
  draft PR #3452 (404 on `main`), and all five siblings (#3428–#3432) edit them as additive,
  non-overlapping sections; #3429/#3430 land in any order. Mitigation: STACK this work on #3452; land in
  dependency order (#3428 → #3431 → #3432) or via one integration PR; fail closed on schema drift.

---

## Complexity: T2

A single-domain, algorithm-scoped contract slice with a small reference validator + fixtures. Not T3:
no external platform, no cross-system transaction, no multi-repository publication (that is `#3433`).
It is nonetheless load-bearing — its population rule and single-owner / no-cross-algorithm-equivalence
invariants are what keep every downstream comparison, insight, and decision brief evidence-bound and
algorithm-scoped, so its fail-closed proofs must hold.
