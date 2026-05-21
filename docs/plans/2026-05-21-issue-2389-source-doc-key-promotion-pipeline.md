# Issue #2389 Plan — feat(doc-intel): thread source_doc_key through promotion pipeline and promoted artifacts

## Metadata
- **Issue:** #2389
- **Layer:** Data → Result provenance
- **Status target:** `status:plan-review` after adversarial review; implementation requires explicit user approval and `status:plan-approved`.
- **Prepared:** 2026-05-21
- **Execution class:** parallel-worktree after approval

## Resource Intel
- GitHub issue #2389: `feat(doc-intel): thread source_doc_key through promotion pipeline and promoted artifacts`.
- Parent/dependency chain: #2389 feeds #2747 and #2748; it is the generic source-traceability primitive for promoted artifacts.
- Workspace hard gates: issue → resource intel → plan → adversarial review → `status:plan-review` → USER APPROVES → `status:plan-approved` → TDD implementation → close.
- User update: private `llm-wiki` posture allows fuller ACMA/client data capture with key-information abstractions; public-safe constraints still apply to public repos/docs.

## Problem
The current promotion chain can stamp output integrity but cannot reliably answer which L1 source produced a promoted knowledge artifact.

## Scope
### Owned paths
- Promotion/orchestrator modules that emit promoted artifacts
- Tests/fixtures for promoted-artifact headers or sidecars
- Documentation for the `source_doc_key` contract

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
- Unit tests proving promoted outputs include both `content-hash` and `source_doc_key`.
- Fixture test proving missing source identity fails closed or emits a structured error.
- Regression test proving existing `content-hash` behavior is preserved.

## Acceptance Criteria
- Promoted artifacts carry output integrity and source traceability independently.
- Missing/ambiguous source document identity cannot silently produce promoted output.
- Docs define canonical `source_doc_key` derivation and propagation.

## Adversarial Review Hardening
- `source_doc_key` must be an opaque/canonical source identity derived from the redacted source registry, not a literal filesystem path, client/project slug, filename, or promoted-artifact-local `doc_key`.
- RED tests must include concrete promoter surfaces under `tests/data/doc_intelligence/`: header/sidecar includes both `# content-hash:` and `# source_doc_key:`, missing/ambiguous source identity raises a structured error, and `content-hash` semantics remain unchanged.
- Add a self-loop guard: fail if `source_doc_key` resolves to the promoted artifact identity instead of the L1/L2 source backlink.
- Add leakage regression tests proving generated public/repo-tracked artifacts do not expose `/mnt/ace`, private repo names, raw client filenames, or literal source paths.
- Before RED starts, execution preflight must verify live `status:plan-approved` and local `.planning/plan-approved/2389.md`; if marker drift exists, stop for governance reconciliation.

## Rollback
- Revert the implementation commit(s) on the issue branch/main.
- Restore prior schema/config/docs from git history.
- For any approved future data operation, require a pre-op manifest and rollback/copy-back command before execution.

## Adversarial Review Targets
- Verify dependency order is enforceable and does not duplicate adjacent issues.
- Check that tests fail before implementation and prove the artifact contract.
- Check no data-destruction path is hidden in documentation-only wording.
- Check public/private boundary language is consistent with current private llm-wiki posture.
