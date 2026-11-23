# Codex adversarial plan review — digitalmodel 2093

Verdict: **REQUEST_CHANGES — 1 MAJOR**. Advisory plan review only; no implementation or native execution approval.

Reviewed revision 1 of `docs/plans/2026-09-11-digitalmodel-2093-mooring-buoy.html`, SHA256 `27a2c45e2660c151a52f5298db2a9df86851446f44fa12a522ec0ba2e830df6e`.

## C1 — MAJOR: inherited harness does not observe whole-job cleanup before the next process

**Plan locations:** resource-intelligence harness row; execution method items 3 and 5; operational acceptance's bounded-cleanup requirement.

The plan promises only one solver process at a time, stopping dependent work after uncertain cleanup, and a new independent reload process after observing cleanup. The referenced harness does contain the child before resume, but its existing cleanup is weaker than the proposed sequential-process guarantee.

Verified source: `docs/plans/evidence/issue-2082-native.ps1:111`, `cleanup_owned`. It requests direct-process termination if needed, closes the kill-on-close Job handle, then waits up to five seconds on **only the direct process handle**. It never queries job membership or active process count. A parent that has already exited therefore satisfies the observed wait regardless of whether descendant termination has been observed. The function cannot provide a whole-job-empty observation after disposing of its only queryable Job handle.

This is a source-established missing observation, not a claim that a live descendant escaped or that the prior fixed smoke failed. It matters here because the new workflow will launch independent solver/readback processes sequentially and claims a non-overlap guarantee.

**Required bounded plan correction:** explicitly include whole-job cleanup confirmation for the local audited-model mode. Retain a queryable handle until a bounded whole-job termination/drain observation completes; do not start reload or the optional original-model solve if that observation fails. A termination request or root exit alone will not count as confirmation. Keep kill-on-close as the failure/crash fallback and make the cleanup deadline and failure evidence explicit. This does not require Deckhand task/queue implementation.

Add RED fake-process/job tests for an already-exited root with a still-active descendant, delayed drain, query/termination failure, deadline exhaustion, and successful drain permitting exactly one next child. Reuse existing native containment tests where appropriate; do not infer whole-job observation from fixed-smoke success.

Microsoft provides job-wide termination and queryable job state through [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) and [QueryInformationJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-queryinformationjobobject). The existing direct-process wait is a different observation.

## Other checks and limits

- Read the actual plan and existing harness containment/cleanup code, smoke thread/reload checks, General builder default and inspected template/original inputs.
- Verified the plan accurately identifies one mooring line, five sections totaling 620 m, four line types and a mid-line clump; the multi-leg header will be corrected without changing model data.
- The proposed field-specific empty-script repair preserves unrelated nulls and explicit overrides; explicit unresolved script semantics remain a native gate. No new native failure was claimed from serialization inspection.
- Source-duration preservation, at most two full solves, independent reload, finite/nonempty/time-coverage checks, predeclared readback tolerances and immutable input evidence are explicit. Additional retries and convergence campaigns remain outside this approval.
- The original model is expressly a compatibility-checked comparison candidate, not a numerical oracle. Missing calibrated damping, allowables, physical criteria and guide/YAML damping differences remain disclosed. Operational success will not establish physical accuracy.
- No code edits, tests, native solves or commits were performed for this review. Only this review artifact was added. Existing worktrees and parent-owned artifacts remain preserved; no review scratch was created.

This is one provider's verdict, not cross-provider consensus. C1 requires an explicit plan disposition before advisory approval.
