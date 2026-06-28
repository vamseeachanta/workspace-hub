# Plan for #3285: wf-api(digitalmodel) — adopt ResultEnvelope + result: descriptors + goldens (FFS, buckling, mooring, wall-thickness)

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3285
> **Epic:** https://github.com/vamseeachanta/workspace-hub/issues/3281
> **Depends on (hard, none owner-approved):** #3297 (engine embeddability) → #3282 (ResultEnvelope + run_workflow + result: descriptor) → #3295 (registry v2 superset reconcile) + #3283 (determinism/golden harness). This plan CONSUMES that upstream contract exactly as specified and does **not** redesign it.
> **Client:** N/A — no wiki content touched (provenance cites existing wiki standard slugs read-only)
> **Lane:** lane:codex (heavy engineering code — engine port, routers, golden capture)
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3285-claude.md | ...-codex.md | ...-gemini.md

---

## Upstream-contract dependency (read first — load-bearing)

This issue is the **first real consumer** of the deterministic-workflow-API contract. That contract is defined in four upstream plans, all currently `draft`/`plan-review` and **none owner-approved**. This plan builds on them **as specified** and flags the dependency rather than re-deriving:

- **#3282** (`docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md`): owns `from assetutilities.workflow_api import run_workflow, ResultEnvelope`. `run_workflow(workflow_id, params=None, cfg=None) -> ResultEnvelope` via the **#3297 embed path** `engine(cfg=..., embed=True, root_folder=tempfile.mkdtemp(), log_to_file=False)`. `ResultEnvelope` = stdlib dataclass (NOT Pydantic): `{workflow_id, status, result, provenance{code_version{package_version,git_sha}, standard_revisions[], data_as_of, input_hash}, determinism{result_hash, reproducible}, confidence, warnings}`. Result LOCATION = registry `result:` descriptor `{kind: in_memory(key) | files(glob the injected root, content-hash sorted basenames, EXCLUDE the save_cfg `<file_name>.yml` dump)}`. **#3282 OWNS the determinism fields + the `result:` descriptor shape.** This plan consumes both.
- **#3297** (`docs/plans/2026-06-28-issue-3297-engine-embeddability.md`): adds `engine(embed=True, root_folder, log_to_file)` + `ConfigureApplicationInputs.configure_embed`. **PREREQ — must land first.** Critically, #3297 is scoped to the **assetutilities** engine and **explicitly excludes the digitalmodel engine fork** ("The digitalmodel fork is out of scope for #3297 … a follow-on issue should track porting the embed path there if/when digitalmodel needs embeddability." — #3297 Risks). **This issue IS that follow-on** — see Gap G0 below.
- **#3295** (`docs/plans/2026-06-28-issue-3295-registry-schema-v2-reconcile.md`): registry `schema_version: 2` additive superset; required top-level `invocation:`; `request_schema`/`response_schema`/`result` RESERVED structured (no `str` invariant); `deckhand/src/deckhand/capability_smoke.py` is the real resolver. **digitalmodel's registry is already `schema_version: 2`** (verified), so this plan only *populates* the reserved per-row `result:` slot — additive, no version bump.
- **#3283** (`docs/plans/2026-06-28-issue-3283-determinism-harness.md`): the golden harness — `result_hash()` (float-tolerance, volatile-field-safe), `stamp_provenance()`, `assert_golden_workflow()` pytest template + refresh/re-sanction procedure, landing in `assetutilities/workflow_api/{hashing,provenance,golden}.py`, with **the digitalmodel buckling workflow as its single reference golden**. This issue's "golden tests per #3283 harness" consume that template and **extend** goldens to FFS, mooring, and wall-thickness.

**This issue cannot be implemented until #3297 + #3282 land (run_workflow + embed path exist), #3295 lands (registry `result:` slot reserved), and #3283 lands (golden harness exists).** Per-issue extra gates may apply (cf. #3066 for the assethold consumer). Implementation is additionally gated behind USER approval of THIS plan.

---

## Resource Intelligence Summary

### Existing repo code (verified 2026-06-28 against `/mnt/local-analysis/digitalmodel` @ local HEAD `ec8e694`, remote main `902be4e`)

**Engine-routability audit (the issue's first explicit ask — "Verify each workflow is engine-routable").** Result: of the four named targets, **only wall-thickness is currently engine-routable**; FFS, buckling, and mooring each have a distinct routing gap.

| Target (scope-named module) | Engine basename | Routes to | Routable today? | Native result surface |
|---|---|---|---|---|
| **FFS** — `asset_integrity/assessment/ffs_coordinator.py` (`assess_component`, `FFSAssessmentResult.to_dict`) | *(none — no `ffs`/`assess_component` basename)* | — | **NO**. Only the legacy `API579` basename routes (`engine.py:287` → `asset_integrity.API579.API579`), a *different* engine. Registry rows `api579-pipe-ffs-b314/b318` use basename `API579`. The Phase-1 coordinator has no route. | `FFSAssessmentResult.to_dict()` — flat JSON dict (`ffs_coordinator.py:90-109`), 16 keys, in-memory |
| **Buckling** — `structural/buckling_parametric.py` (`run_sweep`, `write_outputs`) | *(none — `plate_buckling` routes elsewhere)* | `engine.py:373` → `PlateBuckling()` from `infrastructure/base_solvers/structural/plate_buckling.py` (a **different, older** DNV-RP-C201 class; registry row `plate-buckling`) | **NO** for the scope-named module. `buckling_parametric` is a pure-Python parametric layer invoked by a demo driver (PR #1044), not the engine. | `write_outputs()` → `results.json {meta, lookup, index, index_status, curves}` (`buckling_parametric.py:262-283`); `_round(x, n=4)` everywhere; only volatile key = optional `meta.generated_at` |
| **Mooring** — `orcaflex/mooring_design.py` (`MooringLineDesign.check_mbl_with_safety_factor`, the calc-citation pilot #2685) | `mooring` | `engine.py:377-384` → **`raise NotImplementedError`** | **NO**. Hard NotImplementedError. `mooring_design.py` is a Pydantic library (no `router`). The only mooring-ish route is `api-2sk-mooring` (basename `code_check`, a separate module). | `check_mbl_with_safety_factor()` → dict incl. `citations` sidecar (DNV-OS-E301), in-memory |
| **Wall-thickness** — routed `structural/wall_thickness_quickcheck.py` (`WallThicknessQuickCheck.router`); scope also names example dir `examples/structural/wall_thickness_quickcheck/quick_check.py` | `wall_thickness` | `engine.py:280-286` → `WallThicknessQuickCheck().router()`; registry row `wall-thickness-quickcheck` | **YES** | `router()` writes `<...>.json` (`json.dumps(payload, indent=2, sort_keys=True)`, `wall_thickness_quickcheck.py:85`), `.csv`, `.html`; files |

- **G0 — digitalmodel engine is a FORK without the embed path.** `digitalmodel/src/digitalmodel/engine.py:69` — `def engine(inputfile=None, cfg=None, config_flag=True) -> dict`. It imports `ConfigureApplicationInputs` from **assetutilities** (`engine.py:4`), so `configure_embed` (added by #3297) will be importable — **but the digitalmodel `engine()` function body has no `embed`/`root_folder`/`log_to_file` params and no embed branch.** #3282's `run_workflow` lives in `assetutilities.workflow_api` and drives **assetutilities'** `engine`; digitalmodel basenames are only dispatched by digitalmodel's own `engine` (`engine.py:137-560`, ~80 `elif basename ==` arms). **Therefore digitalmodel workflows are NOT reachable through `assetutilities.run_workflow` as-is.** Closing G0 (port the #3297 embed branch into `digitalmodel/engine.py` + provide a digitalmodel-bound `run_workflow`) is the structural precondition for every other deliverable here.
- **FFS `to_dict` confirmed present** (`ffs_coordinator.py:90`) and `assess_component` is exported (`asset_integrity/assessment/__init__.py`). Reproduction below.
- **Wall-thickness router is determinism-friendly**: `json.dumps(..., sort_keys=True)` (`wall_thickness_quickcheck.py:85`) → stable byte output, ideal for the #3283 `result_hash` + golden.
- **Buckling is the #3283 reference golden** already (`digitalmodel/tests/structural/goldens/buckling_parametric_default.json` is #3283's deliverable). This issue must avoid double-owning that golden — it **reuses** #3283's buckling golden and adds the *registry descriptor* + the other three goldens.
- **No existing `run_workflow`/`ResultEnvelope`/`workflow_api` in digitalmodel** (`grep` → only an unrelated `diffraction_cli.py` match). Greenfield on the digitalmodel side.

### Standards
The four workflows derive constants from DNV/API standards; provenance must record (not re-derive) them per `.claude/rules/calc-citation-contract.md`. No new standards-derived constant is introduced by this plan — it only *stamps* existing citations into `provenance.standard_revisions`.

| Standard | Status | Source |
|---|---|---|
| DNV-OS-E301 (mooring safety factor) | recorded via provenance; **live calc-citation pilot** | `mooring_design.py:check_mbl_with_safety_factor` (#2685); wiki `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` |
| DNV-RP-C201 (plate buckling) | recorded via provenance | `buckling_parametric.py:34` `STANDARD = "DNV-RP-C201"` |
| API 579 / B31G / B31.4 / B31.8 (FFS metal loss) | recorded via provenance | `ffs_coordinator.py` design_code; `api579-pipe-ffs-*` rows |
| API/DNV wall-thickness | recorded via provenance | `wall-thickness-quickcheck` row title |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` — the calc-citation target the mooring sidecar already resolves; its frontmatter `revision` feeds `provenance.standard_revisions`. Read-only here (Client: N/A; no wiki write).

### Documents consulted
- Epic #3281 — defines `ResultEnvelope` + in-process scope; names digitalmodel "the richest deterministic calc surface" / first real consumer.
- #3282 plan — the `run_workflow`/`ResultEnvelope`/`result:` descriptor contract this plan consumes (envelope fields, `kind: in_memory|files`, glob-the-injected-root, exclude the `save_cfg` dump).
- #3297 plan — the embed path; **explicitly defers the digitalmodel fork** (the G0 prereq).
- #3295 plan — registry v2 superset; reserves `result:` (structured, untyped) on digitalmodel's already-v2 registry.
- #3283 plan — the golden harness (`result_hash`/`stamp_provenance`/`assert_golden_workflow`); buckling is its reference golden; this issue extends to FFS/mooring/wall-thickness.
- #1066 (CLOSED — "Indexed FFS lookup + Deckhand API") — the indexed `FFSAssessmentResult.to_dict()` surface this plan exposes as `kind: in_memory`.
- `.claude/rules/calc-citation-contract.md` — `Citation` sidecar shape reused for `provenance.standard_revisions` (`source_sibling: generic` default during digitalmodel migration).

### Gaps identified
- **G0 (structural):** digitalmodel `engine()` is a fork with no embed path; no digitalmodel-side `run_workflow`. Must port #3297's embed branch into `digitalmodel/engine.py` (additive, default-off) and add `digitalmodel/workflow_api` binding `assetutilities.ResultEnvelope`/determinism/`ResultLocator` to digitalmodel's embeddable engine.
- **G1 (FFS):** `assess_component`/`FFSAssessmentResult` has no engine route. Need either a thin `ffs` basename router (cfg → `assess_component` → `cfg[basename] = result.to_dict()`) **or** an in-memory `ResultLocator` that binds the library call. Then a `result: {kind: in_memory, key: ...}` descriptor + golden.
- **G2 (buckling):** the scope-named `buckling_parametric` (results.json producer) is not engine-routed; the engine's `plate_buckling` is a *different* class. Decision required (see Open Decisions): register the descriptor on the **existing** engine-routed `plate-buckling` row, or add a `buckling_parametric` route so the `results.json {meta,lookup,index,curves}` becomes the `kind: files` result. Reuse #3283's buckling golden either way.
- **G3 (mooring):** `mooring` basename raises NotImplementedError; `mooring_design.py` has no router. Need a router (cfg → `MooringLineDesign.check_mbl_with_safety_factor` → cfg[basename]) preserving the DNV-OS-E301 citation sidecar, then `result: {kind: in_memory}` + golden.
- **G4 (wall-thickness):** routable today — only needs the `result: {kind: files}` descriptor + golden. Lowest-risk; the tracer-bullet target.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3285` — OPEN — this issue.
- `#3283` — OPEN — determinism harness (golden template; buckling reference golden).
- `#3284` — OPEN — discovery manifest (downstream consumer of the registries this plan edits).
- `#1066` — **CLOSED** — Indexed FFS lookup + Deckhand API (the `to_dict` surface).
- `#3282`/`#3297`/`#3295` — OPEN/plan-review (upstream contract; none owner-approved).

**File existence** (`ls -la` 2026-06-28):
- EXISTS: `digitalmodel/src/digitalmodel/asset_integrity/assessment/ffs_coordinator.py` (`to_dict` at :90)
- EXISTS: `digitalmodel/src/digitalmodel/structural/buckling_parametric.py` (`write_outputs` at :232)
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` (`check_mbl_with_safety_factor` at :522)
- EXISTS: `digitalmodel/src/digitalmodel/structural/wall_thickness_quickcheck.py` (routed; `WallThicknessQuickCheck.router` at :72)
- EXISTS: `digitalmodel/examples/structural/wall_thickness_quickcheck/quick_check.py` (the example script — distinct from the routed src module)
- EXISTS: `digitalmodel/docs/registry/workflows.yaml` (`schema_version: 2`, `invocation:` at :11, 111 rows)
- EXISTS: `digitalmodel/src/digitalmodel/engine.py` (fork; `def engine(...config_flag=True)` at :69 — **no embed param**)
- MISSING (this plan creates): `digitalmodel/src/digitalmodel/workflow_api/` (run_workflow binding), the four `result:` descriptors, the FFS/mooring routers, the goldens.

**Line excerpts:**
```
engine.py:69    def engine(inputfile: str = None, cfg: dict = None, config_flag: bool = True) -> dict:
engine.py:280   elif basename == "wall_thickness":   -> WallThicknessQuickCheck().router(cfg_base)
engine.py:287   elif basename == "API579":           -> asset_integrity.API579.API579(cfg_base)  # NOT ffs_coordinator
engine.py:373   elif basename == "plate_buckling":   -> PlateBuckling().router(cfg_base)         # NOT buckling_parametric
engine.py:377-384 elif basename == "mooring":  raise NotImplementedError("Mooring via engine requires ... CLI or direct API.")
ffs_coordinator.py:90   def to_dict(self) -> dict:   # 16-key flat summary
buckling_parametric.py:262  payload = {"meta": {...}, "lookup": rows, "index": index_util, "index_status": ..., "curves": curves}
wall_thickness_quickcheck.py:85  json.dumps(payload, indent=2, sort_keys=True) + "\n"   # determinism-friendly
```

**Reproduction proofs** (Step 1.5 — the issue makes runtime/behavioral claims: "FFSAssessmentResult.to_dict exists", "each workflow engine-routable", "mooring is the calc-citation pilot"):
```
$ /mnt/local-analysis/digitalmodel/.venv/bin/python -c "
  from digitalmodel.asset_integrity.assessment.ffs_coordinator import assess_component, FFSAssessmentResult, FFSComponent
  print('to_dict method:', hasattr(FFSAssessmentResult,'to_dict'))
  from digitalmodel.orcaflex.mooring_design import MooringLineDesign
  print('MOORING check_mbl_with_safety_factor:', hasattr(MooringLineDesign,'check_mbl_with_safety_factor'))
  from digitalmodel.structural.buckling_parametric import run_sweep, write_outputs, DEFAULT_SHIP_PLATE_SWEEP
  print('BUCKLING import OK')"
IMPORT_OK
to_dict method: True
fields: ['component_id','assessment_type','level_reached','t_nominal_in','t_min_in','t_measured_min_in', ...]
MOORING check_mbl_with_safety_factor: True
BUCKLING import OK
```
- Reproduced at: 2026-06-28.
- Failure mode vs issue claim: **REFINED.** "FFSAssessmentResult.to_dict exists" — **CONFIRMED**. "mooring is the calc-citation pilot" — **CONFIRMED** (`check_mbl_with_safety_factor` present). "each workflow engine-routable" — **FALSE for FFS, buckling, mooring; TRUE only for wall-thickness** (engine grep above: FFS has no basename, buckling routes to a different class, mooring raises NotImplementedError). This is the load-bearing correction: the plan's scope leads with closing the routing gaps (G0–G3), not merely bolting descriptors onto already-callable workflows.

(Distinct sources consulted: issue body + #3282 plan + #3297 plan + #3295 plan + #3283 plan + #1066 + engine.py + ffs_coordinator.py + buckling_parametric.py + mooring_design.py + wall_thickness_quickcheck.py + plate_buckling.py + registry yaml + calc-citation rule = 14 ≥ 3.)

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3285-digitalmodel-adopt-envelope.md |
| digitalmodel engine embed port (G0) | `digitalmodel/src/digitalmodel/engine.py` |
| digitalmodel run_workflow binding (G0) | `digitalmodel/src/digitalmodel/workflow_api/__init__.py`, `.../runner.py` |
| FFS router (G1) | `digitalmodel/src/digitalmodel/asset_integrity/assessment/ffs_workflow.py` (new) |
| Mooring router (G3) | `digitalmodel/src/digitalmodel/orcaflex/mooring_workflow.py` (new) |
| Registry `result:` descriptors (G1–G4) | `digitalmodel/docs/registry/workflows.yaml` |
| Goldens | `digitalmodel/tests/workflow_api/goldens/{ffs_*,mooring_*,wall_thickness_*}.json` (+ reuse #3283's `tests/structural/goldens/buckling_parametric_default.json`) |
| Tests | `digitalmodel/tests/workflow_api/test_run_workflow_{ffs,buckling,mooring,wall_thickness}.py`, `test_engine_embed_port.py`, `test_result_descriptors.py` |
| Plan reviews | scripts/review/results/2026-06-28-plan-3285-{claude,codex,gemini}.md |
| Plans index | docs/plans/README.md |

> Upstream-owned, **not edited here** (imported only): `assetutilities/src/assetutilities/workflow_api/{envelope,runner,hashing,provenance,golden}.py` (#3282/#3283); `assetutilities/.../ApplicationManager.configure_embed` (#3297); the registry `result:` schema reservation (#3295).

---

## Deliverable

After this issue, the four highest-value digitalmodel workflows — **FFS metal-loss, plate-buckling, mooring design, and wall-thickness quickcheck** — are callable as `run_workflow("digitalmodel:<id>", params)` returning a typed `ResultEnvelope` (the assetutilities-owned shape), each backed by a registry `result:` descriptor declaring its result location (`kind: in_memory` for FFS/mooring, `kind: files` for buckling/wall-thickness) and each guarded by a committed golden test using the #3283 harness — with **zero regression** to the existing `uv run python -m digitalmodel <input.yml>` CLI path. The structural enabler is a digitalmodel-side embed port (G0) so digitalmodel's forked engine is reachable through the deterministic API.

---

## Pseudocode

```python
# ── G0: digitalmodel/engine.py — additive embed port (mirror of #3297, applied to the fork) ──
def engine(inputfile=None, cfg=None, config_flag=True,
           root_folder=None, log_to_file=True, embed=False) -> dict:     # NEW params, default == today
    ... existing cfg load + basename resolution (UNCHANGED) ...
    if embed:                                                            # NEW branch — unreachable without embed=True
        # per-call instance (no module-singleton re-entrancy); configure_embed from assetutilities (#3297)
        cfg_base = ConfigureApplicationInputs().configure_embed(cfg, basename, root_folder, log_to_file=log_to_file)
        # fall through to the SAME basename dispatch below (the ~80 elif arms) — unchanged
    elif config_flag:
        ... existing configure()/fm.router()/configure_result_folder() (UNCHANGED) ...
    else:
        cfg_base = cfg
    ... existing `if/elif basename == ...` dispatch (UNCHANGED) ...      # FFS/mooring arms added by G1/G3
    cfg_base = app_manager.save_cfg(cfg_base=cfg_base)                   # writes under <root>/results in embed mode
    return cfg_base

# ── G0: digitalmodel/workflow_api/runner.py — bind the assetutilities contract to digitalmodel's engine ──
from assetutilities.workflow_api import ResultEnvelope            # shape OWNED by #3282 — imported, not redefined
from assetutilities.workflow_api.runner import (build_cfg, ResultLocator, extract_result)  # reuse upstream helpers
from assetutilities.workflow_api.hashing import result_hash       # #3283
from assetutilities.workflow_api.provenance import stamp_provenance
from digitalmodel.engine import engine as dm_engine               # the EMBEDDABLE fork (post-G0)

REGISTRY = "digitalmodel/docs/registry/workflows.yaml"
def run_workflow(workflow_id, params=None, cfg=None, verify_reproducible=False) -> ResultEnvelope:
    # identical control flow to #3282's run_workflow, but driving dm_engine(embed=True) and digitalmodel's registry.
    # fail-closed: unknown id / engine error -> error envelope (never a raw traceback).
    row     = resolve_digitalmodel_row(workflow_id)               # "digitalmodel:wall-thickness-quickcheck" etc.
    cfg     = cfg or build_cfg(row, params)
    locator = ResultLocator.from_row(row)                         # reads the per-row result: descriptor
    root    = tempfile.mkdtemp(prefix="dmwf_")
    try:
        cb = dm_engine(cfg=copy.deepcopy(cfg), embed=True, root_folder=root, log_to_file=False)
        payload, warns = extract_result(cb, locator, root)       # in_memory: cb[key]; files: glob root, excl save_cfg dump
        prov = stamp_provenance(cfg, row, package="digitalmodel") # code_version{package_version,git_sha}, standard_revisions
        return ResultEnvelope(workflow_id, "ok", payload, prov,
                              {"result_hash": result_hash(payload), "reproducible": <None|double-run>},
                              confidence=None, warnings=warns)
    except Exception as e:
        return ResultEnvelope(workflow_id, "error", {}, stamp_provenance(None, None, "digitalmodel"),
                              {"result_hash": None, "reproducible": None}, None, [str(e)])
    finally:
        shutil.rmtree(root, ignore_errors=True)

# ── G1: asset_integrity/assessment/ffs_workflow.py — give the coordinator an engine route (kind: in_memory) ──
class FFSWorkflow:                                # registered under a NEW basename "ffs" in engine.py
    def router(self, cfg):
        component = FFSComponent(**cfg["component"])
        result = assess_component(component, cfg["grid"], input_units=cfg.get("input_units","in"))
        cfg[cfg["basename"]] = result.to_dict()   # in-memory result locator target (#1066 indexed shape)
        return cfg

# ── G3: orcaflex/mooring_workflow.py — replace the NotImplementedError with a real router (kind: in_memory) ──
class MooringWorkflow:                            # engine "mooring" arm calls this instead of raising
    def router(self, cfg):
        design = MooringLineDesign(**cfg["design"])
        out = design.check_mbl_with_safety_factor(cfg["max_tension_kn"], condition=cfg.get("condition","intact"))
        cfg[cfg["basename"]] = out                # carries the DNV-OS-E301 `citations` sidecar -> provenance.standard_revisions
        return cfg
```

> Buckling (G2) writes no new physics: the descriptor + golden bind to the existing engine-routed `plate-buckling` row OR to `buckling_parametric.write_outputs` per the Open Decision. Wall-thickness (G4) writes no code beyond the registry descriptor + golden — the router already emits sorted-key JSON.

---

## Registry change (additive — schema already v2)

```yaml
# digitalmodel/docs/registry/workflows.yaml  (schema_version: 2 unchanged; result: is the #3295-reserved slot, #3282-shaped)
  - id: wall-thickness-quickcheck
    basename: wall_thickness
    # ... existing fields unchanged ...
    result:                       # NEW (#3282-owned shape; #3295-reserved slot)
      kind: files                 # extract_result globs the injected embed root; EXCLUDES the save_cfg <file_name>.yml dump
  - id: api579-pipe-ffs-b314      # (or a NEW ffs-metal-loss row per the FFS Open Decision)
    basename: API579              # -> may become `ffs` once G1 lands; see Open Decisions
    result:
      kind: in_memory
      key: <basename>             # cfg[basename] = FFSAssessmentResult.to_dict()
  - id: <mooring row>             # NEW row for the mooring router (G3)
    basename: mooring
    result:
      kind: in_memory
      key: mooring
  - id: plate-buckling            # OR a buckling_parametric row per G2 Open Decision
    basename: plate_buckling
    result:
      kind: files                 # results.json {meta,lookup,index,curves} when bound to buckling_parametric
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/src/digitalmodel/engine.py` | G0 embed port (additive `embed`/`root_folder`/`log_to_file`, default-off, byte-identical default path); G1 add `ffs` basename arm; G3 replace `mooring` NotImplementedError with `MooringWorkflow().router` |
| Create | `digitalmodel/src/digitalmodel/workflow_api/__init__.py`, `.../runner.py` | digitalmodel-bound `run_workflow` consuming assetutilities `ResultEnvelope`/`ResultLocator`/hashing/provenance |
| Create | `digitalmodel/src/digitalmodel/asset_integrity/assessment/ffs_workflow.py` | G1 FFS router exposing `assess_component` → `to_dict()` |
| Create | `digitalmodel/src/digitalmodel/orcaflex/mooring_workflow.py` | G3 mooring router preserving the DNV-OS-E301 citation sidecar |
| Modify | `digitalmodel/docs/registry/workflows.yaml` | add per-row `result:` descriptors (FFS, buckling, mooring, wall-thickness); add the mooring row; (FFS/buckling rows per Open Decisions) |
| Create | `digitalmodel/tests/workflow_api/test_run_workflow_{ffs,buckling,mooring,wall_thickness}.py` | per-workflow envelope + golden tests (#3283 `assert_golden_workflow`) |
| Create | `digitalmodel/tests/workflow_api/test_engine_embed_port.py` | G0 embed-port isolation/backward-compat regression (CLI path byte-identical) |
| Create | `digitalmodel/tests/workflow_api/test_result_descriptors.py` | registry `result:` descriptors parse + match `ResultLocator` |
| Create | `digitalmodel/tests/workflow_api/goldens/{ffs_*,mooring_*,wall_thickness_*}.json` | committed golden envelopes (buckling reuses #3283's golden) |
| Update | docs/plans/README.md | add this plan's index row (workspace-hub) |

---

## TDD Test List

| Test name | What it verifies | Input | Output |
|---|---|---|---|
| test_engine_embed_port_default_path_unchanged | **(G0 backward-compat)** `engine(cfg=...)` with no embed/root_folder is byte-identical to today (CLI path) — outputs + logs unchanged | existing wall-thickness input.yml | same result locations as pre-change baseline |
| test_engine_embed_writes_only_under_root | **(G0 isolation)** `dm_engine(cfg=..., embed=True, root_folder=tmp, log_to_file=False)` writes nothing outside `tmp`; no `.log`/`logs/` | wall-thickness cfg | only `tmp/results/*`; cwd unchanged |
| test_run_workflow_wall_thickness_envelope | **(G4 tracer)** `run_workflow("digitalmodel:wall-thickness-quickcheck", params)` → ok envelope; `result.kind=="files"`; save_cfg dump excluded | params dict | populated `ResultEnvelope`, status ok |
| test_wall_thickness_golden | **(G4)** result_hash matches committed golden via #3283 `assert_golden_workflow` | fixed params | golden match within float tolerance |
| test_run_workflow_ffs_in_memory | **(G1)** FFS route returns `to_dict()` as `kind:in_memory` payload | FFS component + grid | envelope.result == to_dict() shape |
| test_ffs_golden | **(G1)** FFS envelope determinism golden | fixed under-measured grid (TAKE_MORE case) | golden match |
| test_run_workflow_mooring_citation_preserved | **(G3)** mooring route no longer raises; payload carries DNV-OS-E301 `citations`; `provenance.standard_revisions` populated | mooring design + max_tension | envelope.result has `citations`; provenance non-empty |
| test_mooring_golden | **(G3)** mooring envelope determinism golden | fixed design | golden match |
| test_run_workflow_buckling_files | **(G2)** buckling route returns the `results.json` payload as `kind:files` (reuses #3283 golden) | default sweep params | files payload; reuses buckling golden |
| test_result_descriptors_parse_and_match_locator | **(G1–G4)** every new `result:` row parses and builds a valid `ResultLocator`; absence still valid (superset) | registry rows | all parse |
| test_run_workflow_unknown_id_error_envelope | unknown id enveloped, not raised (fail-closed) | `run_workflow("digitalmodel:nope")` | status=="error" |
| test_cli_path_no_regression_full_suite | **(NO-REGRESSION)** existing `tests/workflows/test_durable_workflows.py` registry rows still run via CLI | all rows | green |

> Tests are written test-first but go green only once the upstream contract has landed (run_workflow/embed path/golden harness exist). This is the explicit ordering gate documented in Risks.

---

## Acceptance Criteria

- [ ] **Upstream landed:** #3297 + #3282 (run_workflow + embed path), #3295 (registry `result:` reserved), #3283 (golden harness) are merged. This issue does not merge before them.
- [ ] **G0:** `digitalmodel/engine.py` has the additive embed path (default-off, CLI path byte-identical — proven by `test_engine_embed_port_default_path_unchanged`); `digitalmodel.workflow_api.run_workflow` drives digitalmodel's embeddable engine using the **imported** assetutilities `ResultEnvelope`/`ResultLocator`/hashing/provenance (no redefinition).
- [ ] Each of the four workflows returns a typed `ResultEnvelope` via `run_workflow("digitalmodel:<id>", params)`, demonstrated by passing tests under the digitalmodel pytest harness.
- [ ] Each carries a registry `result:` descriptor (`kind: in_memory` FFS/mooring, `kind: files` buckling/wall-thickness) and a committed golden test using the #3283 harness.
- [ ] **Mooring no longer raises NotImplementedError**; its envelope `provenance.standard_revisions` carries DNV-OS-E301 from the live `check_mbl_with_safety_factor` citation sidecar.
- [ ] FFS exposes the `#1066` indexed `to_dict()` surface as the envelope `result`.
- [ ] **No regression to the CLI path:** `uv run python -m digitalmodel <input.yml>` and `tests/workflows/test_durable_workflows.py` stay green (`test_cli_path_no_regression_full_suite`).
- [ ] The buckling golden is **reused** from #3283 (no double-ownership); a cross-link comment records the boundary.
- [ ] Review artifacts posted under scripts/review/results/ (T3 = 3 providers).

---

## Adversarial Review Summary

<!-- PENDING — no review artifacts exist yet. Plan stays `draft` until a no-MAJOR round is recorded. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING (not approval-ready). Implementation is gated behind (a) the upstream contract landing (#3297→#3282, #3295, #3283), (b) the G2/FFS Open Decisions being resolved, and (c) USER approval.

---

## Risks and Open Questions

- **Risk — deep, unapproved upstream stack.** Critical path: #3297 → #3282 → (#3295 + #3283) → **#3285**. All four are `draft`/`plan-review`, none owner-approved; #3297 itself is T3 and was MAJOR'd twice. If the upstream `ResultEnvelope`/`result:` shape shifts, this plan's descriptors/goldens follow. Mitigation: consume the contract **as specified**, import (never redefine) the envelope, and keep the digitalmodel-side surface thin so a contract change is a small re-bind.
- **Risk — G0 is effectively a second #3297 (digitalmodel fork).** #3297 explicitly scoped the digitalmodel engine OUT. Porting the embed branch into the ~80-arm `digitalmodel/engine.py` carries the same backward-compat blast radius (the digitalmodel CLI + all durable-workflow tests). Mitigation: additive params default-off, the embed branch unreachable without `embed=True`, and a byte-identical-CLI regression test. **Open:** should G0 be split into its own digitalmodel child issue (mirroring #3297) so #3285 stays "descriptors + goldens"? Flag for the user — recommended if review judges the engine port too heavy to ride inside this issue.
- **Risk — mooring/FFS routing is new physics-adjacent surface.** Replacing `mooring`'s NotImplementedError and adding an `ffs` basename touches the engine dispatch. Mitigation: routers are thin adapters over already-golden library calls (`assess_component`, `check_mbl_with_safety_factor`); no new calc.
- **Risk — buckling golden double-ownership.** #3283 already commits `buckling_parametric_default.json`. This plan must reuse, not re-create it. Mitigation: cross-link + a test that imports the #3283 golden path.
- **Open Decision — FFS route shape (G1):** add a new `ffs` basename + a `ffs-metal-loss` registry row binding `assess_component`, OR retrofit the existing `API579` basename/rows to the Phase-1 coordinator? Recommend a **new `ffs` basename/row** (the legacy `API579` engine is a different, still-supported path — do not disturb it).
- **Open Decision — buckling target (G2):** register the `result:` descriptor on the **existing engine-routed `plate-buckling`** row (the older `PlateBuckling` class, in-memory array) — OR add a `buckling_parametric` route so the richer `results.json {meta,lookup,index,curves}` (the scope-named module + #3283 golden) is the `kind: files` result? Recommend **binding to `buckling_parametric`** to match the issue's named module and reuse the #3283 golden — but this needs a new engine route (more work). Flag for the user.
- **Open Decision — golden home:** `digitalmodel/tests/workflow_api/goldens/` (this plan) vs `tests/structural/goldens/` (#3283's buckling home). Recommend co-locating new goldens under `tests/workflow_api/goldens/` and referencing #3283's buckling golden in place.

---

## Complexity: T3

**T3** — modifies the forked digitalmodel engine that the whole digitalmodel CLI + durable-workflow suite depends on (G0), adds two new engine routes (FFS, mooring), creates a digitalmodel-side `workflow_api`, populates four registry descriptors, and commits four goldens — all riding on a deep, unapproved, multi-repo upstream contract (#3297/#3282/#3295/#3283). Backward-compat of the CLI path is mandatory and golden-proven; 3-provider adversarial review required. Matches the issue's `lane:codex` engineering-code class.
