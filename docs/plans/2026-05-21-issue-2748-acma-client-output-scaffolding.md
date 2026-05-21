# Issue #2748 Plan — feat(acma): client output scaffolding for reports chatbots and evidence packs

## Metadata
- **Issue:** #2748
- **Layer:** Result/output layer
- **Status target:** `status:plan-review` after adversarial review; implementation requires explicit user approval and `status:plan-approved`.
- **Prepared:** 2026-05-21
- **Execution class:** parallel-worktree after approval

## Resource Intel
- GitHub issue #2748: `feat(acma): client output scaffolding for reports chatbots and evidence packs`.
- Parent/dependency chain: #2748 depends on #2746 private wiki target, #2747 promotion ledger, and #2389 provenance contract.
- Workspace hard gates: issue → resource intel → plan → adversarial review → `status:plan-review` → USER APPROVES → `status:plan-approved` → TDD implementation → close.
- User update: private `llm-wiki` posture allows fuller ACMA/client data capture with key-information abstractions; public-safe constraints still apply to public repos/docs.

## Problem
The client-facing layer must not consume private knowledge silently; every result needs evidence, confidence, and storage/publication rules.

## Scope
### Owned paths
- Client output scaffold templates/config
- Evidence manifest schema/checkers
- Report/chatbot artifact docs and validation helpers

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
- Tests proving reports/chatbots reject unscored private wiki entries.
- Fixture tests for raw output vs curated HTML vs PDF vs chatbot answer-pack retention classes.
- Citation sidecar tests separating source classes.

## Acceptance Criteria
- Output roots and retention/publication rules are distinct.
- Evidence manifests include source IDs, source class, confidence score, and execution metadata.
- HTML is canonical where possible; PDF is a derived deliverable.

## Adversarial Review Hardening
- Implementation is blocked on #2746, #2747, and #2389 being approved/landed enough to define private wiki target, readiness contract, and provenance contract.
- Extend existing report-layer contracts (`docs/architecture/report-evidence-bundle.schema.yaml`, `tests/architecture/test_report_layer_contract.py`, and `templates/client-llm-wiki/reports/`) instead of creating parallel ACMA-only contract drift.
- Add deny-by-default export-control contract: outputs are blocked unless every source class is allowed for that audience/channel/residency. Evidence manifests alone are insufficient.
- Required manifest fields: corpus scope, audience classification, `output_residency`, source class mix, freshness, review/sanitization gate status, `source_doc_key`, readiness/confidence, execution metadata, artifact type, and derivation chain.
- RED tests must reject unscored entries, scored-but-not-review-cleared entries, missing provenance/source class/residency, private-only/internal-note sources in client/public outputs, mixed public/private corpora with public output residency, and chatbot packs whose output residency is broader than corpus posture.
- Explicitly prohibit committing private retrieval indexes, raw answer traces, literal private/client paths, or sensitive source filenames into repo-tracked artifacts.
- HTML/PDF/chatbot packs are A-REPORT outputs; promotion back into wiki is a separate gate.
- Before RED starts, execution preflight must verify live `status:plan-approved` and local `.planning/plan-approved/2748.md`.

## Rollback
- Revert the implementation commit(s) on the issue branch/main.
- Restore prior schema/config/docs from git history.
- For any approved future data operation, require a pre-op manifest and rollback/copy-back command before execution.

## Adversarial Review Targets
- Verify dependency order is enforceable and does not duplicate adjacent issues.
- Check that tests fail before implementation and prove the artifact contract.
- Check no data-destruction path is hidden in documentation-only wording.
- Check public/private boundary language is consistent with current private llm-wiki posture.
