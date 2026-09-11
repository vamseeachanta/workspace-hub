# Codex adversarial review: cutover readiness report

Date: 2026-09-10 local / 2026-09-11 UTC.

Reviewed artifact: `2026-09-10-orcaflex-cutover-readiness.html`, SHA-256 `5A6291A97BF17A483D31B0E6633C0CDEB471567CB7F2064AECBC1384C9015B53`, workspace-hub worktree HEAD `eac078cc5ebb8304fec6e0bb5aa9c377e44b521a`.

**Verdict: MINOR.** No material false queue-state claim or unsafe recovery instruction found. This is a readiness report, not deployment approval and not the implementation plan for [Deckhand 591](https://github.com/vamseeachanta/deckhand/issues/591). The explicit stop conditions and separate approvals are necessary and retained.

## Findings

- **MINOR — fixture contract should be explicit in the forthcoming preview.** `solver-smoke-test` alone does not select OrcaFlex or establish fail-closed workflow options. The exact fixture should explicitly select OrcaFlex, require success, and retain its report for result verification. Review that configuration before queue submission; do not rely on workflow defaults or infer OrcaFlex-only scope from this report's title. The report correctly leaves the fixture revision unresolved, so this is a preparation requirement rather than permission to broaden this change.
- **Evidence boundary:** numerical/native claims match the adjacent merged proof JSON (revision, DLL, threads, 81/81 finite samples, exit zero, 4.5 seconds). The 63-test count is orchestrator-reported; this review did not independently rerun tests or native acceptance.

## Evidence and safety checks

- Independently inspected the live queue read-only: rebase metadata from September 1, original branch `main`, detached HEAD, clean index, no conflicts, 655 local-only heartbeat commits, and cumulative changes confined to its heartbeat path. The local 12 requests all have matching terminal result records. These are snapshot facts; failed synchronization precludes remote-drain claims.
- Confirmed the existing upstream queue repair at `2027c64` is present in candidate `ea24989c...` but absent from live `3de8dba...`. Aborting automatically before preserving detached history would be unsafe. The report instead requires quiescence, preservation of both histories and rebase metadata, verification, and rechecking change scope before reconciliation.
- Confirmed the existing `software-ops` scope permits Deckhand and workspace-hub and declares contents-read/pull-requests-write token permissions. No neutral Windows mapping currently exists. The report keeps exact mapping, fixture, credentials and per-job authority subject to approval, and does not silently reuse the client mapping.
- Compared the cleanup-reproduction JSON with the stated candidate limitation: return code 124 with a false killed diagnostic, unreaped fake process, and removed lock. No native behavior claim is made from this fake reproduction.
- The report correctly separates interactive acceptance from credentialed-task/Linux-route acceptance, holds unsafe candidate deployment, prevents rollback into an unproven process-ownership state, and excludes batch onboarding from the proposed smoke increment.
- All four local artifact links resolve. No private queue/client path or credential value appears in the reviewed HTML.

No runtime, queue, task, code or policy changes were performed. Expected residue: this review artifact only, for orchestrator disposition.
