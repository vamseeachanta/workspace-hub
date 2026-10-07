# Deckhand 591 plan review disposition

Date: 2026-09-11 UTC. Scope: advisory plan review, not implementation or deployment approval.

- [Claude r1](../../../docs/reports/2026-09-11-deckhand-591-claude-review.md): actual MAJOR against revision 1.
- [Codex r1](../../../docs/reports/2026-09-11-deckhand-591-codex-review.md): actual MAJOR against revision 1.
- [Codex r2](../../../docs/reports/2026-09-11-deckhand-591-codex-r2.md): advisory APPROVE against revision 2.
- [Final plan](../../../docs/plans/2026-09-11-deckhand-591-cleanup.html): revision 3; main-session inline disposition below. No provider consensus or revision-3 provider approval is claimed.

## Verified dispositions

1. Codex C1 confirmed locally: `_summary_payload` selects known fields and drops arbitrary runner fields. Revision 2 defines additive `summary.cleanup`, version/state/containment/evidence validation, agent-authored `guard_state`, and actual queue write/read round-trip tests. No existing nested runner payload is assumed. C2 separates failed workload with confirmed cleanup/release from unknown cleanup/quarantine. C3 defines a crash observer retaining process handles but no job handle. Codex r2 verified closure.
2. Claude 1: the suggested `CREATE_BREAKAWAY_OK` and security restriction are not the relevant API contract. Microsoft documents JOB_OBJECT_LIMIT_BREAKAWAY_OK / SILENT_BREAKAWAY_OK and CREATE_BREAKAWAY_FROM_JOB. Revision 3 names the actual limits, supported Windows baseline and denial test. Suspended creation prevents pre-assignment child code from running. Broker/service launching is explicitly excluded from trusted approved workloads.
3. Claude 2: revision 2 defines structural validation and explicitly trusted in-process adapters. A dataclass cannot prove an intentionally malicious adapter truthful; queued input cannot supply attestation authority. The plan does not claim an arbitrary-code sandbox.
4. Claude 3: platform spoofing by trusted in-process code is outside the declared trust boundary. Revision 3 nevertheless freezes backend selection before spawn and forbids post-spawn reclassification as not_started. Lock acquisition can safely precede a no-spawn backend refusal.
5. Claude 4: indefinite quarantine on unknown cleanup is the intended safety behavior, with explicit owner recovery; arbitrary sub-budgets would not prove termination. Revision 3 makes the liveness tradeoff explicit. It retains the total monotonic budget and outer native watchdog.
6. Claude 5: REJECT unsafe recommendation. ERROR_INVALID_HANDLE after close does not prove process absence. Revision 3 requires observation while the job handle is valid and treats invalid handle as unknown. The plan will never convert API query failure into cleanup success.
7. Claude 6: original text already required native tests before candidate qualification; revision 3 tightens sequencing to native PASS before merge and integrated-revision acceptance afterward.
8. Claude 7: cleanup was already monotonic; revision 3 explicitly uses monotonic elapsed time for execution too, math.isfinite for duration and separate boolean rejection.
9. Claude 8: revision 3 caps each diagnostic tail at 4096 characters and separates result serialization from cleanup. Serialization failure after confirmed absence/release remains an error, not a durable success; recreating a released guard would introduce an ownership race. Unknown cleanup retains the original guard even if result writing fails. Both failures get tests.

Main disposition: no unresolved material plan finding after these inline changes. Revision 3 requires owner approval, including intentional unsupported-platform/injected-runner compatibility changes. Code and native proof remain unimplemented; code review will be a separate gate. This is not unanimous provider approval.

## Queue preview review

Main compared the separate queue recovery preview with the preceding sanitized state report. The preview requires all-writer quiescence, complete repository/common-dir snapshot, verified manifests, refs/bundle and restore trial before abort/reconciliation; per-commit paths supplement net-tree comparison. Missing private inputs explicitly prevent operational approval readiness. No commands were executed against the queue. Runtime issue 591 approval will not approve that recovery.

## Evidence sources

- Pinned source `ea24989c521dcab30ba5428cc5c8f791d273ed36`, verified current remote main with `git ls-remote` this turn.
- Main reran the pinned fake-only reproduction: rc124, unreaped fake child, removed lock; no solver/cleanup subprocesses.
- Microsoft: https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects and https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-queryinformationjobobject (consulted 2026-09-11).
- Watchdog's related kill-then-respawn risk is promoted to [592](https://github.com/vamseeachanta/deckhand/issues/592), not buried in this review.
