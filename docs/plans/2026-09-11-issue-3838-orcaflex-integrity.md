# Plan for #3838: three verified OrcaFlex model-building integrity defects

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-09-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3838
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-09-11-plan-3838-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/post_validator.py` — `_check_duplicate_names_from_files()` at line 538 walks generated files and reports duplicate object names within a section. It is the correct host for the new collection-key check.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/__init__.py` — `ModularModelGenerator.generate()` writes `includes/*.yml` in builder-registry order and composes `master.yml` from `- includefile:` entries. This is the emission point the check must gate.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/orcaflex_analysis_components.py:354` — run status is gated by a whitelist `['Reset', 'InStaticState', 'SimulationStopped']`, which correctly excludes the unstable state.
- Found: `digitalmodel/src/digitalmodel/solvers/smoke/probes.py:90` — raises unless dynamics is complete and state is `SimulationStopped`.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/post_validator.py:31` — `_OBJECT_SECTIONS` enumerates the OrcaFlex collection keys (`LineTypes`, `VesselTypes`, `Vessels`, `Lines`, `6DBuoys`, `3DBuoys`, …). This, or `schema/generic.py:298` `SECTION_REGISTRY`, is the authority for the key set. `BuilderRegistry.register()` keys on **output file name**, not collection key (`builders/registry.py:27`, `:58`), and cannot supply it.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/aggregator.py:82` — `orcaflex_version` is extracted from the model and emitted in report sections at `reporting/section_builders/analysis_setup.py:30`. A version **is** therefore recorded on the reporting surface.
- Gap: no call to `OrcFxAPIConfig.setLibPath()` anywhere under `solvers/`, so the version is observed rather than selected, and the resolved library path is recorded nowhere.
- Gap: `OrcFxAPI` is imported at module scope in several modules under `solvers/orcaflex`, including `reporting/extractors/aggregator.py:9`, `schematic_capture.py:46`, `run_to_sim.py:17` and `pipeline_schematic.py:26`. Any of these imported first defeats a later `setLibPath()` for the life of the process.
- Gap: `digitalmodel/src/digitalmodel/solvers/orcaflex/orcaflex_utilities.py:600-601` reads `simulationComplete` and the state name without an evident gate on either.

### Standards

Not applicable. This issue concerns solver-interface correctness, not a standards-derived constant. No `Citation` sidecar is required under `.claude/rules/calc-citation-contract.md`, since no standards-derived numeric constant is introduced.

### LLM Wiki pages consulted

No relevant wiki pages. The defects are properties of the OrcaFlex text-data-file format and the OrcFxAPI binding, documented by the vendor rather than by this ecosystem's wiki.

### Documents consulted

- `_coordination/standard-orcaflex-run-etiquette-2026-09-10` — section 1 scopes that standard to execution and states it does not govern model construction. This plan occupies the complementary surface and does not overlap it.
- Orcina webhelp, *Text data files: Examples of setting data* — states that a list of `- Name:` entries replaces a collection whereas a name-keyed mapping patches it.
- Orcina webhelp, *Python interface: Installation* — states that `OrcFxAPI` uses the OrcaFlex version with the highest version number unless `OrcFxAPIConfig.setLibPath()` is called before import.
- Orcina webhelp, *C_RunSimulation2* — states that an unstable simulation returns `stOK` while setting the model to `msSimulationStoppedUnstable`.
- Related issue #1592 (CLOSED) — OrcaWave to OrcaFlex handoff; prior art for vessel-type generation, not for these defects.

### Gaps identified

- No check exists that any OrcaFlex collection key is emitted in list style by more than one includefile composed into the same master file.
- No mechanism exists to select or record the OrcaFlex version used by a run.
- No enumeration exists of the code paths that complete a simulation, so run-state gating coverage is unknown.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-09-11 via `gh issue list`):
- `#3838` — OPEN — fix(digitalmodel/orcaflex): three verified model-building integrity defects with silent failure modes
- `#1592` — CLOSED — Automate OrcaWave → OrcaFlex handoff: RAO extraction → vessel type generation

**File existence** (verified 2026-09-11):
- EXISTS: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/post_validator.py`
- EXISTS: `digitalmodel/docs/domains/orcaflex/templates/mooring_systems/calm_buoy/includes/05_line_types.yml`
- EXISTS: `digitalmodel/docs/domains/orcaflex/templates/mooring_systems/calm_buoy/includes/08_buoys.yml`
- MISSING (new — this plan creates): a test module covering collection-key collision

**Line excerpts** — generated includefile, list style:

```
LineTypes:
  # Mooring chain - 84mm R4 studless
  - Name: Chain_84mm_R4
    Category: General
    OD: 0.084
```

```
6DBuoys:
  - Name: CALM Buoy
    BuoyType: Spar buoy
```

**Gap proofs**:
- `grep -rn "setLibPath\|OrcFxAPIConfig" digitalmodel/src/digitalmodel/solvers` → no matches → confirms no version pinning exists.

**Reproduction proofs**:

Defect 3 rests on a vendor-documented API behaviour and on an enumeration, both verified:

```
$ python -c "import OrcFxAPI; print(sorted(m for m in dir(OrcFxAPI.ModelState) if not m.startswith('_')))"
['CalculatingStatics', 'InStaticState', 'Reset', 'RunningSimulation',
 'SimulationStopped', 'SimulationStoppedUnstable', ...]
```

- Reproduced at: 2026-09-11
- Failure mode observed matches issue claim: **PARTIAL**. `SimulationStoppedUnstable` exists and the whitelist pattern excludes it, so the guard is sound where applied. Defect 3 is therefore scoped as an audit of coverage, not as a repair of a known-broken gate. Defects 1 and 2 are structural absences proven by the gap proofs above and require no runtime reproduction.

Distinct sources consulted: 5 (issue body, repo code, run-etiquette standard, Orcina webhelp, issue #1592). Minimum 3 met.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-09-11-issue-3838-orcaflex-integrity.md |
| Tests | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_collection_collision.py` |
| Tests | `digitalmodel/tests/solvers/orcaflex/test_solver_version_record.py` |
| Implementation | `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/post_validator.py` |
| Implementation | `digitalmodel/src/digitalmodel/solvers/orcaflex/orcaflex_version.py` |
| Audit record | this plan, section "Run-path audit" |
| Plan review — Claude | scripts/review/results/2026-09-11-plan-3838-claude.md |
| Plan review — Codex | scripts/review/results/2026-09-11-plan-3838-codex.md |
| Plan review — Gemini | scripts/review/results/2026-09-11-plan-3838-gemini.md |

---

## Deliverable

A fail-closed collection-key collision check in the OrcaFlex generator, an explicit OrcaFlex version selection recorded with every run, and a completed enumeration of run paths showing where model-state gating applies.

---

## Pseudocode

```
function check_collection_collisions(master_path):
    # Takes a master file, not generator state, so it also validates a
    # hand-edited includes/ directory that never passed through the generator.
    # A list-style collection REPLACES the collection in OrcaFlex.
    # Two files writing the same key means the later one deletes the earlier.
    known_keys = _OBJECT_SECTIONS            # post_validator.py:31 — NOT BuilderRegistry,
                                             # which keys on output file name
    emitters = map from collection_key -> list of (file, style)
    for each file in includefiles composed by master_path, in composition order:
        parse YAML top level
        for each top-level key in known_keys:
            style = "list" if value is a sequence else "mapping"
            append (file, style) to emitters[key]
        for each top-level key NOT in known_keys:
            record as unrecognised           # surfaced, so an unknown key cannot pass silently

    for each key, entries in emitters:
        list_emitters = entries where style == "list"
        if count(list_emitters) > 1:
            raise ValidationError(
                key, list_emitters,
                "later file replaces the collection written by the earlier")
    # Mapping-style repeats are legitimate: they patch rather than replace.
```

```
# One facade owns the import. Direct `import OrcFxAPI` under solvers/orcaflex is
# banned, because a module-scope import anywhere defeats setLibPath for the whole
# process — see the gap list for the four modules that currently do this.
module orcaflex_api:                      # imports OrcFxAPI lazily, never at module scope
    _resolved = None

    function configure(requested_version or None):
        if OrcFxAPI already in sys.modules:
            raise ConfigurationError(naming the module that imported it first)
        if requested_version is not None:
            OrcFxAPIConfig.setLibPath(path for requested_version)
        _resolved = {
            "requested": requested_version,
            "resolved_lib_path": path the library actually loaded,
            "resolved_version": version string reported by the library,
        }

    function api():                       # every caller reaches OrcFxAPI through this
        if _resolved is None: configure(None)
        import OrcFxAPI; return OrcFxAPI

    function record(): return _resolved   # written into the run manifest by the caller
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/src/.../modular_generator/post_validator.py` | add collection-key collision check, fail closed |
| Create | `digitalmodel/tests/solvers/orcaflex/modular_generator/test_collection_collision.py` | TDD coverage for the check |
| Create | `digitalmodel/src/digitalmodel/solvers/orcaflex/orcaflex_version.py` | version selection and recording |
| Create | `digitalmodel/tests/solvers/orcaflex/test_solver_version_record.py` | TDD coverage for recording |
| Modify | `digitalmodel/src/.../solvers/orcaflex/orcaflex_utilities.py` | gate on model state where the audit shows a gap |
| Update | docs/plans/README.md | add this plan to the index |

---

## TDD Test List

| # | Test | Asserts | Defect |
|---|---|---|---|
| 1 | two includefiles emit `LineTypes:` in list style | raises, names both files and the key | 1 |
| 2 | two includefiles emit `LineTypes:`, one list one mapping | passes — a mapping patches, it does not replace | 1 |
| 3 | two includefiles emit the same key in mapping style | passes | 1 |
| 4 | one includefile per collection, several collections | passes — the current generator output must remain valid | 1 |
| 5 | collision in a file not referenced by the master | passes — only composed files are in scope | 1 |
| 6 | the existing CALM-buoy template set | passes — proves no regression against real output | 1 |
| 7 | a top-level key outside `_OBJECT_SECTIONS` | reported as unrecognised, not ignored | 1 |
| 8 | version requested and available | record carries requested, resolved path and resolved version | 2 |
| 9 | no version requested | record still carries the resolved path and version | 2 |
| 10 | version requested but absent | raises with the requested version in the message | 2 |
| 11 | `configure()` called after `OrcFxAPI` is already imported | raises, naming the earlier importer | 2 |
| 12 | subprocess: facade configured first, then a module that imports `OrcFxAPI` at module scope | selected path is in force | 2 |
| 13 | run completing in `SimulationStoppedUnstable` | the gated path rejects it | 3 |
| 14 | run completing in `SimulationStopped` | the gated path accepts it | 3 |

Tests 8 to 10 require OrcFxAPI and carry the existing `solver` marker. Tests 11 and 12 run in a fresh subprocess, because import state is process-global and cannot be reset within a pytest session. Tests 13 and 14 are exercised against a stubbed model state so they run without a licence.

---

## Run-path audit

Acceptance criterion 3 requires an enumeration rather than a repair. The **inventory is derived mechanically, not listed by hand**, because a hand-written list was demonstrably incomplete: the first draft named five paths and a direct search found at least six more.

Inventory command, whose output is committed with the audit:

```
grep -rn "CalculateStatics()\|RunSimulation(\|C_RunSimulation" digitalmodel/src/digitalmodel
```

Every match is classified. Paths known at planning time:

| Path | Gates on state |
|---|---|
| `orcaflex_analysis_components.py:354` | yes, whitelist |
| `solvers/smoke/probes.py:90` | yes, raises |
| `core/model_interface.py` | tracks an internal state enum, not the OrcFxAPI one — to be assessed |
| `orcaflex_utilities.py:600-601` | records state, no evident gate |
| `modular_input_validation/level_2_orcaflex.py:190` | enumerates states; unstable member not handled |
| `run_to_sim.py:121` | to be classified |
| `orcaflex_custom_analysis.py:167` | to be classified |
| `orcaflex_iterative_runs.py:162` | to be classified |
| `orcaflex_parallel_analysis.py:108` | to be classified |
| `orcaflex_optimized_parallel.py:146` | to be classified |
| `universal/universal_runner.py:435` | to be classified |

The audit is complete when every match in the committed inventory carries a verdict. A path recorded as intentionally ungated **must name the caller that performs the gating instead**; "intentional" without a named gating caller is not an acceptable verdict.

### Committed inventory (raw)

Produced 2026-09-11 against `digitalmodel` at `90bcff85` — the tree the audit was
performed on, before any change from this plan. `main` advanced to `41f874f0`
during implementation; the inventory is byte-identical at both commits
(`git grep ... 90bcff85` vs `... 41f874f0`, `Compare-Object` empty), so the
classification below applies unchanged. Paths are relative to
`digitalmodel/src/digitalmodel/`. 38 matches.

```
solvers/orcaflex/OrcaFlexAnalysis.py:63:#     model.CalculateStatics()
solvers/orcaflex/OrcaFlexAnalysis.py:64:#     model.RunSimulation()
solvers/orcaflex/core/model_interface.py:382:                self._model.CalculateStatics()
solvers/orcaflex/core/model_interface.py:474:                self._model.RunSimulation()
solvers/orcaflex/core/model_interface.py:662:    def RunSimulation(self) -> None:
solvers/orcaflex/modular_input_validation/level_2_orcaflex.py:244:            model.CalculateStatics()
solvers/orcaflex/mooring_tension_iteration/orcaflex_interface.py:335:        self.model.CalculateStatics()
solvers/orcaflex/opp_visualization.py:80:                model.CalculateStatics()
solvers/orcaflex/opp_visualization.py:85:            #     combined_model.CalculateStatics()
solvers/orcaflex/opp_visualization.py:209:            model.CalculateStatics()
solvers/orcaflex/orcaflex_analysis_components.py:74:                    model.RunSimulation()
solvers/orcaflex/orcaflex_analysis_components.py:76:                    model.CalculateStatics()
solvers/orcaflex/orcaflex_custom_analysis.py:167:                model.RunSimulation()
solvers/orcaflex/orcaflex_custom_analysis.py:216:            model.CalculateStatics()
solvers/orcaflex/orcaflex_custom_analysis.py:229:            model.CalculateStatics()
solvers/orcaflex/orcaflex_custom_analysis.py:257:        model.CalculateStatics()
solvers/orcaflex/orcaflex_custom_analysis.py:296:            model.CalculateStatics()
solvers/orcaflex/orcaflex_iterative_runs.py:162:            model.RunSimulation()
solvers/orcaflex/orcaflex_modal_analysis.py:80:        model.CalculateStatics()
solvers/orcaflex/orcaflex_optimized_parallel.py:146:                    model.CalculateStatics()
solvers/orcaflex/orcaflex_optimized_parallel.py:151:                    model.RunSimulation()
solvers/orcaflex/orcaflex_optimized_parallel_v2.py:96:                model.CalculateStatics()
solvers/orcaflex/orcaflex_optimized_parallel_v2.py:101:                model.RunSimulation()
solvers/orcaflex/orcaflex_parallel_analysis.py:108:                model.CalculateStatics()
solvers/orcaflex/orcaflex_parallel_analysis.py:114:                model.RunSimulation()
solvers/orcaflex/orcaflex_utilities.py:125:        model.RunSimulation()
solvers/orcaflex/pipeline_schematic.py:1559:            self._model.CalculateStatics()
solvers/orcaflex/run_to_sim.py:121:                model.CalculateStatics()
solvers/orcaflex/schematic_capture.py:97:        If True, call ``CalculateStatics()`` before capturing views.
solvers/orcaflex/schematic_capture.py:117:        model.CalculateStatics()
solvers/orcaflex/template_generator.py:552:                    model.CalculateStatics()
solvers/orcaflex/time_trace_processor.py:144:            model.RunSimulation()
solvers/orcaflex/universal/README.md:41:# Note: Dynamic analysis runs the full OrcaFlex simulation using model.RunSimulation()
solvers/orcaflex/universal/batch_processor.py:296:                model.CalculateStatics()
solvers/orcaflex/universal/universal_runner.py:435:                    model.CalculateStatics()
solvers/orcaflex/universal/universal_runner.py:440:                    model.RunSimulation()
solvers/smoke/probes.py:118:        model.CalculateStatics()
solvers/smoke/probes.py:127:        model.RunSimulation()
```

### Classification

Every one of the 38 matches carries a verdict. `Verdict at 90bcff85` is the state
found; `Disposition` is what this plan's implementation does about it. The gate is
`digitalmodel.solvers.orcaflex.run_state.check_statics` / `check_simulation`.

| Match | Kind | Verdict at `90bcff85` | Disposition |
|---|---|---|---|
| `OrcaFlexAnalysis.py:63,64` | commented-out example | not a call site | NOT APPLICABLE |
| `core/model_interface.py:382` | statics | UNGATED — comment asserted "OrcaFlex throws if not converged" and set `converged = True` unconditionally | GATED — `check_statics` |
| `core/model_interface.py:474` | dynamics | UNGATED | GATED — `check_simulation` |
| `core/model_interface.py:662` | `def RunSimulation` on `MockOrcaFlexModel` | a definition on the mock, not a call | NOT APPLICABLE |
| `modular_input_validation/level_2_orcaflex.py:244` | statics | UNGATED | REPORTED — this function's contract is to return warnings, not to raise, so a non-static end state is appended as a warning |
| `mooring_tension_iteration/orcaflex_interface.py:335` | statics | UNGATED | GATED — `check_statics` |
| `opp_visualization.py:80` | statics | UNGATED | GATED — `check_statics` |
| `opp_visualization.py:85` | commented-out | not a call site | NOT APPLICABLE |
| `opp_visualization.py:209` | statics | UNGATED | GATED — `check_statics` |
| `orcaflex_analysis_components.py:74` | dynamics | UNGATED — logged "Run simulation successful" unconditionally | GATED — `check_simulation` |
| `orcaflex_analysis_components.py:76` | statics | UNGATED | GATED — `check_statics` |
| `orcaflex_custom_analysis.py:167` | dynamics | UNGATED | GATED — `check_simulation` |
| `orcaflex_custom_analysis.py:216` | statics | UNGATED (inside `try`/bare `except` that sets the FAIL flag) | GATED — `check_statics`; the existing except turns it into the FAIL branch |
| `orcaflex_custom_analysis.py:229` | statics | UNGATED | GATED — `check_statics` |
| `orcaflex_custom_analysis.py:257` | statics (iteration seed) | UNGATED | GATED — `check_statics` |
| `orcaflex_custom_analysis.py:296` | statics (per iteration) | UNGATED | GATED — `check_statics` |
| `orcaflex_iterative_runs.py:162` | dynamics | UNGATED | GATED — `check_simulation` |
| `orcaflex_modal_analysis.py:80` | statics | UNGATED | GATED — `check_statics` |
| `orcaflex_optimized_parallel.py:146` | statics | UNGATED | GATED — `check_statics` |
| `orcaflex_optimized_parallel.py:151` | dynamics | UNGATED | GATED — `check_simulation` |
| `orcaflex_optimized_parallel_v2.py:96` | statics | UNGATED | GATED — `check_statics` |
| `orcaflex_optimized_parallel_v2.py:101` | dynamics | UNGATED | GATED — `check_simulation` |
| `orcaflex_parallel_analysis.py:108` | statics | UNGATED — set `result['static_complete'] = True` on return | GATED — `check_statics` |
| `orcaflex_parallel_analysis.py:114` | dynamics | UNGATED — set `result['dynamic_complete'] = True` on return | GATED — `check_simulation` |
| `orcaflex_utilities.py:125` | dynamics | UNGATED — returned `status_flag = True` on return | GATED — `check_simulation` |
| `pipeline_schematic.py:1559` | statics | UNGATED | GATED — `check_statics` |
| `run_to_sim.py:121` | statics | UNGATED — logged "Successfully created" on return | GATED — `check_statics` |
| `schematic_capture.py:97` | docstring | not a call site | NOT APPLICABLE |
| `schematic_capture.py:117` | statics | UNGATED | GATED — `check_statics` |
| `template_generator.py:552` | statics | PARTIAL — `statics_converged` was set from the absence of an exception | GATED — `check_statics` inside the same `try`, so the state now decides `statics_converged` |
| `time_trace_processor.py:144` | dynamics | UNGATED | GATED — `check_simulation` |
| `universal/README.md:41` | documentation | not a call site | NOT APPLICABLE |
| `universal/batch_processor.py:296` | statics | UNGATED | GATED — `check_statics` |
| `universal/universal_runner.py:435` | statics | UNGATED | GATED — `check_statics` |
| `universal/universal_runner.py:440` | dynamics | UNGATED | GATED — `check_simulation` |
| `solvers/smoke/probes.py:118` | statics | INTENTIONALLY UNGATED at the call | UNCHANGED — gated by the caller `_solve_orcaflex`, which calls `_completed(model, api, detail)` at `probes.py:129`; `_completed` (`probes.py:86-91`) requires `simulationComplete` and `state == SimulationStopped` for the probe as a whole |
| `solvers/smoke/probes.py:127` | dynamics | ALREADY GATED | UNCHANGED — `_completed` at `probes.py:129`, raising at `probes.py:90-91` |

### Two gaps the inventory does not surface

The inventory greps *run* calls. Two paths read a run state without running one,
and both were named in the Resource Intelligence section:

- `orcaflex_analysis_components.py:354` — the whitelist this plan cited as "correct
  where applied" is in fact **dead twice over**, and neither fault is visible from
  the line alone:
  1. It compared `str(model.state)` against member *names*. `OrcFxAPI.ModelState`
     is an `IntEnum`, and from Python 3.11 `str()` of an `IntEnum` member is its
     integer value — `str(ModelState.SimulationStopped)` is `'4'`. The comparison
     matched nothing, so every loaded simulation was discarded.
  2. It sat after `from common.data import PandasChainedAssignent` inside a
     `try:` whose `except Exception: pass` swallowed everything. `common` does not
     resolve in this environment, so control never reached the whitelist at all
     and the loaded model was returned ungated.
  FIXED: the state is resolved by member name through `run_state.state_name`, the
  gate runs first, and the bookkeeping import is in its own narrowed `try`.
- `orcaflex_utilities.py:600-601` — state recorded, no gate. FIXED: a model whose
  state is not a completed-solve state is no longer returned for post-processing.
  The same edit fixes a latent `UnboundLocalError`: `simulation_complete`,
  `run_status`, `start_time`, `stop_time` and `current_time` were assigned only
  inside the `try`, so any load failure raised while building the return dict.

### Deferred

- Nothing in the inventory falls outside the OrcaFlex solver package except
  `solvers/smoke/probes.py`, which was already gated and is unchanged.
- Acceptance criterion 2's second clause — *no direct module-scope
  `import OrcFxAPI` under `solvers/orcaflex`* — is **partially met**. The
  operative property is enforced: nothing reachable from
  `import digitalmodel.solvers.orcaflex` imports the binding, so `configure()` can
  still select a library. Nine modules were converted to the facade
  (`orcaflex_objects`, `opp_range_graph`, `opp_time_series`, `opp_visualization`,
  `orcaflex_utilities`, `run_to_sim`, `pipeline_schematic`, `schematic_capture`,
  `core/model_interface`). Nineteen remain, none of them on that import path; they
  are held by a ratchet test that lets the set shrink but not grow
  (`KNOWN_MODULE_SCOPE_IMPORTERS` in
  `tests/solvers/orcaflex/test_solver_version_record.py`). The seven
  `reporting/extractors/*` modules are the bulk of the remainder and carry an
  `if ofx is None: raise ImportError` availability contract with its own test
  surface in `tests/solvers/orcaflex/reporting/test_extractors.py`; converting
  them is a separate, separately-tested change.

---

## Acceptance Criteria

1. The collision check fails closed on a list-style collection key emitted by more than one composed includefile, naming the key and both files. It is callable against any master file, so it also covers a hand-edited `includes/` directory that never passed through the generator.
2. The OrcaFlex version is selected explicitly where requested, and the resolved library path and version are recorded for every run. Direct module-scope `import OrcFxAPI` no longer occurs under `solvers/orcaflex`; all access goes through the facade.
3. The grep-derived inventory of simulation-completing paths is committed, and every match in it carries a gating verdict. Each ungated path is corrected, or recorded as intentional **naming the caller that gates instead**.
4. The existing generator test suite passes unchanged, and the CALM-buoy template set passes the new check.

---

## Adversarial Review Summary

| Wave | Reviewer | Verdict | MAJOR | MINOR |
|---|---|---|---|---|
| r1 | Claude, inline | APPROVE-WITH-CHANGES | 2 | 4 |
| r2 | Codex | REJECT | 3 | 2 |
| r2 | Gemini / agy | UNAVAILABLE — not installed on this host | – | – |

T2 scope requires two providers; Claude and Codex satisfy it, and the Gemini lane is recorded UNAVAILABLE per the existing `scripts/review/results/` convention rather than blocking.

Revisions made in r3, applied inline without a further review dispatch:

- The collection-key source was changed from `BuilderRegistry` to `_OBJECT_SECTIONS`. Codex established that the registry keys on output file name and cannot supply collection keys; the original approach would not have worked.
- The claim that no version is recorded anywhere was **withdrawn as overbroad**. `aggregator.py:82` extracts `orcaflex_version` and `analysis_setup.py:30` emits it. What is absent is selection and the resolved library path, and the plan now says so.
- Version selection became an import facade with a ban on direct module-scope imports, after Codex identified four existing module-scope `import OrcFxAPI` sites that would defeat `setLibPath` under pytest collection.
- The run-path audit input became a committed grep inventory. The hand-written list held five paths; a direct search found at least six more.
- The collision check was made callable against an arbitrary master file, so it covers hand-edited includefiles — the case most likely to trigger the defect and the one the original placement missed.
- Unrecognised top-level keys are now surfaced rather than ignored.

---

## Risks

| Risk | Mitigation |
|---|---|
| The new check rejects legitimate existing output | Test 6 runs it against the committed template set before the check is enabled. Test 6 is meaningless without test 1, which proves the check fires at all — neither may be deleted without the other |
| Collection-key recognition is incomplete, so a collision is missed | Take the key set from `_OBJECT_SECTIONS` (`post_validator.py:31`), which is the existing authority; surface any unrecognised top-level key rather than ignoring it, so an unknown key cannot pass silently |
| `setLibPath` must run before `OrcFxAPI` is imported, and four modules import it at module scope | A facade owns the import, direct imports under `solvers/orcaflex` are banned, `configure()` raises if `OrcFxAPI` is already in `sys.modules`, and the ordering test runs in a fresh subprocess |
| The audit finds many ungated paths and the issue grows without bound | The inventory is grep-derived and committed, so its size is known before implementation starts. Corrections outside the OrcaFlex solver package are recorded and deferred to a follow-on issue |

---

## Out of Scope

Generator consolidation, rainflow counting, and any change to the builder set. Those belong to separate issues.
