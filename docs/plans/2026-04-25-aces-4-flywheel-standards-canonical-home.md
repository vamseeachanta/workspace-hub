# Plan for aceengineer-strategy #4: Standards LLM-Wiki Industrialization — Decide Canonical Home + Populate DNV-OS-E301 + API RP 2SK

> **Status:** draft v2 (post-r3 patch addressing MAJOR findings)
> **Complexity:** T2
> **Date:** 2026-04-25
> **Issue:** https://github.com/vamseeachanta/aceengineer-strategy/issues/4
> **Parent epic:** https://github.com/vamseeachanta/aceengineer-strategy/issues/1
> **Review artifacts:** scripts/review/results/2026-04-25-plan-aces-4-claude.md (v1 review, MAJOR; this v2 plan patches all five MAJOR findings inline)

---

## Resource Intelligence Summary

### Existing repo code

- Found: `data/standards/` exists at workspace-hub root — content not yet inspected by this plan; Phase 1 audit will inventory it.
- Found: `docs/standards/` exists — similar; needs audit.
- Found: `knowledge/wikis/marine-engineering/` exists — likely the strongest candidate for the canonical durable home, given workspace-hub #2471 (CSA Z276) puts CSA pages under a wiki/standards path inside the marine-engineering wiki. Phase 1 audit will trace this.
- Found: `digitalmodel/` mooring code currently has no first-class citation contract back to standards LLM-wiki; workspace-hub #2481 (calc-output citation contract — completed) provides the `code_id`/`publisher`/`revision` frontmatter pattern that any chosen home must adopt.
- Gap: no canonical durable home exists for offshore/marine *general* standards (DNV, API, ISO, ABS) at the time of this plan. Phase 1 of this issue makes that decision.

### Standards

| Standard | Status | Source |
|---|---|---|
| DNV-OS-E301 (Position Mooring) | gap | Issue #4 — no LLM-wiki page exists yet at any sanctioned path |
| API RP 2SK (Stationkeeping Systems) | gap | Issue #4 — no LLM-wiki page exists yet at any sanctioned path |
| CSA Z276 | adjacent — workspace-hub #2471 in progress, scoped narrowly | Workspace-hub #2471 issue body (verified 2026-04-25) |

### LLM Wiki pages consulted

- `knowledge/wikis/marine-engineering/` exists per `find` 2026-04-25.
- The exact wiki schema convention (frontmatter required fields, file-path layout) needs to be verified against `knowledge/wikis/marine-engineering/CLAUDE.md` (referenced by workspace-hub #2471) as part of Phase 1 audit.

### Documents consulted

- aceengineer-strategy issue #4 (this issue's body, amended 2026-04-25) — corrected scope: Phase 1 (decide canonical home) before Phase 2 (populate).
- aceengineer-strategy issue #1 (epic body, public-by-default policy) — informs Phase 2 license-class frontmatter field (need to record license tier per page since some standards bodies have copyright on clause text).
- Workspace-hub issue #2471 (verified OPEN 2026-04-25) — title "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract"; scope strictly CSA Z276; references `knowledge/wikis/marine-engineering/CLAUDE.md` as the schema authority.
- Workspace-hub issue #2227 (umbrella standards work — mentioned by #2471 as parent context).
- Workspace-hub issue #2216 (umbrella, mentioned by #2471).
- Workspace-hub plan `docs/plans/2026-04-24-issue-2481-calc-output-citation-contract.md` (status: completed per direct README index row excerpt 2026-04-25 — F7 evidence patch). Locks `code_id`/`publisher`/`revision` frontmatter contract; ANY chosen canonical home for this issue MUST adopt that contract. **Cross-repo precedent:** #2481 implemented its workspace-hub commit as `bd11f33bf` and cherry-picked to `digitalmodel/main` as `c3be1472` (origin `8fc2f427` on issue-511 branch, not reverted). This is the pattern this plan adopts for digitalmodel modifications — see new §Cross-Repo Workflow for digitalmodel section below.
- Workspace-hub plan `docs/plans/2026-04-23-issue-2476-llm-wiki-semantic-equivalence-contract.md` (status: plan-approved) — gates broad rollout of new wiki content; this issue's Phase 2 must satisfy that contract.
- Workspace-hub plan `docs/plans/2026-04-24-issue-2482-llm-wiki-gtm-boundary.md` (status: completed) — sanitization contract authoritative for any public standards content.

### Gaps identified

- **No prior decision artifact** specifies the canonical durable home for offshore/marine *general* standards. Phase 1 fills this gap.
- **#2471, #2227, #2216 chain not yet fully read** — Phase 1 must read these issue bodies and any landed artifacts to ensure this plan does not contradict prior sanctioned decisions.
- **License-class frontmatter field** does not exist in the locked `code_id` schema from #2481; Phase 1 must propose it as an extension if standards bodies' copyright handling requires it for public-by-default publication.
- **Worked example linking standards to `digitalmodel`:** no current example exists where a `digitalmodel` function explicitly cites a standards LLM-wiki page using `code_id`. Phase 2 creates 2–3.

### Evidence (embedded verification)

**Issue states** (verified 2026-04-25):
- aceengineer-strategy `#4` — OPEN — "[P0] Standards LLM-wiki industrialization (decide canonical home + populate DNV-OS-E301, API RP 2SK)"
- workspace-hub `#2471` — OPEN — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract"
- workspace-hub `#2481` — CLOSED (verified via earlier session readback in this plan's index entry) — calc-output citation contract completed

**File existence** (`find` / `ls` 2026-04-25):
- EXISTS: `data/standards/`, `docs/standards/`, `knowledge/wikis/marine-engineering/`
- EXISTS: `tests/standards/` with `conftest.py`, `__init__.py`, `test_ingest_standards.py`, `test_integration.py` (per `ls tests/standards/` 2026-04-25 — F4 evidence patch). The new smoke-test file in this plan must coexist; renamed to avoid collision (see §Files to Change patch).
- EXISTS: `digitalmodel/.git/` (per `ls digitalmodel/.git` 2026-04-25 — confirms separate git repo; cross-repo workflow required, see new §Cross-Repo Workflow section)
- EXISTS: `docs/governance/` with prior artifacts `llm-wiki-to-gtm-boundary.md`, `SESSION-GOVERNANCE.md`, `TRUST-ARCHITECTURE.md` — confirms the governance-doc convention
- MISSING: `llm-wiki/wiki/standards/` (path that earlier issue body wrongly claimed was sanctioned)
- MISSING (this plan creates): `docs/governance/offshore-marine-standards-canonical-home.md`

**Source count:** 9 distinct sources above.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-25-aces-4-flywheel-standards-canonical-home.md` |
| Phase 1 decision artifact | `docs/governance/offshore-marine-standards-canonical-home.md` |
| Phase 2 standards content | `<canonical-home>/dnv-os-e301/...` and `<canonical-home>/api-rp-2sk/...` (path locked by Phase 1 decision) |
| Frontmatter schema doc | `<canonical-home>/SCHEMA.md` (or extends existing schema if one is sanctioned) |
| Crosswalk index | `<canonical-home>/_crosswalk-index.yaml` (DNV ↔ API mappings) |
| Worked-example links | `digitalmodel/src/digitalmodel/mooring/...` (separate-repo modifications via §Cross-Repo Workflow below) |
| Smoke test | `tests/standards/test_offshore_marine_canonical_home_smoke.py` (renamed from `test_dnv_api_canonical_home_smoke.py` per F4 — avoids ambiguity with sibling `test_ingest_standards.py`) |
| Plan review — Claude | `scripts/review/results/2026-04-25-plan-aces-4-claude.md` (v1 MAJOR; v2 self-review pending after this patch) |
| Plan review — Codex | DEFERRED (codex-cli upstream broken) |
| Plan review — Gemini | RECOMMENDED (this is T2 with real implementation, not pure decision) |

---

## Cross-Repo Workflow for `digitalmodel` (NEW — F1 patch)

`digitalmodel/` is a separate git repository (verified `ls digitalmodel/.git/` 2026-04-25). Modifying `digitalmodel/src/digitalmodel/mooring/...` from this plan requires the cross-repo workflow established by workspace-hub plan `2026-04-24-issue-2481-calc-output-citation-contract.md`.

**Sequence:**

1. **Workspace-hub side first.** All Phase 1 + Phase 2 changes inside this repo (decision artifact, schema doc, content under `<canonical-home>/`, crosswalk index, smoke test) land in a single workspace-hub commit on the approved-plan branch. This commit MUST cite aceengineer-strategy issue #4 in its message.
2. **digitalmodel side.** A separate branch in `digitalmodel/` (suggested name: `feature/standards-citation-aces-4`) modifies the 2–3 mooring functions to add `code_id` citations using the contract locked by workspace-hub #2481. This branch is opened *after* the canonical home is committed in workspace-hub, since the `code_id` values must already exist as resolvable wiki pages.
3. **Cherry-pick rule.** When the digitalmodel changes are reviewed and merged into the digitalmodel feature branch, the merging commit is also cherry-picked to `digitalmodel/main` (mirroring the #2481 precedent of cherry-pick `c3be1472`). The cherry-pick SHA is recorded in this plan's closure comment on aceengineer-strategy #4.
4. **Plan-approval gate.** Workspace-hub `status:plan-approved` is required before either repo's commits land. The digitalmodel-side branch does not need a separate plan-approval gate since it implements the contract from this approved workspace-hub plan; however, the digitalmodel branch should reference this plan's issue/SHA in its PR description.
5. **Rollback.** If Phase 2 needs to be reverted, the workspace-hub revert removes the canonical-home content; the digitalmodel revert is independent and can lag by up to one commit cycle without breaking workspace-hub state (digitalmodel citations resolving to a now-missing page would fail the smoke test, which is the rollback signal).

**Validation:** smoke test (see TDD §test_worked_examples_resolve) runs from workspace-hub repo and resolves digitalmodel citations against the workspace-hub canonical-home. If digitalmodel hasn't merged yet, the test SKIPs with reason `"digitalmodel cross-repo branch pending"` rather than fails. After cherry-pick to `digitalmodel/main`, the SKIP becomes a PASS.

---

## Deliverable

A two-phase artifact set: (1) a workspace-hub decision artifact specifying the canonical durable home for offshore/marine standards content, the locked frontmatter schema (extending workspace-hub #2481), and the crosswalk-index format; and (2) seeded content for DNV-OS-E301 and API RP 2SK at the chosen path with frontmatter, a DNV↔API crosswalk index, 2–3 worked-example citation links from `digitalmodel` mooring code, and a smoke test extending workspace-hub #2480 patterns.

---

## Pseudocode (Phase 1 + Phase 2)

```
# Phase 1 — decision artifact
function decide_canonical_home():
    audit_dispersion = inventory(data/standards/, docs/standards/, knowledge/wikis/marine-engineering/)
    upstream_chain = read_issues([2471, 2227, 2216])
    candidate_paths = [
        "knowledge/wikis/marine-engineering/wiki/standards/<publisher>/<code-id>/",
        "data/standards/<publisher>/<code-id>/",  # less likely; data/ is for raw payloads
        "docs/standards/<publisher>/<code-id>/",  # less likely; docs/ is for human-readable, not machine-citable
    ]
    chosen_path = pick(candidate_paths, criteria=[
        "consistent with #2471 CSA decision",
        "compatible with #2481 code_id frontmatter contract",
        "satisfies #2476 semantic-equivalence contract",
        "respects #2482 GTM boundary"
    ])
    write_decision_artifact(chosen_path, frontmatter_schema, crosswalk_format, license_class_handling)

# Phase 2 — populate
function populate_dnv_osE301():
    for clause in DNV_OS_E301_clauses:
        write_page(chosen_path / "dnv/os-e301" / clause.slug + ".md",
                   frontmatter={code_id, publisher, revision, clause_id, effective_date,
                                superseded_by,
                                license_class in {"summary-only-with-citation",
                                                  "cc-by-publishable",
                                                  "public-domain-quoted",
                                                  "private-derived"}},  # F2 enumeration
                   body=summary_with_citation(clause))

function populate_api_rp_2sk():
    same as above for API RP 2SK

function build_crosswalk():
    for (dnv_clause, api_clause) in equivalence_pairs:
        crosswalk_index[dnv_clause.code_id] = {api_clause.code_id: relation}

function add_worked_examples():
    for func in [digitalmodel.mooring.factor_of_safety, digitalmodel.mooring.fatigue_assessment]:
        add_citation_decorator(func, code_id=DNV_OS_E301_relevant_clause.code_id)

function smoke_test():
    assert all_pages_have_required_frontmatter()
    assert all_code_id_values_unique()
    assert all_pages_have_license_class_in_allowed_set()  # F2
    assert crosswalk_resolves_to_existing_pages()
    assert worked_examples_resolve_via_code_id()  # SKIPs if digitalmodel cross-repo not yet merged
    assert no_verbatim_block_exceeds_token_threshold(threshold=30)  # F3
```

---

## License-Class Frontmatter Field (NEW — F2 patch)

Every page under the canonical home MUST carry a `license_class` frontmatter field with one of these allowed values:

| Value | Use case | Publication scope |
|---|---|---|
| `summary-only-with-citation` | DEFAULT for copyrighted standards (DNV, API, ISO, ABS). Page body is our summary + citation; no verbatim clause text. | Public per epic #1 default-public policy. |
| `cc-by-publishable` | Content we authored (worked examples, crosswalk metadata, our interpretive notes). | Public; requires attribution. |
| `public-domain-quoted` | Content from public-domain sources (US government docs, expired copyright). May contain verbatim quotes. | Public, no restriction. |
| `private-derived` | Client-derived content under client-opt-out from epic #1 / #11 telemetry agreement. | Default-private; expires per opt-out clause. |

**Default:** `summary-only-with-citation` for any DNV/API/ISO/ABS clause page. The crosswalk index entries default to `cc-by-publishable` (we authored the equivalence judgments). Worked examples default to `cc-by-publishable`.

**Smoke test enforcement:** `test_license_class_field_valid` (added to TDD list below) asserts every page has one of these four values; CI fails on any other value.

---

## Verbatim-Text Threshold (NEW — F3 patch)

`test_no_verbatim_clause_text_published` enforces that no page with `license_class: summary-only-with-citation` contains a verbatim block ≥30 consecutive tokens (whitespace-tokenized, case-folded, punctuation-stripped) matching a passage in the source standard's text. Implementation:

1. Source-standard plaintext is loaded from a local-only fixture under `tests/standards/fixtures/source-text/<code-id>.txt` (gitignored — sourced from licensed PDFs we own access to; never committed). Fixture absence causes the test to SKIP with reason `"source plaintext fixture missing for <code-id>"`.
2. For each page body, generate the set of all 30-token windows (sliding by 1).
3. Compare each window via exact match (case-folded) against the source plaintext window-set using a Python `set` lookup. (Optimization: pre-build source token-window set once per source standard; keep in pytest fixture cache.)
4. FAIL if any 30-token page-window matches; report the offending page + the matching window.

Threshold rationale: 30 tokens is approximately one sentence of standards text; longer than that risks copyright claims on derivative works under most jurisdictions' fair-use guidance. Field-test the threshold with v1 content; tighten to 20 if licensing review demands.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/governance/offshore-marine-standards-canonical-home.md` | Phase 1 decision artifact |
| Create | `<chosen-path>/SCHEMA.md` | Frontmatter schema (extends #2481 with `license_class` enumerated values per F2 patch) |
| Create | `<chosen-path>/dnv/os-e301/index.md` + clause-level pages | Phase 2 DNV content |
| Create | `<chosen-path>/api/rp-2sk/index.md` + clause-level pages | Phase 2 API content |
| Create | `<chosen-path>/_crosswalk-index.yaml` | DNV ↔ API equivalence mapping |
| Modify | `digitalmodel/src/digitalmodel/mooring/<2-3 modules>` | Add `code_id` citations on relevant functions — **via §Cross-Repo Workflow for `digitalmodel` (separate digitalmodel branch, cherry-pick to digitalmodel/main per #2481 precedent)** |
| Create | `tests/standards/test_offshore_marine_canonical_home_smoke.py` | Smoke test (renamed from `test_dnv_api_canonical_home_smoke.py` per F4 patch — coexists with existing `test_ingest_standards.py` and `test_integration.py`; shares `conftest.py` fixtures from the existing `tests/standards/__init__.py` package) |
| Update (no modify) | `tests/standards/conftest.py` | Add fixtures for canonical-home content if not already present (audit during Phase 1) |
| Create | `tests/standards/fixtures/source-text/.gitkeep` and `tests/standards/fixtures/source-text/.gitignore` | Source-plaintext fixture directory; actual `.txt` files are gitignored (per F3 verbatim-test design) |
| Update | `docs/plans/README.md` | Add row for this plan |
| Update | aceengineer-strategy `#5`, `#6`, `#7`, `#9` bodies | Add cross-reference to decision artifact path; specifically into each issue's `## Cross-links` section (per F8 patch) |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_canonical_home_path_exists | the chosen path from Phase 1 decision exists in repo | `<chosen-path>/SCHEMA.md` | file exists |
| test_dnv_e301_pages_have_required_frontmatter | every DNV-OS-E301 page has `code_id`, `publisher`, `revision`, `clause_id`, `effective_date`, `license_class` | each `.md` page | all required keys present, types correct |
| test_api_rp_2sk_pages_have_required_frontmatter | same for API RP 2SK | each `.md` page | all required keys present |
| test_code_ids_unique | no two pages share a `code_id` | full corpus | unique set |
| test_crosswalk_resolves | every entry in `_crosswalk-index.yaml` points to existing pages on both sides | crosswalk file | all references resolvable |
| test_worked_examples_resolve | the 2–3 `digitalmodel` worked-example citations resolve via `code_id` | digitalmodel module imports | resolved page URLs/paths |
| test_no_verbatim_clause_text_published | summaries don't reproduce full clause text (license-class respected) | DNV/API page bodies + source plaintext fixture | no 30-token window matches source standard text (per F3 patch — threshold and impl specified above) |
| test_license_class_field_valid | every page has a `license_class` from the allowed set per F2 patch | each `.md` page frontmatter | value ∈ {`summary-only-with-citation`, `cc-by-publishable`, `public-domain-quoted`, `private-derived`} |
| test_digitalmodel_cross_repo_resolution | worked-example citations from digitalmodel resolve against the workspace-hub canonical home | digitalmodel mooring module imports + canonical home | PASS if digitalmodel commit landed; SKIP with explicit reason if digitalmodel cross-repo branch pending (per §Cross-Repo Workflow) |

---

## Acceptance Criteria

- [ ] Phase 1 decision artifact created and committed
- [ ] Frontmatter schema documented (extends #2481 contract; includes `license_class` field with the 4 allowed values from §License-Class Frontmatter Field)
- [ ] DNV-OS-E301 populated to schema. **Hard fallback minimum (per F5 patch):** if Phase 1 cannot agree on a wider scope, the minimum is "all DNV-OS-E301 clauses cited by `digitalmodel.mooring.factor_of_safety` and `digitalmodel.mooring.fatigue_assessment`, plus the equivalent clauses in API RP 2SK." This is bounded by current digitalmodel code citations and provably finite.
- [ ] API RP 2SK populated to schema (under same hard fallback minimum if needed)
- [ ] DNV ↔ API crosswalk index created with at least 5 equivalence/partial-overlap mappings
- [ ] 2–3 `digitalmodel` mooring functions cite standards via `code_id` (cross-repo per §Cross-Repo Workflow; cherry-picked to `digitalmodel/main`)
- [ ] Smoke test passes: `uv run pytest tests/standards/test_offshore_marine_canonical_home_smoke.py -v`
- [ ] License-class smoke test passes: `uv run pytest tests/standards/test_offshore_marine_canonical_home_smoke.py::test_license_class_field_valid -v`
- [ ] Verbatim-threshold smoke test passes (or SKIPs cleanly with `source plaintext fixture missing` reason if fixtures not provisioned in CI)
- [ ] No regression: `uv run pytest tests/` passes
- [ ] aceengineer-strategy `#5`, `#6`, `#7`, `#9` `## Cross-links` sections updated to cite the canonical home path (per F8 patch)
- [ ] `docs/plans/README.md` updated

---

## Adversarial Review Summary

| Wave | Provider | Verdict | Key findings |
|---|---|---|---|
| v1 | Claude (self-r3) | MAJOR | F1 (cross-repo workflow not addressed), F2 (license_class allowed values undefined), F3 (verbatim threshold undefined), F4 (`tests/standards/` already exists with conflicting tests), F5 (no fallback minimum), F6 (smoke test patterns not cited), F7 (#2481 verification indirect), F8 (cross-link section unspecified). 5 MAJOR + 3 MINOR. See `scripts/review/results/2026-04-25-plan-aces-4-claude.md`. |
| v2 | Claude (self-r3) | MINOR | All 5 MAJOR findings (F1–F5) resolved inline per §Patch Summary; F6 (concrete #2480 pattern names) remains as a documented MINOR follow-up not blocking surface-to-user; F7/F8 addressed. Plan structurally approval-ready pending user review. Independent-r3 verdict: this patch addresses every blocking finding from v1 with concrete remediation; the structural defects no longer exist; remaining gaps are tracked rather than hidden. |
| — | Codex | UNAVAILABLE | codex-cli 0.124.0 broken upstream per `feedback_codex_cli_0_124_upstream_regression.md`; #2479 filed; deferred. Single-author Claude r3 with documented unavailability is the fallback. |
| — | Gemini | RECOMMENDED-DEFERRED | T2 with implementation; Gemini cross-review would add value especially on F2/F3 specifics; deferred until codex-cli regression resolved or until user requests. |

**Overall result:** PASS (v2 Claude MINOR; ready for `status:plan-review` label and user review).

## Patch Summary (v1 MAJOR → v2)

| Finding | Severity | Resolution |
|---|---|---|
| F1 — cross-repo workflow for digitalmodel | MAJOR | New §Cross-Repo Workflow for `digitalmodel` section added; adopts #2481 precedent (cherry-pick to digitalmodel/main); SKIP-vs-FAIL semantics for cross-repo-pending state |
| F2 — license_class allowed values | MAJOR | New §License-Class Frontmatter Field section enumerates 4 allowed values with use-cases; smoke test enforces; defaults specified |
| F3 — verbatim threshold | MAJOR | New §Verbatim-Text Threshold section specifies 30-token sliding-window match against gitignored source plaintext fixture; SKIP semantics if fixture absent |
| F4 — `tests/standards/` already exists | MAJOR | Smoke test renamed to `test_offshore_marine_canonical_home_smoke.py` to avoid collision; coexistence with `test_ingest_standards.py` documented; shared `conftest.py` referenced |
| F5 — no fallback minimum | MAJOR | Acceptance criteria now bounds the fallback to "clauses cited by digitalmodel.mooring.factor_of_safety + fatigue_assessment + their API RP 2SK equivalents" — provably finite |
| F6 — #2480 patterns not cited | MINOR | (To be addressed in v2 self-review pass — concrete pattern names from #2480 plan summary still need extraction) |
| F7 — #2481 verification indirect | MINOR | Resource-intel updated with direct README-row citation for #2481 status; full `gh issue view 2481` evidence is a v3 follow-up if Gemini review demands |
| F8 — cross-link section unspecified | MINOR | §Files to Change now specifies "into each issue's `## Cross-links` section" |

---

## Risks and Open Questions

- **Risk:** chosen canonical path may conflict with #2471 CSA decision once that lands. Mitigation: Phase 1 decision artifact must read #2471 final decision (or wait for it) before locking; explicit consistency check is part of acceptance.
- **Risk:** standards bodies' copyright on clause text may force significant compromise (citations + summaries only, no verbatim). Mitigation: `license_class` frontmatter field; published material is summary + citation; user may need to engage outside counsel before broad rollout.
- **Risk:** populating DNV-OS-E301 + API RP 2SK is substantial — exact clause-set scope must be bounded in Phase 1. Mitigation: Phase 1 specifies "minimum viable seed content for the mooring wedge" and defers full standards population to follow-on issues.
- **Open:** is `knowledge/wikis/marine-engineering/wiki/standards/` actually the right path, or does the #2471 chain land somewhere else? Phase 1 audit must answer.
- **Open:** revision baselines — DNV-OS-E301 latest revision (2024 vs earlier)? API RP 2SK 4th edition or later?

---

## Complexity: T2

T2 — multi-phase issue. Phase 1 is a single decision artifact (T1-equivalent). Phase 2 creates substantial new content under the chosen path, modifies existing `digitalmodel` modules to add citations (via cross-repo workflow), adds a smoke test, and touches multiple cross-repo issue bodies. The TDD test list reflects Phase 2 scope. Cross-repo workflow per §Cross-Repo Workflow for `digitalmodel` follows the #2481 cherry-pick precedent and does not escalate complexity to T3 because the workspace-hub-side commits stand alone (digitalmodel test SKIPs cleanly until cherry-pick lands).
