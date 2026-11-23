# Plan for #3284: wf-api(ecosystem) — discovery manifest (aggregate callable workflows + schemas across repos)

> **Status:** draft
> **Complexity:** T2 (one new generator module + tests + manifest artifact + schema doc; control-plane, contained blast radius)
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3284
> **Epic:** https://github.com/vamseeachanta/workspace-hub/issues/3281
> **Client:** N/A — no wiki content touched
> **Project:** (none)
> **Lane:** lane:claude (aggregation/contract tooling; light edits — matches the issue's `lane:claude` label)
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3284-claude.md | ...-codex.md | ...-gemini.md

---

## Decisions Applied (owner-confirmed 2026-06-28 — baked in, not re-litigated)

These cross-cutting epic decisions are SETTLED and are reflected throughout this plan (they are no longer open questions):

- **D1 (schema, #3295/#3282):** `schema_version` STAYS **2** as an additive superset (deckhand routing triple `version`/`status`/`latest` + new fields). **No v3 bump.** `request_schema`/`response_schema` are **structured descriptors — NOT typed strings, NO `str` invariant**; #3295 RESERVES those slots (structured/untyped) pending #3282, which OWNS their shape. The result LOCATION is a registry `result:` descriptor `{kind: in_memory|files, key: <cfg key> | outputs: [...]}` — OWNED by #3282. `invocation:` IS a **required top-level registry key**; assetutilities' value (added by #3295) will be exactly `"uv run python -m assetutilities {input}"` with **`{input}`-only substitution**. `deckhand/src/deckhand/capability_smoke.py` is the **reference resolver** and is named as such in the schema doc + README.
- **D2 (CI caching, #3291):** out of scope for #3284 — this plan touches **no CI/workflow files** and makes **no package-manager swap**. (#3291 owns the cache adds.)
- **D3 (determinism ownership, #3282 vs #3283):** #3282 OWNS envelope determinism FIELDS (`input_hash`, `result_hash`, computed `reproducible`, `provenance.code_version`). #3283 OWNS the golden harness + volatile-field spec = **key-allowlist only, NEVER value heuristics**. Therefore this manifest does **NOT** infer a determinism status from registry heuristics (the prior `assertions`-presence heuristic is removed); the determinism/golden field is a **reserved passthrough** (null until populated).
- **D4 (discovery, #3284 — this issue):** `workflow_id = "repo:id@version"` plus a **`latest` resolver**; **PRESERVE per-row `input`**; the **license-gated flag derives from `runtime == 'requires-license'`** (NOT `network_required`).
- **D5 (governance, #3296):** out of scope for #3284.
- **D6 (sequencing):** **#3283 is DEFERRED to Wave 2** — not in this wave. The determinism/golden field is therefore reserved-passthrough-null in this manifest and is populated by #3283 in Wave 2.

---

## Resource Intelligence Summary

### Existing repo code

- Found: `assetutilities/docs/registry/workflows.yaml` — `schema_version: 1`, 9 rows; row keys `{id, basename, input, outputs, runtime, test}`; `runtime: fast` (×9). **No top-level `invocation` key** (per-row `test:` only); **no `version`/`latest`/`requires-license`**. (#3295 will reconcile this to the v2 superset and add `invocation: "uv run python -m assetutilities {input}"`.)
- Found: `digitalmodel/docs/registry/workflows.yaml` — `schema_version: 2`; top-level `invocation: "uv run python -m digitalmodel {input}"`; **111 rows**; `runtime: offline` (×109) and **`runtime: requires-license` (×2, lines 425 + 602)** — the real license gate. Carries the deckhand routing triple: e.g. `mooring-fatigue` appears **TWICE** — `version: 1 / status: stable / latest: true` and `version: 2 / status: experimental`. This is the concrete duplicate-`id` case that forces `repo:id@version` keys.
- Found: `worldenergydata/docs/registry/workflows.yaml` — `schema_version: 2`; top-level `invocation: "uv run python -m worldenergydata {input}"`; 9 rows; `runtime: offline` (×9, **no** `requires-license`). Rows carry a `data_source:` block (`type: bundled-fixture`, `network_required: false`, `fixtures: [...]`) and an `assertions:` block. **Per D4 this `network_required` is a network/fixture concern, NOT the license gate** — it is passed through informationally but does not set `license_gated`.
- Found: `assethold/docs/registry/workflows.yaml` — `schema_version: 1`, 7 rows; `runtime: uv-python`; **no top-level `invocation`**, no version/latest.
- Found: `deckhand/src/deckhand/capability_smoke.py` (366 lines) — **the reference resolver** (D1). It parses `<repo>:<workflow-id>[@<version>]` (`_parse_ref`), selects latest-stable when unpinned (`_select_version`: `latest: true` flagged stable row → else highest stable version → else highest of any status; unversioned row = v1 by contract via `_row_version`), reads per-row `input` (fails closed if absent — `"registry row has no input file"`), and renders the run command from the **top-level** `invocation` template via `template.replace("{input}", input_rel)` (`{input}`-only substitution). `OFFLINE_RUNTIMES = {"offline", "", None}`; other runtimes resolve but are reported "registered but not offline-firable". **This manifest's field-set is chosen to be exactly what this resolver consumes**, so a consumer can round-trip a manifest entry through `resolve_workflow()`.
- Found: `scripts/lib/tier1_repos.py` — `tier1_python_repos()` reads `config/tier1-python-repos.txt` (SSoT, #3023); `resolve_tier1_repo_path(slug)` resolves a slug across layouts, fail-closed on missing. **Direct reuse** — the generator must NOT hardcode `/mnt/local-analysis/<repo>` paths (banned by `.claude/rules/coding-style.md`; enforced by `scripts/enforcement/check-no-abs-paths.sh`).
- Found: `config/tier1-python-repos.txt` — `assetutilities`, `digitalmodel`, `worldenergydata`, `assethold` (4 slugs) = the manifest's repo iteration set.
- Found: `scripts/workflow/` exists (completeness/plan-gate tooling); the generator lands here. `scripts/workflow/tests/` exists for TDD.
- Gap: workspace-hub has **no** `docs/registry/` directory; this plan creates it to host the ecosystem manifest + schema + README.
- Gap: no manifest generator anywhere (`grep -rl 'workflow-manifest\|workflow_manifest' scripts config` → empty).
- Gap: **no `request_schema`/`response_schema`/`result:` fields exist in any registry yet** — added by #3282 AFTER #3295 reserves the slots. The generator is schema-tolerant: passes these through structurally when present, emits `null` when absent, **never coerces to/asserts a string type** (D1).

### Standards

Not applicable — harness/aggregation tooling, not an engineering calculation. The calc-citation-contract (`.claude/rules/calc-citation-contract.md`) does not fire.

### LLM Wiki pages consulted

None — control-plane infra/aggregation work, no domain knowledge added. Client: N/A confirmed.

### Documents consulted

- Issue #3284 body — manifest fields (`workflow_id, repo, basename, request_schema, response_schema ref, runtime, determinism/golden status, license-gated flag`), provenance stamp (per-repo registry hash + generation timestamp), stale-registry detection.
- Epic #3281 body — sequencing: #3282 (prereq) → {#3283 determinism, #3284 discovery}. **Per D6, #3283 is deferred to Wave 2.**
- Child #3295 body — reconciles divergent `schema_version` into the **v2 additive superset** (routing triple + reserved structured request/response schema slots + `result:` descriptor slot). This plan consumes that schema; it reads whatever the superset emits and never assumes a single integer or a string-typed schema field.
- #3282 plan (`docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md`) — sibling; `run_workflow(workflow_id, params|cfg) -> ResultEnvelope` is the round-trip consumer; owns the envelope determinism fields + the `result:` descriptor shape.
- `deckhand/src/deckhand/capability_smoke.py` — the reference resolver (see above); the consumer contract the manifest field-set targets.
- wed#450 body — the closest manifest precedent (catalog hash + generation timestamp + robustness contract for real/empty/stale/missing-dir data). This plan extends that pattern to the cross-repo *workflow* surface.

### Gaps identified

- No ecosystem-level `workflow-manifest.json` (greenfield).
- No generator iterating tier-1 registries (greenfield).
- `request_schema`/`response_schema`/`result:` not yet present in any registry — degrade to `null` passthrough (structurally, no str coercion) until #3282 populates.
- No provenance stamping (per-repo registry hash + git sha + generation timestamp).
- No stale-registry detector (recompute hash, compare, fail closed).
- `schema_version` is divergent (1/2/2/1) pending #3295's v2 reconciliation — the manifest records each repo's declared value, never assumes one.
- Duplicate `id` across versions (`digitalmodel:mooring-fatigue` v1+v2) is unhandled by a bare `repo:id` key — requires `repo:id@version` + a latest resolver (D4).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3284` — OPEN, `status:needs-plan`, `lane:claude` — this issue
- `#3281` — OPEN — EPIC: Deterministic Workflow API (parent)
- `#3295` — OPEN — reconcile registry `schema_version` into v2 additive superset (consumed here)
- `#3282` — OPEN, `status:plan-review` — assetutilities envelope + registry schema fields (owns request/response/`result:` shape + envelope determinism)
- `#3283` — OPEN — determinism harness (**deferred to Wave 2, D6**)

**File existence + verified field facts** (live, 2026-06-28):
- `assetutilities`: schema_version 1, 9 rows, `runtime: fast`, NO top-level `invocation`, NO version/latest/requires-license, per-row `input` present (×9).
- `digitalmodel`: schema_version 2, 111 rows, top-level `invocation` present, `runtime: offline` ×109 + `requires-license` ×2, `version:` ×2 + `latest:` ×1, duplicate id `mooring-fatigue` (v1 stable+latest / v2 experimental), per-row `input` ×111.
- `worldenergydata`: schema_version 2, 9 rows, top-level `invocation` present, `runtime: offline` ×9, `data_source.network_required` present, per-row `input` ×9.
- `assethold`: schema_version 1, 7 rows, `runtime: uv-python`, NO top-level `invocation`, per-row `input` ×7.
- MISSING (this plan creates): `scripts/workflow/generate_workflow_manifest.py`, `docs/registry/workflow-manifest.json`, `docs/registry/workflow-manifest.schema.json`, `docs/registry/README.md`, `scripts/workflow/tests/test_generate_workflow_manifest.py`.

**Reference-resolver line excerpts** (`deckhand/src/deckhand/capability_smoke.py`):
- `:117` `_parse_ref` → `<repo>:<workflow-id>[@<version>]`
- `:146` `_select_version` → latest-stable resolution (the manifest's `latest` resolver mirrors this exact rule)
- `:220-223` requires per-row `input` (fails closed if absent) — **why D4 mandates preserving `input`**
- `:231-232` `template = registry.get("invocation")` then `.replace("{input}", input_rel)` — top-level template, `{input}`-only

**Gap proofs:** `grep -rl 'workflow-manifest\|workflow_manifest' scripts config` → empty; `ls docs/registry/` → "No such file or directory".

- Reproduced 2026-06-28: all 4 registries parse; **136 callable rows** across ≥2 repos (AC #1 satisfiable). The abs paths in throwaway reproduction shells are not in the implementation — the generator resolves repos via `resolve_tier1_repo_path()`.

(Distinct sources: issue #3284 + epic #3281 + #3295 + #3282 plan + capability_smoke.py + wed#450 + 4 registry files + `tier1_repos.py` = 10. Minimum 3 met.)

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3284-discovery-manifest.md |
| Generator | `scripts/workflow/generate_workflow_manifest.py` |
| Manifest artifact (generated, committed snapshot) | `docs/registry/workflow-manifest.json` |
| Manifest JSON schema | `docs/registry/workflow-manifest.schema.json` |
| Registry README (consumer contract; names capability_smoke.py resolver) | `docs/registry/README.md` |
| Tests | `scripts/workflow/tests/test_generate_workflow_manifest.py` |
| Plan reviews | scripts/review/results/2026-06-28-plan-3284-{claude,codex,gemini}.md |
| Index row | docs/plans/README.md |

---

## Deliverable

A `scripts/workflow/generate_workflow_manifest.py` generator that reads each tier-1 repo's `docs/registry/workflows.yaml` (resolved via `resolve_tier1_repo_path`) and emits a single provenance-stamped `docs/registry/workflow-manifest.json` enumerating every callable workflow with **exactly the fields the reference resolver `deckhand/src/deckhand/capability_smoke.py` consumes** — `workflow_id` (`repo:id@version`), `routing_id` (`repo:id`), `version`/`status`/`latest`, `repo`, `basename`, `input` (preserved), `outputs`, `runtime`, top-level `invocation` template, `license_gated` (= `runtime == 'requires-license'`), reserved structured `request_schema`/`response_schema`/`result` passthrough, and a reserved-null `determinism` field — plus a per-`routing_id` **latest resolver** map and a `--check` stale-detection mode that fails closed when a repo's live registry hash no longer matches the manifest.

---

## Pseudocode

```
# scripts/workflow/generate_workflow_manifest.py

MANIFEST_VERSION = 1   # manifest-format version (independent of per-repo registry schema_version, which stays 2 per D1)

def load_registry(repo_slug) -> (raw_text, parsed_dict | None, error | None):
    repo_path = resolve_tier1_repo_path(repo_slug)          # reuse tier1_repos.py; fail-closed; NO hardcoded abs paths
    reg = repo_path / "docs/registry/workflows.yaml"
    if not reg.is_file():
        return (None, None, "missing-registry")             # robustness (wed#450 contract)
    raw = reg.read_text(encoding="utf-8")
    try:    parsed = yaml.safe_load(raw)
    except: return (raw, None, "unparseable-registry")
    if not isinstance(parsed, dict):
        return (raw, None, "unparseable-registry")
    return (raw, parsed, None)

def row_version(row) -> int:                                # mirror capability_smoke._row_version: unversioned == v1
    try:    return int(row.get("version") or 1)
    except: return 1

def normalize_row(repo_slug, registry, row) -> dict:
    ver = row_version(row)
    rid = f"{repo_slug}:{row['id']}"
    return {
        "workflow_id": f"{rid}@{ver}",                      # D4: repo:id@version — disambiguates duplicate ids (mooring-fatigue v1/v2)
        "routing_id": rid,                                  # unversioned routing key (resolve via latest_by_routing_id)
        "id": row["id"],
        "repo": repo_slug,
        "version": ver,
        "status": str(row.get("status") or "stable"),       # routing triple (D1)
        "latest": bool(row.get("latest", False)),
        "basename": row.get("basename"),
        "title": row.get("title"),
        "input": row.get("input"),                          # D4: PRESERVE per-row input — resolver fails closed without it
        "outputs": row.get("outputs", []),
        "runtime": row.get("runtime"),
        "invocation": registry.get("invocation"),           # D1: TOP-LEVEL required key ONLY; {input}-only substitution.
                                                            #     NO fallback to row['test'] (that is a pytest nodeid, not a command).
                                                            #     null + warning when a pre-#3295 registry has not added it yet.
        "license_gated": (row.get("runtime") == "requires-license"),   # D4: derives from runtime, NOT network_required
        "request_schema": row.get("request_schema"),        # D1: structured descriptor passthrough; null when absent; NO str coercion
        "response_schema": row.get("response_schema"),      # D1: structured descriptor passthrough; null when absent; NO str coercion
        "result": row.get("result"),                        # D1: registry 'result:' location descriptor (owned by #3282); null until populated
        "data_source": row.get("data_source"),              # informational network/fixture passthrough (NOT the license gate)
        "determinism": None,                                # D3+D6: reserved passthrough; #3283 (Wave 2) populates via key-allowlist. NO heuristic.
    }

def latest_by_routing_id(workflows) -> dict:
    # Mirror capability_smoke._select_version exactly: for each routing_id, the resolved
    # workflow_id when UNPINNED = latest-stable: a `latest: true` stable row if flagged,
    # else the highest-version stable row, else the highest-version row of any status.
    out = {}
    for rid, group in group_by(workflows, key="routing_id"):
        stable  = [w for w in group if w["status"] == "stable"]
        flagged = [w for w in stable if w["latest"]]
        pool    = flagged or stable or group
        out[rid] = max(pool, key=lambda w: w["version"])["workflow_id"]
    return out

def build_manifest() -> dict:
    repos, workflows, warnings = [], [], []
    for slug in tier1_python_repos():                       # SSoT iteration (#3023)
        raw, parsed, err = load_registry(slug)
        if err:
            warnings.append(f"{slug}: {err}")
            repos.append({"repo": slug, "status": err, "registry_sha256": None})
            continue
        sv = parsed.get("schema_version")
        if registry_top_invocation_missing(parsed):         # D1: invocation is a required top-level key
            warnings.append(f"{slug}: missing top-level 'invocation' (pre-#3295 registry); invocation emitted null")
        repos.append({
            "repo": slug,
            "schema_version": sv,                            # record per-repo; never assume one (target is v2 superset, D1)
            "registry_sha256": sha256(raw),                  # provenance: per-repo registry hash
            "git_sha": _git_head(slug),                      # provenance: repo HEAD (best-effort)
            "row_count": len(parsed.get("workflows") or []),
            "status": "ok",
        })
        for row in (parsed.get("workflows") or []):
            if "id" not in row:                              # robustness: malformed row
                warnings.append(f"{slug}: row missing id"); continue
            workflows.append(normalize_row(slug, parsed, row))
    workflows = sorted(workflows, key=lambda w: w["workflow_id"])  # deterministic order
    return {
        "manifest_version": MANIFEST_VERSION,
        "generated_at": iso8601_utc_now(),                  # provenance: generation timestamp (excluded from --check)
        "generator": "scripts/workflow/generate_workflow_manifest.py",
        "resolver": "deckhand/src/deckhand/capability_smoke.py",   # D1: name the reference resolver
        "repos": repos,
        "workflow_count": len(workflows),
        "workflows": workflows,
        "latest_by_routing_id": latest_by_routing_id(workflows),   # D4: the latest resolver, materialized
        "warnings": warnings,
    }

def write_manifest(path):  json.dump(build_manifest(), fp, indent=2, sort_keys=False)

def check_stale() -> int:
    # AC: stale-registry detection — recompute each repo registry hash, compare to committed manifest.
    saved = json.load(open(MANIFEST_PATH))
    fresh = build_manifest()
    drift = [slug for slug in repos_of(saved)
             if sha256_of(saved, slug) != sha256_of(fresh, slug)]   # compares ONLY registry_sha256, not generated_at
    if drift:
        print(f"STALE: registries changed since manifest: {drift}", file=stderr)
        return 1                                            # fail closed — never silently serve stale
    return 0

# CLI: --write (regenerate), --check (stale gate, exit 1 on drift), default --write
```

Notes:
- `generated_at` is excluded from the stale comparison — `--check` compares only the per-repo `registry_sha256` set, so a regeneration with no registry change is a no-op diff (avoids a self-tripping gate).
- `invocation` reads the **top-level** registry key only and substitutes `{input}` only (D1); there is **no** fallback to the per-row `test:` pytest nodeid. Pre-#3295 registries (assetutilities, assethold) emit `invocation: null` + a warning until #3295 adds `"uv run python -m <pkg> {input}"`.
- The duplicate-`id` case is real today (`digitalmodel:mooring-fatigue` v1+v2); `workflow_id = repo:id@version` keeps both entries, and `latest_by_routing_id["digitalmodel:mooring-fatigue"]` resolves to `digitalmodel:mooring-fatigue@1` (v1 is `latest: true`).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/workflow/generate_workflow_manifest.py` | generator + `--check` stale mode; reuses `tier1_repos.py` |
| Create | `scripts/workflow/tests/test_generate_workflow_manifest.py` | TDD suite (fixtures simulating divergent registries + duplicate-id versions) |
| Create | `docs/registry/workflow-manifest.json` | generated ecosystem manifest snapshot (committed) |
| Create | `docs/registry/workflow-manifest.schema.json` | JSON schema documenting the manifest field-set (names `capability_smoke.py` as resolver) |
| Create | `docs/registry/README.md` | documents the manifest + how `capability_smoke.py` / Deckhand / agents read it (consumer contract) |
| Update | docs/plans/README.md | add this plan's index row |

No source/CI/workflow files are edited (D2/D5 are sibling-issue scope).

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_aggregates_two_repos | manifest enumerates workflows from ≥2 fixture registries | 2 temp registries (schema_version 1 + 2) | `workflow_count` = sum; both repos in `repos[]` |
| test_workflow_id_is_repo_id_version | id key is `repo:id@version` (D4) | row id `foo`, version 3 | `workflow_id == "repoA:foo@3"`, `routing_id == "repoA:foo"` |
| test_unversioned_row_is_v1 | unversioned row resolves to version 1 (mirrors `_row_version`) | row with no `version` | `version == 1`, `workflow_id` ends `@1` |
| test_duplicate_id_versions_both_kept | duplicate id across versions both appear, not collided | one id with v1(stable,latest) + v2(experimental) | two entries `...@1` + `...@2`; `latest_by_routing_id[rid] == "...@1"` |
| test_latest_resolver_highest_stable_when_no_flag | latest resolver = highest stable when no `latest:true` | v1 stable + v2 stable, no flag | `latest_by_routing_id[rid]` → `...@2` |
| test_input_is_preserved | per-row `input` carried into each entry (D4) | row with `input: examples/x/input.yml` | entry `input == "examples/x/input.yml"` |
| test_license_gated_from_runtime | `license_gated` derives from `runtime=='requires-license'` (D4) | one `requires-license` row + one `offline` row | first `license_gated True`, second `False` |
| test_network_required_does_not_set_license_gated | `data_source.network_required` does NOT set the license gate (D4) | row `runtime: offline` + `data_source.network_required: true` | `license_gated == False`; `data_source` passed through |
| test_invocation_is_top_level_only | `invocation` = top-level template; NO fallback to per-row `test` (D1) | registry with top-level invocation + row with a `test:` nodeid | entry `invocation == "uv run python -m wed {input}"` (the template, never the nodeid) |
| test_invocation_null_and_warning_when_absent | pre-#3295 registry (no top-level invocation) emits null + warning | schema_version-1 registry, per-row `test` only | entry `invocation is None`; warning names the repo |
| test_request_response_schema_structured_passthrough | absent → null; present structured dict passes through unchanged; NO str coercion (D1) | row without fields; row with `request_schema:{...}` | first `null`, second equals the input dict |
| test_result_descriptor_passthrough | `result:` descriptor passes through when present, null when absent (D1, #3282-owned) | row with `result:{kind:files,outputs:[...]}` | entry `result` equals input; absent → `None` |
| test_determinism_field_is_reserved_null | determinism is reserved-null, NOT a heuristic (D3/D6) | any row (with or without `assertions`) | entry `determinism is None` in both cases |
| test_provenance_registry_hash_and_timestamp | each repo carries `registry_sha256`; manifest carries `generated_at` + `resolver` | 1 fixture registry | sha256 present + matches recomputed; ISO-8601 timestamp; `resolver` names capability_smoke.py |
| test_missing_registry_is_warning_not_crash | a repo with no registry file degrades gracefully | repo dir without registry | repo `status:"missing-registry"`, in `warnings`, no exception |
| test_unparseable_registry_is_warning | malformed YAML (and non-dict YAML) does not crash | invalid YAML / bare scalar | repo `status:"unparseable-registry"`, warning recorded |
| test_check_detects_stale_registry | `--check` returns 1 when a registry hash drifts | manifest then mutate a fixture registry | `check_stale()` returns 1, names drifted repo |
| test_check_clean_returns_zero | `--check` returns 0 when nothing changed (generated_at ignored) | freshly written manifest, regenerate | `check_stale()` returns 0 |
| test_output_is_deterministic_sorted | workflows sorted by `workflow_id`; stable across runs | same fixtures twice | byte-identical `workflows[]` order (generated_at aside) |

---

## Acceptance Criteria

- [ ] `docs/registry/workflow-manifest.json` enumerates callable workflows across ≥2 repos with their schema slots (issue AC #1). Live run includes all 4 tier-1 repos (136 rows as of 2026-06-28).
- [ ] **Round-trip readiness (issue AC #2):** each entry carries exactly what `deckhand/src/deckhand/capability_smoke.py` needs to resolve a runnable command — `workflow_id` (`repo:id@version`), `routing_id`, `repo`, `basename`, **`input`** (preserved), `outputs`, `runtime`, and the **top-level `invocation` template** (`{input}`-only substitution). A consumer picks a `workflow_id` (or resolves a `routing_id` via `latest_by_routing_id`) and feeds it to `resolve_workflow()`. (Driving the run via `run_workflow()` is #3282 scope; this manifest supplies the resolver inputs — documented as a dependency, not silently claimed.)
- [ ] **Duplicate-id disambiguation:** `digitalmodel:mooring-fatigue` v1 and v2 both appear as distinct `workflow_id`s; `latest_by_routing_id["digitalmodel:mooring-fatigue"]` resolves to the `latest:true` stable row (`@1`), mirroring `capability_smoke._select_version`.
- [ ] **License-gated flag:** `license_gated == (runtime == 'requires-license')` (D4); `data_source.network_required` is passed through informationally and does NOT set the gate. (Live: exactly the 2 `digitalmodel` `requires-license` rows are gated.)
- [ ] **Top-level invocation only:** `invocation` reads the top-level registry key with `{input}`-only substitution (D1); never falls back to a per-row `test:` nodeid; pre-#3295 registries emit `invocation: null` + a warning.
- [ ] **Schema-tolerant, structured:** `request_schema`/`response_schema`/`result` pass through structurally when present and emit `null` when absent — **no `str` coercion or invariant** (D1); per-repo `schema_version` is recorded (target is the v2 additive superset), never assumed.
- [ ] **Determinism field reserved:** `determinism` is reserved-null pending #3283 (Wave 2, D6); the manifest does NOT infer it from a registry heuristic (D3).
- [ ] Stale-registry detection: `generate_workflow_manifest.py --check` exits non-zero when any repo's live registry hash differs from the manifest (issue AC #3); never silently serves stale; `generated_at` is excluded from the comparison.
- [ ] Provenance: manifest carries `generated_at` + `resolver`; each repo entry carries `registry_sha256` (+ best-effort `git_sha`).
- [ ] `docs/registry/README.md` + `workflow-manifest.schema.json` document the field-set and name `capability_smoke.py` as the reference resolver.
- [ ] `uv run pytest scripts/workflow/tests/test_generate_workflow_manifest.py -v` green; no abs-path violations (`scripts/enforcement/check-no-abs-paths.sh` passes on the new files).
- [ ] Review artifacts posted under scripts/review/results/.

---

## Adversarial Review Summary

<!-- Round-1 findings are recorded below and resolved in this revision. Round-2 (this revision) is PENDING re-review. Not approval-ready until Round-2 returns no-MAJOR verdicts. -->

| Round | Provider | Verdict | Key findings |
|---|---|---|---|
| R1 | Claude + Codex + Gemini (consensus) | **MAJOR** | 8 findings (below), all resolved in this revision |
| R2 | Claude + Codex + Gemini | PENDING | (this re-review) |

**Round-1 MAJOR findings (8), and how this revision resolves each:**
1. **workflow_id collides duplicate ids** — `repo:id` merges `digitalmodel:mooring-fatigue` v1+v2. → Adopt `workflow_id = repo:id@version` + `routing_id` + `latest_by_routing_id` resolver (D4). Verified against `digitalmodel/docs/registry/workflows.yaml:120-167`.
2. **`input` dropped** — `normalize_row` omitted `input`, breaking the resolver (`capability_smoke.py:220-223` fails closed without it). → Preserve per-row `input` (D4); add `test_input_is_preserved`.
3. **license-gated from wrong source** — used `data_source.network_required`. → `license_gated = (runtime == 'requires-license')` (D4); `network_required` is informational only. Verified: only 2 digitalmodel rows are `requires-license`.
4. **invocation fell back to per-row `test`** — `test:` is a pytest nodeid, not a command. → Read the top-level `invocation` key only, `{input}`-only substitution; null+warning when absent (D1); name `capability_smoke.py` as resolver.
5. **determinism value-heuristic** — inferred status from `assertions` presence, which D3 forbids (#3283 owns it, key-allowlist only) and D6 defers to Wave 2. → `determinism` is a reserved-null passthrough.
6. **request/response schema typed as string** — prior `$ref string` assumption. → Structured passthrough, no `str` invariant (D1); add reserved `result:` descriptor passthrough (#3282-owned).
7. **schema_version reconciliation treated as open** — now settled. → Record per-repo `schema_version`; target is the **v2 additive superset**, no v3 bump (D1); removed from Open Questions.
8. **round-trip AC unverifiable / hand-wavy** — now anchored to the real resolver. → AC #2 is defined as supplying exactly the fields `capability_smoke.resolve_workflow()` consumes; demonstrated via `workflow_id`/`input`/top-level `invocation`.

**Overall result:** PENDING (Round-2 re-review not yet run; plan stays `draft`, never self-approved).

Revisions made based on review: items 1–8 above (this revision).

---

## Risks and Open Questions

- **Risk — schema still in flux (#3295/#3282 not landed):** `request_schema`/`response_schema`/`result` don't exist in any registry yet, and pre-#3295 registries lack the top-level `invocation` key. Mitigation: the generator is schema-tolerant by design (structured null passthrough + per-repo `schema_version` recorded + invocation-null-with-warning). It works today and absorbs the new fields automatically once #3282/#3295 populate them. No hard dependency on either landing first.
- **Risk — round-trip depends on #3282 for actual execution:** the manifest supplies resolver inputs (`workflow_id`, `input`, `invocation`) but `run_workflow()` execution is #3282 scope. Mitigation: AC #2 is scoped to resolver-input readiness against `capability_smoke.resolve_workflow()` (which exists today); execution wiring is the #3282/#3288 closeout. Per the epic, #3282/#3284 are parallel — the manifest is independently useful.
- **Risk — committed manifest churn:** the live `workflow-manifest.json` snapshot drifts as registries change (esp. digitalmodel's 111 rows). Mitigation: `generated_at` excluded from `--check`; wiring `--check` into a cron/CI gate is a candidate follow-on (out of scope here — D2 keeps this plan off CI files).
- **Risk — abs-path enforcement:** the generator resolves sibling repos via `resolve_tier1_repo_path()`, never hardcodes `/mnt/local-analysis/<repo>`. Tests run under `check-no-abs-paths.sh`. Covered by reusing `tier1_repos.py`.
- **Risk — resolver divergence:** `capability_smoke.py` reads compute checkouts under `DEFAULT_COMPUTE_BASE` while this generator reads tier-1 siblings; both read the same `docs/registry/workflows.yaml` shape. The manifest's `latest_by_routing_id` mirrors `_select_version` exactly (tested) so a consumer resolving via the manifest matches a consumer resolving via the live resolver. If `_select_version` changes, the mirrored test must be updated — noted for the implementer.

**Settled (formerly open):** schema unification (v2 superset, D1); round-trip scope (resolver-input readiness, D1/D4); determinism field treatment (reserved-null, D3/D6); manifest home (`docs/registry/`, mirrors per-repo `docs/registry/` convention — decided, not flagged for approval).

---

## Complexity: T2

**T2** — one new generator module + a TDD suite + a generated JSON artifact + a JSON-schema doc + a consumer README, all in the workspace-hub control plane with contained blast radius (no source/CI changes, reuses `tier1_repos.py`, mirrors `capability_smoke.py` resolution). Not T1 (multi-file, real aggregation + version disambiguation + latest resolver + stale-detection + robustness branches requiring TDD); not T3 (no cross-provider engine changes, no systemic harness rewiring).
