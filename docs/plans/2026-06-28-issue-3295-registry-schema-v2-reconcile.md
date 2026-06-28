# Plan for #3295: reconcile registry `schema_version` into a unified v2 superset (unblocks #3282)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3295
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3295-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

This is a cross-repo schema/governance reconciliation. The defect is a **same-integer / divergent-semantics**
collision in `docs/registry/workflows.yaml` across three tier-1 repos, surfaced as a MAJOR in the #3282 plan
review. The fix defines `schema_version: 2` once as a documented **additive superset** and aligns all repos to
it, while reserving (not defining) the request/response/result slots that #3282 will own.

### Existing repo code

- Found: `assetutilities/docs/registry/workflows.yaml:12` — `schema_version: 1`. Rows carry the **base field
  set** only: `id`, `basename`, `input`, `outputs[]`, `test`, `runtime` (9 workflow rows, lines 16–88). Top
  level also has `repo: assetutilities` (line 13) and `issue: 3063` (line 14); **no** `invocation:` key — the
  firable command is currently encoded redundantly in each row's `test:` field
  (`uv run python -m assetutilities examples/workflows/<slug>/input.yml`).
- Found: `digitalmodel/docs/registry/workflows.yaml:9` — `schema_version: 2`. Header comment (lines 1–8)
  defines `2` as the **deckhand versioned-routing triple**: optional `version` (int ≥ 1), `status`
  (stable|deprecated|experimental|retired, default stable), `latest: true`. Top level uses
  `invocation: "uv run python -m digitalmodel {input}"` (line 10); rows carry an extra `title:` field and
  `runtime: offline`. Large registry (~60 KB, many rows).
- Found: `worldenergydata/docs/registry/workflows.yaml:9` — `schema_version: 2`, **identical header comment**
  to digitalmodel (lines 1–8), `invocation: "uv run python -m worldenergydata {input}"` at line 10, plus
  row-level extensions already in use: `data_source:` block (lines 25–33) and `assertions:` block (used later
  in the file).

### The real runtime consumer — `deckhand/src/deckhand/capability_smoke.py` (the reference resolver)

This file is the **Python reference resolver** for the registry contract and must be named as such in the
schema-of-record doc. Verified facts (line cites, 2026-06-28):

- `capability_smoke.py:38` — `REGISTRY_RELPATH = Path("docs/registry/workflows.yaml")` — resolves against the
  exact file this plan reconciles.
- `capability_smoke.py:231` — `template = str(registry.get("invocation") or "uv run python -m {pkg} {input}")`
  — reads the **top-level `invocation`** key. The fallback contains a literal `{pkg}` placeholder.
- `capability_smoke.py:232` — `rendered = template.replace("{input}", input_rel)` — substitution is
  **`{input}`-ONLY**. `{pkg}` is **never** substituted. Therefore the registry's `invocation` string MUST embed
  the literal package name; an `invocation` of `"uv run python -m {pkg} {input}"` would render an un-runnable
  command. This is the hard reason assetutilities' value must be exactly
  `"uv run python -m assetutilities {input}"` and `invocation` must be a **required** top-level key, not optional.
- `capability_smoke.py:133–164` — implements the routing triple (`version`/`status`/`latest`), confirming the
  `schema_version: 2` semantics. `capability_smoke.py:42` — `OFFLINE_RUNTIMES = {"offline", "", None}`; rows
  whose `runtime` is outside this set (e.g. a future `requires-license`) resolve but are reported **SKIPPED**.
  This is the basis for #3284's `license-gated` derivation keying off `runtime`, NOT `network_required`.
- `capability_smoke.py:234` — `rw.outputs = [(compute_root / o).resolve() for o in (row.get("outputs") or [])]`
  — the resolver reads the row-level **`outputs:` list** as the file-output result location today. The richer
  `result:` descriptor (`{kind: in_memory|files, ...}`) is **#3282's to define**, not this plan's.

### Test consumers of the schema (the contract guardrails)

- Found: `digitalmodel/tests/workflows/test_registry_versioning.py:21–22` —
  `def test_registry_is_schema_version_2(): assert _load()["schema_version"] == 2`. Also
  `test_workflow_registry_version_invariants` (lines 25–46) validates the triple. Neither test asserts anything
  about `request_schema`/`response_schema`/`result` today — so reserving those slots adds new coverage without
  contradicting existing assertions.
- Found: `worldenergydata/tests/workflows/test_durable_workflows.py:17–20` — `_load_registry()` asserts
  `registry["schema_version"] == 2`; `test_workflow_registry_version_invariants` (re-asserts via `_load_registry`)
  validates the triple. Same: no current request/response assertion.
- Confirmed: `assetutilities` has **no** registry-schema test — `tests/workflows/` does not exist, and
  `grep -rln "registry/workflows" assetutilities/tests` returns empty. Bumping assetutilities `1 → 2` therefore
  breaks **zero** existing tests; this plan creates the first guard.
- Disambiguation (avoids a false MAJOR): `digitalmodel/tests/docs/test_digitalmodel_routing_contract.py:91`
  asserts `schema_version == 1`, but it loads a **different** registry — `docs/registry/module-routing.yaml`
  (line 13 `REGISTRY = ROOT / "docs" / "registry" / "module-routing.yaml"`), not `workflows.yaml`. It is **out of
  scope** for this issue and must not be touched.

### Standards

Not applicable — this is a workspace-hub governance/contract-schema issue, not an engineering-calculation issue.
No DNV/API/ABS standard is involved.

### LLM Wiki pages consulted

No relevant wiki pages — schema reconciliation does not touch wiki content (Client: N/A). The header comments
reference `[[durable-workflow-registries]]` (a wiki slug cited in #3050/#3067) conceptually, but the schema of
record will live in `workspace-hub/docs/standards/`, not the wiki.

### Documents consulted

- `#3295` issue body — defines the deliverable: one documented `schema_version: 2` (or 3) **superset** carrying
  BOTH the routing triple AND optional `request_schema`/`response_schema`, defined once in the canonical
  workflow-contract doc (companion to #3067), adopted by all repos; existing rows that omit optional fields must
  still validate.
- `docs/plans/2026-06-27-issue-3282-resultenvelope-run-workflow.md` (README index row line 205) — the #3282 plan
  proposes "optional `request_schema`/`response_schema` registry fields" and a `schema_version` bump on
  assetutilities. **This is the collision source:** #3282 would have given assetutilities `2` to mean "carries
  request/response", colliding with digitalmodel/worldenergydata's `2` = "routing triple". #3295 resolves the
  semantics first so #3282's Blocker 3 clears.
- `docs/plans/2026-06-17-issue-3067-uv-workflow-contract-doc.md` — establishes the canonical-contract-doc home
  as `docs/standards/UV_WORKFLOW_CONTRACT.md` (ALLCAPS contract pattern, lines 18, 62, 81), documenting the
  registry schema (`schema_version 1` at the time, line 112). #3067 is **OPEN and unlanded** — the doc does not
  yet exist (confirmed below).
- `#3290` (parent epic, Theme C contract convergence), `#3281` (Deterministic Workflow API epic), `#3284`
  (discovery manifest — downstream consumer of this schema), `#3282` (ResultEnvelope), `#3283` (golden harness,
  **deferred to Wave 2** per D6), `#3067` (UV-contract doc) — all OPEN.
- `.claude/rules/calc-citation-contract.md` — the request/response provenance fields will eventually wire to
  the Citation sidecar shape (#3282 deliverable); this plan only **reserves** the optional schema slots, it does
  not implement provenance.

### Gaps identified

- No canonical schema-of-record document exists in workspace-hub: `docs/standards/UV_WORKFLOW_CONTRACT.md` is
  MISSING (#3067 not landed). This plan must create the schema-of-record so the three repos can cite one source.
- The three registries disagree at the **top level too**, not just `schema_version`: assetutilities uses
  `repo:`/`issue:` and **no** `invocation:`; digitalmodel/worldenergydata use `invocation:` and no `repo:`.
  Because `capability_smoke.py` requires `invocation` to be a present, package-named string, the superset doc
  must declare `invocation` a **required** top-level key (resolved per D1) and `repo`/`issue` as optional legacy.
- No assetutilities registry-schema test exists — a validation test is needed so assetutilities' adoption of v2
  is guarded (and so the "existing rows still validate" acceptance criterion is machine-checked, not asserted in
  prose).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-28 via `gh issue view`):
- `#3295` — OPEN — seamless(contract): reconcile registry schema_version into a unified v2 superset (unblocks #3282)
- `#3282` — OPEN — wf-api(assetutilities): ResultEnvelope + run_workflow() + registry request/response schema [FOUNDATIONAL]
- `#3290` — OPEN — EPIC: Seamless ecosystem development
- `#3281` — OPEN — EPIC: Deterministic Workflow API
- `#3284` — OPEN — wf-api(ecosystem): discovery manifest
- `#3283` — OPEN — golden harness (DEFERRED to Wave 2 per D6)
- `#3067` — OPEN — uv-workflow(workspace-hub): write the canonical UV workflow contract standard doc

**File existence** (`ls -la` 2026-06-28):
- EXISTS: `assetutilities/docs/registry/workflows.yaml` (88 lines, `schema_version: 1`, no `invocation:`)
- EXISTS: `digitalmodel/docs/registry/workflows.yaml` (~60 KB, `schema_version: 2`, `invocation:` line 10)
- EXISTS: `worldenergydata/docs/registry/workflows.yaml` (`schema_version: 2`, `invocation:` line 10)
- EXISTS: `deckhand/src/deckhand/capability_smoke.py` (reference resolver; reads top-level `invocation`, `{input}`-only)
- EXISTS: `digitalmodel/tests/workflows/test_registry_versioning.py`
- EXISTS: `worldenergydata/tests/workflows/test_durable_workflows.py`
- MISSING (this plan creates): `workspace-hub/docs/standards/WORKFLOW_REGISTRY_SCHEMA.md`
- MISSING (#3067, not this plan): `workspace-hub/docs/standards/UV_WORKFLOW_CONTRACT.md`
- MISSING (this plan creates): `assetutilities/tests/workflows/test_registry_schema.py` (no `tests/workflows/` dir today)

**Line excerpts** (`Read` 2026-06-28):
```
assetutilities/docs/registry/workflows.yaml:12   schema_version: 1
assetutilities/docs/registry/workflows.yaml:13   repo: assetutilities          # no top-level invocation: present
digitalmodel/docs/registry/workflows.yaml:9      schema_version: 2
digitalmodel/docs/registry/workflows.yaml:10     invocation: "uv run python -m digitalmodel {input}"
worldenergydata/docs/registry/workflows.yaml:9   schema_version: 2
worldenergydata/docs/registry/workflows.yaml:10  invocation: "uv run python -m worldenergydata {input}"
deckhand/src/deckhand/capability_smoke.py:231    template = str(registry.get("invocation") or "uv run python -m {pkg} {input}")
deckhand/src/deckhand/capability_smoke.py:232    rendered = template.replace("{input}", input_rel)   # {input}-ONLY; {pkg} NOT substituted
deckhand/src/deckhand/capability_smoke.py:234    rw.outputs = [... for o in (row.get("outputs") or [])]  # file-output result location today
digitalmodel/tests/workflows/test_registry_versioning.py:22   assert _load()["schema_version"] == 2
worldenergydata/tests/workflows/test_durable_workflows.py:19   assert registry["schema_version"] == 2
digitalmodel/tests/docs/test_digitalmodel_routing_contract.py:13  REGISTRY = ROOT/"docs"/"registry"/"module-routing.yaml"
digitalmodel/tests/docs/test_digitalmodel_routing_contract.py:91  assert data["schema_version"] == 1   # module-routing.yaml — NOT workflows.yaml, out of scope
```

**Gap proofs:**
- `ls docs/standards/UV_WORKFLOW_CONTRACT.md` → "No such file or directory" → confirms the #3067 doc has not landed.
- `ls assetutilities/tests/workflows/` → "No such file or directory" → confirms no assetutilities registry test exists.
- `grep -rln "registry/workflows" assetutilities/tests` → empty → confirms assetutilities `schema_version` is unguarded.
- `capability_smoke.py:231–232` → confirms the resolver reads `invocation` top-level and substitutes `{input}` only.

**Reproduction proofs:** N/A — this is a pure schema/contract/governance issue with no alleged runtime failure
(no failing test, broken import, missing method, or numeric regression). Per `issue-planning-mode` Step 1.5 the
skip is allowed and intentional. The verifiable substrate (the divergence and its guards) is captured above as
line excerpts: assetutilities=`1`, digitalmodel=`2`, worldenergydata=`2`, with `2` carrying mutually-incompatible
meaning vs the `2` the #3282 plan proposed for assetutilities.

<!-- Source count: #3295 body, #3282 plan, #3067 plan, assetutilities/digitalmodel/worldenergydata registries,
     capability_smoke.py resolver, dm + wed test files, dm module-routing test = 9 distinct sources ✓ (≥3 required). -->

---

## Wave context and cross-issue ownership boundaries (owner-confirmed 2026-06-28)

The owner settled six cross-cutting decisions for the seamless-ecosystem wave. The ones that **constrain what
#3295 may and may not define** are baked into this plan below; they are no longer open questions.

- **D1 (schema — this issue + #3282).** `schema_version` STAYS `2` as an **additive superset** (deckhand routing
  triple `version`/`status`/`latest` + the new reserved fields). **NO v3 bump.** `request_schema`/`response_schema`
  are **structured descriptors — NOT typed strings, NOT Pydantic-path strings, with NO `str` invariant.** The
  result LOCATION is a registry `result:` descriptor `{kind: in_memory|files, key: <cfg key> for in_memory |
  outputs: [...] for files}`. **#3282 OWNS the `result:` descriptor shape and the internal shape of
  `request_schema`/`response_schema`; #3295 only RESERVES those three slots (structured, untyped) pending #3282.**
  `invocation:` IS a **required** top-level registry key; assetutilities' value = exactly
  `"uv run python -m assetutilities {input}"` with **`{input}`-ONLY** substitution; `capability_smoke.py` is the
  reference resolver and is named as such in the schema doc.
- **D3 (determinism ownership — #3282 vs #3283).** #3282 OWNS envelope determinism FIELDS (`input_hash`,
  `result_hash`, `reproducible` computed-not-hardcoded, `provenance.code_version={package_version, git_sha}`).
  #3283 OWNS the golden harness + volatile-field spec. **#3295 does NOT define, reserve, or test any of these
  fields** — it stops at the registry-row schema. Noted here so the schema doc explicitly disclaims them.
- **D4 (discovery — #3284).** `workflow_id = "repo:id@version"` (+ a `latest` resolver); per-row `input` is
  **preserved** (kept in the required base-field set, never dropped); `license-gated` derives from
  `runtime == "requires-license"` (NOT `network_required`). The schema doc records that `runtime` carries the
  license-gate semantics (consistent with `capability_smoke.py:42` `OFFLINE_RUNTIMES`).
- **D6 (sequencing).** #3283 (golden harness) is **deferred to Wave 2** and is not in this wave.

Decisions D2 (CI caching, #3291) and D5 (governance auto-apply, #3296) touch sibling issues' CI/governance
surfaces, not the registry-row schema; they are out of this plan's file scope and are not re-litigated here.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-28-issue-3295-registry-schema-v2-reconcile.md` |
| Schema-of-record doc (new) | `workspace-hub/docs/standards/WORKFLOW_REGISTRY_SCHEMA.md` |
| assetutilities registry (modify) | `assetutilities/docs/registry/workflows.yaml` |
| digitalmodel registry (modify, header only) | `digitalmodel/docs/registry/workflows.yaml` |
| worldenergydata registry (modify, header only) | `worldenergydata/docs/registry/workflows.yaml` |
| assetutilities schema test (new) | `assetutilities/tests/workflows/test_registry_schema.py` |
| digitalmodel superset test (extend) | `digitalmodel/tests/workflows/test_registry_versioning.py` |
| worldenergydata superset test (extend) | `worldenergydata/tests/workflows/test_durable_workflows.py` |
| Reference resolver (read-only context, NOT edited) | `deckhand/src/deckhand/capability_smoke.py` |
| Plans index (update) | `workspace-hub/docs/plans/README.md` |
| Plan review — Claude | `scripts/review/results/2026-06-28-plan-3295-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-06-28-plan-3295-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-06-28-plan-3295-gemini.md` |

---

## Deliverable

A single canonical `docs/standards/WORKFLOW_REGISTRY_SCHEMA.md` in workspace-hub that defines `schema_version: 2`
as one documented **additive superset** (base fields + required `invocation` + optional Deckhand routing triple +
**reserved** `request_schema`/`response_schema`/`result` slots owned by #3282), names `capability_smoke.py` as the
reference resolver, and is adopted by all three tier-1 registries with a machine test in each repo proving (a)
rows that omit the optional/reserved fields still validate, and (b) the reserved slots are accepted untyped — so
#3282 can populate them without re-bumping the version or colliding semantics. This clears #3282 Blocker 3.

---

## Pseudocode

**Settled design decision (D1): the unified version number is `2`, NOT `3` — no v3 bump.**

Adding *optional/reserved* fields to a schema is a backward-compatible superset, not a breaking change, so it does
not warrant a major-version bump. digitalmodel (`test_registry_versioning.py:22`) and worldenergydata
(`test_durable_workflows.py:19`) both pin `schema_version == 2`; keeping the unified version at `2` leaves those
green with no row edits. assetutilities has no version-pinned test, so the `1 → 2` bump breaks nothing. (This was a
Round-1 open question; the owner has settled it as `2`.)

**Settled design decision (D1): request/response/result are RESERVED structured slots, owned by #3282.**

`#3295` does **not** define or type-check the internal shape of `request_schema`, `response_schema`, or `result`.
It only documents that the slots exist, are structured (mappings, not bare strings), and carry **no `str`
invariant**. The internal shape — including the `result: {kind: in_memory|files, key|outputs}` descriptor — is
#3282's deliverable. The #3295 tests therefore prove *reservation* (presence is accepted, absence is valid, no
`str` enforcement), not *validation*.

```
# Canonical superset definition (documented in WORKFLOW_REGISTRY_SCHEMA.md, enforced by per-repo tests)

schema_version: 2            # REQUIRED, top level, integer literal 2 (no v3 bump — D1)
invocation: <string>         # REQUIRED, top level. MUST embed the literal package name and end with " {input}".
                             # capability_smoke.py substitutes {input} ONLY ({pkg} is never substituted).
                             # assetutilities value == "uv run python -m assetutilities {input}" exactly.

top_level:
  required: [schema_version, invocation]   # invocation required — capability_smoke.py:231 reads it
  optional: [repo, issue]                  # assetutilities legacy keys — allowed, not required

workflow_row:
  required: [id, basename, input, outputs, test]   # `input` preserved per D4 (#3284 discovery)
  recommended: [runtime, title]            # runtime: offline|fast|requires-license|...; title: human label
                                           # runtime == "requires-license" => license-gated (D4); not network_required
  optional_routing_triple:                 # Deckhand versioned routing (schema_version 2 origin)
    version:  int >= 1        # absent => 1
    status:   stable | deprecated | experimental | retired   # absent => stable
    latest:   bool            # absent => treated as latest-stable for its id
  reserved_contract_slots:                 # RESERVED here, OWNED + shaped by #3282 — NOT typed by #3295
    request_schema:  <structured>   # structured descriptor; NO str invariant; absent => untyped input
    response_schema: <structured>   # structured descriptor; NO str invariant; absent => untyped output
    result:          <structured>   # {kind: in_memory|files, key: <cfg key> | outputs: [...]}; #3282 owns shape
  optional_extensions:                     # already in use by worldenergydata
    data_source: {type, network_required, fixtures[]}
    assertions:  {json[], csv[]}

# Validator contract (each repo's test):
function validate_registry(path, *, expect_invocation=None):
    reg = yaml.safe_load(path)
    assert reg["schema_version"] == 2
    assert isinstance(reg.get("invocation"), str) and reg["invocation"].strip()   # required top level
    assert "{input}" in reg["invocation"] and "{pkg}" not in reg["invocation"]    # {input}-only; pkg literal
    if expect_invocation:                       # assetutilities pins the exact string
        assert reg["invocation"] == expect_invocation
    for row in reg["workflows"]:
        assert required base fields present and non-empty   # id/basename/input/outputs/test
        if "version" in row:  assert isinstance(row["version"], int) and row["version"] >= 1
        assert row.get("status", "stable") in STATUS_SET
        # request_schema / response_schema / result: RESERVED, UNTYPED in #3295.
        # Their mere PRESENCE must NOT raise, and NO str invariant is imposed.
        # #3295 deliberately does not inspect their internal shape — that is #3282's ResultEnvelope contract.
        # absence of every optional/reserved field is valid (superset back-compat)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `workspace-hub/docs/standards/WORKFLOW_REGISTRY_SCHEMA.md` | canonical superset schema-of-record (the deliverable). Documents: `schema_version: 2` (no v3 bump); **required** top-level `invocation` with `{input}`-only substitution; the routing triple; the **reserved** `request_schema`/`response_schema`/`result` slots as structured-untyped, explicitly owned by #3282; names `deckhand/src/deckhand/capability_smoke.py` as the reference resolver; disclaims the #3282 determinism fields (D3) and records the D4 `runtime=="requires-license"` license-gate. Cited by all three repos; #3067's UV_WORKFLOW_CONTRACT.md will reference it when it lands |
| Modify | `assetutilities/docs/registry/workflows.yaml` | bump `schema_version: 1` → `2`; replace header comment with the superset description + canonical-doc citation; **add required top-level `invocation: "uv run python -m assetutilities {input}"`** (exact string, `{input}`-only — matches the existing `test:` commands and `capability_smoke.py`'s resolver). Rows unchanged; `repo`/`issue` retained as optional legacy keys |
| Modify | `digitalmodel/docs/registry/workflows.yaml` | extend header comment to document the **reserved** `request_schema`/`response_schema`/`result` superset slots (structured, untyped, owned by #3282) + cite the canonical doc; `schema_version` stays `2`, `invocation` unchanged, no row edits |
| Modify | `worldenergydata/docs/registry/workflows.yaml` | same header-comment extension + canonical-doc citation; `schema_version` stays `2`, `invocation` unchanged, no row edits |
| Create | `assetutilities/tests/workflows/test_registry_schema.py` | new TDD guard: asserts `schema_version == 2`, the exact required `invocation` string + `{input}`-only rule, base required fields, that current rows (no optional/reserved fields) validate, and that the reserved slots are accepted untyped (no `str` invariant) |
| Modify | `digitalmodel/tests/workflows/test_registry_versioning.py` | add a superset test: reserved `request_schema`/`response_schema`/`result` slots accepted when present (structured, no `str` invariant) and absence is valid (keep the `== 2` pin and the existing triple test unchanged) |
| Modify | `worldenergydata/tests/workflows/test_durable_workflows.py` | add the same reserved-slot superset test (keep the `== 2` pin; existing `data_source`/`assertions` rows still validate) |
| Update | `workspace-hub/docs/plans/README.md` | add the #3295 index row |

**Repo/PR boundary note:** assetutilities, digitalmodel, worldenergydata, and workspace-hub are four separate
git repositories. This work lands as **four coordinated PRs**, one per repo. The workspace-hub doc PR is the
authority; the three registry PRs cite it. Sequence: land the workspace-hub schema doc first (or concurrently),
then the assetutilities bump (unblocks #3282), then the two header-only PRs for digitalmodel/worldenergydata.
`deckhand/src/deckhand/capability_smoke.py` is **read-only context** for this plan — it is the reference resolver
the schema must stay compatible with, and is NOT edited here.

---

## TDD Test List

| Test name | Repo | What it verifies | Expected input | Expected output |
|---|---|---|---|---|
| `test_schema_version_is_2` | assetutilities | registry declares unified version (no v3 bump) | `workflows.yaml` | `schema_version == 2` |
| `test_invocation_required_exact_and_input_only` | assetutilities | top-level `invocation` is the exact string `"uv run python -m assetutilities {input}"`; contains `{input}`, does NOT contain `{pkg}` (matches `capability_smoke.py` resolver) | `workflows.yaml` | exact match; `{input}` present, `{pkg}` absent |
| `test_base_required_fields_present` | assetutilities | every row has id/basename/input/outputs/test (`input` preserved per D4) | all 9 rows | all present, non-empty |
| `test_existing_rows_validate_without_optional_fields` | assetutilities | superset back-compat: rows omitting routing triple + reserved slots still pass | current rows | no AssertionError |
| `test_reserved_request_response_result_slots_accepted_untyped` **(INVERTS the prior `test_optional_request_response_when_present_are_strings`)** | assetutilities | a synthetic row carrying STRUCTURED (dict) `request_schema`/`response_schema`/`result` validates and is NOT rejected; validator imposes **NO `str` invariant**; internal shape is left to #3282 | crafted row with dict slots; also a row with absent slots | both accepted; a bare-string slot is NOT required and NOT the only allowed form |
| `test_routing_triple_optional_and_typed` | assetutilities | `version` int≥1, `status` in set when present; absence ⇒ defaults | crafted rows | enforced |
| `test_registry_is_schema_version_2` (existing, unchanged) | digitalmodel | regression: dm stays `== 2` | `workflows.yaml` | passes unchanged |
| `test_workflow_registry_version_invariants` (existing, unchanged) | digitalmodel | regression: triple invariants hold | `workflows.yaml` | passes unchanged |
| `test_reserved_contract_slots_accepted_untyped` | digitalmodel | reserved `request_schema`/`response_schema`/`result` accepted (structured, no `str` invariant); absent ⇒ valid | rows | enforced |
| `test_durable_schema_version_2` (existing line 19, unchanged) | worldenergydata | regression: wed stays `== 2` | `workflows.yaml` | passes unchanged |
| `test_reserved_contract_slots_accepted_untyped` | worldenergydata | reserved slots accepted; existing `data_source`/`assertions` rows still validate | rows | enforced |
| `test_doc_documents_version_2_superset` (optional, grep-style) | workspace-hub | the schema doc names `schema_version: 2`, the routing triple, the **reserved** `request_schema`/`response_schema`/`result` slots, the **required** `invocation` with `{input}`-only rule, names `capability_smoke.py` as reference resolver, and names #3282 as owner of the reserved slots | `WORKFLOW_REGISTRY_SCHEMA.md` | all substrings present |

**Inversion note (Round-2):** the Round-1 plan's `test_optional_request_response_when_present_are_strings`
asserted `isinstance(row[f], str)` with a non-empty-string invariant. That contradicts the settled D1 decision
(structured descriptors, no `str` invariant). It is **explicitly inverted** into
`test_reserved_request_response_result_slots_accepted_untyped`, which proves the slots are accepted as structured
mappings and that **no** `str` enforcement exists. The internal-shape validation moves to #3282.

---

## Acceptance Criteria

- [ ] `docs/standards/WORKFLOW_REGISTRY_SCHEMA.md` exists and documents ONE `schema_version: 2` (no v3 bump) whose
      field-set is an **additive superset** (base + required `invocation` + routing triple + **reserved**
      `request_schema`/`response_schema`/`result`), explicitly stating every optional field's absence-default and
      that the reserved slots are **structured, untyped, and owned by #3282** (no `str` invariant) — not a
      per-repo redefinition.
- [ ] The schema doc names `deckhand/src/deckhand/capability_smoke.py` as the **reference resolver**, documents
      that `invocation` is a **required** top-level key whose value embeds the literal package name and uses
      **`{input}`-only** substitution, and disclaims the #3282 determinism fields (`input_hash`/`result_hash`/
      `reproducible`/`provenance.code_version`) per D3 and the D4 `runtime=="requires-license"` license-gate.
- [ ] assetutilities, digitalmodel, and worldenergydata `docs/registry/workflows.yaml` all declare
      `schema_version: 2` with the same documented semantics (header comments cite the canonical doc), and
      assetutilities carries top-level `invocation: "uv run python -m assetutilities {input}"` exactly.
- [ ] assetutilities new test passes: `uv run pytest assetutilities/tests/workflows/test_registry_schema.py -v`
      — including the exact-`invocation` and `{input}`-only assertions.
- [ ] No regression on the existing version pins/triple tests: `uv run pytest
      digitalmodel/tests/workflows/test_registry_versioning.py -v` and `uv run pytest
      worldenergydata/tests/workflows/test_durable_workflows.py -v` stay green.
- [ ] "Existing rows still validate" is machine-proven: each repo's superset test confirms rows that omit the
      optional/reserved fields raise no error.
- [ ] The reserved slots are proven **untyped**: each repo's superset test accepts a structured (dict)
      `request_schema`/`response_schema`/`result` without imposing a `str` invariant (the explicit inversion of
      the Round-1 `...are_strings` test).
- [ ] `digitalmodel/tests/docs/test_digitalmodel_routing_contract.py` (the `module-routing.yaml` `== 1` test) is
      untouched and still green — proof the bump did not bleed into the unrelated registry.
- [ ] #3282 Blocker 3 is resolvable: assetutilities can adopt `request_schema`/`response_schema`/`result` on `2`
      without a semantic collision or a version bump (documented in the schema doc and a #3282 cross-link comment
      stating #3282 owns those slots' internal shape).
- [ ] Review artifacts posted to `scripts/review/results/`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Round-1 (consolidated, owner-reconciled) | **MAJOR** | 6 cross-cutting decisions settled (D1–D6) + the schema-specific fixes they imply for #3295 (see below). Owner-confirmed 2026-06-28. |
| Claude | PENDING (Round-2) | — |
| Codex | PENDING (Round-2) | — |
| Gemini | PENDING (Round-2) | — |

**Round-1 result:** MAJOR. The owner-reconciled findings applied to #3295 in this revision:
1. **(D1) `request_schema`/`response_schema` typed-as-`str` was wrong.** They are structured descriptors with no
   `str` invariant; the result LOCATION is a `result:` descriptor. #3295 now RESERVES all three slots untyped and
   assigns their internal shape to #3282. The `..._are_strings` test is explicitly inverted.
2. **(D1) `invocation` under-specified.** Now a required top-level key; assetutilities pinned to the exact string
   `"uv run python -m assetutilities {input}"`; `{input}`-only substitution rule grounded in
   `capability_smoke.py:231–232`; `capability_smoke.py` named as the reference resolver in the schema doc.
3. **(D1) version-number open question settled.** `schema_version` stays `2`; **no v3 bump**. Removed from Open
   Questions.
4. **(D3) determinism fields delineated.** `input_hash`/`result_hash`/`reproducible`/`provenance.code_version`
   are #3282's; the schema doc disclaims them, #3295 neither reserves nor tests them.
5. **(D4) discovery boundaries.** Per-row `input` preserved in the required base set; `runtime=="requires-license"`
   carries the license-gate (not `network_required`), grounded in `capability_smoke.py:42`.
6. **(D6) sequencing.** #3283 (golden harness) deferred to Wave 2 — recorded; out of this wave.

**Round-2 result:** PENDING (this re-review).

Revisions made based on review (Round-2 prep): listed as items 1–6 above; reflected in Pseudocode,
Files-to-Change, TDD Test List, Acceptance Criteria, and Open Questions (settled items removed).

---

## Risks and Open Questions

- **Settled (was Round-1 open):** version number is `2`, no v3 bump (D1). Reserved slots are structured/untyped
  and owned by #3282 (D1). `invocation` is required, exact, `{input}`-only (D1). These are no longer open.
- **Risk (doc home vs #3067):** #3067 will create `docs/standards/UV_WORKFLOW_CONTRACT.md` and also document the
  registry schema. To avoid two divergent definitions, this plan creates a focused `WORKFLOW_REGISTRY_SCHEMA.md`
  as the single schema-of-record and stipulates #3067's doc must **reference** it, not re-derive it. Decision
  (not deferred): ship the standalone schema doc now so #3295 does not block on the unlanded #3067; #3067 cites it.
- **Risk (top-level key divergence):** assetutilities uses `repo:`/`issue:` and lacked `invocation:`. Resolved per
  D1: add required `invocation:` to assetutilities; keep `repo`/`issue` as optional legacy keys (no strict
  top-level uniformity is imposed — dropping `repo`/`issue` is explicitly out of scope to avoid churn).
- **Risk (cross-repo coordination):** four separate repos, four PRs. The assetutilities bump must not land before
  the schema doc, or it would reference a non-existent canonical doc. Sequence enforced in Files-to-Change note.
- **Risk (resolver compatibility):** `capability_smoke.py:231` falls back to `"uv run python -m {pkg} {input}"`
  only when `invocation` is absent, and never substitutes `{pkg}`. The assetutilities `invocation` value MUST
  therefore embed the literal package name; the new `test_invocation_required_exact_and_input_only` guards this so
  a future edit cannot silently reintroduce an un-runnable `{pkg}` template.
- **Risk (#3282 overlap):** the #3282 plan also proposed bumping assetutilities to `2` and adding
  request/response/result. This plan does the **version + doc + header + required-invocation** reconciliation and
  **reserves** the slots; #3282 then defines their internal shape (including the `result:` descriptor) and
  **populates** specific assetutilities rows. The two plans must not both edit
  `assetutilities/docs/registry/workflows.yaml:schema_version` — #3295 owns the bump, #3282 consumes it. Note this
  explicitly in the #3282 cross-link comment.

---

## Complexity: T2

**T2** — multi-file edits across four repos plus a new contract doc and three test files; no algorithmic
complexity, but real cross-repo coordination, a backward-compatibility invariant to prove, a resolver-compatibility
constraint (`{input}`-only `invocation`), and TDD guards required. Not T1 (more than a single trivial edit; needs
tests). Not T3 (no systemic redesign, no new runtime code path, no cross-provider engineering computation).
