# Plan for #2454: Validate flagship generic-track OrcaFlex mooring case via turret-moored FPSO semantic proof

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2454
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2454-claude.md | scripts/review/results/2026-04-23-plan-2454-codex.md | scripts/review/results/2026-04-23-plan-2454-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `digitalmodel/scripts/semantic_validate.py` — taxonomy-aware comparison engine referenced by `SEMANTIC_DIFF_TAXONOMY.md`. This is the authoritative classification tool; the plan reuses it rather than introducing a parallel comparator.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/generic_builder.py` — owns `_SKIP_GENERAL_KEYS` (34 dormant keys) and `_SKIP_OBJECT_KEYS` (2 keys). Any generic-track C3 omission must come from this list.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/__init__.py` + `cli.py` + `extractor.py` + `post_validator.py` — full generator entry points (`ModularModelGenerator`). Pattern already used by `tests/solvers/orcaflex/modular_generator/test_modular_vs_monolithic.py` for `24in_pipeline` spec — reusable as a structural analog.
- Found: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_extractor.py`, `test_semantic_roundtrip.py`, `test_modular_vs_monolithic.py` — existing modular-generator test surface. None of the three currently covers `c03_turret_moored_fpso` (grep proof below).
- Found: `digitalmodel/tests/solvers/orcaflex/reporting/fixture_helpers.py` — defines `fpso_fixture_metadata_path`, `load_fpso_fixture_metadata`, `build_report_from_metadata`; provides a reporting surface but does not run the modular generator or compare against monolithic native YAML.
- Found (already tracked — do NOT recreate): `digitalmodel/tests/fixtures/reporting/fpso_turret.metadata.json`, `.report.snapshot.html`, `tests/solvers/orcaflex/reporting/test_fpso_fixture_integration.py`, `test_fpso_fixture_snapshot.py`. These are a reporting-baseline regression guard, not semantic equivalence proof. They assert a hand-authored metadata baseline against a frozen HTML; they never call the modular generator or `scripts/semantic_validate.py`.
- Gap: no committed native-YAML generation from `c03_turret_moored_fpso/spec.yml`, no taxonomy-classified diff artifact for C03, no pytest guarding C5/C6 diff count.

### Standards
Not directly standards-driven. Engineering tolerance comes from `SEMANTIC_DIFF_TAXONOMY.md` (C6 class — 5% / 10 kN on tensions, 15% / 5 kN·m on bending), not an external standards ledger.

### LLM Wiki pages consulted
None directly consulted; domain knowledge is inside the repo at `digitalmodel/docs/domains/orcaflex/`. No relevant wiki pages were found for the c03 turret-FPSO case.

### Documents consulted
- `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` — authoritative roadmap. "turret-moored FPSO" listed under "Partial but high-value next validations". Priority 1 cluster is #1652 + #1788 which establish the fixture + snapshot discipline. #2454 is positioned as the first generic-track application of that discipline per the parent-comment guidance and the roadmap's statement that the "strongest open gap is proving OrcaFlex forward semantic fidelity on real native artifacts using committed fixtures and taxonomy-backed validation".
- `digitalmodel/docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md` — defines six mutually exclusive categories (C1 UI/Cosmetic, C2 Normalization, C3 Known Intentional Omission, C4 Reference Resolution, C5 Loadability, C6 Physics-Significant) and three equivalence-claim levels (L1 Loadable, L2 Behaviorally equivalent, L3 Semantically identical). Explicitly says "no model has been proven to achieve L3 across all sections"; the repo's practical target is L2.
- Related issue #1652 — parent of the fixture + snapshot testing discipline; deliverables: minimal `.sim` fixture, integration test, snapshot test, coverage measurement. Status OPEN. Its test pattern is the analog for #2454's regression surface. Note: its assertions hit a baseline JSON, not a modular-generator output.
- Related issue #1788 — child of #1652; builds the snapshot test without OrcFxAPI. Pattern: read committed metadata, render HTML via `OrcaFlexAnalysisReport`, normalize, diff against committed snapshot. Same limitation — not semantic proof.
- Related issue #1586 — solver-queue hardening (Priority 2 in the roadmap). Tangential to #2454 except that if #2454 ever needs to submit the generated FPSO case to `licensed-win-1` for a full OrcFxAPI statics run, that path rides on #1586's batch queue. Call-out only, not a dependency.
- Parent roadmap #1572 — domain capability roadmaps; #2454 rolls up through the canonical spec contract roadmap rather than directly under #1572.
- Owner comments on #2454 (three) — recommend fixture reuse of `c03_turret_moored_fpso`, list the grounded source-file set under `model_library/c03_turret_moored_fpso/`, and suggest fixture/test paths. Treated here as guidance to verify, not as already-landed artifacts.

### Gaps identified
- No test runs `ModularModelGenerator(<c03 spec.yml>)` today; the generator path from `c03_turret_moored_fpso/spec.yml` is unexercised in CI.
- No artifact compares generated native YAML against `monolithic/C03 Turret moored FPSO.yml` using taxonomy categories.
- No committed document states the equivalence-claim level (L1/L2/L3) for turret-moored FPSO, so the roadmap line "Partial but high-value next validations: turret-moored FPSO" cannot be promoted without a written claim boundary.
- `scripts/semantic_validate.py` output format for JSON emission (section-by-section, category-counted) has not been verified; must inspect before treating it as the diff artifact source-of-truth.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view`):
- `#2454` — OPEN — "feat(canonical-spec): validate flagship generic-track OrcaFlex mooring case via turret-moored FPSO semantic proof"
- `#1572` — OPEN — "Domain-specific capability roadmaps — OrcaWave/OrcaFlex, structural, hydrodynamics, pipeline"
- `#1652` — OPEN — "OrcaFlex reporting: integration test with real .sim fixture + HTML snapshot testing"
- `#1788` — OPEN — "OrcaFlex .sim snapshot testing: HTML report from minimal_test.sim fixture"
- `#1586` — OPEN — "Harden solver queue: batch submission, result watcher, auto post-processing"

**File existence** (verified 2026-04-23 via `git -C digitalmodel ls-files`):
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/c03_turret_moored_fpso/spec.yml`
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/c03_turret_moored_fpso/monolithic/C03 Turret moored FPSO.yml`
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/c03_turret_moored_fpso/modular/master.yml`
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/c03_turret_moored_fpso/modular/inputs/parameters.yml`
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/c03_turret_moored_fpso/modular/includes/01_general.yml`
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/c03_turret_moored_fpso/modular/includes/03_environment.yml`
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/c03_turret_moored_fpso/modular/includes/20_generic_objects.yml`
- EXISTS: `digitalmodel/docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md`
- EXISTS: `digitalmodel/scripts/semantic_validate.py`
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/generic_builder.py`
- EXISTS (do NOT recreate): `digitalmodel/tests/fixtures/reporting/fpso_turret.metadata.json`
- EXISTS (do NOT recreate): `digitalmodel/tests/fixtures/reporting/fpso_turret.report.snapshot.html`
- EXISTS (do NOT recreate): `digitalmodel/tests/solvers/orcaflex/reporting/test_fpso_fixture_integration.py`
- EXISTS (do NOT recreate): `digitalmodel/tests/solvers/orcaflex/reporting/test_fpso_fixture_snapshot.py`
- MISSING (new — this plan creates): `digitalmodel/tests/fixtures/reporting/fpso_turret.semantic_diff.json`
- MISSING (new — this plan creates): `digitalmodel/tests/solvers/orcaflex/modular_generator/test_c03_fpso_semantic_proof.py`
- MISSING (new — this plan creates): `digitalmodel/docs/domains/orcaflex/readiness/c03_turret_moored_fpso_semantic_proof.md`

**Gap proofs** (verified 2026-04-23 via `git -C digitalmodel grep -l c03_turret_moored_fpso -- src tests scripts`):
- Only four files reference `c03_turret_moored_fpso` by name:
  - `tests/fixtures/reporting/fpso_turret.metadata.json` (baseline only)
  - `tests/fixtures/reporting/fpso_turret.report.snapshot.html` (baseline only)
  - `tests/solvers/orcaflex/reporting/test_fpso_fixture_integration.py` (reporting baseline only)
  - `tests/solvers/orcaflex/test_spec_upgrader.py` (tangential — spec version upgrader)
- No file under `tests/solvers/orcaflex/modular_generator/` references `c03_turret_moored_fpso`, confirming the gap.
- No file under `scripts/` references `c03_turret_moored_fpso`, confirming no semantic-diff artifact exists yet.

**Line excerpts** from `SEMANTIC_DIFF_TAXONOMY.md` (verified 2026-04-23):
```
| L2 | **Behaviorally equivalent** | Statics/dynamics results match within benchmark tolerance (no C6 diffs) |
| L3 | **Semantically identical** | No differences except C1 (cosmetic) and C2 (normalization) |
Current repo status: Most validated models achieve L2. No model has been
proven to achieve L3 across all sections.
```
Plan's target equivalence-claim level for c03 turret-FPSO is **L2** (no C5, no C6 after classification). L3 is explicitly out-of-scope per repo-wide policy.

<!-- Distinct sources consulted: issue body (1), roadmap doc (2), SEMANTIC_DIFF_TAXONOMY.md (3), related issues #1652/#1788/#1586/#1572 (4), digitalmodel source tree + grep evidence (5). Minimum 3 satisfied. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-23-issue-2454-c03-fpso-semantic-proof.md` |
| Semantic-diff frozen baseline (new) | `digitalmodel/tests/fixtures/reporting/fpso_turret.semantic_diff.json` |
| Semantic-proof pytest (new) | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_c03_fpso_semantic_proof.py` |
| Readiness claim boundary doc (new) | `digitalmodel/docs/domains/orcaflex/readiness/c03_turret_moored_fpso_semantic_proof.md` |
| Roadmap update | `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` (promote "turret-moored FPSO" line conditionally) |
| Plan review — Claude | `scripts/review/results/2026-04-23-plan-2454-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-23-plan-2454-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-23-plan-2454-gemini.md` |
| Reused (no edits) | `digitalmodel/scripts/semantic_validate.py`, `generic_builder.py`, `ModularModelGenerator` entry point, `fixture_helpers.py` |
| Untouched (do NOT modify in this issue) | `digitalmodel/tests/fixtures/reporting/fpso_turret.metadata.json`, `.report.snapshot.html`, `test_fpso_fixture_integration.py`, `test_fpso_fixture_snapshot.py` |

---

## Deliverable

A committed taxonomy-classified semantic-diff artifact for `c03_turret_moored_fpso` plus a pytest that regenerates it and fails on any unclassified or C5/C6 difference, and a readiness doc that pins the equivalence-claim level (target: L2) for the turret-moored-FPSO family so the roadmap snapshot can be updated with a falsifiable claim.

---

## Pseudocode

```
# digitalmodel/tests/solvers/orcaflex/modular_generator/test_c03_fpso_semantic_proof.py

C03_ROOT = Path(digitalmodel/docs/domains/orcaflex/library/model_library/c03_turret_moored_fpso)
SPEC_YML         = C03_ROOT / "spec.yml"
MONOLITHIC_YML   = C03_ROOT / "monolithic/C03 Turret moored FPSO.yml"
FROZEN_DIFF_JSON = tests/fixtures/reporting/fpso_turret.semantic_diff.json

def _generate_native_from_spec(tmp_path):
    generator = ModularModelGenerator(SPEC_YML)
    generator.generate(tmp_path)
    return tmp_path / "master.yml"

def _run_semantic_validator(generated_master, monolithic):
    # Shell out to scripts/semantic_validate.py OR import its entry function.
    # Prefer the importable entry if one exists (check scripts/semantic_validate.py API).
    return diff_report  # dict: {section: {C1..C6: [property list], total, matches, verdict}}

def test_generator_runs_on_c03_spec_without_error(tmp_path):
    assert _generate_native_from_spec(tmp_path).exists()

def test_generated_yaml_is_yaml_strict_loadable():
    # L1 check — parses; no OrcFxAPI needed here.
    ...

@requires_orcaflex  # runs on licensed-win-1 only; skips on dev-primary
def test_generated_yaml_loads_in_orcfxapi(generated_master):
    OrcFxAPI.Model().LoadData(str(generated_master))  # must not raise

def test_semantic_diff_has_no_c5_diffs(diff_report):
    for section, counts in diff_report.items():
        assert counts["C5"] == [], f"C5 loadability diff in {section}: {counts['C5']}"

def test_semantic_diff_has_no_c6_diffs(diff_report):
    for section, counts in diff_report.items():
        assert counts["C6"] == [], f"C6 physics-significant diff in {section}: {counts['C6']}"

def test_c3_omissions_are_documented(diff_report):
    documented = _SKIP_GENERAL_KEYS | _SKIP_OBJECT_KEYS | _WIND_SPEED_DORMANT | GROUPS_POLICY
    for section, counts in diff_report.items():
        for prop in counts["C3"]:
            assert prop in documented, f"Undocumented omission: {section}.{prop}"

def test_c4_references_resolve(diff_report):
    for section, counts in diff_report.items():
        assert counts["C4"] == [], f"Unresolved reference in {section}: {counts['C4']}"

def test_frozen_diff_matches_current(diff_report):
    frozen = json.loads(FROZEN_DIFF_JSON.read_text())
    assert diff_report == frozen, "Diff drifted; update frozen baseline explicitly via intentional commit"
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/tests/fixtures/reporting/fpso_turret.semantic_diff.json` | Frozen per-section C1..C6 diff baseline; regenerated by the test and checked in |
| Create | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_c03_fpso_semantic_proof.py` | Pytest that runs the modular generator on c03 spec.yml, calls `scripts/semantic_validate.py`, and asserts no C5/C6 + documented C3 + resolved C4 |
| Create | `digitalmodel/docs/domains/orcaflex/readiness/c03_turret_moored_fpso_semantic_proof.md` | Claim-boundary doc pinning the equivalence level (L2 target), enumerating allowed diffs, and recording the OrcFxAPI version used for any L1/L2 checks |
| Modify | `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` | Single targeted edit: move the "turret-moored FPSO" bullet from "Partial but high-value next validations" to "Ready now" only if the classification yields zero C5/C6; otherwise leave the bullet with a footnote pointing to the open issues that block promotion |
| Update | `docs/plans/README.md` | Add one row for this plan file (index only; ≤ ~150 chars body per index convention) |

Explicitly **NOT** changing (forbidden per worker scope and per reviewer expectations):
- Any source/test file implementing the feature itself (the worker is planning-only; implementation belongs to a later execution phase)
- Any sibling issue artifact (#2455–#2458 and #1652/#1788/#1586 remain untouched)
- The four existing `fpso_turret.*` reporting-baseline artifacts — they are a different concern (HTML regression)
- The committed modular sources under `c03_turret_moored_fpso/modular/` — the test generates into `tmp_path`; nothing is overwritten in-tree

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_generator_runs_on_c03_spec_without_error` | ModularModelGenerator consumes c03 spec.yml end-to-end | `spec.yml` path | `master.yml` exists in `tmp_path` |
| `test_generated_yaml_is_yaml_strict_loadable` | Generated native YAML parses against strict YAML + Pydantic schema | generated `master.yml` | no exception; all include files resolve |
| `test_generated_yaml_loads_in_orcfxapi` (@requires_orcaflex) | L1 equivalence claim — `OrcFxAPI.Model().LoadData()` succeeds | generated `master.yml` | no OrcFxAPI exception; skipped when OrcFxAPI absent |
| `test_semantic_diff_has_no_c5_diffs` | No loadability hazards classified C5 | diff_report from `semantic_validate.py` | every section's C5 list is empty |
| `test_semantic_diff_has_no_c6_diffs` | L2 claim: no physics-significant diffs | diff_report | every section's C6 list is empty |
| `test_c3_omissions_are_documented` | Every C3 omission traces back to `_SKIP_GENERAL_KEYS` / `_SKIP_OBJECT_KEYS` / `_WIND_SPEED_DORMANT` / GroupsBuilder policy | diff_report | each C3 property ∈ one of the documented sets |
| `test_c4_references_resolve` | All object-name references in the generated model resolve against the generated registry | diff_report | every section's C4 list is empty |
| `test_frozen_diff_matches_current` | Regression guard: C1/C2 diffs are frozen; drift is a deliberate review event | `fpso_turret.semantic_diff.json` vs live run | equal dicts; mismatch is a test failure with explicit diff |

Decision on OrcFxAPI-gated tests: `@requires_orcaflex` is defined in the existing `test_modular_vs_monolithic.py` pattern. Reuse the same skipif shape so dev-primary CI passes without OrcFxAPI, and licensed-win-1 CI exercises the L1 load check. No full statics run is in scope — that is L2 behavioral-equivalence territory and can be layered on later without changing the contract.

---

## Acceptance Criteria

- [ ] All new tests pass on dev-primary: `uv run pytest digitalmodel/tests/solvers/orcaflex/modular_generator/test_c03_fpso_semantic_proof.py -v` (OrcFxAPI-gated tests skip with a clear reason string, not error)
- [ ] All new tests pass on licensed-win-1 including the `@requires_orcaflex` L1 load test
- [ ] No existing regression: `uv run pytest digitalmodel/tests/solvers/orcaflex/ -q` (or the project's standard gate) still passes; the four existing `fpso_turret.*` reporting tests and all modular-generator tests remain green
- [ ] `scripts/semantic_validate.py` output for c03 reports zero C5 and zero C6 diffs across all sections; every C3 is traceable to a documented skip set; every C4 resolves
- [ ] Frozen diff artifact `fpso_turret.semantic_diff.json` committed with explicit schema_version and provenance (OrcFxAPI version, generator version, semantic_validate version if tagged)
- [ ] Readiness doc `c03_turret_moored_fpso_semantic_proof.md` committed with claim level (L2), allowed-diff justification per C1/C2/C3 bucket, and the OrcFxAPI load-test machine + version
- [ ] Roadmap snapshot line reconciled: if zero C5/C6, move "turret-moored FPSO" to "Ready now"; if any C5/C6 is found, leave in "Partial" with a cross-ref to the blocking property families
- [ ] `docs/plans/README.md` row added/updated for this plan
- [ ] Review artifacts posted to `scripts/review/results/2026-04-23-plan-2454-<agent>.md` for at least Claude and one cross-provider (Codex or Gemini), per `.claude/skills/coordination/issue-planning-mode/SKILL.md`
- [ ] GitHub issue #2454 moved to `status:plan-review` only after adversarial review converges to no MAJOR findings

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING — review artifacts will be populated under `scripts/review/results/` before surfacing for user approval.

Revisions made based on review:
- (none yet)

---

## Risks and Open Questions

- **Risk — generator compatibility with c03 spec.yml:** the plan assumes `ModularModelGenerator(c03/spec.yml).generate(tmp_path)` runs without error on today's generic-track builder. The spec.yml contains a large `environment.raw_properties` bag and a generic object surface; if the generator raises or emits a non-loadable native YAML, the plan must fall back to filing a child issue for the unsupported surface and downgrading the claim to L1-partial. **Verification in execution:** smoke-run the generator on the committed spec.yml before authoring assertions. If it fails, the execution phase produces a sub-plan rather than asserting false equivalence.
- **Risk — scripts/semantic_validate.py output shape:** the taxonomy doc describes the intended per-section category-counted format but does not guarantee a stable JSON schema. **Mitigation:** during execution, read `scripts/semantic_validate.py` end-to-end before wiring the pytest; if the script emits only human-readable text, add a thin `--json` emitter to the script or implement a wrapper in the test module that parses the text block. The wrapper path is the safer default because modifying `semantic_validate.py` affects every other structure family (cross-phase risk).
- **Risk — OrcFxAPI version drift on licensed-win-1:** the L1 load test's pass/fail depends on the OrcFxAPI version. Pin the version in the readiness doc provenance block so future upgrades are visible in the diff.
- **Risk — past-tense artifact drift (feedback_plan_past_tense_artifact_claims.md):** the issue comments describe fixture artifacts as both "recommended new paths" and as landed work. This plan treats the four already-committed `fpso_turret.*` artifacts as pre-existing reporting-baseline scope and does NOT propose re-creating them; only the three new semantic-proof artifacts are new work.
- **Risk — worker scope creep into sibling issues:** #2455–#2458 are adjacent family-validation items. This plan must stay bounded to c03 turret-moored FPSO and must not touch sibling-issue artifacts, even when the pattern generalizes.
- **Open — L2 behavioral equivalence vs L1 loadability:** the plan targets L2 (no C5/C6 diffs). A full statics/dynamics comparison between generated-native and monolithic (analogous to `TestModularVsMonolithicComparison` in `test_modular_vs_monolithic.py`) is NOT in scope because it requires a pre-computed `.sim` for the monolithic C03 on licensed-win-1 and a long-running statics job. Flag this to the user: should a follow-up issue be opened to add the statics comparison once licensed-win-1 capacity permits?
- **Open — roadmap promotion threshold:** is "zero C5 and zero C6" sufficient to promote turret-moored FPSO to "Ready now", or does the user require the optional L2 statics comparison first? Default assumption in this plan: zero C5/C6 + documented C3 + resolved C4 is sufficient for "Ready now" under the L2 repo convention.

---

## Complexity: T2

**T2** — three new files in `digitalmodel/`, one surgical roadmap edit, one README index row, one frozen baseline JSON. Reuses existing generator + taxonomy infrastructure without modifying them (except possibly adding a `--json` flag to `semantic_validate.py`, which is scoped as a fallback behind a wrapper-first strategy). No new physics, no new generator builders. The engineering judgement load is in the claim-boundary doc and the C3 documentation audit, not in code volume.
