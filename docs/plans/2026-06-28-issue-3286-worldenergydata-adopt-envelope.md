# Plan for #3286: wf-api(worldenergydata) — adopt envelope + generalize typed-query base; scheduler JobResult; hse_api (#363)

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3286
> **Epic:** https://github.com/vamseeachanta/workspace-hub/issues/3281
> **Depends on (HARD — must land first):** [#3297](https://github.com/vamseeachanta/workspace-hub/issues/3297) (assetutilities engine embeddability) → [#3282](https://github.com/vamseeachanta/workspace-hub/issues/3282) (`ResultEnvelope` + `run_workflow` + `ResultLocator`/hashing). Co-dependency: [#3295](https://github.com/vamseeachanta/workspace-hub/issues/3295) (registry schema v2 — wed registry is **already** v2, so minimal).
> **Client:** N/A — no wiki content touched
> **Lane:** lane:codex (heavy engineering: a wed-engine embed edit mirroring #3297 + a runner + a query base + an HSE query surface across two packages)
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3286-claude.md | ...-codex.md | ...-gemini.md

---

## Upstream-contract dependency (read first — do NOT redesign)

This plan **consumes** the epic-#3281 envelope contract exactly as defined by its upstream children; it does **not** modify or redesign that contract. The upstream contract is **no-MAJOR after multi-round adversarial review but is at `status:plan-review` and NOT owner-approved**. Therefore:

- **#3286 cannot be implemented before #3297 and #3282 land.** It imports `ResultEnvelope`, `run_workflow`, the `input_hash`/`result_hash`/`code_version`/`compute_reproducible` primitives, and the `ResultLocator`/`extract_result` machinery from `assetutilities.workflow_api` (the #3282 deliverable), and it mirrors the #3297 `engine(embed=True, root_folder=, log_to_file=)` embed path onto **worldenergydata's own engine** (`worldenergydata.engine.engine`, which is a *separate* engine from the assetutilities one — see Resource Intel). Both must exist first.
- The contract surface this plan binds to (verbatim, from the orchestrator brief and the #3282 plan):
  - `from assetutilities.workflow_api import run_workflow, ResultEnvelope`
  - `ResultEnvelope` = **stdlib dataclass** (NOT Pydantic): `{workflow_id, status, result, provenance{code_version{package_version, git_sha}, standard_revisions[], data_as_of, input_hash}, determinism{result_hash, reproducible}, confidence, warnings}`.
  - Result LOCATION = registry `result:` descriptor `{kind: in_memory(key) | files(glob the injected root, content-hash sorted basenames, EXCLUDE the `save_cfg` `<file_name>.yml` dump)}`. **#3282 OWNS** the determinism fields + the `result:` descriptor; **#3286 reuses them, owns none.**
- **Per-issue extra gate.** Because #3286 edits worldenergydata's *shared* engine (blast radius across every wed router), it carries an **extra adoption cross-review gate** analogous to the assethold `#3066` gate referenced for the assethold adoption child. Recorded under Acceptance Criteria; do not waive.

---

## Resource Intelligence Summary

### Existing repo code (verified 2026-06-28 against `/mnt/local-analysis/worldenergydata` @ `03ed99b3`)

- **The typed-query reference surface — `packages/worldenergydata-marine_safety/src/worldenergydata/marine_safety/api.py`** (the path the issue scope names; note it lives under the **marine_safety package**, not `src/worldenergydata/marine_safety/`, which holds only `analysis/`, `database/`, `scrapers/`, `utils/`). `class IncidentsQuery` exposes `query(*, source/sources, year/start_year/end_year, vessel_type/vessel_types, incident_type/incident_types, region/regions, **kwargs) -> pd.DataFrame` plus `trends`, `top_types`, `correlations`, `risk_hotspots`. The body (`:142-184`) hand-rolls the **singular→plural collapse 4×** (source/sources, vessel_type/vessel_types, incident_type/incident_types, region/regions) and the **single-year shorthand** (`:170-175`). A module-level singleton `incidents = IncidentsQuery()` (`:280`) backs `wed.marine_safety_api.incidents`. **This repeated normalization boilerplate is exactly what the generalized base extracts.**
- **The sibling reference surface — `packages/worldenergydata-bsee/src/worldenergydata/bsee/api.py`**: `ProductionQuery`/`WellsQuery`/`CompaniesQuery`, same shape (thin wrapper over a loader, `query(**filters) -> DataFrame`), surfaced via `wed.bsee.production` through `bsee/__init__.py:__getattr__` (`:130`). Confirms the base must support **module-singleton attribute access** (`wed.<ns>.<thing>.query(...)`), not just direct instantiation.
- **Lazy top-level wiring — `src/worldenergydata/__init__.py:75-118`**: `__getattr__` resolves `marine_safety_api` (`:93-96`) and any real subpackage. **`hse_api` is NOT wired** (this plan adds it).
- **worldenergydata's engine — `src/worldenergydata/engine.py`**: `engine(inputfile=None, cfg=None, config_flag=True) -> dict`. **It is a SEPARATE engine from assetutilities'** — it imports the assetutilities `ConfigureApplicationInputs` singleton (`app_manager`, `:21`) + `configure_result_folder` (`:70-72`) but dispatches on `basename` to **wed routers** (bsee `:79-81`, sodir, texas_rrc, fdas, marine_safety `:131-135`, …). It has **no `embed`/`root_folder`/`log_to_file` params**, returns the whole mutated `cfg_base`, and (via `app_manager.configure` + `configure_result_folder`) is cwd-coupled the same way the assetutilities engine was — so `run_workflow` (which #3282 wires onto the *assetutilities* engine) **cannot drive a wed workflow as-is**. AC#1 ("run_workflow returns a ResultEnvelope for ≥1 wed workflow, e.g. bsee/fdas") therefore requires a **wed-side embed path + wed-side runner** (see Gaps).
- **Scheduler `JobResult` — `packages/worldenergydata-scheduler/src/worldenergydata/scheduler/jobs/base.py:26-44`**: `@dataclass JobResult{job_name, start_time: datetime, end_time: datetime, status: str ("success"|"failure"|"skipped"), records_updated: int, error_msg: Optional[str], retryable: bool=True}`. Produced by `DataScheduler.run_once` (`scheduler.py:104-155`) and `_record_result`. **This is the exact shape to map → `ResultEnvelope`.**
- **`_metadata.json` shape — `jobs/base.py:90-128` `write_refresh_metadata`**: writes `{module, last_refresh: <UTC ISO>, record_count, file_count, total_size_bytes, source_url, format, files}`. **`last_refresh` is the `data_as_of` source** the issue AC requires.
- **HSE data backing — `packages/worldenergydata-bsee/src/worldenergydata/hse/database/models.py`**: `HSEIncident` (`:24`, → incidents), `ViolationIncident` (`:266`, `penalty_amount`/`penalty_status` → penalties), `SafetyStatistic` (`:313`, → statistics), `ToxicRelease` (`:407`, → EPA TRI), plus importers/acquirers (`hse/importers/`, `hse/acquirers/`). So all four #363 query surfaces (incidents/penalties/statistics/epa_tri) have table backing; **OSHA** lives in `osha_importer.py`/`osha_acquirer.py` but #363 gates it on "once dedup ships". `hse/__init__.py` exports models+importers but **no query API**.
- **Shared base home — `packages/worldenergydata-core/src/worldenergydata/`** ships the `worldenergydata.common` namespace (`common/logging.py:get_logger`). marine_safety depends on `worldenergydata-core` (`pyproject.toml:33`); bsee does too. **A base importable by both marine_safety and bsee must live in core** (`worldenergydata.common.query_api`) to avoid a cross-package cycle.
- **Registry — `docs/registry/workflows.yaml`**: already `schema_version: 2`, `invocation: "uv run python -m worldenergydata {input}"`, with `bsee-*`/`fdas`/etc. rows carrying `outputs:`/`test:`/`data_source:`. **The #3295 v2 reconcile is already satisfied here** — this plan only ADDS optional per-row `result:` descriptors (for the rows it demos), no schema bump.

### Standards
Not applicable — harness/contract code, not an engineering calculation. No standards-derived constants are introduced, so no `Citation` sidecar per `.claude/rules/calc-citation-contract.md`. (`provenance.standard_revisions` stays `[]` for these workflows.)

### LLM Wiki pages consulted
None — contract/infra/query-surface work, no domain knowledge authored. `Client: N/A`.

### Documents consulted
- Epic [#3281](https://github.com/vamseeachanta/workspace-hub/issues/3281) — "Deterministic Workflow API"; #3286 is the worldenergydata adoption child.
- [#3282 plan](2026-06-27-issue-3282-resultenvelope-run-workflow.md) — `ResultEnvelope` dataclass, `run_workflow` over the #3297 embed path, `ResultLocator`/`extract_result` (glob injected root, exclude `save_cfg` dump), `input_hash`/`result_hash`/`code_version`/`compute_reproducible`. **The primitives #3286 imports.**
- [#3297 plan](2026-06-28-issue-3297-engine-embeddability.md) — `engine(embed=True, root_folder=, log_to_file=)` + `ConfigureApplicationInputs.configure_embed`. **wed's engine uses the SAME `ConfigureApplicationInputs`**, so once #3297 lands, wed's engine can call `configure_embed` too — the wed embed edit is a thin mirror.
- [#3295 plan](2026-06-28-issue-3295-registry-schema-v2-reconcile.md) — schema v2 additive superset; wed registry already conforms.
- [#3284 plan](2026-06-28-issue-3284-discovery-manifest.md) — discovery manifest aggregates per-repo registries; wed's already-v2 registry + the new `result:` descriptors feed it. Not a dependency; documented for downstream awareness.
- wed [#363](https://github.com/vamseeachanta/worldenergydata/issues/363) — `hse_api` parity with marine_safety. **`status:plan-approved`, lane:claude.** Heavy ACs (async pooling, Pydantic config, CLI bridge, notebook, EPA-TRI 51.5K live, OSHA-post-dedup) with **hard data dependencies**: wed **#359** (catalog wiring) + HSE DB population (statistics stubs 53 KB, OSHA dedup unverified, EPA-TRI field-drop per WRK-012). **Scoping consequence below.**

### Gaps identified (what #3286 must build)
1. **No reusable typed-query base** — marine_safety + bsee each hand-roll the same filter-normalization. Greenfield: `worldenergydata.common.query_api.TypedQuery` (+ `FilterSpec`).
2. **wed's engine has no embed path** — needed so a wed workflow runs side-effect-free for `run_workflow`. Greenfield edit mirroring #3297, on `worldenergydata.engine.engine`.
3. **No wed `run_workflow`** — #3282's `run_workflow` drives the *assetutilities* engine, not wed's. Greenfield: `worldenergydata.workflow_api.run_workflow` reusing #3282's envelope/locator/hashing primitives but driving wed's embeddable engine.
4. **No `JobResult → ResultEnvelope` adapter** — greenfield: `worldenergydata.scheduler.envelope_adapter`.
5. **No `hse_api`** — greenfield query surface on the new base + `wed.hse_api` lazy wiring; **scoped** (see Risks/Open) to the query-surface ACs of #363, deferring its live-data/CLI/notebook/async ACs to #363's own #359 + DB-population dependencies.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3286` — OPEN — wf-api(worldenergydata) adopt envelope (this issue); labels `status:needs-plan`, `lane:codex`, `domain:workflow-standardization`.
- `#3281` — OPEN — EPIC Deterministic Workflow API.
- `#3297` — OPEN / plan-review — engine embeddability (PREREQ).
- `#3282` — OPEN / plan-review — ResultEnvelope + run_workflow (PREREQ).
- `#3295` — OPEN — registry schema v2 reconcile (co-dep, wed already conforms).
- wed `#363` — OPEN / `status:plan-approved` — hse_api parity (the issue #3286 closes "on the generalized base").

**File existence** (`ls`/`find` 2026-06-28):
- EXISTS: `packages/worldenergydata-marine_safety/src/worldenergydata/marine_safety/api.py` (the generalize source).
- EXISTS: `packages/worldenergydata-scheduler/src/worldenergydata/scheduler/jobs/base.py` (`JobResult`), `.../scheduler/scheduler.py`.
- EXISTS: `packages/worldenergydata-bsee/src/worldenergydata/hse/database/models.py` (HSEIncident/ViolationIncident/SafetyStatistic/ToxicRelease), `hse/__init__.py` (no api).
- EXISTS: `packages/worldenergydata-core/src/worldenergydata/common/` (shared `worldenergydata.common` namespace).
- EXISTS: `docs/registry/workflows.yaml` (schema_version 2, invocation present).
- MISSING (this plan creates): `worldenergydata/common/query_api/base.py`, `worldenergydata/workflow_api/`, `worldenergydata/scheduler/envelope_adapter.py`, `hse/api.py`, `wed.hse_api` wiring.

**Line excerpts:**
```
# marine_safety/api.py — the repeated normalization the base extracts
143-148: src_list = sources if sources elif source -> [source]
149-155: vt_list  = vessel_types if ... elif vessel_type -> [vessel_type]
170-175: if year is not None: sy = ey = year          # single-year shorthand
280:     incidents = IncidentsQuery()                  # module singleton

# scheduler/jobs/base.py — JobResult + _metadata.json
38-44:  JobResult(job_name, start_time, end_time, status, records_updated, error_msg, retryable=True)
117:    "last_refresh": datetime.now(tz=timezone.utc).isoformat()   # -> provenance.data_as_of

# engine.py — wed engine, separate + no embed param
44:     def engine(inputfile=None, cfg=None, config_flag=True) -> dict
60-72:  app_manager.configure(...) ; fm.router(...) ; configure_result_folder(None, cfg_base)
79-135: basename dispatch -> bsee/sodir/texas_rrc/fdas/marine_safety/... wed routers
```

**Reproduction proofs** (Step 1.5):
```
$ cd /mnt/local-analysis/worldenergydata && .venv/bin/python scratchpad/probe_3286.py
MARINE_OK rows= 50 cols= ['source', 'incident_id', 'date', 'incident_type', 'vessel_type', 'region']
HSE_API_ABSENT: module 'worldenergydata' has no attribute 'hse_api'
```
- Reproduced at: 2026-06-28 (venv `/.venv/bin/python`; `uv run` not required — `.venv` resolves the namespace packages).
- Confirms: (a) `wed.marine_safety_api.incidents.query(source="maib")` is a **live, working** typed-query surface returning 50 rows with the documented columns — the base must preserve this behavior byte-for-byte; (b) `wed.hse_api` genuinely **does not exist** today (the #363 gap is real, not already-shipped).
- Failure mode matches issue claim: YES.

(Distinct sources: issue body + #3282 plan + #3297 plan + #3295 plan + #363 issue + marine_safety/api.py + scheduler base.py + engine.py + hse models.py + wed `__init__.py` + registry = 11.)

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3286-worldenergydata-adopt-envelope.md |
| Prereq plan (#3297) | docs/plans/2026-06-28-issue-3297-engine-embeddability.md |
| Prereq plan (#3282) | docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md |
| Typed-query base | `worldenergydata-core/src/worldenergydata/common/query_api/base.py` |
| Base package init | `worldenergydata-core/src/worldenergydata/common/query_api/__init__.py` |
| wed runner (consumes assetutilities primitives) | `worldenergydata/src/worldenergydata/workflow_api/runner.py` + `__init__.py` |
| wed engine embed edit (mirror #3297) | `worldenergydata/src/worldenergydata/engine.py` |
| Scheduler adapter | `worldenergydata-scheduler/src/worldenergydata/scheduler/envelope_adapter.py` |
| marine_safety re-expressed on base | `worldenergydata-marine_safety/src/worldenergydata/marine_safety/api.py` |
| HSE query API | `worldenergydata-bsee/src/worldenergydata/hse/api.py` |
| HSE api wiring | `worldenergydata-bsee/src/worldenergydata/hse/__init__.py`, `worldenergydata/src/worldenergydata/__init__.py` |
| Tests | `worldenergydata/tests/workflow_api/`, `.../tests/common/test_query_api_base.py`, `.../tests/hse/test_hse_api.py`, `.../tests/scheduler/test_envelope_adapter.py`, `.../tests/marine_safety/test_api_on_base.py` |
| Plan reviews | scripts/review/results/2026-06-28-plan-3286-{claude,codex,gemini}.md |

> **Not owned here:** `assetutilities/src/assetutilities/workflow_api/*` and `.../engine.py`/`ApplicationManager.py` — those are #3282/#3297. #3286 only imports/calls them.

---

## Deliverable

worldenergydata adopts the epic-#3281 envelope contract: (1) a reusable `worldenergydata.common.query_api.TypedQuery` base that extracts the marine_safety filter-normalization boilerplate and exposes an optional `query_envelope() -> ResultEnvelope` path; (2) `wed.marine_safety_api.incidents` re-expressed on that base as the reference (behavior unchanged — same 50-row result); (3) `wed.hse_api` (incidents/penalties/statistics/epa_tri query methods) built on the base, closing the **query-surface** portion of wed#363; (4) `worldenergydata.workflow_api.run_workflow(workflow_id, params=None, cfg=None) -> ResultEnvelope` driving a wed workflow (e.g. `bsee-production-summary`) side-effect-free via a wed engine embed path mirroring #3297, reusing #3282's `ResultEnvelope`/`ResultLocator`/hashing primitives; and (5) `worldenergydata.scheduler.envelope_adapter.job_result_to_envelope(JobResult, metadata_path=...) -> ResultEnvelope` with `provenance.data_as_of` populated from `_metadata.json`. All TDD-covered. **No assetutilities edits owned here.**

---

## Pseudocode

```python
# ── worldenergydata/common/query_api/base.py ──────────────────────
@dataclass(frozen=True)
class FilterSpec:
    name: str                 # canonical plural field, e.g. "sources"
    singular: str | None      # e.g. "source"  (None => no singular alias)
    kind: str                 # "list" | "scalar" | "year"   ("year" enables single-year shorthand)

class TypedQuery(ABC):
    """Reusable typed-query base. Subclasses declare `filters` + implement `_execute`.
    Generalizes the marine_safety/bsee query surfaces; OPTIONALLY emits a ResultEnvelope."""
    query_id: str             # e.g. "marine_safety.incidents", "hse.incidents"
    filters: list[FilterSpec]
    result_columns: list[str] # documented output schema (documentary)

    def _normalize(self, **kwargs) -> dict:
        out, extra = {}, dict(kwargs)
        for f in self.filters:
            if f.kind == "list":
                plural = extra.pop(f.name, None)
                single = extra.pop(f.singular, None) if f.singular else None
                out[f.name] = list(plural) if plural else ([single] if single else None)
            elif f.kind == "year":            # start_year/end_year + single `year` shorthand
                y  = extra.pop("year", None)
                sy = extra.pop("start_year", None); ey = extra.pop("end_year", None)
                out["start_year"], out["end_year"] = (y, y) if y is not None else (sy, ey)
            else:                              # scalar
                out[f.name] = extra.pop(f.name, None)
        out["_passthrough"] = extra           # remaining kwargs forwarded (e.g. min_amount)
        return out

    @abstractmethod
    def _execute(self, normalized: dict) -> "pd.DataFrame": ...

    def query(self, **kwargs) -> "pd.DataFrame":
        return self._execute(self._normalize(**kwargs))   # behavior-preserving for marine_safety

    def query_envelope(self, *, data_as_of=None, **kwargs):
        # Lazy import keeps the base free of a hard assetutilities import until envelopes are requested.
        from assetutilities.workflow_api import ResultEnvelope
        from assetutilities.workflow_api.envelope import input_hash, code_version
        norm = self._normalize(**kwargs)
        df = self._execute(norm)
        return ResultEnvelope(
            workflow_id=self.query_id, status="ok",
            result={"kind": "dataframe", "records": int(len(df)),
                    "columns": list(df.columns)},                 # NOT the whole frame
            provenance={"code_version": code_version(), "standard_revisions": [],
                        "data_as_of": data_as_of, "input_hash": input_hash(_hashable(norm))},
            determinism={"result_hash": _df_content_hash(df),     # sha256 of canonical CSV bytes
                         "reproducible": None},                   # query determinism not asserted here
            confidence=None, warnings=[])

# ── marine_safety/api.py (re-expressed) ───────────────────────────
class IncidentsQuery(TypedQuery):
    query_id = "marine_safety.incidents"
    filters = [FilterSpec("sources","source","list"),
               FilterSpec("vessel_types","vessel_type","list"),
               FilterSpec("incident_types","incident_type","list"),
               FilterSpec("regions","region","list"),
               FilterSpec("years",None,"year")]
    result_columns = ["source","incident_id","date","incident_type","vessel_type",
                      "region","fatalities","injuries","severity","description"]
    def __init__(self, importer_config=None):
        from worldenergydata.marine_safety.cross_database import CrossDatabaseAnalyzer
        self._analyzer = CrossDatabaseAnalyzer(importer_config=importer_config)
    def _execute(self, n):
        from worldenergydata.marine_safety.cross_database import CrossDatabaseQuery
        q = CrossDatabaseQuery(sources=n["sources"] or ["maib","imo","emsa","tsb"],
                               incident_types=n["incident_types"], vessel_types=n["vessel_types"],
                               start_year=n["start_year"], end_year=n["end_year"], regions=n["regions"])
        return self._analyzer.query(q).data
    # trends/top_types/correlations/risk_hotspots UNCHANGED (delegate to analyzer)
incidents = IncidentsQuery()    # singleton preserved -> wed.marine_safety_api.incidents

# ── hse/api.py (NEW, on the base) ─────────────────────────────────
class IncidentsQuery(TypedQuery):     # query_id="hse.incidents"; _execute -> HSEIncident query / sample fallback
class PenaltiesQuery(TypedQuery):     # query_id="hse.penalties"; ViolationIncident (penalty_amount/min_amount passthrough)
class StatisticsQuery(TypedQuery):    # query_id="hse.statistics"; SafetyStatistic
class EpaTriQuery(TypedQuery):        # query_id="hse.epa_tri"; ToxicRelease (naics/chemical_carcinogen passthrough)
incidents, penalties, statistics, epa_tri = IncidentsQuery(), PenaltiesQuery(), StatisticsQuery(), EpaTriQuery()

# ── worldenergydata/engine.py (embed edit, mirror #3297) ──────────
def engine(inputfile=None, cfg=None, config_flag=True,
           embed=False, root_folder=None, log_to_file=True) -> dict:
    ... resolve basename ...
    if embed:                                          # NEW path — honors cfg, routes writes under root
        cfg_base = app_manager.configure_embed(cfg, library_name, basename,
                                               root_folder=root_folder, log_to_file=log_to_file)
        cfg_base = FileManagement().router(cfg_base)
    elif config_flag:                                  # UNCHANGED default path (byte-identical to today)
        ...existing app_manager.configure + fm.router + configure_result_folder...
    else:
        cfg_base = cfg
    ...UNCHANGED basename dispatch to wed routers (bsee/fdas/marine_safety/...)...
    return cfg_base

# ── worldenergydata/workflow_api/runner.py (consumes #3282 primitives) ──
def run_workflow(workflow_id=None, params=None, cfg=None, verify_reproducible=False) -> "ResultEnvelope":
    from assetutilities.workflow_api import ResultEnvelope
    from assetutilities.workflow_api.runner import ResultLocator, extract_result, build_cfg
    from assetutilities.workflow_api.envelope import input_hash, result_hash, code_version, compute_reproducible
    from worldenergydata.engine import engine
    try:
        if cfg is None:
            row = _resolve_wed_registry_row(workflow_id)   # docs/registry/workflows.yaml
            cfg = build_cfg(row, params); locator = ResultLocator.from_row(row)
        else:
            row = None; locator = ResultLocator.default_for(cfg)
        ihash = input_hash(cfg)
        def _once():
            root = tempfile.mkdtemp(prefix="wed_wf_")
            try:
                cb = engine(cfg=copy.deepcopy(cfg), embed=True, root_folder=root, log_to_file=False)
                payload, warns = extract_result(cb, locator, root)   # glob root, EXCLUDE save_cfg dump
                return payload, warns, result_hash(payload)
            finally:
                shutil.rmtree(root, ignore_errors=True)
        payload, warns, rhash = _once()
        repro = compute_reproducible(_once, rhash, verify_reproducible)   # None unless asked
        return ResultEnvelope(workflow_id or "(inline-cfg)", "ok", payload,
            {"code_version": code_version(), "standard_revisions": [], "data_as_of": None, "input_hash": ihash},
            {"result_hash": rhash, "reproducible": repro}, None, warns)
    except Exception as e:
        return ResultEnvelope(workflow_id or "(inline-cfg)", "error", {},
            {"code_version": code_version(), "standard_revisions": [], "data_as_of": None, "input_hash": None},
            {"result_hash": None, "reproducible": None}, None, [str(e)])

# ── scheduler/envelope_adapter.py ─────────────────────────────────
_STATUS_MAP = {"success": "ok", "skipped": "ok", "failure": "error"}
def job_result_to_envelope(result: "JobResult", *, metadata_path=None, input_hash_value=None) -> "ResultEnvelope":
    from assetutilities.workflow_api import ResultEnvelope
    from assetutilities.workflow_api.envelope import code_version
    warnings = []
    if result.status == "skipped": warnings.append("job skipped (disabled)")
    if result.error_msg:           warnings.append(result.error_msg)
    data_as_of = _read_last_refresh(metadata_path)   # parse _metadata.json["last_refresh"]; None if absent
    return ResultEnvelope(
        workflow_id=result.job_name, status=_STATUS_MAP.get(result.status, "error"),
        result={"records_updated": result.records_updated,
                "start_time": result.start_time.isoformat(), "end_time": result.end_time.isoformat(),
                "duration_s": (result.end_time - result.start_time).total_seconds(),
                "retryable": result.retryable},
        provenance={"code_version": code_version(), "standard_revisions": [],
                    "data_as_of": data_as_of, "input_hash": input_hash_value},
        determinism={"result_hash": None, "reproducible": None},   # network refresh = non-deterministic, honest None
        confidence=None, warnings=warnings)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `worldenergydata-core/src/worldenergydata/common/query_api/__init__.py` | export `TypedQuery`, `FilterSpec` |
| Create | `worldenergydata-core/src/worldenergydata/common/query_api/base.py` | `TypedQuery` ABC + `FilterSpec` + `_df_content_hash` + `query_envelope` (lazy assetutilities import) |
| Modify | `worldenergydata-marine_safety/src/worldenergydata/marine_safety/api.py` | re-express `IncidentsQuery` on `TypedQuery`; preserve `incidents` singleton + analytic helpers + exact query behavior |
| Create | `worldenergydata-bsee/src/worldenergydata/hse/api.py` | `IncidentsQuery`/`PenaltiesQuery`/`StatisticsQuery`/`EpaTriQuery` on the base + singletons |
| Modify | `worldenergydata-bsee/src/worldenergydata/hse/__init__.py` | export the api module / singletons |
| Modify | `worldenergydata/src/worldenergydata/__init__.py` | lazy `wed.hse_api` attribute in `__getattr__` (mirror `marine_safety_api`) |
| Modify | `worldenergydata/src/worldenergydata/engine.py` | add `embed`/`root_folder`/`log_to_file` params + `configure_embed` path (mirror #3297); default path byte-identical |
| Create | `worldenergydata/src/worldenergydata/workflow_api/__init__.py` | export `run_workflow` |
| Create | `worldenergydata/src/worldenergydata/workflow_api/runner.py` | `run_workflow` + `_resolve_wed_registry_row`; reuses assetutilities `ResultLocator`/`extract_result`/`build_cfg`/hashing |
| Create | `worldenergydata-scheduler/src/worldenergydata/scheduler/envelope_adapter.py` | `job_result_to_envelope` + `_read_last_refresh` |
| Modify | `worldenergydata/docs/registry/workflows.yaml` | add optional per-row `result:` descriptor for the demoed row(s) (e.g. `bsee-production-summary` → `result: {kind: files}`) — additive, no schema bump |
| Create | `worldenergydata/tests/common/test_query_api_base.py` | base normalization/envelope TDD |
| Create | `worldenergydata/tests/marine_safety/test_api_on_base.py` | behavior-preservation regression |
| Create | `worldenergydata/tests/hse/test_hse_api.py` | hse query-surface TDD |
| Create | `worldenergydata/tests/workflow_api/test_runner.py` | run_workflow→envelope + side-effect-freeness TDD |
| Create | `worldenergydata/tests/scheduler/test_envelope_adapter.py` | JobResult→envelope + data_as_of TDD |
| Update | docs/plans/README.md | index row |

> **Dependency, not owned here:** `assetutilities/src/assetutilities/workflow_api/*` (#3282) and `assetutilities/.../engine.py` + `ApplicationManager.py` `configure_embed` (#3297).

---

## TDD Test List

| Test name | What it verifies | Input | Output |
|---|---|---|---|
| test_filterspec_list_collapses_singular_and_plural | `_normalize` collapses `source`→`["src"]` and prefers plural when both given | source="maib" / sources=[..] | `sources` list |
| test_filterspec_year_shorthand | single `year` sets start==end==year; explicit start/end pass through | year=2022 | start_year==end_year==2022 |
| test_normalize_passthrough_extra_kwargs | unknown kwargs land in `_passthrough` (e.g. `min_amount`) | min_amount=1000 | `_passthrough["min_amount"]==1000` |
| test_query_delegates_to_execute | `query()` calls `_execute(_normalize(...))` once | stub subclass | execute called with normalized dict |
| test_query_envelope_shape | `query_envelope()` returns a `ResultEnvelope` with records/columns result + populated provenance.input_hash + determinism.result_hash; reproducible is None | stub | envelope fields present |
| test_query_envelope_result_hash_content_sensitive | changing one cell flips `determinism.result_hash`; identical frames match | two frames | different-then-equal hash |
| **test_marine_safety_query_unchanged** | `wed.marine_safety_api.incidents.query(source="maib")` on the base returns the SAME rows/columns as pre-refactor (golden: 50 rows, 10 cols) | source="maib" | 50 rows, documented columns |
| test_marine_safety_helpers_unchanged | `trends`/`top_types`/`correlations`/`risk_hotspots` still delegate and return same shapes | query df | unchanged outputs |
| test_hse_incidents_query_returns_typed_df | `wed.hse_api.incidents.query(operator=..., year=..., severity=...)` returns a DataFrame with documented HSE columns | filters | DataFrame |
| test_hse_penalties_min_amount | `penalties.query(min_amount=10000)` filters `penalty_amount >= 10000` (passthrough) | min_amount | filtered rows |
| test_hse_statistics_query | `statistics.query(year=..., metric=..., grouping=...)` returns grouped stats | filters | DataFrame |
| test_hse_epa_tri_query | `epa_tri.query(naics=..., chemical_carcinogen=...)` over ToxicRelease | filters | DataFrame |
| test_hse_api_lazy_attr | `import worldenergydata as wed; wed.hse_api.incidents` resolves via `__getattr__` (was AttributeError pre-change) | attr access | singleton, no error |
| test_run_workflow_wed_returns_envelope | `run_workflow("bsee-production-summary")` → `ResultEnvelope(status="ok")` with `kind:files` payload from the injected root | registry id | ok envelope, populated result |
| test_run_workflow_writes_nothing_outside_tempdir | wed run writes nothing outside its `mkdtemp` root; repo `examples/.../outputs/` unchanged before/after; no `.log`/`logs/` | run + dir snapshot | nothing leaked |
| test_run_workflow_unknown_id_error_envelope | unknown id → `status="error"`, message in warnings (fail-closed, not raised) | "nope" | error envelope |
| test_run_workflow_excludes_save_cfg_dump | the `save_cfg` `<file_name>.yml` dump is excluded from payload + result_hash (inherits #3282 `extract_result`) | wed run | dump absent; hash stable across two roots |
| test_envelope_adapter_success_maps_ok | `JobResult(status="success")` → `ResultEnvelope(status="ok")` with records_updated in result | success JobResult | ok envelope |
| test_envelope_adapter_failure_maps_error | `status="failure"` + error_msg → `status="error"`, error_msg in warnings | failure JobResult | error envelope |
| test_envelope_adapter_skipped_maps_ok_with_warning | `status="skipped"` → `status="ok"` + "job skipped" warning | skipped JobResult | ok + warning |
| **test_envelope_adapter_data_as_of_from_metadata** | `_metadata.json["last_refresh"]` populates `provenance.data_as_of`; absent file → `None` | JobResult + metadata path | data_as_of == last_refresh |
| test_envelope_adapter_determinism_none | scheduler envelopes carry `result_hash=None`, `reproducible=None` (network refresh, honest) | any JobResult | both None |

---

## Acceptance Criteria

- [ ] **Prereqs landed:** #3297 (`engine(embed=True)` + `configure_embed`) and #3282 (`assetutilities.workflow_api` with `ResultEnvelope`, `run_workflow`, `ResultLocator`, `extract_result`, `input_hash`/`result_hash`/`code_version`/`compute_reproducible`) are merged. #3286 does not merge before both.
- [ ] **Typed-query base** `worldenergydata.common.query_api.TypedQuery` + `FilterSpec` exists; extracts the singular/plural + single-year normalization; `query_envelope()` emits a contract-shaped `ResultEnvelope` (records/columns result, populated `provenance.input_hash`, content-sensitive `determinism.result_hash`, `reproducible=None`).
- [ ] **Behavior preserved (regression):** `wed.marine_safety_api.incidents.query(source="maib")` returns the SAME 50 rows / 10 columns as before the refactor; `trends`/`top_types`/`correlations`/`risk_hotspots` unchanged. Reproduction golden recorded in `test_marine_safety_query_unchanged`.
- [ ] **hse_api on the base:** `wed.hse_api.incidents/penalties/statistics/epa_tri .query(...)` return typed DataFrames on the generalized base, lazily wired through `worldenergydata.__init__.__getattr__` (mirrors `marine_safety_api`), with tests. **Scope boundary (see Open Decisions):** this closes the *query-surface* ACs of wed#363; its live-data/async-pooling/CLI-bridge/notebook ACs remain gated on wed#359 + HSE DB population and stay open under #363.
- [ ] **`run_workflow` for a wed workflow:** `worldenergydata.workflow_api.run_workflow("bsee-production-summary")` returns a populated `ResultEnvelope`, demonstrated by a passing test under the repo pytest harness, driven by a wed **engine embed path** (`engine(embed=True, root_folder=<mkdtemp>, log_to_file=False)`) that is **genuinely side-effect-free** (repo `examples/.../outputs/` byte-unchanged, no `.log`/`logs/`, tempdir rmtree'd). The wed-engine **default path is byte-identical to today** (`embed=False`).
- [ ] **Scheduler adapter:** `job_result_to_envelope(JobResult, metadata_path=...)` maps success→ok / failure→error / skipped→ok+warning, carries `records_updated`/timing in `result`, populates `provenance.data_as_of` from `_metadata.json["last_refresh"]` (None when absent), and keeps `determinism` honest (`result_hash=None`, `reproducible=None`).
- [ ] **No assetutilities edits owned here** — diff touches only worldenergydata packages (core/marine_safety/bsee/scheduler/root) + the wed registry + tests.
- [ ] `uv run pytest worldenergydata/tests/{common,marine_safety,hse,workflow_api,scheduler}/ -v` green; full wed suite shows no regression (note: use `.venv/bin/python -m pytest` per repo memory if `uv` is broken on the box).
- [ ] **Extra adoption gate** (analogous to assethold #3066): because the wed shared engine is edited, the code-stage cross-review is T3 (3 providers) and explicitly confirms the `embed=False` default path is unchanged. Recorded; not waived.
- [ ] Review artifacts posted under scripts/review/results/.

---

## Adversarial Review Summary

<!-- PENDING — no provider artifacts yet. Plan stays `draft` until a real review wave lands with no-MAJOR verdicts. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING (not approval-ready; not surfaced to `status:plan-review` until a no-MAJOR wave exists).

---

## Risks and Open Questions

- **Risk — hard dependency chain.** Critical path: **#3297 → #3282 → #3286**. The base's `query_envelope`, the runner, and the scheduler adapter all import from `assetutilities.workflow_api`, which does not exist until #3282 lands; the wed engine embed path needs `configure_embed` from #3297. Mitigation: the **dependency-free** pieces (the `TypedQuery` normalization, the marine_safety behavior-preservation refactor, the hse query DataFrames) are written + landable test-first independent of the envelope; the envelope-bound tests go green only after the prereqs land. Do not merge before both prereqs.
- **Risk — wed engine is a SECOND engine.** `run_workflow` from #3282 drives the *assetutilities* engine; a wed workflow (`bsee`, `fdas`, …) runs through `worldenergydata.engine.engine`. This plan adds a wed-side embed path (mirroring #3297) + a wed-side runner, **reusing** #3282's `ResultLocator`/`extract_result`/hashing primitives (NOT duplicating envelope logic). If #3282 later parametrizes `run_workflow` by an injectable engine, the wed runner collapses to a thin call — a clean follow-on, not a blocker.
- **Risk — wed-engine default-path regression.** The `embed=False` branch must stay byte-identical (every wed router depends on it; #3297's review found 2 wed fixtures pinned to the default `update_deep` clobber). Guardrail: `test_run_workflow_writes_nothing_outside_tempdir` + a default-path snapshot test; full-suite regression gate; T3 code-stage review (extra adoption gate).
- **Open Decision — placement of the typed-query base.** Recommended: `worldenergydata.common.query_api` in `worldenergydata-core` (lowest blast radius; both marine_safety and bsee already depend on core; keeps #3286 inside wed). **Alternative** (issue text "likely co-located with Child 1 in assetutilities"): promote the base into `assetutilities` so non-wed repos inherit it too. Recommend **wed-core now, promotion to assetutilities as a follow-on** once a 2nd repo needs it. Flag for user.
- **Open Decision — wed#363 scope boundary.** #363 is `status:plan-approved` with heavy ACs (async pooling, Pydantic config, CLI bridge `worldenergydata hse incidents query …`, `notebooks/quickstart_hse.py`, EPA-TRI 51.5K **live**, OSHA **post-dedup**) and **hard data dependencies** (wed#359 catalog wiring + HSE DB population; statistics stubs 53 KB, OSHA dedup unverified, EPA-TRI field-drop per WRK-012). #3286 should deliver the **query surface on the generalized base** (incidents/penalties/statistics/epa_tri `.query()` + `wed.hse_api` wiring + tests), testable offline against the DB models with a **synthetic/sample fallback mirroring marine_safety's default**. The live-data + CLI + notebook + async ACs stay under #363 gated on #359 + population. Confirm this split with the user (and whether #363 closes here or stays open for its remaining ACs).
- **Open Decision — HSE offline-testability.** marine_safety's `CrossDatabaseAnalyzer` ships a synthetic default; HSE has importers/DB but may have **no synthetic default**. To make `hse_api` tests hermetic (no live DB / no `/mnt/ace`), this plan adds a minimal synthetic HSE fixture (or an in-memory SQLite seed) behind the query surface. Confirm acceptable vs requiring a populated DB.
- **Risk — scheduler determinism semantics.** Scheduler jobs are network refreshes → non-deterministic; the adapter deliberately sets `result_hash=None`/`reproducible=None` rather than fabricating a hash. `data_as_of` comes from `_metadata.json["last_refresh"]`; `input_hash` is optional (caller may pass the job config hash). Documented, not a defect.
- **Risk — `uv`/env fragility on the box.** Repo memory notes `uv` is intermittently broken and `.venv/bin/python` is the reliable interpreter (namespace packages resolve under `.venv`). Reproduction used `.venv/bin/python`. Implementation/tests should fall back to `.venv/bin/python -m pytest` if `uv run` fails.
- **Risk — registry `result:` additive only.** wed registry is already schema_version 2; this plan only ADDS optional per-row `result:` descriptors for demoed rows. No schema bump, no collision with #3295.

---

## Complexity: T3

**T3** — five coupled deliverables across four packages (core, marine_safety, bsee/hse, scheduler) plus a shared-engine embed edit (blast radius across every wed router), TDD throughout, consuming an unland ed upstream contract (#3297 + #3282) and carrying an extra adoption cross-review gate. Foundational for worldenergydata's participation in the epic-#3281 discovery manifest (#3284).
