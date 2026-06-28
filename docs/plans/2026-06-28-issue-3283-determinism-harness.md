# Plan for #3283: wf-api(ecosystem) — determinism harness (golden-test harness + provenance stamp + volatile-field KEY-allowlist + golden-refresh procedure)

> **Status:** draft
> **Complexity:** T3 (cross-repo harness — assetutilities `workflow_api` + digitalmodel reference golden + control-plane refresh doc; the determinism guarantee the whole #3281 epic rests on; 3-provider review)
> **Date:** 2026-06-28 (Wave-2 re-scope after Wave-1 MAJOR — see "Revision note")
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3283
> **Epic:** https://github.com/vamseeachanta/workspace-hub/issues/3281
> **Depends on:** #3297 (engine embeddability — MUST land first) → #3282 (ResultEnvelope + `run_workflow` + `result_hash` — MUST land first) → #3283 (this) | reference golden gated on #3285 (digitalmodel adoption registers a `run_workflow`-callable buckling workflow)
> **Client:** N/A — no wiki content touched
> **Lane:** lane:codex (test/infra harness code; heavy-compute lane per the issue's `lane:codex` label)
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3283-claude.md | ...-codex.md | ...-gemini.md

---

## Revision note (2026-06-28, Wave-2 — re-scope after the Wave-1 MAJOR)

The Wave-1 plan returned **MAJOR**. Root defect: it proposed a value-sniffing canonicalizer that **stripped any date-like / path-like VALUE** from the result before hashing (`VOLATILE_KEYS = {...} # plus path-like / ISO-8601 values`), and it asserted determinism against an **invented `build_envelope_from_buckling(...)`** that bypassed the real emission path. Both are unsound:

1. **Value heuristics risk false-negatives.** Stripping any value that "looks like" a date or a path silently discards *legitimate result content* — a buckling case whose `governing` string or a wall-thickness path-keyed lookup contains a slash, an ISO-date field that is a genuine engineering input (`data_as_of` of a real measurement), or a numeric that string-renders date-like. A determinism harness that erases real output before hashing will report "reproducible" while masking actual drift. **This Wave-2 plan removes ALL value-based stripping.** The volatile-field spec is a **KEY-ALLOWLIST keyed by dotted key-name only**; values are never inspected to decide inclusion.

2. **`result_hash` is #3282-owned — do NOT redefine it.** Wave-1 re-implemented a float-tolerance `result_hash()` inside #3283. That collides with #3282, which already owns `determinism.result_hash` (kind:files = sorted-basename → sha256(file CONTENTS), excluding the `save_cfg` cfg-dump; kind:in_memory = canonical value hash) and `determinism.reproducible` (true double-run). **This Wave-2 plan CONSUMES `envelope.determinism.result_hash` verbatim** as the load-bearing determinism assertion and adds **no second hashing function**.

3. **The reference golden must hash the REAL emitted artifact via `run_workflow`.** Wave-1's `build_envelope_from_buckling` was a fabricated envelope that never exercised the engine. **This Wave-2 plan asserts against the envelope returned by `run_workflow(workflow_id, ...)`** — the genuine #3282 emission path. The digitalmodel buckling reference golden therefore **depends on #3285** registering a `run_workflow`-callable buckling workflow. The harness's own self-test runs against an already-callable **assetutilities** registry workflow (`data_exploration`, the #3282 demo row) so the template is proven green without #3285.

What #3283 owns after this re-scope (narrowed, non-overlapping with #3282):
- **`golden_workflow_test(workflow_id, golden_path, ...)`** — the pytest template that runs `run_workflow`, compares the emitted envelope against a committed golden, and fails on drift.
- **The volatile-field KEY-ALLOWLIST** — an explicit set of dotted envelope key-names the golden comparison ignores (e.g. `provenance.code_version.git_sha`), applied **by key name, never by value**.
- **`stamp_provenance(input_hash, *, standard_revisions, data_as_of)`** — the canonical reusable provenance assembler (codifies the #3282 provenance SHAPE; coordination seam below).
- **A documented golden-refresh / re-sanction procedure** (per the BSEE re-sanction lesson).

What #3283 does NOT own (consumed as specified, not redesigned): `result_hash`, `reproducible`, `input_hash`, the `result:` registry descriptor, the embed path, the `ResultEnvelope` field set.

---

## Resource Intelligence Summary

### Existing repo code (verified 2026-06-28)

- **`assetutilities` `workflow_api` (the #3282 surface this harness extends) — DOES NOT EXIST YET.** `ls /mnt/local-analysis/assetutilities/src/assetutilities/workflow_api` → absent. It is greenfield, created by #3282. #3283 adds two new modules into that package (`golden.py`, `provenance.py`) and a tests dir. **Hard dependency:** #3283 cannot land before #3282 (which itself cannot land before #3297). Critical path: **#3297 → #3282 → #3283**.
- **`/mnt/local-analysis/digitalmodel/src/digitalmodel/structural/buckling_parametric.py` — the cleanest reference workflow.** Verified line-level:
  - `_round(x, n=4)` (`:97-98`) — every numeric is rounded at emit time; the float-stability convention is already *inside the producer*, so the harness needs no float-tolerance step of its own (a second reason Wave-1's float-tolerance hasher was redundant).
  - `write_outputs(rows, curves, out_dir, gamma_m, timestamp=None)` (`:232-284`) emits `cases.csv` + `results.json` with `{meta, lookup, index, index_status, curves}`. The **only** volatile field is `meta.generated_at`, and it is **already optional** — `if timestamp is not None` (`:278-279`). With `timestamp=None` (the default), the emission is byte-stable. This is why buckling is the reference: pure-Python + pandas, no clock, no network, no path-baked-into-output.
- **`/mnt/local-analysis/digitalmodel/docs/registry/workflows.yaml` — `schema_version: 2`, top-level `invocation: "uv run python -m digitalmodel {input}"`.** Already carries buckling rows: `plate-buckling` (`:477`, basename `plate_buckling`, single DNV-RP-C201 check) and `elastic-buckling` (`:410`). **It does NOT carry a `buckling_parametric` row.** So the parametric sweep producer above is *not yet* a `run_workflow`-callable workflow; making one callable is exactly **#3285's** job ("adopt ResultEnvelope + schemas + goldens (FFS, buckling, mooring, wall-thickness)"). The reference golden test is therefore gated on #3285.
- **`/mnt/local-analysis/digitalmodel/src/digitalmodel/asset_integrity/assessment/ffs_coordinator.py:61` — `FFSAssessmentResult` dataclass with `to_dict()` (`:90-107`).** A flat, fully numeric/string JSON summary (`verdict`, `rsf`, `remaining_life_yr`, `sufficiency_status`, …) with **no timestamp or path field at all** — the fallback reference workflow; its `to_dict()` is a clean `kind:in_memory` result payload.
- **`/mnt/local-analysis/digitalmodel/src/digitalmodel/compare_tool/workflow.py:15` — `router(cfg)`** does baseline-vs-variant CSV/YAML diff: outer-merge on a key, per-source `delta`/`ratio`, `max_abs_delta` per label (`:38-43`). This is the prior art the issue says to "reuse for golden comparison". The golden mismatch-diff borrows its keyed-numeric-delta + `max_abs_delta` shape so a failure shows *what* drifted — **for human debugging only; the PASS/FAIL verdict is the `result_hash` string-equality, never a value-delta heuristic.**
- **`/mnt/local-analysis/digitalmodel/tests/hydrodynamics/diffraction/benchmarks/golden_capture.py` — the proven golden-file refresh pattern (#501).** Verified: `enumerate_byte_identity_fixtures()`, `golden_path_for(spec)`, `render_*_bytes() -> bytes`, a `capture_golden()` + `main()` regenerate entry-point, and a module docstring documenting the refresh command (`uv run python -m tests...golden_capture`). The template's capture/refresh ergonomics mirror this shape rather than reinvent it. (Note: it is a *byte-identity, token-level, no-tolerance* golden over OrcaWave **input** text — NOT a `ResultEnvelope` golden over a workflow **result**; the gap #3283 fills.)
- **`/mnt/local-analysis/digitalmodel/src/digitalmodel/citations/` — `schema.py`, `registry.py`, `resolver.py`** (the calc-citation pilot). `Citation` (`code_id`/`publisher`/`revision`) is the source shape for `provenance.standard_revisions` that `stamp_provenance` assembles.

### Standards

Not applicable — this is harness/infra code, not an engineering calculation. The reference golden covers `DNV-RP-C201` (buckling) but introduces no new standards-derived constants; `provenance.standard_revisions` *records* citations, it does not derive them. No `Citation` emission required by this plan.

| Standard | Status | Source |
|---|---|---|
| DNV-RP-C201 (reference workflow only) | recorded via provenance, not derived | `buckling_parametric.py:34` `STANDARD = "DNV-RP-C201"` |

### LLM Wiki pages consulted

None — contract/infra work, no domain knowledge added. (`Client: N/A`.) `provenance.standard_revisions` references the calc-citation wiki-slug mechanism but adds no page.

### Documents consulted

- Epic [#3281](https://github.com/vamseeachanta/workspace-hub/issues/3281) — gap #3 ("Determinism is aspirational… no golden baselines, no byte-identical assertions, no provenance stamp, no result hash") is this issue's exact charter.
- **[#3282 plan](2026-06-27-issue-3282-resultenvelope-run-workflow.md)** — the upstream contract this harness consumes. `from assetutilities.workflow_api import run_workflow, ResultEnvelope`. `run_workflow(workflow_id, params=None, cfg=None) -> ResultEnvelope` via the #3297 embed path. `ResultEnvelope` = stdlib dataclass `{workflow_id, status, result, provenance{code_version{package_version, git_sha}, standard_revisions[], data_as_of, input_hash}, determinism{result_hash, reproducible}, confidence, warnings}`. **#3282 OWNS `determinism.result_hash` (kind:files = sorted-basename → sha256(CONTENTS), EXCLUDING the `save_cfg` `<file_name>.yml` dump; kind:in_memory = canonical value hash), `reproducible`, `input_hash`, and the `result:` descriptor.** No-MAJOR at `status:plan-review`, owner-unapproved.
- **[#3297 plan](2026-06-28-issue-3297-engine-embeddability.md)** — PREREQ. Adds `engine(cfg=..., embed=True, root_folder=, log_to_file=)` + `ConfigureApplicationInputs.configure_embed`. Must land first (transitively, via #3282).
- **[#3295 plan](2026-06-28-issue-3295-registry-schema-v2-reconcile.md)** — registry `schema_version: 2` additive superset; required top-level `invocation:`; `request_schema`/`response_schema` RESERVED structured; `deckhand/src/deckhand/capability_smoke.py` = real resolver. The reference golden's workflow row lives under this schema.
- **[#3284 plan](2026-06-28-issue-3284-discovery-manifest.md)** — aggregates registries into a manifest of callable workflows; the manifest is how `run_workflow` discovers cross-repo workflow ids (relevant to whether `run_workflow("…buckling…")` can resolve a digitalmodel row).
- **[#3285](https://github.com/vamseeachanta/workspace-hub/issues/3285)** (OPEN, `status:needs-plan`, `lane:codex`) — "wf-api(digitalmodel): adopt ResultEnvelope + schemas + goldens (FFS, buckling, mooring, wall-thickness)". **The reference golden test's hard dependency**: it registers a `run_workflow`-callable buckling workflow whose REAL emitted artifact the golden hashes.
- `.claude/rules/calc-citation-contract.md` — `Citation` sidecar shape reused for `provenance.standard_revisions` (`source_sibling` required; default `generic` during digitalmodel migration).
- MEMORY: BSEE golden-baseline re-sanction lesson (`project_julia_field_economics_demo`, `project_bsee_ogor_refresh_mechanics`) — "golden baseline needs RE-SANCTIONING after refresh"; drives the documented refresh-requires-sign-off requirement.

### Gaps identified

- No `golden_workflow_test(workflow_id)` helper / template anywhere; no committed golden *envelope* for any `run_workflow`-callable workflow.
- No volatile-field KEY-ALLOWLIST spec (the Wave-1 attempt was a value heuristic — defective).
- No reusable `stamp_provenance` assembler (the #3282 plan inlines a minimal `provenance(ihash)` + `code_version()`; #3283 generalizes the SHAPE without changing it).
- No documented golden-refresh / re-sanction procedure for `ResultEnvelope` goldens.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3283` — OPEN, `status:needs-plan`, `lane:codex` — this issue
- `#3282` — plan exists, no-MAJOR at `status:plan-review`, owner-unapproved — hard dependency
- `#3297` — plan exists, prereq of #3282
- `#3285` — OPEN, `status:needs-plan`, `lane:codex`, title "wf-api(digitalmodel): adopt ResultEnvelope + schemas + goldens (FFS, buckling, mooring, wall-thickness)" — reference-golden dependency
- `#3281` — OPEN — parent epic

**File existence** (`ls`/`grep` 2026-06-28):
- EXISTS: `digitalmodel/src/digitalmodel/structural/buckling_parametric.py` (`_round` `:97`; `write_outputs` `:232`; `if timestamp is not None` `:278`)
- EXISTS: `digitalmodel/src/digitalmodel/asset_integrity/assessment/ffs_coordinator.py` (`FFSAssessmentResult` `:61`; `to_dict` `:90`, no timestamp/path field)
- EXISTS: `digitalmodel/src/digitalmodel/compare_tool/workflow.py` (`router` `:15`)
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/golden_capture.py` (refresh-pattern precedent)
- EXISTS: `digitalmodel/docs/registry/workflows.yaml` (`schema_version: 2`; rows `plate-buckling` `:477`, `elastic-buckling` `:410`; **no** `buckling_parametric` row)
- MISSING (created here, into the #3282 package): `assetutilities/src/assetutilities/workflow_api/golden.py`, `.../provenance.py`, `assetutilities/tests/workflow_api/test_golden.py`, `.../test_provenance.py`
- MISSING (#3282 creates; #3283 imports): `assetutilities/src/assetutilities/workflow_api/{__init__,runner,envelope}.py`
- MISSING (created here, gated on #3285): `digitalmodel/tests/.../goldens/<buckling-workflow>.envelope.json`, `digitalmodel/tests/.../test_<buckling>_determinism.py`

**Gap proofs** (2026-06-28):
- `grep -rln "result_hash" digitalmodel/src assetutilities/src` → **ZERO** (no `result_hash` exists yet; it arrives with #3282 — #3283 must NOT add a second one).
- `grep -rln "golden_workflow_test\|stamp_provenance" digitalmodel assetutilities` → **ZERO** (greenfield).
- `ls assetutilities/src/assetutilities/workflow_api` → **absent** (the package #3282 creates; #3283 extends it).
- `grep -n "buckling_parametric" digitalmodel/docs/registry/workflows.yaml` → **none** (parametric sweep is not yet `run_workflow`-callable → #3285).

### Step 1.5 — Reproduction

**Claim under test (from the issue body):** "digitalmodel today has no golden baselines and no byte-identical assertions… no provenance stamp, no result hash."

```
$ cd /mnt/local-analysis/digitalmodel
$ grep -rln "result_hash" src | grep -v __pycache__         → ZERO
$ grep -rln "golden" tests/structural tests/asset_integrity → test_panel_buckling.py, test_corroded_pipe.py,
                                                              test_ffs_validation.py, test_dnv_rp_f101.py
$ grep -n "golden" tests/structural/structural_analysis/test_panel_buckling.py
   2: # ABOUTME: ... + DNV golden case.
   7: solver to the 0119-015 DNV-RP-C201 worked example (golden numbers).
$ sed -n '1,12p' tests/hydrodynamics/diffraction/benchmarks/golden_capture.py
   1: """Golden-file capture for OrcaWave byte-identity regression (#501 Sub-task 0).
   6-7: ... byte-identity test then fails on any emission drift — token-level, no numeric tolerance.
```
- Reproduced at: 2026-06-28.
- **Result — refined (the literal claim is PARTIALLY true):** (a) digitalmodel *does* have a byte-identity golden — but only for **OrcaWave input-file emission** (`golden_capture.py`, #501), not a workflow *result*; (b) the structural/FFS "golden" tests assert **golden NUMBERS** (worked-example reference values within tolerance), not same-input→same-output reproducibility of an emitted artifact. What is **genuinely absent** (this issue's charter): a **result-hash / provenance-stamped determinism golden over a `ResultEnvelope` returned by `run_workflow`**. This plan targets that real gap.
- **Behavioral assertions in this plan that CANNOT be reproduced yet (and why):** `run_workflow(...)` does not exist (its package is absent — #3282); a `run_workflow`-callable buckling workflow does not exist (no `buckling_parametric` registry row — #3285). So the end-to-end "re-running yields identical `result_hash`" demonstration is **gated on #3282 + #3285 landing**. Until then the harness is proven by (i) unit tests over `stamp_provenance` and the golden-diff logic with synthetic envelopes, and (ii) a self-test against the already-callable assetutilities `data_exploration` row once #3282 lands. Reproduction of the digitalmodel buckling end-to-end is **N/A until #3285** — recorded here so reviewers know the skip is a dependency gate, not an omission.

(Distinct sources: issue body + #3282 plan + #3297 plan + #3295 plan + #3284 plan + #3285 issue + buckling_parametric.py + ffs_coordinator.py + compare_tool/workflow.py + golden_capture.py + digitalmodel registry + calc-citation rule + grep gap-proofs = 13+.)

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3283-determinism-harness.md |
| Provenance assembler | `assetutilities/src/assetutilities/workflow_api/provenance.py` |
| Golden template + volatile KEY-allowlist + capture/diff | `assetutilities/src/assetutilities/workflow_api/golden.py` |
| Package export (coordinate with #3282's `__init__.py`) | `assetutilities/src/assetutilities/workflow_api/__init__.py` |
| Harness tests | `assetutilities/tests/workflow_api/test_provenance.py`, `test_golden.py` |
| Harness self-test golden (assetutilities `data_exploration`) | `assetutilities/tests/workflow_api/goldens/data_exploration.envelope.json` |
| Reference golden envelope (gated on #3285) | `digitalmodel/tests/structural/goldens/<buckling-workflow>.envelope.json` |
| Reference determinism test (gated on #3285) | `digitalmodel/tests/structural/test_<buckling>_determinism.py` |
| Refresh/re-sanction doc | `docs/standards/2026-06-28-determinism-golden-refresh.md` |
| Plan reviews | scripts/review/results/2026-06-28-plan-3283-{claude,codex,gemini}.md |
| Plan index | docs/plans/README.md |

> **Note:** `assetutilities/src/assetutilities/workflow_api/{runner,envelope}.py` are **#3282's**, not #3283's. #3283 imports `run_workflow`, `ResultEnvelope`, and the emitted `determinism.result_hash`; it does not edit them. The `__init__.py` export line is a coordination seam with #3282.

---

## Deliverable

A determinism golden-test harness added to the `assetutilities.workflow_api` package (created by #3282), comprising:
1. **`golden_workflow_test(workflow_id, golden_path, *, params=None, cfg=None)`** — a pytest helper that calls `run_workflow`, asserts the emitted envelope's `determinism.result_hash` equals the committed golden's, and (optionally) asserts pinned non-volatile envelope fields, ignoring a documented KEY-allowlist of volatile keys; it reuses the `compare_tool` keyed-delta shape to *describe* drift on failure (human debugging) without using value heuristics for the verdict.
2. **`stamp_provenance(input_hash, *, standard_revisions=None, data_as_of=None) -> dict`** — the canonical reusable provenance assembler codifying the #3282 provenance shape (`code_version{package_version, git_sha}` + `standard_revisions[]` + `data_as_of` + `input_hash`).
3. **The volatile-field KEY-ALLOWLIST** — an explicit `GOLDEN_VOLATILE_KEYS` set of dotted envelope key-names the golden comparison ignores, applied **by key name only, never by value sniffing**.
4. **A documented golden-refresh / re-sanction procedure** (`docs/standards/2026-06-28-determinism-golden-refresh.md`) — what `REGEN_GOLDENS=1` does, what re-sanctioning requires, and owner sign-off.

Proven by: the harness self-test against the assetutilities `data_exploration` row (available once #3282 lands), and — gated on #3285 — one committed reference golden + passing determinism test on a `run_workflow`-callable digitalmodel buckling workflow.

---

## Pseudocode

```python
# ── provenance.py ─────────────────────────────────────────────
# Canonical reusable provenance assembler. Codifies the #3282 provenance SHAPE; does not change it.
# (Coordination seam: if #3282 lands with an inline provenance() + code_version(), #3283 refactors that
#  inline body INTO stamp_provenance without altering the emitted dict; #3282 still OWNS the field set.)
def code_version() -> dict:
    return {"package_version": _package_version(),          # importlib.metadata.version(...)
            "git_sha": _git_short_sha_or_none()}            # rev-parse HEAD, best-effort; None off-checkout

def stamp_provenance(input_hash, *, standard_revisions=None, data_as_of=None) -> dict:
    return {
        "code_version": code_version(),
        "standard_revisions": list(standard_revisions or []),   # list of Citation dicts (code_id/publisher/revision)
        "data_as_of": data_as_of,                               # None for pure-calc workflows (buckling)
        "input_hash": input_hash,                               # #3282-owned value; reused verbatim, never recomputed
    }

# ── golden.py ─────────────────────────────────────────────────
# THE VOLATILE-FIELD SPEC = a KEY-ALLOWLIST of DOTTED KEY-NAMES. Never inspects values.
# These are envelope fields that legitimately differ run-to-run / commit-to-commit and so are EXCLUDED
# from the (optional) structural comparison. The determinism PASS/FAIL is result_hash equality, NOT these.
GOLDEN_VOLATILE_KEYS = frozenset({
    "provenance.code_version.git_sha",        # changes every commit
    "provenance.code_version.package_version",# changes on release bump
    "provenance.data_as_of",                  # data-refresh dependent (record, don't pin) -- OPT-IN to pin per golden
    "determinism.reproducible",               # a measured bool/None, not a fixed expectation
})
# NOTE: there is NO value-based rule. A key is volatile iff its dotted name is in this set. A future
# volatile key is added by NAME here (or via a per-golden `extra_volatile_keys=[...]`), never by a
# "looks like a date/path" heuristic. The result PAYLOAD is never value-stripped -- it is covered by the
# #3282 result_hash, which already excludes the save_cfg dump and is content-based.

def _prune_volatile(d: dict, volatile_keys) -> dict:
    # recursively drop dotted keys present in `volatile_keys`; leave everything else byte-for-byte.
    ...

def capture_golden(envelope, golden_path):
    # Write a golden snapshot: the load-bearing determinism.result_hash + a copy of the envelope with
    # GOLDEN_VOLATILE_KEYS pruned (for human-readable structural pinning). Mirrors golden_capture.py ergonomics.
    snapshot = {"workflow_id": envelope.workflow_id,
                "result_hash": envelope.determinism["result_hash"],     # #3282-owned, consumed not recomputed
                "status": envelope.status,
                "envelope_pruned": _prune_volatile(envelope.to_dict(), GOLDEN_VOLATILE_KEYS)}
    Path(golden_path).write_text(json.dumps(snapshot, indent=2, sort_keys=True))

def diff_results(golden_pruned, current_pruned):
    # reuse compare_tool keyed-delta + max_abs_delta shape to DESCRIBE what drifted (debugging aid only).
    # This is NOT the verdict; it is the failure message body.
    ...

def golden_workflow_test(workflow_id, golden_path, *, params=None, cfg=None,
                         pin_structural=False, extra_volatile_keys=()):
    env = run_workflow(workflow_id, params=params, cfg=cfg)             # #3282 entrypoint -- REAL emission
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

# ── digitalmodel reference test (GATED ON #3285) ──────────────
# REQUIRES: #3285 has registered a run_workflow-callable buckling workflow (id TBD by #3285).
BUCKLING_WF = "digitalmodel:buckling-parametric"   # exact id owned by #3285's registry row
GOLDEN = Path(__file__).parent / "goldens" / "buckling_parametric.envelope.json"

def test_buckling_is_deterministic():
    # Same input -> same result_hash. No invented build_envelope: this is the REAL run_workflow emission.
    golden_workflow_test(BUCKLING_WF, GOLDEN, params=DEFAULT_SHIP_PLATE_PARAMS)

def test_buckling_input_change_flips_hash():
    base    = run_workflow(BUCKLING_WF, params=DEFAULT_SHIP_PLATE_PARAMS).determinism["result_hash"]
    mutated = run_workflow(BUCKLING_WF, params=THICKER_PLATE_PARAMS).determinism["result_hash"]
    assert base != mutated                                            # deliberate input change flips it
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `assetutilities/src/assetutilities/workflow_api/provenance.py` | `stamp_provenance` + `code_version` (canonical reusable assembler; #3282 provenance SHAPE) |
| Create | `assetutilities/src/assetutilities/workflow_api/golden.py` | `golden_workflow_test` template, `GOLDEN_VOLATILE_KEYS` (dotted KEY-allowlist), `_prune_volatile`, `capture_golden`, `diff_results` |
| Modify | `assetutilities/src/assetutilities/workflow_api/__init__.py` | export `stamp_provenance`, `golden_workflow_test`, `GOLDEN_VOLATILE_KEYS` (coordination seam with #3282) |
| Create | `assetutilities/tests/workflow_api/test_provenance.py` | provenance assembler TDD |
| Create | `assetutilities/tests/workflow_api/test_golden.py` | template + KEY-allowlist + self-test-on-`data_exploration` TDD |
| Create | `assetutilities/tests/workflow_api/goldens/data_exploration.envelope.json` | harness self-test golden (#3282-callable; no #3285 needed) |
| Create (gated #3285) | `digitalmodel/tests/structural/goldens/<buckling-workflow>.envelope.json` | committed reference golden envelope |
| Create (gated #3285) | `digitalmodel/tests/structural/test_<buckling>_determinism.py` | reference determinism test (same-input→same-hash; mutation flips) |
| Create | `docs/standards/2026-06-28-determinism-golden-refresh.md` | golden-refresh + re-sanction procedure (owner sign-off) |
| Update | `docs/plans/README.md` | refresh this plan's index row |

> **Not owned here:** `assetutilities/src/assetutilities/workflow_api/{runner,envelope}.py` (#3282) and the engine embed path (#3297). #3283 only imports/calls them.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_stamp_provenance_shape | returns `{code_version{package_version,git_sha}, standard_revisions, data_as_of, input_hash}` | `stamp_provenance("ih")` | all four keys; `code_version` has both subkeys |
| test_stamp_provenance_passes_input_hash_verbatim | reuses #3282 `input_hash` unchanged (never recomputes) | `input_hash="sha256:abc"` | `provenance["input_hash"]=="sha256:abc"` |
| test_stamp_provenance_standard_revisions | a DNV-RP-C201 Citation dict lands under `standard_revisions` | one Citation dict | list contains that entry |
| test_code_version_git_sha_none_off_checkout | `git_sha` is `None` when not in a git work-tree, both keys still present | simulated non-git cwd | `{"package_version": str, "git_sha": None}` |
| test_volatile_keys_is_key_allowlist_not_value_heuristic | a result VALUE that string-renders date-like or path-like is **NOT** stripped (no value sniffing) | envelope whose `result` has `"governing":"2024-01-01"` and `"key":"a/b/c"` | both values survive pruning; only KEY-listed fields drop |
| test_prune_volatile_drops_git_sha_by_name | `provenance.code_version.git_sha` removed by dotted-name match | two envelopes differing only in `git_sha` | pruned dicts equal |
| test_prune_volatile_keeps_result_payload | the `result` payload is never value-pruned | envelope with rich result | result identical after prune |
| test_golden_pass_on_matching_result_hash | matching `result_hash` → passes, returns envelope | envelope whose `result_hash`==golden | no failure |
| test_golden_fail_on_result_hash_drift | drifted `result_hash` → AssertionError carrying keyed-delta message | golden vs mutated result | error message names the drifted key(s) |
| test_golden_verdict_is_hash_not_value_delta | a result change that keeps `result_hash` equal (impossible normally; injected) does NOT fail; a `result_hash` change DOES — proves verdict = hash, not value heuristic | two crafted envelopes | pass/fail driven by hash only |
| test_regen_goldens_env_writes_and_skips | `REGEN_GOLDENS=1` rewrites the golden + `pytest.skip` (re-sanction gate) | env var set | golden file written; test skipped |
| test_capture_golden_prunes_volatile | captured snapshot has `git_sha`/`package_version` pruned from `envelope_pruned` but keeps `result_hash` | one envelope | snapshot has `result_hash`, no `git_sha` |
| test_self_test_data_exploration_deterministic *(needs #3282)* | `golden_workflow_test("data_exploration", ...)` green via REAL `run_workflow` | data_exploration row | `result_hash`==committed golden |
| test_buckling_is_deterministic *(needs #3285)* | reference workflow re-run yields the committed hash via REAL `run_workflow` | buckling params | `result_hash`==golden |
| test_buckling_input_change_flips_hash *(needs #3285)* | a deliberate input change flips `result_hash` | thicker-plate params | hash != default golden |

> **Dependency gates on tests:** rows marked *(needs #3282)* go green only after #3282 lands (`run_workflow` callable); rows marked *(needs #3285)* go green only after #3285 registers the buckling workflow. The first 12 rows (provenance + KEY-allowlist + golden-diff logic over synthetic envelopes) are independent and developed/green first.

---

## Acceptance Criteria

- [ ] **#3297 and #3282 have landed** (`run_workflow`, `ResultEnvelope`, `determinism.result_hash` exist and are merged). #3283 does not merge before #3282.
- [ ] `from assetutilities.workflow_api import stamp_provenance, golden_workflow_test, GOLDEN_VOLATILE_KEYS` imports cleanly.
- [ ] **The volatile-field spec is a KEY-ALLOWLIST keyed by dotted key-name only** — `GOLDEN_VOLATILE_KEYS` plus per-golden `extra_volatile_keys`. **No value-based stripping anywhere**; a result value that string-renders date-like or path-like is preserved (asserted by `test_volatile_keys_is_key_allowlist_not_value_heuristic`). This is the Wave-1 MAJOR fix.
- [ ] **`result_hash` is consumed, not redefined** — `golden_workflow_test` asserts `env.determinism["result_hash"] == golden["result_hash"]` (#3282-owned); #3283 adds no second hashing function (grep for a new `sha256(`-based result hasher in #3283's files → none).
- [ ] **The golden test hashes the REAL emitted artifact via `run_workflow`** — there is no `build_envelope_from_buckling` or any fabricated-envelope path; the asserted envelope is the return of `run_workflow(workflow_id, ...)`.
- [ ] **Harness self-test green** on the assetutilities `data_exploration` row (`test_self_test_data_exploration_deterministic`) — proves the template without #3285.
- [ ] **Reference golden (gated on #3285):** a `run_workflow`-callable digitalmodel buckling workflow has a committed golden envelope + a passing determinism test; re-running yields an identical `result_hash`; a deliberate input change flips it. This AC is satisfied when #3285 has registered the workflow; until then the row is tracked as #3285-gated, not failed.
- [ ] **`stamp_provenance`** returns `{code_version{package_version,git_sha}, standard_revisions[], data_as_of, input_hash}`; `input_hash` is reused from #3282 verbatim, not recomputed.
- [ ] `docs/standards/2026-06-28-determinism-golden-refresh.md` documents the golden-refresh procedure: what `REGEN_GOLDENS=1` does (rewrite + `pytest.skip`), what re-sanctioning requires, and owner sign-off (per the BSEE re-sanction lesson).
- [ ] `uv run pytest assetutilities/tests/workflow_api/ -v` green; no regression in the assetutilities suite. (digitalmodel reference test green once #3285 lands.)
- [ ] Review artifacts posted under scripts/review/results/.

---

## Adversarial Review Summary

### Wave-1 (prior) — verdict: **MAJOR** — ADDRESSED in this Wave-2 revision

| Wave-1 finding | Disposition in Wave-2 |
|---|---|
| **MAJOR — value-heuristic canonicalizer** (`VOLATILE_KEYS … plus path-like / ISO-8601 VALUES`) risks false-negatives by stripping legitimate result content | **FIXED.** All value-based stripping removed. The volatile spec is now `GOLDEN_VOLATILE_KEYS` — a KEY-ALLOWLIST of dotted key-names, applied by name only. The result PAYLOAD is never value-pruned; determinism rides on the #3282 `result_hash`. Guard test `test_volatile_keys_is_key_allowlist_not_value_heuristic`. |
| **MAJOR — redefined `result_hash`** inside #3283 (collides with #3282 ownership) | **FIXED.** #3283 deletes its own hashing function and CONSUMES `env.determinism["result_hash"]`. AC + grep guard. |
| **MAJOR — invented `build_envelope_from_buckling`** bypasses the real emission path | **FIXED.** `golden_workflow_test` asserts against `run_workflow(workflow_id, ...)`'s real envelope; the digitalmodel reference golden is gated on #3285 registering a callable buckling workflow. |

### Wave-2 (this revision) — verdict: **PENDING**

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | |
| Codex | PENDING | |
| Gemini | PENDING | |

**Overall result:** PENDING — re-dispatch the T3 wave via `scripts/review/plan-review-fanout.sh`. Not approval-ready until populated with no-MAJOR verdicts. Status stays `draft`.

---

## Risks and Open Questions

- **Risk — hard dependency chain (top risk).** #3283 cannot land before #3282 (which cannot land before #3297); the reference golden cannot land before #3285. Critical path: **#3297 → #3282 → #3283**, with the digitalmodel reference golden a **#3285-gated** sub-deliverable. **Mitigation:** the harness (`provenance.py`, `golden.py`, KEY-allowlist, refresh doc) is developed and green against synthetic envelopes + the assetutilities `data_exploration` self-test, none of which need #3285. The buckling reference golden is a clearly-labeled follow-on that flips green when #3285 registers the workflow. **Per-issue extra gate:** the digitalmodel-side test changes ride the digitalmodel adoption gate (#3285); they are not committed until the workflow id exists. (This is the analogue of the assethold #3066 per-issue gate noted for sibling adoption issues — here the gating issue is #3285, not #3066.)
- **Risk — `stamp_provenance` overlaps #3282's inline `provenance()`/`code_version()`.** #3282's plan inlines a minimal provenance assembler; #3283 introduces the canonical reusable one. **Mitigation / coordination seam:** #3283 does NOT change the emitted provenance SHAPE (#3282 owns it). If #3282 lands first, #3283 refactors the inline body into `stamp_provenance` and has the runner call it — a pure extract-method with an identical output dict, guarded by `test_stamp_provenance_shape`. **Decision needed:** confirm the single-owner of the provenance assembler with the operator (recommend: #3283 owns the reusable assembler, #3282 owns the field set + the runner call-site). Flag at review; do not redesign #3282's contract.
- **Risk — choosing the reference workflow id.** `buckling_parametric` (the clean, `timestamp=None`-optional `results.json` producer) is **not yet** a registry row; `plate-buckling`/`elastic-buckling` are rows but their `outputs:` are cfg-echo `results/input.yml` files that may carry run-time fields. **Mitigation:** the golden test parametrizes on `workflow_id`; #3285 decides which buckling workflow becomes `run_workflow`-callable. Recommendation to #3285: register the parametric sweep (or drive `plate-buckling` with `timestamp=None`) so the emitted artifact is clock-free. FFS `to_dict()` (no timestamp/path field) is the documented fallback reference. **Open:** final reference id is #3285's call.
- **Risk — refresh becomes a rubber stamp.** `REGEN_GOLDENS=1` could silently re-bless drift. **Mitigation:** refresh `pytest.skip`s (does not pass), and the refresh doc requires owner sign-off before a refreshed golden is committed (BSEE re-sanction lesson). A follow-on Level-2 check that a golden change in a PR carries a sign-off marker is flagged out-of-scope.
- **Risk — float determinism across platforms.** Bit-exact float equality is not guaranteed across BLAS/numpy builds. **Mitigation:** the reference producer already rounds at emit time (`buckling_parametric._round`, n=4), so the emitted bytes are stable; #3283 adds NO tolerance step (the Wave-1 float-tolerance hasher is removed as redundant and out-of-scope — it was part of the deleted `result_hash` redefinition). If a future workflow needs cross-platform tolerance, that is #3282's `result_hash` design surface, not #3283's.
- **Risk — `data_as_of` pinning.** `provenance.data_as_of` is in the volatile KEY-allowlist by default (so a data refresh doesn't break the golden), but a workflow whose determinism legitimately depends on a frozen data vintage may want to PIN it. **Mitigation:** `data_as_of` pinning is opt-in per golden via removing it from `extra_volatile_keys`; documented in the refresh doc. Default is record-don't-pin.
- **Open:** `provenance.code_version` shape — `{package_version, git_sha}` (inherited from #3282) vs `git describe`. Inherit whatever #3282 settles; flag at review.

---

## Complexity: T3

**T3** — a foundational, ecosystem-shared harness in the `assetutilities.workflow_api` package, the digitalmodel reference golden, and a control-plane refresh doc; it is the determinism guarantee the rest of epic #3281 inherits, and it is coupled to the still-owner-unapproved #3282 contract and gated on #3285 for its reference demonstration. Warrants 3-provider adversarial review.
