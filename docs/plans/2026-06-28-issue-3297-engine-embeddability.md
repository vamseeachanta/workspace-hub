# Plan for #3297: wf-api(assetutilities) — make the engine embeddable (injected root, no cwd-coupled side effects)

> **Wave-2 cross-repo addendum (2026-06-28).** Wave-2 consumers exposed three contract points folded in here:
> 1. **`_config_dir_path` rebase (added to `configure_embed`):** quickcheck/config-dir-relative routers (e.g. digitalmodel wall-thickness) write to `cfg["_config_dir_path"]` (default `cwd`), NOT `Analysis.result_folder` — so `configure_embed` now sets `cfg["_config_dir_path"] = root_folder`, guaranteeing **every** router's writes land under the injected root. Test: `test_embed_rebases_config_dir_path`.
> 2. **Canonical signature (do not mis-mirror):** `configure_embed(self, cfg, basename, root_folder, log_to_file=False)` takes **NO `library_name`** (it skips the `unify_*` step, the only consumer of `library_name`). Adopters must call it positionally as such — NOT like the regular `configure(cfg, library_name, basename, ...)`.
> 3. **Per-repo engines:** this issue covers **assetutilities'** engine (worldenergydata reuses it). **digitalmodel** and **assethold** have their OWN engines → separate embed-port prereqs **#3307** (digitalmodel) and **#3308** (assethold) mirror this design. The shared `assetutilities.workflow_api.ResultEnvelope` types are imported by all; only engine dispatch is per-repo.
>
> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3297
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3297-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `assetutilities/src/assetutilities/engine.py:27` — `def engine(inputfile=None, cfg=None, config_flag=True) -> dict`. Three live entry shapes:
  - `config_flag=True` (default; both file and in-memory callers) → `app_manager.configure(cfg, library_name, basename, cfg_argv_dict, inputfile)` (`:45`), `fm.router` (`:46`), `app_manager.configure_result_folder(None, cfg_base)` (`:47-49`).
  - `config_flag=False` (`:50-51`) → `cfg_base = cfg` verbatim — **bypasses `configure()` and `configure_result_folder()` entirely**. The only in-process precedent (`yml_utilities.py:128`, `au_engine(inputfile=None, cfg=plot_yml, config_flag=False)`) uses exactly this, precisely because it must keep its in-memory `cfg` and cannot afford `configure()` discarding it.
- **ROOT FINDING (Round-1 MAJOR, verified 2026-06-28):** the in-memory `engine(cfg=..., config_flag=True)` path **does NOT honor the caller's `cfg`**. Trace:
  - `configure(run_dict=cfg, ...)` (`ApplicationManager.py:101`) → `unify_application_and_default_and_custom_yamls(run_dict=cfg, ...)` (`:102`) → `get_custom_file(run_dict=cfg, inputfile=None)` sets `self.customYaml=None` (no argv/inputfile) and `self.CustomInputs=None` (caller `cfg` has no `CustomInputs` key) (`:140-167`).
  - `self.ApplicationInputFile` (the `os.getcwd()/src/assetutilities/tests/test_data/<basename>.yml` path, `:117`) is not a file → loads the **packaged** `base_configs/modules/<basename>/<basename>.yml` via `pkgutil` into `self.ApplicationInputFile_dict` (`:122-133`).
  - `generateYMLInput(run_dict=cfg, cfg_argv_dict={})` (`:169-226`): `os.path.isfile(self.ApplicationInputFile)` is False → `cfg = self.ApplicationInputFile_dict` (`:174`) — **the packaged yaml, NOT the caller cfg**. With `customYaml is None` AND `CustomInputs is None` it takes the `else` branch (`:194-196`: `custom_file_data=""`, `default_yaml_file=None`), the `if (customYaml is not None) or (CustomInputs is not None)` merge guard (`:198`) is False, so the caller `cfg` (`run_dict`) is **never merged** and is returned discarded.
  - Proven by the reviewer: a sentinel `cfg["Analysis"]["analysis_root_folder"]` set by the caller came back **absent** from the configured cfg. So **the caller cfg is dropped at `generateYMLInput` (~:194-196), before any root resolution runs.**
- Found: `ApplicationManager.py:228-282` — `get_application_configuration_parameters()` computes `analysis_root_folder`:
  - `customYaml is not None` → `os.path.split(self.customYaml)[0]` (the input-file dir; `os.getcwd()` only if the path has no dir component) (`:231-235`).
  - `CustomInputs is not None` → `os.path.join(os.getcwd(), "tests", "cfg", basename)` (`:236-238`).
  - else (in-memory `config_flag=True`) → **`os.getcwd()`** (`:239-241`).
  - then `configure_result_folder(analysis_root_folder)` creates `<root>/results/{,Data,Plot}` (`:252-254`), **unconditionally** `os.mkdir(<root>/logs)` (`:256-258`), and **`cfg = update_deep_dictionary(cfg, app_config_params)`** (`:280`) merges the computed `analysis_root_folder` over whatever `cfg["Analysis"]["analysis_root_folder"]` held.
- **LOAD-BEARING CLOBBER (do NOT remove):** the `:280` merge is the mechanism that substitutes the **real runtime root** (`os.getcwd()` or the input-file dir) over any **stale/relative** `Analysis.analysis_root_folder` baked into an input file. Two hand-written worldenergydata fixtures depend on this exact substitution: `worldenergydata/tests/fixtures/bsee/test_bsee_config.yml:2` and `.../test_custom_config.yml:2` both ship `analysis_root_folder: tests\test_data\bsee\results` (a relative, Windows-slash, machine-portable placeholder) and rely on the clobber rewriting it to the real run root at config time. Removing or weakening the `:280` clobber on the default path breaks these. **The clobber is correct for the file/default path and must be preserved byte-identically.**
- Found: `ApplicationManager.py:284-335` — `configure_result_folder(analysis_root_folder, cfg_with_fm=None)`: when `analysis_root_folder is None` it reads it back from `cfg_with_fm["Analysis"]["analysis_root_folder"]` (`:288`); otherwise builds `<root>/results` (`:299-305`) + `Data`/`Plot` (`:310-316`). It already honors whatever root it is handed — **no signature change needed**; feeding it an injected root is sufficient.
- Found: `set_logging.py:9-55` — `set_logging(cfg)` **unconditionally** `os.makedirs(cfg["Analysis"]["log_folder"])` (`:17-18`), then a forced `.log` file via `logging.basicConfig(filename=..., filemode="w", force=True)` (`:28-36`) AND a loguru file sink (`:48`), on **every** call. No no-file mode.
- Found (re-entrancy hazard): `engine.py:21` instantiates a **module-level singleton** `app_manager = ConfigureApplicationInputs()`. `self.customYaml` / `self.CustomInputs` / `self.ApplicationInputFile` are **instance fields mutated by `get_custom_file()`** and read later by `get_application_configuration_parameters()`. Repeated in-process `engine()` calls (the #3282 `run_workflow` use case) reuse the same instance, so these fields leak across calls — a real re-entrancy/threading hazard the embed path must not inherit.
- Found (blast radius): shared `ConfigureApplicationInputs` / `engine` is imported by all 4 tier-1 repos — `digitalmodel/src/digitalmodel/engine.py`, `worldenergydata/src/worldenergydata/engine.py`, `assethold/...`, plus a **forked** copy at `digitalmodel/src/digitalmodel/asset_integrity/common/ApplicationManager.py`. Confirms the T3 blast radius; the fix must be purely additive (new optional params defaulting to today's behavior; a new method/branch that existing callers never reach).
- Gap: there is no existing golden/regression test asserting engine output *locations*. `tests/modules/data_exploration/test_df_basic_statistics.py:26` asserts only `assert result is not None`. There is **no `tests/common/` directory** (`ls` → absent); the new test module is created from scratch.

### Standards
Not applicable — harness/library plumbing change, no engineering standard involved.

### LLM Wiki pages consulted
No relevant wiki pages — this is internal engine plumbing, not domain knowledge.

### Documents consulted
- `docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md` — the blocked dependent. #3282's `run_workflow` needs an in-process call that honors an in-memory cfg AND sandboxes all writes under a tempdir. **Neither existing path delivers this:** `config_flag=True` discards the cfg (root finding above); `config_flag=False` keeps the cfg but never sets up a result folder and never calls `set_logging` in a controlled way. #3297 closes that gap by adding a dedicated embed path. #3282 will call **that embed path** with `root_folder=<tempdir>`, **not** `engine(cfg=..., config_flag=True)`.
- Issue #3297 body — design intent: an embeddable run that writes nothing outside an injected root, with no `os.chdir`, backward-compatible default.
- `docs/plans/2026-06-28-issue-3283-determinism-harness.md` — downstream Wave-2 consumer; confirms critical-path ordering #3297 → #3282 → #3283.

### Gaps identified
- No embeddable run path that preserves an in-memory cfg, writes only under an injected root, sets up the result folder, and uses no-file logging — all four at once.
- No explicit `root_folder` parameter on `engine()` / `configure()` / `get_application_configuration_parameters()`.
- No no-file/in-memory logging mode in `set_logging`; `os.makedirs(log_folder)` fires unconditionally.
- No re-entrancy-safe instance handling for repeated in-process runs (module singleton leaks `customYaml`/`CustomInputs`).
- No regression test pinning today's output locations or the load-bearing clobber.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3297` — OPEN — "wf-api(assetutilities): make the engine embeddable — injected root, no cwd-coupled side effects [PREREQ for #3282]"
- `#3282` — draft/blocked-on-#3297 (per its plan header) — ResultEnvelope/run_workflow

**File existence** (`ls`/`grep` 2026-06-28):
- EXISTS: `assetutilities/src/assetutilities/engine.py`, `.../common/ApplicationManager.py`, `.../common/set_logging.py`, `.../common/yml_utilities.py`
- MISSING (new — this plan creates): `assetutilities/tests/common/test_engine_embeddable_root.py` (and the `tests/common/` dir itself)

**Cfg-discard proof (the MAJOR):** `ApplicationManager.py:194-196` is the `else` branch (`customYaml is None` AND `CustomInputs is None`); `:198` gates the only merge of caller-supplied data; with both None the gate is False so `run_dict` (caller cfg) is never merged, and `:174` has already replaced `cfg` with the packaged `ApplicationInputFile_dict`. → caller cfg discarded **before** root resolution at `:239-241`.

**Load-bearing-clobber proof:** `grep -n analysis_root_folder worldenergydata/tests/fixtures/bsee/{test_bsee_config,test_custom_config}.yml` → both `:2  analysis_root_folder: tests\test_data\bsee\results` (relative placeholder); `ApplicationManager.py:280` rewrites it to the real run root at config time. Removing the clobber on the default path breaks these two fixtures.

**Unconditional side-effect proof:** `set_logging.py:17-18` (`os.makedirs(log_folder)` outside any guard) + `ApplicationManager.py:256-258` (`os.mkdir(<root>/logs)` outside any guard) → both create `logs/` on every config_flag=True call regardless of logging intent.

**Re-entrancy proof:** `engine.py:21  app_manager = ConfigureApplicationInputs()` is module-level; `get_custom_file` (`ApplicationManager.py:147,150,152,163,165,167`) assigns `self.customYaml` / `self.CustomInputs`; `get_application_configuration_parameters` (`:231,236`) reads them. Repeated calls share one instance.

**Gap proof:** `grep -n "result_folder\|assert" tests/modules/data_exploration/test_df_basic_statistics.py` → only `:26 assert result is not None`. No location golden exists.

<!-- Distinct sources: issue #3297 body (1), engine.py (2), ApplicationManager.py (3), set_logging.py (4), yml_utilities.py config_flag=False precedent (5), #3282 plan (6), worldenergydata fixtures (7), Round-1 review proof (8). Count: 8 >= 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3297-engine-embeddability.md |
| Tests | `assetutilities/tests/common/test_engine_embeddable_root.py` |
| Implementation (engine — embed branch + `root_folder`/`log_to_file` params) | `assetutilities/src/assetutilities/engine.py` |
| Implementation (new `configure_embed()` + `root_folder`/`log_to_file` on `configure()`/`get_application_configuration_parameters()`) | `assetutilities/src/assetutilities/common/ApplicationManager.py` |
| Implementation (no-file log mode; gated `makedirs`) | `assetutilities/src/assetutilities/common/set_logging.py` |
| Plan review — Claude | scripts/review/results/2026-06-28-plan-3297-claude.md |
| Plan review — Codex | scripts/review/results/2026-06-28-plan-3297-codex.md |
| Plan review — Gemini | scripts/review/results/2026-06-28-plan-3297-gemini.md |

---

## Deliverable

An embeddable `assetutilities` engine with **two distinct, additive mechanisms**, both defaulting to today's exact behavior:

1. **`root_folder` parameter** — an explicit Python parameter threaded `engine(root_folder=None)` → `configure(...)` → `get_application_configuration_parameters(...)` → `configure_result_folder(...)` → `set_logging(...)`. When `None` (every existing caller, all 4 downstream repos) the resolution is **byte-identical to today** (`os.getcwd()` / input-file dir, with the load-bearing clobber intact). When a caller on the file/default path passes a root, it overrides the resolved `analysis_root_folder` — the cfg-discarding `unify` step still runs (that path needs it to load+merge the input file).

2. **A dedicated embed run path** — `engine(cfg=..., embed=True, root_folder=<dir>)` (and the underlying `ConfigureApplicationInputs.configure_embed(...)`). This is the path #3282 needs and the **crux** of the issue: it dispatches the caller's in-memory cfg **directly**, **without** the `unify_application_and_default_and_custom_yamls` step that discards the cfg, sets up the result folder under the injected root, and uses no-file logging — so an in-process caller runs a real workflow that (a) honors its in-memory cfg, (b) writes only under `root_folder`, (c) gets `results/{,Data,Plot}`, (d) writes no `.log` and creates no `logs/`. No `os.chdir`.

> **#3282 implication (explicit):** `run_workflow` will call **`engine(cfg=<built cfg>, embed=True, root_folder=<tempdir>, log_to_file=False)`** — the embed path — **NOT** `engine(cfg=..., config_flag=True)`, which would silently discard the cfg.

---

## Pseudocode

```
# ---------------- engine.py ----------------
# Additive params; existing callers (root_folder=None, log_to_file=True, embed=False) byte-identical.
def engine(inputfile=None, cfg=None, config_flag=True,
           root_folder=None, log_to_file=True, embed=False) -> dict:
    ... existing cfg load (when cfg is None) + basename resolution (unchanged) ...

    if embed:
        # ---- EMBEDDABLE RUN PATH (the crux #3282 uses) ----
        # Preconditions: cfg is not None AND root_folder is not None AND cfg is a complete
        # run cfg (carries a `default` block with log_level + config.overwrite.output, as every
        # real workflow cfg does). Raise ValueError if cfg/root_folder missing.
        # Per-call instance => NO module-singleton re-entrancy (does not touch customYaml/CustomInputs).
        cfg_base = ConfigureApplicationInputs().configure_embed(
            cfg, basename, root_folder, log_to_file=log_to_file)
        cfg_base = fm.router(cfg_base)
        # NOTE: configure_embed already called configure_result_folder(root_folder);
        #       no second configure_result_folder needed.
    elif config_flag:
        # ---- DEFAULT / FILE PATH (unchanged except threaded params) ----
        cfg_base = app_manager.configure(cfg, library_name, basename, cfg_argv_dict, inputfile,
                                         root_folder=root_folder, log_to_file=log_to_file)
        cfg_base = fm.router(cfg_base)
        result_folder_dict, cfg_base = app_manager.configure_result_folder(None, cfg_base)
    else:
        cfg_base = cfg                      # existing config_flag=False precedent, untouched

    ... existing basename dispatch (if/elif on basename) — unchanged ...

    if cfg is None:
        save_application_cfg(cfg_base=cfg_base)
    cfg_base = app_manager.save_cfg(cfg_base=cfg_base)   # writes <root>/results/<file_name>; reads cfg only, no instance state
    return cfg_base


# ---------------- ApplicationManager.ConfigureApplicationInputs ----------------

# NEW: cfg-direct embed configuration — NO unify step (so the caller cfg is preserved, not discarded).
def configure_embed(self, cfg, basename, root_folder, log_to_file=False):
    if cfg is None or root_folder is None:
        raise ValueError("configure_embed requires both cfg and root_folder")
    application_start_time = datetime.datetime.now()

    custom_file_name = basename
    label = cfg.get("meta", {}).get("label", None)
    if label is not None:
        custom_file_name = custom_file_name + "_" + label
    file_name = custom_file_name + "_" + application_start_time.strftime("%Y%m%d_%Hh%Mm")

    analysis_root_folder = root_folder                          # INJECTED, authoritative; never os.getcwd()
    result_folder_dict, _ = self.configure_result_folder(analysis_root_folder)   # creates results/{,Data,Plot}
    log_folder = os.path.join(analysis_root_folder, "logs")     # value carried; NOT created here (set_logging gates it)
    # CROSS-REPO FIX (Wave-2): quickcheck/config-dir-relative routers (e.g. digitalmodel wall-thickness)
    # write to cfg["_config_dir_path"] (default Path.cwd()), NOT Analysis.result_folder. Rebase it to the
    # injected root so EVERY router's writes land under root_folder — not just routers that honor result_folder.
    cfg["_config_dir_path"] = analysis_root_folder              # config-relative outputs resolve under <root>

    app_config_params = {"Analysis": {
        "basename": basename,
        "analysis_root_folder": analysis_root_folder,
        "file_name": file_name,
        "file_name_for_overwrite": custom_file_name,
        "log_folder": log_folder,
        "log_to_file": log_to_file,
        "start_time": application_start_time,
        "cfg_array_file_names": None,
        "DefaultInputFile": cfg.get("default_yaml", None),
        "CustomInputFile": None,
    }}
    app_config_params["Analysis"] = update_deep_dictionary(app_config_params["Analysis"], result_folder_dict)
    cfg = update_deep_dictionary(cfg, app_config_params)        # MERGE INTO caller cfg (preserve), not replace
    cfg = self.configure_overwrite_filenames(cfg)              # reuses existing method
    cfg = self.convert_cfg_to_attribute_dictionary(cfg)
    cfg = set_logging(cfg)                                      # log_to_file=False -> no file, no logs/ dir
    return cfg


# MODIFIED: thread the two new params; default None/True => today's behavior.
def configure(self, run_dict, library_name, basename, cfg_argv_dict, inputfile=None,
              root_folder=None, log_to_file=True):
    cfg = self.unify_application_and_default_and_custom_yamls(run_dict, library_name, basename, cfg_argv_dict, inputfile)
    cfg = self.get_application_configuration_parameters(run_dict, basename, cfg,
                                                        root_folder=root_folder, log_to_file=log_to_file)
    cfg = self.configure_overwrite_filenames(cfg)
    cfg = self.convert_cfg_to_attribute_dictionary(cfg)
    cfg = set_logging(cfg)
    return cfg


# MODIFIED: override resolved root ONLY when root_folder param is explicitly provided.
#   DO NOT honor cfg["Analysis"]["analysis_root_folder"] (the load-bearing clobber must still win on default path).
def get_application_configuration_parameters(self, run_dict, basename, cfg,
                                             root_folder=None, log_to_file=True):
    ... existing if/elif computes custom_file_name AND analysis_root_folder (UNCHANGED) ...

    if root_folder is not None:
        analysis_root_folder = root_folder          # explicit override; the ONLY injection on this path

    ... file_name / file_name_for_overwrite derivation UNCHANGED ...

    result_folder_dict, cfg_with_fm = self.configure_result_folder(analysis_root_folder)

    log_folder = os.path.join(analysis_root_folder, "logs")
    if log_to_file:                                 # default True -> creates logs/ exactly as today
        if not os.path.exists(log_folder):
            os.mkdir(log_folder)

    app_config_params = {"Analysis": {..., "analysis_root_folder": analysis_root_folder,
                                      "log_folder": log_folder, "log_to_file": log_to_file, ...}}
    app_config_params["Analysis"] = update_deep_dictionary(app_config_params["Analysis"], result_folder_dict)
    cfg = update_deep_dictionary(cfg, app_config_params)   # LOAD-BEARING CLOBBER — unchanged; still wins when root_folder=None
    return cfg


# ---------------- set_logging.py ----------------
def set_logging(cfg):
    log_level = cfg["default"]["log_level"].upper()
    logNumericLevel = getattr(logging, log_level)
    if not isinstance(logNumericLevel, int):
        raise ValueError(...)
    log_to_file = cfg["Analysis"].get("log_to_file", True)    # default True -> unchanged

    # reset root handlers (unchanged)
    for h in logging.root.handlers[:]:
        logging.root.removeHandler(h)

    if log_to_file:
        if not os.path.exists(cfg["Analysis"]["log_folder"]):   # MOVED inside the branch (was unconditional :17-18)
            os.makedirs(cfg["Analysis"]["log_folder"])
        logfilename = os.path.join(cfg["Analysis"]["log_folder"], cfg["Analysis"]["file_name"] + ".log")
        logging.basicConfig(level=logNumericLevel, ..., filename=logfilename, filemode="w", force=True)
        loguru_handlers = [{"sink": sys.stdout, ...}, {"sink": logfilename, "serialize": True, "level": log_level}]
    else:
        logging.basicConfig(level=logNumericLevel, ..., stream=sys.stdout, force=True)   # NO file, NO makedirs
        loguru_handlers = [{"sink": sys.stdout, ...}]                                     # NO file sink

    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.info("Logging started successfully ...")
    logger.configure(handlers=loguru_handlers)
    logger.add(PropagateHandler())
    return cfg
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `assetutilities/src/assetutilities/engine.py` | add optional `root_folder`, `log_to_file`, `embed` params; add the `embed` branch that calls a per-call `ConfigureApplicationInputs().configure_embed(...)`; thread `root_folder`/`log_to_file` into `configure()` on the default branch |
| Modify | `assetutilities/src/assetutilities/common/ApplicationManager.py` | add `configure_embed()` (cfg-direct, no `unify`, injected-root-authoritative, merges into caller cfg); add `root_folder`/`log_to_file` to `configure()` and `get_application_configuration_parameters()` (override root only when `root_folder is not None`; gate the `logs/` mkdir on `log_to_file`). **DROP the cfg-preset-honoring idea entirely** — never read `cfg["Analysis"]["analysis_root_folder"]` as an injection source; the `:280` clobber stays load-bearing on the default path |
| Modify | `assetutilities/src/assetutilities/common/set_logging.py` | move the `os.makedirs(log_folder)` (`:17-18`) inside a `log_to_file` branch; add no-file mode (stdout-only logging, no file sink) gated on `cfg["Analysis"].get("log_to_file", True)` |
| Create | `assetutilities/tests/common/test_engine_embeddable_root.py` (+ `tests/common/` dir) | TDD: embed-path isolation/cfg-honoring/re-entrancy/no-file, file-path `root_folder` override, backward-compat default + load-bearing-clobber regression + file-path golden |
| Update | docs/plans/README.md | add this plan to the Plan Index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_embed_honors_in_memory_cfg | **(crux / MAJOR fix)** the embed path keeps caller cfg keys instead of discarding them | `engine(cfg=<cfg with a sentinel key under e.g. data/settings>, embed=True, root_folder=<tmpA>)` | sentinel key survives into returned cfg; workflow actually dispatched on caller cfg (not the packaged base_config) |
| test_embed_writes_only_under_root | embed writes `results/` under the injected root and **nothing** at cwd | embed run from a different scratch cwd, `root_folder=<tmpA>` | `<tmpA>/results/{,Data,Plot}` exist; cwd child set unchanged (no new `logs`/`results`) |
| test_embed_no_logfile_no_logs_dir | embed default `log_to_file=False` writes no `.log` and creates no `logs/` | `engine(cfg=..., embed=True, root_folder=<tmpA>, log_to_file=False)` | no `*.log` anywhere; `<tmpA>/logs` not created; logging still emits to stdout |
| test_embed_repeated_calls_reentrant | **(re-entrancy / MAJOR-7)** two sequential embed calls with different roots stay isolated — proves per-call instance, no `customYaml`/`CustomInputs` bleed | `engine(cfg=..., embed=True, root_folder=<tmpA>)` then `engine(cfg=..., embed=True, root_folder=<tmpB>)` | each call writes only under its own root; no state from call 1 affects call 2 |
| test_file_path_root_folder_override | `root_folder` param on the file/default path redirects all outputs to the injected dir | `engine(<abs input.yml>, root_folder=<tmpA>)` | `<tmpA>/results/...` + (with default logging) `<tmpA>/logs/*.log`; nothing under the input file's own dir |
| test_default_no_injection_uses_cwd | **(backward-compat)** no `root_folder`, no embed → root defaults to `os.getcwd()` exactly as today (forced `.log` + results preserved) | `engine(cfg=...)` from scratch cwd | `<cwd>/logs/*.log` + `<cwd>/results/{,Data,Plot}` created (today's contract) |
| test_default_clobber_preserves_cwd_over_stale_preset | **(backward-compat / MAJOR-1 regression)** a cfg carrying a stale/relative `Analysis.analysis_root_folder` AND no `root_folder` still resolves the root to `os.getcwd()` (the load-bearing `:280` clobber preserved) | `get_application_configuration_parameters(run_dict, basename, cfg={...Analysis:{analysis_root_folder: "tests\\test_data\\stale"}}, root_folder=None)` from scratch cwd | resolved `cfg.Analysis.analysis_root_folder == os.getcwd()` (stale value overwritten, as the worldenergydata fixtures rely on) |
| test_cli_path_output_locations_unchanged_golden | **(backward-compat golden)** the file-based CLI path lands outputs in the same locations as before | `engine(<abs path to df_basic_statistics.yml>)` | result CSVs/yml under the input file's `results/` (same as pre-change baseline) |
| test_no_file_mode_makedirs_not_called | **(MINOR-5)** with `log_to_file=False`, `set_logging` creates no `logs/` dir even if `log_folder` points at a non-existent path | `set_logging(cfg with Analysis.log_to_file=False, log_folder=<nonexistent>)` | `<nonexistent>` not created; stdout logging works |
| test_existing_data_exploration_suite_passes | no regression in the existing data_exploration tests | run `tests/modules/data_exploration/` | all pass |

> **Removed vs Round-1:** `test_cfg_preset_root_honored` is **deleted** — the cfg-preset honoring mechanism is dropped entirely (MAJOR-1 + MAJOR-3): it is non-functional on the `config_flag=True` path (caller cfg discarded before any root read) and reading the cfg preset as an injection source would break the load-bearing `:280` clobber the worldenergydata fixtures depend on. `test_param_overrides_cfg_preset` is replaced by `test_file_path_root_folder_override` (param vs default-cwd, no cfg-preset involved).

---

## Acceptance Criteria

- [ ] New tests pass: `uv run pytest assetutilities/tests/common/test_engine_embeddable_root.py -v`
- [ ] **Embed path honors the in-memory cfg** — `engine(cfg=..., embed=True, root_folder=<tmpdir>)` dispatches the caller's cfg (not the packaged base_config); proven by `test_embed_honors_in_memory_cfg`. (This is the Round-1 MAJOR.)
- [ ] **Embed path is sandboxed** — it writes **only** under `<root_folder>` (`results/{,Data,Plot}`), no `logs/`, no `.log`, nothing at cwd; `test_embed_writes_only_under_root` + `test_embed_no_logfile_no_logs_dir` assert it. No `os.chdir`.
- [ ] **Embed path is re-entrant** — repeated in-process embed calls with different roots stay isolated (per-call `ConfigureApplicationInputs()` instance, no shared `customYaml`/`CustomInputs`); `test_embed_repeated_calls_reentrant`.
- [ ] **`root_folder` param on the file/default path** redirects outputs to the injected dir when provided; `test_file_path_root_folder_override`.
- [ ] **Backward compatible (default path byte-identical):** no `root_folder`, no `embed` → output locations + forced `.log` unchanged, AND a stale/relative `Analysis.analysis_root_folder` is still clobbered to `os.getcwd()` (worldenergydata fixtures preserved). Proven by `test_default_no_injection_uses_cwd` + `test_default_clobber_preserves_cwd_over_stale_preset` + `test_cli_path_output_locations_unchanged_golden`.
- [ ] **No-file logging creates nothing:** `set_logging` with `log_to_file=False` makes no `logs/` dir and no `.log`; `test_no_file_mode_makedirs_not_called`.
- [ ] No regression: `uv run pytest assetutilities/tests/modules/data_exploration/` passes; broader suite shows no new failures attributable to this change.
- [ ] `digitalmodel` / `worldenergydata` / `assethold` callers (which never pass the new params and never use `embed`) are unaffected — argued from the additive-default signature + the new branch being unreachable without `embed=True`, and spot-checked by importing their `engine` modules.
- [ ] **#3282 hook stated:** the plan documents that `run_workflow` will call `engine(cfg=..., embed=True, root_folder=<tempdir>, log_to_file=False)`, not the `config_flag=True` path.
- [ ] Review artifacts posted to scripts/review/results/ (T3 = 3 providers).

---

## Adversarial Review Summary

**Round-1: MAJOR — ADDRESSED in this revision.** Root finding: `engine(cfg=..., config_flag=True)` discards the caller cfg at `generateYMLInput` (`ApplicationManager.py:194-196`) before any root resolution, so the previous plan's cfg-preset-honoring mechanism was non-functional AND would have broken the load-bearing `:280` clobber the worldenergydata fixtures depend on. Disposition:

- **MAJOR-1 / MAJOR-3 (cfg-preset non-functional + breaks backward-compat):** dropped the cfg-preset honoring entirely; removed `test_cfg_preset_root_honored`; the `:280` clobber is preserved on the default path (new `test_default_clobber_preserves_cwd_over_stale_preset` guards it).
- **MAJOR-4 (no working embed path):** added a dedicated embed path (`engine(embed=True)` → new `configure_embed()`) that bypasses the cfg-discarding `unify` step, dispatches the caller cfg directly, sets up the result folder under the injected root, and uses no-file logging. Verified against the real `engine.py` / `ApplicationManager.py` call chain. #3282 hook stated explicitly.
- **MAJOR-7 (module-singleton re-entrancy):** embed path uses a per-call `ConfigureApplicationInputs()` instance (never touches `customYaml`/`CustomInputs`); `test_embed_repeated_calls_reentrant` proves isolation; residual process-global logging state documented under Risks.
- **MAJOR-3 narrative fix:** Resource Intelligence corrected — the `:280` clobber is **load-bearing for the file/default path**, NOT the in-memory blocker (the caller value is already gone at `:194-196`).
- **MINOR-5 (unconditional makedirs):** `set_logging.py:17-18` `makedirs` moved inside the `log_to_file` branch; `test_no_file_mode_makedirs_not_called` guards it.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | Round-1: MAJOR | cfg discarded before root read; clobber load-bearing; need real embed path; re-entrancy |
| Codex | PENDING (Round-2) | |
| Gemini | PENDING (Round-2) | |

**Overall result:** Round-1 MAJOR addressed; **Round-2 PENDING** (re-dispatch T3 wave via `scripts/review/plan-review-fanout.sh`).

Revisions made based on Round-1 review:
- Dropped cfg-preset honoring + its AC + `test_cfg_preset_root_honored`.
- Added `configure_embed()` + `engine(embed=True)` path (the crux #3282 consumes).
- Added re-entrancy fix (per-call instance) + test.
- Corrected the root-cause narrative (cfg discarded at `:194-196`; `:280` clobber load-bearing for file path).
- Added `test_default_clobber_preserves_cwd_over_stale_preset` regression (worldenergydata fixtures).
- Gated `set_logging` `makedirs` + `get_application_configuration_parameters` `logs/` mkdir on `log_to_file`.

---

## Risks and Open Questions

- **Risk (T3 blast radius):** shared `ApplicationManager`/`engine` feeds 4 tier-1 repos + a digitalmodel fork. Mitigation: every new parameter defaults to today's behavior (`root_folder=None`, `log_to_file=True`, `embed=False`); the embed branch is unreachable without `embed=True`; the default `if/elif` resolution is left byte-identical and only an *additional* `if root_folder is not None` override is appended. The two backward-compat tests + the clobber regression are the guardrails. The digitalmodel fork is **out of scope** for #3297 (it is a copy, not an import of this module); a follow-on issue should track porting the embed path there if/when digitalmodel needs embeddability.
- **Risk (embed cfg completeness):** `configure_embed` reuses `configure_overwrite_filenames` (reads `cfg["default"]["config"]["overwrite"]["output"]`) and `set_logging` (reads `cfg["default"]["log_level"]`). The embed cfg MUST therefore carry a `default` block — which every real workflow cfg (and #3282's built cfg) does. Mitigation: document this precondition; `configure_embed` raises a clear `ValueError`/`KeyError` early rather than half-creating dirs. Open question for the user: should `configure_embed` default-fill `log_level`/`overwrite` when absent (more forgiving) or fail-closed (stricter)? Recommendation: **fail-closed** with a precise message — embedders build full cfgs.
- **Risk (process-global logging state):** `logging.basicConfig(force=True)` + `logger.configure` mutate process-global logging on every call, including repeated embed calls. The per-call-instance fix removes the *config-state* re-entrancy hazard but NOT the global-logging reconfiguration (each embed call resets logging). This matches today's behavior and is acceptable for the single-threaded repeated-call use case #3282 targets; documented here as a residual. True multi-threaded embedding would need a logging lock — out of scope for #3297, flag as a follow-on if #3283's determinism harness runs workflows concurrently.
- **Risk (clobber subtlety):** the default path keeps `update_deep_dictionary(cfg, app_config_params)` at `:280` exactly as today; the new override only changes `analysis_root_folder` *before* `app_config_params` is built, and only when `root_folder is not None`. With `root_folder=None` the branch is skipped entirely → zero behavioral delta. `test_default_clobber_preserves_cwd_over_stale_preset` is the explicit guard.
- **Open:** `unify_application_and_default_and_custom_yamls` (`:117`) joins `os.getcwd()` for a *read* path (locating a packaged default yml). The embed path bypasses `unify` entirely, so this is moot for embedders. It remains a latent footgun for the **file/default** path if run from an unexpected cwd, but it is a read (no write side effect) and out of scope for #3297. Flag as a possible follow-on if it bites #3282 adoption.

---

## Complexity: T3

**T3** — modifies the shared assetutilities engine that all 4 tier-1 repos (assetutilities/digitalmodel/worldenergydata/assethold) depend on; backward compatibility is mandatory and proven by golden/regression tests (including the load-bearing-clobber regression); a new embed entry point is introduced and consumed by #3282; 3-provider adversarial review required. Per the issue's own T3 classification.
