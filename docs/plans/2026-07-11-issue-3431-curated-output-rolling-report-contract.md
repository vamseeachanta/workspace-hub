# Plan for [#3431](https://github.com/vamseeachanta/workspace-hub/issues/3431): Curated Output and Rolling Algorithm Report Contract

> **Status:** adversarial-reviewed (r1 BLOCK remediated; ready for user review)
> **Complexity:** T2
> **Date:** 2026-07-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3431
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** `scripts/review/results/2026-07-11-plan-3431-{claude,codex,gemini}.md`

---

## Resource Intelligence Summary

### Existing repo code

- `assetutilities/src/assetutilities/workflow_api/envelope.py` — `ResultEnvelope` exposes a
  location-independent content `result_hash` for `kind: files` (a hash of curated output *bytes*),
  `code_version()`, a volatile-key-pruned `input_hash`, and `reproducible` (`None` unless an opt-in
  double run runs). `result_hash` is the closest existing surface to an output digest, but it is
  **execution evidence, not a published contract**: it hashes whatever the run emitted, carries no
  role/native-schema/units/validation metadata, has no declared canonicalizer, and does not fail
  closed on volatile content. This contract re-derives a **versioned `output_equality_digest`** and
  treats `result_hash` as evidence only, never an alias.
- `digitalmodel/src/digitalmodel/workflow_api/{runner,provenance,golden}.py` — the runner emits
  output files and `stamp_provenance` assembles provenance; the golden harness compares runs against
  goldens. These produce **native domain outputs** (e.g. tabular results, plots, solver artifacts)
  with no normative Output *record* separating curated primary results from transient scratch, and no
  standard report. dm [#1528](https://github.com/vamseeachanta/digitalmodel/issues/1528) (coupled
  sloshing CFD) is a concrete producer whose per-run manifest lists synchronized time-history traces,
  a report hash, and output files — a real test of non-flattening native-schema output handling.
- `worldenergydata/src/worldenergydata/workflow_api/runner.py` — consumes the same envelope; a
  dataset-backed algorithm whose outputs must reference pinned inputs (per #3430) and whose report
  must pin exact HF revisions.
- `docs/architecture/execution-manifest.schema.yaml` (on `main`) and
  `docs/architecture/report-evidence-bundle.schema.yaml` (on `main`, per #3433 standards table) —
  the report-evidence-bundle schema is the **reuse-and-extend** base for the rolling report's
  evidence sections; this contract extends it with the mandatory Inputs/Outputs structure, the
  failed-run health section, and the exact-revision pin, rather than inventing a parallel bundle.
- **Gap:** no normative Output record (role / native schema / media type / shape / units / convention
  / validation state / review state / artifact refs), no curated-vs-excluded taxonomy, no non-overlapping
  success/failure output requirements, no stable normalized failure signature, no versioned
  `output_equality_digest`, and no one-per-algorithm rolling HTML report contract exist anywhere.

### Standards

| Standard | Status | Source |
|---|---|---|
| Parent run-dataset contract (output/report decisions, exclusions) | binding, extended here | `#3427` plan + `docs/architecture/algorithm-run-dataset-contract.yaml` (in **draft PR #3452**, not yet on `main`) |
| Sibling identity contract (run_id, output_equality_digest ownership boundary) | binding, consumed | `#3428` plan (this session) |
| Sibling artifact contract (content-addressed artifact refs) | binding, referenced | `#3429` (outputs reference artifacts by digest; do not redefine) |
| Report evidence bundle | reusable, extended | `docs/architecture/report-evidence-bundle.schema.yaml` |
| Data/execution/report boundaries | reusable | `docs/architecture/execution-manifest.schema.yaml` |
| Issue lifecycle + approval | binding | `AGENTS.md`, `docs/plans/README.md` |
| Legal/abs-path scans + HTML safety | binding | `scripts/legal/legal-sanity-scan.sh`, `scripts/enforcement/check-no-abs-paths.sh` |

No engineering-calculation standard governs the output/report *contract* itself; producing algorithms
retain their own calculation-citation obligations for the values they emit.

### Documents consulted

- Issue [#3431](https://github.com/vamseeachanta/workspace-hub/issues/3431) (read live 2026-07-11):
  Output contract fields (role, native schema, media type, shape/row count, units, coordinate/sign
  convention, validation state, review state, artifact references); curated vs excluded taxonomy;
  non-overlapping success/failure output requirements; stable normalized diagnostic signature;
  exact-rerun output-digest match with fail-closed no-overwrite; one rolling HTML report per algorithm
  with mandatory Inputs + Outputs and only-applicable optional sections; latest + historical runs,
  failed-run separation, exact-HF-revision links; git history preserves report evolution while
  immutable run records remain the data authority; valid/invalid fixtures; decision manual documents
  the rules. Blocked by #3428 and #3429.
- Parent [#3427](https://github.com/vamseeachanta/workspace-hub/issues/3427) plan: machine-readable
  outputs preserve native domain schema and reference content-addressed artifacts without flattening
  engineering meaning; ONE rolling report per algorithm; byte identity vs a **versioned semantic
  equality digest**; failed runs appear in health analysis but never contribute metrics/insights/
  decisions; report compares immutable historical runs pinned to exact HF revisions; no per-run HTML.
- Sibling identity contract [#3428](https://github.com/vamseeachanta/workspace-hub/issues/3428) plan
  (this session): `run_id` **excludes** outputs; the exact-rerun check compares a **separate,
  versioned `output_equality_digest` that THIS contract (#3431) owns and defines**; a mismatch is a
  reproducibility defect that fails closed and cannot mutate/overwrite the prior record. This is the
  boundary the two contracts share: #3428 mints identity; #3431 defines the output digest #3428
  compares.
- Publication child [#3433](https://github.com/vamseeachanta/workspace-hub/issues/3433) plan (this
  session): the CRITICAL consumer. The rolling report is **drafted at state 3** (unpinned); egress
  **Gate B** scans the draft; **Gate D** re-scans the FINAL pinned report before the source-repo
  commit; the report is finalized only after pinning the EXACT verified HF revision; a moving/`main`
  reference must FAIL. The Publication acceptance **ledger** lives in the SOURCE REPO
  (`reports/<algorithm>/publications.jsonl`), NOT in the HF dataset; the report renders eligibility
  from that ledger. This contract's report structure must be consistent with all of the above.
- Artifact contract [#3429](https://github.com/vamseeachanta/workspace-hub/issues/3429): outputs
  reference content-addressed artifacts by SHA-256 digest + residency policy — **referenced, not
  redefined** here.
- Report-evidence base: `docs/architecture/report-evidence-bundle.schema.yaml` — the evidence-section
  vocabulary this report extends.

### Gaps identified

- No normative Output record enumerates role, native schema, media type, shape/row count, units,
  coordinate/sign convention, validation state, review state, and artifact references in one shape.
- No taxonomy distinguishes curated primary results / supporting validation evidence / selected
  reports / decision-support outputs from EXCLUDED transient outputs.
- No explicit non-overlapping success-vs-failure output requirement, and no stable normalized failure
  signature that excludes volatile timestamps/path noise.
- No versioned `output_equality_digest` (raw-byte default; declared semantic canonicalizer as the
  only exception; undeclared canonicalizer fails closed).
- No one-per-algorithm rolling HTML report contract (mandatory Inputs/Outputs, only-applicable
  optional sections, latest + historical + failed-run separation, exact-HF-revision pins, git-history
  evolution, safe HTML).

### Evidence (verified 2026-07-11)

```text
#3431           OPEN status:needs-plan lane:claude — Blocked by: #3428, #3429 (verified live via gh)
#3428 / #3429   OPEN status:needs-plan (identity + artifact contracts this plan consumes)
DRAFT PR #3452  feat: define algorithm run ledger … (parent #3427 contract; NOT on main)
404 @main       docs/architecture/algorithm-run-dataset-contract.yaml
EXISTS @main    docs/architecture/report-evidence-bundle.schema.yaml (report evidence base)
EXISTS @main    docs/architecture/execution-manifest.schema.yaml
EXISTS          assetutilities …/workflow_api/envelope.py (result_hash = output-byte hash; evidence only)
EXISTS          digitalmodel …/workflow_api/{runner,provenance,golden}.py (native outputs; no report)
#3433           plan-approved consumer: report drafted@3 (Gate B) → pinned@6 (Gate D) → ledger in source repo
```

Distinct sources: issue #3431; parent #3427 plan; sibling #3428 plan; consumer #3433 plan; artifact
#3429; the report-evidence-bundle schema; ResultEnvelope `result_hash`; dm #1528 producer — more than
the required three.

---

## Deliverable

A normative, machine-validated **curated Output record and rolling algorithm report contract**: the
Output record shape (role, native schema, media type, shape/row count, units, coordinate/sign
convention, validation state, review state, artifact references); the curated-vs-excluded output
taxonomy; explicit non-overlapping success/failure output requirements; a stable normalized failure
diagnostic signature; the **versioned `output_equality_digest`** (raw-byte default, declared semantic
canonicalizer as the sole exception, undeclared canonicalizer fails closed); and the one-per-algorithm
rolling HTML report contract (mandatory Inputs + Outputs, only-applicable optional sections, latest +
historical + separated failed runs, exact-HF-revision pins, git-history evolution, safe HTML). A
reference implementation + valid/invalid fixtures prove the rules; the decision manual documents the
output-selection and report-section rules. **This plan builds nothing** — it defines the contract, its
tests, and its fixtures; code lands only after review and explicit approval, and after #3428/#3429 and
the parent contract land on `main`.

---

## Design

### 1. Output record (curated, native, artifact-referencing)

One record per curated output; native domain schema preserved, engineering meaning never flattened.

```text
OutputRecord
  role                  curated_primary_result | supporting_validation_evidence |
                        selected_report | decision_support        # taxonomy §2; EXCLUDED transients omitted, never recorded
  native_schema         { schema_id, schema_version }             # domain-native shape; NOT flattened to a generic blob
  media_type            e.g. application/parquet, application/json, image/svg+xml, application/pdf
  shape                 { rows, cols } | { dims:[...] } | null     # row count / tensor shape where applicable
  units                 per-field unit tags (declared allowlist); a units-bearing field WITHOUT a unit tag FAILS
  convention            coordinate/sign/frame convention WHERE APPLICABLE (e.g. "z-down, tension +"); null when N/A
  validation_state      passed | failed | not_applicable          # against the output's declared schema/domain checks
  review_state          machine_only | human_reviewed | not_required
  artifact_refs[]       -> #3429 content-addressed artifact by { sha256, media_type, residency }  # REFERENCE, not redefine
  digest_contribution   included (DEFAULT) | excluded              # feeds output_equality_digest (§4)
                        # DEFAULTS to `included` for every curated output. `excluded` is permitted
                        # ONLY via an explicitly declared + justified exclusion rule (mirrors the
                        # fail-closed semantic-canonicalizer pattern of §4). An undeclared/silent
                        # exclusion FAILS CLOSED (treated as `included`, i.e. the omission is rejected).
```

Invariants: a curated output MUST carry `role`, `native_schema`, `media_type`, and `artifact_refs`;
units-bearing numeric fields MUST carry unit tags (missing tag → fail closed); a coordinate/sign
convention is mandatory *where applicable* and omitting it for a directional quantity fails.
Every curated output is digest-eligible by default: `digest_contribution` defaults to `included`, and
an output may be `excluded` from `output_equality_digest` ONLY through an explicitly declared and
justified exclusion rule (the same fail-closed pattern §4 uses for the semantic canonicalizer). An
undeclared/silent exclusion fails closed. **Rationale:** an unguarded exclusion could silently drop a
nondeterministic curated output (e.g. a `selected_report` PDF with an embedded timestamp) from the
digest, so the exact-rerun equality check (§4, AC5) would pass while the real emitted bytes differ —
a masked reproducibility defect that defeats AC5. Requiring exclusions to be declared + justified keeps
the digest honest.

### 2. Curated vs excluded taxonomy

Every curated output is digest-eligible **by default** (§1 `digest_contribution` defaults to
`included`); a curated output leaves the digest set ONLY through an explicitly declared + justified
exclusion rule, never silently. This resolves the §1/§4 boundary: "all curated is digest-eligible" is
the default, and the sole escape is a fail-closed declared exclusion.

```text
CURATED (recorded + digest-eligible by default):
  curated_primary_result       the algorithm's authoritative engineering output(s)
  supporting_validation_evidence  goldens, residuals, convergence traces that substantiate the result
  selected_report              a curated human-facing artifact (e.g. a PDF one-pager) chosen for publication
  decision_support             screens/underwriting outputs meant to inform a decision

EXCLUDED (transient — NEVER recorded, NEVER digested, NEVER published):
  scratch/intermediate scratch files, solver temp dirs, re-derivable caches, volatile logs,
  anything not declared curated. Exclusion is by DECLARED allowlist of curated roles; an undeclared
  output defaults to EXCLUDED (fail-closed: unlabelled ≠ curated).
```

### 3. Non-overlapping success vs failed terminal-run output requirements

```text
status = succeeded          => MUST carry >=1 curated_primary_result; MAY carry the other curated roles;
                               MUST NOT carry a failure signature.
status = reproducible_failure => MUST carry a normalized failure signature (§3a) + curated diagnostic
                               artifacts; MUST NOT carry curated_primary_result / metrics / insights /
                               decision_support outputs. It appears ONLY in the report's health analysis.
```

The two requirement sets are **disjoint**: a record set satisfying one MUST violate the other. A
"succeeded" run bearing a failure signature, or a "failed" run bearing a primary result or feeding
metrics, fails validation closed.

#### 3a. Stable normalized diagnostic signature

```text
failure_signature = { phase, code, signature_digest }
  phase             normalized enum (e.g. input_validation | solve | postprocess | export)
  code              normalized failure code (declared vocabulary, not a raw exception string)
  signature_digest  sha256(canonical_json(NORMALIZED evidence)) where normalization STRIPS:
                      absolute paths -> repo-relative or "<path>" tokens
                      volatile timestamps -> removed
                      pids / hostnames / tmpdir nonces / memory addresses -> removed
                    and RETAINS the stable fault shape (phase, code, normalized message skeleton,
                    normalized stack frame set). Same fault on two machines => identical signature_digest.

  Stack-frame normalization: REPO frames keep their repo-relative path + `func`. Third-party / stdlib /
  venv frames are normalized by module `qualname` — DROP the file path, KEEP `module.func` — so venv
  paths (`/home/a/.venv` vs `/home/b/.venv`) do not break cross-machine signature stability, and
  distinct third-party frames do NOT over-collapse to a single `<path>` token.
```

Curated diagnostic artifacts (a trimmed log, a residual plot) are referenced as artifacts (#3429);
their *volatile* bytes are not what the signature hashes — the normalized shape is.

### 4. Versioned `output_equality_digest` (owned by this contract)

`#3428` mints `run_id` (excluding outputs). This contract defines the **separate** digest `#3428`'s
exact-rerun check compares.

**Ownership across the one-way blocking edge (#3428 blocks #3431):** #3428 references the
`output_equality_digest` **concept** and owns ONLY the mismatch → reject-with-no-mutation **policy**,
injecting the digest as an opaque/stub value it does not compute; #3431 **owns the digest's
computation** (scheme, `mode`, canonical ordering, and value below). Ownership is therefore
unambiguous: #3428 decides what happens on mismatch, #3431 decides how the digest is produced.

```text
output_equality_digest = {
  version       digest-scheme version (bumped when the scheme changes; recorded per run)
  mode          "raw_byte" (DEFAULT) | "semantic:<canonicalizer_id>@<ver>" (ONLY declared exception)
  value         sha256 over:
                  raw_byte  : sha256(canonical_json(SORTED list of the per-artifact sha256 of every
                              digest-eligible curated OutputRecord)). Each artifact already carries a
                              sha256 per #3429; canonical_json reuses #3428's pinned canonicalization.
                              This is a digest-of-digests, NOT a raw-byte concatenation — concatenation
                              is boundary-ambiguous (`[A][B]` and `[AB][]` collide), so it is forbidden.
                  semantic  : the DECLARED canonicalizer's normalized form of those outputs
}
```

Rules (fail-closed throughout):
- **Default is raw-byte.** No canonicalization unless a semantic canonicalizer is **explicitly
  declared** for the algorithm's output schema.
- An output that claims a semantic canonicalizer that is **not declared/registered** fails closed
  (an undeclared canonicalizer is never inferred or silently applied).
- On an **exact rerun** (same `run_id`), the recomputed `output_equality_digest` MUST match the stored
  one. A **mismatch fails publication** and **cannot overwrite** the prior immutable record — it is a
  reproducibility defect, surfaced, never merged.
- The digest `version` and `mode` are stored with the run so a later reader knows exactly how equality
  was decided.

### 5. Rolling HTML report contract (one per algorithm)

```text
reports/<algorithm>/report.html            # ONE rolling report per algorithm, in the SOURCE repo
  MANDATORY sections (always present):
    Inputs    the algorithm's replayable public inputs (per #3430), pinned
    Outputs   curated OutputRecords (roles, native schema, units, convention, validation/review state,
              artifact links)
  OPTIONAL sections (rendered ONLY when applicable to the algorithm/run set):
    metrics | plots | comparisons | uncertainty | diagnostics | insights | decision_briefs
  ALWAYS-present run panorama:
    latest run + historical runs, comparing IMMUTABLE historical runs
    FAILED runs are rendered in a CLEARLY SEPARATED health-analysis section — visible, but they
      contribute NOTHING to metrics / insights / comparisons / decision briefs
    EVERY displayed run links to an EXACT Hugging Face revision (immutable commit sha)
    eligibility is rendered FROM the source-repo publications.jsonl ledger (#3433), never inferred
      from HF visibility
```

Report invariants:
- **No per-run HTML reports.** Exactly one rolling report per algorithm; new runs update it in place.
- **Exact-revision pins only.** A moving/`main`/branch reference (not an immutable commit sha) FAILS —
  consistent with #3433 CROSS_VERIFIED and its "moving reference must fail" rule.
- **Draft/pin lifecycle (consumed by #3433):** the report is **drafted unpinned at state 3** (egress
  Gate B scans the draft), then **finalized only after pinning the exact verified HF revision at state
  6** (egress Gate D re-scans the FINAL pinned bytes before the source-repo commit). This contract
  MUST NOT assume the report is pinned at draft time.
- **Data authority vs presentation:** the immutable run records (in the HF dataset) remain the **data
  authority**; the report is a **projection**. Git history of `report.html` preserves the report's
  *evolution*, but never becomes the source of truth for run data.
- **Safe HTML only:** all run-derived text is escaped/sanitized; no unsafe HTML (no injected
  `<script>`, event handlers, `javascript:` URIs, or raw untrusted markup) can reach the rendered
  report. Untrusted content that would inject executable markup fails the render closed.

---

## Pseudocode

```text
# --- Output record admission ---
for each declared curated output:
    require role in curated taxonomy; else EXCLUDED (unlabelled => excluded, fail-closed)
    require native_schema{id,version}, media_type, artifact_refs (#3429, by sha256)
    require unit tag on every units-bearing field           # missing tag => FAIL
    require convention where quantity is directional         # missing => FAIL
    set validation_state / review_state
    digest_contribution defaults to "included"; "excluded" only via a declared + justified rule
      (undeclared/silent exclusion => FAIL CLOSED)
    reject any output whose payload violates its declared native_schema{id,version}   # AC9
transient/undeclared outputs => NOT recorded, NOT digested

# --- Non-overlapping success/failure ---
if status == succeeded:            require >=1 curated_primary_result; forbid failure_signature
if status == reproducible_failure: require normalized failure_signature + diagnostic artifacts;
                                   forbid primary_result/metrics/insights/decision_support
assert requirement-sets disjoint (violating overlap => FAIL)

# --- Failure signature normalization ---
signature_digest = sha256(canonical_json(strip(paths, timestamps, pids, hosts, nonces))(evidence))
# same fault, two machines => identical digest

# --- Output equality digest (computation OWNED here; mismatch POLICY owned by #3428) ---
mode = "raw_byte" UNLESS an explicitly declared semantic canonicalizer exists
if mode claims semantic but canonicalizer undeclared: FAIL CLOSED
raw_byte value = sha256(canonical_json(SORTED per-artifact sha256 of every digest-eligible output))
                 # digest-of-digests, reuses #3428 canonical_json; NOT raw-byte concatenation
output_equality_digest = { version, mode, value }
on exact rerun (same run_id): recompute; MISMATCH => #3428 policy rejects, NO overwrite of prior record

# --- Rolling report render ---
render ONE report per algorithm: MANDATORY Inputs + Outputs; optional sections ONLY when applicable
show latest + historical (immutable) runs; SEPARATE failed runs into health analysis (no metric/insight/decision)
link every displayed run to an EXACT HF revision (moving ref => FAIL)
render eligibility from source-repo publications.jsonl (#3433), not HF visibility
escape/sanitize all run-derived text (unsafe HTML => FAIL); draft unpinned@state3, finalize pinned@state6
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Update | `docs/architecture/algorithm-run-dataset-contract.yaml` (**stacked on parent PR #3452**; YAML is 404 on `main`) | add — as a STRICTLY ADDITIVE, NON-OVERLAPPING section (all five siblings edit this one file; land in dependency order or via one integration PR) — the normative Output record schema + curated/excluded taxonomy + success/failure requirements + `output_equality_digest` scheme + report-section rules |
| Create | `assetutilities/src/assetutilities/workflow_api/output_contract.py` (DECIDED home) | Output record validation; unit/convention checks; failure-signature normalizer; versioned `output_equality_digest`; importable by #3433 projection |
| Create | `assetutilities/src/assetutilities/workflow_api/report_template.{py,html}` | rolling-report template + reference renderer (mandatory Inputs/Outputs, applicable optional sections, failed-run separation, exact-revision pins, HTML sanitization) — consumed by #3433 |
| Create | `assetutilities/tests/workflow_api/test_output_contract.py` + `fixtures/output/{valid,invalid}/…` | valid/invalid output + failure-signature + digest fixtures |
| Create | `assetutilities/tests/workflow_api/test_report_contract.py` + `fixtures/report/{valid,invalid}/…` | report structure, exact-revision pin, unsafe-HTML, failure-leakage fixtures |
| Update | `docs/governance/2026-07-10-algorithm-run-dataset-decision-manual.html` (in PR #3452) | output-selection rules + report-section rules + curated/excluded + failure-signature examples |
| Create | `tests/architecture/test_output_report_contract_parity.py` | assert the decision-manual output/report section matches the contract YAML |
| Update | `docs/plans/README.md` | plan index status |

No source-repository algorithm code, workflow registry, HF dataset, rolling report, or credential is
modified by this planning issue. Pilot rolling reports are authored under #3433's pilot gates (dm
#1505 / wed #927), not here.

---

## TDD Test List

Every acceptance criterion maps to a failing-first test.

| Test | Acceptance criterion | Expected |
|---|---|---|
| `test_output_record_defines_all_contract_fields` | AC1 (role/native schema/media type/shape/units/convention/validation/review/artifact refs) | omitting any required field rejects |
| `test_units_bearing_field_missing_unit_tag_fails` | AC1 (units) | units-bearing field with no unit tag → FAIL closed |
| `test_directional_quantity_missing_convention_fails` | AC1 (coordinate/sign convention where applicable) | directional output without convention rejected |
| `test_output_native_schema_not_flattened` | AC1 + parent (preserve native schema) | nested engineering payload round-trips without flattening |
| `test_curated_vs_excluded_taxonomy` | AC2 | curated roles recorded; undeclared/transient output EXCLUDED (unlabelled → excluded) |
| `test_success_and_failure_requirements_are_disjoint` | AC3 | succeeded needs primary result + no signature; failure needs signature + no primary; overlap fails |
| `test_failed_run_carries_no_primary_result_or_metrics` | AC3 + AC(failure leakage) | failed run with a primary result / metric contribution rejected |
| `test_failure_signature_is_stable_across_machines` | AC4 | same fault, different cwd/host/timestamps → identical `signature_digest` |
| `test_failure_signature_strips_volatile_noise` | AC4 | timestamps/paths/pids removed; stable shape retained |
| `test_digest_contribution_defaults_included_and_exclusion_must_be_declared` | AC5 (§1/§2/§4 reconcile) | curated output defaults `digest_contribution: included`; a silent/undeclared `excluded` fails closed; only an explicitly declared + justified exclusion rule removes it from the digest |
| `test_output_equality_digest_default_is_raw_byte` | AC5 (+ #3428 boundary) | absent a declared canonicalizer, digest is raw-byte |
| `test_raw_byte_digest_is_sorted_per_artifact_sha_not_concatenation` | AC5 | raw_byte value = sha256(canonical_json(sorted per-artifact sha256)); boundary-ambiguous concatenation rejected |
| `test_undeclared_semantic_canonicalizer_fails_closed` | AC5 | claimed-but-undeclared canonicalizer rejected |
| `test_exact_rerun_output_digest_mismatch_fails_no_overwrite` | AC5 | mismatch fails publication; prior immutable record intact |
| `test_report_has_mandatory_inputs_and_outputs_sections` | AC6 | report missing Inputs or Outputs rejected |
| `test_report_optional_sections_only_when_applicable` | AC6 | non-applicable optional section omitted, not empty-rendered |
| `test_report_shows_latest_and_historical_separates_failed` | AC7 | failed runs isolated in health section; excluded from metrics/insights/comparisons/decisions |
| `test_report_links_every_run_to_exact_hf_revision` | AC7 | each displayed run links to an immutable commit sha |
| `test_report_stale_or_moving_revision_link_fails` | AC7 (+ #3433 moving-ref rule) | `main`/branch/moving ref → FAIL |
| `test_report_renders_eligibility_from_source_ledger` | AC7 (+ #3433) | eligibility read from `publications.jsonl`, not HF visibility |
| `test_output_violating_declared_native_schema_rejected` | AC9 (schema mismatch) | an output whose payload violates its declared `native_schema{id,version}` is rejected (dedicated case, not only the umbrella fixtures test) |
| `test_report_rejects_unsafe_html_content` | AC9 (unsafe HTML) | injected `<script>`/handler/`javascript:` sanitized or render fails |
| `test_one_rolling_report_no_per_run_html` | AC6/AC8 + parent | one report per algorithm; no per-run HTML emitted |
| `test_git_history_preserves_report_evolution_records_are_authority` | AC8 | concrete observable: two committed report revisions exist in git history AND the run records are unmutated across them (report is regenerable from the records; records never rewritten to match the report) |
| `test_invalid_fixtures_cover_all_required_cases` | AC9 | fixtures cover schema mismatch, missing units, unsafe HTML, stale revision links, failure leakage, output digest mismatch |
| `test_decision_manual_matches_output_report_contract` | AC10 | manual output-selection + report-section rules ↔ contract YAML parity |
| `test_legal_and_abs_path_scans_pass` | AC (process) | `legal-sanity-scan.sh --diff-only` + `check-no-abs-paths.sh` exit 0 on changed files |

Tests are written first and fail before implementation exists. Non-testable process gates (full-suite
green, legal-scan closeout, substantive multi-provider review) are classified as process/CI gates and
enforced at closeout, not silently dropped.

---

## Acceptance Criteria

Verbatim from issue #3431:

- [ ] The Output contract defines role, native schema, media type, shape/row count, units,
      coordinate/sign convention where applicable, validation state, review state, and artifact
      references.
- [ ] Curated primary results, supporting validation evidence, selected reports, and decision-support
      outputs are distinguishable from excluded transient outputs.
- [ ] Successful and failed terminal runs have explicit, non-overlapping output requirements.
- [ ] Failure evidence excludes volatile timestamps/path noise and yields a stable normalized
      diagnostic signature.
- [ ] Exact reruns must match curated output digests; mismatches fail publication and cannot overwrite
      prior records.
- [ ] One standard rolling HTML report per algorithm renders mandatory Inputs and Outputs sections and
      only applicable optional sections.
- [ ] The report shows latest and historical runs, clearly separates failed runs, and links every
      displayed run to an exact Hugging Face revision.
- [ ] Repository Git history preserves report evolution while immutable run records remain the data
      authority.
- [ ] Valid/invalid fixtures cover schema mismatch, missing units, unsafe HTML content, stale revision
      links, failure leakage into metrics, and output digest mismatch.
- [ ] The decision manual documents the output selection and report-section rules.

Process (this plan):

- [ ] TDD tests are written first and fail before implementation; every acceptance criterion above
      maps to at least one failing-first test in the TDD list.
- [ ] The full suite, the legal scan (`scripts/legal/legal-sanity-scan.sh --diff-only`), and
      `scripts/enforcement/check-no-abs-paths.sh` pass on changed files.

---

## Sequencing & Gate

**Blocked by #3428 (deterministic run identity) and #3429 (content-addressed artifact).** This
contract owns the `output_equality_digest` that #3428's exact-rerun check compares (compute here;
mismatch policy in #3428), and its Output records reference #3429 artifacts by digest — so it cannot
land before both. It extends the parent run-dataset contract, whose YAML
(`docs/architecture/algorithm-run-dataset-contract.yaml`) and decision manual are **404 on `main` and
exist only in parent draft PR #3452**; this implementation is therefore **STACKED ON PR #3452** and
coordinates the Output/report schema with it, and must not fork the closed-schema behavior. All five
sibling contracts edit that same contract YAML as **STRICTLY ADDITIVE, NON-OVERLAPPING sections**,
landing in dependency order (or coalesced via ONE integration PR) so no sibling clobbers another's
section. It is a HITL contract child of epic #3427 and **requires its own reviewed plan and explicit
own-approval** — parent #3427 approval does not authorize it. Downstream consumer #3433 depends on this
report template + output contract reference implementation.

---

## Adversarial Review Summary

| Round | Reviewer | Verdict | Result |
|---|---|---|---|
| r1 | Claude | BLOCK | 1 MAJOR (`digest_contribution` §1/§2 contradiction: free included\|excluded toggle vs "all curated is digest-eligible") + MINORs (raw_byte digest = sorted per-artifact sha256 not concatenation; #3428/#3431 digest ownership boundary; non-repo failure-frame `qualname` normalization) + NITs (dedicated native-schema-mismatch test; concretized AC8 git-history observable). ALL remediated. |

No unavailable provider counts as approval; any depth reduction is disclosed for owner acceptance.

---

## Risks and Open Questions

- **Semantic-canonicalizer scope risk:** an over-permissive semantic mode would let two genuinely
  different output sets hash equal, masking a reproducibility defect. Mitigation: raw-byte is the
  default; a semantic canonicalizer applies only when **explicitly declared and registered** for the
  output schema, is versioned in the stored digest, and an undeclared canonicalizer fails closed.
- **Native-schema-vs-flattening tension:** preserving native domain schema (Parquet/JSONL/tensor
  shapes) while keeping outputs digestible risks either over-flattening (losing engineering meaning)
  or under-specifying the digest. Mitigation: outputs reference content-addressed artifacts (#3429)
  by byte digest; the record carries native `schema_id`/`schema_version`/shape/units so meaning is
  preserved alongside the digest.
- **Report draft/pin coupling risk:** #3433 drafts the report unpinned (state 3) and pins it later
  (state 6); a contract that assumed pin-at-draft would break the consumer. Mitigation: the report
  contract explicitly models the unpinned-draft → exact-revision-pin lifecycle and forbids moving
  references only at finalization.
- **Parent-contract coupling risk:** the contract YAML + decision manual are 404 on `main`, present
  only in parent draft PR #3452, so this work is **stacked on #3452**. Mitigation: coordinate the
  Output/report schema with #3452; fail closed on schema drift; a parity test binds the manual to the
  YAML.
- **Sibling YAML-collision risk:** all five sibling contracts edit the single contract YAML in #3452.
  Mitigation: each sibling adds a STRICTLY ADDITIVE, NON-OVERLAPPING section and they land in
  dependency order (or are coalesced into ONE integration PR), so no sibling clobbers another's
  section.
- **Reference-implementation home — DECIDED:** `assetutilities.workflow_api.output_contract` +
  `report_template` (inherits #3433's owner-confirmed `assetutilities.workflow_api` placement, so
  #3433's publication module imports one implementation, consistent with #3428's identity home). No
  longer an open question.

---

## Complexity: T2

A normative contract slice with a small deterministic reference implementation (output validation,
failure-signature normalizer, versioned `output_equality_digest`, report renderer) plus valid/invalid
fixtures. Not T3: single-domain, no external platform transaction, no cross-system commit — the HF
upload/pin/verify choreography lives in #3433. But it is load-bearing: it owns the output digest the
identity contract compares and the report template the publication workflow renders, so its
fail-closed semantics and HTML-safety proofs are consequential.
