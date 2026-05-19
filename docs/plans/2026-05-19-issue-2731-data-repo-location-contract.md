# Plan for #2731: Data/repo location contract for llm-wiki promotion

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-05-19
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2731
> **Review artifacts:** scripts/review/results/2026-05-19-plan-2731-claude.md | scripts/review/results/2026-05-19-plan-2731-codex.md | scripts/review/results/2026-05-19-plan-2731-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `docs/ROUTING_INDEX.md` — identifies `workspace-hub` as the portfolio control plane for issue planning, agent harness, durable standards, document-intelligence registries, and cross-repo routing. This supports making `workspace-hub` the governance/documentation owner rather than a parent folder that contains all implementation repos.
- Found: `data/document-index/mounted-source-registry.yaml` — already models source roots such as `/mnt/local-analysis/workspace-hub`, `/mnt/ace/docs/_standards`, `/mnt/ace/docs`, and `/mnt/ace-data/digitalmodel/docs/domains`. It provides the nearest existing machine-readable contract for source-root reachability and canonical storage policies.
- Found: `/mnt/ace/README.md` — already declares `/mnt/ace` as canonical external storage for engineering data exceeding git repo limits and lists repo overflow, reference standards, legacy data, and placement rules.
- Gap: no existing single ledger will define the canonical checkout style for active repos under `/mnt/local-analysis`, classify private/public `llm-wiki` repo placement, classify `/mnt/ace` bulk/source roots, and list migration transactions without performing them.

### Standards

| Standard | Status | Source |
|---|---|---|
| Hard-stop policy | active; applies because issue has `cat:data-pipeline` | `docs/standards/HARD-STOP-POLICY.md` |
| Parallel-first execution | active; planning/recon can be `parallel-readonly`; implementation remains gated | `docs/standards/PARALLEL_FIRST_EXECUTION.md` |
| LLM-wiki operating model | normative; defines L1 source docs, L2 registry/provenance, L3 durable knowledge, L5 plans/issues | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` |

### LLM Wiki pages consulted

- No repo-local `knowledge/wikis/**` page was required for this planning slice. This issue is a storage/governance contract for the data and repo location substrate that future wiki promotion will consume.
- Consulted the normative LLM-wiki operating model instead: `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — raw/source documents belong to L1, provenance/registries to L2, durable wiki knowledge to L3, and issue plans/reviews to L5.

### Documents consulted

- Issue [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) — requests concrete inventory and normalization of canonical data/repo locations for `llm-wiki` promotion; current comment updates state the plan should use an adjacent sibling checkout model and should not move data or repos during planning.
- Issue [#2727](https://github.com/vamseeachanta/workspace-hub/issues/2727) — closed parent defining the data layer boundary and `llm-wiki` data promotion model.
- Issue [#2732](https://github.com/vamseeachanta/workspace-hub/issues/2732) — open sibling for canonical first/second-level mount and folder taxonomy; this plan will avoid duplicating that full mount taxonomy and will consume it as a follow-on dependency where needed.
- `docs/plans/README.md` — requires issue → resource intelligence → plan → adversarial review → `status:plan-review` → user approval → `status:plan-approved` → implementation.
- `docs/document-intelligence/data-intelligence-map.md` — maps document-index registries and currently describes `/mnt/ace-data` as an alias to `/mnt/ace`; it also references per-repo data registries that may not exist as adjacent checkouts on this machine.
- `docs/CONTENT_INDEX.md` — contains stale nested path examples such as `/mnt/local-analysis/workspace-hub/digitalmodel`, `/mnt/local-analysis/workspace-hub/worldenergydata`, and `/mnt/local-analysis/workspace-hub/assetutilities`; these will be inventoried and corrected or marked legacy under this issue.

### Gaps identified

- No canonical `docs/standards/` contract currently states that tier-1 implementation repos should be adjacent sibling checkouts under `/mnt/local-analysis/<repo>` rather than nested under `/mnt/local-analysis/workspace-hub/<repo>`.
- No machine-readable ledger currently classifies each relevant path class as active checkout, public wiki repo, private client wiki repo, raw/client source data, standards/reference corpus, repo overflow, extraction staging, generated report, alias, or legacy/stale path.
- No transaction ledger currently separates `NO-MOVE`, `MOVE`, `RECLASSIFY`, `ALIAS-SUPPORT`, and `ALIAS-RETIRE` decisions for `/mnt/local-analysis`, `/mnt/ace`, `/mnt/ace-data`, and stale nested workspace paths.
- No validation currently blocks future docs from reintroducing nested checkout references after this contract is established.
- No implementation-notes HTML artifact currently captures interpretation, deviations, tradeoffs, and open questions while this issue executes.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-19T18:49:33-05:00 via `gh issue view`):

- `#2731` — OPEN — feat(data-governance): inventory and normalize canonical data/repo locations for llm-wiki promotion
- `#2726` — CLOSED — feat(architecture): review data, execution, and report layer boundaries
- `#2727` — CLOSED — feat(architecture): define data layer boundary and llm-wiki data promotion model
- `#2732` — OPEN — feat(data-governance): canonical first/second-level mount and folder taxonomy for repo ecosystem

**File existence** (`test -e` / live reads, 2026-05-19T18:49:33-05:00):

- EXISTS: `docs/plans/_template-issue-plan.md`
- EXISTS: `docs/plans/README.md`
- EXISTS: `docs/standards/HARD-STOP-POLICY.md`
- EXISTS: `docs/standards/PARALLEL_FIRST_EXECUTION.md`
- EXISTS: `docs/document-intelligence/data-intelligence-map.md`
- EXISTS: `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- EXISTS: `data/document-index/mounted-source-registry.yaml`
- EXISTS: `/mnt/ace/README.md`
- MISSING (new — this plan will create/update via implementation): `docs/standards/REPO_AND_DATA_LOCATION_CONTRACT.md`
- MISSING (new — this plan will create/update via implementation): `data/document-index/repo-data-location-ledger.yaml`
- MISSING (new — this plan will create/update via implementation): `docs/reports/issue-2731-implementation-notes.html`

**Live layout proof** (`find /mnt/local-analysis`, 2026-05-19T18:49:33-05:00):

```text
/mnt/local-analysis first level dirs:
assetutilities
digitalmodel
workspace-hub

Git repos at maxdepth 2:
/mnt/local-analysis/assetutilities
/mnt/local-analysis/digitalmodel
/mnt/local-analysis/workspace-hub

/mnt/ace-data alias:
/mnt/ace-data -> /mnt/ace
realpath -m /mnt/ace-data -> /mnt/ace
```

The implementation will re-run this live probe. If cleanup changes leave only `/mnt/local-analysis/workspace-hub`, the contract will record the observed checkout set without claiming absent repos exist on this machine.

**`/mnt/ace` source/bulk proof** (`/mnt/ace/README.md`, lines 1-17):

```text
# /mnt/ace — Canonical External Storage
Local drive (7.3 TB ext4) on ace-linux-1 for engineering data that exceeds git repo limits.
Repo Overflow includes digitalmodel/, worldenergydata/, frontierdeepwater/, client_projects/, rock-oil-field/, saipem/, doris/.
```

**Operating-model proof** (`docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`, lines 46-53):

```text
L1 Source documents — raw external/source files and original locations.
L2 Registry / provenance — inventory, content hashes, file paths, extraction lineage, availability status.
L3 Durable knowledge — LLM-wiki pages and promoted summaries.
L5 Execution state — GitHub issues, plans under docs/plans/, review artifacts.
```

**Stale nested-path proof** (`docs/CONTENT_INDEX.md` excerpts):

```text
Repository: digitalmodel — Path: /mnt/local-analysis/workspace-hub/digitalmodel
Repository: worldenergydata — Path: /mnt/local-analysis/workspace-hub/worldenergydata
Repository: assetutilities — Path: /mnt/local-analysis/workspace-hub/assetutilities
```

**Reproduction proofs:** N/A — this is a governance/data-location planning issue, not a runtime failure. The required empirical proof is the live filesystem/path-reference inventory above and the implementation validation below.

**Distinct source count:** 10+ (`#2731`, `#2727`, `#2732`, `docs/plans/README.md`, `docs/standards/HARD-STOP-POLICY.md`, `docs/standards/PARALLEL_FIRST_EXECUTION.md`, `docs/document-intelligence/data-intelligence-map.md`, `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`, `data/document-index/mounted-source-registry.yaml`, `/mnt/ace/README.md`, `docs/CONTENT_INDEX.md`).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-19-issue-2731-data-repo-location-contract.md` |
| Canonical contract | `docs/standards/REPO_AND_DATA_LOCATION_CONTRACT.md` |
| Machine-readable ledger | `data/document-index/repo-data-location-ledger.yaml` |
| Implementation notes | `docs/reports/issue-2731-implementation-notes.html` |
| Validation tests | `tests/docs/test_repo_data_location_contract.py` |
| Optional path-reference scan script | `scripts/docs/check-repo-data-location-contract.py` |
| Planning index | `docs/plans/README.md` |
| Plan review — Claude | `scripts/review/results/2026-05-19-plan-2731-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-19-plan-2731-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-19-plan-2731-gemini.md` |

---

## Deliverable

A canonical repo/data location contract, machine-readable ledger, validation tests, and implementation-notes report will define how active repos, raw/source data, private/public `llm-wiki` corpora, aliases, and migration transactions should be placed and governed without moving data during this issue.

---

## Pseudocode

```text
function collect_live_layout():
    enumerate /mnt/local-analysis first-level directories
    enumerate git repos under /mnt/local-analysis at maxdepth 2
    resolve /mnt/ace-data and /mnt/ace real paths
    sample /mnt/ace first-level directories relevant to repo overflow, standards, client roots, and llm-wiki corpora
    write compact evidence into implementation notes

function classify_path(path):
    if path is /mnt/local-analysis/workspace-hub:
        return control-plane repo checkout
    if path matches /mnt/local-analysis/<tier-1-repo> and has .git:
        return active adjacent sibling checkout
    if path matches /mnt/local-analysis/workspace-hub/<repo>:
        return legacy/non-canonical nested checkout reference unless explicitly temporary
    if path is /mnt/ace or child raw/client/reference/overflow root:
        return source/bulk storage class with L1/L2 ownership notes
    if path is /mnt/ace-data:
        return alias to /mnt/ace with support-or-retire decision
    if path is planned private llm-wiki repo:
        return planned adjacent private repo target, absent until explicitly created

function build_location_ledger():
    for each observed or planned path:
        record path, realpath, class, canonicality, owner layer, git status expectation, data sensitivity class, move decision, and validation command
    assert every MOVE/RECLASSIFY decision has source, target, rollback, no-delete posture, and child-plan requirement

function validate_docs_contract():
    load canonical contract markdown
    load YAML ledger
    assert required path classes exist
    assert /mnt/local-analysis/<repo> sibling checkout rule exists
    assert /mnt/local-analysis/workspace-hub/<repo> is classified legacy/non-canonical
    assert /mnt/ace-data alias decision is explicit
    assert private/client raw data cannot promote directly to public llm-wiki without sanitized derivative approval gate
    scan selected docs for stale nested paths and require either correction or legacy annotation
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/REPO_AND_DATA_LOCATION_CONTRACT.md` | Human-readable canonical contract for repo checkout placement, data roots, wiki roots, alias policy, and promotion boundaries |
| Create | `data/document-index/repo-data-location-ledger.yaml` | Machine-readable ledger for observed/planned paths, classes, sensitivity, owner layer, canonicality, and transaction decisions |
| Create | `tests/docs/test_repo_data_location_contract.py` | TDD coverage for contract sections, ledger schema, alias decision, nested-path policy, and promotion-gate rules |
| Create | `docs/reports/issue-2731-implementation-notes.html` | Required running notes for design decisions, deviations, tradeoffs, and open questions |
| Create or Update | `scripts/docs/check-repo-data-location-contract.py` | Optional deterministic scanner if tests need reusable path-reference classification logic |
| Update | `docs/document-intelligence/data-intelligence-map.md` | Normalize `/mnt/ace-data` wording based on explicit alias decision and point to the new contract/ledger |
| Update | `data/document-index/mounted-source-registry.yaml` | Normalize source-root policy references where they conflict with `/mnt/ace` canonical/alias wording; avoid bulk source moves |
| Update | `docs/ROUTING_INDEX.md` | Point repo routing and control-plane semantics to the new contract |
| Update | `docs/CONTENT_INDEX.md` | Correct or mark stale nested checkout paths as legacy/non-canonical, without claiming absent checkouts exist |
| Update | `docs/plans/README.md` | Add this plan to the issue-plan index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_contract_declares_adjacent_sibling_checkout_model` | The standard states tier-1 repos live under `/mnt/local-analysis/<repo>` when present | `docs/standards/REPO_AND_DATA_LOCATION_CONTRACT.md` | includes sibling checkout rule and `workspace-hub` control-plane exception |
| `test_nested_workspace_repo_paths_are_noncanonical` | Nested `workspace-hub/<repo>` checkout references are legacy/non-canonical unless explicitly temporary | standard + ledger | policy exists; no silent canonical nested repo class |
| `test_ace_is_canonical_bulk_source_mount` | `/mnt/ace` is canonical source/bulk mount for raw/source/reference/overflow data | standard + ledger | `/mnt/ace` class exists with L1/L2 ownership notes |
| `test_ace_data_alias_decision_is_explicit` | `/mnt/ace-data` is not ambiguous | ledger alias entry | decision is one of `supported_alias` or `retired_wording`, with rationale |
| `test_private_client_data_public_promotion_requires_gate` | Private/client raw/readable data cannot flow directly to public `llm-wiki` | standard | explicit sanitized-derivative approval gate exists |
| `test_ledger_has_required_path_classes` | The ledger covers active checkout, public wiki repo, private client wiki repo, raw source, standards/reference, repo overflow, staging, reports, alias, legacy | ledger YAML | all required classes present |
| `test_move_transactions_are_noop_until_child_approval` | The ledger cannot authorize raw data/repo movement in this issue | ledger YAML | all `MOVE` decisions are planned-only and require child plan/user approval |
| `test_live_layout_probe_is_documented` | Implementation notes contain the live checkout set and do not claim full tier-1 coverage | HTML notes | includes timestamped live probe and observed repo list |
| `test_selected_docs_do_not_reintroduce_unannotated_nested_repo_paths` | Key docs either avoid nested paths or mark them legacy | selected docs scan | no unannotated `/mnt/local-analysis/workspace-hub/<repo>` for tier-1 repos |

---

## Acceptance Criteria

- [ ] RED phase is captured: `uv run pytest tests/docs/test_repo_data_location_contract.py -v` fails before the contract/ledger exists.
- [ ] GREEN phase passes: `uv run pytest tests/docs/test_repo_data_location_contract.py -v`.
- [ ] The contract clearly states the adjacent sibling checkout model: `/mnt/local-analysis/workspace-hub` is the control-plane repo; tier-1 implementation repos are `/mnt/local-analysis/<repo>` when checked out on a machine.
- [ ] The contract explicitly states that `/mnt/local-analysis/workspace-hub/<repo>` nested implementation checkouts are non-canonical legacy references unless a future approved plan grants a temporary shim.
- [ ] The ledger enumerates the live checkout set observed during implementation and does not claim every tier-1 repo is present on ace-linux-1.
- [ ] The ledger defines planned private client `llm-wiki` repo targets as planned/absent unless explicitly created by a later approved issue.
- [ ] `/mnt/ace` is documented as canonical bulk/source storage; `/mnt/ace-data` is resolved as either a supported alias or retired wording with migration-safe rationale.
- [ ] Private/client raw or readable data has no direct path to public `llm-wiki`; sanitized derivatives require explicit approval gate, source-class separation, and citation/provenance separation.
- [ ] Any location movement is represented only as a future transaction record with source, target, rollback, owner, risk, and child-plan requirement; no raw data, repo, symlink, or bulk folder is moved by this issue.
- [ ] `docs/reports/issue-2731-implementation-notes.html` captures design decisions, deviations, tradeoffs, and open questions.
- [ ] Selected docs (`docs/document-intelligence/data-intelligence-map.md`, `data/document-index/mounted-source-registry.yaml`, `docs/ROUTING_INDEX.md`, `docs/CONTENT_INDEX.md`) are updated or annotated so stale nested paths are not presented as current canonical placement.
- [ ] Legal/security scan passes: `scripts/legal/legal-sanity-scan.sh`.
- [ ] Plan review artifacts are posted to `scripts/review/results/` and the issue is labeled `status:plan-review` only after review findings are resolved.

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Not yet run |
| Codex | PENDING | Not yet run |
| Gemini | PENDING | Not yet run |

**Overall result:** PENDING — adversarial plan review required before `status:plan-review`.

Revisions made based on review:
- None yet.

---

## Risks and Open Questions

- **Risk:** `/mnt/local-analysis` cleanup state can change quickly. The implementer will re-run live filesystem probes and will record only observed repos, not assumed tier-1 coverage.
- **Risk:** `docs/CONTENT_INDEX.md` is large and may contain generated/stale inventory. The plan will classify/correct canonical path claims without turning this issue into a full content-index regeneration unless tests prove regeneration is required.
- **Risk:** `/mnt/ace-data` appears in existing docs and registries. Retiring wording too aggressively may break users/scripts; supporting it forever may perpetuate ambiguity. The contract must pick and justify one alias posture.
- **Risk:** Repo checkout placement and raw/source data placement can be conflated. The contract and ledger will keep these as separate classes and will fail tests if a repo checkout rule implies moving bulk data.
- **Risk:** Private client wiki target names may become over-specified before repos exist. The ledger will classify them as planned targets, not present repos.
- **Open:** Should the final contract preserve `/mnt/ace-data` as an accepted human-facing alias, or should new docs use `/mnt/ace` only while scripts tolerate the alias?
- **Open:** Should stale nested checkout paths in generated indexes be corrected in place, or should a generated-index note point to the contract and defer full regeneration to a follow-up issue?

---

## Complexity: T3

**T3** — this is a cross-cutting data-governance and repo-topology contract touching issue workflow, data registries, document-intelligence docs, path-reference validation, private/public promotion gates, and live machine layout evidence. It needs multi-provider adversarial plan review before user approval and implementation.
