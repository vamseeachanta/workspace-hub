# Plan for #3287: wf-api(assethold) — adopt ResultEnvelope for the portfolio financial workflow

> **Status:** draft
> **Complexity:** T2 (new `workflow_api` surface in assethold + registry/example edits + provenance; reuses the shared #3282 envelope/helpers; **no engine edit**) — flagged for **T3-depth review** because it consumes the unlanded, owner-unapproved upstream contract (#3282/#3297) and crosses repo boundaries.
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3287
> **Epic:** https://github.com/vamseeachanta/workspace-hub/issues/3281
> **Depends on (hard):** #3282 (ResultEnvelope + run_workflow + result descriptor — at `status:plan-review`, owner-UNapproved) · #3297 (assetutilities engine embeddability — PREREQ of #3282) · #3066 (assethold engine wiring — **ALREADY LANDED**, see Reproduction)
> **Co-dependency:** #3295 (registry schema_version 2 superset reconcile) for the registry bump · #3284 (discovery manifest) consumes the wired registry row
> **Client:** N/A — no wiki content touched
> **Lane:** lane:codex (matches the issue's `lane:codex` label; heavy engineering — new runner surface + isolation plumbing)
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3287-claude.md | ...-codex.md | ...-gemini.md

---

## Upstream-contract dependency note (READ FIRST)

This plan **builds on, and does not redesign,** the upstream `ResultEnvelope` / `run_workflow` contract owned by **#3282** (`docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md`) and its prerequisite **#3297** (`docs/plans/2026-06-28-issue-3297-engine-embeddability.md`). That contract is **no-MAJOR at plan-review but NOT owner-approved**. Consequences enforced throughout this plan:

- This issue **cannot be implemented before #3282 and #3297 land** — the import `from assetutilities.workflow_api import ResultEnvelope` resolves to a package that **does not exist yet** (verified absent below). The envelope/determinism field set, the `result:` descriptor shape, and the determinism hashing semantics are **consumed exactly as #3282 specifies** (stdlib dataclass; `provenance.code_version = {package_version, git_sha}`; `result_hash` over file CONTENTS for `kind:files`; `reproducible` is `None` unless a double-run is requested; registry schema v2 superset with `invocation:` + per-row `result:`). This plan adds **zero** new fields to the envelope and proposes **no** change to #3282's API.
- The one **architectural decision this plan must make** — because #3282's `run_workflow` is hardwired to *assetutilities*' engine and assethold has its **own** `engine()` — is *how assethold reuses the contract*. It is raised as the lead Open Decision with a recommended, contract-preserving option; it is **not** a redesign of #3282.

---

## Resource Intelligence Summary

### Existing repo code (verified 2026-06-28 against `/mnt/local-analysis/assethold` @ `b6c8910`, and `/mnt/local-analysis/assetutilities`)

- **#3066 hard gate is ALREADY SATISFIED.** `assethold/src/assethold/engine.py:45-70` dispatches on `basename` with **equality** (`if basename == "stocks": … elif basename == "portfolio": …`) across **8 wired basenames** (`stocks`, `portfolio`, `options`, `property`, `risk_metrics`, `dividend_forecast`, `fundamentals`, `market_alerts`), with a fail-closed `else: raise Exception(... not found ... FAIL)`. The `if basename in "stocks":` **substring bug is gone**. Landed by `8d790c0 feat(workflows): wire 6 domains into engine + UV-workflow registry (workspace-hub#3066) (#55)`, on `origin/main`. **The issue body's premise ("engine routes only stocks", "substring bug") is stale — the gate is GREEN.**
- **Portfolio router — result-location design hole.** `assethold/src/assethold/modules/portfolio/portfolio.py:17-42` `PortfolioWorkflow.router(cfg)` reads `cfg["portfolio"]`, computes positions/allocation, writes two CSVs to **`cfg["portfolio"]["outputs"]["positions_csv"]` / `["allocation_csv"]`** (full paths from the input), and returns `record_outputs(cfg, "portfolio", [positions_file, allocation_file])`. The result locator is therefore `cfg["outputs"]["portfolio"]` = **a list of file paths** (`workflow_io.py:59-62`), not data — the exact `cfg[basename]`-holds-paths hole that #3282's `result:` descriptor (`kind: files`) is designed to close.
- **Side-effect coupling (cwd-relative writes).** `assethold/src/assethold/modules/workflow_io.py:19-22` `output_path(path)` = `Path(path)` (relative → resolved against **cwd**) + `mkdir(parents=True)`. The portfolio example's output paths are `examples/workflows/portfolio/outputs/*.csv`, so a default run **writes into the repo example tree**. There is **no embed/`root_folder` path on assethold's engine** (#3297 patches *assetutilities*' engine only). Isolation for `run_workflow` must therefore be supplied by this plan.
- **`save_application_cfg` cfg-dump.** `engine.py:72` calls `save_application_cfg(cfg_base)`; `assetutilities/src/assetutilities/common/utilities.py:259-265` writes `<Analysis.result_folder>/<Analysis.file_name>` (+ `.yml`) — observed as `portfolio-run.yml` in the outputs dir at Reproduction. This is the same cfg-dump-pollution concern #3282 handles by **excluding `<file_name>.yml`** from the file glob/hash; this plan reuses that exclusion.
- **Market inputs have NO as-of date.** The portfolio example carries static offline prices (`portfolio.prices: {VOO: 500.0, BRKB: 400.0}`) with **no date attached**. A repo-wide grep for `data_as_of|prices_as_of` over `src/` + `examples/` returns **only** an unrelated `tax_lots.py` `as_of` parameter — confirming **no provenance as-of field exists** for market inputs. Issue AC#3 requires one.
- **Registry exists (schema v1).** `assethold/docs/registry/workflows.yaml` has `schema_version: 1` and **7 rows** (`portfolio-offline`, `options-…`, `property-…`, `risk-metrics-…`, `dividend-forecast-…`, `fundamentals-…`, `market-alerts-…`), each with `basename`/`input`/`outputs`/`test`/`runtime: uv-python`. No top-level `invocation:`, no per-row `result:` descriptor, no `request_schema`/`response_schema`. No `SCHEMA.md` beside it.
- **Shared `workflow_api` is greenfield (the dependency).** `ls /mnt/local-analysis/assetutilities/src/assetutilities/workflow_api` → **No such file or directory**; `grep -rl "class ResultEnvelope|def run_workflow" /mnt/local-analysis/assetutilities/src` → **empty**. The contract import target does not exist yet; #3282 creates it.

### Standards
Not applicable — this is harness/contract code, not an engineering calculation. **No `Citation` sidecar is required** (per `.claude/rules/calc-citation-contract.md` "do NOT apply when … not a standard"): the portfolio computation uses no standards-derived constant. The provenance `standard_revisions` field is left empty (`[]`), matching #3282.

### LLM Wiki pages consulted
None — contract/infra work, no domain knowledge added. `Client: N/A`.

### Documents consulted
- Issue [#3287](https://github.com/vamseeachanta/workspace-hub/issues/3287) (this issue) — scope, hard-gate-on-#3066, AC (portfolio returns envelope; request/response schema rows + golden test; provenance carries data-as-of).
- Issue [#3066](https://github.com/vamseeachanta/workspace-hub/issues/3066) (OPEN, `status:needs-plan`) — the named hard gate; its scope (wire 6 domains + fix substring) is **already implemented** on assethold `origin/main` (commit `8d790c0`). The issue is still open/un-closed, but the *code state* it gates on exists.
- `docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md` — the **contract this plan consumes**: `ResultEnvelope` stdlib dataclass; `run_workflow(workflow_id, params=None, cfg=None) -> ResultEnvelope`; the embed-path isolation model; `result:` descriptor (`kind: in_memory | files`); content-hash determinism; v2 registry superset. #3282 **OWNS** the determinism fields + the `result:` descriptor.
- `docs/plans/2026-06-28-issue-3297-engine-embeddability.md` — PREREQ; adds `engine(embed=True, root_folder, log_to_file)` + `configure_embed` to the **assetutilities** engine. assethold's engine is **not** covered → this plan supplies cfg-level isolation instead (see Pseudocode).
- `docs/plans/2026-06-28-issue-3295-registry-schema-v2-reconcile.md` (per task brief) — owns the `schema_version: 2` additive superset, required top-level `invocation:`, reserved structured `request_schema`/`response_schema`. assethold's registry bump must land **after/with** #3295.
- #3284 (discovery manifest) — aggregates registries into a manifest of callable workflows; consumes the wired portfolio row.
- digitalmodel `docs/registry/workflows.yaml` — the v2 reference (`schema_version: 2`, top-level `invocation:`); the shape assethold aligns to.

### Gaps identified (each a testable claim)
- No `ResultEnvelope`-returning entrypoint for any assethold workflow (greenfield).
- No isolation mechanism for assethold's cwd-coupled, no-embed-path engine — must be built (cfg-level output redirection into a tempdir, since #3297 does not touch assethold's engine).
- No `data_as_of` provenance field for market inputs anywhere (grep-confirmed) — must be added to the portfolio input + extracted into `provenance.data_as_of`.
- Registry is `schema_version: 1` with no `invocation:` and no per-row `result:` descriptor — must be bumped to the v2 superset (co-dependent on #3295).
- No registry `SCHEMA.md` — must be created to document the `result:` shape + `data_as_of` provenance contract.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3287` — OPEN, `status:needs-plan`, `lane:codex`, `priority:low` — this issue.
- `#3066` — OPEN, `status:needs-plan`, `lane:claude` — the named hard gate; **code already landed** (commit `8d790c0`).
- `#3282` / `#3297` / `#3295` — the upstream contract (plan-review, owner-unapproved per task brief).

**#3066 already-wired engine** (`engine.py:45-70`):
```
45:    if basename == "stocks":
48:    elif basename == "portfolio":
51:    elif basename == "options":
...
69:    else:
70:        raise Exception(f"Analysis for basename: {basename} not found. ... FAIL")
```
```
$ git -C /mnt/local-analysis/assethold log --oneline -3 -- src/assethold/engine.py
c98a365 feat(market_alerts): live-quote → signals → alerts engine (achantas-data#134) (#57)
8d790c0 feat(workflows): wire 6 domains into engine + UV-workflow registry (workspace-hub#3066) (#55)
```

**Portfolio result-locator hole** (`portfolio.py:39-42`, `workflow_io.py:59-62`):
```
39:  positions_to_dataframe(positions).to_csv(positions_file, index=False)
40:  allocation_to_dataframe(allocation).to_csv(allocation_file, index=False)
42:  return record_outputs(cfg, "portfolio", [positions_file, allocation_file])
59:  def record_outputs(cfg, basename, paths): cfg["outputs"][basename] = [str(p) for p in paths]  # PATHS, not data
```

**cfg-dump + result_folder** (`utilities.py:260-265`):
```
260:  output_dir = cfg_base.Analysis["result_folder"]
262:  filename   = cfg_base.Analysis["file_name"]
265:  save_data.saveDataYaml(cfg_base, os.path.join(output_dir, filename), ...)   # writes <result_folder>/<file_name>.yml
```

**Greenfield dependency** (`ls`):
- MISSING: `/mnt/local-analysis/assetutilities/src/assetutilities/workflow_api/` → "No such file or directory" — the contract import target does not exist; #3282 creates it.

**No data_as_of for market inputs** (`grep -rn 'data_as_of\|prices_as_of' src/ examples/`): only `analysis/daily_strategy/tax_lots.py` (unrelated holding-period `as_of`); **zero** hits for market-price provenance → confirms the gap.

(Distinct sources: issue body + #3066 + #3282 plan + #3297 plan + #3295 plan + engine.py + portfolio.py + workflow_io.py + utilities.py + registry yaml + example input.yml = 11.)

---

## Step 1.5 — Reproduction

**Two behavioral claims under test:** (1) the issue's premise that "assethold engine routes only `stocks`"; (2) that the portfolio workflow is runnable and side-effecting (writes into the repo tree), with `cfg["outputs"]["portfolio"]` as a path-list result locator and a `save_application_cfg` cfg-dump polluting the output dir.

```
$ /mnt/local-analysis/assethold/.venv/bin/python /tmp/.../probe_portfolio.py
basename: portfolio
outputs key: {'portfolio': ['examples/workflows/portfolio/outputs/positions.csv',
                            'examples/workflows/portfolio/outputs/allocation.csv']}
result_folder: examples/workflows/portfolio/outputs
files in outputs dir: ['allocation.csv', 'portfolio-run.yml', 'positions.csv']
```
(probe = `os.chdir(assethold); engine(inputfile="examples/workflows/portfolio/input.yml")`.)

- Reproduced at: 2026-06-28.
- **Claim (1) — FALSE.** The engine routes `portfolio` (and 6 others), not only `stocks`. The issue's gating premise is stale; **#3066's wiring is already live** → the hard gate is satisfied. The plan proceeds on the *real* state, not the claimed one (per issue-planning-mode Step 1.5).
- **Claim (2) — CONFIRMED.** Portfolio runs; result locator is a **path list** (`cfg["outputs"]["portfolio"]`); outputs land **inside the repo example tree** (side-effecting, cwd-coupled); the dir also contains `portfolio-run.yml` = the `save_application_cfg` cfg-dump (`file_name: portfolio-run` + `.yml`). This validates the need for (a) the `result: {kind: files}` descriptor, (b) cfg-level tempdir isolation, and (c) cfg-dump exclusion from the content hash.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3287-assethold-adopt-envelope.md |
| Upstream contract (#3282) | docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md |
| Upstream prereq (#3297) | docs/plans/2026-06-28-issue-3297-engine-embeddability.md |
| Runner (assethold-local; reuses shared envelope/helpers) | `assethold/src/assethold/workflow_api/runner.py` |
| Package init (re-exports `run_workflow` + shared `ResultEnvelope`) | `assethold/src/assethold/workflow_api/__init__.py` |
| Provenance/data-as-of extractor | `assethold/src/assethold/workflow_api/provenance.py` |
| Registry (v2 superset: `invocation` + per-row `result` + `market_data_as_of`) | `assethold/docs/registry/workflows.yaml` |
| Registry schema doc | `assethold/docs/registry/SCHEMA.md` |
| Portfolio example (adds declared `data_as_of`) | `assethold/examples/workflows/portfolio/input.yml` |
| Tests | `assethold/tests/workflow_api/test_runner.py`, `test_provenance.py`, `test_registry.py` |
| Plan reviews | scripts/review/results/2026-06-28-plan-3287-{claude,codex,gemini}.md |

> **NOT in this change set:** `assethold/src/assethold/engine.py` (already wired by #3066 — untouched), and the shared `assetutilities/src/assetutilities/workflow_api/*` (created by #3282/#3297). This plan **imports** the shared `ResultEnvelope` + determinism helpers; it does not edit them.

---

## Deliverable

A `workflow_api` surface in **assethold** (`assethold.workflow_api.run_workflow`) that runs the **portfolio** financial workflow end-to-end and returns a shared `ResultEnvelope` (imported from `assetutilities.workflow_api`) — `status="ok"`, `result` = the declared `kind:files` payload (content-hashed CSVs, cfg-dump excluded), `provenance.data_as_of` = the declared market-price as-of date, `provenance.code_version = {package_version, git_sha}`, computed `input_hash`/`result_hash`, `reproducible` honest-`None`-unless-asked — all TDD-covered. The run is **side-effect-free** (writes only under a per-call tempdir that is `rmtree`'d, via cfg-level output redirection — **no assethold engine edit**). The registry adopts the v2 superset (`schema_version: 2`, top-level `invocation:`, per-row `result:` + `market_data_as_of`), documented in a new `SCHEMA.md`.

---

## Pseudocode

```python
# ── assethold/workflow_api/provenance.py ───────────────────────────────────
# data_as_of for MARKET inputs (issue AC#3). Portfolio prices are static/offline
# and carry no date today -> a declared field is required; fail-closed when a
# workflow declares market inputs (prices) but no as-of date.
def market_data_as_of(cfg, row) -> (value: str | None, warnings: list[str]):
    # precedence: cfg.portfolio.prices_as_of  ->  cfg.Analysis.data_as_of  ->  row.market_data_as_of
    as_of = (deep_get(cfg, "portfolio", "prices_as_of")
             or deep_get(cfg, "Analysis", "data_as_of")
             or row.get("market_data_as_of"))
    has_market_inputs = bool(deep_get(cfg, "portfolio", "prices"))
    if has_market_inputs and not as_of:
        return None, ["workflow declares market 'prices' but no data_as_of -> provenance.data_as_of is null"]
    return as_of, []

# ── assethold/workflow_api/runner.py ───────────────────────────────────────
# REUSE the #3282-owned shared machinery; supply assethold engine + registry.
from assetutilities.workflow_api import (
    ResultEnvelope, code_version, input_hash, result_hash, compute_reproducible, ResultLocator,
)
from assethold.engine import engine as assethold_engine

# Side-effect-freeness WITHOUT an assethold engine embed path (#3297 covers
# assetutilities ONLY). Achieved at the CFG LEVEL: redirect every declared output
# path + Analysis.result_folder under a throwaway tempdir, then glob+hash+rmtree.
PORTFOLIO_OUTPUT_KEYS = [("portfolio", "outputs", "positions_csv"),
                         ("portfolio", "outputs", "allocation_csv")]   # per-workflow redirect map

def redirect_outputs_under(cfg, root, output_keys):
    cfg = copy.deepcopy(cfg)
    cfg.setdefault("Analysis", {})["result_folder"] = root          # save_application_cfg dump -> <root>/<file_name>.yml
    for path_keys in output_keys:                                   # rewrite each declared output to <root>/<basename>
        leaf = os.path.basename(deep_get(cfg, *path_keys))
        deep_set(cfg, *path_keys, value=os.path.join(root, leaf))
    return cfg

def extract_result(cfg_base, root) -> (payload, warnings):
    # kind:files -> glob the injected root; EXCLUDE the save_application_cfg cfg-dump
    # <file_name>.yml (engine.py:72 / utilities.py:265) so result_hash is content-only.
    file_name = deep_get(cfg_base, "Analysis", "file_name", default="")
    cfg_dump  = os.path.abspath(os.path.join(root, file_name + ".yml"))
    emitted = sorted(p for p in glob.glob(os.path.join(root, "*"))
                     if os.path.isfile(p) and os.path.abspath(p) != cfg_dump)
    files, warns = [], []
    for p in emitted:
        with open(p, "rb") as fh:
            files.append({"basename": os.path.basename(p), "sha256": sha256(fh.read()).hexdigest()})
    if not files:
        warns.append(f"declared kind:files workflow emitted no files under {root}")
    return {"kind": "files", "outputs": files}, warns

def _run_once(cfg, output_keys):
    root = tempfile.mkdtemp(prefix="ahwf_")
    try:
        sandboxed = redirect_outputs_under(cfg, root, output_keys)
        cb = assethold_engine(cfg=AttributeDict(sandboxed), config_flag=True)   # assethold's OWN engine
        payload, warns = extract_result(cb, root)
        return payload, warns, result_hash(payload)
    finally:
        shutil.rmtree(root, ignore_errors=True)                                 # repo/example tree untouched

def run_workflow(workflow_id=None, params=None, cfg=None, verify_reproducible=False) -> ResultEnvelope:
    wid = workflow_id or "(inline-cfg)"
    try:                                                       # fail-closed from line 1
        row = resolve_registry_row(workflow_id) if cfg is None else lookup_row_for_cfg(cfg)
        cfg = build_cfg(row, params) if cfg is None else cfg   # load row.input, deep-merge params (params win)
        output_keys = output_keys_for(row)                     # PORTFOLIO_OUTPUT_KEYS for the portfolio row
        as_of, as_of_warns = market_data_as_of(cfg, row)
        ihash = input_hash(cfg)
        payload, warns, rhash = _run_once(cfg, output_keys)
        repro = compute_reproducible(lambda: _run_once(cfg, output_keys), rhash, verify_reproducible)
        prov  = {"code_version": code_version("assethold"), "standard_revisions": [],
                 "data_as_of": as_of, "input_hash": ihash}
        return ResultEnvelope(wid, "ok", payload, prov,
                              {"result_hash": rhash, "reproducible": repro}, None, warns + as_of_warns)
    except Exception as e:
        return ResultEnvelope(wid, "error", {},
                              {"code_version": code_version("assethold"), "standard_revisions": [],
                               "data_as_of": None, "input_hash": None},
                              {"result_hash": None, "reproducible": None}, None, [str(e)])
```

> **No `engine.py` pseudocode** — assethold's engine is already wired (#3066) and is **not** edited. Isolation is cfg-level; if `code_version`/`input_hash`/`result_hash`/`ResultLocator` are not exported by #3282's `workflow_api/__init__`, the implementation imports them from their defining module (`assetutilities.workflow_api.envelope`) — confirmed against the landed #3282 surface at implementation time.

---

## Registry change (v2 superset — co-dependent on #3295)

```yaml
# assethold/docs/registry/workflows.yaml
schema_version: 2                                       # was 1; align to the #3295 superset / digitalmodel
invocation: "uv run python -m assethold {input}"        # REQUIRED top-level; {input}-only substitution
repo: assethold
workflows:
  - id: portfolio-offline
    basename: portfolio
    input: examples/workflows/portfolio/input.yml
    outputs:                                            # DOCUMENTARY (expected count); runtime globs the injected root
      - examples/workflows/portfolio/outputs/positions.csv
      - examples/workflows/portfolio/outputs/allocation.csv
    result:                                             # #3282-OWNED descriptor shape (consumed, not redefined)
      kind: files
    market_data_as_of: "2026-06-27"                     # provenance hint for static offline prices (AC#3)
    test: uv run python -m assethold examples/workflows/portfolio/input.yml
    runtime: uv-python
  # ... remaining 6 rows: bumped to v2 form; `result:` optional (kind: files default); `market_data_as_of` only where market inputs exist ...
```

- `request_schema:` / `response_schema:` are **RESERVED by #3295** (structured, no `str` invariant) — this plan does **not** populate them.
- `SCHEMA.md` (new) documents: the `result:` descriptor (`kind: files` default vs `in_memory`); that `outputs:` is **documentary** (runtime globs the injected tempdir, excluding the `<file_name>.yml` cfg-dump); the required `invocation:` (+ `{input}`-only substitution; `deckhand/src/deckhand/capability_smoke.py` is the reference resolver per #3295); and the **`market_data_as_of` / `data_as_of` provenance contract** (declared per row/cfg; fail-soft-warn when market inputs lack an as-of date).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `assethold/src/assethold/workflow_api/__init__.py` | export `run_workflow`; re-export shared `ResultEnvelope` |
| Create | `assethold/src/assethold/workflow_api/runner.py` | `run_workflow`, registry resolution, `build_cfg`, cfg-level `redirect_outputs_under`, `_run_once` (assethold engine → glob → rmtree), `extract_result` (files-by-glob, cfg-dump excluded) |
| Create | `assethold/src/assethold/workflow_api/provenance.py` | `market_data_as_of` (data-as-of for market inputs; fail-soft-warn) |
| Modify | `assethold/docs/registry/workflows.yaml` | `schema_version: 2`; top-level `invocation:`; per-row `result:`; `market_data_as_of` |
| Create | `assethold/docs/registry/SCHEMA.md` | document `result:`, `outputs:`-documentary, `invocation:`, `data_as_of` contract |
| Modify | `assethold/examples/workflows/portfolio/input.yml` | add declared `portfolio.prices_as_of` (or `Analysis.data_as_of`) |
| Create | `assethold/tests/workflow_api/test_runner.py` | runner + isolation + locator + golden-hash TDD |
| Create | `assethold/tests/workflow_api/test_provenance.py` | data-as-of extraction + fail-soft-warn TDD |
| Create | `assethold/tests/workflow_api/test_registry.py` | v2 schema + invocation + result + market_data_as_of TDD |
| Update | docs/plans/README.md | add this plan to the Plan Index |

> **Dependency, not owned here:** `assetutilities/src/assetutilities/workflow_api/*` (`ResultEnvelope` + determinism helpers) is created by **#3282/#3297**; this plan imports it. assethold's `engine.py` is already wired by **#3066** and is **not** modified.

---

## TDD Test List

| Test name | What it verifies | Input | Output |
|---|---|---|---|
| test_run_workflow_portfolio_returns_envelope | portfolio id → populated `ResultEnvelope`, `status=="ok"`, `result.kind=="files"` | `run_workflow("portfolio-offline")` | ok envelope, 2 file digests |
| test_run_workflow_writes_nothing_outside_tempdir | **(isolation)** repo `examples/workflows/portfolio/outputs/` is byte-for-byte unchanged before/after; no stray files; temp root removed | run + dir snapshot | nothing written outside tempdir |
| test_extract_result_excludes_save_cfg_dump | the `portfolio-run.yml` cfg-dump is EXCLUDED from outputs + content hash | portfolio run | outputs exclude `*.yml`; hash stable across two tempdirs |
| test_result_hash_files_content_sensitive | changing a CSV's bytes flips `result_hash`; identical bytes (diff tempdir) → identical hash | two runs | different-then-equal hash |
| test_provenance_data_as_of_populated | declared `prices_as_of` → `provenance.data_as_of == "2026-06-27"` | portfolio cfg w/ as-of | as-of value present |
| test_provenance_data_as_of_missing_warns | market `prices` present but no as-of → `data_as_of is None` + warning (not silent) | cfg w/ prices, no date | warning appended |
| test_provenance_code_version_shape | `provenance.code_version` has `package_version` + `git_sha` keys (git_sha may be None) | envelope | both keys present |
| test_reproducible_default_none | `verify_reproducible=False` → `determinism.reproducible is None` (not True) | run w/o verify | None |
| test_reproducible_computed_true_on_double_run | `verify_reproducible=True` → `reproducible is True` via two isolated runs comparing file CONTENTS | portfolio | True |
| test_run_workflow_unknown_id_error_envelope | unknown id → `status=="error"` envelope (fail-closed, not raised) | `run_workflow("nope")` | error envelope w/ message |
| test_run_workflow_engine_error_envelope | a router exception → error envelope, not a raw traceback | cfg that makes router raise | error envelope w/ message |
| test_build_cfg_merges_params_over_example | `build_cfg(row, params)` loads `row.input` then deep-merges params (params win) | portfolio row + override | merged values |
| test_registry_schema_v2_invocation_result_asof | registry parses at `schema_version: 2`; top-level `invocation == "uv run python -m assethold {input}"`; portfolio row has `result.kind==files` + `market_data_as_of`; all 7 rows valid | current registry | version 2, fields present |
| test_golden_portfolio_result_hash | **(AC golden test)** portfolio run over the committed example yields a STABLE `result_hash` (pinned constant); a perturbed price → different hash | example input | matches golden; perturbation differs |

> **Ordering gate:** every test that calls `run_workflow` imports `ResultEnvelope`/helpers from `assetutilities.workflow_api` and is therefore **red until #3282/#3297 land**. The provenance + registry-schema tests (`test_provenance_*`, `test_registry_schema_*`, `test_build_cfg_*`) are independent of the shared package and can go green earlier — they pin the assethold-side surface. Written test-first regardless.

---

## Acceptance Criteria

- [ ] **Gate check recorded:** #3066's engine wiring is live (verified — `engine.py:45-70`, commit `8d790c0`); #3282 and #3297 have **landed** before this issue is implemented (the `assetutilities.workflow_api` import resolves).
- [ ] `run_workflow("portfolio-offline")` returns a populated shared `ResultEnvelope` (`status=="ok"`, `result.kind=="files"` with the two portfolio CSVs content-hashed), demonstrated by a passing test under the assethold pytest harness.
- [ ] **Side-effect-free:** a run writes nothing outside its per-call `tempfile.mkdtemp()` root (repo `examples/.../outputs/` unchanged before/after; root `rmtree`'d) — isolation via cfg-level output redirection, **no assethold engine edit**.
- [ ] **Provenance carries data-as-of for market inputs (AC#3):** `provenance.data_as_of` is the declared portfolio `prices_as_of`; when market `prices` exist without an as-of date, `data_as_of is None` **and** a warning is emitted (fail-soft, not silent).
- [ ] Determinism fields computed, not hardcoded: `input_hash`/`result_hash` present; `result_hash` over file CONTENTS (cfg-dump `*.yml` excluded); `reproducible` is `None` unless `verify_reproducible=True` (then a measured double-run bool); `provenance.code_version == {package_version, git_sha}`.
- [ ] **request/response schema rows + golden test (AC#2):** registry adopts the v2 superset (`schema_version: 2`, top-level `invocation:`, per-row `result:`, `market_data_as_of`); `request_schema`/`response_schema` left RESERVED for #3295; `SCHEMA.md` created; the golden `result_hash` test (`test_golden_portfolio_result_hash`) pins the portfolio output and detects perturbation.
- [ ] All 7 existing registry rows still validate at v2; the registry bump lands **after/with #3295**.
- [ ] `uv run pytest tests/workflow_api/ -v` green; full assethold suite shows no regression (`tests/unit/test_engine.py`, `tests/test_portfolio.py` still pass).
- [ ] Review artifacts posted under scripts/review/results/.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING (re-draft if any MAJOR). Not approval-ready until populated with no-MAJOR verdicts; status stays `draft`. Implementation remains gated behind (a) USER approval and (b) **#3282 + #3297 landing first**, plus **#3295 co-landing** for the registry bump.

---

## Risks and Open Questions

- **OPEN DECISION (lead) — how assethold reuses the contract.** #3282's `run_workflow` is hardwired to *assetutilities*' engine, but assethold has its own `engine()`. Two options:
  - **Option A (recommended):** ship an **assethold-local** `run_workflow` (`assethold.workflow_api.run_workflow`) that **reuses** the shared `ResultEnvelope` + determinism helpers (imported from `assetutilities.workflow_api`) and drives assethold's own engine. Minimal coupling; preserves #3282 unchanged; the contract import splits into `from assethold.workflow_api import run_workflow` + re-exported `ResultEnvelope`. Diverges *slightly* from the literal `from assetutilities.workflow_api import run_workflow` line in the issue.
  - **Option B:** generalize the **shared** `run_workflow` to dispatch by registry `repo:`/`invocation:` to the target engine. Honors the literal import, but **edits the #3282 contract** (out of scope; owner-unapproved). Defer to a #3282 follow-up.
  - **Recommendation:** Option A — it satisfies AC#1 ("≥1 financial workflow returns a ResultEnvelope via run_workflow") without redesigning the upstream contract. **Flag for owner at approval.**
- **Risk — hard dependency on unlanded, owner-unapproved upstream (#3282 + #3297).** The shared `workflow_api` package does not exist yet (verified). This issue **cannot be implemented** until both land. If #3282's helper export surface differs from assumed (`code_version`/`input_hash`/`result_hash`/`ResultLocator` names), the runner adapts imports at implementation time. Critical path: **#3297 → #3282 → (#3295 for registry) → #3287**.
- **Risk — issue premise is stale (#3066 already landed).** The issue gates on "#3066 wires routing / fixes substring bug", but that code is already on `origin/main` (commit `8d790c0`); the engine routes 7 wired workflows with `==`. The gate is **GREEN**; #3066 the *issue* is still open/unclosed. No work is needed against #3066 here — only the *code state* matters. Surfaced so the owner doesn't block #3287 waiting on a closed-in-effect gate.
- **Risk — assethold has NO engine embed path.** #3297 patches *assetutilities*' engine only; assethold's engine writes cwd-relative + a cfg-dump. Mitigation: cfg-level output redirection (`redirect_outputs_under`) into a tempdir — **no engine edit**, but the redirect map (`PORTFOLIO_OUTPUT_KEYS`) is **workflow-shape-specific**. Generalizing to all 7 wired workflows is **future work**; this pilot covers **portfolio only**. Alternative (heavier, rejected for the pilot): add an `engine(embed=True, root_folder=...)` path to assethold's engine mirroring #3297 — flag as a follow-on if multi-workflow adoption is wanted.
- **Risk — cfg-dump pollution.** `save_application_cfg` writes `<file_name>.yml` into the result folder (observed: `portfolio-run.yml`). `extract_result` excludes it from the glob/hash (keyed on `Analysis.file_name`), mirroring #3282's fix. Generalization edge: a workflow whose *genuine* output is itself `<file_name>.yml` would be wrongly excluded — not the case for portfolio (CSV outputs). Documented.
- **Risk — data_as_of is a declared convention, not derived.** Static offline prices have no intrinsic date; `provenance.data_as_of` reflects what the input declares. When market inputs exist without a date, the run still succeeds but emits a warning and `data_as_of=None` (fail-soft). A future live-quote path (e.g., `market_alerts`) could stamp a real fetch timestamp — out of scope here.
- **Risk — registry reconciliation overlap with #3295.** This plan lands `schema_version: 2` + `invocation:` + per-row `result:` + `market_data_as_of` (all additive). #3295 owns the cross-registry reconcile + `request_schema`/`response_schema` reservation. Land **after/with #3295** to avoid a meaning collision; if #3295 renames a field, a fast follow-up adjusts.
- **Risk — heavy/slow import.** assethold's engine pulls assetutilities (plotly etc.) and emits a `requests_html` warning (~tens of seconds cold). Reproduction used the repo `.venv`. Implementation re-verifies under the assethold pytest harness; lazy-import follow-on if unacceptable. Not a blocker.

**Open Questions:**
1. Lead Open Decision above (Option A vs B) — needs owner sign-off.
2. Provenance field placement: `portfolio.prices_as_of` (workflow-scoped) vs `Analysis.data_as_of` (engine-scoped)? Plan supports both with precedence; recommend `Analysis.data_as_of` as the cross-workflow convention. Flag at approval.

---

## Complexity: T2

**T2** — one new small package (3 source files) + a registry bump + a schema doc + an example edit, TDD throughout, **reusing** the #3282 shared envelope/helpers with **zero engine edits** (isolation is cfg-level). Flagged for **T3-depth review** because it consumes an unlanded, owner-unapproved cross-repo contract (#3282/#3297) and must reconcile with #3295.
