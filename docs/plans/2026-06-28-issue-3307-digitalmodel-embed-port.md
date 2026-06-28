# Plan for #3307: wf-api(digitalmodel) — engine embed-port (mirror #3297 for digitalmodel's own engine)

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3307
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3307-claude.md | ...-codex.md | ...-gemini.md

---

## Context and locked contract (consume AS SPECIFIED — do not redesign)

This is the **digitalmodel** sibling of the per-repo engine-embeddability work. The canonical embed contract is owned by **#3297 (assetutilities)**, re-locked at plan-review 2026-06-28 (no-MAJOR). #3307 ports that contract onto digitalmodel's **own** `engine()` entrypoint. The relevant locked points:

- **#3297** — canonical signature `configure_embed(self, cfg, basename, root_folder, log_to_file=False)` — **NO `library_name`**. It sets `analysis_root_folder=root`, log folders under root, AND **`cfg["_config_dir_path"] = root`** so config-relative routers (which resolve outputs against `_config_dir_path`) write under the injected root. `engine(cfg=..., embed=True, root_folder=, log_to_file=False)` is the embed path. Default (no root) byte-identical.
- **Per-repo engines (owner-confirmed 2026-06-28):** assetutilities engine = #3297 (worldenergydata reuses it). **digitalmodel has its OWN engine → embed-port #3307.** Each port MIRRORS #3297 and reuses the shared `assetutilities.workflow_api.ResultEnvelope` types. **Only the engine dispatch is per-repo.**
- **configure_embed CALL:** positional `(cfg, basename, root_folder, log_to_file=)` — NEVER pass `library_name` (that is only on the regular `configure()`).

**What #3307 does NOT do** (scope guard): it does not adopt `ResultEnvelope`, does not register registry rows, does not emit `code_version`/provenance, and does not resolve `repo:id@version` ids. Those are #3285 (digitalmodel adopt-envelope), #3284 (discovery/id-resolution), and #3282 (run_workflow/envelope). #3307 delivers **only** the embed entrypoint that #3285's digitalmodel-bound `run_workflow` will call.

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/engine.py:69` — `def engine(inputfile=None, cfg=None, config_flag=True) -> dict`. This is digitalmodel's **own** engine, distinct from assetutilities'. Three behaviors matter:
  - `engine.py:4` imports `ConfigureApplicationInputs` from **`assetutilities.common.ApplicationManager`** (the shared one, the target of #3297) and `engine.py:57` instantiates a **module-level singleton** `app_manager = ConfigureApplicationInputs()`. **digitalmodel's live `engine()` reuses assetutilities' ApplicationManager — it does NOT use the asset_integrity fork.** So `configure_embed` is provided by #3297; #3307 only wires the engine.
  - `engine.py:87-90` — when `cfg is None` (file path), the engine sets `cfg["_config_file_path"]` and **`cfg["_config_dir_path"] = os.path.dirname(os.path.abspath(inputfile))`** (`:89`), then logs it (`:90`). This is the digitalmodel-specific config-dir tracking that the shared assetutilities engine does not have.
  - `engine.py:99-122` (`config_flag` branch) — calls `app_manager.configure(cfg, library_name, basename, cfg_argv_dict, inputfile=inputfile)` (`:105`/`:111`), then **manually re-copies** `_config_file_path`/`_config_dir_path` from the original `cfg` onto `cfg_base` (`:114-118`), then `fm.router(cfg_base)` (`:119`), then `app_manager.configure_result_folder(None, cfg_base)` (`:120-122`).
  - `engine.py:123-124` (`else`/`config_flag=False`) → `cfg_base = cfg` verbatim.
  - `engine.py:135-594` — a large `if/elif basename` dispatch; `engine.py:597` `app_manager.save_cfg(cfg_base=cfg_base)`; `engine.py:599` `return cfg_base`.
- Found (the load-bearing router): `digitalmodel/src/digitalmodel/structural/wall_thickness_quickcheck.py:72-89` — `WallThicknessQuickCheck.router(cfg)` derives `config_dir = Path(cfg.get("_config_dir_path", Path.cwd()))` (`:73`) and resolves **all four outputs** (cache, output_html, output_json, output_csv) relative to it via `_resolve_path(config_dir, value)` (`:34-38`, `:75-78`), then `mkdir(parents=True)` + writes the HTML/JSON/CSV under `config_dir`. **This is exactly why `configure_embed` must rebase `_config_dir_path` to root** — otherwise the quickcheck writes next to the input file, escaping the injected root. `engine.py:280-286` routes `basename == "wall_thickness"` to this class.
- Found (the dispatch breadth): `grep "_config_dir_path"` returns **20+** digitalmodel routers (ansys, code_checks, compare_tool, drilling_riser, fatigue, field_development, geotechnical, hydrodynamics, installation, lifting_lug, marine_ops, …). They all read `_config_dir_path` for relative I/O, so the rebase is load-bearing across the whole digitalmodel router surface, not just wall-thickness.
- Found (save target honors root): `assetutilities/.../common/ApplicationManager.py:370-378` — `save_cfg` writes the cfg dump to `cfg_base.Analysis["analysis_root_folder"]/results/<file_name>`. Since `configure_embed` sets `analysis_root_folder=root`, the `engine.py:597` `save_cfg` lands under root. `save_cfg` reads cfg only (no instance state) → the module singleton at `engine.py:57` is safe for this call even in embed mode.
- Gap: digitalmodel's `engine()` has **no `embed` / `root_folder` / `log_to_file` params** and **no embed branch**. There is no way today to run a digitalmodel workflow in-process with all writes sandboxed under an injected root.
- Out of scope (documented): the **forked** `digitalmodel/src/digitalmodel/asset_integrity/common/ApplicationManager.py` is a legacy copy with a *different* API (`ConfigureApplicationInputs(basename)` ctor; `configure(run_dict)`; Windows `\\`-joined paths; `os.getcwd()`-rooted). `grep` shows it is referenced only by `src/digitalmodel.egg-info/SOURCES.txt` — **no live import on the `engine()` path**. #3307 does NOT touch it (porting the fork's embed path would be dead work). Flagged in Risks.

### Standards
Not applicable — harness/library plumbing change, no engineering standard or calc constant involved (so `calc-citation-contract.md` does not fire).

### LLM Wiki pages consulted
No relevant wiki pages — internal engine plumbing, not domain knowledge. (`Client: N/A`; `wiki-sibling-routing.md` out of scope.)

### Documents consulted
- `docs/plans/2026-06-28-issue-3297-engine-embeddability.md` — the canonical contract being mirrored. Confirms: canonical `configure_embed(self, cfg, basename, root_folder, log_to_file=False)` signature (no `library_name`); `cfg["_config_dir_path"] = root_folder` rebase added there for assetutilities' own `path_resolver.py` fallback; per-call `ConfigureApplicationInputs()` instance for re-entrancy; default byte-identical; #3282 calls `engine(embed=True, root_folder=, log_to_file=False)`. #3297 is **not yet landed** (status:plan-review) — HARD DEP for #3307.
- `docs/plans/2026-06-28-issue-3285-digitalmodel-adopt-envelope.md` — the dependent. Its **G0** explicitly names "digitalmodel's `engine()` is a FORK without the embed path (#3297 explicitly scoped the fork OUT) → port the embed branch into `digitalmodel/engine.py`." #3307 **owns** that port; #3285 **consumes** it (do not have #3285 re-create it). #3285 is at `status:needs-plan`.
- `docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md` — `run_workflow(workflow_id, params, cfg)` lives in assetutilities and calls assetutilities' engine; per-repo engines provide their own runner reusing the shared `ResultEnvelope`. digitalmodel's runner (built in #3285) will call digitalmodel's `engine(embed=True, ...)` — the entrypoint #3307 creates.
- Issue #3307 body — scope: `engine(embed=True, root_folder=, log_to_file=False)` + `configure_embed` honoring injected root incl `cfg["_config_dir_path"]=root`; reuse shared `assetutilities.workflow_api.ResultEnvelope`; default byte-identical; blocks #3285; T3 (digitalmodel is large).

### Gaps identified
- No embed entrypoint on digitalmodel's `engine()` (no `embed`/`root_folder`/`log_to_file` params, no embed branch).
- No mechanism that forces `_config_dir_path` to the injected root in an in-process run — and digitalmodel's `engine.py:114-118` **actively re-copies** the original cfg's `_config_dir_path` onto `cfg_base`, which (if reused in embed mode) would *defeat* the rebase. The port must skip that re-copy in embed mode.
- No re-entrancy-safe per-call instance for repeated in-process runs (digitalmodel reuses the `engine.py:57` module singleton).
- No regression/golden test pinning digitalmodel's current default output locations or the embed isolation.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3307` — OPEN, `status:needs-plan`, `lane:codex` — "wf-api(digitalmodel): engine embed-port — mirror #3297 …[prereq for #3285]"
- `#3297` — OPEN, `status:plan-review`, `lane:codex` — assetutilities embeddability (HARD DEP, **not landed**)
- `#3285` — OPEN, `status:needs-plan`, `lane:codex` — digitalmodel adopt-envelope (the consumer #3307 blocks)
- `#3282` — OPEN, `status:plan-review` — run_workflow/ResultEnvelope (foundational)
- `#3281` — OPEN — EPIC parent

**File existence** (`ls`/`grep` 2026-06-28):
- EXISTS: `digitalmodel/src/digitalmodel/engine.py` (599 lines), `digitalmodel/src/digitalmodel/structural/wall_thickness_quickcheck.py`
- EXISTS (legacy, out of scope): `digitalmodel/src/digitalmodel/asset_integrity/common/ApplicationManager.py`
- EXISTS (provider of `configure_embed` once #3297 lands): `assetutilities/src/assetutilities/common/ApplicationManager.py` — current `configure(self, run_dict, library_name, basename, cfg_argv_dict, inputfile=None)` at `:101`, **no `configure_embed` yet** (confirms #3297 unlanded)
- MISSING (new — this plan creates): `digitalmodel/tests/test_engine_embed_root.py`

**`_config_dir_path` set/read proof** (`Read` 2026-06-28):
```
engine.py:89   cfg["_config_dir_path"] = os.path.dirname(os.path.abspath(inputfile))
engine.py:117-118   if "_config_dir_path" in cfg:  cfg_base["_config_dir_path"] = cfg["_config_dir_path"]
wall_thickness_quickcheck.py:73   config_dir = Path(cfg.get("_config_dir_path", Path.cwd()))
```

**digitalmodel reuses assetutilities ApplicationManager (not the fork) proof:**
```
engine.py:4    from assetutilities.common.ApplicationManager import ConfigureApplicationInputs
engine.py:57   app_manager = ConfigureApplicationInputs()
grep "asset_integrity.common.ApplicationManager" src/ → only src/digitalmodel.egg-info/SOURCES.txt (no live import)
```

**save_cfg honors root proof** (`assetutilities ApplicationManager.py:370-378`):
```
def save_cfg(self, cfg_base):
    output_dir = cfg_base.Analysis["analysis_root_folder"]
    filename_path = os.path.join(output_dir, "results", filename)
```

**Reproduction proofs (Step 1.5):**
The embed path does not exist yet, so "embed isolates writes" cannot be run pre-port. Instead the load-bearing **mechanism** the port relies on — that the wall-thickness/config-relative router resolves outputs against `_config_dir_path` — is reproduced directly against the real module (stdlib-only helpers, no heavy deps):
```
$ python3 scratchpad/repro.py   # imports the real wall_thickness_quickcheck.py
no _config_dir_path -> default base: True            # router falls back to Path.cwd() (line 73)
relative resolves under injected root: True -> /tmp/embed_root_demo/output/report.json
absolute escapes root: True                          # _resolve_path returns abs path verbatim
```
- Reproduced at: 2026-06-28.
- Conclusion 1 (load-bearing): with NO `_config_dir_path`, the router writes under `cwd`; setting `cfg["_config_dir_path"]=root` (the #3297 rebase) lands **relative** outputs under root. Matches the issue claim that the rebase is required for digitalmodel embed isolation. YES.
- Conclusion 2 (residual hazard surfaced): a cfg whose quickcheck output paths are **absolute** escapes the root regardless of the rebase — recorded under Risks (not a regression; an isolation boundary the embed contract cannot enforce for absolute-path cfgs).

> Distinct sources: issue #3307 body (1), digitalmodel `engine.py` (2), `wall_thickness_quickcheck.py` (3), #3297 plan (4), #3285 plan (5), #3282 plan (6), assetutilities `ApplicationManager.py` save_cfg/configure (7), the asset_integrity fork + SOURCES.txt grep (8), Step-1.5 reproduction (9). Count: 9 ≥ 3.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3307-digitalmodel-embed-port.md |
| Implementation (engine — embed branch + `root_folder`/`log_to_file`/`embed` params; skip `_config_dir_path` re-copy in embed mode) | `digitalmodel/src/digitalmodel/engine.py` |
| Tests | `digitalmodel/tests/test_engine_embed_root.py` |
| Plan review — Claude | scripts/review/results/2026-06-28-plan-3307-claude.md |
| Plan review — Codex | scripts/review/results/2026-06-28-plan-3307-codex.md |
| Plan review — Gemini | scripts/review/results/2026-06-28-plan-3307-gemini.md |
| Plan index | docs/plans/README.md |

> **Note:** `configure_embed` itself is NOT created here — it is delivered by #3297 in `assetutilities/src/assetutilities/common/ApplicationManager.py`. #3307 only consumes it. No assetutilities file is modified by #3307.

---

## Deliverable

A digitalmodel `engine(cfg=..., embed=True, root_folder=<dir>, log_to_file=False)` path that runs a digitalmodel workflow in-process and writes **nothing outside `<dir>`** — including the config-relative routers (wall-thickness quickcheck and the 20+ peers that read `_config_dir_path`) — by reusing assetutilities' `configure_embed` (#3297) and ensuring `_config_dir_path` is rebased to the injected root and **not** clobbered back to the input-file dir by digitalmodel's `engine.py:114-118` preservation block. Default behavior (no `embed`, no `root_folder`) is byte-identical to today's digitalmodel CLI. This is the entrypoint #3285's digitalmodel-bound `run_workflow` will call.

---

## Pseudocode

```
# ---------------- digitalmodel/src/digitalmodel/engine.py ----------------
# Additive params; existing callers (embed=False, root_folder=None) byte-identical.
def engine(inputfile=None, cfg=None, config_flag=True,
           root_folder=None, log_to_file=False, embed=False) -> dict:

    cfg_argv_dict = {}
    if cfg is None:
        ... existing arg validation + yml load + AttributeDict ...
        if inputfile and os.path.exists(inputfile):
            cfg["_config_file_path"] = os.path.abspath(inputfile)
            cfg["_config_dir_path"] = os.path.dirname(os.path.abspath(inputfile))   # unchanged (:89)

    ... existing basename resolution (cfg["basename"] / cfg["meta"]["basename"]) — unchanged ...

    if embed:
        # ---- EMBEDDABLE RUN PATH (the crux #3285 consumes) ----
        if cfg is None or root_folder is None:
            raise ValueError("engine(embed=True) requires both cfg and root_folder")
        fm = FileManagement()
        # Per-call instance => no engine.py:57 module-singleton re-entrancy leak.
        # configure_embed (from #3297) sets analysis_root_folder=root, log folders under root,
        # AND cfg["_config_dir_path"] = root_folder. Positional call — NO library_name.
        cfg_base = ConfigureApplicationInputs().configure_embed(
            cfg, basename, root_folder, log_to_file=log_to_file)
        # DELIBERATELY DO NOT re-copy _config_dir_path/_config_file_path from the original cfg
        # (engine.py:114-118 does that on the default path) — that would overwrite the rebased
        # root and send config-relative routers back to the input-file dir, defeating isolation.
        cfg_base = fm.router(cfg_base)
        # configure_embed already created results/{,Data,Plot}; NO second configure_result_folder.
    elif config_flag:
        # ---- DEFAULT / FILE PATH (unchanged; root_folder threaded additively) ----
        fm = FileManagement()
        ... existing pytest-argv shuffle around app_manager.configure(...) ...
        cfg_base = app_manager.configure(cfg, library_name, basename, cfg_argv_dict,
                                         inputfile=inputfile,
                                         root_folder=root_folder, log_to_file=log_to_file)  # see Open decision
        if "_config_file_path" in cfg: cfg_base["_config_file_path"] = cfg["_config_file_path"]   # :115-116 unchanged
        if "_config_dir_path"  in cfg: cfg_base["_config_dir_path"]  = cfg["_config_dir_path"]    # :117-118 unchanged
        cfg_base = fm.router(cfg_base)
        result_folder_dict, cfg_base = app_manager.configure_result_folder(None, cfg_base)        # :120 unchanged
    else:
        cfg_base = cfg                              # config_flag=False precedent, untouched

    ... existing output-control + the entire if/elif basename dispatch — UNCHANGED ...

    app_manager.save_cfg(cfg_base=cfg_base)         # reads cfg only -> writes <root>/results in embed mode
    return cfg_base
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/src/digitalmodel/engine.py` | add optional `root_folder=None`, `log_to_file=False`, `embed=False` params; add the `embed` branch (per-call `ConfigureApplicationInputs().configure_embed(cfg, basename, root_folder, log_to_file=)`, **no** `library_name`, **skip** the `:114-118` `_config_dir_path` re-copy, **skip** the second `configure_result_folder`); thread `root_folder`/`log_to_file` into the default-path `app_manager.configure(...)` call (additive — see Open decision) |
| Create | `digitalmodel/tests/test_engine_embed_root.py` | TDD: embed isolation / `_config_dir_path` rebase / re-entrancy / no-file logging / backward-compat default + signature guard |
| Update | docs/plans/README.md | add this plan to the Plan Index |

> **Not modified:** `assetutilities/...` (provides `configure_embed` via #3297) and `digitalmodel/.../asset_integrity/common/ApplicationManager.py` (legacy fork, not on the `engine()` path).

---

## TDD Test List

> Tests target the `wall_thickness` basename because it is the **only** scope workflow routable through `engine()` today (per #3285's engine-routability audit) AND it is the canonical `_config_dir_path` consumer. A tiny fixture cfg + a pre-seeded quickcheck cache drives a real embed run.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_embed_requires_cfg_and_root | guard: `embed=True` without `root_folder` (or without `cfg`) fails fast | `engine(cfg=<wt cfg>, embed=True)` (no root) | `ValueError` |
| test_embed_rebases_config_dir_path | **(crux)** embed sets `cfg_base["_config_dir_path"] == root_folder`, NOT the input-file dir or cwd | `engine(cfg=<wt cfg>, embed=True, root_folder=<tmpA>)` | returned `cfg_base["_config_dir_path"] == str(<tmpA>)` |
| test_embed_quickcheck_writes_under_root | the wall-thickness router writes html/json/csv **under** `<tmpA>` and nothing at cwd | embed run from a scratch cwd, `root_folder=<tmpA>`, relative output paths in cfg | quickcheck `report_html`/`result_json`/`result_csv` all under `<tmpA>`; scratch cwd unchanged |
| test_embed_writes_only_under_root | results dir + cfg-dump land under root, nothing outside | embed run, `root_folder=<tmpA>` | `<tmpA>/results/...` exists; no new dirs at cwd or input dir |
| test_embed_no_logfile_no_logs_dir | `log_to_file=False` (default for embed) writes no `.log`, creates no `logs/` | `engine(cfg=..., embed=True, root_folder=<tmpA>, log_to_file=False)` | no `*.log` anywhere; `<tmpA>/logs` absent; stdout logging still emits |
| test_embed_repeated_calls_reentrant | **(re-entrancy)** two sequential embed calls with different roots stay isolated (per-call instance, no `engine.py:57` singleton bleed) | embed `<tmpA>` then embed `<tmpB>` | each writes only under its own root; call-1 state never affects call-2 |
| test_embed_skips_config_dir_recopy | the `:114-118` original-cfg re-copy does NOT run in embed mode (a stale `_config_dir_path` on the input cfg does not survive) | `engine(cfg={... "_config_dir_path": "/stale/dir" ...}, embed=True, root_folder=<tmpA>)` | `cfg_base["_config_dir_path"] == str(<tmpA>)`, not `/stale/dir` |
| test_default_path_unchanged_golden | **(backward-compat)** file/default path with no `embed`/`root_folder` lands outputs in the same locations as before, `_config_dir_path` = input-file dir | `engine(<abs wall_thickness .yml>)` | outputs under the input file's dir; `cfg_base["_config_dir_path"] == dirname(input)` (today's contract) |
| test_engine_signature_additive | the three new params default to embed-off / today's behavior | `inspect.signature(engine)` | params `root_folder=None, log_to_file=False, embed=False` present with defaults; positional callers unaffected |
| test_existing_engine_suite_passes | no regression in the existing engine tests | `tests/test_engine.py` (+ a wall-thickness CLI test) | all pass |

---

## Acceptance Criteria

- [ ] New tests pass: `cd digitalmodel && uv run pytest tests/test_engine_embed_root.py -v` (per repo memory: digitalmodel may need `.venv/bin/python` / `PYTHONPATH=src` if `uv` is broken — runner picks the working invocation).
- [ ] **Embed path isolates writes** — `engine(cfg=..., embed=True, root_folder=<tmpdir>)` writes only under `<tmpdir>` (results + cfg-dump + quickcheck html/json/csv), no `logs/`, no `.log`, nothing at cwd or the input dir. (`test_embed_quickcheck_writes_under_root` + `test_embed_writes_only_under_root` + `test_embed_no_logfile_no_logs_dir`)
- [ ] **`_config_dir_path` rebased to root** and not clobbered by the `:114-118` re-copy. (`test_embed_rebases_config_dir_path` + `test_embed_skips_config_dir_recopy`)
- [ ] **Re-entrant** — repeated in-process embed calls with different roots stay isolated via a per-call `ConfigureApplicationInputs()` instance. (`test_embed_repeated_calls_reentrant`)
- [ ] **Backward compatible (default byte-identical)** — no `embed`, no `root_folder` → output locations + `_config_dir_path`=input-file dir unchanged. (`test_default_path_unchanged_golden` + `test_engine_signature_additive`)
- [ ] **`configure_embed` called positionally without `library_name`** — `(cfg, basename, root_folder, log_to_file=)`.
- [ ] No regression: `tests/test_engine.py` and a wall-thickness CLI test pass.
- [ ] **#3285 hook stated:** #3307 delivers the embed entrypoint; #3285's digitalmodel-bound `run_workflow` calls `engine(cfg=..., embed=True, root_folder=<tempdir>, log_to_file=False)`. #3307 does NOT adopt `ResultEnvelope` or register registry rows.
- [ ] Review artifacts posted to scripts/review/results/ (T3 = 3 providers).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | |
| Codex | PENDING | |
| Gemini | PENDING | |

**Overall result:** PENDING (dispatch T3 wave via `scripts/review/plan-review-fanout.sh` once #3297's contract is owner-approved).

Revisions made based on review:
- (none yet — initial draft)

---

## Risks and Open Questions

- **HARD DEP — #3297 must land first.** `configure_embed` does not exist in the assetutilities checkout today (`ApplicationManager.py:101` still `configure(self, run_dict, library_name, basename, cfg_argv_dict, inputfile=None)`; no `configure_embed`). #3297 is at `status:plan-review`, owner-UNapproved. #3307 implementation cannot start until #3297 (and its `root_folder`/`log_to_file` additions to `configure()`) is merged into the editable `../assetutilities` digitalmodel depends on (`pyproject.toml:372`). The plan is built AS SPECIFIED against the re-locked #3297 contract — if #3297's signature changes during its own review, #3307 re-aligns.
- **Dependency chain (state explicitly):** #3297 (assetutilities embed) → **#3307 (this, digitalmodel embed entrypoint)** → #3285 (digitalmodel adopt-envelope, which builds the digitalmodel `run_workflow` that calls this entrypoint). #3282 (run_workflow/ResultEnvelope) and #3295 (registry v2) are sibling foundations consumed by #3285, not by #3307 directly. **#3307 blocks #3285.**
- **Risk (the `:114-118` re-copy):** digitalmodel's engine uniquely re-copies `_config_dir_path` from the original cfg onto `cfg_base` on the default path — assetutilities' engine has no such block. The embed branch MUST bypass it, else the #3297 rebase is silently undone and every config-relative router escapes the root. `test_embed_skips_config_dir_recopy` is the explicit guard. This is the single most important digitalmodel-specific delta vs #3297.
- **Risk (absolute-path escape — surfaced by Step-1.5):** `wall_thickness_quickcheck._resolve_path` returns absolute output paths verbatim (reproduced: `absolute escapes root: True`). If an embed cfg specifies absolute quickcheck output paths, the rebase cannot contain them. This matches assetutilities' own behavior (no `os.chdir`; relative-only sandboxing) and is acceptable for #3282/#3285's built cfgs (which use relative paths). Documented as an isolation boundary, not a regression. **Generalizable finding** — candidate for promotion to a shared note if other adopters' routers also resolve absolute paths verbatim (per the "promote generalizable review findings" rule).
- **Risk (re-entrancy):** the default path keeps the `engine.py:57` module singleton (byte-identical); only the embed branch uses a per-call instance. `save_cfg` (`engine.py:597`) stays on the singleton but reads cfg only (no instance state), so it is safe in embed mode. Process-global logging reconfiguration (loguru/basicConfig) on each call is a residual shared with #3297 — acceptable for the single-threaded repeated-call use case; flag if #3283's harness runs digitalmodel workflows concurrently.
- **Risk (T3 blast radius):** `engine.py` is digitalmodel's central dispatch for ~80 basenames. Mitigation: all three new params default to today's behavior; the embed branch is unreachable without `embed=True`; the default/`config_flag` path is left byte-identical except the additive `root_folder`/`log_to_file` pass-through to `configure()`. `test_default_path_unchanged_golden` + `test_existing_engine_suite_passes` are the guardrails.
- **Out of scope (documented):** the legacy `asset_integrity/common/ApplicationManager.py` fork is not on the `engine()` path (no live import) — #3307 does not port an embed path into it. If a future asset_integrity workflow needs in-process embedding through *that* fork, file a follow-on.
- **Open decision 1 — file-path `root_folder` threading:** the issue scope names only `engine(embed=True, root_folder=, log_to_file=False)`. The plan additionally threads `root_folder`/`log_to_file` into the default-path `app_manager.configure(...)` to fully mirror #3297. **Recommendation:** include it (cheap, additive, defaults to None→today). Alternative: embed-only (drop the default-path thread) to minimize blast radius. Flag for owner.
- **Open decision 2 — cross-repo id resolution:** N/A for #3307 — this plan provides only the engine entrypoint; resolving `repo:id@version` and creating registry rows belong to #3284/#3285. No id resolver is touched here.
- **Open question — test cache fixture:** `test_embed_quickcheck_writes_under_root` needs a small pre-seeded quickcheck `cache` so `quick_check.run_from_cache(cache_path)` succeeds offline. Plan to reuse an existing fixture under `examples/structural/wall_thickness_quickcheck/data/` or synthesize a minimal cache in the test; the runner picks whichever is hermetic.

---

## Complexity: T3

**T3** — modifies digitalmodel's central `engine()` dispatch (~80 basenames); hard cross-repo dependency on the unlanded #3297 contract; backward compatibility mandatory and proven by a default-path golden; a new in-process embed entry point introduced and consumed downstream by #3285; the digitalmodel-specific `_config_dir_path` re-copy interaction adds correctness risk beyond the assetutilities port; 3-provider adversarial review required. Per the issue's own T3 classification ("digitalmodel is large").
