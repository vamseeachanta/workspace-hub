# Plan for #3282: wf-api(assetutilities) — ResultEnvelope + run_workflow() + registry result descriptor

> ⛔ **BLOCKED on #3297 (2026-06-28).** Wave-1c review proved the per-call temp-dir sandbox is insufficient: the engine is **cwd-coupled** — `configure()` forces `analysis_root_folder=os.getcwd()`, `set_logging()` writes `<cwd>/logs/<name>.log`, and `configure_result_folder()` creates `<cwd>/results/{,Data,Plot}` outside the sandbox; plus a basename mismatch (`data_exploration_FST*.csv` vs registry `input_FST*.csv`) empties `extract_result`. Owner decision: split out the engine-embeddability fix as prereq **#3297** (engine honors an injected root, no cwd side effects), then this envelope sits cleanly on top (no chdir). This plan will be re-scoped onto #3297 (Wave 1d) and the basename-derivation fix folded in. NOT plan-review-ready until #3297 lands.
>
> **Status:** draft (blocked on #3297)
> **Complexity:** T2 (new module + 2 method edits; foundational blast radius — review at T3 depth)
> **Date:** 2026-06-27 (revised 2026-06-28 R3 — Round-2 MAJOR cleared: side-effect-freeness now via a per-call temp-dir SANDBOX of the result folder, file-output `result_hash` over file CONTENTS, csv_utilities removed as a demo target; R2 = Round-1 MAJOR cleared + owner D1/D3/D6 baked in)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3282
> **Epic:** https://github.com/vamseeachanta/workspace-hub/issues/3281
> **Client:** N/A — no wiki content touched
> **Lane:** lane:claude (contract/API design; light edits)
> **Review artifacts:** scripts/review/results/2026-06-27-plan-3282-claude.md | ...-codex.md | ...-gemini.md

---

## Revision note (2026-06-28, Round-2 prep)

This plan was returned **MAJOR** at Round-1. This revision (a) clears every Round-1 finding against the **real** `/mnt/local-analysis/assetutilities` checkout, and (b) bakes in the owner-confirmed cross-cutting decisions (2026-06-28) that settle three former Open Questions. The substantive changes since Round-1:

1. **Result location is a DECLARED registry contract (`result:` descriptor), not an assumption.** The old plan assumed `cfg[basename]` is the result payload. Verified false: `data_exploration.py:115-117` sets `cfg[basename]` to a dict of **file paths** (built at `:113` as `{"data": <filepath>, "label": ...}`, after writing the real CSVs at `:111`), and `csv_utilities_router.py` `router()` simply `return cfg` — there is **no** `cfg["csv_utilities"]` result key at all. Per owner decision **D1**, #3282 **OWNS** the `result:` descriptor shape `{kind: in_memory|files, key: <cfg key> (in_memory) | outputs: [...] (files)}`. (Round-1 Finding 4, escalated to a design blocker — RESOLVED.)
2. **`persist=False` guards ONLY the file write, never `standardize_yml_data`** (Round-1 Finding 2). Verified at `ApplicationManager.py:370-378`: line 375 `cfg_base = self.standardize_yml_data(cfg_base)` runs **before** line 377 `save_data.saveDataYaml(...)` inside the same method. Suppressing the whole call would skip numpy→list / `Path`→str / np-scalar normalization (`standardize_yml_data`, lines 380-401), so the in-memory `result_hash` would be computed over different bytes than the persisted file. Standardization now always runs; only `saveDataYaml` is gated.
3. **Schema: adopt the unified v2 SUPERSET, no v3** (Round-1 Finding 3 + owner decision **D1**). The Round-1 fear was a collision between assetutilities `schema_version: 1` and digitalmodel `schema_version: 2`. That fear is now SETTLED: v2 is **defined as an additive superset** (deckhand routing triple `version`/`status`/`latest` **+** `invocation` **+** reserved `request_schema`/`response_schema` **+** `result`). #3282 adopts v2 on the assetutilities registry, adding the **required top-level `invocation:` key** (`"uv run python -m assetutilities {input}"`, `{input}`-only substitution — `capability_smoke.py` is the reference resolver) and the per-row `result:` descriptor it owns. #3295 owns the formal cross-registry reconciliation and **reserves** the structured (NOT typed-string) `request_schema`/`response_schema` slots pending #3282. **No v3 bump.**
4. **Determinism FIELDS are computed, not hardcoded** (owner decision **D3**). The Round-1 pseudocode hardcoded `"reproducible": True` — fixed. `#3282` OWNS `input_hash`, `result_hash`, a **computed** `reproducible`, and `provenance.code_version = {package_version, git_sha}`. File-output `result_hash` hashes **sorted basenames** (location-independent), never absolute paths. *(SUPERSEDED by R3 — Round-2 found basename-only hashing content-blind; `result_hash` now hashes `basename → sha256(file contents)`. See the Round-3 prep note.)* The golden harness + the volatile-field **key-allowlist** spec is #3283's, which is **DEFERRED to Wave 2** (D6) — so #3282 computes `reproducible` itself via an opt-in double-run, defaulting to `None` ("not checked") rather than a fabricated `True`.
5. **Error enveloping is fail-closed from the first line** (Round-1 Finding 5). Registry resolution and cfg build move INSIDE the guarded region so an unknown id returns a `status=="error"` envelope, not a raw traceback. `input_hash` volatile-key exclusion is explicitly specified (Round-1 Finding 6).
6. **Import is SLOW, not a hang** (Round-1 reproduction honesty correction). The Round-1 note claimed the re-run "timed out at import." A 2026-06-28 bounded live run (`timeout 90 .venv/bin/python -c "from assetutilities.engine import engine"`) **succeeded in ~29.4 s** — heavy transitive imports (`WebScraping`/`TextAnalytics`/`DownloadDataFromURL`), not a deadlock. AC#1's empirical demonstration is therefore achievable; the prior "blocked" was a too-short timeout. Recorded below as a *slow cold-import* risk, not a blocker.

---

## Revision note (2026-06-28, Round-3 prep — Round-2 MAJOR cleared)

Round-2 returned **MAJOR** with three findings, each re-verified against the live `/mnt/local-analysis/assetutilities` checkout and now structurally fixed (not just re-worded):

1. **`persist=False` is NOT side-effect-free — routers write files themselves.** Verified: `data_exploration.py:83`, `:93`, and `:111` call `df.to_csv(...)` / `df_statistics.to_csv(...)` into `cfg["Analysis"]["result_folder"]` **inside the router**, before `engine.py:120 save_cfg`. `persist=False` would gate **only** `ApplicationManager.py:377 saveDataYaml` (the cfg-dump), so `engine(cfg=..., persist=False)` still litters the example/result dir on every call. **Fix (owner-locked):** `run_workflow` makes the call genuinely side-effect-free by **sandboxing the result folder per call** — `tempfile.mkdtemp()`, then point `cfg.Analysis.result_folder` + `analysis_root_folder` (and, robustly, `cfg.file_management.output_directory`) at the temp dir **before** `engine(cfg=..., config_flag=True, persist=False)`, so **all** router writes land in the throwaway dir; `shutil.rmtree` after extraction. `persist=False` still gates only the `save_cfg` cfg-dump; the **sandbox** is what neutralizes router writes. (Verified at `ApplicationManager.py:299`: an *absolute* `file_management.output_directory` is returned verbatim as `result_folder` by `configure_result_folder`, surviving `configure()`'s reset of `analysis_root_folder` to `os.getcwd()` on the in-memory `inputfile=None` path — this is why the abs-`output_directory` override is the robust sandbox hook.)
2. **csv_utilities is NOT a registry row and writes nothing.** Verified: the registry has **9 rows** (visualization, data_exploration, excel_utilities, zip_utilities, yaml_utilities, file_management, file_edit, word_utilities, reportgen) — **no `csv_utilities`** — and `csv_utilities_router.py` `router()` just `return cfg`. So `run_workflow("csv_utilities")` would error at registry resolution and any "csv_utilities files demo" AC is unsatisfiable. **Fix:** csv_utilities is **removed as a demo target** everywhere; the `kind=="files"` branch is demonstrated on **data_exploration** (a real registry row that writes 2 CSVs). `csv_utilities_router.py` remains cited only as **evidence** that `cfg[basename]` is an unreliable result locator (the design-hole proof), never as a runnable target.
3. **basename-only file hash is content-blind → vacuous determinism.** Verified: the R2 `result_hash` hashed `sorted(os.path.basename(p) ...)` only; data_exploration always emits the same 2 basenames, so `reproducible` was tautologically `True` regardless of content drift. **Fix (owner-locked):** `kind=="files"` `result_hash` now **reads each output file in the sandbox and hashes `basename → sha256(content)` (sorted by basename)** — both location-independent (basename-keyed) **and** content-sensitive (a changed output value flips the hash). `in_memory` is documented as **supported-but-currently-unexercised** (all 9 registry rows are file-writing; `cfg[basename]` holds paths/echoes, not data), so the plan claims **no** in_memory demo that no registry row satisfies.

---

## Resource Intelligence Summary

### Existing repo code (verified 2026-06-28 against `/mnt/local-analysis/assetutilities`)

- **Found** `src/assetutilities/engine.py:27` — `def engine(inputfile: str = None, cfg: dict = None, config_flag: bool = True) -> dict`. When `cfg` is supplied, `engine.py:29 if cfg is None` is skipped, so `cfg_argv_dict` stays `{}` and `inputfile` stays `None`. With `config_flag=True` (default) the in-memory branch runs `app_manager.configure(cfg, library_name, basename, {}, None)` (`:45`), `fm.router` (`:46`), `configure_result_folder(None, cfg_base)` (`:47-49`), dispatches on `basename` (`:55-114`), and returns `cfg_base` (`:121`). This is the exact path `run_workflow` uses.
- **Found** `engine.py:116-117` — `save_application_cfg(cfg_base)` runs **only** when `cfg is None` (the file-path branch), so it is irrelevant to the in-memory API path.
- **Found** `engine.py:120` — `cfg_base = app_manager.save_cfg(cfg_base=cfg_base)` runs **unconditionally** on every call. This is **one** of two file-write side effects; `persist=False` gates only this one. The **other** is the per-router output write (next item), which `persist=False` cannot touch — both must be neutralized for a truly side-effect-free call.
- **Found** `src/assetutilities/common/ApplicationManager.py:284-335` — `configure_result_folder(analysis_root_folder, cfg_with_fm)`: when `file_management.output_directory` is **absolute** (`:299 os.path.isabs`), it is returned **verbatim** as `result_folder` (`:300`); otherwise `result_folder = <analysis_root_folder>/results` (`:304`). Since `engine.py:45 configure()` resets `analysis_root_folder` to `os.getcwd()` on the in-memory (`inputfile=None`) path, the robust per-call sandbox hook is setting `cfg.file_management.output_directory` to an **absolute temp dir** — it survives `configure()` and forces every router write into the sandbox.
- **Found** `src/assetutilities/common/ApplicationManager.py:370-378` — `save_cfg(self, cfg_base)` does, in order: compute `output_dir`/`filename_path` (`:371-374`); **`:375 cfg_base = self.standardize_yml_data(cfg_base)`** (load-bearing normalization); **`:377 save_data.saveDataYaml(cfg_base, filename_path, default_flow_style=False)`** (the write); `:378 return`. **Confirmed**: standardization precedes the write inside the same method — guarding the whole call kills both. The persist guard must wrap **only `:377`** (and the `:371-374` path computation, which is only needed for the write).
- **Found** `ApplicationManager.py:380-401` — `standardize_yml_data` recursively converts `dict`/`list` children, `Path`→`str` (`:391-392`), `np.ndarray`→`list` (`:393-394`), np-int→`int` (`:395-397`), np-float→`float` (`:398-400`). Exactly the normalization the determinism hash needs; must always run.
- **Found** `src/assetutilities/modules/data_exploration/data_exploration.py:83/93/106-117` — writes the real CSVs at `:83`, `:93` (summary tables) and `:111` (`df_statistics.to_csv`) to `cfg["Analysis"]["result_folder"]` **inside the router, before `engine.py:120 save_cfg`**, then sets `cfg[cfg["basename"]] = {"df_basic_statistics": {"groups": [...]}}` where each element (`:113`) is `{"data": <filepath>, "label": <label>}`. So even when `cfg[basename]` IS a dict, it holds **file paths, not data**. The registry already lists those CSVs under `outputs:`. **Consequence (Round-2 Finding 1):** `persist=False` does NOT suppress these router writes — only the per-call result-folder **sandbox** does. With the example input (`file_name="input"`, labels `FST1`/`FST2`) the basenames are `input_FST1.csv`/`input_FST2.csv`, matching the registry `outputs:` and the sandbox-relative resolution.
- **Found** `src/assetutilities/modules/csv_utilities/csv_utilities_router.py` — `router(self, cfg)` does a no-op encoding check and `return cfg`. There is **no** `cfg["csv_utilities"]` result key. **Confirmed**: `cfg[basename]` is a per-workflow-inconsistent, unreliable result locator — the core design hole.
- **Found** `docs/registry/workflows.yaml` — `schema_version: 1`, `repo: assetutilities`, `issue: 3063`, **9 rows** (visualization, data_exploration, excel_utilities, zip_utilities, yaml_utilities, file_management, file_edit, word_utilities, reportgen). Each row carries `id`, `basename`, `input`, `outputs:` (list of produced files), `test`, `runtime`. **There is NO top-level `invocation:` key** (verified by `grep`). The `outputs:` list is the existing authoritative declaration of where file results land.
- **Found** `digitalmodel/docs/registry/workflows.yaml` — `schema_version: 2`, top-level `invocation: "uv run python -m digitalmodel {input}"`, plus the deckhand versioned-routing triple (`version`/`status`/`latest`, all optional). This is the v2 superset assetutilities aligns to.
- **Found** `deckhand/src/deckhand/capability_smoke.py:231` — `template = str(registry.get("invocation") or "uv run python -m {pkg} {input}")` then `:232 rendered = template.replace("{input}", input_rel)`. **Confirms D1**: `capability_smoke.py` is the reference resolver; it reads the top-level `invocation:` key and performs **`{input}`-only** substitution (falling back to a `{pkg}` default only when the key is absent). The schema doc must name it.
- **Verified (live, 2026-06-28)** — `timeout 90 .venv/bin/python -c "from assetutilities.engine import engine"` → **`IMPORT OK 29.4 s`**. The import is slow but does **not** hang. No existing test references `save_cfg` / `persist` / `standardize_yml_data` (`grep` over `tests/` clean) — the two method edits have **no contradicting test**.
- **Gap** — no `workflow_api/` package anywhere under `src/assetutilities` (the `ResultEnvelope` + `run_workflow()` surface is greenfield — confirmed `ls` returns nothing).
- **Gap** — `engine()` returns the whole mutated `cfg`; no typed result payload, no provenance, no determinism hash, no declared result location.

### Standards
Not applicable — harness/contract code, not an engineering calculation. The provenance `standard_revisions` field reuses the *shape* of the Citation sidecar in `.claude/rules/calc-citation-contract.md`; it introduces no standards-derived constants, so no `Citation` emission is required here.

### LLM Wiki pages consulted
None — contract/infra work, no domain knowledge. (`Client: N/A`.)

### Documents consulted
- Epic [#3281](https://github.com/vamseeachanta/workspace-hub/issues/3281) — defines the `ResultEnvelope` field set and the in-process-only scope (HTTP deferred to a later child).
- [#3295](https://github.com/vamseeachanta/workspace-hub/issues/3295) (OPEN) — reconcile registry `schema_version` into a unified **v2 superset**; per **D1** it owns the cross-registry reconciliation and **reserves** the structured `request_schema`/`response_schema` slots pending #3282. #3282 contributes the `result:` descriptor shape into that superset.
- [#3283](https://github.com/vamseeachanta/workspace-hub/issues/3283) — golden-determinism harness + volatile-field **key-allowlist** spec. Per **D6** this is **DEFERRED to Wave 2** and is NOT a dependency of #3282; #3282 computes `reproducible` itself (opt-in double-run).
- [#3050](https://github.com/vamseeachanta/workspace-hub/issues/3050) / [#3067](https://github.com/vamseeachanta/workspace-hub/issues/3067) — upstream CLI/registry contract epic; the API-contract doc is a companion deliverable, not this issue.
- digitalmodel `results.json {meta, lookup, index, curves}` (buckling/FFS) — precedent for a structured result payload.

### Gaps identified
- No shared `ResultEnvelope` type (greenfield).
- No `run_workflow(id, params)` entrypoint (greenfield).
- Two write sites block a side-effect-free in-process call: (a) `save_cfg`'s cfg-dump (gated by `persist=False`) and (b) the per-router output writes (`data_exploration.py:83/93/111`, etc.) which `persist=False` cannot touch and which a per-call temp-dir **sandbox** of the result folder neutralizes.
- The registry lacks a top-level `invocation:` key and a uniform per-row `result:` descriptor — both added by this plan.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`): `#3282` OPEN (this issue); `#3295` OPEN (schema reconciliation / unblocks #3282); `#3283` OPEN (deferred Wave 2); `#3281` OPEN (parent epic).

**Line excerpts** (`engine.py`):
```
27:  def engine(inputfile: str = None, cfg: dict = None, config_flag: bool = True) -> dict:
116:    if cfg is None:
117:        save_application_cfg(cfg_base=cfg_base)
120:    cfg_base = app_manager.save_cfg(cfg_base=cfg_base)   # <-- UNCONDITIONAL file write
121:    return cfg_base
```

**Line excerpts** (`ApplicationManager.save_cfg`, the Round-1 Finding 2 site):
```
370:  def save_cfg(self, cfg_base):
371:      output_dir = cfg_base.Analysis["analysis_root_folder"]
373:      filename = cfg_base.Analysis["file_name"]
374:      filename_path = os.path.join(output_dir, "results", filename)
375:      cfg_base = self.standardize_yml_data(cfg_base)   # <-- normalization (MUST always run)
377:      save_data.saveDataYaml(cfg_base, filename_path, default_flow_style=False)  # <-- guard THIS only
378:      return cfg_base
```

**Line excerpts** (design-hole sites + resolver):
```
data_exploration.py:111:   df_statistics.to_csv(filename, index=False)              # real result -> file
data_exploration.py:113:   basic_statistic_array.append({"data": filename, ...})    # paths, not data
data_exploration.py:115:   cfg[cfg["basename"]] = {...}                             # holds paths
csv_utilities_router.py:    return cfg                                              # NO result key at all
capability_smoke.py:231:    template = str(registry.get("invocation") or "...{pkg} {input}")
capability_smoke.py:232:    rendered = template.replace("{input}", input_rel)        # {input}-ONLY substitution
```

(Distinct sources: issue body + #3295 body + engine.py + ApplicationManager.py + data_exploration.py + csv_utilities_router.py + both registry files + capability_smoke.py + live import run = 9+.)

---

## Step 1.5 — Reproduction

**Claim under test:** `engine(cfg=<dict>, config_flag=True)` (the exact path `run_workflow` uses) runs end-to-end and returns a populated dict **without an input file**, AND `cfg[basename]` is *not* a usable result payload.

**Prior in-session reproduction (captured Round-1):**
```
$ uv run python repro_cfg.py   # engine(cfg=<dict from data_exploration input.yml>, config_flag=True)
... data_exploration, application ... END
RESULT TYPE: dict
result[data_exploration] type: <holds file-path dict, not data>
IN-MEMORY cfg PATH: WORKS
```
Established: (a) the in-memory `cfg` path **works** (returns a dict, runs the router) — no engine-rebuild scope expansion; (b) `cfg[basename]` is the wrong result locator.

**2026-06-28 import characterization (honest correction to Round-1):** Round-1 claimed the re-run "timed out at import." A bounded re-run — `timeout 90 .venv/bin/python -c "from assetutilities.engine import engine"` — **succeeded in ~29.4 s** (`IMPORT OK 29.4 s`). The earlier "timeout" was a too-short bound, not a deadlock. The import is **slow** (heavy transitive `WebScraping`/`TextAnalytics`/`DownloadDataFromURL` loads at module top) but not broken. This is recorded as a *slow cold-import* risk only; it does **not** block AC#1's empirical demonstration under the repo pytest harness.

**Static corroboration:** the dispatch trace `engine.py:43→45→46→47→55..114` with `cfg supplied / config_flag=True` is unambiguous; `data_exploration.py:111/113/115` and `csv_utilities_router.py` directly show the result-location inconsistency. The design conclusion holds independent of runtime.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md |
| Envelope impl | `assetutilities/src/assetutilities/workflow_api/envelope.py` |
| Result-locator + runner impl | `assetutilities/src/assetutilities/workflow_api/runner.py` |
| Package init | `assetutilities/src/assetutilities/workflow_api/__init__.py` |
| Engine edit | `assetutilities/src/assetutilities/engine.py` |
| save_cfg edit | `assetutilities/src/assetutilities/common/ApplicationManager.py` |
| Registry (v2 superset: `invocation` + per-row `result`) | `assetutilities/docs/registry/workflows.yaml` |
| Schema doc (names `result:` shape + `invocation` + capability_smoke.py resolver) | `assetutilities/docs/registry/SCHEMA.md` |
| Tests | `assetutilities/tests/workflow_api/test_envelope.py`, `test_runner.py` |
| Plan reviews | scripts/review/results/2026-06-27-plan-3282-{claude,codex,gemini}.md |

---

## Deliverable

A `workflow_api` package in `assetutilities/src/` exposing `run_workflow(workflow_id, params=None, cfg=None, verify_reproducible=False) -> ResultEnvelope` — a typed, **genuinely side-effect-free** in-process call over the existing `engine()`. Side-effect-freeness is achieved by **sandboxing the result folder per call**: the runner creates a `tempfile.mkdtemp()` dir, points the cfg's result/analysis folders (and the abs `file_management.output_directory`) at it before `engine(cfg=..., config_flag=True, persist=False)` so **all router file-writes** land in the throwaway dir, then `shutil.rmtree`s it after extraction (`persist=False` separately gates only the `save_cfg` cfg-dump). The result location is **declared per-workflow** (registry `result:` descriptor, `kind: in_memory | files`) rather than assumed. Plus the `ResultEnvelope` type with **computed** determinism fields (`input_hash`, `result_hash` over **file contents** for `kind:files`, `reproducible`, `provenance.code_version = {package_version, git_sha}`), a `persist=False` path that preserves `standardize_yml_data`, the registry's required top-level `invocation:` key, the per-row `result:` descriptor (#3282-owned), and a registry `SCHEMA.md` naming `capability_smoke.py` as the reference invocation resolver — all TDD-covered.

---

## Pseudocode

```python
# ── envelope.py ────────────────────────────────────────────────
@dataclass
class ResultEnvelope:
    workflow_id: str
    status: str                  # "ok" | "error"
    result: dict                 # the DECLARED result payload (see ResultLocator), never the whole cfg
    provenance: dict             # {code_version: {package_version, git_sha}, standard_revisions: [],
                                 #  data_as_of, input_hash}
    determinism: dict            # {result_hash, reproducible: bool | None}   # None == "not checked"
    confidence: dict | None      # optional screening-vs-certified band
    warnings: list[str]
    def to_dict() / from_dict()  # lossless round-trip; canonical sorted-key order

# Provenance shape SETTLED by owner decision D3 (was a Round-1 Open Question):
def code_version() -> dict:
    pkg = importlib.metadata.version("assetutilities")        # package_version
    sha = _git_sha_or_none()                                  # git rev-parse HEAD, best-effort
    return {"package_version": pkg, "git_sha": sha}           # both keys always present

# Hashing spec (#3282 OWNS these fields; #3283 golden harness is Wave-2 deferred):
VOLATILE_TOP_KEYS = {"Analysis", "default", "cfg_array"}      # abs paths / resolved folders / timestamps
def canonical_input(cfg) -> str:
    pruned = {k: v for k, v in cfg.items() if k not in VOLATILE_TOP_KEYS}
    return json.dumps(pruned, sort_keys=True, default=str)    # str-coerce stray Path/np objects
def input_hash(cfg)  -> sha256(canonical_input(cfg))

def result_hash(payload) -> str:
    # payload is ALREADY standardize_yml_data-normalized (numpy->list, Path->str) -> bytes match persist=True.
    # R2-FIX: for kind=="files", hash basename -> sha256(FILE CONTENTS), sorted by basename.
    #   Location-independent (basename-keyed, drops sandbox abs path) AND content-sensitive
    #   (a changed output value flips the hash) -> real determinism, not the old basename-only tautology.
    #   extract_result has already read each file in the sandbox into payload["outputs"][i]["sha256"].
    if payload.get("kind") == "files":
        canon = {"kind": "files",
                 "files": sorted((f["basename"], f["sha256"]) for f in payload.get("outputs", []))}
    else:
        canon = payload                                       # in_memory: hash the standardized value
    return sha256(json.dumps(canon, sort_keys=True, default=str))

# reproducible is COMPUTED, never hardcoded (D3). Default None == "not checked".
# Content-sensitive now: each run uses its OWN sandbox; result_hash compares file CONTENTS by basename,
# so a deterministic workflow -> equal hashes -> True, while drifted output bytes -> False.
def compute_reproducible(rerun_fn, first_hash, verify: bool):
    if not verify:
        return None                                           # honest: not a fabricated True
    _, _, second_hash = rerun_fn()                            # second invocation in a FRESH sandbox
    return second_hash == first_hash                          # True / False, measured over contents

# ── ResultLocator: the design-hole fix (shape OWNED by #3282 per D1) ──
#   result:
#     kind: files            # "files" (default) | "in_memory"
#     key: data_exploration  # for in_memory: cfg[key] is the payload
#     outputs: [...]         # for files: defaults to the row's existing `outputs:` list
#   NOTE: kind=="in_memory" is SUPPORTED but currently UNEXERCISED — all 9 registry rows are
#   file-writing (cfg[basename] holds paths/echoes input, not data), so #3282 demos kind=="files"
#   on data_exploration and only documents the in_memory shape. No in_memory demo is claimed.
def extract_result(cfg_base, locator, sandbox) -> (payload: dict, warnings: list):
    if locator.kind == "in_memory":
        if locator.key not in cfg_base:
            return {"kind": "in_memory", "value": None}, \
                   [f"declared in_memory result_key '{locator.key}' absent from cfg"]  # NOT silent {}
        return {"kind": "in_memory", "value": cfg_base[locator.key]}, []
    else:  # kind == "files" — read CONTENTS from the per-call sandbox, by basename
        wanted = sorted(os.path.basename(p) for p in (locator.outputs or []))
        files, warns = [], []
        for name in wanted:
            path = os.path.join(sandbox, name)                # router wrote here (abs output_directory)
            if os.path.exists(path):
                with open(path, "rb") as fh:
                    files.append({"basename": name,
                                  "sha256": sha256(fh.read()).hexdigest(),
                                  "size": os.path.getsize(path)})
            else:
                warns.append(f"declared output missing in sandbox: {name}")
        # payload carries basenames + per-file content digest (NOT dead sandbox paths -> dir is rmtree'd)
        return {"kind": "files", "outputs": files}, warns

# ── runner.py ─────────────────────────────────────────────────
# Per-call SANDBOX: every engine() invocation runs with its result folder pointed at a throwaway
# temp dir, so NO router write ever touches the repo/example dirs. persist=False ALSO gates the
# save_cfg cfg-dump; the two together make the call genuinely side-effect-free.
def _run_once(cfg, locator) -> (payload, warns, rhash):
    sandbox = tempfile.mkdtemp(prefix="auwf_")
    try:
        c = copy.deepcopy(cfg)
        c.setdefault("Analysis", {})["analysis_root_folder"] = sandbox
        c["Analysis"]["result_folder"]                       = sandbox
        # ABS output_directory survives configure()/configure_result_folder (ApplicationManager.py:299)
        c.setdefault("file_management", {})["output_directory"] = sandbox
        cb = engine(cfg=c, config_flag=True, persist=False)  # routers write INTO sandbox; no cfg-dump
        payload, warns = extract_result(cb, locator, sandbox)  # read CONTENTS before teardown
        rhash = result_hash(payload)
        return payload, warns, rhash
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)           # throwaway -> repo/example dirs untouched

def run_workflow(workflow_id=None, params=None, cfg=None, verify_reproducible=False) -> ResultEnvelope:
    wid = workflow_id or "(inline-cfg)"
    try:                                                  # fail-closed from the FIRST line (Finding 5)
        if cfg is None:
            row     = resolve_registry_row(workflow_id)   # unknown id -> raises -> caught below
            cfg     = build_cfg(row, params)
            locator = ResultLocator.from_row(row)
        else:
            row     = lookup_row_for_cfg(cfg)             # may be None
            locator = ResultLocator.from_row(row) if row else ResultLocator.default_for(cfg)
        ihash          = input_hash(cfg)
        payload, warns, rhash = _run_once(cfg, locator)   # sandboxed; side-effect-free
        repro          = compute_reproducible(lambda: _run_once(cfg, locator), rhash,
                                              verify_reproducible)   # None unless asked; FRESH sandbox
        return ResultEnvelope(wid, "ok", payload,
                              provenance(ihash), {"result_hash": rhash, "reproducible": repro},
                              None, warns)
    except Exception as e:
        return ResultEnvelope(wid, "error", {}, provenance(None),
                              {"result_hash": None, "reproducible": None}, None, [str(e)])

# ── engine.py edit (minimal, backward-compatible) ─────────────
def engine(inputfile=None, cfg=None, config_flag=True, persist=True) -> dict:
    ...                                                   # unchanged dispatch
    cfg_base = app_manager.save_cfg(cfg_base=cfg_base, persist=persist)   # thread persist through
    return cfg_base

# ── ApplicationManager.save_cfg edit (Finding 2 fix) ──────────
def save_cfg(self, cfg_base, persist=True):
    cfg_base = self.standardize_yml_data(cfg_base)        # ALWAYS — normalization is load-bearing
    if persist:                                           # guard ONLY the write + its path computation
        output_dir    = cfg_base.Analysis["analysis_root_folder"]
        filename_path = os.path.join(output_dir, "results", cfg_base.Analysis["file_name"])
        save_data.saveDataYaml(cfg_base, filename_path, default_flow_style=False)
    return cfg_base
```

---

## Registry change (v2 superset — D1)

```yaml
# docs/registry/workflows.yaml
schema_version: 2                                  # adopt unified superset (was 1); matches digitalmodel
invocation: "uv run python -m assetutilities {input}"   # REQUIRED top-level key; {input}-only substitution
repo: assetutilities
issue: 3063
workflows:
  - id: data_exploration
    basename: data_exploration
    input: examples/workflows/data_exploration/input.yml
    outputs:
      - examples/workflows/data_exploration/results/input_FST1.csv
      - examples/workflows/data_exploration/results/input_FST2.csv
    result:                                        # #3282-OWNED descriptor; optional per row
      kind: files                                  # defaults to the row's `outputs:` when omitted
    test: uv run python -m assetutilities examples/workflows/data_exploration/input.yml
    runtime: fast
  # ... remaining 8 rows unchanged; `result:` is optional (kind: files default) ...
```

- `request_schema:` / `response_schema:` are **structured (not typed-string) descriptors RESERVED by #3295**; #3282 does NOT populate them and does NOT impose a `str` invariant.
- `docs/registry/SCHEMA.md` (new) documents: the `result:` descriptor shape (`kind: files` default vs `kind: in_memory`), the required `invocation:` key with `{input}`-only substitution, and names `deckhand/src/deckhand/capability_smoke.py` as the reference resolver. **No v3.** It also records that `kind: in_memory` is **supported but currently unexercised** — all 9 rows are file-writing (`cfg[basename]` holds paths/echoes, not data), so no row sets `kind: in_memory` yet.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `assetutilities/src/assetutilities/workflow_api/__init__.py` | export `run_workflow`, `ResultEnvelope` |
| Create | `assetutilities/src/assetutilities/workflow_api/envelope.py` | `ResultEnvelope` dataclass + `input_hash`/`result_hash` (file-CONTENTS hash for `kind:files`)/`code_version`/`compute_reproducible` + volatile-key spec |
| Create | `assetutilities/src/assetutilities/workflow_api/runner.py` | `run_workflow`, registry resolution, `ResultLocator`, per-call temp-dir **sandbox** (`_run_once`: mkdtemp → engine → rmtree), `extract_result` (in_memory + files-from-sandbox branches) |
| Modify | `assetutilities/src/assetutilities/engine.py` | add `persist: bool = True` param; thread into `save_cfg` (no dispatch change) |
| Modify | `assetutilities/src/assetutilities/common/ApplicationManager.py` | `save_cfg(cfg_base, persist=True)` — standardize ALWAYS, gate only `saveDataYaml` + its path computation |
| Modify | `assetutilities/docs/registry/workflows.yaml` | `schema_version: 2`; add top-level `invocation:`; add optional per-row `result:` descriptor |
| Create | `assetutilities/docs/registry/SCHEMA.md` | document `result:` shape, `invocation:` substitution, name `capability_smoke.py` resolver |
| Create | `assetutilities/tests/workflow_api/test_envelope.py` | envelope + hashing + reproducible TDD |
| Create | `assetutilities/tests/workflow_api/test_runner.py` | runner + locator + registry TDD |
| Update | docs/plans/README.md | index row (workspace-hub) |

---

## TDD Test List

| Test name | What it verifies | Input | Output |
|---|---|---|---|
| test_envelope_roundtrip | `to_dict`/`from_dict` lossless | populated envelope | equal envelope |
| test_input_hash_excludes_volatile_keys | two cfgs differing only in `Analysis`/`default`/`cfg_array` → same `input_hash` | two cfgs | identical hash |
| test_input_hash_changes_on_real_input | changing a real (non-volatile) input key changes the hash | two cfgs | different hash |
| test_result_hash_over_standardized_payload | `result_hash` is stable and computed over normalized payload (numpy→list applied) | payload w/ numpy types | hash equal to post-standardize hash |
| test_result_hash_files_content_sensitive | **R2-FIX**: same basenames + same bytes → identical `result_hash`; **one output's bytes changed → DIFFERENT `result_hash`** (content-sensitive, not the old basename-only tautology) | two file payloads (equal vs one byte-differing) | equal-then-different hash |
| test_result_hash_files_location_independent | **R2-FIX**: same basenames + same contents under different sandbox dirs (and reordered) → identical `result_hash` (basename-keyed, path-dropped) | two file payloads | same hash both ways |
| test_provenance_code_version_shape | **D3**: `provenance.code_version` has both `package_version` and `git_sha` keys (git_sha may be `None`) | envelope | both keys present |
| test_reproducible_not_hardcoded_default_none | **D3**: `verify_reproducible=False` → `determinism.reproducible is None` (NOT `True`) | run w/o verify | `reproducible is None` |
| test_reproducible_computed_true_on_double_run | `verify_reproducible=True` on a deterministic workflow → `reproducible is True` via measured second run | data_exploration | `reproducible is True` |
| test_save_cfg_persist_false_no_write_but_standardizes | `save_cfg(cfg, persist=False)` writes no file AND still returns a standardized dict (Path/np converted) | cfg w/ Path + np values | no file; values normalized |
| test_save_cfg_persist_true_backward_compat | default `persist=True` writes the same results file as before | a basename | file created (unchanged) |
| test_engine_persist_param_threads_through | `engine(cfg=..., persist=False)` skips the `save_cfg` cfg-dump while `persist=True` writes it (`save_cfg` write-site gating only) | data_exploration cfg | dump vs no-dump |
| test_run_workflow_sandboxes_router_writes | **R2-FIX (Finding 1)**: `run_workflow("data_exploration", ...)` writes **NOTHING** outside the temp sandbox — the repo `examples/workflows/data_exploration/results/` dir is byte-for-byte unchanged (snapshot before/after), and the sandbox is rmtree'd | run + dir snapshot | no file written outside temp dir; sandbox gone |
| test_locator_files_reads_contents_from_sandbox | **R2-FIX**: `extract_result(..., sandbox)` for data_exploration returns `{kind: files, outputs: [{basename, sha256, size}, ...]}` read from the sandbox (NOT abs repo paths) | data_exploration cfg_base + sandbox | per-file content digests |
| test_locator_in_memory_missing_key_warns_not_silent | declared `in_memory` key absent → warning appended, NOT silent `{}` | cfg_base missing key | warnings non-empty |
| test_locator_files_missing_output_warns | a declared output file absent → warning, status still ok | cfg_base w/ no file | warning present |
| test_run_workflow_by_id_returns_envelope | resolves a registry id → ok envelope w/ declared result | `run_workflow("data_exploration", params=...)` | `status=="ok"`, populated `result` |
| test_run_workflow_unknown_id_error_envelope | unknown id is enveloped, NOT raised (fail-closed) | `run_workflow("nope")` | `status=="error"`, warning carries message |
| test_run_workflow_engine_error_envelope | a router exception → error envelope, not a raw traceback | cfg that makes a router raise | `status=="error"`, warning carries message |
| test_registry_schema_v2_invocation_and_optional_result | registry parses at `schema_version: 2`; top-level `invocation == "uv run python -m assetutilities {input}"`; all 9 rows valid with `result:` optional | current registry | version 2, invocation present, rows valid |

---

## Acceptance Criteria

- [ ] `from assetutilities.workflow_api import run_workflow, ResultEnvelope` works; `run_workflow` returns a populated `ResultEnvelope` for ≥1 existing workflow (`data_exploration`), demonstrated **empirically by a passing test under the repo pytest harness** (import is slow ~30 s but loads green — Step 1.5).
- [ ] `ResultEnvelope.result` carries the **declared** result (`kind:files` branch demonstrated on **`data_exploration`**, a real registry row — **csv_utilities is NOT a target**: it is not a registry row and writes nothing), never the whole `cfg`, and never silently returns `{}`/`None` on a missing declared key (warning emitted).
- [ ] **`run_workflow` is genuinely side-effect-free (R2-FIX, Finding 1):** a call writes **nothing** outside its per-call `tempfile.mkdtemp()` sandbox — the repo `examples/.../results/` dir is unchanged before/after — and the sandbox is `shutil.rmtree`'d. Router writes are neutralized by the **sandbox**, not by `persist=False`.
- [ ] `save_cfg(cfg, persist=False)` writes no cfg-dump file but **still standardizes** (numpy→list, Path→str); `persist=True` default is byte-for-byte the prior behavior (existing suite green).
- [ ] `engine(..., persist=False)` skips the `save_cfg` cfg-dump; default `persist=True` unchanged. (Full side-effect-freeness of `run_workflow` comes from the runner sandbox, above — `persist` alone does not stop router writes.)
- [ ] Determinism fields are **computed, not hardcoded** (D3): `input_hash`, `result_hash` present; `reproducible` is `None` when unchecked and a measured `True`/`False` under `verify_reproducible=True`; `provenance.code_version == {package_version, git_sha}`. File-output `result_hash` is over **file CONTENTS** (basename → sha256(content), sorted) — **content-sensitive** (a changed output value flips the hash) AND location-independent.
- [ ] `kind:in_memory` is documented as **supported-but-currently-unexercised** (all 9 registry rows are file-writing); the plan claims **no** in_memory demo.
- [ ] Registry adopts the **v2 superset** (D1): `schema_version: 2`, required top-level `invocation: "uv run python -m assetutilities {input}"`, optional per-row `result:` descriptor; all 9 existing rows still validate; `request_schema`/`response_schema` left RESERVED for #3295. `SCHEMA.md` names `capability_smoke.py` as the reference resolver. **No v3.**
- [ ] `uv run pytest assetutilities/tests/workflow_api/ -v` green; full `assetutilities` suite shows no regression.
- [ ] Review artifacts posted under scripts/review/results/.

---

## Adversarial Review Summary

<!-- Round 3 PENDING — re-review after this revision. Round-2 returned MAJOR (now addressed). Not approval-ready until populated with no-MAJOR verdicts. Status stays draft. -->

### Round 1 (2026-06-27) — verdict: **MAJOR** (Claude inline; 3 MAJOR + 1 design-blocker + 3 MINOR = 7 distinct findings)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MAJOR** | M1 Step 1.5 tested the *file* path, not the in-memory `cfg` path; M2 `persist=False` guarding the whole `save_cfg` also suppresses `standardize_yml_data` → in-memory `result_hash` ≠ persisted bytes; M3 `schema_version: 2` collides with digitalmodel's `2`. Design-blocker: `cfg[basename]` is not the result payload. MINORs: m1 pilot unverified, m2 error-envelope pre-`try` gap, m3 `input_hash` volatile set undefined. |
| Codex | UNAVAILABLE | rc=3 — `codex exec` stdin-hangs under Claude-Code Bash (`CLAUDECODE` env). Re-run pending via `env -u CLAUDECODE`. |
| Gemini | UNAVAILABLE | hung on interactive browser-auth; needs operator login. T3→T2 degrade per cross-review routing rule. |

**How this revision resolves Round 1 (each finding re-verified against the live checkout):**
- **M1 (in-memory path):** the in-memory `cfg`/`config_flag=True` path is the explicit Step 1.5 target; the prior in-session run + static dispatch trace stand. The Round-1 "import timed out" note was a too-short timeout — a 2026-06-28 bounded re-run loads green in ~29.4 s. AC#1 demands a passing harness test as evidence.
- **M2 (standardization):** `save_cfg` standardizes ALWAYS and gates only `saveDataYaml` (+ its path computation), verified against `ApplicationManager.py:375/377`. `result_hash` is over the standardized payload. Test `test_save_cfg_persist_false_no_write_but_standardizes`.
- **M3 (schema collision):** RESOLVED by D1 — v2 is the additive superset; assetutilities adopts `schema_version: 2` + required `invocation:` key + the #3282-owned `result:` descriptor; #3295 reserves `request_schema`/`response_schema`. No v3.
- **Design-blocker (`cfg[basename]`):** replaced by the per-workflow declared `ResultLocator` (`kind: in_memory | files`) sourced from the registry `result:`/`outputs:`.
- **m2 (error envelope):** resolution + cfg build inside the guarded region; unknown id → error envelope (test pinned).
- **m3 (input_hash):** explicit `VOLATILE_TOP_KEYS = {"Analysis", "default", "cfg_array"}` + sorted-key JSON canonicalization.
- **New (D3 determinism):** `reproducible` is now computed (default `None`, measured under `verify_reproducible=True`) — the Round-1 hardcoded `True` is removed; `provenance.code_version = {package_version, git_sha}`. (Round-2 superseded the file-output `result_hash` from sorted basenames to **file CONTENTS** — see Round-2 resolution below.)

### Round 2 (2026-06-28) — verdict: **MAJOR** (3 findings; now addressed by the R3 revision above)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MAJOR** | F1 `persist=False` is NOT side-effect-free — routers write output files themselves (`data_exploration.py:83/93/111`) before `save_cfg`, so `engine(persist=False)` still writes the example/result dir on every call; the "no file write" Deliverable/pseudocode/Risk and the `test_engine_persist_param_threads_through` row were false. F2 `csv_utilities` cited as a files-branch demo target but it is NOT one of the 9 registry rows and its router `return cfg` writes nothing → `run_workflow("csv_utilities")` errors at registry resolution; AC unsatisfiable. F3 `kind:files` `result_hash` hashed only sorted basenames (never content); data_exploration always emits the same 2 basenames → `reproducible` tautologically `True` regardless of content drift → determinism AC vacuous. |
| Codex | UNAVAILABLE | re-run pending via `env -u CLAUDECODE`. |
| Gemini | UNAVAILABLE | needs operator browser-auth. T3→T2 degrade per cross-review routing rule. |

**How the R3 revision resolves Round 2 (each finding re-verified against the live checkout, owner-locked design applied):**
- **F1 (side-effect-freeness):** the runner now **sandboxes the result folder per call** (`_run_once`: `tempfile.mkdtemp()` → set `cfg.Analysis.result_folder`/`analysis_root_folder` + abs `cfg.file_management.output_directory` → `engine(cfg=..., config_flag=True, persist=False)` → `shutil.rmtree`). All router writes land in the throwaway dir; the repo/example dirs are untouched. `persist=False` is reframed to gate **only** the `save_cfg` cfg-dump. Verified at `ApplicationManager.py:299` (abs `output_directory` survives `configure_result_folder`). Test `test_run_workflow_sandboxes_router_writes`; `test_engine_persist_param_threads_through` reworded to assert dump-gating only.
- **F2 (csv_utilities):** removed as a demo target everywhere; the `kind:files` branch is demonstrated on **data_exploration** (a real registry row). `csv_utilities_router.py` is retained only as evidence of the `cfg[basename]` design hole. `kind:in_memory` documented as supported-but-currently-unexercised.
- **F3 (content-blind hash):** `kind:files` `result_hash` now reads each sandbox output file and hashes `basename → sha256(content)` (sorted) — content-sensitive AND location-independent. Tests `test_result_hash_files_content_sensitive` + `test_result_hash_files_location_independent`; `compute_reproducible` compares content hashes across two fresh sandboxes.

### Round 3 (2026-06-28)
(PENDING — re-review after this revision; Claude inline + Codex via `env -u CLAUDECODE`. **Overall result: PENDING.**)

---

## Risks and Open Questions

- **Risk — slow cold import (~30 s), NOT a hang.** `engine.py` imports `WebScraping`/`TextAnalytics`/`DownloadDataFromURL` at module load; the first `run_workflow` call inherits a ~30 s import cost (measured 2026-06-28). Mitigation: implementation re-verifies the in-memory path runs green under the repo pytest harness; if the cost is unacceptable, file a follow-on to lazy-import the heavy routers in `engine.py`. Not a blocker for AC#1.
- **Risk — persist guard correctness.** Splitting `save_cfg` must not change the `persist=True` output. The byte-for-byte test (`test_save_cfg_persist_true_backward_compat`) plus the full existing suite are the guardrails. The `output_dir`/`filename_path` computation moves inside the `persist` branch (only needed for the write), removing the in-memory path's dependency on `Analysis["analysis_root_folder"]`.
- **Risk — sandbox must actually capture every router write.** The side-effect-freeness claim depends on `cfg.file_management.output_directory = <abs sandbox>` being honored by `configure_result_folder` (verified: `ApplicationManager.py:299` returns an absolute `output_directory` verbatim as `result_folder`, surviving `configure()`'s reset of `analysis_root_folder` to cwd on the in-memory path). Guardrail: `test_run_workflow_sandboxes_router_writes` snapshots the repo `examples/.../results/` dir before/after and asserts **no** change. If any future router writes outside `result_folder` (e.g., a hardcoded path), that test catches it and the sandbox set is widened. Demonstrated on `data_exploration`; per-workflow `result:` population is the adoption children ([#3285](https://github.com/vamseeachanta/workspace-hub/issues/3285)/[#3286](https://github.com/vamseeachanta/workspace-hub/issues/3286)).
- **Risk — result-locator coverage.** The `files` default covers the file-writing registry rows (data_exploration, excel_utilities, zip_utilities, word_utilities, visualization, …). `in_memory` is opt-in per row and **currently unexercised** (no registry row exposes data via `cfg[basename]`). #3282 demonstrates `files` on `data_exploration` and documents the convention. **Scope boundary, not a defect.**
- **Risk — reproducible double-run cost/side effects.** `verify_reproducible=True` runs the engine twice; each run does the ~30 s import once (warm thereafter) and writes only into its **own** per-call temp sandbox, which is `rmtree`'d — never the repo/example dirs. Default is `False` (→ `reproducible=None`) so the common path pays nothing. The formal cross-run volatile-field **key-allowlist** is #3283's (Wave 2, D6); #3282's content-hash `result_hash` (basename → sha256(content), standardized payload) is sufficient — and now genuinely content-sensitive — for the in-process double-run comparison.
- **Risk — registry reconciliation overlap with #3295.** #3282 lands `schema_version: 2` + `invocation:` + per-row `result:` (all additive/optional). #3295 owns the formal cross-registry reconciliation and the `request_schema`/`response_schema` slot reservation. If #3295 renames a field, a fast follow-up adjusts; the `result:` shape itself is #3282-owned and stable.
- **Risk — dependency weight.** `ResultEnvelope` is a stdlib `dataclass` (not Pydantic) to avoid a hard dep in the shared lib; serialization via explicit `to_dict`/`from_dict`. worldenergydata may later adapt it to its Pydantic surface (#3286).
- **Risk — wheel packaging ([assetutilities #88]).** `run_workflow(workflow_id=...)` loading a packaged example input hits the example-not-in-wheel gap. Mitigation: primary path is `run_workflow(id, params=<dict>)` / `run_workflow(cfg=<dict>)`, needing no packaged example. Note the dependency; do not block.

**Open Questions:** none outstanding. The three former Round-1 open questions are now SETTLED by owner decisions: schema version (D1 — v2 superset, no v3), `provenance.code_version` shape (D3 — `{package_version, git_sha}`), and file-output `result_hash` (D3 + R2-fix — over **file CONTENTS**: `basename → sha256(content)`, sorted; content-sensitive AND location-independent). The Round-2 owner-locked design (per-call result-folder **sandbox** for side-effect-freeness, csv_utilities removed as a demo target, content-hash determinism) is baked into the plan above.

---

## Complexity: T2

**T2** — one new small package (3 files) + two minimal backward-compatible method edits (`engine.persist`, `save_cfg.persist`) + additive v2-superset registry fields + a schema doc, TDD throughout. Flagged for **T3-depth review** because it is the foundational contract the rest of epic #3281 inherits.
