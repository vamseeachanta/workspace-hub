# Codex adversarial review — Deckhand 591 plan revision 1

Verdict: **MAJOR — revise before implementation.** Advisory plan review only; no owner or deployment approval.

Reviewed [plan](../plans/2026-09-11-deckhand-591-cleanup.html), SHA256 `bdc768ce594f7a2428fa88e68635c2aa653a42e7c71c9b882a4097b5b56042d0`, against pinned Deckhand `ea24989c521dcab30ba5428cc5c8f791d273ed36`.

## Findings

### MAJOR C1 — serialized cleanup contract relies on a nonexistent payload

**Section:** Proposed lifecycle, item 6, “Result semantics.”

The plan says cleanup evidence will use the “existing nested runner payload.” That payload does not exist in the pinned source. `licensed_run_agent.py:_result_payload` builds top-level schema/run/state/timestamp/returncode/summary/audit/artifact_refs fields; `_summary_payload` at lines 617–634 selects stdout/stderr tails and request/result metadata, discarding other runner dictionary fields. `licensed_run_queue.py:validate_result` requires a summary dictionary but supplies no cleanup contract.

An implementation that only adds proof to the returned runner dictionary will silently lose that evidence when the queue result is written. This defeats the specified durable cleanup outcome and makes the contract tests' notion of “valid proof” underspecified.

**Required revision:** choose an additive location, for example `summary.cleanup`, define its version, allowed states, required evidence fields and invalid combinations, and identify the serializer/consumer checks. Include a round-trip test through actual result writing and `read_result`, demonstrating both confirmed and quarantined outcomes survive serialization; malformed/missing proof must produce failure before result-file return and guard release. Preserve schema-1 compatibility without claiming an already-existing nested payload.

### MINOR C2 — distinguish failed workload from retained quarantine

**Section:** Proposed lifecycle, items 2, 4 and 6.

Item 4 permits killing unexpected descendants and establishing an empty job; item 2 permits release after confirmed cleanup. Item 6 groups uncertainty and unexpected descendants together as failures that “identify quarantine.” A parent exiting zero with descendants that are subsequently proven dead should fail workload acceptance, but need not retain the guard under the stated release rule.

**Required clarification:** freeze this outcome separately: unexpected descendants plus confirmed cleanup => nonzero workload result, confirmed cleanup, safe release; unknown cleanup => nonzero result, retained guard/quarantine. Test both.

### MINOR C3 — crash/kill-on-close test must not defeat its own mechanism

**Section:** Native qualification and Windows construction.

Supervisor interruption coverage needs an explicit observer arrangement. Holding an extra Job Object handle in the test observer prevents the last-handle-close condition whose crash behavior is being tested. Conversely, after the last handle closes, the observer cannot rely on querying that same job as its post-crash oracle.

**Required clarification:** observe job membership before interruption, retain independent handles to the known generic child/descendant processes, leave no observer-owned job handle alive across the supervisor crash, then require those process handles to become signaled under the outer deadline. Keep the separate normal/timeout tests for explicit zero-active-process accounting. This is a native test design constraint, not a request for deployment.

## Verified scope and limits

- Windows-first containment and non-Windows default fail-before-spawn are explicit intentional compatibility changes. Linux producer use is distinct from executing the default runner. No POSIX whole-tree equivalence is claimed.
- The injected runner call signature is preserved but its result contract intentionally changes. Existing test doubles must become explicit trusted adapters; queued data must not supply proof authority.
- Existing `_kill_process_tree` and `process_group_kwargs` are consumed by `licensed_run_watchdog.py`, which still kills then respawns without proof. The plan explicitly leaves those helpers unchanged and does not certify watchdog cleanup; this review does not treat broader watchdog repair as a prerequisite to this bounded code change.
- Retained guards survive agent restarts only while their protected path remains intact. The plan declares cooperating writers and excludes manual deletion/malicious replacement; legacy/PID-only locks stay busy, so it does not claim automatic crash recovery.
- Failed spawn, partial suspended creation, observation failure, normal-exit descendants, nonfinite deadlines and bounded cleanup are covered as proposed tests. Their implementation and native behavior remain unverified.

## Checks performed

Read the full revision-1 plan. Read pinned runtime, agent result serialization, queue validation and watchdog call sites via `git show`/`git grep`. Compared them with the prior fake-only cleanup reproduction. No solver, process-termination experiment, deployment change or implementation test was executed during this review. Microsoft documents kill-on-close in terms of the last job handle: [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects).

Only this review artifact was written. No commits or external comments were made.
