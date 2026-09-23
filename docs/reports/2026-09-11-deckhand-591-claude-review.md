# Deckhand issue591 — Claude plan review

Model: haiku; effort low; existing auth; empty setting sources; no session persistence; tools disabled; packet-only prompt.
Deadline120s. Exit: 0. Elapsed: 58.26s. Timed out: False.
Private temporary directory removed: True.
Raw stdout SHA256: df9b6115577ab37bb887059a8cccbec3401093fb21a28cd810aa5e82ca456568
Pinned source: ea24989c521dcab30ba5428cc5c8f791d273ed36; runtime, watchdog, agent _execute_with_lock and _write_runner_result.
Private context redacted if present; otherwise exact output.

## Reviewed file hashes

{
  "docs/reports/2026-09-10-deckhand-cleanup-reproduce.py": "486d511a5b10680a3f16fea2070a419f1731fade8865af80de8660b9f1103050",
  "docs/reports/2026-09-10-deckhand-cleanup-reproduction.json": "8eb64e48c5f9226c641d70439333d5260f4dc44471202729fceb92403ea980ec",
  "docs/plans/2026-09-11-deckhand-591-cleanup.html": "bdc768ce594f7a2428fa88e68635c2aa653a42e7c71c9b882a4097b5b56042d0"
}

## Actual stdout

# PLAN REVIEW: Deckhand #591 Licensed-Run Cleanup
**VERDICT: MAJOR** — Governance intent sound, Windows Job Object strategy correct, but six material gaps require concrete fixes before TDD begins. **Submit clarifications; do not authorize implementation yet.**

---

## Concrete Defects

### 1. **Job Object Inheritance/Breakaway Edge Case (Design Gap)**
Section 3 proposes "breakaway disabled" to contain descendants. Windows docs permit child processes with `CREATE_BREAKAWAY_OK` to escape the job *unless explicitly denied*. However:
- Plan does not verify that `CREATE_BREAKAWAY_OK` is actually restricted via `SetInformationJobObject` with `JOBOBJECT_SECURITY_NO_ADMIN` / similar.
- "No uncertain partial-spawn path releases guard" — but if a child spawns with `CREATE_BREAKAWAY_OK` before assignment check completes, does it escape? Plan says to verify "no process started" but doesn't enumerate win32 return codes that prove this.
- **Fix**: Specify exact `SetInformationJobObject` limits used; document Windows versions this applies to; add test case for CREATE_BREAKAWAY_OK denial.

### 2. **Injected Runner Cleanup Proof Lacks Structural Validation**
Section 3, point 6: "Missing proof will fail and retain ownership; affected tests will supply intentional fake proofs."
- A test could return `{"cleanup_state": "confirmed"}` without actually terminating descendants. Plan trusts the return value but never inspects what the runner actually *did*.
- `_execute_with_lock` will "validate the contract before release" — but where is the struct definition? Is it a pydantic model, a dict schema check, a runtime assertion?
- What stops a malicious injected runner from lying?
- **Fix**: Define a `CleanupAttestation` dataclass with fields (cleanup_state, containment_kind, process_handles_verified, observed_job_accounting); require `_execute_with_lock` to type-check this; document that only in-process adapters can attest (never queue input).

### 3. **Non-Windows Platform Detection Edge Case**
Section 3, point 7: "Non-Windows default licensed execution will return an explicit unsupported-containment failure before spawn and **safely release a not_started guard.**"
- What if `os.name` is misconfigured or spoofed? Does release happen *before* validating that no process was spawned?
- If a test mocks `os.name` to return a non-"nt" value partway through acquire+spawn, does the lock get freed even if a process started?
- **Fix**: Clearly state: platform check happens BEFORE lock acquire (not after spawn); add test: acquiring lock, spawning a child, then checking `os.name != "nt"` returns unsupported+retained (not released).

### 4. **Cleanup Budget Starves Observation Under Cascading Kills**
Section 3, point 4: "Cleanup will use one monotonic 30-second budget shared by termination, observation and output finalization, not 30 seconds per operation."
- If `TerminateJobObject` blocks for 25 seconds (cascading child shutdown), observation has 5 seconds left.
- If job accounting query also blocks (kernel scheduler preempted), observation timeout triggers → "unknown final observation will retain quarantine."
- But then the next agent retry will also fail, starving the queue forever.
- Plan says "OS process creation/scheduling and durable storage calls will be explicitly excluded from a hard real-time claim" — but then how do you prevent indefinite quarantine?
- **Fix**: Define sub-budgets (e.g., 15s termination, 10s observation, 5s output); or implement a separate cancellation token for observation-only paths; document worst-case queue blocking scenario and recovery procedure trigger point.

### 5. **Handle Race After close_handle: Observation Window Undefined**
Section 3, point 4: "Handles will close in nested finally blocks; unknown final observation will retain quarantine."
- Between close(job_handle) and the next `QueryInformationJobObject` call (if retried), the kernel may or may not have torn down job accounting structures.
- "Unknown final observation" — but is this a timeout, a failed API call, or both?
- **Fix**: Specify: if close succeeds but query fails with ERROR_INVALID_HANDLE, treat as confirmed-empty (job was valid, now closed, so descendants are gone). If query fails with other codes, retain guard. Add test: close handle, wait 100ms, query → expect ERROR_INVALID_HANDLE and confirmation.

### 6. **Test Gate Reversed: Windows Native Tests After RC Qualification**
Section "Validation": "Native Windows tests will be required before release-candidate qualification."
- RC qualification *nominally* happens after integration/acceptance testing.
- Does this mean tests are written in order: fake → acceptance → native?
- Or does "before RC" mean tests must pass before shipping the RC, i.e., tests come first?
- **Fix**: Use unambiguous phrasing: "Native Windows tests must PASS before code is merged to main (not after integration); Windows-only tests will be explicitly skipped on non-Windows CI, but must run on release-candidate builds."

### 7. **Clock Source Mismatch: Deadline vs. Budget**
Section 3, point 4: Configuration will "reject nonfinite values" — but rejects based on which clock?
- Are `max_wall_seconds` deadlines checked against `time.monotonic()` or `time.time()`?
- Is the 30s cleanup budget a monotonic timer or wall-clock?
- If a system clock skew happens (NTP adjustment), could a deadline be missed silently?
- **Fix**: Specify: all timeouts use `time.monotonic()` (immune to clock skew); deadline validation rejects non-finite using math.isfinite() (covers inf, -inf, nan, bool). Add test: system clock skew simulation → verify monotonic clock is unaffected.

### 8. **Result Serialization Bloat Under Cleanup Budget**
Section 3, point 5: "Returned diagnostic tails will be bounded, and raw paths will not be published."
- What is the tail bound? 1KB? 100KB?
- Does serializing the full runner result dict (with cleanup attestation, diagnostics, stdout/stderr) happen within the 30s budget or outside?
- If result serialization times out or fails, does the guard release?
- **Fix**: Define max diagnostic tail (e.g., 5KB), explicitly exclude serialization from 30s budget (it happens in finally after cleanup), and specify: if final result serialization fails, retain guard and log path to partial result.

---

## Minor Issues (Wording/Clarity)

- **Section 3, point 1**: "Existing, malformed, partial and legacy PID locks will remain busy" — does this apply to locks from crashed agents? Should orphaned locks have an owner-review recovery path documented here (cross-ref to #566)?
- **Section TDD**: "Affected tests will supply intentional fake proofs" — which tests, which proofs? Enumerate: timeout test, descendant test, recovery test.
- **Acceptance section**: "Deployment selection under #3831 will await integration" — but this plan is FOR #591, not #3831. Clarify: is this a dependency or a separate gate?

---

## What the Plan Gets Right

✓ Windows Job Object containment (breakaway + suspended child) is sound.
✓ Fail-before-spawn on non-Windows is explicit and safe.
✓ Watchdog helpers unchanged (avoids downstream breakage).
✓ Ownership token + versioned guard prevents stale unlock.
✓ Injected runners must attest cleanup (closes legacy bug).
✓ TDD sequence lands RED tests first.

---

## Recommendation

**DO NOT APPROVE.** Return with fixes to: (1) Job Object API specifics, (2) injected proof struct & validation, (3) platform detection timing, (4) cleanup budget sub-allocation, (5) handle-race recovery, (6) test gate phrasing, (7) clock sources, (8) result serialization boundaries. Fixes are clarifications, not scope expansion. Resubmit revised HTML with changes highlighted.


## Actual stderr
