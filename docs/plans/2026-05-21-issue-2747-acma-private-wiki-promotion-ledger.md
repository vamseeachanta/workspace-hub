# Issue #2747 Plan — feat(acma): raw-to-private-wiki promotion ledger with completion confidence scoring

## Metadata
- **Issue:** #2747
- **Layer:** Data → Result readiness
- **Status target:** `status:plan-review` after adversarial review; implementation requires explicit user approval and `status:plan-approved`.
- **Prepared:** 2026-05-21
- **Execution class:** parallel-worktree after approval

## Resource Intel
- GitHub issue #2747: `feat(acma): raw-to-private-wiki promotion ledger with completion confidence scoring`.
- Parent/dependency chain: #2747 depends on #2746 private wiki target and should consume #2389 `source_doc_key`; blocks #2748 unscored-output prevention.
- Workspace hard gates: issue → resource intel → plan → adversarial review → `status:plan-review` → USER APPROVES → `status:plan-approved` → TDD implementation → close.
- User update: private `llm-wiki` posture allows fuller ACMA/client data capture with key-information abstractions; public-safe constraints still apply to public repos/docs.

## Problem
ACMA private wiki promotion needs a computable ledger so raw data becomes auditable, scoreable knowledge rather than a pile of extracted text.

## Scope
### Owned paths
- `schemas/` or config paths for promotion ledger schema
- `scripts/` validation/report helpers for ledger entries
- ACMA/private-wiki docs/templates that define scoring categories

### Read-only paths
- `docs/standards/`
- `docs/plans/`
- Related issue comments and existing reports under `docs/reports/` and `scripts/review/results/`

### Forbidden paths / operations
- No destructive `/mnt/ace` move/delete/compression until an approved execution issue explicitly authorizes the exact action.
- No secrets, credentials, gateway tokens, or local `.env` writes.
- No `status:plan-approved` label application by an agent.

## Implementation Strategy After Approval
1. Re-read issue, plan, comments, and current branch state.
2. Create/use isolated worktree under `/mnt/local-analysis/agent-worktrees/`.
3. RED: add failing tests/fixtures/checks for the target behavior.
4. GREEN: implement the smallest repo-side contract change.
5. REFACTOR: tighten docs/schema/CLI behavior without widening scope.
6. Verify with targeted tests and relevant validators.
7. Post issue comment with commit SHA, tests, evidence, blockers, and closeout recommendation.

## TDD / Verification Plan
- Schema tests for valid/invalid ledger entries.
- Threshold tests for not-started / partial / usable-with-caveats / client-ready / needs-human-review.
- Report-readiness test proving unscored entries are excluded or flagged.

## Acceptance Criteria
- Every promoted item has raw source ID, extraction version, confidence/completion score, and revision state.
- Dashboard/report can show ready vs blocked knowledge.
- AI-model revision workflow preserves prior extraction versions.

## Adversarial Review Hardening
- Implementation is blocked on #2389 landing, unless the execution plan defines a temporary compatibility shim that is removed before close.
- Ledger readiness must distinguish confidence score from publication/client-readiness approval. Score is not approval.
- Schema/test scope must include `source_doc_key`, `source_class`, `input_residency`, allowed `output_residency`, sanitization/legal/reviewer gate state, extraction version, revision lineage, scoring actor/tool, schema version, and rationale bucket.
- Existing `templates/client-llm-wiki/ledgers/` contracts must be extended rather than contradicted; if `overall` remains operator judgment, deterministic threshold tests must target derived report classification instead of mutating operator fields.
- Fail-closed tests must reject entries missing source class, residency, provenance, score metadata, or review/gate state. Regression tests must prove downstream report/chatbot consumers cannot treat “scored” as sufficient when publication/residency clearance is absent.
- Before RED starts, execution preflight must verify live `status:plan-approved` and local `.planning/plan-approved/2747.md`.

## Rollback
- Revert the implementation commit(s) on the issue branch/main.
- Restore prior schema/config/docs from git history.
- For any approved future data operation, require a pre-op manifest and rollback/copy-back command before execution.

## Adversarial Review Targets
- Verify dependency order is enforceable and does not duplicate adjacent issues.
- Check that tests fail before implementation and prove the artifact contract.
- Check no data-destruction path is hidden in documentation-only wording.
- Check public/private boundary language is consistent with current private llm-wiki posture.
