# Owner-default approval follow-through pattern

Use when the user says they approve recommended defaults for a GTM / Business Brain work packet and asks to continue.

## Proven sequence

1. Treat the approval as permission to execute the previously surfaced defaults, not as a request to re-ask.
2. Revalidate live issue labels and local artifacts before mutation.
3. Apply the defaults in repo artifacts:
   - update the primary plan;
   - update the human-facing scaffold/report;
   - update lane summaries and plan index rows so counts/statuses agree;
   - preserve public/private boundaries and no-outreach-without-explicit-send-approval.
4. If a default implies backlog creation, create GitHub follow-up issues immediately and link them back into the plan/scaffold/summary.
5. Reconcile workflow labels explicitly:
   - move cleared downstream artifacts to `status:plan-review` only when live review evidence exists;
   - keep still-blocked upstream artifacts on `status:blocked` / draft-blocked until evidence-fill or waiver + re-review clears MAJOR findings.
6. Verify with deterministic checks before commit:
   - counts in body vs summary/index;
   - newly added target names / issue links present;
   - legal sanity scan for public-facing GTM artifacts;
   - target-file diff clean after commit.
7. Commit/push intended files only, then post concise comments to the affected child issue(s) and parent command-center issue.

## Example from vessel-contractor GTM wave

Owner approved defaults after #2554/#2555 review. The correct action was:
- add enough fully populated countable targets to fix the matrix count blocker;
- keep partner-shape firms non-counted;
- keep wind-only rows deferred pending FOWT proof;
- create follow-up issues for evidence-fill / FOWT / GoM expansion;
- move #2555 to `status:plan-review` because live Claude/Codex/Gemini reviews were MINOR;
- keep #2554 blocked because evidence-fill and re-review still gated downstream #2556.

## Pitfalls

- Do not move a parent/upstream issue to `status:plan-review` merely because count/default blockers were partially fixed; evidence-fill MAJORs remain blocking until closed/waived and re-reviewed.
- Do not let a partial patch corrupt plan-index prose. After patching long Markdown table rows, re-read the affected rows and run string/count checks.
- Do not claim send-readiness when only corporate-root evidence exists; distinguish corporate-root, deep-link, and pain-point evidence.
- Do not treat label changes as sufficient state reconciliation; repo plans, plan index, GitHub labels, and issue comments should tell the same story.
