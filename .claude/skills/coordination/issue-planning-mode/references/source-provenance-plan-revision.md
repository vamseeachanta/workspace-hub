# Source-Provenance Plan Revision

Use this checklist when resuming a plan-review issue after a key external/source-provenance question has been resolved (for example a licensed workbook, private standard, off-repo source, or vendor document becomes available).

## Trigger

- A plan is already in or near `status:plan-review`, but a material source route/provenance decision changed.
- The source is licensed, private, or off-repo and must not be committed as raw evidence.
- Review findings were mostly about source ambiguity, citation/calc provenance, or leakage risk.

## Required sequence

1. Re-open the live issue and current plan artifact; verify live labels before editing.
2. Patch the existing canonical plan instead of creating a replacement plan unless the scope materially changed.
3. In the plan, make the source route explicit:
   - absolute off-repo source path if needed for local reproducibility
   - source class/license boundary
   - what may and may not be committed
   - whether extracted corpora/tables are forbidden, temporary, or durable artifacts
4. Add fail-closed acceptance criteria for citation/provenance sidecars when calculations depend on the source.
5. Add TDD cases that prove:
   - protected/raw source artifacts and reusable extracted corpora are not committed
   - citation sidecars resolve to the expected source IDs
   - placeholder/source-gate/sign/unit/oracle checks fail closed
6. If a prior review wave already exists, run a focused re-review against the patched source/provenance sections rather than a full restart when the rest of the plan is unchanged.
7. Record the re-review synthesis in `scripts/review/results/` and in the plan's adversarial review summary.
8. Post a concise issue comment with: changed plan artifact, review verdicts, residual blockers, and exact next gate.
9. Verify final state: issue open/closed state, `status:*` labels, local plan row/status, review artifacts, git commit/push if local artifacts changed.

## Boundaries

- Do not self-apply `status:plan-approved`; explicit user approval is still required.
- Do not treat a known off-repo source path as permission to commit licensed source files or reusable extracted coefficient databases.
- Do not over-broaden implementation scope while patching provenance; keep the revision narrowly tied to the resolved ambiguity.

## Output shape

Recommended closeout summary:

```text
Current state: <issue>, <labels>, approval blocked/approved
Evidence: <commit>, <issue comment>, <plan artifact>, <review artifact>
What changed: source route, license boundary, fail-closed tests
Gap/blocker: explicit user approval or named unresolved source decision
Next action: label transition or TDD implementation checkpoint
```
