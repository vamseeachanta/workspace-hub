# Plan for #3308: wf-api(assethold) — engine embed-port (mirror #3297 for assethold's OWN engine)

> **Wave-2 cross-repo port (2026-06-28).** This plan ports the #3297 embed contract to **assethold's own engine**, which is **structurally different** from assetutilities' engine: it does NOT use `ApplicationManager.configure()`, `set_logging`, `configure_result_folder`, or `_config_dir_path` today. Its writes are cwd-coupled through **two distinct mechanisms** (`workflow_io.output_path` for 8 modules + `cfg["Analysis"]["analysis_root_folder"]` for stocks), plus a `save_application_cfg` cfg-dump. The port mirrors #3297's **canonical `configure_embed` signature** and **byte-identical-default** discipline but adapts the mechanics to assethold's actual write paths. The shared `assetutilities.workflow_api.ResultEnvelope` types are consumed unchanged (no redesign).
>
> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3308
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3308-claude.md | ...-codex.md | ...-gemini.md

---

## Hard Dependencies (state explicitly)

| Dependency | State (verified 2026-06-28) | Effect on this plan |
|---|---|---|
| Re-locked contract (#3297 canonical `configure_embed(cfg, basename, root_folder, log_to_file=False)`; #3282 `code_version(package_name)` parameterized) | `#3297` at `status:plan-review` (owner-UNapproved); `#3282` at `status:plan-review` (owner-UNapproved) | Consumed AS SPECIFIED. The **embed-isolation mechanics** (AC#1/AC#2) do NOT import anything from assetutilities' engine or `workflow_api` — assethold has its OWN engine + OWN `configure_embed` + OWN `workflow_io` — so they are buildable independently of #3282/#3297 landing. Only the canonical signature shape is borrowed. |
| #3066 (assethold engine wiring beyond `stocks`) | **ALREADY LANDED** — commit `8d790c0` "feat(workflows): wire 6 domains into engine + UV-workflow registry (workspace-hub#3066)" (PR #55). GitHub issue #3066 still OPEN, but the code is merged. | The issue body's premise ("routes only `stocks` today; #3066 wires the rest") is **STALE**. The engine routes **8** basenames (`stocks`, `portfolio`, `options`, `property`, `risk_metrics`, `dividend_forecast`, `fundamentals`, `market_alerts`) with `==` matching (substring bug fixed — `test_engine_does_not_route_stocks_substrings` green). The "gated on #3066" condition is **satisfied**. The embed port therefore covers ALL wired domains, not just `stocks`. |
| #3282 (`code_version(package_name)` in `assetutilities.workflow_api`) | at `status:plan-review`, owner-UNapproved; package `assetutilities.workflow_api` **does not exist yet** | **Provenance AC#3 ONLY** (`code_version("assethold")`) hard-depends on #3282. This plan wires it with an import-guarded local fallback so the AC is testable now and flips to `code_version("assethold")` when #3282 lands. The embed-isolation core does not need it. |
| #3308 **blocks** #3287 | #3287 plan (`docs/plans/2026-06-28-issue-3287-assethold-adopt-envelope.md`) currently supplies its OWN **portfolio-only** `redirect_outputs` isolation hack because "assethold has NO #3297 embed path" and explicitly names "add an `engine(embed=True, root_folder=...)` path to assethold's engine mirroring #3297" as the **deferred follow-on**. | **This issue IS that follow-on.** #3308 delivers the workflow-shape-agnostic engine embed path that #3287's runner SHOULD consume (replacing `redirect_outputs` + `PORTFOLIO_OUTPUT_KEYS`) for multi-workflow isolation. |

---

## Resource Intelligence Summary

### Existing repo code

- Found: `assethold/src/assethold/engine.py:25` — `def engine(inputfile=None, cfg=None, config_flag=True) -> dict`. **Structurally unlike assetutilities' engine:** no `ApplicationManager`, no `configure()`, no `set_logging`, no `configure_result_folder`, no `_config_dir_path`. Flow: load cfg (`:27-32`) → `basename = cfg["basename"]` (`:34`) → `fm = FileManagement()` + (when `config_flag`) `cfg_base = fm.router(cfg_base)` (`:37-39`) → `if/elif` dispatch on `basename` to one of **8** workflow routers (`:45-70`) → `save_application_cfg(cfg_base=cfg_base)` (`:72`) → `return cfg_base`.
- Found: `engine.py:37-41` — `config_flag` ONLY gates whether `FileManagement().router(cfg_base)` runs. There is **no `root_folder` / `embed` parameter** and **no injected-root honoring** anywhere.
- Found (write-mechanism #1 — cwd-coupled, the load-bearing leak): `assethold/src/assethold/modules/workflow_io.py:19-22` — `output_path(path)` = `Path(path)` (a relative config value → resolved against **`os.getcwd()`**) + `target.parent.mkdir(parents=True, exist_ok=True)`. **Used by 8 modules:** `dividend_forecast`, `fundamentals`, `gis`, `market_alerts`, `options`, `portfolio`, `property`, `risk_metrics` (grep below). `output_path` takes **no cfg and no root** — so the 7+ wired financial domains write **relative to the process cwd**, escaping any intended sandbox.
- Found (write-mechanism #2 — `analysis_root_folder`): `assethold/src/assethold/modules/stocks/{get_stock_data.py:74, investment_value.py:105, investment_value_ffn.py:92,101}` — the `stocks` domain writes via `os.path.join(cfg["Analysis"]["analysis_root_folder"], file_name)` (and **skips** the write with a warning when `analysis_root_folder` is absent — `get_stock_data.py:70-71`). So `stocks` ALREADY honors an injected root **if** `cfg["Analysis"]["analysis_root_folder"]` is set; the other 7 domains do not.
- Found (write-mechanism #3 — cfg-dump): `engine.py:72` `save_application_cfg(cfg_base=cfg_base)` → `assetutilities/common/utilities.py:259-265` reads `cfg_base.Analysis["result_folder"]` + `cfg_base.Analysis["file_name"]` (AttributeDict **attribute** access) and writes `<result_folder>/<file_name>.yml` via `saveDataYaml`. Reproduced below: it **raises `AttributeError`** when `Analysis.result_folder` is absent, and writes the dump under `result_folder` when present. So the embed path must set `Analysis.result_folder` (under root) + `Analysis.file_name` and make cfg an `AttributeDict`, or the dump either crashes or escapes the root.
- Found (write-mechanism #4 — fm.router): `assetutilities/common/file_management.py:146-190` — `FileManagement.router(cfg)` reads `cfg.Analysis["analysis_root_folder"]` and `mkdir(parents=True, exist_ok=True)` on output dirs **under that root**. So when `config_flag=True` AND `analysis_root_folder=root`, `fm.router` writes under root automatically — no extra change needed for it once the root is injected.
- Found (no provenance today): `grep code_version|git_sha|package_version` over `src/` → **only** `__version__` constants. `src/assethold/__init__.py:9 __version__ = "0.0.1"` — **but** `pyproject.toml` declares `version = "0.1.0"` (mismatch flagged under Risks). No `code_version` helper exists in assethold; it lives in `assetutilities.workflow_api` per #3282 (unlanded).
- Found (existing tests): `assethold/tests/unit/test_engine.py` — 20+ tests, all **mock** `FileManagement`, `Stocks`/`*Workflow`, and `save_application_cfg`, so they never exercise real writes. The parametrized `test_engine_calls_requested_workflow_router` (`:191-220`) pins the 6 non-stocks wired routers; `test_engine_does_not_route_stocks_substrings` (`:349-365`) pins `==` matching (the #3066 substring fix). These are the backward-compat golden to preserve.
- Found (no ApplicationManager fork): assethold imports `assetutilities.common.{file_management, update_deep, utilities, yml_utilities}` from the installed package; it has **no** local `ApplicationManager` copy (unlike digitalmodel's fork). So there is **no `configure_embed` method to extend** — assethold needs its OWN `configure_embed` (a standalone function, no `self`, mirroring #3297's signature minus `library_name`).
- Gap: there is **no embed/`root_folder` path** on assethold's engine; **no** workflow-shape-agnostic output-root rebase; **no** `configure_embed`; **no** `code_version("assethold")` provenance wiring; **no** regression test pinning output LOCATIONS (existing tests assert routing only, via mocks).

### Standards

Not applicable — harness/library plumbing change inside assethold; no engineering standard or standards-derived constant involved. Per `.claude/rules/calc-citation-contract.md` "do NOT apply when … not a standard": **no `Citation` sidecar required**.

### LLM Wiki pages consulted

No relevant wiki pages — internal engine plumbing, not domain knowledge. Client: N/A (no wiki content touched), so `.claude/rules/wiki-sibling-routing.md` does not apply.

### Documents consulted

- Issue [#3308](https://github.com/vamseeachanta/workspace-hub/issues/3308) body — scope (mirror #3297 for assethold's own engine; `configure_embed` honoring root incl `_config_dir_path`; provenance via `code_version("assethold")`; blocks #3287; gated on #3066). **Premise correction:** "routes only stocks today" is stale — see Hard Dependencies / Reproduction.
- `docs/plans/2026-06-28-issue-3297-engine-embeddability.md` — the contract being mirrored: canonical `configure_embed(self, cfg, basename, root_folder, log_to_file=False)` (NO `library_name`); sets `analysis_root_folder=root`, log folders under root, AND `cfg["_config_dir_path"]=root`; `engine(cfg=..., embed=True, root_folder=, log_to_file=False)` is the embed entry; default (no root) byte-identical. assethold has its OWN engine → this is a sibling port, not a reuse.
- `docs/plans/2026-06-28-issue-3287-assethold-adopt-envelope.md` — the blocked dependent. It documents (lines 31, 342) that assethold's engine writes cwd-relative via `workflow_io.output_path`, has **no embed path**, and that its `redirect_outputs` isolation is **portfolio-shape-specific** (`PORTFOLIO_OUTPUT_KEYS`) with "generalizing to all 7 wired workflows is future work" — naming the assethold engine embed path as the rejected-for-pilot alternative. **#3308 supplies exactly that generalization.**
- `docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md` — `code_version(package_name="assetutilities")` is PARAMETERIZED; adopters pass their own package. assethold passes `"assethold"`. The package `assetutilities.workflow_api` does not exist yet.
- Related issue #3066 — **landed** (`8d790c0`/PR #55) despite OPEN status; engine wiring + substring fix confirmed by Reproduction.

### Gaps identified

- No `engine(embed=True, root_folder=..., log_to_file=False)` path on assethold's engine.
- No workflow-shape-agnostic output-root rebase for `workflow_io.output_path` (the 8-module cwd leak).
- No `configure_embed` for assethold (no ApplicationManager to host it; needs a standalone function).
- No setup of `Analysis.result_folder` / `file_name` / AttributeDict for the embed path → `save_application_cfg` would crash or escape root.
- No `code_version("assethold")` provenance wiring (gated on #3282).
- No regression test pinning output LOCATIONS (existing tests mock all writes).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3308` — OPEN — "wf-api(assethold): engine embed-port — mirror #3297 for assethold's own engine [prereq for #3287]"
- `#3307` — OPEN — digitalmodel sibling embed-port (mirrors #3297 for digitalmodel's own engine)
- `#3287` — OPEN — assethold adopt-ResultEnvelope (the dependent #3308 blocks)
- `#3066` — OPEN (but code LANDED `8d790c0`) — assethold engine wiring + substring fix
- `#3282` — OPEN, plan at `status:plan-review` (owner-UNapproved) — `code_version(package_name)` source
- `#3297` — OPEN, plan at `status:plan-review` (owner-UNapproved) — the contract being mirrored

**File existence** (`find`/`ls` 2026-06-28):
- EXISTS: `assethold/src/assethold/engine.py`, `.../modules/workflow_io.py`, `.../modules/stocks/{get_stock_data,investment_value,investment_value_ffn}.py`, `assethold/tests/unit/test_engine.py`
- MISSING (new — this plan creates): `assethold/src/assethold/common/configure_embed.py`, `assethold/src/assethold/common/provenance.py`, `assethold/tests/common/test_engine_embed_root.py` (and the `tests/common/` dir)
- NOTE: assethold has **no** local `ApplicationManager.py` (only the installed `assetutilities` copy under `.venv/`); confirms `configure_embed` must be a new assethold-local function.

**`output_path` cwd-coupling** (`grep -rln "output_path" src/assethold/modules/`):
```
dividend_forecast/dividend_forecast.py  fundamentals/fundamentals.py  gis/imagery_fetcher.py
gis/report_generator.py  market_alerts/market_alerts.py  options/options.py
portfolio/portfolio.py  property/property.py  risk_metrics/risk_metrics.py  (+ workflow_io.py)
```

**Reproduction proofs** (Step 1.5 — runtime claims):

1) **`output_path` resolves relative paths under cwd, ignoring any root** (the load-bearing leak):
```
$ .venv/bin/python -c "<chdir to tmp; output_path('results/portfolio/positions.csv')>"
cwd            : /tmp/tmpsguoqinl
output_path -> : /tmp/tmpsguoqinl/results/portfolio/positions.csv
is under cwd   : True
absolute?      : False
```
→ Confirms: config-relative output paths land under the process cwd; `output_path` honors no injected root. Embed isolation must rebase this.

2) **`save_application_cfg` requires `Analysis.result_folder`/`file_name` and writes there**:
```
$ .venv/bin/python  # save_application_cfg(AttributeDict({"basename":"portfolio","outputs":{}}))
save_application_cfg without Analysis.result_folder -> AttributeError 'AttributeDict' object has no attribute 'Analysis'
$ # with Analysis.result_folder=<tmp>, file_name="portfolio_test":
with result_folder=/tmp/tmpzd5290xh -> wrote: ['portfolio_test.yml']
```
→ Confirms: the embed path must set `Analysis.result_folder` (under root) + `Analysis.file_name` + make cfg an `AttributeDict`, else the cfg-dump crashes or escapes the root.

3) **#3066 wiring landed (issue premise stale)** (`git log` + engine source):
```
$ git -C /mnt/local-analysis/assethold log --oneline -- src/assethold/engine.py | head -2
c98a365 feat(market_alerts): live-quote -> signals -> alerts engine ...
8d790c0 feat(workflows): wire 6 domains into engine + UV-workflow registry (workspace-hub#3066) (#55)
```
engine.py routes 8 basenames with `==` (`:45-70`); `test_engine_does_not_route_stocks_substrings` green.

- Reproduced at: 2026-06-28
- Failure mode observed matches issue claim: **PARTIAL** — the cwd-leak claim (no embed path / writes escape root) is CONFIRMED; the "routes only stocks today" claim is **FALSE** (engine routes 8 domains — #3066 already landed). The plan addresses the actual state, not the stale premise.

<!-- Distinct sources: issue #3308 body (1), engine.py (2), workflow_io.py (3), stocks modules (4), save_application_cfg/utilities.py (5), file_management.py (6), #3297 plan (7), #3287 plan (8), #3282 plan (9), test_engine.py (10), git log/#3066 (11). Count: 11 >= 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3308-assethold-embed-port.md |
| Upstream contract mirrored (#3297) | docs/plans/2026-06-28-issue-3297-engine-embeddability.md |
| Dependent unblocked (#3287) | docs/plans/2026-06-28-issue-3287-assethold-adopt-envelope.md |
| Implementation (engine — embed branch + `root_folder`/`log_to_file`/`embed` params) | `assethold/src/assethold/engine.py` |
| Implementation (new `configure_embed()` — standalone, no `self`, no `library_name`) | `assethold/src/assethold/common/configure_embed.py` |
| Implementation (output-root rebase: ContextVar + `output_root()` ctx mgr) | `assethold/src/assethold/modules/workflow_io.py` |
| Implementation (provenance: `assethold_code_version()` → `code_version("assethold")`) | `assethold/src/assethold/common/provenance.py` |
| Tests | `assethold/tests/common/test_engine_embed_root.py` (+ `tests/common/` dir) |
| Plan review — Claude | scripts/review/results/2026-06-28-plan-3308-claude.md |
| Plan review — Codex | scripts/review/results/2026-06-28-plan-3308-codex.md |
| Plan review — Gemini | scripts/review/results/2026-06-28-plan-3308-gemini.md |
| Plan index | docs/plans/README.md |

---

## Deliverable

An embeddable assethold engine that mirrors the #3297 contract for assethold's OWN engine, with **two additive mechanisms**, both defaulting to today's exact behavior:

1. **`engine(cfg=..., embed=True, root_folder=<dir>, log_to_file=False)`** — a dedicated embed path that calls a new assethold-local **`configure_embed(cfg, basename, root_folder, log_to_file=False)`** (canonical #3297 signature, **no `self`, no `library_name`**). `configure_embed` makes the in-memory cfg an `AttributeDict` and sets, **under the injected root**: `Analysis.analysis_root_folder` (honored by `stocks` + `fm.router`), `Analysis.result_folder` + `Analysis.file_name` (so `save_application_cfg`'s cfg-dump lands under root, not crash/escape), and `cfg["_config_dir_path"]` (per the locked contract — for any `PathResolver`-routed writes + cross-repo uniformity). The engine's embed branch then runs the existing basename dispatch **inside an `output_root(root_folder)` context** so that `workflow_io.output_path` rebases every config-relative write under the root. Result: an in-process run that writes **nothing outside `root_folder`** across all 8 wired domains, with no `os.chdir`.

2. **Output-root rebase in `workflow_io`** — a module-level `ContextVar` + `output_root(root)` context manager consumed by `output_path`. When the contextvar is unset (every existing caller / default path) behavior is **byte-identical** (relative → cwd). When set (only inside the embed branch), a **relative** config path is rebased to `<root>/<path>`; an **absolute** config path is left untouched (caller's explicit choice). Zero call-site edits across the 8 modules; re-entrancy-safe via the contextvar token reset.

Plus **provenance wiring** (AC#3, gated on #3282): a thin `assethold_code_version()` that returns assethold's own `{package_version, git_sha}` — wired to call `code_version("assethold")` from `assetutilities.workflow_api` when #3282 lands, with an import-guarded local fallback until then.

> **#3287 implication (explicit):** #3287's `run_workflow` SHOULD call **`engine(cfg=<built cfg>, embed=True, root_folder=<tempdir>, log_to_file=False)`** — this generalized embed path — instead of its portfolio-only `redirect_outputs` + `PORTFOLIO_OUTPUT_KEYS` hack, giving multi-workflow isolation for free.

---

## Pseudocode

```
# ---------------- modules/workflow_io.py ----------------
# Additive: a ContextVar-driven output root. Default (unset) => byte-identical (relative -> cwd).
from contextlib import contextmanager
from contextvars import ContextVar
_output_root: ContextVar[str | None] = ContextVar("assethold_output_root", default=None)

@contextmanager
def output_root(root):
    token = _output_root.set(root)            # re-entrant: token reset in finally
    try:
        yield
    finally:
        _output_root.reset(token)

def output_path(path):                        # MODIFIED (additive)
    target = Path(path)
    root = _output_root.get()
    if root is not None and not target.is_absolute():
        target = Path(root) / target          # rebase ONLY relative paths, ONLY under embed
    target.parent.mkdir(parents=True, exist_ok=True)
    return target                             # default (root is None): identical to today


# ---------------- common/configure_embed.py (NEW) ----------------
# Canonical #3297 signature, standalone (no self), NO library_name. cfg-direct (no unify step exists here).
def configure_embed(cfg, basename, root_folder, log_to_file=False):
    if cfg is None or root_folder is None:
        raise ValueError("configure_embed requires both cfg and root_folder")
    cfg = cfg if isinstance(cfg, AttributeDict) else AttributeDict(cfg)   # save_application_cfg needs attr access
    ts = datetime.datetime.now().strftime("%Y%m%d_%Hh%Mm")

    result_folder = os.path.join(root_folder, "results")
    os.makedirs(result_folder, exist_ok=True)                            # a write UNDER root (allowed)

    analysis = dict(cfg.get("Analysis", {}))                             # preserve any caller Analysis keys
    analysis.update({
        "analysis_root_folder": root_folder,    # honored by stocks modules + fm.router
        "result_folder": result_folder,         # save_application_cfg writes <result_folder>/<file_name>.yml here
        "file_name": f"{basename}_{ts}",
        "log_to_file": log_to_file,             # carried for #3297 parity (assethold engine writes no .log today)
    })
    cfg["Analysis"] = analysis
    cfg["_config_dir_path"] = root_folder       # locked-contract: PathResolver-relative writes resolve under root
    return cfg


# ---------------- common/provenance.py (NEW) ----------------
# AC#3: assethold's OWN provenance. Gated on #3282 for code_version; import-guarded fallback until it lands.
def assethold_code_version():
    try:
        from assetutilities.workflow_api import code_version          # #3282 (parameterized)
        return code_version("assethold")                              # NOT the assetutilities default
    except ImportError:
        from assethold import __version__                             # local fallback (pre-#3282)
        return {"package_version": __version__, "git_sha": _git_sha_or_none()}


# ---------------- engine.py ----------------
# Additive params; existing callers (embed=False, root_folder=None, log_to_file=False) byte-identical.
def engine(inputfile=None, cfg=None, config_flag=True,
           root_folder=None, log_to_file=False, embed=False) -> dict:
    if cfg is None:
        ... existing file-load (validate_arguments_run_methods -> ymlInput -> AttributeDict) UNCHANGED ...

    basename = cfg["basename"]
    fm = FileManagement()

    if embed:
        # ---- EMBED PATH (the crux #3287 consumes) ----
        if root_folder is None:
            raise ValueError("engine(embed=True) requires root_folder")
        cfg_base = configure_embed(cfg, basename, root_folder, log_to_file=log_to_file)
        cfg_base = fm.router(cfg_base)          # now writes under Analysis.analysis_root_folder == root
        logging.info(f"{basename}, application ... START")
        with output_root(root_folder):          # rebases workflow_io.output_path writes under root
            cfg_base = _dispatch(basename, cfg_base)   # existing if/elif extracted to a helper (no behavior change)
        save_application_cfg(cfg_base=cfg_base) # writes <root>/results/<file_name>.yml (set by configure_embed)
        logging.info(f"{basename}, application ... END")
        return cfg_base

    # ---- DEFAULT PATH (unchanged byte-identical) ----
    if config_flag:
        cfg_base = cfg
        cfg_base = fm.router(cfg_base)
    else:
        cfg_base = cfg
    logging.info(f"{basename}, application ... START")
    cfg_base = _dispatch(basename, cfg_base)    # same if/elif chain, no contextvar set => output_path unchanged
    save_application_cfg(cfg_base=cfg_base)
    logging.info(f"{basename}, application ... END")
    return cfg_base
```

> **Note on `_dispatch`:** extracting the existing `if basename == ... elif ...` chain into a private `_dispatch(basename, cfg_base)` helper is a pure refactor (same branches, same `raise Exception` for unknown basename) so both the default and embed paths share one dispatch site. The existing `test_engine_*` routing tests must stay green unchanged.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `assethold/src/assethold/engine.py` | add optional `root_folder`/`log_to_file`/`embed` params; add the `embed` branch (calls `configure_embed`, wraps dispatch in `output_root(root_folder)`); extract the `if/elif` dispatch into `_dispatch()` shared by both paths. Default path byte-identical. |
| Create | `assethold/src/assethold/common/configure_embed.py` | new standalone `configure_embed(cfg, basename, root_folder, log_to_file=False)` — canonical #3297 signature (no `self`, no `library_name`); makes cfg AttributeDict; sets `Analysis.{analysis_root_folder,result_folder,file_name,log_to_file}` + `_config_dir_path` under root; `makedirs(<root>/results)`. |
| Modify | `assethold/src/assethold/modules/workflow_io.py` | add `_output_root` ContextVar + `output_root()` context manager; make `output_path` rebase **relative** paths under the root when set. Default (unset) byte-identical. |
| Create | `assethold/src/assethold/common/provenance.py` | `assethold_code_version()` → `code_version("assethold")` (import-guarded; local `{package_version, git_sha}` fallback pre-#3282). |
| Create | `assethold/src/assethold/common/__init__.py` (if absent) | package marker for the new `common/` module dir. |
| Create | `assethold/tests/common/test_engine_embed_root.py` (+ `tests/common/` dir) | TDD: embed isolation across both write mechanisms, re-entrancy, absolute-path passthrough, default byte-identical, provenance. |
| Update | docs/plans/README.md | add this plan to the Plan Index. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_embed_workflow_io_writes_under_root | **(crux)** a `workflow_io`-based domain (e.g. portfolio) writes its `output_path` CSVs **only** under the injected root | `engine(cfg=<portfolio cfg with relative output paths>, embed=True, root_folder=<tmpA>)` run from a different scratch cwd | output files exist under `<tmpA>/...`; **nothing** created under the scratch cwd |
| test_embed_stocks_writes_under_root | the `stocks` domain (which uses `Analysis.analysis_root_folder`) writes under the injected root via `configure_embed` setting that key | `engine(cfg=<stocks cfg>, embed=True, root_folder=<tmpA>)` | stock outputs under `<tmpA>`; no skip-warning (root configured) |
| test_embed_cfg_dump_under_root | `save_application_cfg`'s `<file_name>.yml` lands under `<root>/results`, not cwd, and does not crash | `engine(cfg=..., embed=True, root_folder=<tmpA>)` | `<tmpA>/results/<basename>_<ts>.yml` exists; cwd unchanged |
| test_embed_sets_config_dir_path | `configure_embed` sets `cfg["_config_dir_path"] == root_folder` (locked-contract uniformity) | `configure_embed(cfg, "portfolio", <tmpA>)` | returned `cfg["_config_dir_path"] == <tmpA>` |
| test_embed_requires_root_folder | `engine(embed=True)` without `root_folder` raises `ValueError` | `engine(cfg=..., embed=True)` | `ValueError` |
| test_embed_absolute_output_path_not_rebased | an **absolute** config output path is left untouched (caller's explicit choice) | embed run with `outputs.x = "/abs/where/x.csv"` | write lands at `/abs/where/x.csv`, not under root |
| test_embed_repeated_calls_reentrant | two sequential embed calls with different roots stay isolated (ContextVar token reset; no bleed) | `engine(...,root_folder=<tmpA>)` then `engine(...,root_folder=<tmpB>)` | each writes only under its own root; `_output_root` is `None` after both |
| test_output_path_default_unchanged | **(backward-compat)** with no `output_root` context, `output_path` resolves relative → cwd exactly as today | `output_path("results/x.csv")` from scratch cwd | `<cwd>/results/x.csv`; parent dir created |
| test_engine_default_path_routing_unchanged | **(backward-compat)** existing routing/golden behavior preserved (re-runs the existing mocked routing assertions through the refactored `_dispatch`) | the existing `test_engine.py` matrix (stocks + 6 workflows + substring reject) | all pass unchanged |
| test_provenance_is_assethold_not_assetutilities | **(AC#3)** `assethold_code_version()` returns assethold's package version (not assetutilities') | call `assethold_code_version()` | `package_version` == assethold `__version__` (pre-#3282 fallback) / `code_version("assethold")` (post) — never the assetutilities default |

> **Ordering note:** every test in `test_engine_embed_root.py` exercises **assethold-local** code only (engine, configure_embed, workflow_io, provenance fallback) and is therefore **green without #3282/#3297 landing**. The `test_provenance_is_assethold_not_assetutilities` test pins the package-name parameterization and flips its assertion target (fallback → `code_version("assethold")`) automatically once `assetutilities.workflow_api` is importable.

---

## Acceptance Criteria

- [ ] **AC#1 — Embed writes nothing outside root:** `engine(cfg=..., embed=True, root_folder=<tmp>)` writes **nothing** outside `<tmp>` across BOTH write mechanisms (`workflow_io.output_path` domains AND the `stocks` `analysis_root_folder` domain) AND the `save_application_cfg` cfg-dump. Proven by `test_embed_workflow_io_writes_under_root` + `test_embed_stocks_writes_under_root` + `test_embed_cfg_dump_under_root`. No `os.chdir`.
- [ ] **AC#2 — Default behavior unchanged (golden):** no `embed`, no `root_folder` → routing + write locations byte-identical to today; `output_path` with no context resolves relative → cwd. Proven by `test_output_path_default_unchanged` + `test_engine_default_path_routing_unchanged` (existing `test_engine.py` matrix passes unchanged).
- [ ] **AC#3 — Provenance stamps assethold's version:** `assethold_code_version()` returns assethold's own `{package_version, git_sha}` via `code_version("assethold")` (parameterized per #3282) — **never** the assetutilities default. Proven by `test_provenance_is_assethold_not_assetutilities`. **Gated on #3282** for the `code_version` import; import-guarded local fallback until then.
- [ ] `configure_embed` honors the injected root incl `_config_dir_path` (`test_embed_sets_config_dir_path`) and is re-entrant (`test_embed_repeated_calls_reentrant`).
- [ ] Absolute config output paths are not rebased (`test_embed_absolute_output_path_not_rebased`).
- [ ] New tests pass: `uv run pytest assethold/tests/common/test_engine_embed_root.py -v`.
- [ ] No regression: `uv run pytest assethold/tests/unit/test_engine.py` passes; broader assethold suite shows no new failures attributable to this change.
- [ ] **#3287 hook stated:** the plan documents that #3287's `run_workflow` should call `engine(cfg=..., embed=True, root_folder=<tempdir>, log_to_file=False)` instead of its portfolio-only `redirect_outputs` hack.
- [ ] Legal/security scan clean (`scripts/legal/legal-sanity-scan.sh`); no client identifiers; no hardcoded secrets.
- [ ] Review artifacts posted to scripts/review/results/ (T2 = 2 providers; flagged for T3-depth — see Adversarial Review).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | |
| Codex | PENDING | |
| Gemini | PENDING | |

**Overall result:** PENDING (dispatch T2 wave, T3-depth, via `scripts/review/plan-review-fanout.sh`).

Revisions made based on review:
- (none yet — initial draft)

---

## Risks and Open Questions

- **Risk (issue premise stale — #3066):** the issue says "routes only stocks today; #3066 wires the rest." Reproduction shows #3066 **already landed** (`8d790c0`); the engine routes 8 domains. The plan is scoped to the **actual** state (cover all wired domains), not the stale premise. The "gated on #3066" condition is satisfied — flag for owner confirmation that #3066's GitHub issue should be closed.
- **Risk (provenance gated on #3282):** `code_version("assethold")` lives in the unlanded `assetutilities.workflow_api`. AC#3 is import-guarded with a local fallback so it is testable now; the assertion flips automatically when #3282 lands. If #3282's `code_version` signature differs from `code_version(package_name)`, the provenance helper adapts at implementation time. The embed-isolation core (AC#1/AC#2) has **no** such dependency.
- **Risk (version mismatch):** `src/assethold/__init__.py:9 __version__ = "0.0.1"` vs `pyproject.toml version = "0.1.0"`. `assethold_code_version()`'s fallback reads `__init__.__version__` (0.0.1) which disagrees with the packaged version (0.1.0). Open question for owner: reconcile (single-source the version) before relying on provenance — out of scope for the embed mechanics but flagged so the provenance value is trustworthy. `code_version("assethold")` from #3282 (which reads installed-package metadata) sidesteps this once landed.
- **Risk (ContextVar vs threads):** `_output_root` is a `ContextVar`, correct for sequential and asyncio-task isolation. True OS-thread-parallel embed runs sharing one process would each see their own context only if dispatched via `contextvars.copy_context`; the single-threaded repeated-call use case #3287/#3283 target is fully covered. Documented as residual (mirrors #3297's process-global-logging residual).
- **Risk (`fm.router` cfg shape):** `FileManagement.router` reads `cfg.Analysis["analysis_root_folder"]`; `configure_embed` sets it, so embed `fm.router` writes under root. But `fm.router` may expect additional `Analysis`/`file_management` keys for some cfgs. Mitigation: the embed branch runs `fm.router` exactly as the default path does after `configure_embed`; if a specific workflow cfg lacks keys `fm.router` needs, that is a pre-existing cfg-completeness requirement (not introduced here) — `configure_embed` raises early on missing `cfg`/`root_folder` rather than half-creating dirs. Test coverage uses real portfolio + stocks cfgs.
- **Risk (`save_application_cfg` for non-stocks domains today):** Reproduction shows `save_application_cfg` requires `Analysis.result_folder`/`file_name` — which the wired workflow_io domains do NOT set in a plain `engine(cfg=...)` call, so an un-embedded real run of e.g. portfolio likely crashes at `:72` today. `configure_embed` fixes this for the embed path. The **default** path is left untouched (out of scope: a separate hardening of the default path could set these, but #3308 must not change default behavior). Flag as a possible follow-on.
- **Open:** should `configure_embed` set `result_folder = <root>/results` (chosen here, mirrors assetutilities' `results/` convention) or `= root_folder` directly (flatter)? Recommendation: `<root>/results` for parity with #3297 and to keep the cfg-dump separate from workflow outputs. Flag for owner.

---

## Complexity: T2

**T2** — additive, backward-compatible, all within the assethold repo: one engine modified (small, no ApplicationManager), one shared-ish module extended (`workflow_io`, used by 8 modules but via a default-off ContextVar), two new small modules, one new test module. Simpler than #3297 (T3) because assethold's engine has no `ApplicationManager`/`set_logging`/load-bearing-clobber complexity. **Flagged for T3-depth review** (2→3 providers) because it (a) mirrors a cross-repo contract (#3297) that is owner-UNapproved, and (b) its provenance AC consumes the unlanded #3282 `code_version` — both warrant deeper scrutiny than a routine T2.
