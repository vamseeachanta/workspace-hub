# Disagreement report — plan #504 (2026-04-24)

## Verdicts

| Provider | Verdict |
|---|---|
| adversarial | The plan passes all four #504-specific hard gates but has concrete defects that require revision before `status:plan-approved`. Registry collision is named with line-and-key specificity, both Approach A and Approach B are presented with PROS/CONS, Approach B recommendation includes a public-callers audit via `grep -rn "BuoysBuilder\|get_support_geometry"` in the acceptance criteria, and golden-fixture byte-identical preservation is an explicit acceptance gate. None of these are missing; but the plan still has MINOR-severity ambiguities that will bite during implementation, plus one MAJOR-adjacent defect around `build()` method placement in the orchestrator shim. |
| claude | MAJOR |
| codex | UNAVAILABLE (codex CLI failed, rc=2: error: unexpected argument '--no-interactive' found    tip: to pass '--no-interactive' as a value, use '-- --no-interactive'  Usage: codex exec [OPTIONS] [PROMPT]        codex exec [OPTIONS] <COMMAND>) |
| gemini | UNAVAILABLE (gemini CLI failed, rc=55: [31mGemini CLI is not running in a trusted directory. To proceed, either use `--skip-trust`, set the `GEMINI_CLI_TRUST_WORKSPACE=true` environment variable, or trust this directory in interactive mod) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### adversarial

(no findings unique to this provider)

### claude

- **[MAJOR] Pseudocode uses non-existent method `is_slay()`.** Plan §Pseudocode line 131 (RollerBuilder) calls `self.spec.is_slay()`. The actual method in `schema/root.py:193` is `is_s_lay()` (with underscore). Implementing verbatim raises `AttributeError` at first invocation. Every sibling builder already uses `is_s_lay()` — the plan's typo would not survive the first test run.
- **[MAJOR] Pseudocode calls `get_effective_rollers()` on the wrong object.** Plan §Pseudocode line 131 invokes `self.spec.get_effective_rollers()`. The method lives at `schema/equipment.py:402` — the correct path is `self.spec.equipment.get_effective_rollers()`, which is what the current mega-builder uses at `buoys_builder.py:85`. Verbatim implementation → `AttributeError`.
- **[MAJOR] `EndBuoyBuilder.should_generate()` narrows current behavior and will break the byte-identical golden-file acceptance criterion.** Plan §Pseudocode line 163 gates end-buoy on `self.spec.is_floating()`. But the current mega-builder at `buoys_builder.py:106–113` builds the end-buoy AND mid-pipe marker **unconditionally** once the outer `should_generate()` passes. Because `is_floating()` is defined as `pipeline is not None AND equipment.tugs is not None` (`schema/root.py:197–199`), the current slay-with-roller-arrangement path (which passes the outer gate via `effective_rollers is not None` at `buoys_builder.py:65`, with no tugs) currently produces both end-buoy and mid-pipe. Under plan's Approach B gate, that case drops both — producing a different `08_buoys.yml`. This contradicts Deliverable line 116 ("no change to the emitted `08_buoys.yml` content or ordering") and Acceptance Criterion line 256 ("Golden-file diff empty").
- **[MAJOR] `TugBuilder.should_generate()` also narrows current behavior.** Plan §Pseudocode line 146 gates tugs on `is_floating()`. Current code at `buoys_builder.py:94` is just `if self.spec.equipment.tugs:` — no `is_floating()` condition. `is_floating()` is formally equivalent to "pipeline + tugs present," so for a slay spec that happens to have tugs defined (permitted by schema), the plan's gate and the current gate diverge. Same class of golden-file regression as finding 3.
- **[MAJOR] `test_roller_builder_should_generate_floating` and `test_tug_builder_should_generate_floating_only` codify the wrong semantics.** Plan §TDD Test List lines 225 and 234 assert the new builders gate on floating. These tests, if written first as TDD safety net (as plan Risks line 316 demands), will either (a) fail against the unmodified mega-builder — blocking the pre-move TDD step per plan's own "If the pre-move unit tests fail, the refactor is paused" constraint — or (b) pass only if written to codify the NEW (wrong) semantics, at which point they no longer protect against regression. The TDD plan is internally inconsistent with the gate pseudocode.
- **[MAJOR] Missing `bm_buoy_name` cross-builder dependency.** Plan §Resource Intelligence line 19 claims "`builders/lines_builder.py` line 44 consumes `end_buoy_name` from `BuilderContext` — cross-builder dependency must survive split." But `lines_builder.py:46` also reads `bm_buoy_name = self.context.bm_buoy_name`. The plan-§TDD Test List only has `test_lines_builder_consumes_end_buoy_name_unchanged` — no equivalent `bm_buoy_name` integration test. If `BuoyancyBuilder` omits `self._register_entity("bm_buoy_name", "BM")`, lines_builder silently picks up the default-value literal `"BM"` from `context.py:43` and masks the regression.
- **[MAJOR] Approach-B orchestrator composition plumbing is under-specified.** Plan §Files-to-Change line 211 says the orchestrator "composes `RollerBuilder`, `TugBuilder`, `BuoyancyBuilder`, `EndBuoyBuilder` as private instances…calls each child's `build()` in fixed order." But each child's `_register_entity` (via `base.py:62–73`) writes to BOTH `self._generated_entities` and `self.context` (shared). The outer generator loop (`modular_generator/__init__.py:164`) calls `context.update_from_dict(builder.get_generated_entities())` on the **orchestrator's** dict, not the children's. Unless the orchestrator explicitly merges each child's `get_generated_entities()` into its own `self._generated_entities`, the outer loop's `update_from_dict` call is a no-op for the children's registered keys (`roller_buoy_names`, `buoy_names_6d`, `buoy_names_3d`, etc.). The current `update_from_dict` happens to be tolerant because children write to context directly, but any downstream reader of the generator's return dict for `get_generated_entities()` (including `test_builder_context.py` fixtures per plan §Resource Intelligence line 53) would see an empty orchestrator dict. Plan pseudocode and Files-to-Change do not show this merge step.
- **[MINOR] Line-citation off-by-one for `lines_builder.py`.** Plan §Resource Intelligence line 19 says "line 44 consumes `end_buoy_name`." Line 44 is a comment; the actual consumption is line 45. Not load-bearing but violates the plan's own retrieval-skepticism stance.
- **[MINOR] Acceptance Criterion line 260 has no artifact to verify.** `uv run pytest digitalmodel/tests/.../test_registry*.py passes (approach A only)` — no `test_registry_*.py` file is listed in Approach A's §Files-to-Change. The TDD row `test_registry_allows_multiple_slots_per_output (approach A only)` (line 247) never gets a home. Orphan acceptance criterion.
- **[MINOR] Open question at §Risks line 327 ("external manifest references to `08_buoys.yml`") is unanswered and gates Approach A.** The plan flags but does not perform the grep. If the user selects Approach A, the plan is under-scoped: the grep must happen before implementation, not during review. Either move this to a pre-implementation checklist item or do it now.
- **[MINOR] Plan's "rollers → tugs → BM → end_buoy" ordering claim in Risks §line 317 is incomplete.** Current emission (per `buoys_builder.py:84–113`) is `rollers → tugs → BM → end_buoy` in `6DBuoys`, plus `mid_pipe` as sole entry in `3DBuoys`. Mid-pipe isn't in the 6D list, so the Risks line reads correctly but the TDD test `test_output_ordering_preserved` (line 244) should explicitly assert both lists' ordering, not just the 4-element 6D sequence.

### codex

(no findings unique to this provider)

### gemini

(no findings unique to this provider)

