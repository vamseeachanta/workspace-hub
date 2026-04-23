# Claude Terminal-1 Self-Review — Issue #2460 (post-r6 tightening pass)

Date: 2026-04-23 (terminal-1 overnight delivery; self-review of edits applied 2026-04-22)
Issue: #2460
Plan: `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md`
Reviewer: Claude Code (terminal-1 overnight session)
Review type: **Single-author self-verification pass, not a cross-provider adversarial review.** I edited the plan; this artifact is my honest reassessment of my own edits against the r6 wave findings. A fresh external Codex + Gemini rerun is still required before any `status:plan-review` transition or GitHub posting.
Verdict: MINOR

## Scope of this review

The r6 wave (outputs at `.planning/quick/review-2460-r6-*.out`) returned: Gemini APPROVE, Claude MINOR (5 findings), Codex MAJOR×2 + MINOR×1. This review verifies whether the post-r6 edits in this terminal-1 pass actually close those findings or whether residuals remain.

## Finding-by-finding disposition

### Codex r6 [MAJOR] — Retrieval-contract class union not satisfied
**Status: RESOLVED**

- Plan's Resource Intelligence Summary → Documents consulted now includes:
  - `#2209 durable-vs-transient knowledge boundary` — documentation-class required source, with a specific finding ("The tier-1 indexing contract is a durable normative document per the llm-wiki operating model §2 worked examples").
  - `.claude/rules/coding-style.md` and `.claude/rules/patterns.md` — harness-class required sources, with specific findings tied to enforcement-gradient levels and path-handling rules.
  - `config/agents/*` (ai-agents-registry.json, behavior-contract.yaml, routing-config.yaml, provider-capabilities.yaml, model-registry.yaml, drift-policy.yaml) — harness-class required sources, with a specific finding ("no agent-routing or provider config references the tier-1 indexing contract").
- The inline evidence-count comment now explicitly enumerates which class bundles are satisfied and confirms the `cat:documentation + cat:harness` union is covered.
- Source count updated from 8 → 12.

### Codex r6 [MAJOR] — STRICT_FILES coverage not codified
**Status: PRE-RESOLVED (verified still in place)**

- Files to Change already lists `Modify | tests/docs/test_banned_stale_references.py`.
- TDD Test List already contains `test_new_contract_docs_are_under_curated_stale_reference_guard`.
- Pseudocode `implement_with_tdd()` already extends this test before editing docs.
- Acceptance Criteria already includes "`tests/docs/test_banned_stale_references.py` is updated so the new contract/checklist docs are under the curated-doc stale-reference guard."

This MAJOR was closed before r6 but the r6 Codex run was apparently evaluating an older snapshot. Confirmed still resolved in current plan text.

### Codex r6 [MINOR] — DATA_PLACEMENT thresholds not referenced
**Status: PRE-RESOLVED (verified still in place)**

- TDD row `test_tier1_contract_requires_repo_vs_bulk_artifact_store_rule` references `≥ 10 MB` / `≥ 1000 files` thresholds from `docs/standards/DATA_PLACEMENT.md`.
- Acceptance Criteria row for this rule also references the thresholds.
- Deliverable text still frames bulk-artifact-store generically; this is acceptable because the test/acceptance rows carry the exact numeric thresholds.

### Claude r6 [MINOR 1] — Pipe-rendering hazard in table cells
**Status: RESOLVED**

- The pipe-delimited inline code span `` `present | partial | missing | not-applicable` `` in TDD and Acceptance status-values cells has been replaced with comma-separated individual inline-code tokens: `present`, `partial`, `missing`, `not-applicable`.
- Both locations updated: the TDD row for `test_tier1_checklist_records_surface_status_per_repo` and the Acceptance Criterion for the same rule.
- GFM table-cell rendering is no longer ambiguous.

### Claude r6 [MINOR 2] — BUSINESS_BRAIN scope coupling is narrative-only
**Status: RESOLVED**

- Added new TDD row `test_tier1_checklist_repo_set_matches_business_brain_tier1_section` that explicitly requires parsing `docs/BUSINESS_BRAIN.md` at test runtime and asserting set equality.
- Pseudocode `validate_contract_docs()` now asserts "the checklist's repo set is computed against a live parse of `docs/BUSINESS_BRAIN.md` tier-1 section, not just a hardcoded literal list (drift-detection)."
- Acceptance Criteria adds a bullet requiring this drift-detection test to exist.

### Claude r6 [MINOR 3] — "Multiple" unquantified
**Status: RESOLVED**

- Pseudocode `define_tier1_indexing_and_code_placement_contract()` legacy-retirement block now requires "AT LEAST 3 DISTINCT CATEGORIES" with three named minimums: (a) literal legacy filenames, (b) legacy path fragments, (c) legacy reference blocks used as active navigation authority.
- TDD row `test_tier1_contract_defines_legacy_retirement_rule` updated with the same quantification.
- Acceptance Criteria updated with the same quantification.
- Pseudocode `validate_contract_docs()` assert clause updated.

### Claude r6 [MINOR 4] — Artifact Map bleeds scope
**Status: RESOLVED**

- Removed the row `| Optional script/docs drift follow-up only (not in this issue) | scripts/ / child issue #2465 |` from Artifact Map.
- Added a dedicated "Not in scope (delegated to child issues)" block under Risks and Open Questions, explicitly listing scripts-work → #2465, per-repo remediation → #2461-#2464, and freshness automation → #2465.

### Claude r6 [MINOR 5] — Child-issue placement under-specified
**Status: RESOLVED**

- TDD row `test_tier1_contract_links_child_issues` rewritten to require each child issue number co-located with its scope clause: #2461 with "assetutilities", #2462 with "digitalmodel", #2463 with "aceengineer-website", #2464 with "workspace-hub", #2465 in the daily-freshness section.
- Pseudocode `validate_contract_docs()` assertion updated with the same co-location requirement.

### New: #2390 Work Stream G dependency testability
**Status: ADDED**

- New TDD row `test_tier1_contract_names_llm_wiki_roadmap_dependency` requires the contract doc to name #2390 as the upstream umbrella.
- New Acceptance Criterion matches.
- Risks section now has a "Dependencies" block naming #2390 Work Stream G as upstream and #2461-#2465 as downstream-gated.

## Residual minor findings (still worth external review)

- [MINOR] The `test_tier1_contract_links_child_issues` co-location assertion is vague about distance — "within the same section" vs "within N lines of the scope clause" is not specified. Recommend tightening during the external rerun: either "within the same markdown section" or "within 10 lines of the scope clause."
- [MINOR] The new BUSINESS_BRAIN drift-detection test parses a markdown document. Parsing rules (heading identity, table format, etc.) are not specified in the plan. The test implementation will need to encode these; flagging so the implementer doesn't invent an arbitrary parser.
- [MINOR] The Adversarial Review Summary now runs long (r3 + r6 + post-r6 patches). Once fresh external review lands and this draft is superseded, consider collapsing the r3 block into a single one-liner.
- [MINOR] The "broader `docs/standards/CONTROL_PLANE_CONTRACT.md` still contains historical legacy-path discussion" risk is still unresolved in the plan; it's an honest risk flag but might warrant a pointer to a follow-up issue.

## Checks performed

- Verified all r6 findings were either closed in this pass or pre-resolved (and the pre-resolved ones still appear in current plan text).
- Verified `#2209` plan exists at `docs/plans/2026-04-16-issue-2209-durable-vs-transient-knowledge-boundary.md`.
- Verified `.claude/rules/` contains `coding-style.md`, `patterns.md`, `README.md`.
- Verified `config/agents/` contains `ai-agents-registry.json`, `behavior-contract.yaml`, `routing-config.yaml`, etc.
- Verified `tests/docs/test_banned_stale_references.py:7` defines `STRICT_FILES`.
- Verified `#2390` live issue body contains Work Stream G with the recommended sequence naming `#2460` as the contract.
- Did NOT run `uv run pytest` (no tests exist yet per plan design; the contract doc and test file are the deliverables, not this review's environment).
- Did NOT dispatch Codex or Gemini — planning-only overnight session; cross-provider rerun remains the morning operator's responsibility.

## Recommended next step

Dispatch fresh Codex + Gemini review via `scripts/review/cross-review.sh` targeting the post-r6-tightened plan. If both return APPROVE or MINOR, the plan is ready for `status:plan-review` label and GitHub posting. Do NOT self-approve or add `status:plan-approved`.
