# Disagreement report — plan #515 (2026-04-24)

## Verdicts

| Provider | Verdict |
|---|---|
| adversarial | `MINOR` |
| claude | **MAJOR** |
| codex | UNAVAILABLE (codex CLI failed, rc=2: error: unexpected argument '--no-interactive' found    tip: to pass '--no-interactive' as a value, use '-- --no-interactive'  Usage: codex exec [OPTIONS] [PROMPT]        codex exec [OPTIONS] <COMMAND>) |
| gemini | UNAVAILABLE (gemini CLI failed, rc=55: [31mGemini CLI is not running in a trusted directory. To proceed, either use `--skip-trust`, set the `GEMINI_CLI_TRUST_WORKSPACE=true` environment variable, or trust this directory in interactive mod) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### adversarial

(no findings unique to this provider)

### claude

- **Count error: `_SKIP_GENERAL_KEYS` is 24 keys, not 34** (plan §"Existing repo code" and §"Evidence" both claim 34). Counted directly in `generic_builder.py:115-149`: 12 Default*View*/Shaded*, 2 drawing (BackgroundColour, WireframeMode), 5 sea-surface rendering, 1 ModelState, 1 TemperatureUnits, 1 ImplicitVariableMaxTimeStep, 2 DefaultShaded* = 24. The plan's "34" propagates into the TDD row `test_skip_general_keys_documented_in_taxonomy` ("all 34 keys present in taxonomy; 0 unlisted") — this acceptance criterion will be false as authored.
- **Count error: `EXTRACTION_MAP` is 16 entries, not 17** (plan §"Existing repo code" and §"Line excerpts" both assert 17; §"Gaps" #7 says "hardcoded at 17"). Verified by `awk '/^EXTRACTION_MAP/,/^]/'` count and by inspection of `modular_to_spec.py:20-43`. In addition, the plan's claim that confidence is `extracted_count/17` is wrong: `modular_to_spec.py:46` defines `_TOTAL_EXTRACTABLE = len(EXTRACTION_MAP)` — the denominator is computed dynamically, not hardcoded to 17. The plan's "a01 confidence 0.88" figure is almost certainly carried over from a stale (17-entry) version of the map.
- **Count error: `_DEFAULTS` is 29 entries, not 21** (plan §"Existing repo code" claims "21 hardcoded env defaults"; Approach-A acceptance criterion asserts "each of the 21 `_DEFAULTS`" and "licensed-win-1 test ... all 21 match"). Verified by reading `environment_builder.py:49-79`. The OQ-3 test specification that enumerates "21 defaults" is therefore authored against a fiction.
- **Pre-failing TDD: `test_allowed_diff_props_superset_of_skip_general` will fail on day one.** Plan asserts `ALLOWED_DIFF_PROPS ⊇ _SKIP_GENERAL_KEYS`. Grep confirmed that `ImplicitVariableMaxTimeStep` appears in `generic_builder.py` (`_SKIP_GENERAL_KEYS`) but does NOT appear anywhere in `semantic_validate.py`. The superset relationship does not hold today. The plan presents this test as drift-detection for a property that already holds; it is actually a divergence-exposure test, and the plan should either (a) pre-reconcile the two lists before adding the test, or (b) narrate the expected first-run failure as scope.
- **OQ-4 diagnosis disagrees with code.** Plan repeatedly says `values_equal()` produces "false-positive SIGNIFICANT diffs" for Yes↔true. Reading `semantic_validate.py:398-403`: when `type(mono_val) != type(mod_val)` and both are NOT numeric, the function returns `Significance.TYPE_MISMATCH`, not `Significance.SIGNIFICANT`. The proposed Approach-A patch still may be correct, but the *mechanism the plan claims to be fixing* is misidentified — any acceptance test that greps for "0 SIGNIFICANT diffs" on a bool-only fixture may already pass *before* the fix, because the miscounted diffs would be TYPE_MISMATCH in the current code. Plan needs to re-baseline the current behavior empirically before asserting what "fixed" looks like.
- **Line-range citation drift for `_WIND_SPEED_DORMANT`.** Plan §"Existing repo code" cites `environment_builder.py:49-159` as containing `_WIND_SPEED_DORMANT`. Actual location: line 160 — one line past the cited range. `_WIND_TYPE_PROPS` (lines 123-157) is not mentioned by the plan at all, though it is the mechanism that already handles the wind-type-dependent keys OQ-1 turns on. The plan's intel summary elided a relevant structure.
- **Incorrect type claim: `Significance` is NOT an `Enum`.** Plan §Pseudocode shows `class Significance(Enum): match | cosmetic | ...`. Actual at `semantic_validate.py:101-108` is a plain class with `str` constants (no `Enum` import in scope). If the reconciliation test parses taxonomy and compares against `Significance` members, `Significance.__members__` won't exist; `Significance.__dict__` iteration or a manual list is required. The plan's pseudocode would not compile as written.
- **Stale label claim.** Plan §"Evidence" lists `#515 — ... status:pending`. Live label set is `enhancement, cat:engineering, priority:high, route:B, status:plan-approved`. `status:pending` is not present; `status:plan-approved` is. If the plan was authored after the label advanced, the Evidence block is out of date; if before, the plan itself predates the approval gate and should re-verify.
- **`ALLOWED_DIFF_PROPS` "50+" is ≤50.** Plan §"Existing repo code" calls it "50+". Inspection of `semantic_validate.py:117-178` shows exactly 50 entries. Not wrong enough to block, but it reinforces the retrieval-hygiene concern — several counts in the plan are slightly above actuals. This suggests the intel pod's numbers were rounded or copied imprecisely throughout.
- **Registry pseudocode uses `a01_catenary_riser` as L1 but makes an unverified claim about `c03_fpso` from #2454.** Plan §Pseudocode (`MODEL_CLAIM_REGISTRY.yaml` example) hard-codes `test_enforcing: tests/.../test_c03_fpso_semantic.py  # from #2454`. The plan's Artifact Map and Files-to-Change rows do not list #2454's test path as existing; the sibling plan file (`docs/plans/2026-04-23-issue-2454-c03-fpso-semantic-proof.md`) exists, but that does not imply the test module has landed. Acceptance criterion `test_model_claim_registry_tests_exist` will fail if the #2454 test is not yet merged. Plan does not address ordering-dependency on #2454 execution.
- **Approach-A complexity estimate is conservative.** Plan rates Approach A as "T2-high (potentially T3)". Approach A touches `semantic_validate.py` (2108 lines), modifies `environment_builder.py`, adds a licensed-win-1 test, and amends `SEMANTIC_DIFF_TAXONOMY.md`. The OQ-4 patch is inside the diff engine that every prior per-family proof (#2454/2455/2456/2457) depends on; those proofs' verdicts may shift under re-run. The Risks section flags this ("may re-classify previous test-run verdicts") but the complexity rating does not reflect it. Approach A is T3, not T2-high, once re-baselining of four existing proofs is scoped in.
- **Cross-repo artifact placement not justified.** Plan targets `vamseeachanta/digitalmodel#515` (digitalmodel repo) yet stores review artifacts under `scripts/review/results/` in workspace-hub, and cross-references a workspace-hub plan (`docs/plans/2026-04-23-issue-2476-...`) as upstream approved work. Plan never states whether review artifacts should be pushed to digitalmodel or kept in workspace-hub, or how the link between the digitalmodel issue and the workspace-hub artifact is discoverable by reviewers browsing the issue. Needs an explicit sentence.

### codex

(no findings unique to this provider)

### gemini

(no findings unique to this provider)

