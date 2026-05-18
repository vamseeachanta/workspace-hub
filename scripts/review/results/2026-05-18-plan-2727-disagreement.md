# Disagreement report — plan #2727 (2026-05-18)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNKNOWN |
| codex | MAJOR |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

- `docs/plans/README.md` §“Required Sections in Each Plan” requires “4. **Pseudocode** — 5-15 lines per function (T2/T3); ‘trivial’ note for T1.” The plan has no `## Pseudocode` section. This is a workflow-contract miss for a T3 plan.
- `docs/plans/README.md` Plan Index still lists `#2727` as `draft` and “not adversarial-reviewed,” while the plan header says `status:plan-review` and “revised after MAJOR review findings.” The plan/index traceability is stale before approval.
- The plan’s “Machine-readable inventory schema” says `tests/fixtures/architecture/data_source_inventory.yaml` is “the single tested source of truth,” but the TDD row `test_data_inventory_required_seed_sources` uses `data-source-inventory.md` as expected input. That permits seed-source coverage to pass against the human view while the YAML source of truth is incomplete or divergent.
- The plan’s “Machine-readable inventory schema” requires `runtime_probe.command`, `runtime_probe.machine`, `runtime_probe.timestamp`, `runtime_probe.status`, and `mounted_source_registry_ref`, but the TDD list has no test that explicitly validates those required YAML keys. `test_inventory_has_bucket_contract_columns` covers only allowed/forbidden/canonical/retention/publication/output fields.
- The plan’s “Client data handling model” says tracked docs and fixtures must not publish raw client-identifying paths, and the “Revision / Adversarial Review Summary” claims “Redaction not testable” was fixed with “explicit redaction TDD/AC.” The TDD list contains no explicit redaction test that scans `docs/architecture/*.md` and `tests/fixtures/architecture/*.yaml` for literal private/client roots or validates only `client_present_###` / `client_planned_###` IDs appear.
- The plan’s Files to Change row for `docs/architecture/data-boundary-violations-and-gaps.md` requires “actual `gh issue create` commands/body drafts,” and Acceptance Criteria repeats “exact `gh issue create` command/body drafts.” The TDD row `test_follow_up_issue_backlog_present` only requires “proposed follow-up GitHub issue titles/scopes” or “no-action rationale,” so the executable command/body requirement can disappear while tests pass.
- The plan’s repo-tier wording is not reconciled across cited sources. `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` defines Tier-1 core engineering repos as `digitalmodel`, `assetutilities`, `assethold`, `worldenergydata`; `docs/BUSINESS_BRAIN.md` defines Tier-1 as `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website` and puts `assethold` in Tier-3. The plan says “only explicitly documented repos may be called tier-1” but does not choose or reconcile the conflicting documented authorities.
- `docs/document-intelligence/data-intelligence-map.md` lists concrete document-intelligence data artifacts that are directly in this issue’s scope, including `data/document-index/index.jsonl`, `data/document-index/summaries/<sha>.json`, `data/doc-intelligence/requirements.jsonl`, `data/doc-intelligence/constants.jsonl`, and deep extraction artifacts. The plan’s Acceptance Criteria says the inventory includes derived indexes, but the initial source classes and tests do not explicitly require these existing document-intelligence artifacts or their source/residency rules.
- The plan’s “Machine-readable inventory schema” says unknown enum-like fields fail closed “unless the row is explicitly `status: unavailable`,” but the required key list only includes `runtime_probe.status`, not a row-level `status`. This makes the exception ambiguous and easy to implement incorrectly.
- `scripts/review/results/2026-05-17-plan-2727-disagreement.md` is cited as prior-cycle context, but its findings include stale references to old plan defects and prior line numbers. The plan says current-cycle artifacts “must be generated after this revision,” but it does not require revision/SHA binding for those artifacts; `scripts/review/plan-review-fanout.sh` writes date-based filenames that can overwrite same-day review outputs.

### gemini

- **Tier Classification Contradiction:** Plan § "Initial known data/source classes" classifies `worldenergydata` and `assethold` as "documented tier-1 engineering/data repos." However, the plan also cites `docs/BUSINESS_BRAIN.md` as the "existing knowledge-promotion authority; architecture docs must reference this instead of creating a competing promotion policy." `docs/BUSINESS_BRAIN.md` explicitly lists `worldenergydata` as a Tier-2 repo and `assethold` as a Tier-3 repo. The plan violates its own cited authority by misclassifying these repositories.
- **Schema Requirement Impossibility:** Plan § "Machine-readable inventory schema" states that `mounted_source_registry_ref` is a required YAML key per source row, and a "missing registry reference is invalid". However, the plan proposes inventorying sources like `digitalmodel` reference data, public `llm-wiki` content, and `[REDACTED-CLIENT-ROOT]` project data. These sources do not exist in `data/document-index/mounted-source-registry.yaml`, and the plan explicitly prohibits forking that registry (Plan § "Client data handling model"). This creates an impossible schema constraint for non-mounted sources.
- **Undefined Search Scope for Violations:** Plan § "Machine-readable inventory schema" requires boundary-violation searches to record `paths_scanned` and states "A `none_found` conclusion is invalid without these fields." However, the plan nowhere defines *which* specific paths, systems, or repositories must be scanned to satisfy the Acceptance Criterion: "Boundary violation/gap inventory identifies existing blurred-boundary artifacts or explicitly records none-found with search evidence." Without a defined minimum search scope, the acceptance criterion is meaningless and can be bypassed.
