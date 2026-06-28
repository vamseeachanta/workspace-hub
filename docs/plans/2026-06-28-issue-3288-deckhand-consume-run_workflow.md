# Plan for #3288: wf-api(deckhand) — EXECUTE leg consumes run_workflow + renders envelope [GTM payoff]

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3288
> **Epic:** https://github.com/vamseeachanta/workspace-hub/issues/3281
> **Target implementation repo:** `vamseeachanta/deckhand` (sibling — separate git repo from the tier-1 set; this workspace-hub issue is the coordination issue, the implementation PR lands in deckhand)
> **Depends on (hard, must land first):** #3297 (engine embeddability) → #3282 (`run_workflow`/`ResultEnvelope`) ; plus #3295 (registry v2 superset reserves `request_schema`) + #3284 (discovery manifest supplies `request_schema` to validate against)
> **Client:** N/A — no wiki content touched
> **Lane:** lane:claude (integration/orchestration glue between the deckhand resolver and the assetutilities workflow API; matches the issue's `lane:claude` label)
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3288-claude.md | ...-codex.md | ...-gemini.md

---

## Upstream-contract dependency (read first — this issue cannot be implemented yet)

This child **consumes** an upstream contract that has passed multi-round adversarial review (no-MAJOR) but is **owner-unapproved** (the #3282/#3297/#3295 plans sit at `status:plan-review`/`draft`). Per the epic sequencing and the per-issue extra-gate convention (cf. #3066 for assethold), this plan is drafted to the contract **as specified** and does **not** redesign it. The hard ordering is:

```
#3297 (engine embeddable)  →  #3282 (assetutilities.workflow_api.run_workflow + ResultEnvelope)  →  #3288 (THIS: deckhand consumes it)
#3295 (registry v2 superset: reserves request_schema)  ┐
#3284 (discovery manifest: passthrough request_schema) ┘ →  #3288 param validation
```

**#3288 cannot be implemented before #3282 lands** (the symbol `assetutilities.workflow_api.run_workflow` does not exist — verified absent below). The param-validation acceptance criterion additionally depends on #3295 reserving `request_schema` and #3284 surfacing it; until a registry row populates `request_schema`, validation degrades **fail-open with a warning** (no schema ⇒ nothing to validate) and is **fail-closed only when a schema is present and params violate it**. The implementation tests are written test-first against an **injected** `run_workflow` stub (mirroring the existing `runner=`/`clock=` injection in `capability_smoke.run_workflow`) so the deckhand suite stays hermetic and green without the assetutilities dependency, then the live wiring goes green once #3282 ships.

---

## Resource Intelligence Summary

### Existing repo code (verified 2026-06-28 against `/mnt/local-analysis/deckhand` @ `1c8524b`, branch `main`)

- **The current EXECUTE leg is subprocess-shell + file-presence PASS/FAIL — NOT a typed envelope.** `deckhand/src/deckhand/capability_smoke.py:293-358` `run_workflow(resolved, *, timeout, clock, runner=subprocess.run)` shells out the resolved `argv` (`uv run python -m <pkg> <input>`) via `subprocess.run(... capture_output=True ...)` (`:320-326`) in the compute checkout, then declares **PASS** = `exit 0 AND every declared output file present` (`:339-349`). The result type `RunResult` (`:271-290`) carries only `{ref, status: PASS|FAIL|ERROR|SKIPPED, returncode, duration_s, outputs_present, detail, stdout_tail}` — **no `result` payload, no `provenance`, no `determinism` hash, no `confidence`, no structured `warnings`**. This is the "bespoke per-workflow results.json parsing" the issue replaces: the run is judged by exit code + output-file existence, and the typed answer is never surfaced.
- **The resolver this plan builds on.** `capability_smoke.resolve_workflow(ref, *, compute_base, cta, domain, subdomain) -> ResolvedWorkflow` (`:167-242`) parses `<repo>:<workflow-id>[@<version>]` (`_parse_ref`, `:117-130`), selects latest-stable (`_select_version`, `:146-164`), reads the per-row `input` (fails closed when absent — `:221-228`), and builds `argv` from the **top-level** `invocation` template via `template.replace("{input}", input_rel)` (`{input}`-only — `:231-233`). `ResolvedWorkflow` exposes `repo`, `workflow_id` (the bare id, no repo prefix or version), `resolved_version`, `coordinate` (`:85-96`), `outputs`, `input_path`, `argv`, `compute_root`, `runtime`, `firable` (`:81-82`, `ok AND runtime in OFFLINE_RUNTIMES`). **`workflow_id` is exactly the bare id `assetutilities.workflow_api.run_workflow(workflow_id, ...)` expects** — this is the key reuse: keep `resolve_workflow` as the resolver, add an in-process executor that calls `run_workflow(resolved.workflow_id, params)` instead of shelling `argv`.
- **The render surface.** `capability_smoke_serve.py:70-111` `run_payload(ref, routing_dir, *, compute_base, timeout, domain, subdomain, published_relpath, pages_base)` is the one place a run result becomes a JSON response today: it calls `cs.run_workflow(rw, timeout=timeout).as_dict()` (`:89`), stamps `result["coordinate"] = rw.coordinate` (`:92`), adds `artifacts` (declared outputs + presence, `_artifacts_for` `:51-67`) and a `report_url` (publish-time, `:101-110`). `API_SPEC` (`:117-184`) documents the `/api/run` request/response shape. This is where the envelope fields (`result`/`provenance`/`determinism`/`confidence`/`warnings`) must be threaded so "chat → typed deterministic answer" is visible.
- **Test conventions.** `tests/deckhand/test_capability_smoke.py` uses a `fake_base` `tmp_path` registry fixture (`:29-50`) + an **injected `runner=`/`clock=`** to unit-test the PASS/FAIL logic with no real compute (`:81-120`). The new in-process executor mirrors this exactly: an **injected `run_workflow` importer** so the deckhand suite never imports assetutilities. There is no `tests/deckhand/test_capability_execute.py` yet (new).
- **Gap — the in-process path does not exist.** No deckhand module imports a `workflow_api`, references `ResultEnvelope`, or renders `provenance`/`determinism` (`grep` over `src/deckhand/*.py` finds only docstring uses of the word "provenance"; no `ResultEnvelope`, no in-process `run_workflow(` consumption).
- **Gap — the upstream symbol does not exist yet.** `assetutilities/src/assetutilities/workflow_api/` is **absent** (`ls` → "No such file or directory") — it is #3282's greenfield deliverable.
- **Note — deckhand has no `docs/registry/`.** The registries the resolver reads live in the *compute checkouts* under `DEFAULT_COMPUTE_BASE = /mnt/local-analysis/.deckhand-compute` (`capability_smoke.py:35-38`). The `request_schema` deckhand validates against comes from the resolved compute-checkout registry row (and/or the #3284 ecosystem manifest), not from a deckhand-local registry.

### In-process scope boundary (load-bearing design fact)

`assetutilities.workflow_api.run_workflow` runs **assetutilities-registry** workflows via the #3282/#3297 embed path (it imports `assetutilities.engine`). It is **package-local**: it does not run digitalmodel/worldenergydata/assethold workflows. Deckhand's EXECUTE leg, by contrast, resolves `<repo>:<id>` across **all four** repos. Therefore #3288's in-process path applies **only to repos that expose a `<pkg>.workflow_api.run_workflow`** — assetutilities first; worldenergydata is slated to adapt the envelope (#3286); digitalmodel/assethold have no such API yet. The executor must therefore:
1. resolve the target package's `run_workflow` (assetutilities canonical); if the repo exposes none, **degrade gracefully to the existing subprocess `capability_smoke.run_workflow`** (PASS/FAIL + artifacts) rather than failing the run.
2. never claim an envelope it didn't get.
This boundary is the single biggest correctness risk and is encoded as an explicit fallback + test, not papered over.

### Standards
Not applicable — integration/harness glue, no engineering calculation. `provenance.standard_revisions` is an envelope field **produced upstream by #3282** and merely rendered here; #3288 introduces no standards-derived constant, so the calc-citation contract (`.claude/rules/calc-citation-contract.md`) does not fire.

### LLM Wiki pages consulted
None — control-plane integration, no domain knowledge added. `Client: N/A` confirmed.

### Documents consulted
- Epic [#3281](https://github.com/vamseeachanta/workspace-hub/issues/3281) — "Deterministic Workflow API"; #3288 is the closing GTM child (chat → typed deterministic answer).
- #3282 plan (`docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md`) — the consumed contract: `from assetutilities.workflow_api import run_workflow, ResultEnvelope`; `run_workflow(workflow_id, params=None, cfg=None) -> ResultEnvelope`; envelope = stdlib dataclass `{workflow_id, status, result, provenance{code_version{package_version,git_sha}, standard_revisions[], data_as_of, input_hash}, determinism{result_hash, reproducible}, confidence, warnings}` with `to_dict()`/`from_dict()`. #3282 OWNS the determinism fields + the `result:` descriptor; returns `status=="error"` envelopes (fail-closed) rather than raising.
- #3297 plan (`docs/plans/2026-06-28-issue-3297-engine-embeddability.md`) — PREREQ for #3282; #3288 does not touch the engine.
- #3295 plan (`docs/plans/2026-06-28-issue-3295-registry-schema-v2-reconcile.md`) — reserves `request_schema`/`response_schema` as **structured, untyped** slots (no `str` invariant); adds the required top-level `invocation:` key; names `capability_smoke.py` the reference resolver.
- #3284 plan (`docs/plans/2026-06-28-issue-3284-discovery-manifest.md`) — `workflow-manifest.json` passes `request_schema` through structurally (null when absent, **no `str` coercion**); supplies the schema deckhand validates against; `workflow_id = repo:id@version` + `latest_by_routing_id`.
- Cross-links from the issue body: #2933 (gateway availability), #3239 (Deckhand deliverables from the reporting block library), #1066 (the digitalmodel `results.json` index consumption this replaces).

### Gaps identified
- No deckhand in-process executor that calls `<pkg>.workflow_api.run_workflow` and renders an envelope (greenfield — new `capability_execute.py`).
- No param-validation boundary that checks `params` against a registry `request_schema` and fails closed on violation.
- No envelope→response renderer (`provenance`/`determinism`/`confidence`/`warnings` → the serve payload + chat surface).
- No graceful in-process→subprocess fallback for repos without a `workflow_api`.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3288` — OPEN, `status:needs-plan`, `lane:claude` — this issue ("wf-api(deckhand): EXECUTE leg consumes run_workflow + renders envelope [GTM payoff]").
- `#3282` — OPEN, `status:plan-review` (owner-unapproved) — the consumed `run_workflow`/`ResultEnvelope`.
- `#3297` — OPEN — engine embeddability (PREREQ for #3282).
- `#3295` — OPEN — registry v2 superset (reserves `request_schema`).
- `#3284` — OPEN — discovery manifest (supplies `request_schema`).
- `#3281` — OPEN — parent epic.

**File existence** (`ls`/`git` 2026-06-28):
- EXISTS: `deckhand/src/deckhand/capability_smoke.py` (366 lines, the resolver + subprocess executor), `deckhand/src/deckhand/capability_smoke_serve.py` (the render surface), `deckhand/tests/deckhand/test_capability_smoke.py`.
- MISSING (the upstream dependency — #3282 creates): `assetutilities/src/assetutilities/workflow_api/` → `ls` returns "No such file or directory".
- MISSING (this plan creates, in the deckhand repo): `deckhand/src/deckhand/capability_execute.py`, `deckhand/tests/deckhand/test_capability_execute.py`.
- deckhand HEAD `1c8524b2f498175f3b8ddc780b67015b22f224f8`, branch `main`, origin `https://github.com/vamseeachanta/deckhand`.

**Line excerpts** (`grep`/`sed` 2026-06-28):
```
capability_smoke.py:293-298  def run_workflow(resolved, *, timeout=600.0, clock=time.monotonic, runner=subprocess.run)
capability_smoke.py:320      proc = runner(resolved.argv, cwd=str(resolved.compute_root), capture_output=True, ...)
capability_smoke.py:342      if proc.returncode == 0 and outputs_present:  status, detail = "PASS", ""
capability_smoke.py:271-279  class RunResult: ref/status/returncode/duration_s/outputs_present/detail/stdout_tail   # NO provenance/determinism/result
capability_smoke_serve.py:89 result = cs.run_workflow(rw, timeout=timeout).as_dict()
capability_smoke_serve.py:92 result["coordinate"] = rw.coordinate
```

**Gap proof:**
- `ls assetutilities/src/assetutilities/workflow_api` → "No such file or directory" → the consumed symbol does not exist yet (hard dependency on #3282).
- `grep -rn "ResultEnvelope" deckhand/src/deckhand` → empty → no in-process consumption today.

**Reproduction proofs:** see Step 1.5 below.

<!-- Distinct sources: issue #3288 body + #3282 plan + #3297 plan + #3295 plan + #3284 plan + capability_smoke.py + capability_smoke_serve.py + test_capability_smoke.py + assetutilities workflow_api absence = 9 (≥3 required). -->

---

## Step 1.5 — Reproduction (verify-against-repo-state)

**Claims under test:** (a) the current EXECUTE leg is subprocess + file-presence PASS/FAIL with no typed envelope; (b) the in-process `run_workflow`/`ResultEnvelope` path does not exist in deckhand; (c) the upstream `assetutilities.workflow_api.run_workflow` symbol this issue consumes does not exist yet.

```
$ grep -n "def run_workflow\|subprocess.run\|capture_output" deckhand/src/deckhand/capability_smoke.py
293:def run_workflow(
298:    runner=subprocess.run,
323:            capture_output=True,
# -> current execute leg shells out; RunResult (sed 271-290) has no result/provenance/determinism field.

$ ls -la assetutilities/src/assetutilities/workflow_api 2>&1; echo exit=$?
ls: cannot access '.../workflow_api': No such file or directory
exit=2
# -> the consumed assetutilities.workflow_api.run_workflow / ResultEnvelope do NOT exist (created by #3282).

$ grep -rn "ResultEnvelope\|provenance\|determinism" deckhand/src/deckhand/capability_smoke.py deckhand/src/deckhand/capability_smoke_serve.py
# -> only docstring uses of "provenance"; no ResultEnvelope, no determinism rendering today.
```

- Reproduced at: 2026-06-28 (deckhand @ `1c8524b`).
- Failure mode observed matches issue claim: **YES** — the in-process envelope path is genuinely absent, and the dependency type it would call is not yet built. This is the gap #3288 closes; it is **blocked** on #3282 landing (cannot run the new path end-to-end until then). The deckhand-side adapter, param validation, envelope rendering, and the in-process→subprocess fallback are all independently buildable + testable now against an injected `run_workflow` stub; the live wiring goes green when #3282 ships.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3288-deckhand-consume-run_workflow.md |
| In-process executor + validator + renderer (NEW, deckhand repo) | `deckhand/src/deckhand/capability_execute.py` |
| Render surface (MODIFY, deckhand repo) | `deckhand/src/deckhand/capability_smoke_serve.py` |
| Tests (NEW, deckhand repo) | `deckhand/tests/deckhand/test_capability_execute.py` |
| Resolver (read-only reuse — NOT edited) | `deckhand/src/deckhand/capability_smoke.py` |
| Consumed upstream contract (NOT edited here) | `assetutilities/src/assetutilities/workflow_api/` (#3282) |
| Plan review — Claude | scripts/review/results/2026-06-28-plan-3288-claude.md |
| Plan review — Codex | scripts/review/results/2026-06-28-plan-3288-codex.md |
| Plan review — Gemini | scripts/review/results/2026-06-28-plan-3288-gemini.md |
| Plans index (MODIFY, workspace-hub) | docs/plans/README.md |

---

## Deliverable

A `deckhand/src/deckhand/capability_execute.py` module that turns a resolved `<repo>:<workflow-id>` plus a `params` dict into a **typed, deterministic, provenance-stamped answer**: it (1) **validates `params` against the workflow's `request_schema`** (from the resolved compute-checkout registry row / #3284 manifest) and **fails closed** on violation with a structured error (no stack trace), (2) imports the target repo's `<pkg>.workflow_api.run_workflow` and calls `run_workflow(resolved.workflow_id, params) -> ResultEnvelope` **in-process** (replacing the subprocess shell-out for repos that expose the API), (3) **renders the envelope** (`result` + `provenance{code_version, standard_revisions, data_as_of, input_hash}` + `determinism{result_hash, reproducible}` + `confidence` + `warnings`) into the chat/report response surface, and (4) **degrades gracefully** to the existing subprocess `capability_smoke.run_workflow` for repos without a `workflow_api`. Wired into `capability_smoke_serve.run_payload` so a single `/api/run` call returns the rendered envelope, all TDD-covered against an injected `run_workflow` stub.

---

## Pseudocode

```python
# ── deckhand/src/deckhand/capability_execute.py ───────────────────────────────
from deckhand import capability_smoke as cs   # reuse the resolver + the subprocess fallback

# --- package -> in-process API resolution (assetutilities canonical; others as they adopt) ---
def resolve_run_workflow(resolved, *, importer=importlib.import_module):
    """Return the target repo's workflow_api.run_workflow callable, or None.
    pkg is derived from the invocation template ('uv run python -m <pkg> {input}'),
    falling back to the repo slug. None => caller degrades to subprocess."""
    pkg = _pkg_from_invocation(resolved) or resolved.repo   # e.g. "assetutilities"
    try:
        mod = importer(f"{pkg}.workflow_api")
        return getattr(mod, "run_workflow", None)
    except ImportError:
        return None                                         # repo has no in-process API (digitalmodel/assethold today)

# --- fail-closed param validation against the registry request_schema (#3284/#3282) ---
def validate_params(request_schema, params) -> list[str]:
    """Return a list of human violations (empty == valid).
    request_schema is the STRUCTURED, UNTYPED slot reserved by #3295 and shaped by #3282.
    Contract here: fail-OPEN when absent (None/{} => no schema => [] + caller warns),
    fail-CLOSED when present and params violate. Do NOT redefine the schema shape —
    consume whatever #3282 emits. v1 validator: if it looks like JSON Schema
    (has 'type'/'properties'), validate via jsonschema; else treat as opaque and
    pass through with a 'request_schema present but unrecognized shape' note."""
    if not request_schema:
        return []                                           # nothing to validate (pre-#3282 registries)
    if _looks_like_json_schema(request_schema):
        return _jsonschema_violations(request_schema, params or {})
    return []   # opaque structured schema -> accept; record a warning at the call site

# --- the in-process EXECUTE leg (the crux) ---
def run_envelope(resolved, params=None, *, request_schema=None,
                 importer=importlib.import_module, run_workflow=None) -> dict:
    """Resolve -> validate -> in-process run_workflow -> render envelope.
    `run_workflow` is INJECTABLE for hermetic tests (mirrors capability_smoke's runner=)."""
    if not resolved.ok:
        return _error_response(resolved.ref, f"unresolved: {resolved.reason}")
    # 1) fail-closed param validation
    violations = validate_params(request_schema, params)
    if violations:
        return _error_response(resolved.ref, "invalid params", warnings=violations)  # NOT a traceback
    # 2) resolve the in-process API (or signal fallback)
    fn = run_workflow or resolve_run_workflow(resolved, importer=importer)
    if fn is None:
        return None                                         # sentinel: caller degrades to subprocess
    # 3) call run_workflow(bare_id, params) in-process; #3282 returns an envelope, never raises
    try:
        envelope = fn(resolved.workflow_id, params=params)  # ResultEnvelope (stdlib dataclass)
    except Exception as exc:                                # defense-in-depth: #3282 shouldn't raise, but never leak a trace
        return _error_response(resolved.ref, f"run_workflow raised: {exc}")
    return render_envelope(resolved, envelope)

# --- envelope -> chat/report response (the "typed deterministic answer") ---
def render_envelope(resolved, envelope) -> dict:
    e = envelope.to_dict() if hasattr(envelope, "to_dict") else dict(envelope)
    det = e.get("determinism") or {}
    prov = e.get("provenance") or {}
    return {
        "ref": resolved.ref,
        "status": "PASS" if e.get("status") == "ok" else "FAIL",  # back-compat with the serve console status field
        "engine": "in-process",                              # vs "subprocess" — so the surface knows which path ran
        "result": e.get("result"),                           # the DECLARED typed payload (#3282 result: descriptor)
        "provenance": prov,                                  # code_version{package_version,git_sha}, standard_revisions[], data_as_of, input_hash
        "determinism": {                                     # surfaced so the answer is DEFENSIBLE (issue AC)
            "result_hash": det.get("result_hash"),
            "reproducible": det.get("reproducible"),
        },
        "confidence": e.get("confidence"),
        "warnings": e.get("warnings") or [],
        "coordinate": resolved.coordinate,
        "envelope": e,                                       # full envelope passthrough for richer renderers (#3239)
    }

def _error_response(ref, detail, warnings=None) -> dict:
    return {"ref": ref, "status": "FAIL", "engine": "in-process",
            "result": None, "provenance": {}, "determinism": {}, "confidence": None,
            "detail": detail, "warnings": warnings or [detail]}

# ── deckhand/src/deckhand/capability_smoke_serve.py (run_payload — additive branch) ──
def run_payload(ref, routing_dir, *, compute_base=None, timeout=600.0,
                domain=None, subdomain=None, params=None,
                published_relpath=None, pages_base=None):
    rw = cs.resolve_workflow(ref, compute_base=compute_base, cta=..., domain=domain, subdomain=subdomain)
    # NEW: in-process envelope path when params are supplied AND the repo exposes a workflow_api.
    if params is not None:
        request_schema = _request_schema_for(rw)            # read row['request_schema'] from the resolved registry / #3284 manifest
        env = capability_execute.run_envelope(rw, params, request_schema=request_schema)
        if env is not None:                                 # in-process path ran (or fail-closed)
            env.setdefault("report_url", None)
            return env
    # FALLBACK: existing subprocess PASS/FAIL + artifacts + report_url (unchanged).
    result = cs.run_workflow(rw, timeout=timeout).as_dict()
    result["coordinate"] = rw.coordinate
    result["engine"] = "subprocess"
    ... existing artifacts / report_url logic unchanged ...
    return result
```

> Note: `run_envelope` returns `None` **only** as the "no in-process API → degrade to subprocess" sentinel; every other path (unresolved, invalid params, run error, success) returns a dict. The `params is not None` gate keeps the existing no-params console behavior (subprocess PASS/FAIL) byte-identical — the envelope path is strictly additive.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `deckhand/src/deckhand/capability_execute.py` | in-process executor: `resolve_run_workflow`, `validate_params` (fail-closed), `run_envelope`, `render_envelope`, `_error_response`, `_pkg_from_invocation`, `_request_schema_for` |
| Modify | `deckhand/src/deckhand/capability_smoke_serve.py` | `run_payload` gains a `params=` arg + the additive in-process branch; `do_POST` parses `params`; `API_SPEC` `/api/run` documents `params` + the envelope response (`result`/`provenance`/`determinism`/`confidence`/`warnings`/`engine`) |
| Create | `deckhand/tests/deckhand/test_capability_execute.py` | TDD with an injected `run_workflow` stub + a fake `ResultEnvelope`-shaped object (`.to_dict()`) — hermetic, no assetutilities import |
| Update | `workspace-hub/docs/plans/README.md` | add this plan's index row |

> **No assetutilities/digitalmodel/worldenergydata edits here.** #3288 only *imports and calls* `<pkg>.workflow_api.run_workflow`. The resolver `capability_smoke.py` is reused read-only. The implementation diff is confined to deckhand (two source files + one test) plus the workspace-hub plan index.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_run_envelope_renders_typed_answer | success path renders `result`+`provenance`+`determinism`+`confidence`+`warnings` from an injected envelope | resolved + stub `run_workflow` returning a fake ok envelope | dict with `status=="PASS"`, `engine=="in-process"`, populated `result`/`provenance`/`determinism.result_hash` |
| test_determinism_surfaced_for_defensibility | `result_hash` + `reproducible` reach the rendered response (issue AC) | ok envelope w/ `determinism={result_hash:"abc",reproducible:true}` | response `determinism == {result_hash:"abc", reproducible:true}` |
| test_invalid_params_fail_closed_not_traceback | params violating a JSON-Schema `request_schema` are rejected as a structured error | request_schema requiring `depth:number`, params `{depth:"deep"}` | `status=="FAIL"`, `detail=="invalid params"`, `warnings` non-empty, **no exception** |
| test_valid_params_pass_validation | params satisfying the schema proceed to run | schema + valid params | reaches `run_workflow`, returns ok response |
| test_absent_request_schema_fails_open | no `request_schema` ⇒ no validation, params passed through | `request_schema=None`, any params | `run_workflow` called; no validation error |
| test_opaque_structured_schema_accepted_with_note | a structured-but-non-JSON-Schema `request_schema` is accepted (no `str` invariant — D1) and noted | `request_schema={"$ref":"..."}` | params accepted; a warning records the unrecognized shape |
| test_no_workflow_api_degrades_to_subprocess | a repo without `<pkg>.workflow_api` returns the `None` sentinel so the caller falls back | importer raising `ImportError` | `run_envelope(...) is None` |
| test_passes_bare_workflow_id_not_repo_prefixed | `run_workflow` is called with `resolved.workflow_id` (bare id), not `repo:id@ver` | resolved `assetutilities:data_exploration` | stub asserts it received `"data_exploration"` + the params dict |
| test_run_workflow_error_envelope_rendered_not_raised | a stub envelope with `status=="error"` renders FAIL with warnings, not a crash | stub returns error envelope | `status=="FAIL"`, `warnings` carries the envelope message |
| test_run_workflow_unexpected_raise_is_caught | defense-in-depth: a raising stub yields a structured error, not a traceback | stub raises `RuntimeError` | `status=="FAIL"`, `detail` names the failure |
| test_unresolved_ref_is_error_response | an unresolved `ResolvedWorkflow` returns a structured error before any import | `resolved.ok=False` | `status=="FAIL"`, `detail` carries the resolve reason |
| test_pkg_derived_from_invocation_template | package name parsed from `uv run python -m <pkg> {input}`, fallback to repo slug | invocation `"uv run python -m assetutilities {input}"` | pkg `=="assetutilities"` |
| test_serve_run_payload_in_process_when_params | `run_payload(..., params={...})` returns the rendered envelope when the API resolves | fake_base + injected envelope | response carries `provenance`/`determinism`; `engine=="in-process"` |
| test_serve_run_payload_no_params_keeps_subprocess | `run_payload(...)` with no params is byte-compatible with today (subprocess PASS/FAIL + artifacts) | fake_base + injected runner | `engine=="subprocess"`, `artifacts` present, no `provenance` key required |
| test_api_spec_documents_params_and_envelope | `/api/run` spec lists `params` request + the envelope response fields | `spec_payload()` | the `/api/run` entry mentions `params`, `provenance`, `determinism` |

---

## Acceptance Criteria

- [ ] **#3282 (and its prereq #3297) have landed** — `from assetutilities.workflow_api import run_workflow, ResultEnvelope` works. #3288 does not merge before #3282.
- [ ] **At least one live workflow answerable end-to-end from the EXECUTE leg via in-process `run_workflow` + envelope render** — demonstrated on an assetutilities registry workflow (e.g. `assetutilities:data_exploration`): `run_payload(ref, params={...})` returns a rendered envelope, proven by a passing test (live wiring) once #3282 ships; hermetic tests pass now against the injected stub.
- [ ] **Invalid params are rejected against the `request_schema` (fail-closed, not a stack trace)** — when a row carries a `request_schema`, violating params return a structured error (`status=="FAIL"`, `detail`, `warnings`); valid params proceed; absent schema fails open with a warning; a structured-but-non-JSON-Schema schema is accepted untyped (no `str` invariant, per #3295 D1).
- [ ] **Envelope provenance + determinism are visible in the rendered answer** — `provenance.code_version{package_version,git_sha}`, `standard_revisions`, `data_as_of`, `input_hash`, and `determinism{result_hash, reproducible}` reach the response so the answer is defensible (the GTM payoff).
- [ ] **In-process path is package-local + degrades gracefully** — repos exposing `<pkg>.workflow_api.run_workflow` (assetutilities) use the in-process envelope path; repos without it (digitalmodel/assethold today) fall back to the existing subprocess `capability_smoke.run_workflow` with no regression.
- [ ] **`run_workflow` is called with the bare `resolved.workflow_id`** (not `repo:id@version`), matching the assetutilities registry id contract.
- [ ] **No-params behavior is byte-compatible** with today's subprocess PASS/FAIL + artifacts + report_url path (the envelope path is strictly additive, gated on `params is not None`).
- [ ] `uv run pytest deckhand/tests/deckhand/test_capability_execute.py -v` green; `deckhand/tests/deckhand/test_capability_smoke.py` shows no regression.
- [ ] Review artifacts posted under `scripts/review/results/`.

---

## Adversarial Review Summary

<!-- PENDING — plan drafted to the upstream contract as specified; not surfaced to user until cross-review returns no-MAJOR. Status stays draft. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING (cross-review not yet run; plan stays `draft`, never self-approved). Implementation is additionally gated behind (a) USER approval and (b) **#3282 + #3297 landing first** (hard dependency), with #3295 + #3284 needed for the request-schema validation criterion.

---

## Risks and Open Questions

- **Risk — hard upstream dependency (owner-unapproved contract).** #3288 consumes `assetutilities.workflow_api.run_workflow`/`ResultEnvelope`, which do not exist yet (#3282 greenfield, at `status:plan-review`, owner-unapproved). Mitigation: build + test the deckhand adapter, validator, renderer, and fallback now against an **injected** `run_workflow` stub (hermetic, no assetutilities import); the live wiring goes green only after #3282 lands. The plan consumes the contract **as specified** and does not redesign it; if #3282's envelope field names shift during its own review, a fast follow-up adjusts `render_envelope` (the only coupling point).
- **Risk — in-process scope is package-local, not ecosystem-wide.** `assetutilities.workflow_api.run_workflow` runs only assetutilities-registry workflows. digitalmodel/worldenergydata/assethold have no `workflow_api` yet (worldenergydata is slated via #3286). Mitigation: `resolve_run_workflow` returns `None` for repos without the API and the caller degrades to the existing subprocess path — no run is broken, the typed-answer upgrade simply lands repo-by-repo as each adopts the API. Encoded by `test_no_workflow_api_degrades_to_subprocess`.
- **Risk — `request_schema` shape is #3282-owned and currently unpopulated.** No registry row carries `request_schema` today (#3284 confirms null passthrough). Mitigation: `validate_params` fails open when absent (warning) and fails closed only when present-and-violated; it does **not** impose a `str` invariant (respects #3295 D1) and treats unrecognized structured schemas as opaque-accept-with-note. The concrete JSON-Schema validator path (`jsonschema`) is the v1 recognizer; if #3282 defines a non-JSON-Schema shape, the recognizer extends without changing the fail-open/fail-closed contract. **Open question for the user:** should an *unrecognized* structured `request_schema` be opaque-accept (current plan, forward-compatible) or fail-closed (stricter, but blocks runs until the recognizer is taught the shape)? Recommendation: opaque-accept-with-warning until #3282 fixes the shape, then tighten.
- **Risk — `jsonschema` dependency.** The fail-closed validator may need `jsonschema`. Mitigation: import it lazily; if unavailable, degrade to a minimal required-keys/type check and record a warning (do not hard-fail the run on a missing dev dep). Confirm whether deckhand already vendors a validator before adding a dependency.
- **Risk — live-chat rendering surface beyond `run_payload`.** The live EXECUTE dispatch (deckhand#275) renders inside a `delegate_task` subagent prompt + the reporting block library (#3239), not only the localhost serve console. Mitigation: #3288 lands the pure `render_envelope` + the `run_payload` wiring (the testable, deterministic surface); threading the rendered envelope into the live chat/report templates (chat_provenance.py / report_templates.py / response_packaging.py) is cross-linked to #3239 and can be a fast follow-on once the renderer exists. Flag for the user whether the live-chat wiring must be in this PR or a follow-on.
- **Risk — version pinning.** assetutilities registry rows are all v1, so `resolved.workflow_id` (bare id) suffices. A future versioned in-process API (digitalmodel `mooring-fatigue` v1/v2) would need the version threaded into the call; out of scope until a versioned repo exposes `workflow_api`. Noted, not built.

**Open Questions for approval:**
1. Unrecognized structured `request_schema`: opaque-accept-with-warning (recommended) vs fail-closed?
2. Live-chat rendering (chat_provenance/report_templates wiring) in this PR or a #3239 follow-on?

---

## Complexity: T2

**T2** — one new deckhand module + an additive branch in the serve render surface + one new test file, TDD throughout, consuming the #3282 contract with **zero** upstream edits. Flagged for **elevated (T2→T3-depth) review** because it is the GTM-closing integration of epic #3281 and sits on an owner-unapproved upstream contract with a real cross-repo scope boundary (package-local in-process API + graceful subprocess fallback).
