# Plan for #2454: Validate flagship generic-track OrcaFlex mooring case via turret-moored FPSO semantic proof

> **Status:** draft (iter-2 after MAJOR review)
> **Complexity:** T2
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2454
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2454-claude.md | scripts/review/results/2026-04-23-plan-2454-claude-iter-2.md

---

## Scope anchor — what this plan claims and what it explicitly does NOT claim

- **In scope (claim):** static-YAML semantic equivalence of `c03_turret_moored_fpso` — the generated modular output (`spec.yml → ModularModelGenerator → master.yml + includes/`) contains no `Significance.SIGNIFICANT` or `Significance.TYPE_MISMATCH` diffs against the monolithic YAML, every `Significance.MISSING` property is traceable to a documented generator skip-list, and (on `licensed-win-1` only) the generated YAML loads in OrcFxAPI without error. This is the taxonomy doc's **L1 (Loadable) + static-YAML-diff equivalence**. It is *not* L2.
- **Out of scope (explicit non-claim):** L2 behavioral equivalence — running statics/dynamics on both models and comparing tension/bending-moment results within benchmark tolerance. That requires a long-running `CalculateStatics()` on `licensed-win-1` plus a committed pre-computed `.sim` baseline for `C03 Turret moored FPSO.yml`. A follow-up issue will be filed at execution time to extend the proof to L2 once L1 is green.
- **Roadmap promotion rule:** if static-diff evidence is clean (conditions above), move the `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` "turret-moored FPSO" bullet from "Partial but high-value next validations" to a NEW "Ready for L1 / static-YAML-diff" bucket (to be added to the roadmap), not to "Ready now". Only L2-validated items belong in "Ready now".

---

## Resource Intelligence Summary

### Existing repo code
- Found: `digitalmodel/scripts/semantic_validate.py` — real API is `load_monolithic(path: Path) -> dict`, `load_modular(modular_dir: Path) -> dict`, `compare(monolithic_data, modular_data) -> ValidationResult`, `to_json(ValidationResult) -> dict`. Its `--json` flag already exists (line 1951). The output shape per section is `{type, total_mono, total_mod, matches, diffs: [PropertyDiff], missing_in_mod, extra_in_mod, objects?, missing_objects?, extra_objects?, categories?}`. Each `PropertyDiff` carries a `significance` field drawn from the `Significance` enum at line 101: `match | cosmetic | minor | significant | type_mismatch | missing | extra`. The tool also owns the authoritative `ALLOWED_DIFF_PROPS` (line 117) which is the concrete C1 set.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/__init__.py` exposes `ModularModelGenerator(spec_file)` and `.generate(output_dir)`. `output_dir` ends up containing `master.yml`, `includes/*.yml`, `inputs/*.yml`. `load_modular()` takes the directory (not the master file).
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/generic_builder.py` — owns module-level `_SKIP_GENERAL_KEYS` (line 115, 34 keys) and `_SKIP_OBJECT_KEYS` (line 160, 2 keys).
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/environment_builder.py:160` — `EnvironmentBuilder._WIND_SPEED_DORMANT` is a **class attribute** (not module-level). Must be accessed as `EnvironmentBuilder._WIND_SPEED_DORMANT`.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/groups_builder.py:27-29` — `GroupsBuilder.should_generate()` returns `spec.is_pipeline() or spec.is_riser()`. For a `structure: generic, operation: generic` spec, this returns `False`, so the Groups section is intentionally suppressed in the modular output. There is NO symbol named `GROUPS_POLICY`; the policy is a predicate on the spec.
- Found: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_modular_vs_monolithic.py:27-37` — defines the `requires_orcaflex` skipif decorator as a local three-line block (`try: import OrcFxAPI; ORCAFLEX_AVAILABLE = True; except: False` + `pytest.mark.skipif`). There is no shared conftest; the new test module must copy this block verbatim or the 2454 executor must extract it into a shared conftest first (scope-decision at execution time).
- Found: `digitalmodel/tests/fixtures/reporting/fpso_turret.metadata.json`, `.report.snapshot.html`, `tests/solvers/orcaflex/reporting/test_fpso_fixture_integration.py`, `test_fpso_fixture_snapshot.py` — already committed, reporting-baseline regression guards, NOT semantic proof. Do NOT recreate.
- Gap: no current test runs `ModularModelGenerator` on `c03 spec.yml`; no committed diff artifact for c03; no readiness doc for turret-moored FPSO.

### Standards
Not standards-driven. Diff significance thresholds come from `semantic_validate.py` (numeric tolerance logic, property-name skip-lists, `ALLOWED_DIFF_PROPS`).

### LLM Wiki pages consulted
None. Domain knowledge is repo-internal.

### Documents consulted
- `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` — turret-moored FPSO listed under "Partial but high-value next validations" (line 116). Roadmap separates Priority 1 (`#1652 + #1788` — prove forward native fidelity) from subsequent priorities.
- `digitalmodel/docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md` — defines C1..C6 categories (line 25 table) and L1/L2/L3 claim levels (line 273). L2 explicitly requires statics/dynamics results matching (line 275). L3 not achieved repo-wide (line 279). The doc's §3 table (line 256) maps `Significance` mechanism → possible C1..C6 categories as a many-to-many relation requiring judgement — not a 1:1 tool output.
- Related issues #1652, #1788, #1586, #1572 — as previously verified; all OPEN, roles per the roadmap bullet structure.
- Owner comments on #2454 — suggested file paths; treated as guidance, not authoritative landed work.

### Gaps identified
- No test runs the modular generator on `c03_turret_moored_fpso/spec.yml`.
- No artifact classifies the c03 semantic diff.
- No readiness/claim-boundary document for turret-moored FPSO.
- The C1..C6 taxonomy is a human overlay on top of `Significance`; there is no existing importable Python module that maps `(Significance, key) → C1..C6`. This plan treats the classifier as **optional tooling**; the core assertions use `Significance` values directly to avoid introducing a new classifier module in this deliverable (keeps complexity at T2).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view`):
- `#2454` — OPEN — "feat(canonical-spec): validate flagship generic-track OrcaFlex mooring case via turret-moored FPSO semantic proof"
- `#1572` — OPEN; `#1652` — OPEN; `#1788` — OPEN; `#1586` — OPEN.

**File existence** (verified 2026-04-23 via `git -C digitalmodel ls-files`):
- EXISTS: `digitalmodel/docs/domains/orcaflex/library/model_library/c03_turret_moored_fpso/spec.yml`, `monolithic/C03 Turret moored FPSO.yml`, `modular/master.yml`, `modular/inputs/parameters.yml`, `modular/includes/01_general.yml`, `modular/includes/03_environment.yml`, `modular/includes/20_generic_objects.yml`.
- EXISTS: `digitalmodel/docs/domains/orcaflex/SEMANTIC_DIFF_TAXONOMY.md`, `digitalmodel/scripts/semantic_validate.py`, `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/generic_builder.py`, `.../environment_builder.py`, `.../groups_builder.py`.
- EXISTS (reporting-baseline only; do NOT recreate or modify): `digitalmodel/tests/fixtures/reporting/fpso_turret.metadata.json`, `.report.snapshot.html`, `tests/solvers/orcaflex/reporting/test_fpso_fixture_integration.py`, `tests/solvers/orcaflex/reporting/test_fpso_fixture_snapshot.py`.
- MISSING (new — this plan's execution phase creates): `digitalmodel/tests/fixtures/reporting/fpso_turret.semantic_diff.json`, `digitalmodel/tests/solvers/orcaflex/modular_generator/test_c03_fpso_semantic_proof.py`, `digitalmodel/docs/domains/orcaflex/readiness/c03_turret_moored_fpso_semantic_proof.md`.

**Tool-schema evidence** (verified 2026-04-23 via `sed -n Np semantic_validate.py`):
- Line 101: `class Significance: MATCH = "match"; COSMETIC = "cosmetic"; MINOR = "minor"; SIGNIFICANT = "significant"; TYPE_MISMATCH = "type_mismatch"; MISSING = "missing"; EXTRA = "extra"`.
- Line 117-178: `ALLOWED_DIFF_PROPS: set[str] = {...}` — 50+ canonical cosmetic/view/dormant property names; this is the concrete C1 set the tool already tracks.
- Line 304: `def load_modular(modular_dir: Path) -> dict:` — takes a **directory**, iterates `modular_dir/"includes"/*.yml` (falls back to `modular_dir/*.yml`). Does NOT accept a single master.yml path.
- Line 1206-1258: `to_json(ValidationResult) -> dict` — per-section shape includes `diffs`, `missing_in_mod`, `extra_in_mod`, and for list sections `missing_objects`, `extra_objects`, `objects`. Object references that don't resolve surface as `missing_objects` / `extra_objects`.
- Line 1951: `--json` flag exists.

**Builder-symbol evidence** (verified 2026-04-23 via `grep -n`):
- `_SKIP_GENERAL_KEYS` at `generic_builder.py:115` (module level, set).
- `_SKIP_OBJECT_KEYS` at `generic_builder.py:160` (module level, set).
- `_WIND_SPEED_DORMANT` at `environment_builder.py:160` (class attribute of `EnvironmentBuilder`).
- `GroupsBuilder.should_generate()` at `groups_builder.py:27-29` — returns True only for pipeline/riser. No `GROUPS_POLICY` symbol exists.

<!-- Distinct sources consulted: issue body (1), roadmap (2), SEMANTIC_DIFF_TAXONOMY.md (3), semantic_validate.py source (4), builder source files (5), related issues (6). Well above the minimum 3. -->

---

## Artifact Map

| Artifact | Path | Phase |
|---|---|---|
| This plan | `docs/plans/2026-04-23-issue-2454-c03-fpso-semantic-proof.md` | planning |
| Plan review — Claude iter-1 | `scripts/review/results/2026-04-23-plan-2454-claude.md` | planning |
| Plan review — Claude iter-2 | `scripts/review/results/2026-04-23-plan-2454-claude-iter-2.md` | planning |
| Semantic-diff frozen baseline | `digitalmodel/tests/fixtures/reporting/fpso_turret.semantic_diff.json` | execution |
| Semantic-proof pytest | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_c03_fpso_semantic_proof.py` | execution |
| Readiness claim-boundary doc | `digitalmodel/docs/domains/orcaflex/readiness/c03_turret_moored_fpso_semantic_proof.md` | execution |
| Roadmap update | `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` | execution |
| Reused (no edits) | `digitalmodel/scripts/semantic_validate.py`, `ModularModelGenerator`, `generic_builder.py`, `environment_builder.py`, `groups_builder.py` | execution |
| Untouched | The four existing `fpso_turret.*` reporting-baseline files; all sibling-issue (#2455-#2458) artifacts | — |

The planning-agent write-set is limited to rows marked `planning` above. Rows marked `execution` describe the downstream work that will happen only after `status:plan-approved`.

---

## Deliverable (execution phase)

A committed frozen JSON diff artifact for `c03_turret_moored_fpso`, a pytest that regenerates and compares against it, and a readiness doc that pins the equivalence claim to **L1 (loadability) + static-YAML-diff equivalence** — not L2. A conditional roadmap edit that introduces a new "Ready for L1 / static-YAML-diff" bucket and moves the turret-moored FPSO bullet into it when the assertions pass.

---

## Pseudocode (grounded in actual `semantic_validate.py` schema)

```python
# digitalmodel/tests/solvers/orcaflex/modular_generator/test_c03_fpso_semantic_proof.py

from pathlib import Path
import json, sys
import pytest

# Copy skipif block from test_modular_vs_monolithic.py:27-37 (no shared conftest export)
try:
    import OrcFxAPI  # noqa: F401
    ORCAFLEX_AVAILABLE = True
except ImportError:
    ORCAFLEX_AVAILABLE = False
requires_orcaflex = pytest.mark.skipif(not ORCAFLEX_AVAILABLE, reason="OrcFxAPI not available")

# Add digitalmodel/scripts to path so we can import semantic_validate
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from semantic_validate import (
    Significance,
    ALLOWED_DIFF_PROPS,
    load_monolithic,
    load_modular,
    compare,          # returns ValidationResult
    to_json,          # ValidationResult -> dict
)
from digitalmodel.solvers.orcaflex.modular_generator import ModularModelGenerator
from digitalmodel.solvers.orcaflex.modular_generator.builders.generic_builder import (
    _SKIP_GENERAL_KEYS, _SKIP_OBJECT_KEYS,
)
from digitalmodel.solvers.orcaflex.modular_generator.builders.environment_builder import (
    EnvironmentBuilder,
)
from digitalmodel.solvers.orcaflex.modular_generator.builders.groups_builder import (
    GroupsBuilder,
)

C03_ROOT = Path("digitalmodel/docs/domains/orcaflex/library/model_library/c03_turret_moored_fpso")
SPEC_YML          = C03_ROOT / "spec.yml"
MONOLITHIC_YML    = C03_ROOT / "monolithic" / "C03 Turret moored FPSO.yml"
FROZEN_DIFF_JSON  = Path("digitalmodel/tests/fixtures/reporting/fpso_turret.semantic_diff.json")

DOCUMENTED_OMISSION_KEYS = (
    set(_SKIP_GENERAL_KEYS)
    | set(_SKIP_OBJECT_KEYS)
    | set(EnvironmentBuilder._WIND_SPEED_DORMANT)  # class attribute, not module-level
    # NOTE: Groups-section suppression is a structural policy (GroupsBuilder.should_generate()
    # returns False for generic specs). When the `Groups` section appears in missing_objects
    # at the section level, classify at assertion time by calling GroupsBuilder.should_generate(spec).
)

@pytest.fixture(scope="module")
def generated_modular(tmp_path_factory):
    out = tmp_path_factory.mktemp("c03_modular")
    ModularModelGenerator(SPEC_YML).generate(out)
    return out  # directory, per load_modular contract

@pytest.fixture(scope="module")
def diff_report(generated_modular):
    mono_data = load_monolithic(MONOLITHIC_YML)
    mod_data  = load_modular(generated_modular)  # directory, not master.yml
    result = compare(mono_data, mod_data)
    return to_json(result)

def test_generator_runs_on_c03_spec_without_error(generated_modular):
    assert (generated_modular / "master.yml").exists()
    assert (generated_modular / "includes").exists()

def test_generated_modular_is_yaml_strict_loadable(generated_modular):
    import yaml
    for p in (generated_modular / "includes").glob("*.yml"):
        yaml.safe_load(p.read_text(encoding="utf-8"))  # must not raise
    yaml.safe_load((generated_modular / "master.yml").read_text(encoding="utf-8"))

@requires_orcaflex
def test_generated_modular_loads_in_orcfxapi(generated_modular):
    model = OrcFxAPI.Model()
    model.LoadData(str(generated_modular / "master.yml"))  # must not raise — L1 claim

def test_no_significant_diffs(diff_report):
    offenders = []
    for sec_name, sec in diff_report["sections"].items():
        for d in sec.get("diffs", []):
            if d["significance"] == Significance.SIGNIFICANT:
                offenders.append(f"{sec_name}.{d['key']}: mono={d.get('mono')} vs mod={d.get('mod')}")
    assert not offenders, "SIGNIFICANT diffs detected:\n" + "\n".join(offenders)

def test_no_type_mismatch_diffs(diff_report):
    offenders = []
    for sec_name, sec in diff_report["sections"].items():
        for d in sec.get("diffs", []):
            if d["significance"] == Significance.TYPE_MISMATCH:
                offenders.append(f"{sec_name}.{d['key']}")
    assert not offenders, "TYPE_MISMATCH diffs:\n" + "\n".join(offenders)

def test_missing_properties_are_documented_omissions(diff_report):
    # Significance.MISSING ≈ taxonomy C3 if the key is in a documented skip-list, otherwise
    # either C1 (if in ALLOWED_DIFF_PROPS) or a real gap that must fail.
    undocumented = []
    for sec_name, sec in diff_report["sections"].items():
        for d in sec.get("missing_in_mod", []):
            key = d["key"]
            if key in ALLOWED_DIFF_PROPS:      # C1 equivalence — cosmetic
                continue
            if key in DOCUMENTED_OMISSION_KEYS:  # C3 equivalence — deliberate skip
                continue
            undocumented.append(f"{sec_name}.{key}")
    assert not undocumented, "Undocumented omissions:\n" + "\n".join(undocumented)

def test_object_references_resolve(diff_report):
    # C4 equivalence — no missing/extra named objects in list sections
    for sec_name, sec in diff_report["sections"].items():
        if sec.get("type") == "list":
            assert sec.get("missing_objects", []) == [], f"{sec_name} missing objects: {sec['missing_objects']}"
            assert sec.get("extra_objects", []) == [],   f"{sec_name} extra objects: {sec['extra_objects']}"

def test_groups_section_absence_justified_for_generic_spec():
    # When `Groups` shows up as missing at section level, it is C3 iff the spec is generic.
    # Proof: GroupsBuilder.should_generate(spec) returns False for generic specs.
    spec = ModularModelGenerator(SPEC_YML).spec  # attribute name to confirm in execution
    assert not GroupsBuilder(spec).should_generate(), "spec is not generic — Groups omission is NOT C3"

def test_frozen_diff_matches_current(diff_report):
    # First-baseline validation: the committed JSON is validated by the adversarial plan review
    # + human inspection of the initial diff at execution time. This test only guards against
    # subsequent drift.
    frozen = json.loads(FROZEN_DIFF_JSON.read_text())
    assert diff_report == frozen, "Diff drifted vs. frozen baseline — inspect and, if intentional, regenerate baseline"
```

Import paths not yet verified at runtime: `from digitalmodel.solvers.orcaflex.modular_generator import ModularModelGenerator` (confirmed via ls-files); `ModularModelGenerator(SPEC_YML).spec` attribute name (**MUST be confirmed in execution phase** before wiring `test_groups_section_absence_justified_for_generic_spec`). If the attribute is named differently (e.g. `._spec`, `.model_spec`), adjust at execution time; no plan change required.

---

## Files to Change

| Phase | Action | Path | Reason |
|---|---|---|---|
| planning | Create | `docs/plans/2026-04-23-issue-2454-c03-fpso-semantic-proof.md` | This plan file |
| planning | Create | `scripts/review/results/2026-04-23-plan-2454-claude.md` | Iter-1 adversarial review (MAJOR) |
| planning | Create | `scripts/review/results/2026-04-23-plan-2454-claude-iter-2.md` | Iter-2 adversarial review after tightening |
| planning | Update | `docs/plans/README.md` | Single index row for this plan |
| execution | Create | `digitalmodel/tests/fixtures/reporting/fpso_turret.semantic_diff.json` | Frozen per-section `to_json()` baseline with schema_version, tool version, OrcFxAPI version, generator version |
| execution | Create | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_c03_fpso_semantic_proof.py` | Pytest per pseudocode |
| execution | Create | `digitalmodel/docs/domains/orcaflex/readiness/c03_turret_moored_fpso_semantic_proof.md` | Claim-boundary doc; target claim = L1 + static-YAML-diff equivalence |
| execution | Modify | `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` | (a) Add new "Ready for L1 / static-YAML-diff" subsection under "Structure readiness snapshot" around current line 107-121; (b) move the existing "- turret-moored FPSO" bullet from the "Partial but high-value next validations" list to that new subsection, with a one-line footnote "L2 behavioral proof pending — see follow-up issue" |

Explicitly **NOT** in the planning-agent write set:
- Any `digitalmodel/` source or test file
- `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md`
- Sibling-issue artifacts (#2455-#2458, #1652, #1788, #1586)
- The four existing `fpso_turret.*` reporting-baseline artifacts

---

## TDD Test List (execution phase)

| Test name | What it verifies | Pass condition |
|---|---|---|
| `test_generator_runs_on_c03_spec_without_error` | `ModularModelGenerator(spec).generate(tmp)` produces `master.yml` + `includes/` | `master.yml` and `includes/` exist in tmp |
| `test_generated_modular_is_yaml_strict_loadable` | All include files parse via `yaml.safe_load` | No exception |
| `test_generated_modular_loads_in_orcfxapi` (`@requires_orcaflex`) | L1 claim: OrcFxAPI `.LoadData(master.yml)` succeeds | No exception (skips on dev-primary) |
| `test_no_significant_diffs` | No `Significance.SIGNIFICANT` diffs anywhere in `to_json()` sections | `offenders == []` |
| `test_no_type_mismatch_diffs` | No `Significance.TYPE_MISMATCH` diffs | `offenders == []` |
| `test_missing_properties_are_documented_omissions` | Every `missing_in_mod` key is in `ALLOWED_DIFF_PROPS` (C1) OR `DOCUMENTED_OMISSION_KEYS` (C3) | `undocumented == []` |
| `test_object_references_resolve` | List-section `missing_objects` and `extra_objects` are empty — approximation of C4 | Empty lists |
| `test_groups_section_absence_justified_for_generic_spec` | If Groups section absent, justified because `GroupsBuilder.should_generate()` returns False for generic spec | Assertion holds |
| `test_frozen_diff_matches_current` | `to_json()` output equals committed frozen baseline | Equal dicts (drift detector) |

Taxonomy mapping in the readiness doc (authored at execution time), human-readable:
- `Significance.COSMETIC` or `key in ALLOWED_DIFF_PROPS` → C1
- `Significance.MINOR` on bool↔Yes/No, int↔float, whitespace → C2
- `Significance.MISSING` with `key in DOCUMENTED_OMISSION_KEYS` or Groups-section-for-generic → C3
- List-section `missing_objects` / `extra_objects` (non-empty) → C4
- Any `Significance` that causes `OrcFxAPI.LoadData()` to raise → C5 (L1 test would catch)
- `Significance.SIGNIFICANT` or `Significance.TYPE_MISMATCH` on physics property families → C6

---

## Acceptance Criteria

- [ ] On dev-primary: `uv run pytest digitalmodel/tests/solvers/orcaflex/modular_generator/test_c03_fpso_semantic_proof.py -v` returns green; `test_generated_modular_loads_in_orcfxapi` reports SKIPPED with reason "OrcFxAPI not available".
- [ ] On licensed-win-1: `uv run pytest digitalmodel/tests/solvers/orcaflex/modular_generator/test_c03_fpso_semantic_proof.py -v` returns green including the OrcFxAPI load test.
- [ ] No regression: `uv run pytest digitalmodel/tests/solvers/orcaflex/modular_generator/ digitalmodel/tests/solvers/orcaflex/reporting/ -q` passes (narrowed from the full `tests/solvers/orcaflex/` tree to exclude tests that require offline `.sim` fixtures not available in this branch).
- [ ] `fpso_turret.semantic_diff.json` committed with explicit fields: `schema_version`, `semantic_validate_version` (git SHA of `scripts/semantic_validate.py`), `generator_version` (git SHA of modular_generator), `orcaflex_version` (string, or `"n/a - dev-primary baseline"`), `generated_on_machine`, `monolithic_source_path`, plus the full `to_json()` output.
- [ ] Readiness doc committed with explicit claim: "**L1 (loadability) + static-YAML-diff equivalence**" in its first-paragraph claim statement; explicit non-claim paragraph for L2; table mapping each observed `Significance` to its taxonomy category with justification.
- [ ] Roadmap reconciled: "turret-moored FPSO" bullet moved from "Partial but high-value next validations" to a new "Ready for L1 / static-YAML-diff" subsection, with footnote pointing to a new follow-up issue for L2 behavioral proof.
- [ ] A follow-up GitHub issue filed at execution time: "Add L2 behavioral proof (statics/dynamics) for c03_turret_moored_fpso canonical spec" — referenced from the readiness doc and roadmap footnote.
- [ ] `docs/plans/README.md` has one row for this plan.
- [ ] Review artifacts for at least Claude iter-1 and Claude iter-2 posted to `scripts/review/results/`. Cross-provider (Codex or Gemini) review is a nice-to-have but not blocking because this worker is permission-gated from dispatching cross-review.sh; see `feedback_permission_gate_blocks_cross_review.md`.
- [ ] `status:plan-review` applied only after the latest review artifact returns no MAJOR findings.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (iter-1, cold context) | MAJOR | M1 C1..C6 buckets are a human overlay, not tool output; M2 `load_modular` expects a directory not a file; M3 L2 claim unsubstantiated by L1 tests; M4 `GROUPS_POLICY` symbol fabricated. |
| Claude (iter-2, cold context) | PENDING | — |
| Codex | N/A | Planning-only worker permission-gated from dispatching `scripts/review/cross-review.sh`; Codex review deferred to the execution phase or to a later cross-review wave. |
| Gemini | N/A | Same gating rationale as Codex. |

**Overall result:** iter-2 pending. Revisions made since iter-1:
- Rewrote §Pseudocode against the real `semantic_validate.py` schema: `Significance` enum + `ALLOWED_DIFF_PROPS` + `load_modular(directory)`. No more `counts["C1"]..["C6"]` assertions.
- Demoted the claim from "L2" to "**L1 + static-YAML-diff equivalence**" — aligned with the taxonomy doc's own L2 definition (requires dynamics). Added explicit non-claim paragraph; introduced a new "Ready for L1 / static-YAML-diff" roadmap bucket instead of promoting to "Ready now".
- Replaced the fabricated `GROUPS_POLICY` with a structural test calling `GroupsBuilder(spec).should_generate()` and a documented omission set that uses the real importable symbols (`_SKIP_GENERAL_KEYS`, `_SKIP_OBJECT_KEYS`, `EnvironmentBuilder._WIND_SPEED_DORMANT`).
- Added a "Scope anchor" section at the top stating the claim and non-claim explicitly.
- Phase-tagged the "Files to Change" table (planning vs execution) to resolve the self-contradiction between "worker is planning-only" and the deliverables list.
- Narrowed the regression-test acceptance criterion to `tests/solvers/orcaflex/modular_generator/ + tests/solvers/orcaflex/reporting/` instead of the full tree.
- Removed the out-of-date "add `--json` to semantic_validate" mitigation (the flag exists at line 1951).
- Pinned the `@requires_orcaflex` shape to a literal copy from `test_modular_vs_monolithic.py:27-37`.
- Added the first-baseline-validation framing under Risks.
- Committed to filing a follow-up issue for L2 so the scope boundary is tracked, not hand-waved.

---

## Risks and Open Questions

- **Risk — generator compatibility:** `ModularModelGenerator(c03/spec.yml).generate(tmp)` is assumed to succeed. If it raises on the large `environment.raw_properties` bag or on generic-track object pass-through, the execution phase files a child issue and downgrades this plan's claim to "partial L0 — generator does not yet consume c03". Verification sequence at execution: smoke-generate first; only after success do we author assertions.
- **Risk — Significance vs C1..C6 mapping precision:** the assertion set uses `Significance.SIGNIFICANT` and `Significance.TYPE_MISMATCH` as proxies for C6. A future property family could emit `Significance.MINOR` on a physics-relevant property and escape this gate. Mitigation: the readiness doc explicitly lists property families that must NEVER appear even as MINOR (water depth, wave height, wave period, current speed, line length, segment length, EA, EI, OD, ID, mass-per-length) and the pytest includes a narrow "forbidden MINOR" whitelist check for those families. If this check adds material complexity at execution, it is documented as a sub-issue rather than dropped.
- **Risk — first-baseline circularity:** `test_frozen_diff_matches_current` on the very first commit only proves determinism. The first baseline is validated by (a) this adversarial plan review, (b) human inspection of the JSON before commit in the execution phase, (c) the other assertions (no SIGNIFICANT, no TYPE_MISMATCH, all missing documented, references resolve) which independently catch real defects. The readiness doc captures this reasoning so the frozen artifact cannot become a rubber-stamp baseline in future drift cycles.
- **Risk — OrcFxAPI version drift on licensed-win-1:** L1 test outcome depends on OrcFxAPI version. The frozen baseline records the OrcFxAPI version present at generation time; any upgrade that changes the load behaviour produces a visible diff.
- **Risk — `.spec` attribute name on `ModularModelGenerator`:** pseudocode's `test_groups_section_absence_justified_for_generic_spec` calls `ModularModelGenerator(SPEC).spec`. The attribute name is unverified in this planning pass. Executor adjusts to the real name (likely `_spec` or `spec`) in the execution phase; no plan revision required.
- **Risk — past-tense artifact drift:** issue comments describe fixture artifacts in both recommendation and landed-artifact voice. This plan explicitly treats the four committed `fpso_turret.*` reporting files as pre-existing scope and scopes new work to the three new semantic-proof artifacts.
- **Risk — worker scope creep into #2455-#2458:** siblings apply the same pattern to jumper/riser/multibody/ship cases. Execution must stay bounded to c03; the pattern generalisation is a later-wave concern.
- **Open — L2 follow-up sequencing:** the follow-up L2 issue will require a committed `.sim` baseline of `C03 Turret moored FPSO.yml` after `CalculateStatics()` on licensed-win-1. That `.sim` could be large; the follow-up should settle on either committing a minimal-mesh statics `.sim` or generating on every CI run via `@requires_orcaflex` fixture. This decision belongs in the L2 issue's plan, not here.
- **Open — roadmap subsection name:** plan proposes a new "Ready for L1 / static-YAML-diff" bucket. Alternative names: "L1-validated (loadable + static equivalent)", "Static-proof ready". Executor may pick the most consistent name; no plan change required.

---

## Complexity: T2

**T2** — three new digitalmodel files (one JSON, one pytest, one markdown), one surgical roadmap edit, one README row. No new Python modules are created; the test imports existing validator + generator symbols. No new physics, no new generator work, no new C1..C6 classifier module. The engineering judgement load is in the readiness doc's claim boundary and in the `DOCUMENTED_OMISSION_KEYS` construction. Execution effort is scoped by the narrow assertion set and the "L1 + static-diff equivalence" claim — L2 behavioral proof is a separate follow-up issue.
