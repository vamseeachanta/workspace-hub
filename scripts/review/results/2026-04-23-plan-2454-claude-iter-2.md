# Adversarial plan review — #2454 (Claude, cold context, iter-2)
**Verdict:** MAJOR
**Reviewer:** claude (cold-context adversarial, iter-2)
**Date:** 2026-04-23
**Plan path:** docs/plans/2026-04-23-issue-2454-c03-fpso-semantic-proof.md

## What I verified

1. `digitalmodel/scripts/semantic_validate.py` line 101 — `Significance` is a plain class of string constants (`MATCH`, `COSMETIC`, `MINOR`, `SIGNIFICANT`, `TYPE_MISMATCH`, `MISSING`, `EXTRA`). Confirmed.
2. `ALLOWED_DIFF_PROPS` at line 117 (set through line 178). Confirmed.
3. `load_monolithic(path: Path) -> dict` at line 291; `load_modular(modular_dir: Path) -> dict` at line 304 — directory-only. Confirmed the plan's M2 fix (uses directory, not master.yml).
4. `--json` flag exists at line 1951 with `action="store_true"`. Confirmed; plan's m4 minor is resolved.
5. `to_json(result: ValidationResult) -> dict` at line 1206. Confirmed.
6. `ModularModelGenerator(spec_file)` constructor at `modular_generator/__init__.py:69` assigns `self.spec = self._load_and_validate_spec()` at line 71 — `.spec` attribute DOES exist and is a `ProjectInputSpec`. The plan's hedge about "unverified `.spec` attribute name" is overly cautious.
7. `EnvironmentBuilder._WIND_SPEED_DORMANT` at `environment_builder.py:160` IS a class attribute — but its value is `{"Full field"}`, a set of WindType mode names, NOT a set of property keys.
8. `GroupsBuilder.should_generate()` at `groups_builder.py:27-29` returns `spec.is_pipeline() or spec.is_riser()`. Confirmed.
9. `BaseBuilder.__init__(self, spec, context)` at `builders/base.py:23` requires TWO positional args — `spec` AND `context: BuilderContext`. `GroupsBuilder` inherits this unchanged.
10. `@requires_orcaflex` block at `test_modular_vs_monolithic.py:27-37` matches what the plan copies verbatim.
11. Roadmap `docs/roadmaps/orcawave-orcaflex-canonical-spec-contract-roadmap.md` — "turret-moored FPSO" bullet at line 116 under "Partial but high-value next validations". Only two existing buckets ("Ready now" at line 109, "Partial..." at line 115); the plan's proposal to add a third "Ready for L1 / static-YAML-diff" bucket is structurally coherent.
12. c03 fixture paths at `digitalmodel/docs/domains/orcaflex/library/model_library/c03_turret_moored_fpso/{spec.yml,monolithic/,modular/}` — all exist.
13. `SEMANTIC_DIFF_TAXONOMY.md` — L1/L2/L3 defined at lines 274-276 (plan cites line 273, off-by-one but non-material). L2 explicitly requires statics/dynamics result matching.

## Findings (by severity)

### MAJOR

- **[MAJOR] Pseudocode imports a non-existent `compare` function** — `docs/plans/2026-04-23-issue-2454-c03-fpso-semantic-proof.md:126` imports `compare` from `semantic_validate` and at line 164 writes `result = compare(mono_data, mod_data)`. No such symbol exists in `semantic_validate.py`. The real API is `validate(mono_data, mod_data, rtol, atol, sections_filter) -> list[SectionResult]` at line 917. Additionally `validate()` returns a `list[SectionResult]`, not a `ValidationResult`, so `to_json(result)` would fail as `to_json` expects a `ValidationResult` (line 1206) and reads `result.sections`, `result.model_name`, `result.monolithic_path`, `result.modular_path`, `result.timestamp` (lines 1209, 1249-1252). The pseudocode cannot be executed as written — the test would fail at import time, and even after renaming to `validate` it would fail at the `to_json` call. Comparing with `main()` at lines 2077-2088 shows the canonical wiring: call `validate()`, then wrap in `ValidationResult(model_name, monolithic_path, modular_path, timestamp, sections=validate_return)`, THEN call `to_json()`. The plan's Resource Intel summary at line 22 asserts "real API is … `compare(monolithic_data, modular_data) -> ValidationResult`" — this is factually wrong and the prior M1 finding has recurred in a new form (was "wrong bucket assertions"; is now "wrong entry-point symbol"). This is the single highest-priority defect.

- **[MAJOR] Pseudocode misses SIGNIFICANT diffs in list and nested sections** — `test_no_significant_diffs` (plan lines 182-188), `test_no_type_mismatch_diffs` (lines 190-196), and `test_missing_properties_are_documented_omissions` (lines 198-210) all iterate ONLY `sec.get("diffs", [])` and `sec.get("missing_in_mod", [])`. Per `to_json` output shape at `semantic_validate.py:1208-1244`, list-section diffs live under `sec["objects"][obj_name]["diffs"] / ["missing_in_mod"]` (lines 1223-1232), and nested-section diffs live under `sec["categories"][cat_name]["diffs"] / ["missing_in_mod"]` (lines 1235-1244). The assertions as written will silently pass even when real SIGNIFICANT or TYPE_MISMATCH diffs exist in LineTypes, Vessels, Lines, VesselTypes — which are list sections, and are exactly the sections where turret-moored FPSO physics properties live (mooring line EA/EI/mass, vessel types, mooring geometry). Compare to the real implementation of `SectionResult.has_significant_diffs` at `semantic_validate.py:248-261` which correctly walks `self.diffs`, `self.objects[*].diffs`, AND `self.nested_categories[*].diffs`. This is not a pseudocode nit — it is a semantic hole in the L1 claim itself: the test suite cannot prove "no SIGNIFICANT diffs anywhere" without walking all three levels. The plan therefore fails its own §Acceptance Criteria bullet 1 even when the test reports green.

- **[MAJOR] `GroupsBuilder(spec).should_generate()` will TypeError at runtime** — Plan line 222-223: `spec = ModularModelGenerator(SPEC_YML).spec; assert not GroupsBuilder(spec).should_generate(), ...`. `GroupsBuilder` inherits `BaseBuilder.__init__(self, spec, context)` at `builders/base.py:23`, which requires a `BuilderContext` as its second positional argument. Passing only `spec` raises `TypeError: __init__() missing 1 required positional argument: 'context'`. The plan's Risk section at line 326 hedges the `.spec` attribute name but doesn't catch this constructor shape. The prior M4 finding was "GROUPS_POLICY fabricated" and iter-2 replaced it with a call to a real method via a fabricated constructor signature — the defect moved rather than resolving. Fix options: (a) pass `BuilderContext()` as a second arg (it has no required args per `builders/context.py`; still must verify), or (b) promote `should_generate` to a staticmethod/classmethod if the executor owns that API change (scope creep — not this plan's write set), or (c) replace the test with a direct check on `spec.is_pipeline() or spec.is_riser()` (cleanest — bypasses builder instantiation altogether).

### MINOR

- **[MINOR] `DOCUMENTED_OMISSION_KEYS` type-confuses WindType values with property keys** — Plan lines 145-152 union `set(EnvironmentBuilder._WIND_SPEED_DORMANT)` into `DOCUMENTED_OMISSION_KEYS`, which is then checked against property-name keys at line 207 (`if key in DOCUMENTED_OMISSION_KEYS`). `_WIND_SPEED_DORMANT = {"Full field"}` at `environment_builder.py:160` is a set of WindType MODE names, used at line 236 as `if wind_type not in self._WIND_SPEED_DORMANT`. It is not a set of property keys that would ever appear in `missing_in_mod`. The union is harmless (it never matches a real key so cannot falsely whitelist anything), but the plan misunderstands the semantic role of this symbol and the Resource Intel section at line 71 states it as if it were a property-key skip-list. If the intent is to document that `WindSpeed` is dormant for certain wind types, the whitelist should contain `"WindSpeed"` (conditional on spec's wind_type); the plan's reasoning chain is broken even if the runtime effect is benign.

- **[MINOR] `_SKIP_GENERAL_KEYS` count claim overstated** — Plan Resource Intel line 24 claims "34 keys" for `_SKIP_GENERAL_KEYS`. Direct count of the set literal at `generic_builder.py:115-149` is 24 entries. Doesn't affect correctness but signals the verification pass was shallow; adjust or drop the count.

- **[MINOR] Frozen-diff equality check at line 230 is brittle to non-determinism** — `assert diff_report == frozen` on the full `to_json()` dict. The dict includes `timestamp` (per `to_json()` line 1252 via `result.timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")`) and `monolithic_path` / `modular_path` that are absolute at generation time but relative (or differently absolute) at test time. Every test run will produce a new timestamp; every cross-machine run will produce a new absolute path. The test will fail on run 2 regardless of whether any semantic content drifted. Mitigation: strip `timestamp`/paths before comparison, OR normalize to a canonical form (e.g. basename-only), OR compare only `sections` sub-dict. The plan's Risk section addresses first-baseline circularity but not this second failure mode.

- **[MINOR] SEMANTIC_DIFF_TAXONOMY.md line citations drift by ~1** — Plan line 39 cites line 273 for L1/L2/L3 claim levels; actual is line 274. Plan line 39 cites line 275 for L2 dynamics requirement; actual is line 275 ✓. Plan line 39 cites line 279 for L3 not-achieved; actual is line 278-280. Not correctness-relevant but suggests the citation pass was approximate.

- **[MINOR] `test_generated_modular_is_yaml_strict_loadable` will parse the master-file pseudo-YAML** — `_write_master()` at `modular_generator/__init__.py:226-240` emits a file whose first three lines are `%YAML 1.1\n# Type: Model\n# Generated from: ...\n` followed by `---`. The plan's test at line 175 does `yaml.safe_load((generated_modular / "master.yml").read_text(encoding="utf-8"))` which DOES parse valid YAML but only the first document. If OrcFxAPI treats this as a multi-document stream (the `%YAML` directive + the `---` document separator strongly suggest so), `yaml.safe_load` is wrong; should be `yaml.safe_load_all(...)` and iterate. This may be a latent defect depending on how OrcFxAPI actually consumes master.yml — executor should confirm at runtime.

### NITS

- Plan line 47 asserts "the C1..C6 taxonomy is a human overlay on top of `Significance`; there is no existing importable Python module that maps `(Significance, key) → C1..C6`" — correct and appropriately scoped out.
- Plan line 74 counts "distinct sources consulted: 6" — correct.
- Plan Risks section (line 323) adds "forbidden MINOR whitelist" as mitigation for the MINOR→physics escape path, BUT defers the concrete property-family list to "execution phase … documented as a sub-issue rather than dropped". This is a hedge, not a plan — the families ARE listed in prose (water depth, wave height, wave period, current speed, line length, segment length, EA, EI, OD, ID, mass-per-length). Acceptable as a MINOR-tier item; the list is concrete enough to be transcribed into a `_FORBIDDEN_MINOR_KEYS` constant at execution time. Not a blocker.
- Plan lines 300-304 attribute `N/A` Codex/Gemini verdicts to the "permission-gated worker" constraint, citing `feedback_permission_gate_blocks_cross_review.md`. This matches the memory entry and is transparent provenance; acceptable per the referenced feedback.

## Verdict justification

Three MAJOR findings, each individually sufficient to block:

1. The pseudocode imports `compare` — a symbol that does not exist. This is M1 recurring. If the plan is handed to an execution agent verbatim, the first pytest collection will fail at import time. The fix is mechanical (`validate` + wrap in `ValidationResult`), but the plan must state it correctly because the pseudocode is the executable contract between planner and executor.

2. The `test_no_significant_diffs` / `test_no_type_mismatch_diffs` / `test_missing_properties_are_documented_omissions` trio only walks flat-section diffs. The turret-moored FPSO model's load-bearing physics (mooring `LineTypes`, `Vessels`, `Lines` coordinates) lives in list sections. The tests can return green while carrying SIGNIFICANT physics diffs, which invalidates the §Acceptance-Criteria L1 + static-YAML-diff claim. This is a semantic hole in the proof itself.

3. `GroupsBuilder(spec)` cannot be constructed with one arg — `BaseBuilder.__init__` needs `(spec, context)`. The plan replaced fabricated `GROUPS_POLICY` with a fabricated constructor signature. The test would TypeError before its assertion runs.

The iter-1 M2, M3, m1-m6 findings DO appear genuinely addressed. The resource-intel section is substantially stronger than iter-1. But iter-2 introduces two new correctness defects (the `compare` symbol, the constructor shape) and carries forward one that iter-1 didn't catch (the list-section blind spot in assertions).

The plan is close — these are mechanical fixes to pseudocode, not structural rethinks — but it cannot proceed to `status:plan-review` with pseudocode that won't execute and tests that under-cover the claim.

---

**Summary:** verdict MAJOR; 3 MAJOR findings and 5 MINOR; NOT ready for `status:plan-review` until the three correctness-critical defects in pseudocode and assertion coverage are resolved.
