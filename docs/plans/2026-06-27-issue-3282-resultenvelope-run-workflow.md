# Plan for #3282: wf-api(assetutilities) — ResultEnvelope + run_workflow() + registry result descriptor

> **Depends on #3297 (engine embeddability).** This plan is re-scoped (Wave-1d) onto the #3297 **embed contract**: `run_workflow` will call the dedicated embed path `engine(cfg=<built cfg>, embed=True, root_folder=<tempdir>, log_to_file=False)` — **NOT** `engine(cfg=..., config_flag=True)` and **NOT** a `persist=False` "sandbox" hack. The prior "persist=False suppresses writes / sandbox result_folder" design was retired by the Wave-1c review, which proved the engine is **cwd-coupled** (`config_flag=True` discards the caller cfg at `generateYMLInput`, and even with the cfg honored the result/log folders resolve under `os.getcwd()` not an injected root). #3297 (now at plan-review, no-MAJOR) adds `ConfigureApplicationInputs.configure_embed(cfg, basename, root_folder, log_to_file=False)` — it **merges** the caller cfg (does not discard it), routes **all** writes (results + logs) under `root_folder`, and uses no-file logging. #3282 consumes that path. **#3282 cannot land until #3297 lands** (the `embed=True` parameter must exist). This plan owns **zero** engine/ApplicationManager edits — it only *calls* `engine(embed=True)`.
>
> **Status:** draft (depends on #3297)
> **Complexity:** T2 (new `workflow_api` package; consumes the #3297 embed path; foundational blast radius — review at T3 depth)
> **Date:** 2026-06-27 (re-scoped 2026-06-28 Wave-1d onto the #3297 embed contract — see "Revision note (Wave-1d)")
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3282
> **Epic:** https://github.com/vamseeachanta/workspace-hub/issues/3281
> **Depends on:** https://github.com/vamseeachanta/workspace-hub/issues/3297 (engine embeddability — MUST land first)
> **Client:** N/A — no wiki content touched
> **Lane:** lane:claude (contract/API design; no engine edits owned here)
> **Review artifacts:** scripts/review/results/2026-06-27-plan-3282-claude.md | ...-codex.md | ...-gemini.md

---

## Revision note (2026-06-28, Wave-1d — re-scope onto the #3297 embed contract)

The Wave-1c review (Round-2 MAJOR) proved the prior side-effect-freeness mechanism was unsound: pointing `cfg.Analysis.result_folder` / `analysis_root_folder` at a tempdir and calling `engine(cfg=..., config_flag=True, persist=False)` does **not** isolate the call, because (a) `config_flag=True` silently **discards** the caller's in-memory cfg at `generateYMLInput` (`ApplicationManager.py:194-196`) — so the tempdir overrides on the caller cfg never even reach the engine — and (b) the engine forces `analysis_root_folder = os.getcwd()` and writes `<cwd>/logs/<name>.log` + `<cwd>/results/{,Data,Plot}` regardless. The fix is a **separate prerequisite**, #3297, which adds a real embed path. This revision re-scopes #3282 onto it. The substantive changes since Wave-1c:

1. **Side-effect-freeness now comes from the #3297 EMBED PATH, not a persist/sandbox hack.** `run_workflow` calls `engine(cfg=<built cfg>, embed=True, root_folder=tempfile.mkdtemp(), log_to_file=False)`. #3297's `configure_embed` **merges** the caller cfg (preserving it), points `result_folder`/`analysis_root_folder` at the injected `root_folder`, creates `<root>/results/{,Data,Plot}`, and logs to stdout only (no `.log`, no `logs/` dir). `run_workflow` then reads + content-hashes the emitted outputs from that tempdir and `shutil.rmtree`s it. **All** "persist=False suppresses the write" / "sandbox the result_folder" framing is removed — the embed path's injected `root_folder` is the isolation mechanism, and the rmtree of a throwaway dir is the cleanup.

2. **Basename-derivation residual (Wave-1c MAJOR) fixed by globbing the injected root.** Because the embed path HONORS the caller cfg, the output `file_name` derives from the **cfg** (`basename: data_exploration` + `default.config.overwrite.output: True` ⇒ `file_name == "data_exploration"`, verified below), so the router writes `data_exploration_FST1.csv` / `data_exploration_FST2.csv` into `<root>/results/` — **NOT** the registry's declared `input_FST*.csv` (the `input_` prefix only arises on the CLI **file** path, where `customYaml` is the `input.yml` path). `extract_result` therefore reads the **actually emitted** files by **globbing the injected root** (`<root>/results/*`), never by matching registry `outputs:` names. The registry `outputs:` list degrades to documentary/expected-count metadata, not a literal filename oracle.

3. **`result_hash` for `kind:files` = content hash of the emitted files.** Read each emitted file in the tempdir, hash `sorted(basename) → sha256(file CONTENTS)`. Location-independent (basename-keyed, drops the throwaway abs path) AND content-sensitive (a changed output value flips the hash). `compute_reproducible` does a **true double-run content comparison** (two fresh embed runs, each with its own `root_folder`, compare content hashes). The Wave-1c basename-only tautology is gone.

4. **csv_utilities removed as the files demo; data_exploration is the demo.** `csv_utilities` is **not** a registry row and its `router()` `return cfg` writes nothing — `run_workflow("csv_utilities")` would error at registry resolution. The `kind:files` branch is demonstrated on **`data_exploration`** (a real registry row that writes 2 CSVs). `kind:in_memory` is documented as **supported-but-currently-unexercised** — all 9 registry workflows are file-writing and `cfg[basename]` holds **paths/echoed input**, not data — so the plan claims **no** in_memory demo that no row satisfies.

5. **`build_cfg(row, params)` is specified.** Start from the registry row's `basename` + its example `input` (loaded), deep-merge caller `params`, hand the merged cfg to the embed path. The example-file load interacts with assetutilities#88 (example not in wheel); the **params-dict primary path** (`run_workflow(id, params=<dict>)` / `run_workflow(cfg=<dict>)`) avoids it — documented under Risks.

6. **#3282 owns ZERO engine edits.** The Wave-1c `engine.persist` / `save_cfg.persist` edits are **deleted** from this plan — they belong to the retired persist mechanism. #3282 only consumes `engine(embed=True, root_folder=..., log_to_file=False)`, which #3297 provides. The schema-reservation work (#3295), the `result:` descriptor ownership, `ResultEnvelope` as a stdlib dataclass, `provenance.code_version = {package_version, git_sha}`, and the `input_hash` volatile-key allowlist are all retained from Wave-1c.

---

## Resource Intelligence Summary

### Existing repo code (verified 2026-06-28 against `/mnt/local-analysis/assetutilities`)

- **Prereq (#3297) embed path** — `engine(inputfile=None, cfg=None, config_flag=True, root_folder=None, log_to_file=True, embed=False)`. When `embed=True` (the path #3282 uses), the engine calls a **per-call** `ConfigureApplicationInputs().configure_embed(cfg, basename, root_folder, log_to_file=log_to_file)` which **bypasses `unify_application_and_default_and_custom_yamls`** (the step that discards the caller cfg on `config_flag=True`), **merges** the computed `Analysis` params **into** the caller cfg, points `analysis_root_folder`/`result_folder` at the injected `root_folder`, and runs `set_logging` in no-file mode when `log_to_file=False`. Per #3297's plan, `engine(embed=True)` then runs `fm.router(cfg_base)`, dispatches on `basename`, and `save_cfg(cfg_base)` writes the cfg-dump into `<root>/results/` (inside the sandbox, so harmless). **This is the exact path `run_workflow` calls. #3282 does not edit it.**
- **Verified — file_name derivation (Wave-1c MAJOR root cause), `ApplicationManager.py:228-282` + `:337-347`:** `get_application_configuration_parameters` (the **CLI/file** path) sets `custom_file_name = os.path.split(self.ApplicationInputFile)[1].split(".")[0]` (`:240`) — i.e. `"input"` for `.../data_exploration/input.yml` — then `configure_overwrite_filenames` (`:337-339`) sets `cfg.Analysis.file_name = file_name_for_overwrite = custom_file_name` when `cfg["default"]["config"]["overwrite"]["output"] is True`. So the **CLI** path yields `file_name == "input"` ⇒ outputs `input_FST*.csv` (matching the registry `outputs:`). The **embed** path (#3297 `configure_embed`) instead sets `custom_file_name = basename` (`= "data_exploration"`, no `meta.label`) and `file_name_for_overwrite = custom_file_name`, and the SAME `configure_overwrite_filenames` (reused by `configure_embed`) collapses `file_name` to `"data_exploration"`. **Net: the embed path emits `data_exploration_FST1.csv` / `data_exploration_FST2.csv`, NOT `input_FST*.csv`.** This is why `extract_result` must glob the injected root, not match registry names.
- **Verified — router output naming, `data_exploration.py:78-93` + `:106-113`:** every CSV is written to `os.path.join(cfg["Analysis"]["result_folder"], cfg["Analysis"]["file_name"] + "_" + label + ".csv")`, where `label` ∈ {`FST1`, `FST2`} comes from `data.groups[].label` in the input. So filename = `<file_name>_<label>.csv`. Confirms the prefix is fully cfg-derived (`file_name`), and the labels are data-derived (`FST1`/`FST2`).
- **Verified — example input, `examples/workflows/data_exploration/input.yml`:** `basename: data_exploration`; `data.groups` labels `FST1`/`FST2` (sample_1.csv / sample_2.csv); `default.config.overwrite.output: True`. So under the embed path the two emitted basenames are deterministically `data_exploration_FST1.csv` and `data_exploration_FST2.csv`.
- **Verified — result folder location, `ApplicationManager.py:284-335`:** `configure_result_folder(analysis_root_folder)` builds `result_folder = <analysis_root_folder>/results` (default `output_directory == "results"`, relative; resolved against the root) and creates `results/{,Data,Plot}`. In the embed path `analysis_root_folder == root_folder == <tempdir>`, so the CSVs land in `<tempdir>/results/`. `extract_result` globs there (the engine returns the resolved `cfg_base["Analysis"]["result_folder"]`, which `run_workflow` reads back to locate the glob root robustly).
- **Verified — `data_exploration.py:115-117`:** `cfg[cfg["basename"]] = {"df_basic_statistics": {"groups": [{"data": <filepath>, "label": ...}, ...]}}` — i.e. `cfg[basename]` holds **file paths**, not data. Evidence that `cfg[basename]` is an unreliable result locator (the design hole the `result:` descriptor closes).
- **Verified — `csv_utilities_router.py`:** `router(self, cfg)` does a no-op check and `return cfg`. There is **no** `cfg["csv_utilities"]` result key, and csv_utilities is **not** one of the 9 registry rows. Cited only as evidence of the `cfg[basename]` design hole — **never a runnable demo target**.
- **Verified — `docs/registry/workflows.yaml`:** `schema_version: 1`, `repo: assetutilities`, `issue: 3063`, **9 rows** (visualization, data_exploration, excel_utilities, zip_utilities, yaml_utilities, file_management, file_edit, word_utilities, reportgen). The `data_exploration` row declares `outputs: [examples/workflows/data_exploration/results/input_FST1.csv, .../input_FST2.csv]` — the **CLI-path** filenames; the embed path emits `data_exploration_FST*.csv` instead, which is exactly why `extract_result` cannot trust these names. No top-level `invocation:` key yet (added here).
- **Verified — `digitalmodel/docs/registry/workflows.yaml`:** `schema_version: 2`, top-level `invocation: "uv run python -m digitalmodel {input}"`, deckhand routing triple. The v2 superset assetutilities aligns to.
- **Verified — `deckhand/src/deckhand/capability_smoke.py:231-232`:** `template = str(registry.get("invocation") or "uv run python -m {pkg} {input}")`; `rendered = template.replace("{input}", input_rel)`. The reference `invocation:` resolver — `{input}`-only substitution. Named in `SCHEMA.md`.
- **Gap** — no `workflow_api/` package anywhere under `src/assetutilities` (`ResultEnvelope` + `run_workflow()` are greenfield).
- **Gap** — `engine()` returns the whole mutated `cfg`; no typed result payload, no provenance, no determinism hash, no declared result location.

### Standards
Not applicable — harness/contract code, not an engineering calculation. The provenance `standard_revisions` field reuses the *shape* of the Citation sidecar in `.claude/rules/calc-citation-contract.md`; it introduces no standards-derived constants, so no `Citation` emission is required here.

### LLM Wiki pages consulted
None — contract/infra work, no domain knowledge. (`Client: N/A`.)

### Documents consulted
- Epic [#3281](https://github.com/vamseeachanta/workspace-hub/issues/3281) — defines the `ResultEnvelope` field set and the in-process-only scope (HTTP deferred to a later child).
- [#3297](https://github.com/vamseeachanta/workspace-hub/issues/3297) (OPEN, plan-review) — **the dependency.** Engine embeddability: adds `engine(embed=True, root_folder=, log_to_file=)` + `ConfigureApplicationInputs.configure_embed(...)`. #3282 calls that embed path; it cannot land until #3297 lands. Plan: `docs/plans/2026-06-28-issue-3297-engine-embeddability.md`.
- [#3295](https://github.com/vamseeachanta/workspace-hub/issues/3295) (OPEN) — reconcile registry `schema_version` into a unified **v2 superset**; it owns the cross-registry reconciliation and **reserves** the structured `request_schema`/`response_schema` slots pending #3282. #3282 contributes the `result:` descriptor shape into that superset.
- [#3283](https://github.com/vamseeachanta/workspace-hub/issues/3283) — golden-determinism harness + volatile-field **key-allowlist** spec; **DEFERRED to Wave 2** (D6), NOT a dependency of #3282; #3282 computes `reproducible` itself (opt-in double-run).
- [#3050](https://github.com/vamseeachanta/workspace-hub/issues/3050) / [#3067](https://github.com/vamseeachanta/workspace-hub/issues/3067) — upstream CLI/registry contract epic; the API-contract doc is a companion deliverable, not this issue.
- digitalmodel `results.json {meta, lookup, index, curves}` (buckling/FFS) — precedent for a structured result payload.

### Gaps identified
- No shared `ResultEnvelope` type (greenfield).
- No `run_workflow(id, params)` entrypoint (greenfield).
- The registry lacks a top-level `invocation:` key and a uniform per-row `result:` descriptor — both added by this plan.
- The engine has no embed path yet — **closed by #3297 (dependency), not by #3282.**

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`): `#3282` OPEN (this issue); `#3297` OPEN/plan-review (the dependency); `#3295` OPEN (schema reconciliation); `#3283` OPEN (deferred Wave 2); `#3281` OPEN (parent epic).

**file_name derivation — embed vs CLI** (`ApplicationManager.py`):
```
240:  custom_file_name = os.path.split(self.ApplicationInputFile)[1].split(".")[0]   # CLI path -> "input"
338:  if cfg["default"]["config"]["overwrite"]["output"] is True:
339:      cfg["Analysis"]["file_name"] = cfg["Analysis"]["file_name_for_overwrite"]   # collapse to custom_file_name
# embed path (#3297 configure_embed): custom_file_name = basename = "data_exploration"
#   -> file_name_for_overwrite = "data_exploration" -> (overwrite True) file_name = "data_exploration"
```

**Router output naming** (`data_exploration.py`):
```
106-108: filename = os.path.join(cfg["Analysis"]["result_folder"],
                                 cfg["Analysis"]["file_name"] + "_" + label + ".csv")
111:     df_statistics.to_csv(filename, index=False)     # -> <root>/results/data_exploration_FST{1,2}.csv (embed)
115:     cfg[cfg["basename"]] = {...}                     # holds paths, not data
```

**Design-hole + resolver:**
```
csv_utilities_router.py:    return cfg                                              # NO result key; NOT a registry row
capability_smoke.py:231:    template = str(registry.get("invocation") or "...{pkg} {input}")
capability_smoke.py:232:    rendered = template.replace("{input}", input_rel)        # {input}-ONLY substitution
```

(Distinct sources: issue body + #3297 plan + #3295 body + engine.py + ApplicationManager.py + data_exploration.py + input.yml + csv_utilities_router.py + both registry files + capability_smoke.py = 10+.)

---

## Step 1.5 — Reproduction

**Claim under test:** the #3297 embed path `engine(cfg=<built cfg>, embed=True, root_folder=<tempdir>, log_to_file=False)` (a) honors the caller's in-memory cfg, (b) writes its outputs **only** under `root_folder` (as `data_exploration_FST*.csv`, NOT `input_FST*.csv`), (c) creates no `.log`/`logs/`, so a content hash over the emitted files is well-defined; AND `cfg[basename]` is NOT a usable result payload (holds file paths).

**Wave-1c evidence that the OLD path failed (retained for the audit trail):**
- `config_flag=True` discards the caller cfg at `generateYMLInput` (`ApplicationManager.py:194-196`) — proven in #3297's Round-1 review by a sentinel `cfg["Analysis"]["analysis_root_folder"]` returning **absent**. ⇒ the prior tempdir overrides on the caller cfg never reached the engine.
- `data_exploration.py:111` writes CSVs into `cfg["Analysis"]["result_folder"]` which (on `config_flag=True`) resolved under `os.getcwd()`, not any caller-supplied tempdir. ⇒ the prior "sandbox the result_folder" plan littered the cwd.

**This plan's reproduction (to run at implementation time, AFTER #3297 lands):**
```
# embed path, from a scratch cwd:
cb = engine(cfg=build_cfg(data_exploration_row, params=None), embed=True,
            root_folder="/tmp/auwf_probe", log_to_file=False)
# EXPECT: /tmp/auwf_probe/results/data_exploration_FST1.csv and _FST2.csv exist;
#         NO *.log anywhere; /tmp/auwf_probe/logs absent;
#         cwd has no new results/ or logs/;
#         cb["data_exploration"] holds file PATHS (not data) -> cfg[basename] is not the result locator.
```
Because #3297 is the dependency, AC#1's empirical demonstration is gated on #3297 landing; until then the design conclusion stands on #3297's verified call-chain trace + the file_name/router static analysis above.

**Static corroboration:** the embed dispatch trace `engine(embed=True) → configure_embed → fm.router → basename dispatch → save_cfg(into <root>/results)` (from #3297's pseudocode) + the `file_name == "data_exploration"` derivation + `data_exploration.py:106-111` jointly fix the emitted filenames as `data_exploration_FST{1,2}.csv` under `<root>/results/`. The design conclusion holds independent of runtime.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md |
| Dependency plan (#3297) | docs/plans/2026-06-28-issue-3297-engine-embeddability.md |
| Envelope impl | `assetutilities/src/assetutilities/workflow_api/envelope.py` |
| Result-locator + runner impl (consumes `engine(embed=True)`) | `assetutilities/src/assetutilities/workflow_api/runner.py` |
| Package init | `assetutilities/src/assetutilities/workflow_api/__init__.py` |
| Registry (v2 superset: `invocation` + per-row `result`) | `assetutilities/docs/registry/workflows.yaml` |
| Schema doc (names `result:` shape + `invocation` + capability_smoke.py resolver) | `assetutilities/docs/registry/SCHEMA.md` |
| Tests | `assetutilities/tests/workflow_api/test_envelope.py`, `test_runner.py` |
| Plan reviews | scripts/review/results/2026-06-27-plan-3282-{claude,codex,gemini}.md |

> **Note:** `assetutilities/src/assetutilities/engine.py` and `.../common/ApplicationManager.py` are **NOT** in #3282's change set — they are edited by #3297 (the dependency). #3282 only *imports and calls* `engine(embed=True)`.

---

## Deliverable

A `workflow_api` package in `assetutilities/src/` exposing `run_workflow(workflow_id, params=None, cfg=None, verify_reproducible=False) -> ResultEnvelope` — a typed, **genuinely side-effect-free** in-process call built on the **#3297 embed path**. Side-effect-freeness is achieved by `engine(cfg=<built cfg>, embed=True, root_folder=tempfile.mkdtemp(), log_to_file=False)`: the embed path routes **all** result + log writes under the injected `root_folder` and emits no `.log`; `run_workflow` reads + content-hashes the emitted outputs from that tempdir, then `shutil.rmtree`s it — leaving the repo/example dirs byte-for-byte untouched. The result location is **declared per-workflow** (registry `result:` descriptor, `kind: in_memory | files`); for `kind:files` the **actually emitted** files are discovered by **globbing the injected root** (the embed-path file_name is cfg-derived — `data_exploration_FST*.csv`, not the registry's `input_FST*.csv`). Plus the `ResultEnvelope` type with **computed** determinism fields (`input_hash`, `result_hash` over **file contents** for `kind:files`, `reproducible` via a true double-run content comparison, `provenance.code_version = {package_version, git_sha}`), the registry's required top-level `invocation:` key, the per-row `result:` descriptor (#3282-owned), and a registry `SCHEMA.md` naming `capability_smoke.py` as the reference invocation resolver — all TDD-covered. **No engine/ApplicationManager edits owned here** (those are #3297's).

---

## Pseudocode

```python
# ── envelope.py ────────────────────────────────────────────────
@dataclass
class ResultEnvelope:                     # stdlib dataclass, NOT Pydantic (no hard dep in the shared lib)
    workflow_id: str
    status: str                  # "ok" | "error"
    result: dict                 # the DECLARED result payload (see ResultLocator), never the whole cfg
    provenance: dict             # {code_version: {package_version, git_sha}, standard_revisions: [],
                                 #  data_as_of, input_hash}
    determinism: dict            # {result_hash, reproducible: bool | None}   # None == "not checked"
    confidence: dict | None      # optional screening-vs-certified band
    warnings: list[str]
    def to_dict() / from_dict()  # lossless round-trip; canonical sorted-key order

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
    # kind=="files": hash sorted(basename) -> sha256(FILE CONTENTS). Location-independent (basename-keyed,
    #   drops the throwaway tempdir abs path) AND content-sensitive (a changed output value flips the hash).
    #   extract_result has ALREADY read each emitted file in the tempdir into payload["outputs"][i]["sha256"].
    if payload.get("kind") == "files":
        canon = {"kind": "files",
                 "files": sorted((f["basename"], f["sha256"]) for f in payload.get("outputs", []))}
    else:
        canon = payload                                       # in_memory: hash the standardized value
    return sha256(json.dumps(canon, sort_keys=True, default=str))

# reproducible is COMPUTED, never hardcoded. Default None == "not checked".
# True double-run content comparison: each run uses its OWN embed root_folder; result_hash compares
# file CONTENTS by basename -> deterministic workflow -> equal hashes -> True; drifted bytes -> False.
def compute_reproducible(rerun_fn, first_hash, verify: bool):
    if not verify:
        return None                                           # honest: not a fabricated True
    _, _, second_hash = rerun_fn()                            # second embed run in a FRESH root_folder
    return second_hash == first_hash                          # measured over emitted-file CONTENTS

# ── ResultLocator: the design-hole fix (shape OWNED by #3282) ──
#   result:
#     kind: files            # "files" (default) | "in_memory"
#     key: data_exploration  # for in_memory: cfg[key] is the payload
#     outputs: [...]         # for files: DOCUMENTARY (expected count / human reference) — NOT a filename
#                            #   oracle. The embed path's file_name is cfg-derived, so the real emitted
#                            #   names (data_exploration_FST*.csv) differ from these CLI-path names.
#   NOTE: kind=="in_memory" is SUPPORTED but currently UNEXERCISED — all 9 registry rows are file-writing
#   (cfg[basename] holds paths/echoes input, not data). #3282 demos kind=="files" on data_exploration and
#   only documents the in_memory shape. No in_memory demo is claimed.
def extract_result(cfg_base, locator, root_folder) -> (payload: dict, warnings: list):
    if locator.kind == "in_memory":
        if locator.key not in cfg_base:
            return {"kind": "in_memory", "value": None}, \
                   [f"declared in_memory result_key '{locator.key}' absent from cfg"]   # NOT silent {}
        return {"kind": "in_memory", "value": cfg_base[locator.key]}, []
    else:  # kind == "files" — read the ACTUALLY emitted files by GLOBBING the injected root
        # The embed path resolves outputs into <root_folder>/results/ ; read the engine-resolved folder
        # back from cfg_base for robustness, fall back to <root_folder>/results.
        results_dir = cfg_base.get("Analysis", {}).get("result_folder") \
                      or os.path.join(root_folder, "results")
        # CRITICAL (R4 MAJOR): engine.py:120 ALWAYS calls save_cfg, which writes a cfg-DUMP
        # <results_dir>/<file_name>.yml into this SAME dir (saveData.saveDataYaml appends ".yml").
        # That dump embeds the tempdir abspath + a start_time datetime (standardize_yml_data does NOT
        # convert datetime), so globbing it would (a) inflate the file count and (b) make result_hash
        # location- AND time-dependent -> reproducible spuriously False. It MUST be excluded. Its name is
        # exactly <file_name>.yml (no "_<label>" suffix); genuine router outputs are <file_name>_<label>.<ext>.
        file_name = cfg_base.get("Analysis", {}).get("file_name", "")
        cfg_dump = os.path.abspath(os.path.join(results_dir, file_name + ".yml"))
        emitted = sorted(p for p in glob.glob(os.path.join(results_dir, "*"))
                         if os.path.isfile(p) and os.path.abspath(p) != cfg_dump)  # REAL outputs only
        files, warns = [], []
        for path in emitted:
            with open(path, "rb") as fh:
                files.append({"basename": os.path.basename(path),
                              "sha256": sha256(fh.read()).hexdigest(),
                              "size": os.path.getsize(path)})
        if not files:
            warns.append(f"declared kind:files workflow emitted no files under {results_dir}")
        # Optional: cross-check emitted COUNT against len(locator.outputs) and warn on mismatch
        # (documentary only — names are NOT compared, since embed file_name != registry CLI names).
        if locator.outputs and len(files) != len(locator.outputs):
            warns.append(f"emitted {len(files)} files; registry outputs lists {len(locator.outputs)}")
        # payload carries basenames + per-file content digest (NOT dead tempdir paths -> dir is rmtree'd)
        return {"kind": "files", "outputs": files}, warns

# ── runner.py ─────────────────────────────────────────────────
# Each engine() invocation runs via the #3297 EMBED PATH with root_folder=<throwaway tempdir>, so NO
# result/log write ever touches the repo/example dirs. The tempdir is rmtree'd after content extraction.
def _run_once(cfg, locator) -> (payload, warns, rhash):
    root = tempfile.mkdtemp(prefix="auwf_")
    try:
        basename = cfg["basename"]                            # e.g. "data_exploration"
        # THE #3297 EMBED PATH — honors caller cfg, routes ALL writes under root, no .log:
        cb = engine(cfg=copy.deepcopy(cfg), embed=True, root_folder=root, log_to_file=False)
        payload, warns = extract_result(cb, locator, root)    # read emitted-file CONTENTS before teardown
        rhash = result_hash(payload)
        return payload, warns, rhash
    finally:
        shutil.rmtree(root, ignore_errors=True)               # throwaway -> repo/example dirs untouched

def build_cfg(row, params) -> dict:
    # Start from the registry row's basename + its example input (loaded), then deep-merge caller params.
    cfg = {"basename": row["basename"]}
    if row.get("input"):
        # NOTE (R4 MINOR): this loads examples/workflows/<slug>/input.yml — a packaged-EXAMPLE gap that is
        # RELATED TO but DISTINCT FROM assetutilities#88 (which is specifically `base_configs/modules/**`).
        # So run_workflow(id, params=...) STILL hits this example load. Only the run_workflow(cfg=<full dict>)
        # entrypoint (which skips build_cfg entirely) is load-free. Recommended #88-/example-free path: pass cfg=.
        cfg = deep_merge(cfg, load_yaml(resolve_example_path(row["input"])))
    if params:
        cfg = deep_merge(cfg, params)                         # caller params win
    return cfg

def run_workflow(workflow_id=None, params=None, cfg=None, verify_reproducible=False) -> ResultEnvelope:
    wid = workflow_id or "(inline-cfg)"
    try:                                                  # fail-closed from the FIRST line
        if cfg is None:
            row     = resolve_registry_row(workflow_id)   # unknown id -> raises -> caught below
            cfg     = build_cfg(row, params)
            locator = ResultLocator.from_row(row)
        else:
            row     = lookup_row_for_cfg(cfg)             # may be None
            locator = ResultLocator.from_row(row) if row else ResultLocator.default_for(cfg)
        ihash          = input_hash(cfg)
        payload, warns, rhash = _run_once(cfg, locator)   # embed path; side-effect-free
        repro          = compute_reproducible(lambda: _run_once(cfg, locator), rhash,
                                              verify_reproducible)   # None unless asked; FRESH root_folder
        return ResultEnvelope(wid, "ok", payload,
                              provenance(ihash), {"result_hash": rhash, "reproducible": repro},
                              None, warns)
    except Exception as e:
        return ResultEnvelope(wid, "error", {}, provenance(None),
                              {"result_hash": None, "reproducible": None}, None, [str(e)])
```

> **No engine.py / ApplicationManager.py pseudocode here** — #3282 consumes `engine(embed=True, root_folder=, log_to_file=)` exactly as #3297 defines it. The `engine.persist` / `save_cfg.persist` edits from the retired Wave-1c design are deleted.

---

## Registry change (v2 superset)

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
    outputs:                                       # DOCUMENTARY (CLI-path names); NOT a runtime oracle
      - examples/workflows/data_exploration/results/input_FST1.csv
      - examples/workflows/data_exploration/results/input_FST2.csv
    result:                                        # #3282-OWNED descriptor; optional per row
      kind: files                                  # embed path emits data_exploration_FST*.csv -> extract_result
                                                   #   GLOBS the injected root; does not match `outputs:` names
    test: uv run python -m assetutilities examples/workflows/data_exploration/input.yml
    runtime: fast
  # ... remaining 8 rows unchanged; `result:` is optional (kind: files default) ...
```

- `request_schema:` / `response_schema:` are **structured (not typed-string) descriptors RESERVED by #3295**; #3282 does NOT populate them and does NOT impose a `str` invariant.
- `docs/registry/SCHEMA.md` (new) documents: the `result:` descriptor shape (`kind: files` default vs `kind: in_memory`); that the per-row `outputs:` list is **documentary** (CLI-path filenames) and the runtime files-branch discovers emitted files by **globbing the injected embed root** (because the embed-path `file_name` is cfg-derived, not input-file-derived); the required `invocation:` key with `{input}`-only substitution; and names `deckhand/src/deckhand/capability_smoke.py` as the reference resolver. **No v3.** It also records that `kind: in_memory` is **supported but currently unexercised** — all 9 rows are file-writing (`cfg[basename]` holds paths/echoes, not data), so no row sets `kind: in_memory` yet.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `assetutilities/src/assetutilities/workflow_api/__init__.py` | export `run_workflow`, `ResultEnvelope` |
| Create | `assetutilities/src/assetutilities/workflow_api/envelope.py` | `ResultEnvelope` stdlib dataclass + `input_hash`/`result_hash` (file-CONTENTS hash for `kind:files`)/`code_version`/`compute_reproducible` + volatile-key spec |
| Create | `assetutilities/src/assetutilities/workflow_api/runner.py` | `run_workflow`, registry resolution, `build_cfg`, `ResultLocator`, `_run_once` (calls **`engine(embed=True, root_folder=mkdtemp(), log_to_file=False)`** → extract → rmtree), `extract_result` (in_memory + files-by-glob-of-injected-root branches) |
| Modify | `assetutilities/docs/registry/workflows.yaml` | `schema_version: 2`; add top-level `invocation:`; add optional per-row `result:` descriptor |
| Create | `assetutilities/docs/registry/SCHEMA.md` | document `result:` shape, `outputs:`-is-documentary + glob-the-injected-root semantics, `invocation:` substitution, name `capability_smoke.py` resolver |
| Create | `assetutilities/tests/workflow_api/test_envelope.py` | envelope + hashing + reproducible TDD |
| Create | `assetutilities/tests/workflow_api/test_runner.py` | runner + locator + registry + side-effect-freeness TDD |
| Update | docs/plans/README.md | index row (workspace-hub) |

> **Dependency, not owned here:** `assetutilities/src/assetutilities/engine.py` (`embed`/`root_folder`/`log_to_file` params) and `.../common/ApplicationManager.py` (`configure_embed`) are edited by **#3297**. #3282 imports and calls them; it does not modify them.

---

## TDD Test List

| Test name | What it verifies | Input | Output |
|---|---|---|---|
| test_envelope_roundtrip | `to_dict`/`from_dict` lossless | populated envelope | equal envelope |
| test_input_hash_excludes_volatile_keys | two cfgs differing only in `Analysis`/`default`/`cfg_array` → same `input_hash` | two cfgs | identical hash |
| test_input_hash_changes_on_real_input | changing a real (non-volatile) input key changes the hash | two cfgs | different hash |
| test_result_hash_files_content_sensitive | same basenames + same bytes → identical `result_hash`; **one output's bytes changed → DIFFERENT `result_hash`** (content-sensitive, not basename-only) | two file payloads (equal vs one byte-differing) | equal-then-different hash |
| test_result_hash_files_location_independent | same basenames + same contents under different tempdirs (and reordered) → identical `result_hash` (basename-keyed, path-dropped) | two file payloads | same hash both ways |
| test_provenance_code_version_shape | `provenance.code_version` has both `package_version` and `git_sha` keys (git_sha may be `None`) | envelope | both keys present |
| test_reproducible_not_hardcoded_default_none | `verify_reproducible=False` → `determinism.reproducible is None` (NOT `True`) | run w/o verify | `reproducible is None` |
| test_reproducible_computed_true_on_double_run | `verify_reproducible=True` on `data_exploration` → `reproducible is True` via two embed runs comparing **file contents** | data_exploration | `reproducible is True` |
| test_run_workflow_writes_nothing_outside_tempdir | **(embed-path isolation)** `run_workflow("data_exploration", ...)` writes **NOTHING** outside its `mkdtemp` root — the repo `examples/workflows/data_exploration/results/` dir is byte-for-byte unchanged (snapshot before/after), no `.log`/`logs/` anywhere, and the temp root is rmtree'd | run + dir snapshot | nothing written outside temp dir; sandbox gone |
| test_extract_result_globs_injected_root_real_filenames | **(basename-derivation fix)** `extract_result(cfg_base, locator, root)` for data_exploration returns the **actually emitted** `data_exploration_*.csv` files read by **globbing the injected root** — NOT the registry's `input_FST*.csv` names. Assert against the demo's *real* emitted set (verified empirically at impl time — the router may emit label `_FST*` and/or column `_<col>`/`_T` variants; do NOT hard-code exactly 2) | data_exploration cfg_base + embed root | per-file content digests for the REAL emitted names |
| test_extract_result_excludes_save_cfg_dump | **(R4 MAJOR fix)** the `save_cfg` cfg-dump `<file_name>.yml` written into `<root>/results/` by `engine.py:120` is **EXCLUDED** from the emitted-file list and the content hash, so `result_hash` is not poisoned by the dump's tempdir-abspath + `start_time` datetime | data_exploration embed run | outputs exclude `data_exploration.yml`; `result_hash` stable across two runs in different tempdirs |
| test_locator_in_memory_missing_key_warns_not_silent | declared `in_memory` key absent → warning appended, NOT silent `{}` | cfg_base missing key | warnings non-empty |
| test_locator_files_emits_no_files_warns | a `kind:files` run that emits nothing → warning, status still ok | cfg_base w/ empty results | warning present |
| test_run_workflow_by_id_returns_envelope | resolves a registry id → ok envelope w/ declared result | `run_workflow("data_exploration", params=...)` | `status=="ok"`, populated `result` |
| test_run_workflow_unknown_id_error_envelope | unknown id is enveloped, NOT raised (fail-closed) | `run_workflow("nope")` | `status=="error"`, warning carries message |
| test_run_workflow_engine_error_envelope | a router exception → error envelope, not a raw traceback | cfg that makes a router raise | `status=="error"`, warning carries message |
| test_build_cfg_merges_params_over_example | `build_cfg(row, params)` loads the example input then deep-merges params (params win) | data_exploration row + override params | merged cfg has params values |
| test_registry_schema_v2_invocation_and_optional_result | registry parses at `schema_version: 2`; top-level `invocation == "uv run python -m assetutilities {input}"`; all 9 rows valid with `result:` optional | current registry | version 2, invocation present, rows valid |

> **Dependency note:** the embed-path tests (`test_run_workflow_writes_nothing_outside_tempdir`, `test_extract_result_globs_injected_root_real_filenames`, `test_reproducible_computed_true_on_double_run`, `test_run_workflow_by_id_returns_envelope`) require `engine(embed=True)` from **#3297**. They are written test-first but go green only once #3297 has landed — explicit ordering gate.

---

## Acceptance Criteria

- [ ] **#3297 has landed** (`engine(cfg=..., embed=True, root_folder=, log_to_file=)` exists and is merged). #3282 does not merge before #3297.
- [ ] `from assetutilities.workflow_api import run_workflow, ResultEnvelope` works; `run_workflow` returns a populated `ResultEnvelope` for `data_exploration` via the **embed path** `engine(cfg=..., embed=True, root_folder=<mkdtemp>, log_to_file=False)`, demonstrated **empirically by a passing test under the repo pytest harness**.
- [ ] **`run_workflow` is genuinely side-effect-free:** a call writes **nothing** outside its per-call `tempfile.mkdtemp()` root — the repo `examples/.../results/` dir is unchanged before/after, no `.log`, no `logs/` — and the root is `shutil.rmtree`'d. Isolation comes from the **embed path's injected `root_folder`** (not `persist=False`, which is removed).
- [ ] **Basename-derivation fix:** `ResultEnvelope.result` for `kind:files` carries the **actually emitted** files discovered by **globbing the injected root** (`data_exploration_FST1.csv` / `data_exploration_FST2.csv`), **NOT** the registry's `input_FST*.csv` names. The `kind:files` branch is demonstrated on **`data_exploration`** (a real registry row); **csv_utilities is NOT a target** (not a registry row, writes nothing). Result is never the whole `cfg`, and never silently `{}`/`None` on a missing declared key (warning emitted).
- [ ] Determinism fields are **computed, not hardcoded**: `input_hash`, `result_hash` present; `reproducible` is `None` when unchecked and a measured `True`/`False` under `verify_reproducible=True` via a **true double-run content comparison** (two embed runs, each its own `root_folder`); `provenance.code_version == {package_version, git_sha}`. File-output `result_hash` is over **file CONTENTS** (sorted basename → sha256(content)) — content-sensitive AND location-independent.
- [ ] `kind:in_memory` is documented as **supported-but-currently-unexercised** (all 9 registry rows are file-writing); the plan claims **no** in_memory demo.
- [ ] `build_cfg(row, params)` starts from the row's basename + loaded example input, deep-merges caller params (params win), and hands the merged cfg to the embed path; the params-dict primary path avoids the assetutilities#88 wheel-package-data gap (documented).
- [ ] Registry adopts the **v2 superset**: `schema_version: 2`, required top-level `invocation: "uv run python -m assetutilities {input}"`, optional per-row `result:` descriptor; all 9 existing rows still validate; `request_schema`/`response_schema` left RESERVED for #3295. `SCHEMA.md` names `capability_smoke.py` as the reference resolver and documents that `outputs:` is documentary (glob the injected root at runtime). **No v3.**
- [ ] **#3282 owns no engine/ApplicationManager edits** — it only consumes `engine(embed=True)`; the diff touches only `workflow_api/`, the registry, `SCHEMA.md`, and tests.
- [ ] `uv run pytest assetutilities/tests/workflow_api/ -v` green; full `assetutilities` suite shows no regression.
- [ ] Review artifacts posted under scripts/review/results/.

---

## Adversarial Review Summary

<!-- Re-scoped onto #3297 (Wave-1d). Prior Round-1 + Round-2 MAJOR findings addressed via the #3297 re-scope. New round PENDING — re-review after this revision. Not approval-ready until populated with no-MAJOR verdicts. Status stays draft. -->

### Round 1 (2026-06-27) — verdict: **MAJOR** (3 MAJOR + 1 design-blocker + 3 MINOR)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MAJOR** | M1 Step 1.5 tested the *file* path, not the in-memory `cfg` path; M2 `persist=False` guarding the whole `save_cfg` also suppresses `standardize_yml_data`; M3 `schema_version: 2` collides with digitalmodel's `2`. Design-blocker: `cfg[basename]` is not the result payload. MINORs: m1 pilot unverified, m2 error-envelope pre-`try` gap, m3 `input_hash` volatile set undefined. |
| Codex | UNAVAILABLE | rc=3 — `codex exec` stdin-hangs under Claude-Code Bash. Re-run pending via `env -u CLAUDECODE`. |
| Gemini | UNAVAILABLE | hung on interactive browser-auth; needs operator login. T3→T2 degrade. |

### Round 2 / Wave-1c (2026-06-28) — verdict: **MAJOR** (3 findings)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | **MAJOR** | F1 `persist=False` + "sandbox the result_folder" is NOT side-effect-free — `config_flag=True` discards the caller cfg before the tempdir overrides apply, and the engine is cwd-coupled (writes `<cwd>/logs`, `<cwd>/results`); F2 csv_utilities cited as a files demo but it is not a registry row and writes nothing; F3 `kind:files` `result_hash` hashed basenames only → tautological `reproducible: True`. |
| Codex | UNAVAILABLE | re-run pending via `env -u CLAUDECODE`. |
| Gemini | UNAVAILABLE | needs operator browser-auth. T3→T2 degrade. |

**How the Wave-1d re-scope resolves Rounds 1–2 (re-verified against the live `/mnt/local-analysis/assetutilities` checkout):**
- **R1-M1 / R1-design-blocker (in-memory path + `cfg[basename]`):** the cwd-coupling that broke the in-memory path is fixed **out of band by #3297's embed path**, which #3282 now calls; the result locator is the per-workflow declared `ResultLocator` (registry `result:`), not `cfg[basename]`.
- **R1-M3 (schema collision):** v2 is the additive superset; assetutilities adopts `schema_version: 2` + `invocation:` + the #3282-owned `result:`; #3295 reserves `request_schema`/`response_schema`. No v3.
- **R2-F1 (side-effect-freeness):** the runner calls the **#3297 embed path** `engine(cfg=..., embed=True, root_folder=mkdtemp(), log_to_file=False)` — which honors the caller cfg AND routes all result+log writes under the injected root AND emits no `.log` — then `rmtree`s the root. The retired `persist=False`/"sandbox the result_folder" mechanism is removed entirely; `engine.persist`/`save_cfg.persist` edits dropped from the change set. Test `test_run_workflow_writes_nothing_outside_tempdir`.
- **R2-F1 residual — basename derivation (Wave-1c MAJOR):** because the embed path honors the cfg, `file_name == "data_exploration"` (verified: `configure_overwrite_filenames` collapses `file_name` to `basename` under `overwrite.output: True`), so the router emits `data_exploration_FST*.csv` — **not** the registry's `input_FST*.csv`. `extract_result` now **globs the injected root** for the real emitted files instead of matching registry `outputs:` names. Tests `test_extract_result_globs_injected_root_real_filenames`.
- **R2-F2 (csv_utilities):** removed as a demo target everywhere; `kind:files` is demonstrated on **data_exploration**; csv_utilities retained only as evidence of the `cfg[basename]` design hole; `kind:in_memory` documented as supported-but-currently-unexercised.
- **R2-F3 (content-blind hash):** `kind:files` `result_hash` reads each emitted file in the tempdir and hashes `basename → sha256(content)` (sorted) — content-sensitive AND location-independent; `compute_reproducible` compares content hashes across two fresh embed roots. Tests `test_result_hash_files_content_sensitive` + `test_result_hash_files_location_independent`.

### Round 3 / Wave-1d re-scope (2026-06-28) — verdict: **MAJOR** (correctness) + **MINOR** (dependency)

| Lens | Verdict | Key findings → disposition |
|---|---|---|
| Correctness | **MAJOR** | `extract_result` globbed the `save_cfg` cfg-dump (`<file_name>.yml`, written by `engine.py:120` into `<root>/results/`), which embeds the tempdir abspath + a `start_time` datetime → poisoned the file list and made `result_hash` non-deterministic (R2-F3 *relocated* from "always True" to "spuriously False"). **FIXED:** `extract_result` now excludes `<file_name>.yml` (via `cfg_base.Analysis["file_name"]`) before listing/hashing; test `test_extract_result_excludes_save_cfg_dump`. Confirmed CLOSED by review: side-effect-freeness, basename mismatch (glob is correct), csv_utilities. |
| Dependency/determinism | **MINOR** | Confirmed determinism is now genuinely content-sensitive, #3297 dep prominent, in_memory honest, #3295 reservation respected. MINORs folded: (m1) "params avoids #88" over-claimed — only `cfg=<dict>` is example-load-free, and the example gap ≠ #88's `base_configs`; (m2) #3295 owns the `schema_version: 2` bump — sequencing now noted; (m3) "exactly 2 files" softened (router has a column-keyed branch). |

### Round 4 / Wave-1d confirm (2026-06-28) — verdict: **APPROVE**

Focused confirmation that the R3 cfg-dump MAJOR is closed: **APPROVE — no remaining defects.** Verified against real code: the exclusion keys off `cfg_base.Analysis["file_name"]` (the same key `save_cfg` uses at `ApplicationManager.py:373`) — strongest possible coupling; the non-determinism root (`start_time` datetime not handled by `standardize_yml_data`) is removed; `test_extract_result_excludes_save_cfg_dump` asserts both exclusion + cross-tempdir hash stability; degrades safely under a custom `output_directory`. Only the documented generalization-MINOR remains (yaml-output collision → clean fix = #3297 embed-mode cfg-dump suppression). 

**Overall result (planning): NO-MAJOR — surfaced to `status:plan-review`.** Implementation still gated behind (a) USER approval and (b) **#3297 landing first** (hard dependency) + **#3295 co-landing** for the registry bump.

---

## Risks and Open Questions

- **Risk — hard dependency on #3297.** #3282 cannot land until #3297's `engine(embed=True, root_folder=, log_to_file=)` is merged. Mitigation: the embed-path tests are written test-first and run green only after #3297 lands; the non-embed tests (envelope round-trip, hashing, build_cfg merge, registry schema) are independent and can be developed in parallel. Critical path: **#3297 → #3282 → #3283**. **Sequencing note (#3295, R3 MINOR-2):** #3295 owns the `schema_version: 2` superset reconciliation; #3282's registry edit (adopting `2` + `invocation:` + the #3282-owned `result:` descriptor) must land **after or with** #3295 to avoid a `workflows.yaml` meaning-collision / merge conflict. Treat #3295 as a co-dependency of #3282's registry change, not just #3297.
- **Risk — embed path must capture every write.** Side-effect-freeness depends on #3297's `configure_embed` routing **all** result + log writes under `root_folder` (verified in #3297: `analysis_root_folder = root_folder`; `configure_result_folder(root_folder)` → `<root>/results`; `log_to_file=False` → no `logs/`, no `.log`). Guardrail: `test_run_workflow_writes_nothing_outside_tempdir` snapshots the repo `examples/.../results/` dir before/after and asserts no change, plus asserts no `.log`/`logs/` anywhere. If any future router writes outside `result_folder` (a hardcoded path), that test catches it.
- **Risk — emitted filenames are cfg-derived, not registry-declared.** The embed path's `file_name` comes from `basename` (+ `overwrite.output`), so the real outputs (`data_exploration_FST*.csv`) differ from the registry `outputs:` (`input_FST*.csv`). Mitigation: `extract_result` **globs the injected root** and never matches registry names; the registry `outputs:` is documented as documentary (expected-count cross-check only). This is the explicit Wave-1c MAJOR fix.
- **Risk — result-locator coverage.** The `files` default covers the file-writing registry rows (data_exploration, excel_utilities, zip_utilities, word_utilities, visualization, …). `in_memory` is opt-in per row and **currently unexercised** (no registry row exposes data via `cfg[basename]`). #3282 demonstrates `files` on `data_exploration` and documents the convention. Scope boundary, not a defect.
- **Risk — `save_cfg` cfg-dump exclusion (R3 MAJOR fix) and its generalization edge.** `extract_result` excludes `<file_name>.yml` (the `save_cfg` dump) so it cannot poison the file list/hash. This is unambiguous for the `data_exploration` demo (outputs are `*.csv`). **Generalization edge:** a future `kind:files` row whose *genuine* output is itself `<file_name>.yml` (e.g. a `yaml_utilities`-style workflow) would be wrongly excluded. **Clean general fix (recommended #3297 refinement):** have the #3297 embed path **skip the `save_cfg` cfg-dump write entirely** in embed mode (an embedder reads results via `extract_result` and never needs the persisted cfg YAML) — then `extract_result` globs a clean dir with no exclusion needed and no collision risk. The #3282-side exclusion remains as belt-and-suspenders. Flagged to #3297; not a blocker for the `data_exploration` demo scope.
- **Risk — reproducible double-run cost/side effects.** `verify_reproducible=True` runs the embed path twice; each run writes only into its **own** `mkdtemp` root (rmtree'd), never the repo/example dirs. Default is `False` (→ `reproducible=None`) so the common path pays nothing. The formal cross-run volatile-field key-allowlist is #3283's (Wave 2); #3282's content-hash `result_hash` is sufficient — and genuinely content-sensitive — for the in-process double-run comparison.
- **Risk — registry reconciliation overlap with #3295.** #3282 lands `schema_version: 2` + `invocation:` + per-row `result:` (all additive/optional). #3295 owns the formal cross-registry reconciliation and the `request_schema`/`response_schema` reservation. If #3295 renames a field, a fast follow-up adjusts; the `result:` shape is #3282-owned and stable.
- **Risk — dependency weight.** `ResultEnvelope` is a stdlib `dataclass` (not Pydantic) to avoid a hard dep in the shared lib; serialization via explicit `to_dict`/`from_dict`. worldenergydata may later adapt it to its Pydantic surface (#3286).
- **Risk — wheel packaging ([assetutilities #88]).** `build_cfg(row, params)` loading a packaged example input hits the example-not-in-wheel gap. Mitigation: the **primary path is the params dict** (`run_workflow(id, params=<dict>)` / `run_workflow(cfg=<dict>)`), needing no packaged example; the example-load path is a convenience for in-repo runs. Note the dependency; do not block.
- **Risk — slow cold import (~30 s), NOT a hang.** `engine.py` imports `WebScraping`/`TextAnalytics`/`DownloadDataFromURL` at module load (measured ~29.4 s, 2026-06-28); the first `run_workflow` call inherits it. Mitigation: implementation re-verifies the embed path runs green under the repo pytest harness; if unacceptable, file a follow-on to lazy-import the heavy routers. Not a blocker.

**Open Questions:** none outstanding. Schema version (v2 superset, no v3), `provenance.code_version` shape (`{package_version, git_sha}`), and file-output `result_hash` (over **file CONTENTS**: sorted basename → sha256(content)) are settled. The side-effect-freeness mechanism is now the **#3297 embed path** (`engine(embed=True, root_folder=, log_to_file=False)`), not a persist/sandbox hack; csv_utilities is removed as a demo target; the basename-derivation residual is fixed by globbing the injected root.

---

## Complexity: T2

**T2** — one new small package (3 source files) + a schema doc + additive v2-superset registry fields, TDD throughout, consuming the #3297 embed path with **zero** engine/ApplicationManager edits owned here. Flagged for **T3-depth review** because it is the foundational contract the rest of epic #3281 inherits, and because it depends on the T3 #3297 change.
