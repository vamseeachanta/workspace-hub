# Plan for #3287: wf-api(assethold) — adopt ResultEnvelope for the portfolio financial workflow

> **Status:** draft
> **Complexity:** T2 (new `workflow_api` runner surface in assethold + registry/example edits + market data-as-of provenance; reuses the shared #3282 envelope/helpers AND the assethold engine embed-port delivered by #3308) — flagged for **T3-depth review** because it consumes three unlanded, owner-unapproved upstream contracts (#3282, #3308, and #3308's mirror-source #3297) and crosses repo boundaries.
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3287
> **Epic:** https://github.com/vamseeachanta/workspace-hub/issues/3281
> **Depends on (hard):** #3282 (ResultEnvelope + `run_workflow` + parameterized `code_version(package_name)` + determinism helpers — at `status:plan-review`, owner-UNapproved) · **#3308 (assethold engine embed-port — mirrors #3297 for assethold's OWN engine; PREREQ, `status:needs-plan`)** · #3066 (assethold engine wiring — **ALREADY LANDED**, commit `8d790c0`; see Reproduction)
> **Transitive / co-dependency:** #3297 (assetutilities embed-port — the mirror-source #3308 ports) · #3295 (registry `schema_version: 2` superset reconcile) for the registry bump · #3284 (discovery manifest) consumes the wired registry row (NOT a resolution dependency — see Cross-repo id decision)
> **Client:** N/A — no wiki content touched
> **Lane:** lane:codex (matches the issue's `lane:codex` label; heavy engineering — new runner surface consuming the embed-port)
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3287-claude.md | ...-codex.md | ...-gemini.md

---

## Upstream-contract dependency note (READ FIRST)

This plan **consumes, and does not redesign,** three upstream contracts. Per the re-locked contract (plan-review 2026-06-28) they are consumed **as specified**:

1. **#3282** (`docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md`) — provides the shared `assetutilities.workflow_api` package: `ResultEnvelope` (stdlib dataclass, **NO Pydantic**), the determinism helpers (`input_hash`, `result_hash` over file CONTENTS for `kind:files`, `compute_reproducible`), and the **parameterized** `code_version(package_name="assetutilities")` — adopters pass their **own** package name. This plan calls `code_version("assethold")`. **This is a consumption of the parameterized API delivered by the refined #3282 — there is no "#3282 unchanged" framing; #3282 already exposes `code_version(package_name)` (verified at the #3282 plan, `runner.py` helper).** assethold imports these shared types; it does **not** edit them.

2. **#3308** (`wf-api(assethold): engine embed-port — mirror #3297 for assethold's own engine`) — provides assethold's **OWN** engine embed path: `engine(cfg=..., embed=True, root_folder=<dir>, log_to_file=False)` + a `configure_embed(self, cfg, basename, root_folder, log_to_file=False)` that mirrors #3297 (honors the injected root, rebases `cfg["_config_dir_path"]`, routes **all** writes under `root_folder`, default byte-identical, and stamps assethold's own `code_version("assethold")`). **assethold has its OWN `engine()` — it does NOT use assetutilities' `run_workflow` or assetutilities' embed path.** #3287's isolation comes entirely from calling **this #3308 embed path**; this plan adds **no** cfg-level output-redirection of its own (the Wave-2 approach that returned MAJOR — see Adversarial Review Summary).

3. **#3295** — owns the registry `schema_version: 2` additive superset, the required top-level `invocation:` key, and the **reserved** structured `request_schema`/`response_schema` slots. assethold's registry bump lands after/with #3295.

The single **architectural decision this plan makes** — how assethold reuses the contract when it has its own engine — is **already locked** by the cross-cutting decision (owner-confirmed 2026-06-28): assethold ships an **assethold-local `run_workflow`** (`assethold.workflow_api.run_workflow`) that reuses the shared `ResultEnvelope` + determinism helpers and drives assethold's **own** engine via the **#3308 embed path**. This is no longer an open decision; it is the locked design (see Risks for the rationale, retained for reviewers).

---

## Resource Intelligence Summary

### Existing repo code (verified 2026-06-28 against `/mnt/local-analysis/assethold` @ `b6c8910`, `/mnt/local-analysis/assetutilities`)

- **#3066 hard gate is ALREADY SATISFIED.** `assethold/src/assethold/engine.py:34,45-70` dispatches on `basename` with **equality** (`if basename == "stocks": … elif basename == "portfolio": …`) across **8 wired basenames** (`stocks`, `portfolio`, `options`, `property`, `risk_metrics`, `dividend_forecast`, `fundamentals`, `market_alerts`), with a fail-closed `else: raise Exception(... not found ... FAIL)` at `:69-70`. The `if basename in "stocks":` **substring bug is gone**. Landed by `8d790c0 feat(workflows): wire 6 domains into engine + UV-workflow registry (workspace-hub#3066)`. **The issue body's premise ("engine routes only stocks", "substring bug") is stale — the gate is GREEN.**

- **assethold's engine signature is its OWN — NOT assetutilities'.** `engine.py:25` → `def engine(inputfile: str = None, cfg: dict = None, config_flag: bool = True) -> dict`. It has **NO** `ApplicationManager`, **NO** `configure()`, **NO** embed path today (`grep -rln "class.*ApplicationManager\|def configure_embed" assethold/src` → **empty**). It calls `FileManagement().router(cfg_base)` (`engine.py:36-39`) for the `file_management`-flagged config-relative routing, dispatches to the module router, then `save_application_cfg(cfg_base=cfg_base)` (`engine.py:72`). **This is exactly why #3308 exists** (a separate embed-port issue) — #3297's assetutilities embed path does not cover assethold's distinct engine. #3287 consumes #3308's `engine(embed=True, root_folder=, log_to_file=False)`.

- **THE ISOLATION GAP #3308 MUST CLOSE (load-bearing for AC#2).** The portfolio router writes its CSVs via `assethold/src/assethold/modules/workflow_io.py:19-22` `output_path(path) -> Path(path)` (+ `parent.mkdir`) — i.e. the **literal config string resolved against `cwd`**, consulting **neither** `_config_dir_path` **nor** `Analysis.result_folder`. `portfolio.py:37-38` calls `output_path(outputs["positions_csv"])` where `positions_csv = "examples/workflows/portfolio/outputs/positions.csv"` (`input.yml:14`). **Consequence:** a #3297-style `_config_dir_path`-only rebase (which `path_resolver.py:114` sets and `:38` reads) is **insufficient** to sandbox assethold's portfolio writes — `output_path` never reads `_config_dir_path`. For `engine(embed=True, root_folder=<tmp>)` to write portfolio CSVs **under** `<tmp>` (AC#2), **#3308's `configure_embed` must rebase assethold's `output_path` writers** (e.g. make `workflow_io.output_path` resolve relative paths under `_config_dir_path`/the injected root, OR rewrite `portfolio.outputs.*` under root). This is **#3308-owned**; #3287's isolation test (`test_run_workflow_writes_nothing_outside_tempdir`) is the **consumer assertion** that #3308 satisfied it. Surfaced as the lead Risk + a precise cross-issue handoff so #3308's plan/impl closes it.

- **`_config_dir_path` is real and config-relative (grounds the #3308/#3297 rebase target).** `assetutilities/src/assetutilities/common/path_resolver.py:114` sets `cfg["_config_dir_path"] = os.path.dirname(os.path.abspath(config_file_path))`; `:37-38,52` resolve relative paths via `cfg.get("_config_dir_path")` → … → `os.getcwd()` fallback. `PathResolver` is imported by `common/file_management.py` (the `fm.router` layer `engine.py:36-39` runs). So #3297's rebase (`cfg["_config_dir_path"] = root_folder`) IS load-bearing for routers that go through `path_resolver` — but assethold's `workflow_io.output_path` does **not** (gap above).

- **`save_application_cfg` cfg-dump.** `engine.py:72` calls `save_application_cfg(cfg_base)`; `assetutilities/src/assetutilities/common/utilities.py` writes `<Analysis.result_folder>/<Analysis.file_name>` (+`.yml`) — observed as `portfolio-run.yml` at Reproduction (`examples/workflows/portfolio/outputs/portfolio-run.yml` exists in the tree). In embed mode #3308's `configure_embed` rebases the result folder under `root_folder` (mirroring #3297 `configure_result_folder(root)`), so the cfg-dump lands under `<tmp>`; the runner **excludes** `<file_name>.yml` from the content glob/hash (same fix #3282 applies).

- **Portfolio result-locator hole.** `portfolio.py:42` returns `record_outputs(cfg, "portfolio", [positions_file, allocation_file])`; `workflow_io.py:59-62` `record_outputs` sets `cfg["outputs"]["portfolio"] = [str(p) …]` — i.e. `cfg["outputs"]["portfolio"]` is a **list of file PATHS**, not data. This is exactly the `cfg[basename]`-holds-paths hole the #3282 `result:` descriptor (`kind: files`) closes; the runner discovers the **actually emitted** files by **globbing the injected embed root** (mirroring #3282), not by trusting the path list.

- **Market inputs have NO as-of date.** `input.yml:10-12` carries static offline prices (`portfolio.prices: {VOO: 500.0, BRKB: 400.0}`) with **no date attached**. A repo-wide grep (`grep -rn 'data_as_of|prices_as_of|as_of' src/ examples/`) returns **only** `analysis/daily_strategy/tax_lots.py` (an unrelated holding-period `as_of` param) — confirming **no provenance as-of field exists** for market inputs. Issue AC#3 requires one.

- **Registry exists (schema v1).** `assethold/docs/registry/workflows.yaml:1` `schema_version: 1` with **7 rows** (`portfolio-offline`, `options-covered-call-offline`, `property-valuation-offline`, `risk-metrics-offline`, `dividend-forecast-offline`, `fundamentals-offline`, `market-alerts-offline`), each with `id`/`basename`/`input`/`outputs`/`test`/`runtime: uv-python`. No top-level `invocation:`, no per-row `result:` descriptor, no `request_schema`/`response_schema`. No `SCHEMA.md` beside it.

- **Shared `workflow_api` is greenfield (the #3282 dependency).** `ls /mnt/local-analysis/assetutilities/src/assetutilities/workflow_api` → **No such file or directory**. The contract import target does not exist yet; #3282 creates it.

### Standards
Not applicable — harness/contract code, not an engineering calculation. **No `Citation` sidecar required** (per `.claude/rules/calc-citation-contract.md` "do NOT apply when … not a standard"): the portfolio computation uses no standards-derived constant. `provenance.standard_revisions` is left `[]`, matching #3282.

### LLM Wiki pages consulted
None — contract/infra work, no domain knowledge added. `Client: N/A`.

### Documents consulted
- Issue [#3287](https://github.com/vamseeachanta/workspace-hub/issues/3287) — scope (adopt ResultEnvelope in assethold; gated on engine wiring), AC (portfolio returns envelope via `run_workflow`; request/response schema rows + golden test; provenance carries market data-as-of).
- Issue [#3308](https://github.com/vamseeachanta/workspace-hub/issues/3308) (OPEN, `status:needs-plan`, `lane:codex`) — the engine embed-port that **mirrors #3297** for assethold's own engine; **explicitly "Blocks: #3287"**. Scope: `engine(embed=True, root_folder=, log_to_file=False)` + `configure_embed` routing ALL writes under root; provenance via `code_version("assethold")`. Its AC ("writes nothing outside `<tmp>`", "default unchanged (golden)", "stamps `code_version("assethold")`") is the foundation #3287 stands on.
- Issue [#3066](https://github.com/vamseeachanta/workspace-hub/issues/3066) (OPEN, `status:needs-plan`, `lane:claude`) — the engine-wiring gate; its scope is **already implemented** on `origin/main` (commit `8d790c0`). The issue stays open/unclosed, but the *code state* it gates on exists.
- `docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md` — the contract this plan consumes: `ResultEnvelope` stdlib dataclass; parameterized `code_version(package_name)` (`:171-173`); `result_hash` over file CONTENTS for `kind:files`; `compute_reproducible` true double-run; `run_workflow(workflow_id, params=None, cfg=None, verify_reproducible=False)`; **`_run_once` calls `engine(embed=True, root_folder=mkdtemp(), log_to_file=False)` then globs the injected root** (`:148,338`) — the exact shape assethold mirrors against its OWN engine.
- `docs/plans/2026-06-28-issue-3297-engine-embeddability.md` — the **mirror-source** #3308 ports. Canonical `configure_embed(self, cfg, basename, root_folder, log_to_file=False)` — **NO `library_name`** (`:151-152`); sets `cfg["_config_dir_path"] = root_folder` (`:168`) so config-relative router writes land under root. assethold's engine is **not** covered → #3308 supplies the assethold mirror.
- `docs/plans/2026-06-28-issue-3295-registry-schema-v2-reconcile.md` — owns `schema_version: 2`, required `invocation:`, reserved `request_schema`/`response_schema`. assethold's registry bump lands after/with #3295.
- #3284 (discovery manifest) — aggregates registries; consumes the wired portfolio row (NOT a resolution dependency for #3287 — see Cross-repo id decision below).

### Cross-repo id decision (per re-locked contract — STATE THE CHOICE)
The issue's workflow ids (`portfolio-offline`, …) are **bare single-registry ids** in assethold's **own** `docs/registry/workflows.yaml`. #3287's `run_workflow` resolves a **bare id against assethold's own registry** — it does **NOT** resolve `repo:id@version`. Therefore **#3287 does NOT gate on #3284** (cross-repo id resolution). #3284 later *consumes* assethold's wired row into the discovery manifest; that is a downstream, not-upstream, relationship. **Choice: bare single-registry id; no #3284 dependency.**

### Gaps identified (each a testable claim)
- No `ResultEnvelope`-returning entrypoint for any assethold workflow (greenfield).
- assethold has **no engine embed path** today; isolation depends entirely on #3308 landing the embed-port **including** the `output_path` rebase (the gap above). #3287 supplies **no** cfg-level redirection.
- No `data_as_of` provenance field for market inputs anywhere (grep-confirmed) — must be added to the portfolio input + extracted into `provenance.data_as_of`.
- Registry is `schema_version: 1` with no `invocation:` and no per-row `result:` descriptor — must be bumped to the v2 superset (co-dependent on #3295).
- No registry `SCHEMA.md` — must be created to document the `result:` shape + `data_as_of` provenance contract.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3287` — OPEN, `status:needs-plan`/`lane:codex` — this issue.
- `#3308` — OPEN, `status:needs-plan`, `lane:codex`, title `wf-api(assethold): engine embed-port — mirror #3297 for assethold's own engine [prereq for #3287]`, body declares `Blocks: #3287`.
- `#3066` — OPEN, `status:needs-plan`, `lane:claude` — code already landed (commit `8d790c0`).
- `#3282` / `#3297` — `status:plan-review`, owner-UNapproved.

**assethold engine signature + wired router** (`engine.py:25,45-70`):
```
25: def engine(inputfile: str = None, cfg: dict = None, config_flag: bool = True) -> dict:
36:     fm = FileManagement(); cfg_base = fm.router(cfg_base)         # config-relative routing
45:     if basename == "stocks": ...  48: elif basename == "portfolio": ...
69:     else: raise Exception(f"Analysis for basename: {basename} not found. ... FAIL")
72:     save_application_cfg(cfg_base=cfg_base)
```

**Isolation gap — portfolio writes are cwd-relative, ignore `_config_dir_path`** (`workflow_io.py:19-22`, `portfolio.py:37-38`):
```
workflow_io 19: def output_path(path: str) -> Path:
            20:     target = Path(path)                               # cwd-relative literal; no _config_dir_path
            21:     target.parent.mkdir(parents=True, exist_ok=True)
portfolio   37: positions_file  = output_path(outputs["positions_csv"])   # "examples/.../positions.csv"
            38: allocation_file = output_path(outputs["allocation_csv"])
```

**`_config_dir_path` rebase target** (`assetutilities path_resolver.py:38,114`):
```
38:  base_dir = cfg.get("_config_dir_path")                            # read (config-relative resolve)
114: cfg["_config_dir_path"] = os.path.dirname(os.path.abspath(config_file_path))  # set by engine
```

**Parameterized `code_version`** (#3282 plan `:171-173`):
```
171: #   digitalmodel -> code_version("digitalmodel"), assethold -> code_version("assethold"), etc.
172: def code_version(package_name="assetutilities") -> dict:
173:     pkg = importlib.metadata.version(package_name)
```

**Greenfield dependency** (`ls`): `/mnt/local-analysis/assetutilities/src/assetutilities/workflow_api/` → "No such file or directory" — #3282 creates it.

**No data_as_of for market inputs** (`grep -rn 'data_as_of\|prices_as_of\|as_of' src/ examples/`): only `analysis/daily_strategy/tax_lots.py` (unrelated holding-period `as_of`); **zero** hits for market-price provenance.

(Distinct sources: issue body + #3308 body + #3066 + #3282 plan + #3297 plan + #3295 plan + engine.py + portfolio.py + workflow_io.py + path_resolver.py + registry yaml + input.yml = 12.)

---

## Step 1.5 — Reproduction

**Behavioral claims under test:** (1) the issue's premise that "assethold engine routes only `stocks`"; (2) that the portfolio workflow is runnable and side-effecting (writes into the repo tree) with `cfg["outputs"]["portfolio"]` as a path-list locator and a `save_application_cfg` cfg-dump; (3) that portfolio CSVs are written via the **cwd-relative `output_path`** (not via `_config_dir_path`), which is *why* a #3297-style rebase alone is insufficient and #3308 must rebase `output_path`.

```
$ /mnt/local-analysis/assethold/.venv/bin/python /tmp/.../probe_portfolio.py   # os.chdir(assethold); engine(inputfile="examples/workflows/portfolio/input.yml")
basename: portfolio
outputs key: {'portfolio': ['examples/workflows/portfolio/outputs/positions.csv',
                            'examples/workflows/portfolio/outputs/allocation.csv']}
result_folder: examples/workflows/portfolio/outputs
files in outputs dir: ['allocation.csv', 'portfolio-run.yml', 'positions.csv']
```

- Reproduced at: 2026-06-28 (repo `.venv`).
- **Claim (1) — FALSE.** The engine routes `portfolio` (and 6 others), not only `stocks`. The issue's gating premise is stale; **#3066's wiring is already live** → the engine-wiring gate is satisfied (per issue-planning-mode Step 1.5, the plan proceeds on real state).
- **Claim (2) — CONFIRMED.** Portfolio runs; result locator is a **path list** (`cfg["outputs"]["portfolio"]`); outputs land **inside the repo example tree** (side-effecting); the dir also contains `portfolio-run.yml` = the `save_application_cfg` cfg-dump (`Analysis.file_name: portfolio-run` + `.yml`). Validates the need for (a) the `result: {kind: files}` descriptor, (b) embed-path tempdir isolation, (c) cfg-dump exclusion from the content hash.
- **Claim (3) — CONFIRMED by static read** (no runtime injection needed): outputs landed at the **literal `portfolio.outputs.*` paths** (`examples/workflows/portfolio/outputs/*.csv`), resolved against cwd by `output_path` (`workflow_io.py:20`), **not** under any `_config_dir_path`/`result_folder` redirection. Confirms the isolation gap: **#3308's `configure_embed` must make `output_path` honor the injected root** for `engine(embed=True, root_folder=<tmp>)` to sandbox these writes. (Runtime double-confirmation deferred to #3308's own Step 1.5 with the embed path in place — **N/A here because the embed path is unlanded**; #3287's `test_run_workflow_writes_nothing_outside_tempdir` is the consumer gate.)

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3287-assethold-adopt-envelope.md |
| Upstream contract (#3282) | docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md |
| Engine embed-port PREREQ (#3308) | (plan TBD — `wf-api(assethold): engine embed-port`) |
| Mirror-source (#3297) | docs/plans/2026-06-28-issue-3297-engine-embeddability.md |
| Runner (assethold-local; reuses shared envelope/helpers; drives assethold engine embed path) | `assethold/src/assethold/workflow_api/runner.py` |
| Package init (re-exports `run_workflow` + shared `ResultEnvelope`) | `assethold/src/assethold/workflow_api/__init__.py` |
| Provenance / market data-as-of extractor | `assethold/src/assethold/workflow_api/provenance.py` |
| Registry (v2 superset: `invocation` + per-row `result` + `market_data_as_of`) | `assethold/docs/registry/workflows.yaml` |
| Registry schema doc | `assethold/docs/registry/SCHEMA.md` |
| Portfolio example (adds declared `data_as_of`) | `assethold/examples/workflows/portfolio/input.yml` |
| Tests | `assethold/tests/workflow_api/test_runner.py`, `test_provenance.py`, `test_registry.py` |
| Plan reviews | scripts/review/results/2026-06-28-plan-3287-{claude,codex,gemini}.md |

> **NOT in this change set:** `assethold/src/assethold/engine.py` + the embed-port (`configure_embed`, `output_path` rebase) — **owned by #3308**; the shared `assetutilities/src/assetutilities/workflow_api/*` — **created by #3282/#3297**. This plan **imports** the shared `ResultEnvelope` + helpers and **calls** assethold's #3308 embed path; it edits neither.

---

## Deliverable

A `workflow_api` surface in **assethold** (`assethold.workflow_api.run_workflow`) that runs the **portfolio** financial workflow end-to-end and returns a shared `ResultEnvelope` (imported from `assetutilities.workflow_api`) — `status="ok"`, `result` = the declared `kind:files` payload (content-hashed CSVs discovered by **globbing the #3308 injected embed root**, cfg-dump excluded), `provenance.data_as_of` = the declared market-price as-of date, `provenance.code_version = code_version("assethold")` = `{package_version, git_sha}`, computed `input_hash`/`result_hash`, `reproducible` honest-`None`-unless-`verify_reproducible=True` — all TDD-covered. The run is **side-effect-free** because it drives assethold's **own** engine through the **#3308 embed path** (`engine(cfg=…, embed=True, root_folder=tempfile.mkdtemp(), log_to_file=False)`) and `rmtree`s the root — **#3287 adds NO cfg-level redirection**. The registry adopts the v2 superset (`schema_version: 2`, top-level `invocation:`, per-row `result:` + `market_data_as_of`), documented in a new `SCHEMA.md`.

---

## Pseudocode

```python
# ── assethold/workflow_api/provenance.py ───────────────────────────────────
# data_as_of for MARKET inputs (issue AC#3). Portfolio prices are static/offline
# and carry no date today -> a declared field is required; fail-SOFT-warn when a
# workflow declares market inputs (prices) but no as-of date (never silent).
def market_data_as_of(cfg, row) -> (value: str | None, warnings: list[str]):
    # precedence: cfg.portfolio.prices_as_of -> cfg.Analysis.data_as_of -> row.market_data_as_of
    as_of = (deep_get(cfg, "portfolio", "prices_as_of")
             or deep_get(cfg, "Analysis", "data_as_of")
             or row.get("market_data_as_of"))
    has_market_inputs = bool(deep_get(cfg, "portfolio", "prices"))
    if has_market_inputs and not as_of:
        return None, ["workflow declares market 'prices' but no data_as_of -> provenance.data_as_of is null"]
    return as_of, []

# ── assethold/workflow_api/runner.py ───────────────────────────────────────
# REUSE the #3282-owned shared machinery; drive assethold's OWN engine via the
# #3308 embed path. NO cfg-level output redirection here (the Wave-2 MAJOR).
from assetutilities.workflow_api import (
    ResultEnvelope, code_version, input_hash, result_hash, compute_reproducible,
)
from assethold.engine import engine as assethold_engine        # assethold's OWN engine

def extract_result(cfg_base, root) -> (payload, warnings):
    # kind:files -> glob the #3308 INJECTED root (mirrors #3282). The portfolio
    # CSVs + the save_application_cfg cfg-dump both land under <root> because
    # #3308's configure_embed rebases result_folder AND the output_path writers.
    # EXCLUDE the cfg-dump <file_name>.yml so result_hash is content-only.
    file_name = deep_get(cfg_base, "Analysis", "file_name", default="")
    cfg_dump  = os.path.abspath(os.path.join(root, file_name + ".yml"))   # also matched anywhere under root
    emitted = sorted(p for p in glob.glob(os.path.join(root, "**", "*"), recursive=True)
                     if os.path.isfile(p) and os.path.basename(p) != (file_name + ".yml"))
    files = [{"basename": os.path.basename(p), "sha256": sha256(open(p, "rb").read()).hexdigest()}
             for p in emitted]
    warns = [] if files else [f"declared kind:files workflow emitted no files under {root}"]
    return {"kind": "files", "outputs": files}, warns

def _run_once(cfg):
    root = tempfile.mkdtemp(prefix="ahwf_")
    try:
        # #3308 embed path: honors in-memory cfg, sandboxes ALL writes under root,
        # no .log / logs/. NOT engine(cfg=..., config_flag=...) which side-effects to cwd.
        cb = assethold_engine(cfg=AttributeDict(cfg), embed=True,
                              root_folder=root, log_to_file=False)
        payload, warns = extract_result(cb, root)
        return payload, warns, result_hash(payload)
    finally:
        shutil.rmtree(root, ignore_errors=True)                 # repo/example tree untouched

def run_workflow(workflow_id=None, params=None, cfg=None, verify_reproducible=False) -> ResultEnvelope:
    wid = workflow_id or "(inline-cfg)"
    try:                                                        # fail-closed from line 1
        row = resolve_registry_row(workflow_id) if cfg is None else lookup_row_for_cfg(cfg)
        cfg = build_cfg(row, params) if cfg is None else cfg    # load row.input (bare id, OWN registry), deep-merge params (params win)
        as_of, as_of_warns = market_data_as_of(cfg, row)
        ihash = input_hash(cfg)
        payload, warns, rhash = _run_once(cfg)
        repro = compute_reproducible(lambda: _run_once(cfg), rhash, verify_reproducible)   # None unless asked; FRESH root
        prov  = {**code_version_provenance(), "data_as_of": as_of, "input_hash": ihash}
        return ResultEnvelope(wid, "ok", payload, prov,
                              {"result_hash": rhash, "reproducible": repro}, None, warns + as_of_warns)
    except Exception as e:
        return ResultEnvelope(wid, "error", {}, {**code_version_provenance(), "data_as_of": None, "input_hash": None},
                              {"result_hash": None, "reproducible": None}, None, [str(e)])

def code_version_provenance():   # assethold's OWN package version, per #3282's parameterized API + #3308 AC
    return {"code_version": code_version("assethold"), "standard_revisions": []}
```

> **No `engine.py` / `configure_embed` pseudocode** — that is **#3308's** deliverable (the assethold embed-port). #3287 only **calls** `assethold_engine(embed=True, root_folder=, log_to_file=False)`. If #3282's helpers (`input_hash`/`result_hash`/`compute_reproducible`/`code_version`) are exported from a submodule rather than the package root, the runner imports them from their defining module (confirmed against the landed #3282 surface at implementation time).

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
    outputs:                                            # DOCUMENTARY (expected count); runtime globs the injected embed root
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
- `SCHEMA.md` (new) documents: the `result:` descriptor (`kind: files` default vs `in_memory`); that `outputs:` is **documentary** (runtime globs the #3308 injected embed root, excluding the `<file_name>.yml` cfg-dump); the required `invocation:` (+ `{input}`-only substitution; `deckhand/src/deckhand/capability_smoke.py` is the reference resolver per #3295); and the **`market_data_as_of` / `data_as_of` provenance contract** (declared per row/cfg; fail-soft-warn when market inputs lack an as-of date).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `assethold/src/assethold/workflow_api/__init__.py` | export `run_workflow`; re-export shared `ResultEnvelope` |
| Create | `assethold/src/assethold/workflow_api/runner.py` | `run_workflow`, registry resolution (bare id, OWN registry), `build_cfg`, `_run_once` (calls **`assethold_engine(embed=True, root_folder=mkdtemp(), log_to_file=False)`** → glob injected root → rmtree), `extract_result` (files-by-glob, cfg-dump excluded), `code_version("assethold")` provenance |
| Create | `assethold/src/assethold/workflow_api/provenance.py` | `market_data_as_of` (data-as-of for market inputs; fail-soft-warn) |
| Modify | `assethold/docs/registry/workflows.yaml` | `schema_version: 2`; top-level `invocation:`; per-row `result:`; `market_data_as_of` |
| Create | `assethold/docs/registry/SCHEMA.md` | document `result:`, `outputs:`-documentary + glob-injected-root, `invocation:`, `data_as_of` contract |
| Modify | `assethold/examples/workflows/portfolio/input.yml` | add declared `portfolio.prices_as_of` (or `Analysis.data_as_of`) |
| Create | `assethold/tests/workflow_api/test_runner.py` | runner + embed-path isolation + locator + golden-hash TDD |
| Create | `assethold/tests/workflow_api/test_provenance.py` | data-as-of extraction + fail-soft-warn TDD |
| Create | `assethold/tests/workflow_api/test_registry.py` | v2 schema + invocation + result + market_data_as_of TDD |
| Update | docs/plans/README.md | add/update this plan in the Plan Index |

> **Dependency, not owned here:** `assetutilities/src/assetutilities/workflow_api/*` (`ResultEnvelope` + helpers + parameterized `code_version`) — **#3282/#3297**. assethold's `engine.py` embed-port (`configure_embed`, `output_path` rebase) — **#3308**. assethold's engine *wiring* is already landed by **#3066**.

---

## TDD Test List

| Test name | What it verifies | Input | Output |
|---|---|---|---|
| test_run_workflow_portfolio_returns_envelope | portfolio id → populated `ResultEnvelope`, `status=="ok"`, `result.kind=="files"` | `run_workflow("portfolio-offline")` | ok envelope, 2 file digests |
| test_run_workflow_drives_embed_path | **(consumer contract)** `_run_once` calls `assethold_engine` with `embed=True` + a `root_folder` tempdir + `log_to_file=False` (monkeypatch-spy on the engine) — NOT `config_flag` | run | engine invoked with embed kwargs |
| test_run_workflow_writes_nothing_outside_tempdir | **(isolation, #3308 consumer gate)** repo `examples/workflows/portfolio/outputs/` is byte-for-byte unchanged before/after; no stray files; temp root removed | run + dir snapshot | nothing written outside tempdir |
| test_extract_result_excludes_save_cfg_dump | the `portfolio-run.yml` cfg-dump is EXCLUDED from outputs + content hash | portfolio run | outputs exclude `*-run.yml`; hash stable across two tempdirs |
| test_result_hash_files_content_sensitive | changing a CSV's bytes flips `result_hash`; identical bytes (diff tempdir) → identical hash | two runs | different-then-equal hash |
| test_provenance_data_as_of_populated | declared `prices_as_of` → `provenance.data_as_of == "2026-06-27"` | portfolio cfg w/ as-of | as-of present |
| test_provenance_data_as_of_missing_warns | market `prices` present, no as-of → `data_as_of is None` + warning (not silent) | cfg w/ prices, no date | warning appended |
| test_provenance_code_version_is_assethold | `provenance.code_version` from `code_version("assethold")` — `package_version` is assethold's (NOT assetutilities') + `git_sha` key present | envelope | assethold version, both keys |
| test_reproducible_default_none | `verify_reproducible=False` → `determinism.reproducible is None` | run w/o verify | None |
| test_reproducible_computed_true_on_double_run | `verify_reproducible=True` → `reproducible is True` via two isolated embed runs comparing file CONTENTS | portfolio | True |
| test_run_workflow_unknown_id_error_envelope | unknown id → `status=="error"` envelope (fail-closed, not raised) | `run_workflow("nope")` | error envelope w/ message |
| test_run_workflow_engine_error_envelope | a router exception → error envelope, not a raw traceback | cfg that makes router raise | error envelope w/ message |
| test_build_cfg_merges_params_over_example | `build_cfg(row, params)` loads `row.input` then deep-merges params (params win) | portfolio row + override | merged values |
| test_registry_schema_v2_invocation_result_asof | registry parses at `schema_version: 2`; top-level `invocation == "uv run python -m assethold {input}"`; portfolio row has `result.kind==files` + `market_data_as_of`; all 7 rows valid | current registry | version 2, fields present |
| test_golden_portfolio_result_hash | **(AC golden test)** portfolio run over the committed example yields a STABLE `result_hash` (pinned constant); a perturbed price → different hash | example input | matches golden; perturbation differs |

> **Ordering gate:** tests that call `run_workflow` import `ResultEnvelope`/helpers from `assetutilities.workflow_api` (red until #3282 lands) **and** call `assethold_engine(embed=True,…)` (red until #3308 lands the embed-port). `test_run_workflow_writes_nothing_outside_tempdir` is specifically the consumer gate on #3308's `output_path` rebase. The provenance + registry-schema + build_cfg tests are independent of both shared packages and can go green earlier — they pin the assethold-side surface. Written test-first regardless.

---

## Acceptance Criteria

- [ ] **Gate check recorded:** #3066's engine wiring is live (verified — `engine.py:45-70`, commit `8d790c0`); **#3308 has landed** (assethold `engine(embed=True, root_folder=)` exists and sandboxes ALL writes incl `output_path`); **#3282 has landed** (`assetutilities.workflow_api` + parameterized `code_version` resolve) — all before this issue is implemented.
- [ ] `run_workflow("portfolio-offline")` returns a populated shared `ResultEnvelope` (`status=="ok"`, `result.kind=="files"` with the two portfolio CSVs content-hashed), demonstrated by a passing test under the assethold pytest harness.
- [ ] **Side-effect-free via the #3308 embed path:** a run writes nothing outside the per-call `tempfile.mkdtemp()` root (repo `examples/.../outputs/` unchanged before/after; root `rmtree`'d) — isolation comes from `engine(embed=True, root_folder=, log_to_file=False)`, **NOT** from any cfg-level redirection in #3287.
- [ ] **Provenance carries data-as-of for market inputs (AC#3):** `provenance.data_as_of` is the declared portfolio `prices_as_of`; when market `prices` exist without an as-of date, `data_as_of is None` **and** a warning is emitted (fail-soft, not silent).
- [ ] **Provenance stamps assethold's own version:** `provenance.code_version == code_version("assethold")` = `{package_version, git_sha}` — assethold's package_version, not assetutilities'.
- [ ] Determinism fields computed, not hardcoded: `input_hash`/`result_hash` present; `result_hash` over file CONTENTS (cfg-dump `<file_name>.yml` excluded); `reproducible` is `None` unless `verify_reproducible=True` (then a measured double-run bool).
- [ ] **request/response schema rows + golden test (AC#2):** registry adopts the v2 superset (`schema_version: 2`, top-level `invocation:`, per-row `result:`, `market_data_as_of`); `request_schema`/`response_schema` left RESERVED for #3295; `SCHEMA.md` created; the golden `result_hash` test pins the portfolio output and detects perturbation.
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

**Prior round (Wave 2) — MAJORs ADDRESSED in this revision:**
- **MAJOR (isolation by cfg-level redirection / "no engine edit").** The prior draft achieved side-effect-freeness by a `redirect_outputs_under` / `PORTFOLIO_OUTPUT_KEYS` cfg rewrite and claimed "no engine edit", duplicating embed logic and being workflow-shape-specific. **Addressed:** the re-locked contract gives assethold its OWN embed-port via **#3308** (mirrors #3297). This revision **deletes all cfg-level redirection** and consumes `engine(embed=True, root_folder=, log_to_file=False)`; isolation + the `output_path` rebase are now #3308-owned, with #3287's `test_run_workflow_writes_nothing_outside_tempdir` as the consumer gate.
- **MAJOR (`run_workflow` provenance via a hardcoded / assetutilities `code_version`, "no #3282 change" framing).** **Addressed:** this revision consumes the **parameterized** `code_version("assethold")` delivered by the refined #3282; the "#3282 unchanged" framing is dropped — #3287 is an adopter of the parameterized API.
- **MAJOR (lead Open Decision "Option A vs B" left unresolved).** **Addressed:** the cross-cutting decision locks Option A (assethold-local `run_workflow` reusing shared types + assethold's own engine embed path). The open decision is removed; rationale retained in Risks.
- **MAJOR (cross-repo id resolution ambiguity / implicit #3284 gate).** **Addressed:** explicit choice stated — **bare single-registry id against assethold's OWN registry; no #3284 dependency**.

**Overall result:** PENDING — new round not yet run. Not approval-ready until populated with no-MAJOR verdicts; status stays `draft`. Implementation remains gated behind (a) USER approval and (b) **#3282 + #3308 landing first** (plus #3066 already-landed code state), and **#3295 co-landing** for the registry bump.

---

## Risks and Open Questions

- **Risk (LEAD) — #3308 must rebase assethold's `output_path` writers, not just `_config_dir_path`.** assethold's portfolio CSVs are written via `workflow_io.output_path(path) = Path(path)` (cwd-relative literal; `workflow_io.py:19-22`), which **never reads `_config_dir_path`**. A bare #3297-mirror (which only rebases `_config_dir_path` + `result_folder`) would leave portfolio CSVs writing into the repo tree, **failing #3287's isolation AC**. Mitigation/handoff: #3308's scope ("route ALL writes under the injected root") **must** include making `output_path` (or the portfolio router's declared output paths) resolve under the injected root. **Cross-issue handoff:** this finding is filed against #3308's plan; #3287's `test_run_workflow_writes_nothing_outside_tempdir` is the consumer assertion that catches a non-conforming #3308. If #3308 ships without it, #3287 is blocked, not worked-around (no cfg-redirection fallback — that was the Wave-2 MAJOR).
- **Decision (LOCKED, not open) — how assethold reuses the contract.** #3282's `run_workflow` drives *assetutilities*' engine; assethold has its OWN engine. Per the owner-confirmed cross-cutting decision: assethold ships an **assethold-local `run_workflow`** (`assethold.workflow_api.run_workflow`) that **reuses** the shared `ResultEnvelope` + determinism helpers (from `assetutilities.workflow_api`) and drives assethold's OWN engine via the **#3308 embed path**. This diverges *slightly* from a literal `from assetutilities.workflow_api import run_workflow` but is the locked design (minimal coupling; preserves #3282 + #3308 unchanged). The alternative (generalize the shared `run_workflow` to dispatch by `repo:`) was rejected — it would edit the #3282 contract.
- **Risk — hard dependency on three unlanded, owner-unapproved upstreams (#3282 + #3308 + #3308's source #3297).** The shared `workflow_api` package and assethold's embed path do not exist yet (verified). This issue **cannot be implemented** until #3282 + #3308 land. Critical path: **#3297 → #3308 → #3287** and **#3297 → #3282 → #3287** (with **#3295** for the registry bump). If #3282's helper export surface differs from assumed names, the runner adapts imports at implementation time.
- **Risk — issue premise is stale (#3066 already landed).** The issue gates on "#3066 wires routing / fixes substring bug", but that code is on `origin/main` (commit `8d790c0`); the engine routes 7 wired workflows with `==`. The engine-wiring gate is **GREEN**; #3066 the *issue* is still open/unclosed. No work is needed against #3066 here.
- **Risk — cfg-dump pollution.** `save_application_cfg` writes `<file_name>.yml` into the result folder (observed: `portfolio-run.yml`). `extract_result` excludes it from the glob/hash (keyed on `Analysis.file_name`), mirroring #3282. Edge: a workflow whose *genuine* output is itself `<file_name>.yml` would be wrongly excluded — not the case for portfolio (CSV outputs). Documented.
- **Risk — data_as_of is a declared convention, not derived.** Static offline prices have no intrinsic date; `provenance.data_as_of` reflects what the input declares. When market inputs exist without a date, the run still succeeds but emits a warning and `data_as_of=None` (fail-soft). A future live-quote path (e.g. `market_alerts`) could stamp a real fetch timestamp — out of scope here.
- **Risk — registry reconciliation overlap with #3295.** This plan lands `schema_version: 2` + `invocation:` + per-row `result:` + `market_data_as_of` (all additive). #3295 owns the cross-registry reconcile + `request_schema`/`response_schema` reservation. Land **after/with #3295**; if #3295 renames a field, a fast follow-up adjusts.
- **Risk — single-workflow pilot.** This adopts **portfolio only**. The remaining 6 wired workflows adopt later (each needs its own `result:`/`market_data_as_of` review); the runner generalizes since it globs the injected root rather than hardcoding portfolio output keys. Multi-workflow rollout is follow-on.
- **Risk — heavy/slow import.** assethold's engine pulls assetutilities (plotly etc.) and emits a `requests_html` warning (~tens of seconds cold). Reproduction used the repo `.venv`. Implementation re-verifies under the assethold pytest harness; lazy-import follow-on if unacceptable. Not a blocker.

**Open Questions:**
1. Provenance field placement: `portfolio.prices_as_of` (workflow-scoped) vs `Analysis.data_as_of` (engine-scoped)? Plan supports both with precedence; recommend `Analysis.data_as_of` as the cross-workflow convention. Flag at approval.
2. Confirm #3308's plan absorbs the `output_path`-rebase requirement (LEAD risk) before #3287 is scheduled — otherwise #3287's isolation AC is unsatisfiable.

---

## Complexity: T2

**T2** — one new small package (3 source files) + a registry bump + a schema doc + an example edit, TDD throughout, **reusing** the #3282 shared envelope/helpers AND the #3308 assethold engine embed-port with **zero engine edits owned here**. Flagged for **T3-depth review** because it consumes three unlanded, owner-unapproved cross-repo contracts (#3282, #3308, #3297) and must reconcile with #3295.
