# Disagreement report — plan #279 (2026-04-24)

## Verdicts

| Provider | Verdict |
|---|---|
| adversarial | **REQUEST_CHANGES** — 3 MAJOR, 5 MINOR. Plan cannot ship as-is. |
| claude | MAJOR |
| codex | UNAVAILABLE (codex CLI failed, rc=2: error: unexpected argument '--no-interactive' found    tip: to pass '--no-interactive' as a value, use '-- --no-interactive'  Usage: codex exec [OPTIONS] [PROMPT]        codex exec [OPTIONS] <COMMAND>) |
| gemini | UNAVAILABLE (gemini CLI failed, rc=55: [31mGemini CLI is not running in a trusted directory. To proceed, either use `--skip-trust`, set the `GEMINI_CLI_TRUST_WORKSPACE=true` environment variable, or trust this directory in interactive mod) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### adversarial

(no findings unique to this provider)

### claude

- **Dispatch pseudocode is a refactor masquerading as an addition.** Plan §Pseudocode lines 141-147 presents dispatch as `renderer_map = {"pipeline": PipelineRenderer, ... "vessel": VesselRenderer}`. Actual `report_generator.py` lines 60-74 uses an `if stype == "riser": … elif … else: BaseRenderer` chain — no map exists. "Files to Change" row for `report_generator.py` (line 182) says "add `"vessel"` to dispatch map." The implementer will either (a) add an `elif` (keeping the idiom) or (b) rewrite the whole block to a dict (behavior change — loses the ability to pass per-branch kwargs to each renderer constructor). Plan must commit to one form and state why.
- **FPSO snapshot baseline will silently regress.** `tests/solvers/orcaflex/reporting/test_fpso_fixture_snapshot.py:13-25` already asserts `test_fpso_snapshot_contains_expected_structural_markers` and a byte-level snapshot match for `fpso_turret`. FPSO is a vessel. Today that report is produced by the `else` branch at `report_generator.py:73-74` (BaseRenderer fallback). Acceptance Criterion #3 (plan line 226) promises "16-section vessel report without `BaseRenderer` fallback" — the moment the new `VesselRenderer` is wired, the FPSO snapshot diverges and the existing `test_fpso_report_matches_snapshot` must be re-baselined. The plan does not mention this and does not state whether `fpso_turret` becomes the `test_per_type_snapshot_vessel` fixture or remains independent. Silent-break on a committed baseline.
- **"Gap #8" is already wired — not a gap.** Plan §Gaps identified line 52 ("wiring audit: `boundary_conditions_extractor.py` … import path into `aggregator.py` unverified") and Files-to-Change line 183 ("verify `boundary_conditions_extractor` is wired") assert uncertainty. Verified: `extractors/aggregator.py:24` imports `extract_boundary_conditions` and calls it at line 68 via `_safe_extract`. The plan will send an implementer to do verification work that is already satisfied; the gap should be removed from the gap list or converted to a one-line "confirmed wired" note.
- **Vessel-as-primary vs. vessel-as-subcomponent is unresolved.** `models/other_structures.py:20` ships `vessels: List[dict]` and `models/boundary_conditions.py:8` uses `"Vessel"` as a connection `type`. A mooring or riser report already carries vessel data through `other_structures`. The new `structure_type="vessel"` path introduces a second representation. Plan is silent on the data contract: do `VesselExtract.hull` fields propagate into `OtherStructures.vessels[]` when the vessel appears inside a mooring report? If not, the same vessel renders different fields depending on which report surfaces it. This needs explicit resolution in §Pseudocode or §Risks, not a renderer in isolation.
- **`fixtures/` root directory does not exist; scope is larger than plan states.** Artifact Map line 90/188 lists `digitalmodel/tests/solvers/orcaflex/reporting/fixtures/{pipeline,riser,jumper,installation,vessel}/`. `ls` confirms the `fixtures/` directory is absent. Existing snapshot tests load fixtures via `fixture_helpers.py` / `snapshot_helpers.py` (direct file references inside the test module), not a `fixtures/` subtree. Implementer must (a) create the directory, (b) refactor `fixture_helpers.py` to index by structure type, (c) possibly migrate the existing `fpso_turret` and mooring fixtures into the new subtree. That is at least a T2 task on its own; the plan treats it as a single "Create" row.
- **Extractor count inconsistency.** Plan §Existing repo code line 18 states "7 OrcFxAPI live adapters" then enumerates 8 files (`aggregator.py, boundary_conditions_extractor.py, geometry_extractor.py, loads_extractor.py, materials_extractor.py, mesh_extractor.py, mooring_extractor.py, results_extractor.py`). Actual count on disk is 8 non-`__init__` files. The "7" is wrong.
- **`css.py` omitted from resource inventory.** `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/css.py` (213 lines) is the likely location of the `#2c3e50` theme the plan later compares against Bootstrap `#0d6efd` at `builder.py:31`. Plan's inventory lists every other top-level file in the package but not this one, so subsequent claims about where vessel styling belongs are unsupported.
- **Existing `test_report_generator.py` ignored.** The 166-line `tests/solvers/orcaflex/reporting/test_report_generator.py` already tests dispatch (`test_generate_report_invalid_structure_type` at line 112). Plan creates a new `test_vessel_renderer.py` with `test_vessel_renderer_dispatched` (TDD line 202). Dispatch-coverage duplication or drift. Plan should either extend the existing file or state why a new one is needed.
- **Section count off by one.** §Existing repo code line 16: "17 section modules matching the canonical 16-section FEA layout + utils.py." 17 modules for 16 sections is not self-consistent; if one (e.g., `header.py`) is chrome-not-section the plan should say so. Otherwise the "canonical 16-section" label is wrong.
- **TRADEOFF-gated acceptance criteria block implementation start.** Acceptance #7, #8 (plan lines 230-231) hinge on `(if TRADEOFF choice = deprecate)` and `structure_types/ disposition applied per TRADEOFF`. Three TRADEOFFs remain open (lines 262-273). Complexity is labeled T2 with "no new architectural layer" — but none of the implementation can start until the user resolves the TRADEOFFs, and two of the three (Legacy Option B; Vessel Option B) are explicitly called out as upgrading the plan to T2-large. The plan should reorder: TRADEOFFs resolved first, complexity re-stated, then acceptance locked.
- **Gemini NO_OUTPUT × 14 makes the review gate un-shippable as written.** §Risks line 258 acknowledges Gemini NO_OUTPUT'd 14 times on spec v1.13. §Adversarial Review Summary table (lines 243-245) requires a Gemini row filled in with a verdict. If Gemini NO_OUTPUTs on this plan too, the table cannot be completed and the plan cannot move off draft. Plan must specify an explicit fallback ("Gemini NO_OUTPUT = review attempted, proceed with Claude+Codex consensus") or the review step is an indefinite block.
- **Deprecation comment contradicts itself.** Pseudocode lines 164-172: header says "Legacy deprecation (non-removal, single release)" but the warning body says "will be removed in v<N+2>". "Non-removal" and "removed in v<N+2>" are opposites. Pick one and align the Acceptance Criterion #7 wording.

### codex

(no findings unique to this provider)

### gemini

(no findings unique to this provider)

