# Adversarial Review — Plan #501 (OrcaWave QTF + field points + irregular-freq method)

**Reviewer:** Claude (adversarial, defect-hunter)
**Plan:** `docs/plans/2026-04-24-issue-501-orcawave-qtf-fieldpoints-irregfreq.md`
**Intel:** `/tmp/orca-batch-2026-04-24/intel-501.md`
**Issue JSON:** `/tmp/orca-batch-2026-04-24/issue-501.json`
**Date:** 2026-04-24

---

## Verdict

**MAJOR** — re-draft required before implementation.

Three load-bearing technical defects (D1, D2, D4) invalidate correctness claims or back-compat claims on the emission paths. Two contradiction-class defects (D3, D5) break internal consistency of the back-compat strategy. The plan is structurally solid and scope-correct, so the re-draft is targeted, not a rewrite — but the defects below would cause silent test passes with incorrect emissions, exactly the failure mode the byte-identity gate exists to catch yet cannot detect when the gate itself is mis-specified.

---

## Full Defect Checklist (required per reviewer contract)

| # | Class of check | Result |
|---|---|---|
| 1 | Greenfield vs. brownfield — did plan acknowledge 90%-plumbed `control_surface`? | **PASS** — L16, L47, L79, L92, and complexity ranking all explicitly name the existing plumbing |
| 2 | Sub-task ordering per intel (irreg-freq → QTF → field-points, lightest→heaviest) | **PASS** — L118, L148, L185, and L219 all enforce the order; independently landable |
| 3 | bool→enum migration tradeoff explicitly surfaced | **PARTIAL** — surfaced (L291) but the in-plan mechanism contradicts the stated default (see D3) |
| 4 | Scope discipline (no drift into #500 runner territory) | **PASS** — L48-L49, L112, L285, L112-L114 of intel all respected; runner excluded |
| 5 | Byte-identity regression gate defined | **PARTIAL** — gate exists (L243-L245) but mis-specified against real code (see D1, D2) |
| 6 | QTF section gating (solve_type vs qtf_calculation) correctly modeled | **FAIL** — see D2 |
| 7 | Headings-section QTF crossing-angle gating correctly modeled | **FAIL** — see D1 |
| 8 | `DetectAndSkipFieldPointsInsideBodies` current behavior correctly described | **FAIL** — see D4 |
| 9 | Deprecation semantics for `remove_irregular_frequencies` | **FAIL** — see D3 |
| 10 | Deprecation semantics for flat `qtf_calculation` | **PARTIAL** — see D5 |
| 11 | Past-tense / "already done" claims about proposed work | **PASS** — plan consistently uses "must be created", "does not exist" |
| 12 | Hard-forbidden self-approval language | **PASS** — Adversarial Review Summary section is empty placeholder |
| 13 | Distinct-source attestation (≥6) | **PASS** — 15 sources enumerated at L88 |
| 14 | Test names concrete and falsifiable | **PASS** — all 19 tests have concrete inputs/outputs |
| 15 | Acceptance criteria are executable commands | **PASS** — all five `uv run pytest` lines runnable from the plan |
| 16 | Risk register names DNV-RP-C205 / WAMIT / OrcaWave manual verification step | **PARTIAL** — manual verification named (L289) but not tied to a concrete acceptance gate |

---

## Specific Defects

### D1 — [CRITICAL] Headings-section QTF crossing-angle emission is gated by `qtf_calculation OR is_qtf`, not unconditional

**Location:** plan lines 172-174, 213, 234 (`test_qtf_crossing_angle_override`); pseudocode for sub-task 2.

**Plan claim:** "`backend._build_headings_section(spec): QTFMinCrossingAngle = qtf.min_crossing_angle # was 0`". Plan reads as if the hardcoded 0/180 is always emitted and only needs replacement.

**Live code** (`orcawave_backend.py:507-532`):
```
if spec.solver_options.qtf_calculation or is_qtf:
    section["QTFMinCrossingAngle"] = 0
    section["QTFMaxCrossingAngle"] = 180
    ...
```
The emission is **inside a conditional block**. Under the plan's proposed bool→nested migration path, if `qtf.enabled=False` is the resolved state, this block must **continue to not emit** those keys, otherwise back-compat L00 fixture (which does not set `qtf_calculation`) starts emitting `QTFMinCrossingAngle=0` and the byte-identity gate fails.

**Why it matters:** The plan's test `test_qtf_crossing_angle_override` and the pseudocode assume the lines can be mechanically swapped. They cannot. The replacement must preserve the `if qtf.enabled or solve_type in (...qtf...)` gate. Without this, either (a) the byte-identity test fails silently only on the QTF-using fixtures (L03), or (b) the test is written as a happy-path assertion and misses the gate regression entirely.

**Required remediation:** Pseudocode and test list must make the gate explicit: "crossing-angle override only emits when QTF section is gated on." Add a test `test_qtf_crossing_angle_not_emitted_when_qtf_disabled`.

---

### D2 — [CRITICAL] `_build_qtf_section` fires only for `solve_type in (diagonal_qtf, full_qtf)`, not for `qtf_calculation: bool`

**Location:** plan lines 176-183, 237-239, 293.

**Plan claim:** Pseudocode for sub-task 2 maps `qtf.load_calculation_method` to `QTFCalculationMethod` / `PreferredQTFCalculationMethod` inside `_build_qtf_section`, and tests `test_qtf_load_calc_method_{near_field,far_field,both}` drive this.

**Live code** (`orcawave_backend.py:572-580`):
```
def _build_qtf_section(spec):
    solve_type = _effective_solve_type(spec)
    if solve_type not in ("diagonal_qtf", "full_qtf"):
        return {}
    ...
    section["QTFCalculationMethod"] = "Both"
    section["PreferredQTFCalculationMethod"] = "Direct method"
```
The QTF section is **keyed off `solve_type`, not `qtf_calculation`**. That means:
1. A nested `QTFOptions(enabled=True, load_calculation_method="far field")` with `solve_type="potential_and_source"` will **silently drop the load-calc-method override** (empty dict returned before the mapping runs).
2. The plan's `QTFOptions.enabled: bool` is not the correct gate — the real gate is `solve_type`, and the plan does not propose reconciling the two.
3. The compat shim "if any flat qtf_* field is set → synthesize qtf" (L167-168) does not address the solve_type coupling, so an existing fixture with `qtf_calculation: true` but `solve_type="potential_and_source"` (which today emits nothing) will behave the same only by coincidence — not by design.

**Why it matters:** The plan introduces a `QTFOptions.enabled` flag that is effectively decorative. Users will set `enabled=True` and their overrides will be silently ignored unless they also set `solve_type` to a QTF value. This is a UX footgun and a correctness regression waiting to happen.

**Required remediation:** Decide whether `QTFOptions.enabled=True` should (a) raise if `solve_type` is not a QTF type, (b) auto-upgrade `solve_type`, or (c) preserve today's `solve_type`-keyed gate and make `enabled` purely informational. Add a test that exercises the interaction.

---

### D3 — [HIGH] `remove_irregular_frequencies` default change breaks implicit back-compat

**Location:** plan lines 128-134, 232, 291.

**Plan claim (tradeoff B, compat-preserving):** keep `remove_irregular_frequencies: bool | None = None` as deprecated alias; derive new enum from it.

**Live code** (`input_schemas.py:457-460`):
```
remove_irregular_frequencies: bool = Field(
    default=True,
    description="Remove irregular frequency effects",
)
```
Today the field is **non-optional with default `True`**. The plan changes both the type (to `bool | None`) and the default (to `None`). A spec that does NOT set `remove_irregular_frequencies` today gets `True` (interior panels); under the plan, unset → `None` → `irregular_frequency_method=interior_panels` via the validator default. This only works if the validator explicitly hard-codes the `None → interior_panels` mapping, but the plan's pseudocode (L132-134) only describes the branches for `is not None`. The unset case falls through to `irregular_frequency_method: IrregularFrequencyMethod = interior_panels` (the field default), which happens to match — but the plan does not say so, and a reviewer cannot verify back-compat from the pseudocode alone.

Worse, `test_remove_irregular_frequencies_legacy_true` and `..._legacy_false` cover the legacy explicit cases, but no test covers the **legacy-implicit-default** case: "spec that omits both fields → emits `BodyAddInteriorSurfacePanels=Yes`". This is the single most common legacy path and it has no gate.

**Required remediation:** Add `test_remove_irregular_frequencies_legacy_unset` ("spec sets neither field → default emission unchanged"). Document in pseudocode that the new field's default is `interior_panels` specifically to preserve today's default-`True` behavior.

---

### D4 — [HIGH] `DetectAndSkipFieldPointsInsideBodies` is hardcoded `"Yes"` today — plan misdescribes current state

**Location:** plan lines 17, 20, 200-202, 297.

**Plan claim (L17):** "`OutputSpec` has `detect_field_points_inside_bodies` but no `field_points` collection."

**Live code** (`orcawave_backend.py:548`): `section["DetectAndSkipFieldPointsInsideBodies"] = "Yes"` is hardcoded; there is **no field on `OutputSpec`** reading into this emission. The intel file (intel L27) correctly says "`_build_outputs_section` emits only `OutputPanelVelocities` + `DetectAndSkipFieldPointsInsideBodies: Yes`" — no claim that OutputSpec carries a field for it.

**Why it matters:** The plan's risk register (L297) says "respect existing `detect_field_points_inside_bodies` global override" and the pseudocode (L202) says "respect existing detect_field_points_inside_bodies global override" — but there is no such override on OutputSpec today. The plan is proposing a new feature while asserting it already exists. Adversarial reading: either (a) the plan needs to add `OutputSpec.detect_field_points_inside_bodies: bool = True` explicitly (currently missing from Files-to-Change), or (b) the backend keeps hardcoding `"Yes"` and the per-`FieldPointSpec.detect_inside_bodies` is indeed purely informational. Pick one and say so.

**Required remediation:** Either add `OutputSpec.detect_field_points_inside_bodies` to the schema change list (sub-task 3) with a clear default that preserves today's `"Yes"` emission, or amend L17 to say the current code hardcodes the switch and the plan does not expose it yet. Current ambiguity will yield an implementation that splits the difference and breaks byte-identity.

---

### D5 — [MEDIUM] Flat `qtf_calculation: bool` → nested `qtf: QTFOptions | None` default-drift

**Location:** plan lines 160-170, 239.

**Plan claim:** "retained deprecated aliases ... if neither is set → `qtf = QTFOptions(enabled=False)` (preserves today's default)".

**Live code:** `qtf_calculation: bool` default `False`, so today's neither-set case emits no QTF section for non-QTF solve_types (D2 above) and emits with hardcoded 0/180/Both/Direct for QTF solve_types. The plan's "preserves today's default" holds for the `enabled=False` boolean, but the side effects of the nested shape — `min_crossing_angle=0.0`, `max_crossing_angle=180.0` as Python floats — diverge from today's integer literals `0` and `180` at the YAML emission layer if the pseudocode is taken literally (L174 writes `qtf.min_crossing_angle` → float). PyYAML / Ruamel emit `0.0` vs. `0` differently. The byte-identity gate will fail on L03.

**Required remediation:** Pin the default types to match today's emission (integer `0` / `180` if that's what goes to YAML today — grep the golden file, do not guess). Or, cast in the backend emission step. Either way, add an explicit integer-vs-float assertion to the byte-identity test.

---

### D6 — [MEDIUM] Byte-identity test naming is load-bearing but test implementation is unspecified

**Location:** plan lines 243-245, 256-257.

**Plan claim:** `test_byte_identical_L00_fixture`, `..._L02_fixture`, `..._L03_fixture` compare OrcaWave YAML to a "golden file".

**Defect:** No golden file path is named. `test_orcawave_semantic_roundtrip.py` (301 lines, per intel) is today a **semantic** roundtrip, not byte-level. Introducing byte-level tests without naming the golden-file artifact location is a hand-wave — the reviewer cannot verify the gate exists or where it lives. Worse, if golden files are generated from HEAD at implementation time, they will bake in whatever the implementation emits (including D1/D2/D4 regressions) and silently "pass." Golden files must be frozen from the **pre-change** tree and committed as a separate prior step.

**Required remediation:** Name the golden-file directory (e.g., `digitalmodel/tests/hydrodynamics/diffraction/fixtures/golden/L00_orcawave.yml`). Add an explicit acceptance-criterion bullet: "golden YAML files generated from current HEAD, committed **before** any schema change, and diffed byte-for-byte." Add a separate pre-implementation commit for the golden-file generation step to the Files-to-Change table.

---

### D7 — [MEDIUM] `_build_general_section` (L414-451) is named in intel but ignored by the plan

**Location:** intel L29 flags `_build_general_section` as "Read-only consumer of new fields; if `qtf_calculation` becomes a nested `QTFOptions.enabled`, need a compat shim here." Plan's Files-to-Change table (L211-217) does not mention `_build_general_section`.

**Defect:** The plan's compat shim is described as living on `SolverOptions` (model_validator level) which should be fine — but intel explicitly warned that `_build_general_section` is a downstream consumer, and the plan neither confirms the warning is resolved by the model-level shim nor adds a test that `_build_general_section` emission is unchanged. If `_build_general_section` reads `spec.solver_options.qtf_calculation` directly (common pattern), the validator's synthesis may not flow through without a resolver accessor like the plan's `resolved_qtf()` (L172, L177) — but `resolved_qtf()` is used only in headings/qtf sections, not in general.

**Required remediation:** Extend the audit to `_build_general_section` and either use `resolved_qtf().enabled` there too, or add an explicit test that `_build_general_section` emission is byte-identical under the flat-field compat path.

---

### D8 — [LOW] "Near field / far field / both" → Direct / Indirect / Both mapping is unverified

**Location:** plan L178-182, L289.

**Plan admits** (risk L289) that the mapping "needs correction in the OrcaWave manual citation step. Reviewer must confirm mapping against the OrcaWave User Manual before landing sub-task 2." This is honest but soft. The plan's tests (L235-237) hard-code the mapping without citing the manual or deferring the decision. If the mapping is wrong, the tests will pass and the OrcaWave binary will either reject the spec or silently do the wrong thing.

**Required remediation:** Promote the manual check to an explicit acceptance bullet: "`QTFCalculationMethod` mapping cited in code comment with OrcaWave User Manual section reference" — or make load_calculation_method pass through verbatim (e.g., `Literal["Direct", "Indirect", "Both"]`) and let the caller supply OrcaWave's own vocabulary. The latter is safer.

---

### D9 — [LOW] Sub-task 3 test `test_field_points_empty_unchanged` claims "byte-identical to pre-#501 output" without a golden

Same defect as D6, narrower scope. `OutputSpec(field_points=[])` producing "backend YAML byte-identical to pre-#501 output" requires a captured pre-#501 reference. Either cover via D6 fix or remove the claim and fold into the L00/L02/L03 fixtures.

---

### D10 — [LOW] `load_calculation_method` string literal drift

**Location:** plan L157, L178-182.

`QTFOptions.load_calculation_method: Literal["near field", "far field", "both"]` uses **lowercase + space**. The intel (L77) and OrcaWave User Manual use **title-case** in YAML (`"Direct method"`, `"Indirect method"`, `"Both"`). Two spellings in a plan that treats strings as contract is a trap — case and spacing mismatches here will drive a whole round of test churn. Pick the canonical form once (Python enum → backend mapping) and stop referring to the raw strings in prose.

---

## Justification

**Why MAJOR, not MINOR:** The plan is well-scoped, correctly cites intel, orders sub-tasks correctly (D-2 checklist pass), and respects the #500 boundary. The defect distribution is narrow but hits the two most dangerous failure modes for this class of work:

1. **The byte-identity regression gate is the plan's only defense against silent back-compat breaks** (explicitly called out at L283). D1, D2, D4, D5, D6 all attack that gate's integrity — either by misdescribing what it compares against (D6), by regressing conditions the gate needs to preserve (D1, D2, D5), or by introducing an ambiguous spec that will be "resolved" in implementation and bake a hidden regression into the golden file (D4). A plan whose load-bearing safety mechanism is mis-specified cannot be approved.

2. **The enum/bool migration semantics are the only user-visible API change in the whole plan** (explicit tradeoff at L291). D3 shows the proposed compat shim does not actually cover the most common legacy invocation path (unset-field default). A migration plan that breaks its most common migration case is not compat-preserving.

**Why not CRITICAL/BLOCKER:** No defect indicates an architectural rethink is needed. All ten defects are fixable by targeted edits to the pseudocode, test list, and Files-to-Change table. The plan's sub-task decomposition, ordering, and scope are sound.

**Re-draft scope:** ~30-50 lines of plan edits covering (a) QTF gating reconciliation (D1+D2), (b) remove_irregular_frequencies default-preservation (D3), (c) DetectAndSkip current-state disambiguation (D4), (d) golden-file naming + ordering (D6+D9), (e) load-calc-method literal canonicalization (D10), (f) `_build_general_section` audit coverage (D7). No rework of the three-sub-task structure or the ordering.

**Hard-forbidden check:** Plan does not self-approve, does not mark `status:plan-approved`, does not pre-authorize downstream agents. Adversarial Review Summary (L264-277) is correctly left empty for reviewer fill-in. No past-tense "already implemented" claims about the proposed work. **Clean on forbiddens.**

---

## Critical findings summary (for Summary row)

D1 + D2 break the QTF emission gating (`_build_headings_section` conditional, `_build_qtf_section` solve_type key); D4 misstates current `DetectAndSkip...` handling; D6 leaves the byte-identity golden-file source unnamed. Fix these before implementation.
