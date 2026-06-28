# Plan for #3283: wf-api(ecosystem) — determinism harness (provenance stamp + result hash + golden-baseline template)

> **Status:** draft
> **Complexity:** T3 (cross-repo harness — assetutilities + digitalmodel + control-plane doc; the determinism guarantee the whole #3281 epic rests on; 3-provider review)
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3283
> **Epic:** https://github.com/vamseeachanta/workspace-hub/issues/3281
> **Depends on:** #3282 (ResultEnvelope shape — plan-against, currently Round-1 MAJOR / Round-2 pending)
> **Client:** N/A — no wiki content touched
> **Lane:** lane:codex (test/infra harness code; heavy-compute lane per issue label)
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3283-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `assetutilities/src/assetutilities/engine.py:27` — `engine(inputfile=None, cfg=None, config_flag=True) -> dict`; the shared in-process call path the harness measures determinism over. No `result_hash`, no provenance.
- Found: `digitalmodel/src/digitalmodel/structural/buckling_parametric.py:232` — `write_outputs(rows, curves, out_dir, gamma_m, timestamp=None)` emits `results.json` with `{meta, lookup, index, index_status, curves}`. Two facts the harness generalizes directly: (a) it already rounds every numeric via `_round(x, n=4)` (line 97) — a float-tolerance convention to lift into the hasher; (b) the **only** volatile field is `meta.generated_at`, and it is **already made optional** (`if timestamp is not None` line 278) — confirming the volatile-field-exclusion design is feasible. This is the cleanest reference workflow: pure-Python + pandas, no network, no clock dependence unless `timestamp` is passed.
- Found: `digitalmodel/src/digitalmodel/asset_integrity/assessment/ffs_coordinator.py:61` — `FFSAssessmentResult` dataclass with `to_dict()` (line 90) returning a flat JSON-serialisable summary. The fallback reference workflow; its `to_dict()` is the canonical result payload a hash would cover.
- Found: `digitalmodel/src/digitalmodel/compare_tool/workflow.py:15` — `router(cfg) -> dict` does baseline-vs-variant CSV/YAML diff: outer-merge on a key, per-source `delta`/`ratio` columns, and `max_abs_delta` per label (lines 38–43). This is the prior art the issue says to "reuse for golden comparison" — the harness's mismatch-diff borrows its keyed-numeric-delta + `max_abs_delta` shape so a golden failure shows *what* drifted, not just "hash mismatch".
- Found: `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/golden_capture.py` — an **existing** golden-file pattern (OrcaWave byte-identity, #501): `enumerate_byte_identity_fixtures()`, `golden_path_for()`, `render_orcawave_bytes() -> bytes`, with a documented regenerate procedure (`uv run python -m tests...golden_capture`). The template's capture/refresh ergonomics should mirror this proven shape rather than reinvent.
- Found: `digitalmodel/src/digitalmodel/citations/` — `schema.py`, `registry.py`, `resolver.py` (the calc-citation pilot). `Citation` (code_id/publisher/revision) is the source shape for `provenance.standard_revisions`.
- Found: `docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md` — the dependency. `ResultEnvelope` proposed as `{workflow_id, status, result, provenance{code_version, standard_revisions[], data_as_of, input_hash}, determinism{result_hash, reproducible}, confidence, warnings}`. `input_hash` is owned by #3282; `result_hash` + provenance stamping are this issue's to populate. **The envelope's `result` extraction is a #3282 Round-2 open design blocker (`result_key`/`response_schema`)** — the harness must hash whatever `envelope.result` ends up being and stay decoupled from how it is extracted.

### Standards

Not applicable — this is harness/infra code, not an engineering calculation. The reference golden covers `DNV-RP-C201` (buckling) but introduces no new standards-derived constants; `provenance.standard_revisions` *records* citations, it does not derive them.

| Standard | Status | Source |
|---|---|---|
| DNV-RP-C201 (reference workflow only) | recorded via provenance, not derived | `buckling_parametric.py:34` `STANDARD = "DNV-RP-C201"` |

### LLM Wiki pages consulted

No relevant wiki pages — contract/infra work, no domain knowledge added. (Provenance `standard_revisions` references the calc-citation wiki-slug mechanism but adds no page.)

### Documents consulted

- Epic #3281 body — gap #3 ("Determinism is aspirational... no golden baselines, no byte-identical assertions, no provenance stamp, no result hash") is this issue's exact charter; sequencing places #3283 in parallel with #3284 after #3282.
- `docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md` — the envelope contract to plan against (see above).
- `.claude/rules/calc-citation-contract.md` — the `Citation` sidecar shape reused for `provenance.standard_revisions` (`source_sibling` required; default `generic` during digitalmodel migration).
- MEMORY: BSEE golden-baseline re-sanction lesson (`project_julia_field_economics_demo`, `project_bsee_ogor_refresh_mechanics`) — "golden baseline needs RE-SANCTIONING after refresh"; drives the documented refresh-requires-sign-off requirement.

### Gaps identified

- No result-hash function anywhere (`grep -rln result_hash src` → ZERO in both repos).
- No provenance stamper (code_version / standard_revisions / data_as_of assembler).
- No `golden_workflow_test(workflow_id)` helper / template; no committed golden *envelope* for any registered workflow.
- No same-input→same-output hash assertion in `tests/structural` or `tests/asset_integrity` (no `hashlib/sha256/md5` there).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3283` — OPEN, `status:needs-plan`, `lane:codex` — this issue
- `#3282` — OPEN, `status:needs-plan` — dependency; plan exists but Round-1 review = MAJOR, Round-2 pending (envelope shape not yet frozen)
- `#3281` — OPEN — parent epic

**File existence** (`ls -la` 2026-06-28):
- EXISTS: `digitalmodel/src/digitalmodel/structural/buckling_parametric.py`
- EXISTS: `digitalmodel/src/digitalmodel/asset_integrity/assessment/ffs_coordinator.py`
- EXISTS: `digitalmodel/src/digitalmodel/compare_tool/workflow.py`
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/benchmarks/golden_capture.py`
- EXISTS: `digitalmodel/src/digitalmodel/citations/{schema,registry,resolver}.py`
- MISSING (this plan creates): `assetutilities/src/assetutilities/workflow_api/{hashing,provenance,golden}.py`
- MISSING (this plan creates): `digitalmodel/tests/structural/goldens/buckling_parametric_default.json`, `digitalmodel/tests/structural/test_buckling_determinism.py`
- MISSING (depends on #3282): `assetutilities/src/assetutilities/workflow_api/{envelope,runner}.py`

**Line excerpts** (`buckling_parametric.py`):
```
 97: def _round(x: float, n: int = 4) -> float:
 98:     return round(float(x), n)
...
278:     if timestamp is not None:
279:         payload["meta"]["generated_at"] = timestamp   # <-- only volatile field; already optional
```

**Gap proofs** (2026-06-28):
- `grep -rln "result_hash" digitalmodel/src assetutilities/src` → **ZERO** — no result hash exists.
- `grep -rn "hashlib\|sha256\|md5" digitalmodel/tests/structural digitalmodel/tests/asset_integrity` → **empty** — no hash-based same-input/same-output assertion.

**Reproduction proofs** (Step 1.5 — verify the issue's runtime claim "digitalmodel has no golden baselines and no byte-identical assertions"):
```
$ cd digitalmodel
$ grep -rln "result_hash" src | grep -v __pycache__         → ZERO
$ grep -rln "golden" tests/structural tests/asset_integrity → test_panel_buckling.py, test_corroded_pipe.py,
                                                              test_ffs_validation.py, test_dnv_rp_f101.py
$ grep -n "golden" tests/structural/structural_analysis/test_panel_buckling.py
   2: # ABOUTME: ... + DNV golden case.
   7: solver to the 0119-015 DNV-RP-C201 worked example (golden numbers).
$ grep -n "byte-identity\|numeric tolerance" tests/.../benchmarks/golden_capture.py
   1: """Golden-file capture for OrcaWave byte-identity regression (#501 Sub-task 0).
   6-7: ... byte-identity test then fails on any emission drift — token-level, no numeric tolerance.
```
- Reproduced at: 2026-06-28.
- Failure mode observed matches issue claim: **PARTIALLY — refined.** The literal claim "no golden baselines and no byte-identical assertions" is **not strictly true**: (a) digitalmodel *does* have a byte-identity golden — but only for **OrcaWave input-file emission** (`golden_capture.py`, #501), not a workflow *result*; (b) the structural/FFS "golden" tests assert **golden NUMBERS** (worked-example reference values within tolerance), not same-input→same-output reproducibility. What is **genuinely absent** (and is exactly #3283's charter): a **result-hash / provenance-stamped determinism golden over a `ResultEnvelope` for a registered workflow**. The plan targets that real gap, not the over-broad claim.

(Distinct sources: issue body + 4 implementation files + #3282 plan + calc-citation rule + golden_capture precedent + grep gap-proofs = 9+.)

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3283-determinism-harness.md |
| Hashing impl | `assetutilities/src/assetutilities/workflow_api/hashing.py` |
| Provenance impl | `assetutilities/src/assetutilities/workflow_api/provenance.py` |
| Golden template impl | `assetutilities/src/assetutilities/workflow_api/golden.py` |
| Envelope wiring (coord. w/ #3282) | `assetutilities/src/assetutilities/workflow_api/envelope.py` |
| Harness tests | `assetutilities/tests/workflow_api/test_hashing.py`, `test_provenance.py`, `test_golden.py` |
| Reference golden envelope | `digitalmodel/tests/structural/goldens/buckling_parametric_default.json` |
| Reference determinism test | `digitalmodel/tests/structural/test_buckling_determinism.py` |
| Refresh/re-sanction doc | `docs/standards/2026-06-28-determinism-harness-contract.md` |
| Plan reviews | scripts/review/results/2026-06-28-plan-3283-{claude,codex,gemini}.md |
| Plan index | docs/plans/README.md |

---

## Deliverable

A shared determinism harness in `assetutilities/workflow_api` — a float-tolerance-aware `result_hash()`, a `stamp_provenance()` assembler (code_version + standard_revisions + data_as_of + input_hash), and an `assert_golden_workflow()` pytest template with a documented refresh/re-sanction procedure — proven by one committed golden envelope + passing determinism test on the digitalmodel buckling reference workflow.

---

## Pseudocode

```
# hashing.py — float-tolerance-aware, volatile-field-safe
VOLATILE_KEYS = {"generated_at", "timestamp", "run_id", "duration_s",
                 "analysis_root_folder", "host", "cwd"}        # plus path-like / ISO-8601 values
def canonicalize(obj, float_ndigits=6, drop_keys=VOLATILE_KEYS):
    # recursively: drop volatile keys; round floats to float_ndigits (generalizes _round);
    # coerce numpy/Path/AttributeDict -> plain; sort dict keys; leave list order intact
    return normalized_obj
def result_hash(result_payload, float_ndigits=6, drop_keys=VOLATILE_KEYS) -> str:
    canon = canonicalize(result_payload, float_ndigits, drop_keys)
    blob = json.dumps(canon, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + sha256(blob.encode("utf-8")).hexdigest()

# provenance.py
def stamp_provenance(input_hash, *, standard_revisions=None, data_as_of=None) -> dict:
    return {
        "code_version": code_version(),        # {package_version: importlib.metadata, git_sha: rev-parse|None}
        "standard_revisions": standard_revisions or [],   # list of Citation dicts (code_id/publisher/revision)
        "data_as_of": data_as_of,              # None for pure-calc workflows (buckling)
        "input_hash": input_hash,              # from #3282; reused, not redefined
    }
def code_version() -> dict:
    return {"package_version": metadata.version(pkg), "git_sha": git_short_sha_or_none()}

# golden.py — the test template (mirrors golden_capture.py refresh ergonomics)
def capture_golden(envelope, golden_path):           # write {result_hash, result_canonical, provenance_skeleton}
def diff_results(golden_canon, current_canon, float_tol):   # reuse compare_tool keyed-delta + max_abs_delta shape
def assert_golden_workflow(workflow_id, golden_path, *, params=None, cfg=None, float_ndigits=6):
    env = run_workflow(workflow_id, params=params, cfg=cfg)   # #3282 entrypoint (or adapter for unregistered)
    rh = result_hash(env.result, float_ndigits)
    if os.environ.get("REGEN_GOLDENS") == "1":
        capture_golden(env, golden_path); pytest.skip("golden refreshed — re-sanction required")
    golden = json.load(golden_path)
    assert rh == golden["result_hash"], diff_results(golden["result_canonical"],
                                                     canonicalize(env.result, float_ndigits), float_tol)
    return env

# digitalmodel reference test (buckling — pure, deterministic)
def test_buckling_default_sweep_is_deterministic():
    env = build_envelope_from_buckling(DEFAULT_SHIP_PLATE_SWEEP, timestamp=None)  # no clock field
    assert_golden_workflow("buckling_parametric", GOLDEN, cfg=env_cfg)            # same input -> same hash
def test_buckling_input_change_flips_hash():
    base = result_hash(run_default().result); mutated = result_hash(run_with(thickness+=1).result)
    assert base != mutated
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `assetutilities/src/assetutilities/workflow_api/hashing.py` | `canonicalize` + `result_hash` (float-tolerance, volatile-safe) |
| Create | `assetutilities/src/assetutilities/workflow_api/provenance.py` | `stamp_provenance` + `code_version` |
| Create | `assetutilities/src/assetutilities/workflow_api/golden.py` | `assert_golden_workflow` template + capture/diff |
| Modify | `assetutilities/src/assetutilities/workflow_api/envelope.py` | wire `determinism.result_hash`/`provenance` to call the harness (coordination seam with #3282) |
| Modify | `assetutilities/src/assetutilities/workflow_api/__init__.py` | export `result_hash`, `stamp_provenance`, `assert_golden_workflow` |
| Create | `assetutilities/tests/workflow_api/test_hashing.py` | hashing TDD |
| Create | `assetutilities/tests/workflow_api/test_provenance.py` | provenance TDD |
| Create | `assetutilities/tests/workflow_api/test_golden.py` | template TDD |
| Create | `digitalmodel/tests/structural/goldens/buckling_parametric_default.json` | committed reference golden envelope |
| Create | `digitalmodel/tests/structural/test_buckling_determinism.py` | reference determinism test (same-input→same-hash; mutation flips) |
| Create | `docs/standards/2026-06-28-determinism-harness-contract.md` | golden-refresh + re-sanction procedure (companion to #3067) |
| Update | `docs/plans/README.md` | add this plan's index row |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_result_hash_stable_same_input | same payload → identical hash | one result dict, hashed twice | equal `sha256:` strings |
| test_result_hash_changes_on_value | a changed numeric flips the hash | dict vs dict with one float changed beyond tol | unequal hashes |
| test_result_hash_excludes_volatile | `generated_at`/path/run_id do not affect hash | two dicts differing only in volatile keys | equal hashes |
| test_canonicalize_float_tolerance | sub-`float_ndigits` jitter does not flip | 0.1234561 vs 0.1234559 at ndigits=6 | equal hashes |
| test_canonicalize_coerces_numpy_path | numpy float / Path / AttributeDict normalize | mixed-type dict | JSON-serializable, stable |
| test_canonicalize_list_order_significant | list reordering DOES flip (order is meaningful) | `[a,b]` vs `[b,a]` | unequal hashes |
| test_code_version_shape | returns `{package_version, git_sha}`; git_sha None off-checkout | call in repo / simulated non-git | dict with both keys |
| test_stamp_provenance_passthrough_input_hash | provenance reuses #3282 `input_hash` verbatim | input_hash="x" | `provenance["input_hash"]=="x"` |
| test_stamp_provenance_standard_revisions | Citation list lands under standard_revisions | one DNV-RP-C201 Citation dict | list with that entry |
| test_assert_golden_pass | matching golden → no failure, returns envelope | envelope == committed golden | passes |
| test_assert_golden_mismatch_diffs | drift → AssertionError carrying keyed delta + max_abs_delta | golden vs mutated result | error message names the drifted key |
| test_regen_goldens_env_writes_and_skips | `REGEN_GOLDENS=1` rewrites golden + skips (re-sanction gate) | env set | golden file written; test skipped |
| test_buckling_default_sweep_is_deterministic | reference workflow re-run yields the committed hash | `DEFAULT_SHIP_PLATE_SWEEP`, timestamp=None | hash == golden |
| test_buckling_input_change_flips_hash | a deliberate input change flips `result_hash` | thickness list +1mm | hash != default golden |

---

## Acceptance Criteria

- [ ] `from assetutilities.workflow_api import result_hash, stamp_provenance, assert_golden_workflow` imports cleanly.
- [ ] One reference workflow (digitalmodel buckling) has a **committed golden envelope** (`tests/structural/goldens/buckling_parametric_default.json`) + a passing determinism test.
- [ ] Re-running the reference workflow yields an **identical `result_hash`**; a deliberate input change (thickness +1mm) **flips** it — both asserted by tests.
- [ ] `result_hash` is float-tolerance-aware (rounding to `float_ndigits`) and never hashes volatile fields (`generated_at`, paths, run_id) — covered by tests.
- [ ] Provenance stamp carries `{code_version{package_version,git_sha}, standard_revisions[], data_as_of, input_hash}`; `input_hash` is reused from #3282, not redefined.
- [ ] `docs/standards/2026-06-28-determinism-harness-contract.md` documents the golden-refresh procedure: what `REGEN_GOLDENS=1` does, what re-sanctioning requires, and owner sign-off (per the BSEE re-sanction lesson).
- [ ] `uv run pytest assetutilities/tests/workflow_api/ -v` and `uv run pytest digitalmodel/tests/structural/test_buckling_determinism.py -v` green; no regression in either suite.
- [ ] Review artifacts posted under scripts/review/results/.

---

## Adversarial Review Summary

<!-- Filled after Step 3. Not approval-ready until populated with no-MAJOR verdicts. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | |
| Codex | PENDING | |
| Gemini | PENDING | |

**Overall result:** PENDING

Revisions made based on review:
- (none yet)

---

## Risks and Open Questions

- **Risk — #3282 not frozen (top risk):** `ResultEnvelope` is at Round-1 MAJOR / Round-2 pending, and `result` *extraction* (`result_key`/`response_schema`) is an open #3282 design blocker. **Mitigation:** keep `hashing.py`/`provenance.py` as pure dict→str/dict functions that take a `result` payload, with **zero import dependency on `envelope.py`**. The envelope merely *calls* them. So #3283 can ship the harness in parallel with #3282 (as the epic's `{#3283,#3284}`-after-#3282 graph intends); only the `envelope.py` wiring line is a coordination seam. If #3282 has not landed when implementation starts, the reference test wraps buckling's pure functions into a minimal envelope-shaped dict directly. **Decision needed:** confirm with the operator that #3282 lands (or its envelope skeleton merges) before #3283's envelope-wiring edit.
- **Risk — float determinism across platforms:** bit-exact float equality is not guaranteed across BLAS/numpy builds. **Mitigation:** hash the *rounded* canonical form (`float_ndigits`, default 6, per-workflow overridable via response_schema). Document that the golden encodes a tolerance, not bit-identity — distinct from the OrcaWave byte-identity golden (which is token-level text, no float math).
- **Risk — reference-workflow choice:** buckling chosen over FFS because it is pure-Python/pandas, has no clock/path dependence (`timestamp` already optional, `buckling_parametric.py:278`), and already emits a structured `results.json`. FFS (`FFSAssessmentResult.to_dict()`) is the documented fallback if buckling cannot be driven via `run_workflow` without #3285 registration. **Open:** is buckling registered as a callable workflow id by the time this lands, or does the reference test wrap its pure functions directly? (Adoption/registration is #3285; this plan does not require it.)
- **Risk — volatile-key denylist completeness:** missing a volatile key would make the golden flaky (fails on re-run). **Mitigation:** start from the empirically-confirmed single buckling volatile field (`meta.generated_at`) + the engine's known volatiles (`analysis_root_folder`, result paths); add a test that injects each and asserts the hash is unchanged; allow per-workflow `drop_keys` override.
- **Risk — refresh becomes a rubber stamp:** `REGEN_GOLDENS=1` could silently re-bless drift. **Mitigation:** refresh skips the test (does not pass), and the contract doc requires owner sign-off before a refreshed golden is committed (BSEE re-sanction lesson). Consider a follow-on Level-2 enforcement check that a golden change in a PR carries a sign-off marker — flag as out-of-scope follow-up, not this issue.
- **Open:** `provenance.code_version` — `{package_version, git_sha}` (proposed) vs `git describe`. Inherit whatever #3282 settles for consistency; flag at review.

---

## Complexity: T3

**T3** — a foundational, ecosystem-shared harness spanning two compute repos (assetutilities harness + digitalmodel reference golden) plus a control-plane standard doc; it is the determinism guarantee the rest of epic #3281 inherits and is coupled to the still-in-flux #3282 contract. Warrants 3-provider adversarial review.
