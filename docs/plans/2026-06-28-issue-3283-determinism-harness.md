# Plan for #3283: wf-api(ecosystem) — determinism harness (golden-test template + provenance stamp + volatile-field KEY-allowlist + golden-refresh procedure)

> **Status:** draft
> **Complexity:** T3 (cross-repo harness — assetutilities `workflow_api` `golden.py`/`provenance.py` + a control-plane refresh doc; the determinism guarantee the whole #3281 epic rests on; 3-provider review)
> **Date:** 2026-06-28 (Wave-3 re-scope after the Wave-2 MAJOR — see "Revision note")
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3283
> **Epic:** https://github.com/vamseeachanta/workspace-hub/issues/3281
> **Depends on:** #3297 (engine embeddability) → #3282 (ResultEnvelope + `run_workflow` + `result_hash` + parameterized `code_version`) → **#3283 (this)**. The harness **self-test** needs only #3282 (a bare single-registry assetutilities id). The digitalmodel **buckling reference golden is OWNED BY #3285** (not #3283) and additionally gates on **#3284** (cross-repo `repo:id@version` resolution) and transitively **#3307** (digitalmodel's own engine embed-port). #3283 ships only the consuming template.
> **Client:** N/A — no wiki content touched
> **Lane:** lane:codex (test/infra harness code; per the issue's `lane:codex` label)
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3283-claude.md | ...-codex.md | ...-gemini.md

---

## Revision note (2026-06-28, Wave-3 — re-scope after the Wave-2 MAJOR)

The Wave-2 plan returned **MAJOR (1)**. Two coupled defects, both now fixed:

1. **MAJOR — the reference golden used a CROSS-REPO id without gating on its resolver.** Wave-2's `BUCKLING_WF = "digitalmodel:buckling-parametric"` is a `repo:id` cross-repo workflow id. Resolving `repo:id[@version]` to a runnable workflow is **owned by #3284** (the discovery manifest + `latest` resolver; the reference resolver is `deckhand/src/deckhand/capability_smoke.py` `_parse_ref` `:117` / `resolve_workflow` `:167`). Wave-2 asserted `run_workflow("digitalmodel:buckling-parametric")` would resolve with no dependency on #3284 — unsound. **Fix:** the harness **self-test** uses a **bare single-registry id** (`data_exploration`, resolved inside assetutilities' own registry by #3282's `run_workflow` — **no #3284**). The **digitalmodel buckling reference golden** is the one that uses the cross-repo id; it is therefore explicitly gated on **#3284** (resolver) **and #3285** (row/route/golden) — and, since it runs through digitalmodel's OWN engine, transitively on **#3307**.

2. **MAJOR — #3283 was creating the buckling registry row's golden + determinism test that #3285 owns.** Wave-2 listed `digitalmodel/tests/structural/goldens/<buckling>.envelope.json` + `test_<buckling>_determinism.py` as **#3283 deliverables** ("gated on #3285"). But **#3285 OWNS creating the buckling registry row + engine route + reference golden** — its own acceptance criterion reads "*Each has … a committed golden test (Child 2 harness)*", where Child 2 = #3283. So #3283 is the **harness #3285 consumes**, not the producer of digitalmodel's golden. **Fix:** the digitalmodel buckling golden + test are **removed from #3283's Files to Change**; they appear here only as an **illustrative consumer example** of `golden_workflow_test`, authored by #3285. #3283 owns the template, the KEY-allowlist, `stamp_provenance`, the refresh doc, and a self-test on an assetutilities row.

Carried forward from the Wave-2 fixes (already-correct, retained verbatim):
- **No value heuristics.** The volatile-field spec is a **KEY-ALLOWLIST keyed by dotted key-name only**; values are never inspected to decide inclusion. (Wave-1 MAJOR fix — kept.)
- **`result_hash` is #3282-owned — not redefined.** #3283 **CONSUMES** `envelope.determinism.result_hash` verbatim and adds **no second hashing function**. (Wave-1 MAJOR fix — kept.)
- **The golden test hashes the REAL emitted artifact via `run_workflow`** — no fabricated-envelope path. (Wave-1 MAJOR fix — kept.)

What #3283 OWNS after this re-scope (narrow, non-overlapping):
- **`golden_workflow_test(workflow_id, golden_path, ...)`** — the pytest template that runs `run_workflow`, compares the emitted envelope against a committed golden, and fails on drift.
- **`stamp_provenance(input_hash, *, package_name="<adopter>", standard_revisions, data_as_of)`** — the canonical reusable provenance assembler (codifies the #3282 provenance SHAPE; `code_version` is **parameterized** per #3282).
- **The volatile-field KEY-ALLOWLIST** (`GOLDEN_VOLATILE_KEYS`) — dotted envelope key-names the golden comparison ignores, applied by name, never by value.
- **A documented golden-refresh / re-sanction procedure** (per the BSEE re-sanction lesson).
- **A harness self-test** against the already-callable assetutilities `data_exploration` row (proves the template without #3284/#3285).

What #3283 does NOT own (consumed as specified, not redesigned): `result_hash`, `reproducible`, `input_hash`, the `result:` registry descriptor, the embed path, the `ResultEnvelope` field set (all #3282/#3297); cross-repo `repo:id@version` resolution (#3284); the digitalmodel buckling registry row + engine route + its committed golden (#3285).

---

## Resource Intelligence Summary

### Existing repo code (verified 2026-06-28)

- **`assetutilities` `workflow_api` — DOES NOT EXIST YET.** `ls /mnt/local-analysis/assetutilities/src/assetutilities/workflow_api` → `No such file or directory`. It is greenfield, created by #3282. #3283 adds two new modules into that package (`golden.py`, `provenance.py`) + a tests dir. **Hard dependency:** #3283 cannot land before #3282 (which cannot land before #3297). Critical path: **#3297 → #3282 → #3283**.
- **`assetutilities/src/assetutilities/engine.py` (4427 bytes) + `common/ApplicationManager.py` EXIST.** These are what #3297's embed path edits and #3282's `run_workflow` drives. #3283 touches **neither** — it calls `run_workflow` (a black box over the assetutilities engine). (Per-repo engines: assetutilities engine = #3297; digitalmodel/assethold have their OWN engines + embed-ports #3307/#3308 — only relevant to #3283 transitively, via the #3285-owned digitalmodel reference golden.)
- **`/mnt/local-analysis/digitalmodel/src/digitalmodel/structural/buckling_parametric.py` — the cleanest reference workflow.** Verified line-level:
  - `_round(x, n=4)` (`:97`) — every emitted numeric is rounded at emit time (e.g. `utilization` `:146`, `critical_stress_mpa` `:147`, `safety_factor` `:148`). The float-stability convention is already *inside the producer*, so the harness needs no float-tolerance step (a second reason the deleted Wave-1 float-tolerance hasher was redundant).
  - `write_outputs(... timestamp=None)` (`:232`) emits `results.json`; the **only** volatile field is `meta.generated_at`, written **only** `if timestamp is not None` (`:278-279`). With the default `timestamp=None` the emission is clock-free / byte-stable — why buckling is the natural reference. `STANDARD = "DNV-RP-C201"` (`:34`).
- **`/mnt/local-analysis/digitalmodel/docs/registry/workflows.yaml` — `schema_version: 2` (`:9`), top-level `invocation: "uv run python -m digitalmodel {input}"` (`:10`).** Carries `elastic-buckling` (`:410`) and `plate-buckling` (`:477`) rows but **NO `buckling_parametric` row** (`grep buckling_parametric` → none). So the parametric sweep producer is **not yet** a `run_workflow`-callable workflow; making one callable + writing its golden is exactly **#3285's** job. The reference golden is therefore #3285-owned, not #3283's.
- **`/mnt/local-analysis/deckhand/src/deckhand/capability_smoke.py` (13268 bytes) — the cross-repo id resolver (the #3284 contract this plan must respect).** Verified: `OFFLINE_RUNTIMES` (`:42`), `_parse_ref` parsing `<repo>:<workflow-id>[@<version>]` (`:117`), `_select_version` latest-stable resolution (`:146`), `resolve_workflow` "never raises — unresolvable ref returns" with reason "malformed ref" (`:167`-`:194`). This is why a `digitalmodel:buckling-parametric` reference id depends on #3284 wiring this resolver into a manifest `run_workflow` can consume cross-repo. A **bare single-registry id** (the self-test path) avoids it.
- **`/mnt/local-analysis/digitalmodel/src/digitalmodel/asset_integrity/assessment/ffs_coordinator.py` — `FFSAssessmentResult` (`:61`) with `to_dict()` (`:90`).** A flat numeric/string JSON summary with **no timestamp or path field** — the documented fallback reference workflow (also a #3285 target).
- **`/mnt/local-analysis/digitalmodel/src/digitalmodel/compare_tool/workflow.py` — `router(cfg)` (`:15`).** Baseline-vs-variant diff: per-source `delta_column`/`ratio_column` (`:36-41`), `max_abs_delta` per label (`:42-43`, `:55`). Prior art the issue says to "reuse for golden comparison". The golden mismatch-diff borrows its keyed-numeric-delta + `max_abs_delta` shape to *describe what drifted* on failure — **human debugging only; the PASS/FAIL verdict is `result_hash` string-equality, never a value-delta heuristic.**
- **`/mnt/local-analysis/digitalmodel/tests/hydrodynamics/diffraction/benchmarks/golden_capture.py` (2673 bytes) — the proven golden-refresh pattern (#501).** A byte-identity, no-tolerance golden over OrcaWave **input** text with a `capture`/`main()` regen entry-point + docstring documenting the refresh command. The template's capture/refresh ergonomics mirror this shape. (It is NOT a `ResultEnvelope` golden over a workflow *result* — the gap #3283 fills.)
- **`/mnt/local-analysis/digitalmodel/src/digitalmodel/citations/`** (`schema.py`/`registry.py`/`resolver.py`, the calc-citation pilot). `Citation` (`code_id`/`publisher`/`revision`) is the source shape for `provenance.standard_revisions` that `stamp_provenance` assembles.

### Standards

Not applicable — harness/infra code, not an engineering calculation. The reference workflow covers `DNV-RP-C201` (buckling) but introduces no new standards-derived constants; `provenance.standard_revisions` *records* citations, it does not derive them. No `Citation` emission required by this plan.

| Standard | Status | Source |
|---|---|---|
| DNV-RP-C201 (reference workflow only) | recorded via provenance, not derived | `buckling_parametric.py:34` `STANDARD = "DNV-RP-C201"` |

### LLM Wiki pages consulted

None — contract/infra work, no domain knowledge added. (`Client: N/A`.) `provenance.standard_revisions` references the calc-citation wiki-slug mechanism but adds no page.

### Documents consulted

- Epic [#3281](https://github.com/vamseeachanta/workspace-hub/issues/3281) — gap #3 ("Determinism is aspirational… no golden baselines, no byte-identical assertions, no provenance stamp, no result hash") is this issue's exact charter.
- **[#3282 plan](2026-06-27-issue-3282-resultenvelope-run-workflow.md)** — the upstream contract this harness consumes. `from assetutilities.workflow_api import run_workflow, ResultEnvelope`. `run_workflow(workflow_id=None, params=None, cfg=None, verify_reproducible=False) -> ResultEnvelope` (`:278`) via the #3297 embed path. `ResultEnvelope` = **stdlib dataclass (NO Pydantic)**. **#3282 OWNS `determinism.result_hash` (kind:files = sorted-basename → sha256(file CONTENTS), EXCLUDING the `save_cfg` dump; kind:in_memory = canonical value hash), `reproducible`, `input_hash`, the `result:` descriptor, AND a PARAMETERIZED `code_version(package_name="assetutilities")` (`:172` — adopters pass their own package).** Demo row is **`data_exploration`** (a real registry row writing 2 CSVs; `kind:files`). No-MAJOR at `status:plan-review`, `lane:claude`, owner-unapproved.
- **[#3297 plan](2026-06-28-issue-3297-engine-embeddability.md)** — PREREQ (transitive via #3282). Canonical `configure_embed(self, cfg, basename, root_folder, log_to_file=False)` (positional; **NO `library_name`** — that is only on the regular `configure()`); sets `analysis_root_folder`, log folders, and `cfg["_config_dir_path"]=root`. `engine(cfg=..., embed=True, root_folder=, log_to_file=False)` is the embed path; default (no root) byte-identical. #3283 never calls `configure_embed` directly — it is behind `run_workflow`.
- **[#3295 plan](2026-06-28-issue-3295-registry-schema-v2-reconcile.md)** — registry `schema_version: 2` additive superset; required top-level `invocation:`; `request_schema`/`response_schema` RESERVED structured; `result:` descriptor `{kind: in_memory|files}`. The reference golden's workflow row lives under this schema.
- **[#3284 plan](2026-06-28-issue-3284-discovery-manifest.md)** — **OWNS cross-repo id resolution.** `workflow_id = "repo:id@version"` + a `latest` resolver (D4); `routing_id = "repo:id"` (`:150`); `latest_by_routing_id` (`:172`). The manifest field-set is chosen to round-trip through `deckhand/src/deckhand/capability_smoke.py` `resolve_workflow`. **This is the dependency a `digitalmodel:buckling-parametric` reference id incurs.** `status:plan-review`, `lane:claude`.
- **[#3285](https://github.com/vamseeachanta/workspace-hub/issues/3285)** (OPEN, `status:needs-plan`, `lane:codex`) — "wf-api(digitalmodel): adopt ResultEnvelope + schemas + goldens (FFS, buckling, mooring, wall-thickness)". **OWNS creating the buckling registry row + engine route + committed golden test (its AC: "Each has … a committed golden test (Child 2 harness)" — Child 2 = #3283).** #3283 is the harness #3285 consumes; #3283 does NOT author digitalmodel's golden.
- **[#3307](https://github.com/vamseeachanta/workspace-hub/issues/3307)** — digitalmodel engine embed-port (mirrors #3297 for digitalmodel's OWN forked engine + ApplicationManager). Transitive prereq of the #3285 reference golden running through `run_workflow`. Not a direct #3283 dependency.
- `.claude/rules/calc-citation-contract.md` — `Citation` sidecar shape reused for `provenance.standard_revisions` (`source_sibling` required; default `generic` during digitalmodel migration).
- MEMORY: BSEE golden-baseline re-sanction lesson (`project_julia_field_economics_demo`, `project_bsee_ogor_refresh_mechanics`) — "golden baseline needs RE-SANCTIONING after refresh"; drives the documented refresh-requires-sign-off requirement.

### Gaps identified

- No `golden_workflow_test(workflow_id)` helper / template anywhere; no committed golden *envelope* for any `run_workflow`-callable workflow.
- No volatile-field KEY-ALLOWLIST spec (the Wave-1 attempt was a value heuristic — defective).
- No reusable `stamp_provenance` assembler (the #3282 plan inlines a minimal `provenance(ihash)` + parameterized `code_version(package_name)`; #3283 generalizes the SHAPE without changing it).
- No documented golden-refresh / re-sanction procedure for `ResultEnvelope` goldens.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3283` — OPEN, `status:needs-plan`, `lane:codex` — this issue
- `#3282` — `status:plan-review`, `lane:claude` — hard dependency (no-MAJOR, owner-unapproved)
- `#3284` — `status:plan-review`, `lane:claude` — cross-repo id resolution dependency for the reference golden
- `#3285` — OPEN, `status:needs-plan`, `lane:codex`, title "wf-api(digitalmodel): adopt ResultEnvelope + schemas + goldens (FFS, buckling, mooring, wall-thickness)" — OWNS the buckling row/route/golden
- `#3281` — OPEN — parent epic

**File existence** (`ls`/`grep` 2026-06-28):
- EXISTS: `digitalmodel/src/digitalmodel/structural/buckling_parametric.py` (`_round` `:97`; `write_outputs` `:232`; `if timestamp is not None` `:278`; `STANDARD` `:34`)
- EXISTS: `digitalmodel/src/digitalmodel/asset_integrity/assessment/ffs_coordinator.py` (`FFSAssessmentResult` `:61`; `to_dict` `:90`)
- EXISTS: `digitalmodel/src/digitalmodel/compare_tool/workflow.py` (`router` `:15`; `max_abs_delta` `:42`/`:55`)
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/golden_capture.py` (refresh-pattern precedent)
- EXISTS: `digitalmodel/docs/registry/workflows.yaml` (`schema_version: 2` `:9`; rows `elastic-buckling` `:410`, `plate-buckling` `:477`; **no** `buckling_parametric` row)
- EXISTS: `deckhand/src/deckhand/capability_smoke.py` (`_parse_ref` `:117`, `resolve_workflow` `:167` — the #3284 cross-repo resolver)
- EXISTS: `assetutilities/src/assetutilities/engine.py`, `common/ApplicationManager.py` (#3297/#3282 surface; #3283 doesn't edit)
- MISSING (created here, into the #3282 package): `assetutilities/src/assetutilities/workflow_api/golden.py`, `.../provenance.py`, `assetutilities/tests/workflow_api/test_golden.py`, `.../test_provenance.py`, `.../goldens/data_exploration.envelope.json`
- MISSING (#3282 creates; #3283 imports): `assetutilities/src/assetutilities/workflow_api/{__init__,runner,envelope}.py`
- **NOT created here — #3285-owned:** `digitalmodel/tests/.../goldens/buckling_parametric.envelope.json`, `digitalmodel/tests/.../test_buckling_determinism.py`

**Gap proofs** (2026-06-28):
- `grep -rln "result_hash" assetutilities/src digitalmodel/src` → **ZERO** (no `result_hash` exists yet; arrives with #3282 — #3283 must NOT add a second one).
- `grep -rln "golden_workflow_test\|stamp_provenance" digitalmodel assetutilities` → **ZERO** (greenfield).
- `ls assetutilities/src/assetutilities/workflow_api` → **absent** (the package #3282 creates).
- `grep buckling_parametric digitalmodel/docs/registry/workflows.yaml` → **none** (parametric sweep not yet `run_workflow`-callable → #3285).

### Step 1.5 — Reproduction

**Claim under test (issue body):** "digitalmodel today has no golden baselines and no byte-identical assertions… no provenance stamp, no result hash."

```
$ cd /mnt/local-analysis/digitalmodel
$ grep -rln "result_hash" src | grep -v __pycache__         → ZERO
$ grep -n "_round\|if timestamp is not None" src/digitalmodel/structural/buckling_parametric.py
   97: def _round(x: float, n: int = 4) -> float:
  278: if timestamp is not None:        # generated_at omitted by default → clock-free emission
$ grep -n "schema_version\|buckling_parametric" docs/registry/workflows.yaml
    9: schema_version: 2
   (no buckling_parametric row)
$ grep -n "_parse_ref\|resolve_workflow" /mnt/local-analysis/deckhand/src/deckhand/capability_smoke.py
  117: def _parse_ref(ref: str)            # parses <repo>:<workflow-id>[@<version>]
  167: def resolve_workflow(...)           # cross-repo id resolver (the #3284 contract)
```
- Reproduced at: 2026-06-28.
- **Result (the literal claim is PARTIALLY true):** digitalmodel has a byte-identity golden only for **OrcaWave input-file emission** (`golden_capture.py`, #501), and "golden NUMBER" tests for structural/FFS worked examples — but **NO result-hash / provenance-stamped determinism golden over a `ResultEnvelope` returned by `run_workflow`**. That real gap is this issue's charter.
- **Behavioral assertions in this plan that CANNOT be reproduced yet (and why — N/A is a dependency gate, not an omission):**
  - `run_workflow(...)` does not exist (package absent — **#3282**).
  - Cross-repo resolution of `digitalmodel:buckling-parametric` does not exist (the manifest/resolver wiring is **#3284**; the resolver lib `capability_smoke.py` exists but is not wired into `run_workflow`).
  - A `run_workflow`-callable buckling workflow + its golden does not exist (no registry row + no engine route + no committed golden — **#3285**, running through digitalmodel's embed-port **#3307**).
  - So the end-to-end "re-running `digitalmodel:buckling-parametric` yields an identical `result_hash`" demonstration is **N/A until #3282 + #3284 + #3285 land**. Until then #3283 is proven by (i) unit tests over `stamp_provenance` + the golden-diff logic with synthetic envelopes, and (ii) a self-test against the already-callable assetutilities `data_exploration` **bare single-registry id** once #3282 lands (needs neither #3284 nor #3285).

(Distinct sources: issue body + #3282 plan + #3297 plan + #3295 plan + #3284 plan + #3285 issue + #3307 + buckling_parametric.py + ffs_coordinator.py + compare_tool/workflow.py + golden_capture.py + capability_smoke.py + digitalmodel registry + calc-citation rule + grep gap-proofs = 15+.)

---

## Artifact Map

| Artifact | Path | Owner |
|---|---|---|
| This plan | docs/plans/2026-06-28-issue-3283-determinism-harness.md | #3283 |
| Provenance assembler | `assetutilities/src/assetutilities/workflow_api/provenance.py` | #3283 |
| Golden template + volatile KEY-allowlist + capture/diff | `assetutilities/src/assetutilities/workflow_api/golden.py` | #3283 |
| Package export (coordinate with #3282's `__init__.py`) | `assetutilities/src/assetutilities/workflow_api/__init__.py` | #3282 owns file; #3283 adds export lines |
| Harness tests | `assetutilities/tests/workflow_api/test_provenance.py`, `test_golden.py` | #3283 |
| Harness self-test golden (assetutilities `data_exploration`, bare single-registry id) | `assetutilities/tests/workflow_api/goldens/data_exploration.envelope.json` | #3283 |
| Refresh/re-sanction doc | `docs/standards/2026-06-28-determinism-golden-refresh.md` | #3283 |
| Plan reviews | scripts/review/results/2026-06-28-plan-3283-{claude,codex,gemini}.md | #3283 |
| Plan index | docs/plans/README.md | #3283 |
| **digitalmodel buckling golden envelope** | `digitalmodel/tests/structural/goldens/buckling_parametric.envelope.json` | **#3285 (NOT #3283)** |
| **digitalmodel buckling determinism test** | `digitalmodel/tests/structural/test_buckling_determinism.py` | **#3285 (NOT #3283)** |

> **Not owned here:** `assetutilities/src/assetutilities/workflow_api/{runner,envelope}.py` (#3282), the engine embed path (#3297), the cross-repo resolver wiring (#3284), and the digitalmodel buckling row/route/golden (#3285). #3283 imports `run_workflow`, `ResultEnvelope`, `code_version`, and the emitted `determinism.result_hash`; it does not edit them. The buckling rows in this plan's pseudocode are an **illustrative consumer example** of `golden_workflow_test` for #3285 to author, not a #3283 deliverable.

---

## Deliverable

A determinism golden-test harness added to the `assetutilities.workflow_api` package (created by #3282), comprising:
1. **`golden_workflow_test(workflow_id, golden_path, *, params=None, cfg=None, pin_structural=False, extra_volatile_keys=())`** — a pytest helper that calls `run_workflow`, asserts the emitted envelope's `determinism.result_hash` equals the committed golden's, and (optionally) asserts pinned non-volatile envelope fields, ignoring a documented KEY-allowlist of volatile keys. It reuses the `compare_tool` keyed-delta shape to *describe* drift on failure (human debugging) without using value heuristics for the verdict.
2. **`stamp_provenance(input_hash, *, package_name="assetutilities", standard_revisions=None, data_as_of=None) -> dict`** — the canonical reusable provenance assembler codifying the #3282 provenance shape. **`code_version` is parameterized** (`code_version(package_name)` per #3282 `:172`) so each adopter (digitalmodel, assethold, …) stamps its OWN package version.
3. **The volatile-field KEY-ALLOWLIST** — an explicit `GOLDEN_VOLATILE_KEYS` set of dotted envelope key-names the golden comparison ignores, applied **by key name only, never by value sniffing**.
4. **A documented golden-refresh / re-sanction procedure** (`docs/standards/2026-06-28-determinism-golden-refresh.md`) — what `REGEN_GOLDENS=1` does, what re-sanctioning requires, and owner sign-off.

Proven by: the harness self-test against the assetutilities `data_exploration` **bare single-registry id** (available once #3282 lands; no #3284/#3285). The digitalmodel buckling reference golden + its determinism test are authored by **#3285** consuming this template (gated on #3284 + #3307).

---

## Pseudocode

```python
# ── provenance.py ─────────────────────────────────────────────
# Canonical reusable provenance assembler. Codifies the #3282 provenance SHAPE; does not change it.
# code_version is #3282-owned and PARAMETERIZED — adopters pass their own package_name.
from assetutilities.workflow_api import code_version    # #3282 :172 -> code_version(package_name="assetutilities")

def stamp_provenance(input_hash, *, package_name="assetutilities",
                     standard_revisions=None, data_as_of=None) -> dict:
    return {
        "code_version": code_version(package_name),             # adopter's package version+git_sha; NOT hardcoded
        "standard_revisions": list(standard_revisions or []),   # Citation dicts (code_id/publisher/revision)
        "data_as_of": data_as_of,                               # None for pure-calc workflows (buckling)
        "input_hash": input_hash,                               # #3282-owned value; reused verbatim, never recomputed
    }
# Coordination seam: if #3282 lands with an inline provenance() body, #3283 extracts it INTO stamp_provenance
# without altering the emitted dict; #3282 still OWNS the field set + the runner call-site.

# ── golden.py ─────────────────────────────────────────────────
# THE VOLATILE-FIELD SPEC = a KEY-ALLOWLIST of DOTTED KEY-NAMES. Never inspects values.
GOLDEN_VOLATILE_KEYS = frozenset({
    "provenance.code_version.git_sha",         # changes every commit
    "provenance.code_version.package_version", # changes on release bump
    "provenance.data_as_of",                   # data-refresh dependent (record, don't pin) -- opt-in to pin per golden
    "determinism.reproducible",                # a measured bool/None, not a fixed expectation
})
# A key is volatile IFF its dotted name is in this set (or per-golden extra_volatile_keys). A future volatile
# key is added by NAME, never by a "looks like a date/path" heuristic. The result PAYLOAD is never value-stripped
# -- it rides the #3282 result_hash, which already excludes the save_cfg dump and is content-based.

def _prune_volatile(d: dict, volatile_keys) -> dict:
    # recursively drop dotted keys present in `volatile_keys`; leave everything else byte-for-byte.
    ...

def capture_golden(envelope, golden_path):
    snapshot = {"workflow_id": envelope.workflow_id,
                "result_hash": envelope.determinism["result_hash"],   # #3282-owned, consumed not recomputed
                "status": envelope.status,
                "envelope_pruned": _prune_volatile(envelope.to_dict(), GOLDEN_VOLATILE_KEYS)}
    Path(golden_path).write_text(json.dumps(snapshot, indent=2, sort_keys=True))

def diff_results(golden_pruned, current_pruned):
    # reuse compare_tool keyed-delta + max_abs_delta shape to DESCRIBE what drifted (debugging aid only,
    # NOT the verdict; it is the failure message body).
    ...

def golden_workflow_test(workflow_id, golden_path, *, params=None, cfg=None,
                         pin_structural=False, extra_volatile_keys=()):
    env = run_workflow(workflow_id, params=params, cfg=cfg)            # #3282 entrypoint -- REAL emission
    assert env.status == "ok", f"{workflow_id} errored: {env.warnings}"
    if os.environ.get("REGEN_GOLDENS") == "1":
        capture_golden(env, golden_path)
        pytest.skip(f"golden {golden_path} refreshed -- re-sanction + owner sign-off required before commit")
    golden = json.loads(Path(golden_path).read_text())
    # (1) LOAD-BEARING determinism assertion -- string equality of the #3282-owned result_hash:
    assert env.determinism["result_hash"] == golden["result_hash"], \
        diff_results(golden["envelope_pruned"].get("result"),
                     _prune_volatile(env.to_dict(), GOLDEN_VOLATILE_KEYS).get("result"))
    # (2) OPTIONAL structural pin -- only the non-volatile keys, excluded BY NAME:
    if pin_structural:
        vk = GOLDEN_VOLATILE_KEYS | frozenset(extra_volatile_keys)
        assert _prune_volatile(env.to_dict(), vk) == golden["envelope_pruned"]
    return env

# ── harness SELF-TEST (ships with #3283; needs ONLY #3282; BARE single-registry id) ──
def test_self_test_data_exploration_deterministic():
    # 'data_exploration' is a bare assetutilities registry id -- resolved by #3282's run_workflow inside
    # assetutilities' OWN registry. NO repo: prefix => NO #3284 cross-repo resolution needed.
    golden_workflow_test("data_exploration",
                         Path(__file__).parent / "goldens" / "data_exploration.envelope.json")

# ── digitalmodel buckling reference test (ILLUSTRATIVE -- AUTHORED BY #3285, NOT #3283) ──
# Shown so #3285 sees the consume pattern. #3283 does NOT commit this file or its golden.
# REQUIRES: #3284 (resolve the cross-repo id) + #3285 (the row/route/golden) + #3307 (digitalmodel embed path).
BUCKLING_WF = "digitalmodel:buckling-parametric"   # CROSS-REPO id => needs #3284 resolver (capability_smoke.py)
def test_buckling_is_deterministic():              # <-- lives in digitalmodel/tests, owned by #3285
    golden_workflow_test(BUCKLING_WF, BUCKLING_GOLDEN, params=DEFAULT_SHIP_PLATE_PARAMS)
def test_buckling_input_change_flips_hash():
    base    = run_workflow(BUCKLING_WF, params=DEFAULT_SHIP_PLATE_PARAMS).determinism["result_hash"]
    mutated = run_workflow(BUCKLING_WF, params=THICKER_PLATE_PARAMS).determinism["result_hash"]
    assert base != mutated
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `assetutilities/src/assetutilities/workflow_api/provenance.py` | `stamp_provenance` (parameterized `code_version(package_name)`; #3282 provenance SHAPE) |
| Create | `assetutilities/src/assetutilities/workflow_api/golden.py` | `golden_workflow_test` template, `GOLDEN_VOLATILE_KEYS` (dotted KEY-allowlist), `_prune_volatile`, `capture_golden`, `diff_results` |
| Modify | `assetutilities/src/assetutilities/workflow_api/__init__.py` | export `stamp_provenance`, `golden_workflow_test`, `GOLDEN_VOLATILE_KEYS` (coordination seam with #3282) |
| Create | `assetutilities/tests/workflow_api/test_provenance.py` | provenance assembler TDD |
| Create | `assetutilities/tests/workflow_api/test_golden.py` | template + KEY-allowlist + self-test-on-`data_exploration` TDD |
| Create | `assetutilities/tests/workflow_api/goldens/data_exploration.envelope.json` | harness self-test golden (#3282-callable bare id; no #3284/#3285) |
| Create | `docs/standards/2026-06-28-determinism-golden-refresh.md` | golden-refresh + re-sanction procedure (owner sign-off) |
| Update | `docs/plans/README.md` | refresh this plan's index row |

> **Explicitly NOT in #3283's Files to Change (owned by #3285):** `digitalmodel/tests/structural/goldens/buckling_parametric.envelope.json` and `digitalmodel/tests/structural/test_buckling_determinism.py`. #3285 authors these by consuming #3283's `golden_workflow_test`. #3283 does not touch digitalmodel.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_stamp_provenance_shape | returns `{code_version{package_version,git_sha}, standard_revisions, data_as_of, input_hash}` | `stamp_provenance("ih")` | all four keys; `code_version` has both subkeys |
| test_stamp_provenance_package_name_parameterized | `code_version` reflects the passed `package_name`, not a hardcoded assetutilities version | `stamp_provenance("ih", package_name="digitalmodel")` | `code_version.package_version` is digitalmodel's version (mock importlib.metadata) |
| test_stamp_provenance_passes_input_hash_verbatim | reuses #3282 `input_hash` unchanged (never recomputes) | `input_hash="sha256:abc"` | `provenance["input_hash"]=="sha256:abc"` |
| test_stamp_provenance_standard_revisions | a DNV-RP-C201 Citation dict lands under `standard_revisions` | one Citation dict | list contains that entry |
| test_code_version_git_sha_none_off_checkout | `git_sha` is `None` off a git work-tree, both keys still present | simulated non-git cwd | `{"package_version": str, "git_sha": None}` |
| test_volatile_keys_is_key_allowlist_not_value_heuristic | a result VALUE that string-renders date-like or path-like is **NOT** stripped (no value sniffing) | envelope whose `result` has `"governing":"2024-01-01"` and `"key":"a/b/c"` | both values survive pruning; only KEY-listed fields drop |
| test_prune_volatile_drops_git_sha_by_name | `provenance.code_version.git_sha` removed by dotted-name match | two envelopes differing only in `git_sha` | pruned dicts equal |
| test_prune_volatile_keeps_result_payload | the `result` payload is never value-pruned | envelope with rich result | result identical after prune |
| test_golden_pass_on_matching_result_hash | matching `result_hash` → passes, returns envelope | envelope whose `result_hash`==golden | no failure |
| test_golden_fail_on_result_hash_drift | drifted `result_hash` → AssertionError carrying keyed-delta message | golden vs mutated result | error message names the drifted key(s) |
| test_golden_verdict_is_hash_not_value_delta | verdict is driven by `result_hash` equality, not a value delta | crafted envelopes | pass/fail driven by hash only |
| test_regen_goldens_env_writes_and_skips | `REGEN_GOLDENS=1` rewrites the golden + `pytest.skip` (re-sanction gate) | env var set | golden file written; test skipped |
| test_capture_golden_prunes_volatile | captured snapshot prunes `git_sha`/`package_version` from `envelope_pruned` but keeps `result_hash` | one envelope | snapshot has `result_hash`, no `git_sha` |
| test_self_test_data_exploration_deterministic *(needs #3282)* | `golden_workflow_test("data_exploration", ...)` green via REAL `run_workflow` on a BARE single-registry id | data_exploration row | `result_hash`==committed golden |

> **Dependency gates on tests:** the first 13 rows (provenance + KEY-allowlist + golden-diff over synthetic envelopes) are independent and developed/green first. Row 14 goes green only after **#3282** lands. The digitalmodel buckling determinism tests are **not in #3283's suite** — they are #3285's, gated additionally on #3284 + #3307.

---

## Acceptance Criteria

- [ ] **#3297 and #3282 have landed** (`run_workflow`, `ResultEnvelope`, `determinism.result_hash`, parameterized `code_version` exist and are merged). #3283 does not merge before #3282.
- [ ] `from assetutilities.workflow_api import stamp_provenance, golden_workflow_test, GOLDEN_VOLATILE_KEYS` imports cleanly.
- [ ] **The volatile-field spec is a KEY-ALLOWLIST keyed by dotted key-name only** — `GOLDEN_VOLATILE_KEYS` plus per-golden `extra_volatile_keys`. **No value-based stripping anywhere**; a result value that string-renders date-like or path-like is preserved (asserted by `test_volatile_keys_is_key_allowlist_not_value_heuristic`). (Wave-1 MAJOR fix — kept.)
- [ ] **`result_hash` is consumed, not redefined** — `golden_workflow_test` asserts `env.determinism["result_hash"] == golden["result_hash"]` (#3282-owned); #3283 adds no second hashing function (grep for a new `sha256(`-based result hasher in #3283's files → none).
- [ ] **The golden test hashes the REAL emitted artifact via `run_workflow`** — no `build_envelope_*` / fabricated-envelope path; the asserted envelope is the return of `run_workflow(workflow_id, ...)`.
- [ ] **`stamp_provenance` parameterizes `code_version`** — `stamp_provenance(input_hash, package_name="digitalmodel")` stamps digitalmodel's version, not a hardcoded assetutilities one (`test_stamp_provenance_package_name_parameterized`). Returns `{code_version{package_version,git_sha}, standard_revisions[], data_as_of, input_hash}`; `input_hash` reused from #3282 verbatim.
- [ ] **Harness self-test green** on the assetutilities `data_exploration` **bare single-registry id** (`test_self_test_data_exploration_deterministic`) — proves the template without #3284 or #3285.
- [ ] **The digitalmodel buckling reference golden is OWNED BY #3285, not #3283** — #3283 commits no `digitalmodel/tests/...` file; the buckling rows in the pseudocode are an illustrative consumer example. The reference golden uses the cross-repo id `digitalmodel:buckling-parametric` and is gated on **#3284** (resolver) + **#3285** (row/route/golden) + **#3307** (digitalmodel embed-port). When #3285 lands, re-running yields an identical `result_hash` and a deliberate input change flips it.
- [ ] `docs/standards/2026-06-28-determinism-golden-refresh.md` documents the golden-refresh procedure: what `REGEN_GOLDENS=1` does (rewrite + `pytest.skip`), what re-sanctioning requires, and owner sign-off (BSEE re-sanction lesson).
- [ ] `uv run pytest assetutilities/tests/workflow_api/ -v` green; no regression in the assetutilities suite.
- [ ] Review artifacts posted under scripts/review/results/.

---

## Adversarial Review Summary

### Wave-1 — verdict: **MAJOR** — ADDRESSED in Wave-2 (retained)

| Wave-1 finding | Disposition |
|---|---|
| **MAJOR — value-heuristic canonicalizer** (`VOLATILE_KEYS … plus path-like / ISO-8601 VALUES`) risks false-negatives | **FIXED.** Volatile spec is now `GOLDEN_VOLATILE_KEYS` — a KEY-ALLOWLIST of dotted key-names, applied by name only; result PAYLOAD never value-pruned. Guard `test_volatile_keys_is_key_allowlist_not_value_heuristic`. |
| **MAJOR — redefined `result_hash`** inside #3283 | **FIXED.** #3283 CONSUMES `env.determinism["result_hash"]`; no second hasher. |
| **MAJOR — invented `build_envelope_from_buckling`** bypasses real emission | **FIXED.** `golden_workflow_test` asserts against `run_workflow(...)`'s real envelope. |

### Wave-2 — verdict: **MAJOR (1)** — ADDRESSED in this Wave-3 revision

| Wave-2 finding | Disposition in Wave-3 |
|---|---|
| **MAJOR — reference golden `run_workflow("digitalmodel:buckling-parametric")` used a CROSS-REPO id without gating on its resolver (owned by #3284)** | **FIXED.** The harness **self-test** now uses a **bare single-registry id** (`data_exploration`, resolved inside assetutilities' own registry by #3282 — no #3284). The cross-repo `digitalmodel:buckling-parametric` id is used only by the **#3285-owned** reference golden, which is now explicitly gated on **#3284** (resolver `capability_smoke.py:117/:167`) + **#3285** + **#3307**. |
| **MAJOR (coupled) — #3283 was authoring the digitalmodel buckling golden + test that #3285 OWNS** | **FIXED.** Those two files are removed from #3283's Files to Change and moved to the Artifact Map under **#3285 ownership**; they appear in this plan only as an illustrative consumer example. #3283 ships the template + a self-test on an assetutilities row. |
| (carried) `code_version` must be parameterized per #3282 | **APPLIED.** `stamp_provenance(... package_name=...)` calls `code_version(package_name)` (#3282 `:172`); `test_stamp_provenance_package_name_parameterized`. |

### Wave-3 (this revision) — verdict: **PENDING**

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | |
| Codex | PENDING | |
| Gemini | PENDING | |

**Overall result:** PENDING — re-dispatch the T3 wave via `scripts/review/plan-review-fanout.sh`. Not approval-ready until populated with no-MAJOR verdicts. Status stays `draft`.

---

## Risks and Open Questions

- **Risk — hard dependency chain (top risk).** #3283 cannot land before #3282 (which cannot land before #3297). The digitalmodel reference golden additionally needs #3284 (cross-repo resolution) + #3285 (row/route/golden) + #3307 (digitalmodel embed-port). **Mitigation:** the harness (`provenance.py`, `golden.py`, KEY-allowlist, refresh doc) is developed and green against synthetic envelopes + the assetutilities `data_exploration` **bare-id** self-test — none of which need #3284/#3285/#3307. The buckling reference golden is a clearly-labeled #3285 follow-on.
- **Risk — cross-repo vs bare id confusion (the Wave-2 MAJOR class).** A `repo:id` id silently incurs a #3284 dependency a bare id does not. **Mitigation:** #3283's only `run_workflow` call (the self-test) uses a bare single-registry id; the plan flags every cross-repo id as #3284-gated. **Promotion candidate:** "cross-repo `repo:id@version` ids require the #3284 manifest resolver; bare ids resolve in-registry" is a generalizable adoption-issue gotcha — worth a one-line note in the registry README so #3285/#3286/#3287 don't re-discover it (per the promote-generalizable-findings rule).
- **Risk — `stamp_provenance` overlaps #3282's inline provenance assembler.** **Mitigation / seam:** #3283 does NOT change the emitted provenance SHAPE (#3282 owns it). If #3282 lands first, #3283 extracts its inline body into `stamp_provenance` — a pure extract-method with an identical output dict, guarded by `test_stamp_provenance_shape`. **Decision needed:** confirm single-owner of the reusable assembler with the operator (recommend: #3283 owns the reusable assembler, #3282 owns the field set + parameterized `code_version` + the runner call-site). Flag at review; do not redesign #3282's contract.
- **Risk — choosing the reference workflow id.** `buckling_parametric` (the clean, `timestamp=None`-default `results.json` producer) is **not yet** a registry row; `plate-buckling`/`elastic-buckling` rows emit cfg-echo `results/input.yml` that may carry run-time fields. **Mitigation:** #3285 decides which buckling workflow becomes `run_workflow`-callable and authors its golden. Recommendation to #3285: register the parametric sweep (or drive `plate-buckling` with `timestamp=None`) so the emitted artifact is clock-free; FFS `to_dict()` (no timestamp/path field) is the documented fallback. **Open:** final reference id is #3285's call.
- **Risk — refresh becomes a rubber stamp.** **Mitigation:** `REGEN_GOLDENS=1` `pytest.skip`s (does not pass), and the refresh doc requires owner sign-off before a refreshed golden is committed (BSEE re-sanction lesson). A follow-on Level-2 check that a golden change in a PR carries a sign-off marker is flagged out-of-scope.
- **Risk — float determinism across platforms.** **Mitigation:** the reference producer already rounds at emit time (`buckling_parametric._round`, n=4), so emitted bytes are stable; #3283 adds NO tolerance step. Cross-platform tolerance, if ever needed, is #3282's `result_hash` design surface, not #3283's.
- **Risk — `data_as_of` pinning.** `provenance.data_as_of` is in the volatile KEY-allowlist by default (so a data refresh doesn't break the golden); a workflow whose determinism legitimately depends on a frozen data vintage may PIN it via removing it from `extra_volatile_keys`. Default is record-don't-pin; documented in the refresh doc.
- **Open:** `provenance.code_version` shape — `{package_version, git_sha}` (inherited from #3282) vs `git describe`. Inherit whatever #3282 settles; flag at review.

---

## Complexity: T3

**T3** — a foundational, ecosystem-shared harness in the `assetutilities.workflow_api` package plus a control-plane refresh doc; it is the determinism guarantee the rest of epic #3281 inherits, it is coupled to the still-owner-unapproved #3282 contract, and its reference demonstration is gated on #3284 + #3285 + #3307. Warrants 3-provider adversarial review.
