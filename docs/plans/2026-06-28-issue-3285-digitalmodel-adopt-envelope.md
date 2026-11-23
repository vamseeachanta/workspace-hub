# Plan for #3285: wf-api(digitalmodel) — adopt ResultEnvelope + result: descriptors + goldens (FFS, buckling, mooring, wall-thickness)

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3285
> **Epic:** https://github.com/vamseeachanta/workspace-hub/issues/3281
> **Depends on (hard, none owner-approved):** **#3307 (digitalmodel engine embed-port — the digitalmodel-fork mirror of #3297; MUST land first)** → #3282 (ResultEnvelope + `run_workflow` + `result:` descriptor + parameterized `code_version`) → #3295 (registry v2 superset; reserves the per-row `result:` slot). #3283 (determinism/golden harness) provides the `golden_workflow_test` template. **#3285 OWNS-CREATES** the `buckling-parametric` registry row + engine route + reference golden, runnable via a **bare in-repo digitalmodel id** (`run_workflow("buckling-parametric", …)`). **#3283 references that golden only as an ILLUSTRATIVE consumer example of its template — it does NOT commit it.** Any **CROSS-REPO** id form (`digitalmodel:buckling-parametric`) is **#3284-gated** (cross-repo resolver) and is NOT a dependency of #3285's in-repo golden. This plan CONSUMES the upstream contract exactly as specified and does **not** redesign it.
> **Client:** N/A — no wiki content touched (provenance cites existing wiki standard slugs read-only)
> **Lane:** lane:codex (heavy engineering code — engine routes, routers, golden capture)
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3285-claude.md | ...-codex.md | ...-gemini.md

---

## Upstream-contract dependency (read first — load-bearing)

This issue is the **first real consumer** of the deterministic-workflow-API contract. It rides on a re-locked, owner-confirmed (2026-06-28) contract. This plan builds on it **as specified** and flags the dependency rather than re-deriving:

- **#3307** (`wf-api(digitalmodel): engine embed-port — mirror #3297 for digitalmodel's own engine [prereq for #3285]`, OPEN, `status:needs-plan`, `lane:codex`): owns the **digitalmodel-fork** embed path. digitalmodel has its OWN forked engine + forked `ApplicationManager` usage; #3297 is scoped to the **assetutilities** engine and explicitly excludes the fork. #3307 MIRRORS #3297 in the fork: adds `engine(cfg=..., embed=True, root_folder=, log_to_file=False)`; honors the injected root for results + logs; **and rebases `cfg["_config_dir_path"]` to the injected root** so the config-relative routers (which write via `_config_dir_path`) land under the root rather than next to the input file. Default (no `root_folder`) byte-identical to today. **#3285 does NOT port the embed branch — it CONSUMES #3307's embed path** (this is the Wave-2 MAJOR-1 fix; see §Wave-2 revisions).
- **#3282** (`docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md`): owns `run_workflow(workflow_id, params=None, cfg=None) -> ResultEnvelope`. `ResultEnvelope` = **stdlib dataclass (NOT Pydantic)**: `{workflow_id, status, result, provenance{code_version{package_version, git_sha}, standard_revisions[], data_as_of, input_hash}, determinism{result_hash, reproducible}, confidence, warnings}`. `code_version(package_name="assetutilities")` is **PARAMETERIZED** — adopters pass their own package; digitalmodel calls `code_version("digitalmodel")`. `run_workflow` lives in assetutilities and drives **assetutilities'** engine; **per-repo engines provide their own runner reusing the shared `ResultEnvelope` + helpers.** Result LOCATION = registry `result:` descriptor `{kind: in_memory(key) | files(glob the injected root, content-hash sorted basenames, EXCLUDE the `save_cfg` `<file_name>.yml` dump)}`. **#3282 OWNS the determinism fields + the `result:` descriptor shape + `code_version`.** This plan consumes all three.
- **#3295** (`docs/plans/2026-06-28-issue-3295-registry-schema-v2-reconcile.md`): registry `schema_version: 2` additive superset; required top-level `invocation:`; `request_schema`/`response_schema` reserved; `result:` descriptor `{kind: in_memory|files}` reserved structured. **digitalmodel's registry is already `schema_version: 2`** with top-level `invocation:` (verified `workflows.yaml:9-10`), so this plan only *populates* the reserved per-row `result:` slot and *adds rows* — additive, no version bump.
- **#3283** (`docs/plans/2026-06-28-issue-3283-determinism-harness.md`): the golden harness — `golden_workflow_test(workflow_id, golden_path, …)` asserting against the REAL `run_workflow` emission, `stamp_provenance`, a volatile-field KEY-ALLOWLIST, and a refresh/re-sanction procedure, landing in `assetutilities/workflow_api/`. **#3283 CONSUMES `determinism.result_hash` (#3282-owned).** #3283 proves its own template with a **self-test on the assetutilities `data_exploration` bare id** — NOT on #3285's buckling golden. **#3285 OWNS-CREATES** the `buckling-parametric` registry row + engine route + reference golden (runnable via a **bare in-repo digitalmodel id**); #3283's plan carries this golden only as an **ILLUSTRATIVE consumer example** of `golden_workflow_test` and explicitly does NOT commit it (#3283 Artifact Map lists the buckling golden/test under "#3285 (NOT #3283)"). The illustrative example uses the **CROSS-REPO** id `digitalmodel:buckling-parametric`, which #3283 gates on **#3284** (resolver) + **#3285** (row/route/golden) + **#3307** (digitalmodel embed-port). #3285's own golden does not need #3284 — it runs the bare in-repo id.

**This issue cannot be implemented until #3307 lands (the digitalmodel embed path exists), #3282 lands (`run_workflow` + `ResultEnvelope` + `result:` descriptor exist), and #3295 lands (registry `result:` slot reserved).** #3283 lands in parallel; it is NOT a dependency of #3285 and #3285 does not depend back on #3283. #3285 OWNS the buckling reference golden that #3283 may later cite illustratively. Implementation is additionally gated behind USER approval of THIS plan.

---

## Wave-2 revisions (returned MAJOR — both addressed)

1. **MAJOR-1 — routers write outside the injected root; #3285 was wrongly porting the embed branch itself.** digitalmodel's config-relative routers (e.g. `path_resolver.py`, `inspection_planning.py`, `code_checks/workflow.py`) resolve output paths via `cfg["_config_dir_path"]` (engine.py:89 sets it to `dirname(inputfile)`; engine.py:117-118 propagates it). Under a naive embed, those routers would still write next to the input file, escaping the injected root. **Resolution:** this is now resolved by **#3307**, whose embed path **rebases `_config_dir_path` to the injected root**. #3285 **DEPENDS ON #3307 and consumes its embed path** — it no longer ports the embed branch into `engine.py`. The former "G0 (digitalmodel embed port)" deliverable is **removed from #3285's scope** and is now a hard prerequisite (#3307). #3285 retains only the three *additive engine routes* it owns — all NEW basenames that collide with nothing: `ffs` (FFS), `buckling_parametric` (buckling sweep), and `mooring_mbl` (mooring MBL pilot).
2. **MAJOR-2 — inverted buckling ownership.** The prior draft said "reuse #3283's buckling golden." That is backwards. **Resolution:** **#3285 OWNS-CREATES** the buckling registry row (`buckling-parametric`), the engine route (basename `buckling_parametric`), AND the reference golden, runnable via a **bare in-repo id**. **#3283 references it only as an ILLUSTRATIVE consumer example** of its template (it does not commit it); any cross-repo id form is #3284-gated. No "reuse from #3283" language remains.

## Wave-3 revisions (returned MAJOR (3) — all addressed)

1. **MAJOR-1 — descriptor-only new rows break the no-regression durable suite.** The Wave-2 draft added `ffs-metal-loss`/`buckling-parametric`/`mooring-design-mbl` as **descriptor-only** rows (`id`/`basename`/`title`/`result:` only). But `tests/workflows/test_durable_workflows.py::test_workflow_registry` parametrizes over **EVERY** registry row (`_load_registry()`) and, for `runtime: offline` rows (the default), unconditionally reads `workflow["input"]` (`:38`) and iterates `workflow["outputs"]` (`:48`). Three descriptor-only rows would raise `KeyError("input")`/`KeyError("outputs")` for three new parametrize cases — a direct regression, violating the "no regression to the CLI/durable path" AC. **Resolution (choice made — option A):** give each new row **FULL** `input:`/`outputs:`/`test:`/`runtime:` keys + committed example fixtures (`examples/workflows/<id>/input.yml` + produced `results/`), so they become **real CLI-exercised durable workflows** — exactly the existing registry convention (every row today carries those keys). The durable suite then *covers* the three new routes green (extra no-regression coverage) instead of breaking. (Rejected option B — relaxing the durable parametrization to skip rows lacking `input:` — because it weakens a shared test all other rows rely on and would let future descriptor-only rows silently escape CLI exercise.)
2. **MAJOR-2 — mooring basename collision.** The Wave-2 draft commandeered the existing `mooring` basename and "replaced the NotImplementedError". But `engine.py:377-384` signposts `mooring` for the **separate `subsea/mooring_analysis/` subsystem** (`cli.py`/`designer.py`/`fpso_workflow.py`/`catenary.py`/`orcaflex_generator.py` all present; the arm imports `subsea.mooring_analysis.cli` and raises to redirect there). Hijacking it would break that subsystem's reserved route. **Resolution:** the `orcaflex/mooring_design.py` MBL pilot (#2685) gets a **NEW basename `mooring_mbl`** (consistent with the new-basename choice already made for `ffs` and `buckling_parametric`). #3285 **adds a new `mooring_mbl` arm** and **leaves the existing `mooring` signpost untouched**.
3. **MAJOR-3 — over-claimed reciprocal #3283 consumer demo.** The Wave-2 draft framed #3283 as "depending back on" / running a "determinism self-proof" against #3285's buckling golden — a reciprocal/self-proof over-claim. #3283's own plan treats #3285's buckling golden as **ILLUSTRATIVE-only** (it does not commit it; its self-test uses the assetutilities `data_exploration` bare id) and gates the **cross-repo** `digitalmodel:buckling-parametric` demo on **#3284**. **Resolution:** framing aligned — **#3285 OWNS-CREATES** the buckling row/route/reference golden, runnable via a **bare in-repo id** (no #3284). #3283 merely **references** it illustratively. Any **cross-repo** id resolution is **#3284-gated**. The reciprocal "depends back" / "self-proof" language is removed throughout.

---

## Resource Intelligence Summary

### Existing repo code (verified 2026-06-28 against `/mnt/local-analysis/digitalmodel` @ local HEAD `ec8e694`)

**Engine-routability audit (the issue's first explicit ask — "Verify each workflow is engine-routable").** Result: of the four named targets, **only wall-thickness is currently engine-routable**; FFS, buckling, and mooring each have a distinct routing gap THIS issue closes.

| Target (scope-named module) | Engine basename | Routes to | Routable today? | Native result surface |
|---|---|---|---|---|
| **FFS** — `asset_integrity/assessment/ffs_coordinator.py` (`assess_component`, `FFSAssessmentResult.to_dict`) | *(none — no `ffs`/`assess_component` basename)* | — | **NO**. Only the legacy `API579` basename routes (`engine.py:287` → `asset_integrity.API579.API579`), a *different* engine. Registry rows `api579-pipe-ffs-b314/b318` (`workflows.yaml:712,720`) use basename `API579`. The Phase-1 coordinator has no route. | `FFSAssessmentResult.to_dict()` — flat JSON dict (`ffs_coordinator.py:90-110`), 16 keys, in-memory |
| **Buckling** — `structural/buckling_parametric.py` (`run_sweep`, `write_outputs`) | *(none)* | `engine.py:373` → `PlateBuckling()` (`infrastructure/base_solvers/structural/plate_buckling.py`, a **different, older** DNV-RP-C201 class; registry row `plate-buckling` `:477`) | **NO** for the scope-named module. `buckling_parametric` is a pure-Python parametric layer (PR #1044), **not engine-routed and has no registry row** (grep → none). | `write_outputs()` → `results.json {meta, lookup, index, index_status, curves}` (`buckling_parametric.py:232-286`); `_round(x, n=4)` throughout; only volatile key = optional `meta.generated_at` (`if timestamp is not None`, `:278`) |
| **Mooring** — `orcaflex/mooring_design.py` (`MooringLineDesign.check_mbl_with_safety_factor`, the calc-citation pilot #2685) | *(none — `mooring` is RESERVED, see note)* | — | **NO**. The existing `mooring` basename (`engine.py:377-384`) is **signposted for the separate `subsea/mooring_analysis/` subsystem** (imports `subsea.mooring_analysis.cli`, raises `NotImplementedError` to redirect there; `cli.py`/`designer.py`/`fpso_workflow.py` present) — **NOT** for this `orcaflex/mooring_design.py` pilot. So this pilot gets a **NEW non-colliding basename `mooring_mbl`** (this issue). `mooring_design.py` is a Pydantic library (no `router`). | `check_mbl_with_safety_factor()` → dict incl. `citations` sidecar (DNV-OS-E301), in-memory |
| **Wall-thickness** — routed `structural/wall_thickness_quickcheck.py` (`WallThicknessQuickCheck.router`); scope also names example dir | `wall_thickness` | `engine.py:280-286` → `WallThicknessQuickCheck().router()`; registry row `wall-thickness-quickcheck` (`:701`) | **YES** | `router()` writes `<...>.json` (`json.dumps(payload, indent=2, sort_keys=True)`), `.csv`, `.html`; files |

- **Embed path is #3307-owned (NOT this issue).** `digitalmodel/src/digitalmodel/engine.py:69` — `def engine(inputfile=None, cfg=None, config_flag=True) -> dict`. It imports `ConfigureApplicationInputs` from **assetutilities** (`engine.py:4`). The default path calls `app_manager.configure(cfg, library_name, basename, ...)` (`engine.py:105-113`) — note it passes `library_name` (a fork-specific arg). It sets `cfg["_config_dir_path"]` at `:89` and propagates it at `:117-118`. **#3307 adds the `embed=True`/`root_folder`/`log_to_file` branch that calls `configure_embed` (canonical signature `configure_embed(self, cfg, basename, root_folder, log_to_file=False)` — NEVER `library_name`, which is only on the regular `configure()`), routes writes under the root, and rebases `_config_dir_path` to the root.** #3285 consumes that; it does not author it. The three NEW arms #3285 adds (`ffs`, `buckling_parametric`, `mooring_mbl`) are additive dispatch branches; none touches the existing `mooring` arm (reserved for `subsea/mooring_analysis/`) or the embed branch.
- **Config-relative routers are why `_config_dir_path` rebasing matters.** `grep -rln "_config_dir_path" src/` → `engine.py`, `solvers/orcaflex/universal/path_resolver.py`, `asset_integrity/inspection_planning.py`, `code_checks/workflow.py`, `compare_tool/workflow.py`, `drilling_riser/{workflow,tsj_workflow}.py`, `fatigue/workflow.py`, `field_development/{rig_capability,registry_workflows}.py`, and more. These resolve outputs against the config dir; without #3307's rebase, embedded runs would leak writes outside the root (the MAJOR-1 mechanism).
- **FFS `to_dict` confirmed present** (`ffs_coordinator.py:90`) with the 16-key indexed shape (`component_id`, `assessment_type`, `level_reached`, `t_*`, `rsf*`, `folias_factor`, `remaining_life_yr`, `verdict`, `rerated_pressure_psi`, `sufficiency_status`, `passes`) — the #1066 Deckhand-API surface. `assess_component` is exported (`asset_integrity/assessment/__init__.py`). Reproduction below.
- **Wall-thickness router is determinism-friendly**: `json.dumps(..., sort_keys=True)` → stable byte output, ideal tracer-bullet for the #3283 `golden_workflow_test`.
- **Buckling has NO route and NO registry row** (verified): `grep "buckling_parametric" docs/registry/workflows.yaml` → none; `engine.py` routes only `plate_buckling` → `PlateBuckling`. **This issue OWNS-CREATES the route + row + reference golden**, runnable via the bare in-repo id `buckling-parametric`; #3283 references that golden illustratively only.
- **No existing `run_workflow`/`ResultEnvelope`/`workflow_api` in digitalmodel** (greenfield on the digitalmodel side).

### Standards
The four workflows derive constants from DNV/API standards; provenance must record (not re-derive) them per `.claude/rules/calc-citation-contract.md`. No new standards-derived constant is introduced — this plan only *stamps* existing citations into `provenance.standard_revisions`.

| Standard | Status | Source |
|---|---|---|
| DNV-OS-E301 (mooring safety factor) | recorded via provenance; **live calc-citation pilot** | `mooring_design.py:check_mbl_with_safety_factor` (#2685); wiki `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` |
| DNV-RP-C201 (plate buckling) | recorded via provenance | `buckling_parametric.py:34` `STANDARD = "DNV-RP-C201"` |
| API 579 / B31.4 / B31.8 (FFS metal loss) | recorded via provenance | `ffs_coordinator.py` design_code; `api579-pipe-ffs-*` rows |
| API/DNV wall-thickness | recorded via provenance | `wall-thickness-quickcheck` row title |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` — the calc-citation target the mooring sidecar already resolves; its frontmatter `revision` feeds `provenance.standard_revisions`. Read-only (Client: N/A; no wiki write).

### Documents consulted
- Epic #3281 — defines `ResultEnvelope` + in-process scope; names digitalmodel "the richest deterministic calc surface" / first real consumer.
- #3307 issue — the digitalmodel embed-port (this plan's hard prereq; mirrors #3297 in the fork; rebases `_config_dir_path`).
- #3282 plan — the `run_workflow`/`ResultEnvelope`/`result:` descriptor/parameterized `code_version` contract this plan consumes.
- #3297 plan — the assetutilities embed path #3307 mirrors (canonical `configure_embed` signature; default byte-identical).
- #3295 plan — registry v2 superset; reserves `result:` on digitalmodel's already-v2 registry.
- #3283 plan — the golden harness; provides `golden_workflow_test`. #3285 OWNS-CREATES the buckling reference golden (bare in-repo id); #3283 **references** it only as an illustrative consumer example (#3283 plan §"making one callable is exactly #3285's job"; #3283 Artifact Map lists the buckling golden/test under "#3285 (NOT #3283)") and #3284-gates the cross-repo form.
- #1066 (CLOSED — "Indexed FFS lookup + Deckhand API") — the indexed `FFSAssessmentResult.to_dict()` surface this plan exposes as `kind: in_memory`.
- `.claude/rules/calc-citation-contract.md` — `Citation` sidecar shape reused for `provenance.standard_revisions` (`source_sibling: generic` default during digitalmodel migration).

### Gaps identified (G0 removed — see Wave-2 revisions)
> **Every new row below is a FULL durable workflow** (`id`/`basename`/`title`/`input:`/`outputs:`/`test:`/`runtime: offline` + the new `result:`) with a committed `examples/workflows/<id>/input.yml` fixture — NOT a descriptor-only row. This is the Wave-3 MAJOR-1 fix: `tests/workflows/test_durable_workflows.py` parametrizes over every row and reads `workflow["input"]`/`["outputs"]`, so descriptor-only rows would `KeyError`. Full rows make the durable suite *cover* the new routes instead of breaking.
- **G1 (FFS):** `assess_component`/`FFSAssessmentResult` has no engine route. Add a thin `ffs` basename router (cfg → `assess_component` → `cfg[basename] = result.to_dict()`) + a new FULL `ffs-metal-loss` registry row + `result: {kind: in_memory, key: ffs}` + fixture + golden. (Open decision RESOLVED below: new `ffs` basename, not retrofit `API579`.)
- **G2 (buckling) — #3285-OWNED:** the scope-named `buckling_parametric` (results.json producer) is not engine-routed and has no registry row. Add a `buckling_parametric` basename route (cfg → `run_sweep` → `write_outputs(out_dir=<result folder>)`), a new FULL `buckling-parametric` registry row, `result: {kind: files}`, a fixture, and the **reference golden** runnable via the bare in-repo id (#3283 references it illustratively). (Open decision RESOLVED below: new `buckling_parametric` route, not retrofit `plate-buckling`.)
- **G3 (mooring):** the `orcaflex/mooring_design.py` MBL pilot has no engine route, and the existing `mooring` basename is reserved for `subsea/mooring_analysis/` (it raises a redirect NotImplementedError — do NOT hijack it). Add a **NEW `mooring_mbl` basename** + arm + router (cfg → `MooringLineDesign.check_mbl_with_safety_factor` → `cfg["mooring_mbl"]`) preserving the DNV-OS-E301 citation sidecar, a new FULL `mooring-design-mbl` registry row, `result: {kind: in_memory, key: mooring_mbl}` + fixture + golden. The existing `mooring` arm is left untouched.
- **G4 (wall-thickness):** routable today (already a full durable row) — only needs the `result: {kind: files}` descriptor + golden. Lowest-risk; the tracer-bullet target.
- **Runner (R):** create `digitalmodel/src/digitalmodel/workflow_api/` — a digitalmodel-bound `run_workflow` that drives digitalmodel's **#3307-embeddable** engine (`engine(embed=True, root_folder=, log_to_file=False)`), resolving rows in digitalmodel's own registry, reusing the **imported** assetutilities `ResultEnvelope`/`ResultLocator`/hashing/provenance (per the re-locked "per-repo engines provide their own runner reusing the shared helpers" decision). `code_version("digitalmodel")`.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3285` — OPEN — this issue.
- `#3307` — OPEN, `status:needs-plan`, `lane:codex`, title "wf-api(digitalmodel): engine embed-port — mirror #3297 for digitalmodel's own engine [prereq for #3285]" — **this plan's hard prereq.**
- `#3308` — OPEN, `status:needs-plan` — the assethold sibling embed-port (prereq for #3287; not this issue).
- `#3283` — OPEN — determinism harness (golden template; **consumes** this issue's buckling golden).
- `#3284` — OPEN — discovery manifest (owns cross-repo `repo:id@version` resolution).
- `#1066` — **CLOSED** — Indexed FFS lookup + Deckhand API (the `to_dict` surface).
- `#3282`/`#3297`/`#3295` — OPEN/plan-review (upstream contract; none owner-approved).

**File existence** (`ls`/`grep` 2026-06-28):
- EXISTS: `digitalmodel/src/digitalmodel/asset_integrity/assessment/ffs_coordinator.py` (`to_dict` at :90)
- EXISTS: `digitalmodel/src/digitalmodel/structural/buckling_parametric.py` (`write_outputs` at :232; `if timestamp is not None` at :278 → byte-stable default)
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` (`check_mbl_with_safety_factor`)
- EXISTS: `digitalmodel/src/digitalmodel/structural/wall_thickness_quickcheck.py` (routed; `WallThicknessQuickCheck.router`)
- EXISTS: `digitalmodel/docs/registry/workflows.yaml` (`schema_version: 2` `:9`, `invocation:` `:10`; rows `wall-thickness-quickcheck` `:701`, `plate-buckling` `:477`, `api579-pipe-ffs-b314` `:712`)
- EXISTS: `digitalmodel/src/digitalmodel/engine.py` (fork; `def engine(...config_flag=True)` at :69 — **no embed param** until #3307; `_config_dir_path` set :89, propagated :117-118)
- MISSING (this plan creates): `digitalmodel/src/digitalmodel/workflow_api/` (run_workflow binding); the four `result:` descriptors; the three new FULL durable rows `ffs-metal-loss` (basename `ffs`) + `buckling-parametric` (basename `buckling_parametric`) + `mooring-design-mbl` (basename `mooring_mbl`); their `examples/workflows/<id>/input.yml` fixtures; the FFS/buckling/mooring-MBL routes (three NEW arms; the existing `mooring` arm untouched); the goldens.
- MISSING (created by #3307, NOT this plan): the `embed`/`root_folder`/`log_to_file` params + embed branch + `_config_dir_path` rebase in `digitalmodel/engine.py`.

**Line excerpts:**
```
engine.py:69    def engine(inputfile=None, cfg=None, config_flag=True) -> dict:        # embed params added by #3307
engine.py:89    cfg["_config_dir_path"] = os.path.dirname(os.path.abspath(inputfile)) # #3307 rebases this to the embed root
engine.py:105   cfg_base = app_manager.configure(cfg, library_name, basename, ...)      # default path passes library_name
engine.py:117   if "_config_dir_path" in cfg: cfg_base["_config_dir_path"] = cfg["_config_dir_path"]
engine.py:280   elif basename == "wall_thickness":   -> WallThicknessQuickCheck().router(cfg_base)   # G4 routable today
engine.py:287   elif basename == "API579":           -> asset_integrity.API579.API579(cfg_base)       # NOT ffs_coordinator
engine.py:373   elif basename == "plate_buckling":   -> PlateBuckling().router(cfg_base)              # NOT buckling_parametric
engine.py:377-384 elif basename == "mooring":  import subsea.mooring_analysis.cli; raise NotImplementedError(...)  # RESERVED for subsea/mooring_analysis -> #3285 adds a SEPARATE `mooring_mbl` arm, leaves this untouched
buckling_parametric.py:232  def write_outputs(rows, curves, out_dir, gamma_m=1.15, timestamp=None) -> dict[str,Path]
ffs_coordinator.py:90   def to_dict(self) -> dict:   # 16-key flat summary
```

**Reproduction proofs** (Step 1.5 — the issue makes runtime/behavioral claims):
```
$ /mnt/local-analysis/digitalmodel/.venv/bin/python -c "
  from digitalmodel.asset_integrity.assessment.ffs_coordinator import assess_component, FFSAssessmentResult
  print('to_dict:', hasattr(FFSAssessmentResult,'to_dict'))
  from digitalmodel.orcaflex.mooring_design import MooringLineDesign
  print('mooring pilot:', hasattr(MooringLineDesign,'check_mbl_with_safety_factor'))
  from digitalmodel.structural.buckling_parametric import run_sweep, write_outputs
  print('buckling import OK')"
to_dict: True
mooring pilot: True
buckling import OK
```
- **Engine `_config_dir_path` claim — REPRODUCED.** `grep -n "_config_dir_path" engine.py` → `:89` sets it to `os.path.dirname(os.path.abspath(inputfile))`; `:117-118` propagates it into `cfg_base`. Confirms the MAJOR-1 mechanism: config-relative routers resolve against this, so #3307's embed path must rebase it to the injected root for embedded writes to stay under root.
- **Engine routability claim — REFINED (load-bearing correction):** "FFSAssessmentResult.to_dict exists" CONFIRMED; "mooring is the calc-citation pilot" CONFIRMED; **"each workflow engine-routable" FALSE for FFS/buckling/mooring-MBL, TRUE only for wall-thickness** (`grep 'basename == "(mooring|API579|wall_thickness|ffs|plate_buckling|mooring_mbl)"' engine.py` → no `ffs` arm; no `mooring_mbl` arm; the `mooring` arm raises a redirect to `subsea/mooring_analysis/` and is RESERVED for it; `plate_buckling` routes to a different class; `buckling_parametric` absent). The plan therefore leads with closing the routing gaps via three NEW non-colliding basenames (`ffs`, `buckling_parametric`, `mooring_mbl`) + creating the buckling route/row/golden, not merely bolting descriptors onto callable workflows.
- Reproduced at: 2026-06-28.

(Distinct sources consulted: issue body + #3307 issue + #3282 plan + #3297 plan + #3295 plan + #3283 plan + #1066 + engine.py + ffs_coordinator.py + buckling_parametric.py + mooring_design.py + wall_thickness_quickcheck.py + path_resolver.py + registry yaml + calc-citation rule = 15 ≥ 3.)

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3285-digitalmodel-adopt-envelope.md |
| digitalmodel run_workflow binding (R) | `digitalmodel/src/digitalmodel/workflow_api/__init__.py`, `.../runner.py` |
| FFS router (G1) | `digitalmodel/src/digitalmodel/asset_integrity/assessment/ffs_workflow.py` (new) |
| Buckling router (G2, #3285-OWNED) | `digitalmodel/src/digitalmodel/structural/buckling_workflow.py` (new) |
| Mooring-MBL router (G3) | `digitalmodel/src/digitalmodel/orcaflex/mooring_workflow.py` (new) |
| Engine route arms (G1/G2/G3) | `digitalmodel/src/digitalmodel/engine.py` (add three NEW arms `ffs` + `buckling_parametric` + `mooring_mbl`; the existing `mooring` arm — reserved for `subsea/mooring_analysis/` — is left untouched) |
| Durable example fixtures (G1–G3) | `digitalmodel/examples/workflows/{ffs-metal-loss,buckling-parametric,mooring-design-mbl}/input.yml` (+ produced `results/`) |
| Registry `result:` descriptors + new FULL rows (G1–G4) | `digitalmodel/docs/registry/workflows.yaml` |
| Goldens (incl. buckling reference — #3285 OWNS; #3283 references illustratively) | `digitalmodel/tests/workflow_api/goldens/{ffs_*,buckling_parametric_*,mooring_mbl_*,wall_thickness_*}.json` |
| Tests | `digitalmodel/tests/workflow_api/test_run_workflow_{ffs,buckling,mooring,wall_thickness}.py`, `test_result_descriptors.py` |
| Plan reviews | scripts/review/results/2026-06-28-plan-3285-{claude,codex,gemini}.md |
| Plans index | docs/plans/README.md |

> Upstream-owned, **not edited here** (imported only): `assetutilities/src/assetutilities/workflow_api/{envelope,runner,hashing,provenance,golden}.py` (#3282/#3283); the registry `result:` schema reservation (#3295). **digitalmodel-engine embed path owned by #3307** (this plan consumes `engine(embed=True, root_folder=, log_to_file=False)`; it does NOT add the embed branch).

---

## Deliverable

After this issue, the four highest-value digitalmodel workflows — **FFS metal-loss (basename `ffs`), plate-buckling (the `buckling_parametric` sweep), mooring-MBL design (NEW basename `mooring_mbl`), and wall-thickness quickcheck** — are callable as `run_workflow("<id>", params)` returning a typed `ResultEnvelope` (the assetutilities-owned shape), each backed by a registry `result:` descriptor declaring its result location (`kind: in_memory` for FFS/mooring-MBL, `kind: files` for buckling/wall-thickness) and each guarded by a committed golden test using the #3283 `golden_workflow_test` template. The three new rows are **FULL durable workflows** (committed `examples/workflows/<id>/input.yml` fixtures + `input:`/`outputs:`/`test:`/`runtime:` keys), so the existing `tests/workflows/test_durable_workflows.py` parametrized suite *covers* them green — with **zero regression** to the existing `uv run python -m digitalmodel <input.yml>` CLI/durable path. **#3285 OWNS-CREATES the buckling registry row + engine route + reference golden**, runnable via a bare in-repo id; **#3283 references that golden only as an illustrative consumer example** (cross-repo id resolution is #3284-gated). The structural enabler — the digitalmodel embed path — is **delivered by #3307**, which this issue depends on and consumes.

---

## Pseudocode

```python
# ── R: digitalmodel/workflow_api/runner.py — per-repo runner reusing the SHARED contract ──
from assetutilities.workflow_api import ResultEnvelope            # shape OWNED by #3282 — imported, NOT redefined
from assetutilities.workflow_api.runner import (build_cfg, ResultLocator, extract_result)  # reuse upstream helpers
from assetutilities.workflow_api.hashing import result_hash       # #3282-owned (#3283 consumes; we don't redefine)
from assetutilities.workflow_api.provenance import stamp_provenance, code_version
from digitalmodel.engine import engine as dm_engine               # the #3307-EMBEDDABLE fork

REGISTRY = "digitalmodel/docs/registry/workflows.yaml"
def run_workflow(workflow_id, params=None, cfg=None, verify_reproducible=False) -> ResultEnvelope:
    # Cross-repo `repo:id@version` resolution is #3284-owned. THIS runner resolves a BARE single-registry id
    # within digitalmodel's own registry (decision below). Unknown id / engine error -> error envelope (fail-closed).
    row     = resolve_digitalmodel_row(workflow_id)               # bare id, e.g. "wall-thickness-quickcheck"
    cfg     = cfg or build_cfg(row, params)
    locator = ResultLocator.from_row(row)                         # reads the per-row result: descriptor
    root    = tempfile.mkdtemp(prefix="dmwf_")
    try:
        # #3307 embed path: writes (results + logs) under root; _config_dir_path rebased to root.
        cb = dm_engine(cfg=copy.deepcopy(cfg), embed=True, root_folder=root, log_to_file=False)
        payload, warns = extract_result(cb, locator, root)        # in_memory: cb[key]; files: glob root, excl save_cfg dump
        prov = stamp_provenance(cfg, row, code_version("digitalmodel"))   # PARAMETERIZED package (#3282)
        return ResultEnvelope(workflow_id, "ok", payload, prov,
                              {"result_hash": result_hash(payload), "reproducible": <None|double-run>},
                              confidence=None, warnings=warns)
    except Exception as e:
        return ResultEnvelope(workflow_id, "error", {}, stamp_provenance(None, None, code_version("digitalmodel")),
                              {"result_hash": None, "reproducible": None}, None, [str(e)])
    finally:
        shutil.rmtree(root, ignore_errors=True)

# ── G1: asset_integrity/assessment/ffs_workflow.py — give the coordinator an engine route (kind: in_memory) ──
class FFSWorkflow:                                # registered under a NEW basename "ffs" in engine.py
    def router(self, cfg):
        component = FFSComponent(**cfg["component"])
        result = assess_component(component, cfg["grid"], input_units=cfg.get("input_units","in"))
        cfg[cfg["basename"]] = result.to_dict()   # in-memory locator target (#1066 indexed 16-key shape)
        return cfg

# ── G2 (#3285-OWNED): structural/buckling_workflow.py — make buckling_parametric run_workflow-callable (kind: files) ──
class BucklingParametricWorkflow:                # NEW basename "buckling_parametric" in engine.py
    def router(self, cfg):
        sweep = BucklingSweepConfig(**cfg.get("sweep", {})) or DEFAULT_SHIP_PLATE_SWEEP
        rows  = run_sweep(sweep)
        curves = build_curves(rows)
        out_dir = _result_out_dir(cfg)            # config-relative result folder: CLI durable path -> <config dir>/results;
                                                  #   #3307 embed path -> rebased to the injected root. Same call, both paths.
        write_outputs(rows, curves, out_dir, timestamp=None)   # timestamp=None -> byte-stable results.json (the golden)
        return cfg

# ── G3: orcaflex/mooring_workflow.py — NEW `mooring_mbl` arm/router (kind: in_memory); does NOT touch the reserved `mooring` arm ──
class MooringMBLWorkflow:                         # registered under a NEW basename "mooring_mbl" in engine.py (NOT "mooring")
    def router(self, cfg):
        design = MooringLineDesign(**cfg["design"])
        out = design.check_mbl_with_safety_factor(cfg["max_tension_kn"], condition=cfg.get("condition","intact"))
        cfg[cfg["basename"]] = out                # cfg["mooring_mbl"]; carries DNV-OS-E301 `citations` sidecar -> provenance.standard_revisions
        return cfg
```

> Wall-thickness (G4) writes no code beyond the registry `result:` descriptor + golden — the router already emits sorted-key JSON. The embed branch + `_config_dir_path` rebase are **#3307's** deliverable; this plan consumes `engine(embed=True, …)`.

---

## Registry change (additive — schema already v2; new rows are FULL durable workflows)

> **Wave-3 MAJOR-1 fix:** the three new rows carry the SAME full key-set every existing row has (`input:`/`outputs:`/`test:`/`runtime:`) plus the new `result:` — they are NOT descriptor-only. `tests/workflows/test_durable_workflows.py::test_workflow_registry` parametrizes over EVERY row and, for `runtime: offline`, reads `workflow["input"]` (`:38`) + iterates `workflow["outputs"]` (`:48`); descriptor-only rows would `KeyError`. Full rows make the durable suite *cover* the three new routes green.

```yaml
# digitalmodel/docs/registry/workflows.yaml  (schema_version: 2 unchanged; result: is the #3295-reserved slot, #3282-shaped)
  - id: wall-thickness-quickcheck       # EXISTING full row (:701, already has input/outputs/test/runtime) — add result: only
    basename: wall_thickness
    result:                             # NEW (#3282-owned shape; #3295-reserved slot)
      kind: files                       # extract_result globs the injected embed root; EXCLUDES the save_cfg dump
  - id: ffs-metal-loss                  # NEW FULL durable row (G1; new `ffs` basename — does NOT disturb api579-* rows)
    basename: ffs
    title: API 579 L1/L2 metal-loss FFS coordinator (measurement-sufficiency aware, #1066)
    input: examples/workflows/ffs-metal-loss/input.yml
    outputs:
      - examples/workflows/ffs-metal-loss/results/input.yml          # save_cfg dump carrying cfg["ffs"] = to_dict()
    test: tests/workflows/test_durable_workflows.py::test_workflow_registry[ffs-metal-loss]
    runtime: offline
    result:
      kind: in_memory
      key: ffs                          # cfg["ffs"] = FFSAssessmentResult.to_dict()
  - id: buckling-parametric             # NEW FULL durable row (G2; #3285-OWNED; bare in-repo id; #3283 references golden illustratively)
    basename: buckling_parametric
    title: DNV-RP-C201 plate-buckling parametric sweep (results.json + O(1) index)
    input: examples/workflows/buckling-parametric/input.yml
    outputs:
      - examples/workflows/buckling-parametric/results/input.yml     # save_cfg dump
      - examples/workflows/buckling-parametric/results/results.json  # write_outputs payload (meta.generated_at omitted -> byte-stable)
    test: tests/workflows/test_durable_workflows.py::test_workflow_registry[buckling-parametric]
    runtime: offline
    result:
      kind: files                       # results.json {meta,lookup,index,index_status,curves}; meta.generated_at omitted
  - id: mooring-design-mbl              # NEW FULL durable row (G3; NEW `mooring_mbl` basename — does NOT collide with the reserved `mooring` arm)
    basename: mooring_mbl
    title: DNV-OS-E301 mooring MBL safety-factor check (calc-citation pilot #2685)
    input: examples/workflows/mooring-design-mbl/input.yml
    outputs:
      - examples/workflows/mooring-design-mbl/results/input.yml      # save_cfg dump carrying cfg["mooring_mbl"]
    test: tests/workflows/test_durable_workflows.py::test_workflow_registry[mooring-design-mbl]
    runtime: offline
    result:
      kind: in_memory
      key: mooring_mbl
```

> The existing `plate-buckling` (`:477`), `api579-pipe-ffs-*` (`:712,720`), and the `mooring` basename (reserved for `subsea/mooring_analysis/`) are **left untouched** — the new `ffs`/`buckling_parametric`/`mooring_mbl` basenames are additive, so the legacy still-supported engines and the reserved mooring subsystem are not disturbed.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/src/digitalmodel/engine.py` | Add three NEW arms: `ffs` (G1), `buckling_parametric` (G2), `mooring_mbl` → `MooringMBLWorkflow().router` (G3). **Leave the existing `mooring` arm (reserved for `subsea/mooring_analysis/`) untouched. No embed-branch edit — that is #3307.** |
| Create | `digitalmodel/src/digitalmodel/workflow_api/__init__.py`, `.../runner.py` | digitalmodel-bound `run_workflow` driving the #3307-embeddable engine, reusing imported assetutilities `ResultEnvelope`/`ResultLocator`/hashing/provenance; `code_version("digitalmodel")` |
| Create | `digitalmodel/src/digitalmodel/asset_integrity/assessment/ffs_workflow.py` | G1 FFS router exposing `assess_component` → `to_dict()` |
| Create | `digitalmodel/src/digitalmodel/structural/buckling_workflow.py` | G2 buckling router making `buckling_parametric` run_workflow-callable (#3285-owned) |
| Create | `digitalmodel/src/digitalmodel/orcaflex/mooring_workflow.py` | G3 `MooringMBLWorkflow` router (NEW `mooring_mbl` basename) preserving the DNV-OS-E301 citation sidecar |
| Create | `digitalmodel/examples/workflows/{ffs-metal-loss,buckling-parametric,mooring-design-mbl}/input.yml` | durable-workflow input fixtures (MAJOR-1: make the new rows real CLI-exercised durable workflows) |
| Modify | `digitalmodel/docs/registry/workflows.yaml` | add `result:` to `wall-thickness-quickcheck`; add three new FULL durable rows `ffs-metal-loss` (`ffs`), `buckling-parametric` (`buckling_parametric`), `mooring-design-mbl` (`mooring_mbl`) — each with `input:`/`outputs:`/`test:`/`runtime:`/`result:` |
| Create | `digitalmodel/tests/workflow_api/test_run_workflow_{ffs,buckling,mooring_mbl,wall_thickness}.py` | per-workflow envelope + golden tests (#3283 `golden_workflow_test`) |
| Create | `digitalmodel/tests/workflow_api/test_result_descriptors.py` | registry `result:` descriptors parse + match `ResultLocator`; absence still valid (superset) |
| Create | `digitalmodel/tests/workflow_api/goldens/{ffs_*,buckling_parametric_*,mooring_mbl_*,wall_thickness_*}.json` | committed golden envelopes; **`buckling_parametric_*` is the #3285-owned reference golden #3283 references illustratively** |
| Update | docs/plans/README.md | update this plan's index row (workspace-hub) |

---

## TDD Test List

| Test name | What it verifies | Input | Output |
|---|---|---|---|
| test_run_workflow_wall_thickness_envelope | **(G4 tracer)** `run_workflow("wall-thickness-quickcheck", params)` → ok envelope; `result.kind=="files"`; save_cfg dump excluded from content hash | params dict | populated `ResultEnvelope`, status ok |
| test_wall_thickness_golden | **(G4)** `result_hash` matches committed golden via #3283 `golden_workflow_test` | fixed params | golden match within float tolerance |
| test_run_workflow_ffs_in_memory | **(G1)** FFS route returns `to_dict()` as `kind:in_memory` payload (`cfg["ffs"]`) | FFS component + grid | envelope.result == to_dict() shape (16 keys) |
| test_ffs_golden | **(G1)** FFS envelope determinism golden | fixed under-measured grid (TAKE_MORE case) | golden match |
| test_run_workflow_buckling_files | **(G2, #3285-OWNED)** new `buckling_parametric` route returns `results.json` payload as `kind:files` via the **bare in-repo id** `run_workflow("buckling-parametric", …)`; `meta.generated_at` absent (byte-stable) | default sweep params | files payload; golden committed here |
| test_buckling_reference_golden_bare_in_repo_id | **(G2)** the #3285-owned buckling reference golden is runnable via the **bare in-repo id** (no #3284); double-run yields identical `result_hash`; cross-link comment notes #3283 may reference it illustratively and that the cross-repo `digitalmodel:buckling-parametric` form is #3284-gated | fixed sweep | stable hash; in-repo id only |
| test_run_workflow_mooring_mbl_citation_preserved | **(G3)** the NEW `mooring_mbl` arm routes (the reserved `mooring` arm is untouched); payload carries DNV-OS-E301 `citations`; `provenance.standard_revisions` populated | mooring design + max_tension | envelope.result has `citations`; provenance non-empty |
| test_mooring_mbl_golden | **(G3)** `mooring_mbl` envelope determinism golden | fixed design | golden match |
| test_mooring_basename_still_reserved | **(G3 no-collision)** the existing `mooring` basename still routes to its `subsea/mooring_analysis/` redirect (unchanged); `mooring_mbl` is a distinct arm | `engine(... basename="mooring")` | original NotImplementedError redirect preserved |
| test_result_descriptors_parse_and_match_locator | **(G1–G4)** every new `result:` row parses + builds a valid `ResultLocator`; absence still valid (superset) | registry rows | all parse |
| test_run_workflow_unknown_id_error_envelope | unknown id enveloped, not raised (fail-closed) | `run_workflow("nope")` | status=="error" |
| test_embed_run_writes_only_under_root | **(consume #3307)** `run_workflow(...)` leaves nothing outside the tempdir root; cwd unchanged (depends on #3307's rebase of `_config_dir_path`) | any routed workflow | only `root/**`; cwd clean |
| test_cli_path_no_regression_full_suite | **(NO-REGRESSION, MAJOR-1)** the existing `tests/workflows/test_durable_workflows.py::test_workflow_registry` parametrized suite — which reads `workflow["input"]`/`["outputs"]` for EVERY offline row — runs green, INCLUDING the three new full rows (`ffs-metal-loss`, `buckling-parametric`, `mooring-design-mbl`); no `KeyError` from a descriptor-only row | all registry rows (existing + 3 new) | green; 3 new parametrize cases pass |

> Tests are written test-first but go green only once #3307 (embed path) + #3282 (`run_workflow`) land. This ordering gate is documented in Risks.

---

## Acceptance Criteria

- [ ] **Upstream landed:** #3307 (digitalmodel embed path), #3282 (`run_workflow` + `ResultEnvelope` + `result:` descriptor + parameterized `code_version`), #3295 (registry `result:` reserved) are merged. This issue does not merge before them. #3283 lands in parallel and references this issue's buckling golden.
- [ ] **Runner (R):** `digitalmodel.workflow_api.run_workflow` drives digitalmodel's **#3307-embeddable** engine using the **imported** assetutilities `ResultEnvelope`/`ResultLocator`/hashing/provenance (no redefinition), resolving a **bare single-registry id** in digitalmodel's registry; calls `code_version("digitalmodel")`.
- [ ] Each of the four workflows returns a typed `ResultEnvelope` via `run_workflow("<id>", params)`, demonstrated by passing tests under the digitalmodel pytest harness.
- [ ] Each carries a registry `result:` descriptor (`kind: in_memory` FFS/mooring-MBL, `kind: files` buckling/wall-thickness) and a committed golden test using the #3283 `golden_workflow_test` template.
- [ ] **The three new rows are FULL durable workflows (MAJOR-1):** each carries `input:`/`outputs:`/`test:`/`runtime: offline` + committed `examples/workflows/<id>/input.yml`, so `tests/workflows/test_durable_workflows.py::test_workflow_registry` parametrizes over them WITHOUT `KeyError` and they pass via the CLI path. No descriptor-only rows are added.
- [ ] **#3285 OWNS-CREATES the buckling adoption:** the new `buckling-parametric` registry row + `buckling_parametric` engine route + reference golden exist and run via the **bare in-repo id** `run_workflow("buckling-parametric", …)`. **#3283 references the golden only as an illustrative example**; any cross-repo `digitalmodel:buckling-parametric` resolution is **#3284-gated** (not a dependency here). Cross-link comment recorded on #3283/#3285.
- [ ] **Mooring-MBL is routed under the NEW `mooring_mbl` basename (MAJOR-2):** the existing `mooring` basename (reserved for `subsea/mooring_analysis/`) is untouched; its envelope `provenance.standard_revisions` carries DNV-OS-E301 from the live `check_mbl_with_safety_factor` citation sidecar.
- [ ] FFS exposes the #1066 indexed `to_dict()` 16-key surface as the envelope `result` via the new `ffs` basename (legacy `API579` rows untouched).
- [ ] **Embed isolation (consumes #3307):** `run_workflow` writes only under the injected tempdir root (proven by `test_embed_run_writes_only_under_root`); no leak via `_config_dir_path`.
- [ ] **No regression to the CLI/durable path:** `uv run python -m digitalmodel <input.yml>` and `tests/workflows/test_durable_workflows.py` (now including the three new rows) stay green.
- [ ] Review artifacts posted under scripts/review/results/ (T3 = 3 providers).

---

## Adversarial Review Summary

<!-- Wave-1 MAJOR (2) addressed in Wave-2. Wave-2 review returned MAJOR (2) — addressed in Wave-3 (route count / framing). Wave-3 review returned MAJOR (3) — all addressed in THIS revision; a fresh review round is PENDING. Plan stays `draft` until a no-MAJOR round is recorded. -->

**Wave-1 round — MAJOR (2), addressed in Wave-2:**
- **MAJOR-1 (routers write outside the injected root; #3285 was porting the embed branch).** ADDRESSED: the embed path + `_config_dir_path` rebase is now **#3307-owned**; #3285 depends on #3307 and consumes `engine(embed=True, root_folder=, log_to_file=False)`. The former G0 "port the embed branch" deliverable is removed from scope.
- **MAJOR-2 (inverted buckling ownership — "reuse #3283's golden").** ADDRESSED: framing FLIPPED. #3285 OWNS-CREATES the `buckling-parametric` registry row + `buckling_parametric` engine route + reference golden; #3283 references it illustratively.

**Wave-3 round — MAJOR (3), addressed in THIS revision:**
- **MAJOR-1 (descriptor-only new rows break the no-regression durable suite).** ADDRESSED: the three new rows are now **FULL durable workflows** (`input:`/`outputs:`/`test:`/`runtime:` + committed `examples/workflows/<id>/input.yml` fixtures), so `test_durable_workflows.py::test_workflow_registry` parametrizes over them without `KeyError` and *covers* the new routes. (Chosen over relaxing the durable parametrization.)
- **MAJOR-2 (mooring basename collision).** ADDRESSED: the MBL pilot uses a **NEW basename `mooring_mbl`** with a new engine arm; the existing `mooring` arm — reserved for `subsea/mooring_analysis/` — is left untouched. Registry row, route, golden, fixture, tests, and ACs all updated to `mooring_mbl`.
- **MAJOR-3 (over-claimed reciprocal #3283 consumer demo).** ADDRESSED: framing aligned with #3283. #3285 OWNS-CREATES the buckling row/route/reference golden runnable via a **bare in-repo id**; #3283 references it only illustratively; any **cross-repo** id resolution is **#3284-gated**. Removed the reciprocal "depends back" / "self-proof" language throughout; corrected the template name to `golden_workflow_test`.

**New round (Wave-4) — PENDING:**

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING (not approval-ready). Implementation is gated behind (a) the upstream contract landing (#3307 → #3282, #3295; #3283 in parallel), and (b) USER approval.

---

## Risks and Open Questions

- **Risk — deep, unapproved upstream stack.** Critical path: **#3307** → #3282 → #3295 → **#3285** (with #3283 consuming #3285's buckling golden). All are `draft`/`needs-plan`/`plan-review`, none owner-approved; #3297 (which #3307 mirrors) was MAJOR'd twice. If the upstream `ResultEnvelope`/`result:` shape or #3307's embed signature shifts, this plan's descriptors/goldens/runner follow. Mitigation: consume the contract **as specified**, import (never redefine) the envelope + helpers, keep the digitalmodel-side surface thin so a contract change is a small re-bind.
- **Risk — #3307 must land first and must rebase `_config_dir_path`.** This issue's embed isolation AC (`test_embed_run_writes_only_under_root`) is only satisfiable if #3307 rebases `_config_dir_path` to the injected root (the MAJOR-1 mechanism). If #3307 ships without the rebase, config-relative routers leak writes. Mitigation: state the dependency explicitly; the isolation test fails loudly if the rebase is absent. Recommend #3307's plan carry a matching AC.
- **Risk — new engine routes touch the fork's dispatch.** Adding three NEW arms (`ffs`, `buckling_parametric`, `mooring_mbl`) touches the ~80-arm dispatch. Mitigation: routers are thin adapters over already-tested library calls (`assess_component`, `run_sweep`/`write_outputs`, `check_mbl_with_safety_factor`); no new calc; all three are NEW basenames (no existing arm modified — the reserved `mooring` arm is untouched); CLI/durable no-regression suite (now including the 3 new rows) pins behavior.
- **Decision RESOLVED — new rows are FULL durable workflows (MAJOR-1):** each new row carries `input:`/`outputs:`/`test:`/`runtime:` + a committed `examples/workflows/<id>/input.yml`, NOT a descriptor-only `result:`-only row. Rationale: `test_durable_workflows.py` parametrizes over every row and reads `input:`/`outputs:`; descriptor-only rows would `KeyError`. Chosen over relaxing that shared parametrization.
- **Decision RESOLVED — FFS route shape (G1):** **new `ffs` basename + new `ffs-metal-loss` registry row** binding `assess_component`. Do NOT retrofit the legacy `API579` basename/rows (a different, still-supported engine). Basename chosen: `ffs`.
- **Decision RESOLVED — buckling route (G2):** **new `buckling_parametric` basename + new `buckling-parametric` registry row + reference golden**, all #3285-owned, runnable via a bare in-repo id. Do NOT retrofit the existing `plate-buckling` row (different `PlateBuckling` class). This matches the issue's named module; #3283 references the golden illustratively only.
- **Decision RESOLVED — mooring basename (G3, MAJOR-2):** **new `mooring_mbl` basename + new `mooring-design-mbl` registry row + new engine arm**. Do NOT commandeer the existing `mooring` basename — `engine.py:377-384` reserves it for the `subsea/mooring_analysis/` subsystem (`cli.py`/`designer.py`/`fpso_workflow.py`). The `orcaflex/mooring_design.py` MBL pilot (#2685) is a distinct calc and gets its own non-colliding basename, consistent with `ffs`/`buckling_parametric`.
- **Decision RESOLVED — cross-repo id (MAJOR-3 alignment):** the digitalmodel runner resolves a **bare single-registry id** within digitalmodel's own `workflows.yaml`; the buckling reference golden runs via that bare id (`buckling-parametric`). Cross-repo `repo:id@version` resolution (`digitalmodel:buckling-parametric`) is **#3284-owned** and is NOT a dependency of #3285's goldens. #3283 may reference the buckling golden as an illustrative example of its template; that cross-repo demo (not #3285's in-repo golden) is what #3284-gates.
- **Decision RESOLVED — golden home:** new goldens under `digitalmodel/tests/workflow_api/goldens/`; the buckling reference golden lives here and is cross-linked from #3283 (which references it illustratively, does not commit it).

---

## Complexity: T3

**T3** — adds three new engine routes under three NEW non-colliding basenames (`ffs`, `buckling_parametric`, `mooring_mbl`) into the forked digitalmodel dispatch that the whole digitalmodel CLI + durable-workflow suite depends on, adds three FULL durable rows + example fixtures, creates a digitalmodel-side `workflow_api` runner, OWNS-CREATES the buckling registry row + route + reference golden (bare in-repo id; #3283 references it illustratively), populates four registry descriptors, and commits four goldens — all riding on a deep, unapproved, multi-repo upstream contract (#3307/#3282/#3295). Backward-compat of the CLI/durable path is mandatory and regression-pinned (the durable suite now covers the three new rows); 3-provider adversarial review required. Matches the issue's `lane:codex` engineering-code class.
