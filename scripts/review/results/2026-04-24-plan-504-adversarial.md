# Adversarial Review — Plan #504 (OrcaFlex buoys builder refactor)

**Reviewer:** adversarial (defect-hunter stance)
**Date:** 2026-04-24
**Plan:** docs/plans/2026-04-24-issue-504-orcaflex-buoys-builder-refactor.md
**Intel:** /tmp/orca-batch-2026-04-24/intel-504.md
**Issue:** https://github.com/vamseeachanta/digitalmodel/issues/504

---

## Verdict: MINOR

The plan passes all four #504-specific hard gates but has concrete defects that require revision before `status:plan-approved`. Registry collision is named with line-and-key specificity, both Approach A and Approach B are presented with PROS/CONS, Approach B recommendation includes a public-callers audit via `grep -rn "BuoysBuilder\|get_support_geometry"` in the acceptance criteria, and golden-fixture byte-identical preservation is an explicit acceptance gate. None of these are missing; but the plan still has MINOR-severity ambiguities that will bite during implementation, plus one MAJOR-adjacent defect around `build()` method placement in the orchestrator shim.

---

## Hard-Gate Checklist (per intel — MUST PASS)

| # | Gate | Status | Evidence in plan |
|---|---|---|---|
| 1 | Named `BuilderRegistry._registry` collision keyed by `08_buoys.yml` | **PASS** | Line 17 ("dict keyed by `output_file` (line 24). A second `@register('08_buoys.yml', ...)` silently overwrites the first"); Line 40 ("no 'multiple builders → same output file' convention"); TRADEOFF block line 288 reproduces and escalates. |
| 2 | Both Approach A (distinct slots) AND Approach B (BuoysOrchestrator) visible | **PASS** | Lines 290-295 (Approach A: distinct slots `08a_rollers.yml...08d_end_buoys.yml`, PROS, CONS, complexity). Lines 296-300 (Approach B: orchestrator under single slot, PROS, CONS, complexity). Recommendation to user (B) is made explicitly while A stays visible with its triggers (lines 306-309). |
| 3 | For recommended Approach B: verified no public-API callers bypass orchestrator | **PASS (with caveat)** | Line 259 in acceptance criteria: `grep -rn "BuoysBuilder\|get_support_geometry" digitalmodel/` — every hit must go through new API or shim. Intel already enumerated all call sites (3 test files + 2 `__init__.py` + `lines_builder.py` for context field). **Caveat:** the acceptance grep is defined but has not been EXECUTED in the plan text itself — the Resource Intelligence section enumerates callers but does not attest that no other repo-wide caller invokes methods like `_build_tugs`, `_build_buoyancy_module` directly. See DEFECT #3. |
| 4 | Golden-fixture test preservation included (611-line file is test-protected) | **PASS** | Line 195 (`Verify (byte-identical) ... 08_buoys.yml, _08_buoys_data.yml — Golden-file diff MUST be empty`), Line 243 (`test_golden_08_buoys_yml_byte_identical`), Line 256 (acceptance: `diff ... → no output`), Line 244 (`test_output_ordering_preserved`). Coverage explicit. |

All four hard gates pass.

---

## Full Defect Checklist (standard stance)

| # | Category | Status | Note |
|---|---|---|---|
| 1 | Scope creep / hidden behavior change | CLEAN | Plan explicitly says no behavior change; byte-identical YAML is an acceptance criterion. |
| 2 | Acceptance criteria falsifiability | MINOR | Criterion "Output-ordering check" is worded without a concrete assertion command (see DEFECT #2). |
| 3 | Test list completeness | MINOR | Missing a test for the `all_buoy_names` aggregation path (see DEFECT #4). |
| 4 | TDD-before-move ordering | CLEAN | Line 41 + line 316 make pre-move backfill load-bearing. |
| 5 | Public-API breakage handling | MINOR | Approach B preserves `BuoysBuilder` symbol; however compat-shim for `get_support_geometry` is asserted without specifying whether the forwarder preserves the `@staticmethod` decorator AND the import-time registration side-effect chain (see DEFECT #1). |
| 6 | Cross-builder coupling | PARTIAL | `lines_builder.py` line 44 consumer named; `test_lines_builder_consumes_end_buoy_name_unchanged` present. GOOD. |
| 7 | Context-field bookkeeping | MINOR | `all_buoy_names` aggregation surfaced in risks (line 318) but NO concrete test in TDD list for it under Approach B; intel flagged this as "SINGLE most load-bearing cross-cutting concern". See DEFECT #4. |
| 8 | Registry convention correctness (Approach A) | MINOR | Plan says order=80.1..80.4 "OR equivalent" — whether `BuilderRegistry` currently supports fractional orders (vs. int-only) is NOT verified against `registry.py`. See DEFECT #5. |
| 9 | DRY / shared constants | CLEAN | `_buoy_geometry.py` with leading underscore is explicit; BM bespoke wireframe explicitly excluded from shared (line 319, line 236). |
| 10 | BulkModulus divergence | CLEAN | Per-type tests pinned (lines 233, 237, 239). |
| 11 | Complexity sizing | CLEAN | T2 with bounded scope, justified against T1 and T3. |
| 12 | Artifact paths | CLEAN | All absolute paths resolve; new files flagged as MISSING (pre-refactor). |
| 13 | Golden fixture path accuracy | CLEAN | Paths match intel; two fixture files enumerated. |
| 14 | Static-method shim semantics | MINOR | See DEFECT #1. |
| 15 | Orchestrator shim fidelity | MAJOR-adjacent | See DEFECT #6 — plan says orchestrator invokes each child's `build()` in fixed order; but `BuoysBuilder.build()` currently assembles `six_d_buoys`/`three_d_buoys` lists as locals and writes to context once at the end. Delegation order + where the list accumulation lives is under-specified. |
| 16 | Plan status transitions | CLEAN | Line 263 enumerates GSD states correctly. |
| 17 | Tense discipline (per `feedback_plan_past_tense_artifact_claims`) | CLEAN | All prospective artifacts use MISSING/`create` verbs; no false past-tense claims. |

---

## Specific Defects

### DEFECT #1 — `get_support_geometry` compat shim under-specified (MINOR)

**Location:** Plan line 211 (Approach B rewrite row) + line 246 (test row).

**Problem:** The plan says the rewritten `BuoysBuilder` "Preserves the `BuoysBuilder.get_support_geometry` re-export as a `@staticmethod` forwarding to `RollerBuilder.get_support_geometry`". Two ambiguities:

1. The forwarder MUST be a true `@staticmethod` (not a classmethod or instance method). The current call sites (`test_buoys_builder.py` lines 171/190/203/216) call `BuoysBuilder.get_support_geometry(station, roller_type)` WITHOUT instantiating, so instance/classmethod would pass an extra arg and break silently.
2. The import-order risk: `buoys_builder.py` imports `roller_builder.RollerBuilder` at module load to forward. If `RollerBuilder` in turn imports from `buoys_builder` (e.g., through `__init__.py` re-exports or the `_buoy_geometry.py` path), a circular import can land. Plan does NOT specify the import topology or assert acyclicity.

**Recommended fix:** Add to the Pseudocode section an explicit `class BuoysBuilder: get_support_geometry = staticmethod(RollerBuilder.get_support_geometry)` construct AND add a circular-import acceptance gate (e.g., `python -c "from digitalmodel.solvers.orcaflex.modular_generator.builders import BuoysBuilder, RollerBuilder"` must succeed with fresh import cache).

### DEFECT #2 — Output-ordering acceptance is not a script-level check (MINOR)

**Location:** Plan line 257.

**Problem:** `"Output-ordering check: emitted 6DBuoys list in test_cli_base still reads rollers → tugs → BM → end_buoy"` — reads as manual eyeball. There's no `yq` / `python -c` snippet to assert. A refactor reviewer cannot falsify this without re-deriving the expected sequence.

**Recommended fix:** Either (a) rely solely on the byte-identical golden-file diff (which implicitly verifies order), making this criterion redundant and removable, or (b) provide a concrete assertion command like `python -c "import yaml; d=yaml.safe_load(open('...08_buoys.yml')); names=[b['Name'] for b in d['6DBuoys']]; assert names[0].startswith('Roller_') and names[-1].startswith('EndBuoy_')"`. Otherwise this line is prose, not a gate.

### DEFECT #3 — Public-caller audit is declared, not executed (MINOR)

**Location:** Plan Resource Intelligence + line 259 acceptance.

**Problem:** The plan enumerates known callers (`builders/__init__.py`, `modular_generator/__init__.py`, `lines_builder.py`, 3 tests) but never explicitly attests "I ran `grep -rn 'BuoysBuilder\|buoys_builder' $WORKSPACE` and above list is COMPLETE". The acceptance criterion defers this grep to implementation time. Under Approach B's "no bypass" invariant required by the hard gate, the plan should prove the callers list is closed NOW — because an unknown caller that invokes a private method like `_build_tugs` directly (unlikely but possible via test fixtures or ad-hoc scripts) would silently break even with Approach B.

**Recommended fix:** Add one line to Evidence section: `grep -rn "BuoysBuilder\|_build_tugs\|_build_buoyancy_module\|_build_end_buoy\|_build_mid_pipe_marker" /mnt/local-analysis/workspace-hub/ → returns only the N call sites enumerated above; no unexpected callers`. This closes the gate pre-implementation, not at acceptance time.

### DEFECT #4 — No test for `all_buoy_names` aggregation under Approach B (MINOR → load-bearing)

**Location:** TDD Test List (lines 219-247) — missing.

**Problem:** Intel explicitly flagged `all_buoy_names` aggregation as "the SINGLE most load-bearing cross-cutting concern in the refactor" (intel line 104). Plan risk block acknowledges it (line 318: "Approach B aggregates inside the orchestrator after delegating"), but the TDD test list has NO `test_orchestrator_aggregates_all_buoy_names` entry. Tests exist for `roller_buoy_names` (line 224), `end_buoy_name` (line 241), `buoy_names_3d` (line 240), but the UNION (`all_buoy_names` = `buoy_names_6d` ∪ `buoy_names_3d`) is untested.

**Recommended fix:** Add a test row: `test_orchestrator_all_buoy_names_is_union | Under Approach B, context.all_buoy_names equals union of buoy_names_6d + buoy_names_3d after all 4 sub-builders run | floating spec with rollers+tugs+BM+end+mid-pipe | set(context.all_buoy_names) == set(context.buoy_names_6d) | set(context.buoy_names_3d) and length matches`.

### DEFECT #5 — Fractional `order=` values under Approach A are unverified (MINOR)

**Location:** Plan line 317: "Approach A must use `order=80.1, 80.2, 80.3, 80.4` (or equivalent)".

**Problem:** Plan assumes `BuilderRegistry.register(order=...)` accepts floats. Sibling-builder convention in intel (standards line 84) says "multiples of 10 for order" — implying int-typed. If `_registry` is an ordered collection sorted by `order` where `order` is typed `int`, 80.1 fails at type-check or mis-sorts. The plan does not verify `registry.py`'s `order` parameter type.

**Recommended fix:** Add to Evidence block a one-line check: `registry.py line N: order parameter is typed as <int|float>; stable sort behavior when two builders share same int verified by test Y`. If `order` is int-only, Approach A requires registering as `order=80, 81, 82, 83` (which the Pseudocode block actually uses — lines 128, 143, 151, 160 — creating an INCONSISTENCY with line 317). Fix: pick one (int-only or fractional) and make the Risks block and Pseudocode agree.

### DEFECT #6 — Orchestrator list-accumulation contract under-specified (MAJOR-adjacent)

**Location:** Plan line 211 (orchestrator rewrite) + Pseudocode block line 169.

**Problem:** Today's `BuoysBuilder.build()` (lines 67-126 per intel) assembles two local lists (`six_d_buoys`, `three_d_buoys`) across all four sub-operations and then calls `_register_entity` six times at the end. Under Approach B, each sub-builder is now its own `BaseBuilder` with its own `build()` method. Questions the plan does NOT answer:

- Does each sub-builder write DIRECTLY to `self.context` fields during its own `build()`, and the orchestrator just coordinates ordering?
- OR does the orchestrator invoke each sub-builder's `build()` which RETURNS fragments, then the orchestrator aggregates and writes to context?
- OR do sub-builders append to a shared mutable accumulator passed by the orchestrator?

These three options have different failure modes (ordering races, duplicate registrations, partial-write visibility). The plan picks none. Without specification, two reviewers could implement legal-per-plan code that produces different `6DBuoys` orderings.

**Severity:** approaches MAJOR because this is the exact cross-cutting concern the intel flagged as MOST load-bearing, and the Pseudocode omits it. Downgraded to MAJOR-adjacent MINOR only because the byte-identical golden-file gate would eventually catch a wrong implementation — but post-hoc catching via fixture diff is exactly the kind of implicit spec the planning workflow is supposed to prevent.

**Recommended fix:** Add to Pseudocode an explicit orchestrator body:

```
class BuoysBuilder(BaseBuilder):
    def build(self):
        children = [RollerBuilder(self.spec, self.context), TugBuilder(...), BuoyancyBuilder(...), EndBuoyBuilder(...)]
        six_d, three_d = [], []
        for c in children:
            if c.should_generate():
                six, three = c.build()  # contract: returns (6d_fragments, 3d_fragments)
                six_d += six; three_d += three
        self._register_entity("buoy_names_6d", [b['Name'] for b in six_d])
        self._register_entity("buoy_names_3d", [b['Name'] for b in three_d])
        self._register_entity("all_buoy_names", [b['Name'] for b in six_d] + [b['Name'] for b in three_d])
        # end_buoy_name, bm_buoy_name, roller_buoy_names written by respective children directly on context
        return {"6DBuoys": six_d, "3DBuoys": three_d}
```

…OR whichever of the three options the planner chose, but it MUST be picked and named.

### DEFECT #7 — Mid-pipe marker placement rationale incomplete (INFORMATIONAL)

**Location:** Plan Open Questions, line 325.

**Problem:** Planner decision to house `_build_mid_pipe_marker` inside `end_buoy_builder.py` is reasonable but justified only by "both share floating-only gate, both free-standing". Not mentioned: mid-pipe marker is the ONLY `3DBuoy` producer (intel line 44, plan line 77). Putting it in `end_buoy_builder.py` means `end_buoy_builder` writes BOTH `6DBuoys` and `3DBuoys`, which is a minor SRP violation against the stated "four focused single-concern builders" framing. Not a blocker, but should be acknowledged explicitly.

**Recommended fix:** Add one sentence to the open question: "Accepting this SRP mini-dilution because the marker is ~25 lines, shares gating, and splitting it to its own file over-decomposes."

---

## Justification

The plan is unusually thorough for a T2 refactor. It surfaces the registry collision as an explicit `[TRADEOFF FOR USER]` with both approaches fully characterized, names all call sites from intel, carries pre-move TDD backfill as a load-bearing constraint, and treats golden-file byte-identity as the primary regression gate. These strengths earn MINOR (not MAJOR) despite seven concrete defects.

**Why MINOR not APPROVE:** DEFECT #6 leaves the orchestrator's list-accumulation contract ambiguous in the exact place the intel flagged as "the SINGLE most load-bearing cross-cutting concern" (intel line 104). A plan that escalates registry collision as a mandatory tradeoff while handwaving the aggregation semantics is asymmetric. DEFECT #4 (no test for `all_buoy_names` union) is the direct downstream consequence — untested invariant for the exact field intel warned about. DEFECT #5 is a contradiction inside the plan itself (Pseudocode uses `order=80..83` but Risks block uses `order=80.1..80.4`) that will cause implementation drift.

**Why not MAJOR:** None of the defects individually invalidate the approach. The byte-identical golden-file acceptance gate will catch ordering errors post-hoc (expensive but not fatal). Hard gates 1-4 all pass. The planner's Approach B recommendation is well-reasoned and the fallback to Approach A is clearly triggered. With the six MINOR fixes applied, the plan is ready for `plan-approved`.

**Hard-forbiddens check:**
- No past-tense claims about uncommitted work (CLEAN).
- No self-approval language (CLEAN — line 263 requires user approval).
- No dispatch of downstream agents pre-approval (CLEAN).
- No absolute paths hardcoded outside of `file_path`-required contexts (CLEAN — paths used are project-rooted).

---

## Recommended Revisions (in priority order)

1. **DEFECT #6** — Add explicit orchestrator Pseudocode showing list-accumulation contract and where `_register_entity` calls land.
2. **DEFECT #4** — Add `test_orchestrator_all_buoy_names_is_union` row to TDD Test List.
3. **DEFECT #5** — Resolve `order=` int-vs-float contradiction between Pseudocode and Risks block; verify against `registry.py` type.
4. **DEFECT #1** — Specify `@staticmethod` forwarder construction and circular-import acceptance check.
5. **DEFECT #3** — Execute and embed the `grep -rn` caller-closure attestation in Evidence block (pre-approval, not at acceptance).
6. **DEFECT #2** — Either remove redundant "output-ordering check" acceptance line or replace with concrete assertion command.
7. **DEFECT #7** — Add one-line SRP-dilution acknowledgment for mid-pipe marker placement.

With 1-3 addressed, re-review can likely upgrade to APPROVE.
