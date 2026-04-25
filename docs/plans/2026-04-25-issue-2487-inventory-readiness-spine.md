# Plan for #2487: Raw-data to GTM readiness matrix and dispatch board

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-04-25
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2487
> **Review artifacts:** `scripts/review/results/2026-04-25-plan-2487-claude.md` | `scripts/review/results/2026-04-25-plan-2487-codex.md` | `scripts/review/results/2026-04-25-plan-2487-gemini.md` | `scripts/review/results/2026-04-25-plan-2487-disagreement.md`

---

## Resource Intelligence Summary

### Existing repo code and data surfaces
- `docs/reports/provider-work-queue.md` — current provider dispatch signal; generated `2026-04-25T09:20:15.784834Z`, recommended order `codex, gemini, claude`, and current ready counts: Codex `4`, Gemini `1`, Claude `17`.
- `tools/SCHEMA_COMPARISON.md` — inventory/knowledge database join contract: `/mnt/ace/.ace-knowledge/index.db` and `/mnt/ace/O&G-Standards/_inventory.db` share `file_path`; inventory has `27,980` documents, `26,982` text records, `1,043,616` chunks, and `27,343` overlapping files with the knowledge DB.
- `data/document-index/registry.yaml` — existing document-index registry used as the durable source registry surface.
- `data/document-index/resource-intelligence-maturity.yaml` — existing maturity/status vocabulary for intelligence resources.
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — existing operating model for promoting source/resource intelligence into durable llm-wiki surfaces.
- `docs/plans/2026-04-24-issue-2481-calc-output-citation-contract.md` — related local plan for calculation-output citation contracts; #2487 consumes this as downstream citation/provenance context.

### Related issues and dependency roles
| Issue | Role in #2487 | Required for #2487 implementation? | Notes |
|---|---|---:|---|
| #2487 | current spine | yes | creates readiness matrix + dispatch board contract |
| #2481 | citation/provenance reference | no | local plan exists and informs calculation-output evidence fields |
| #2471 | downstream/live dependency | no | no local plan artifact found; #2487 must link it as issue-backed dependency only |
| #2464 | downstream Codex implementation candidate | no | strongest immediate Codex lane after #2487 approval |
| #2403 | downstream Gemini/model-selection candidate | no | research/model-selection lane after matrix exists |
| #2346 | downstream website/GTM candidate | no | GTM lane once upstream readiness evidence exists |
| #2465 | downstream re-audit candidate | no | plan-approved but should be re-audited before dispatch |
| #2402 | future planning/review candidate | no | remains not approved for implementation |
| #2392 | future planning/review candidate | no | coverage-gap detector candidate after spine exists |

### Gaps identified
- No canonical `config/knowledge/inventory-readiness.yaml` exists to connect raw data, inventory, llm-wiki, calculation code, parametric outputs, and website/GTM deliverables.
- No validator exists to enforce readiness status rules or reject unsupported `READY` claims.
- No generated report exists that turns provider work queue + source readiness into dispatchable packages.
- Existing provider queue counts are an observed input, not a success threshold; #2487 must not fabricate backlog readiness.

### Evidence
**Verified 2026-04-25T09:53:43Z**:
- #2487 is OPEN with labels: `enhancement`, `priority:high`, `cat:data-pipeline`, `cat:documentation`, `domain:knowledge-management`.
- File existence check from isolated worktree:
  - EXISTS: `docs/reports/provider-work-queue.md`
  - EXISTS: `tools/SCHEMA_COMPARISON.md`
  - EXISTS: `data/document-index/registry.yaml`
  - EXISTS: `data/document-index/resource-intelligence-maturity.yaml`
  - EXISTS: `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
  - EXISTS: `docs/plans/2026-04-24-issue-2481-calc-output-citation-contract.md`
  - CREATE: `config/knowledge/inventory-readiness.yaml`
  - CREATE: `scripts/knowledge/validate_inventory_readiness.py`
  - CREATE: `tests/knowledge/test_inventory_readiness.py`
  - CREATE: `docs/reports/inventory-readiness-matrix-2026-04-25.md`

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-25-issue-2487-inventory-readiness-spine.md` |
| Canonical machine config | `config/knowledge/inventory-readiness.yaml` |
| Validator / renderer | `scripts/knowledge/validate_inventory_readiness.py` |
| TDD tests | `tests/knowledge/test_inventory_readiness.py` |
| Derived dispatch report | `docs/reports/inventory-readiness-matrix-2026-04-25.md` |
| Plan index | `docs/plans/README.md` |

---

## Deliverable

Create a machine-checkable inventory readiness spine that maps each package family across `raw_data -> inventory -> llm_wiki -> calculation_code -> parametric_outputs -> website_gtm`, validates evidence-backed readiness statuses, and renders a provider dispatch board for Codex/Gemini/Claude work packages.

---

## Scope Boundaries

### In scope
- Add a small stdlib-only YAML/JSON validator-renderer for the readiness matrix.
- Add a canonical YAML config with initial rows grounded in existing reports/issues.
- Add TDD tests for schema, readiness rules, dependency roles, and report rendering.
- Render a markdown dispatch board that separates observed provider queue counts from readiness assertions.
- Use #2481 as local citation-contract context and #2471 as live issue dependency context.

### Out of scope
- Do not implement downstream #2464/#2403/#2346/#2465/#2402/#2392 work.
- Do not build embeddings, llm-wiki promotion, calculation solvers, or GTM website assets in this issue.
- Do not mark issue rows `READY` without required evidence.
- Do not mutate/downgrade invalid YAML into a weaker status; invalid `READY` claims must fail validation.

---

## Canonical Schema Contract

`config/knowledge/inventory-readiness.yaml` is the source of truth. The markdown report is derived.

Top-level shape:

```yaml
schema_version: 1
provider_queue_snapshot:
  generated_at: "2026-04-25T09:20:15.784834Z"
  source: docs/reports/provider-work-queue.md
  current_counts:
    codex_candidates: 4
    gemini_tasks: 1
    claude_reviews: 17
package_families:
  - id: og_standards_to_gtm
    title: O&G standards source-to-GTM readiness
    owner_provider: codex|gemini|claude
    preferred_next_provider: codex|gemini|claude
    readiness:
      raw_data: READY|PARTIAL|MISSING|STALE|BLOCKED
      inventory: READY|PARTIAL|MISSING|STALE|BLOCKED
      llm_wiki: READY|PARTIAL|MISSING|STALE|BLOCKED
      calculation_code: READY|PARTIAL|MISSING|STALE|BLOCKED
      parametric_outputs: READY|PARTIAL|MISSING|STALE|BLOCKED
      website_gtm: READY|PARTIAL|MISSING|STALE|BLOCKED
    evidence:
      raw_data_paths: []
      inventory_artifacts: []
      wiki_doc_keys: []
      calculation_artifacts: []
      parametric_artifacts: []
      website_gtm_artifacts: []
      issue_refs:
        - issue: 2464
          relation: downstream_candidate|dependency|reference
          approval_state: plan-approved|plan-review|open|closed|unknown
          produces_stages: []
          implemented_artifacts: []
          artifact_contract: string|null
    dependency_roles:
      - issue: 2471
        role: downstream_only|partial_only|blocking
        reason: string
    dispatch:
      ready_for_provider: codex|gemini|claude|null
      rationale: string
      dependency_issues: []
      expected_output_artifact: string|null
```

Allowed readiness enum values: `READY`, `PARTIAL`, `MISSING`, `STALE`, `BLOCKED`.
Allowed dependency roles: `blocking`, `partial_only`, `downstream_only`.
Allowed providers: `codex`, `gemini`, `claude`, or `null` where no provider can act yet.

Readiness decision rules:
- `READY` requires at least one concrete supporting evidence item for that stage.
- `llm_wiki: READY` requires at least one `wiki_doc_keys` entry; if a parent/source contract requires `doc_key` and none is present, validation fails.
- `calculation_code: READY` requires implemented `calculation_artifacts`; an approved plan without implemented artifacts can support only `PARTIAL`.
- `parametric_outputs: READY` requires implemented `parametric_artifacts`; an approved plan without implemented artifacts can support only `PARTIAL`.
- `website_gtm: READY` requires implemented `website_gtm_artifacts`; an approved plan without implemented artifacts can support only `PARTIAL`.
- `issue_refs[]` entries are typed evidence objects. `approval_state` and `produces_stages` can explain why a stage is `PARTIAL`, but they cannot by themselves make that stage `READY` unless `implemented_artifacts` also contains concrete artifact paths.
- `BLOCKED` requires at least one `dependency_roles` entry with `role: blocking`.
- `PARTIAL` may be used when evidence exists for some but not all downstream handoff requirements.
- `MISSING` means no usable evidence is present for that stage.
- `STALE` requires a concrete stale source/review artifact reference.

Provider dispatch rules:
- Codex: implementation/test/fix packages, calculation-code adapters, validator/report code, mechanical refactors.
- Gemini: raw-data scouting, source scans, competitive/GTM research, gap discovery, model-selection spikes.
- Claude: plan synthesis, adversarial review, governance/architecture decisions, issue decomposition.
- A row can be dispatched only when `dispatch.ready_for_provider` is non-null and `dispatch.rationale` names the next evidence-producing action. `dispatch.dependency_issues` must mirror any issue refs needed for that action.

First-run behavior:
- Missing config path exits nonzero and prints the expected path.
- Valid config with zero `package_families` exits nonzero because it cannot produce a dispatch board.
- Missing provider queue snapshot is allowed only if `provider_queue_snapshot.source` is null and `current_counts` are all null; the markdown must label counts as `unknown`, not zero.

Malformed data behavior:
- Unknown enum/provider/dependency role exits nonzero.
- Required field omission exits nonzero and names the missing path.
- Unsupported `READY` exits nonzero; the validator must not silently downgrade readiness.
- Duplicate package IDs exit nonzero.

---

## Pseudocode

```text
load YAML from config/knowledge/inventory-readiness.yaml
validate top-level keys: schema_version, provider_queue_snapshot, package_families
validate schema_version == 1
validate provider queue counts are integers >= 0 or null
for each package family:
    validate unique id, title, providers, readiness stages, evidence lists
    validate typed issue_refs: issue, relation, approval_state, produces_stages, implemented_artifacts, artifact_contract
    validate dependency_roles issue + role + reason
    apply readiness decision rules stage by stage; approved plans without implemented artifacts can be PARTIAL only
    apply dispatch decision rules and dependency issue mirror checks
if validation_only:
    print summary and exit 0
render markdown report:
    include provider_queue_snapshot source and observed counts
    include package family table by stage
    include dispatch board grouped by provider
    include blocked/partial/missing evidence section
write docs/reports/inventory-readiness-matrix-YYYY-MM-DD.md
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/knowledge/test_inventory_readiness.py` | TDD suite before implementation |
| Create | `scripts/knowledge/validate_inventory_readiness.py` | schema validation and markdown rendering |
| Create | `config/knowledge/inventory-readiness.yaml` | canonical machine-readable readiness matrix |
| Create | `docs/reports/inventory-readiness-matrix-2026-04-25.md` | derived dispatch board/report |
| Create | `docs/plans/2026-04-25-issue-2487-inventory-readiness-spine.md` | canonical issue plan |
| Update | `docs/plans/README.md` | keep exactly one #2487 row and point it at this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_valid_minimal_matrix_passes` | schema accepts complete minimal config | one evidence-backed package | exit 0 / valid result |
| `test_missing_required_top_level_key_fails` | required top-level fields enforced | omit `package_families` | nonzero with field name |
| `test_unknown_readiness_status_fails` | enum validation | `raw_data: DONE` | nonzero with enum message |
| `test_ready_without_stage_evidence_fails` | no unsupported `READY` claims | `llm_wiki: READY`, no `wiki_doc_keys` | nonzero, no YAML mutation |
| `test_missing_doc_key_for_wiki_ready_fails` | fail-fast wiki identity | wiki ready without doc key | nonzero with `doc_key`/`wiki_doc_keys` |
| `test_approved_plan_without_implemented_artifact_cannot_make_ready` | governance gate preserved | approved issue ref, no implemented artifact | nonzero if stage is `READY`; valid if `PARTIAL` |
| `test_typed_issue_ref_wrong_stage_cannot_satisfy_partial_claim` | issue evidence is stage-specific | issue ref produces `website_gtm`, row claims calculation handoff | nonzero or partial warning per fixture |
| `test_stale_requires_stale_evidence` | stale status has concrete cause | `STALE` with no stale artifact/source | nonzero |
| `test_missing_config_path_fails` | missing config behavior | nonexistent config path | nonzero with expected path |
| `test_invalid_provider_snapshot_null_contract_fails` | queue snapshot nullability enforced | source null but one count integer | nonzero |
| `test_missing_nested_required_field_names_path` | nested required fields named | omit `dispatch.rationale` | nonzero with field path |
| `test_blocked_requires_blocking_dependency` | blocked status has explicit cause | `BLOCKED` with no blocking dependency | nonzero |
| `test_dependency_role_enum_enforced` | only allowed dependency roles | role `maybe` | nonzero |
| `test_duplicate_package_ids_fail` | stable row identity | duplicate `id` | nonzero |
| `test_unknown_provider_fails` | dispatch provider enum enforced | `ready_for_provider: llama` | nonzero |
| `test_zero_package_families_fails` | no empty dispatch board | empty list | nonzero |
| `test_null_queue_counts_render_unknown` | unknown counts not treated as zero | counts null | report says `unknown` |
| `test_report_groups_dispatch_by_provider` | render dispatch board | Codex/Gemini/Claude rows | provider sections present |
| `test_current_provider_counts_are_observed_not_thresholds` | counts don't gate validation | counts 4/1/17 | valid if row evidence valid |
| `test_expected_output_artifact_may_be_null_for_unrun_recon` | Gemini expected artifact can be null | unrun scouting task | valid when rationale says expected output |
| `test_cli_validate_only_does_not_write_report` | validation mode safe | `--validate-only` | no report file written |

---

## Acceptance Criteria

- [ ] Tests are written before implementation in `tests/knowledge/test_inventory_readiness.py`.
- [ ] `uv run pytest tests/knowledge/test_inventory_readiness.py -v` passes.
- [ ] `uv run python scripts/knowledge/validate_inventory_readiness.py --config config/knowledge/inventory-readiness.yaml --validate-only` exits 0 on the canonical config.
- [ ] Invalid fixtures for unsupported `READY`, approved-plan-without-implemented-artifact `READY`, unknown enums, duplicate IDs, stale-without-evidence, invalid queue snapshot nullability, missing config path, missing nested fields, and empty package list fail nonzero.
- [ ] `uv run python scripts/knowledge/validate_inventory_readiness.py --config config/knowledge/inventory-readiness.yaml --output docs/reports/inventory-readiness-matrix-2026-04-25.md` writes a report with provider sections for Codex, Gemini, and Claude.
- [ ] The report clearly labels provider queue counts as observed values from `docs/reports/provider-work-queue.md`, not acceptance thresholds.
- [ ] The report includes downstream issue references for #2464, #2403, #2346, #2465, #2402, and #2392 without implying they were implemented in #2487.
- [ ] Downstream issues are referenced only as dependencies/candidates; they are not executed inside #2487.

---

## Adversarial Review Summary

| Provider lane | Verdict | Key findings |
|---|---|---|
| Claude/governance | APPROVE | Governance sequence preserved; downstream issues remain references/dependencies only. |
| Codex/schema-contract | APPROVE | Typed issue evidence, failure semantics, and tests resolve machine-checkable schema blockers. |
| Gemini/research-dispatch | APPROVE | Provider dispatch semantics are bounded; unrun recon outputs are expected artifacts, not claimed evidence. |

**Overall result:** PASS — ready for user approval gate.


---

## Risks and Open Questions

- **Risk:** YAML parser drift. Mitigation: implementation must use the repo's existing YAML dependency if available; otherwise it must reject unsupported YAML features and document the supported JSON-compatible subset in the validator help.
- **Risk:** Provider queue counts can go stale. Mitigation: store `generated_at` and `source`; report treats counts as observed snapshot only.
- **Risk:** Downstream issue labels may change. Mitigation: #2487 records issue refs and readiness evidence, but does not require downstream issue execution.
- **Open:** Exact initial package-family rows can be intentionally conservative; unsupported `READY` claims fail validation.

---

## Complexity: T2

T2 — small new validator/report generator plus canonical config and tests. It coordinates several downstream packages but does not implement those downstream workstreams.
