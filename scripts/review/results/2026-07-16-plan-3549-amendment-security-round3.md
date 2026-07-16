# #3549 Implementation Amendment Security Review — Round 3

## Verdict

**MAJOR**

**Reviewed commit:** `d28dc9b7e3957e4e2a18b83921108b710c17f945`

## Blocking findings

1. **[MAJOR] The overlay availability row is still not errno-bearing and therefore does not close round 2's required availability-side classification proof.** The revised matrix injects an already-classified `FallbackUnavailableError("overlay.file", "unavailable")` and merely says it represents a missing parent/file (`docs/plans/2026-07-16-issue-3549-amendment.md:61-67`). That proves command rendering of a domain exception, but it cannot prove that an actual missing parent/file `ENOENT` is translated into that exception rather than falling into the command's registry `OSError`/exit-3 boundary. Round 2 explicitly required one availability errno and one integrity/I/O errno. The current code demonstrates why that distinction matters: `_read_secure_overlay` performs several filesystem operations and translates their exceptions itself (`src/workspace_hub/workstations/connection.py:227-261`), while `_execute` still maps an escaping `OSError` from the combined registry/overlay resolution block to `registry_unavailable`/3 (`src/workspace_hub/workstations/connection_command.py:167-176`). The EIO row is errno-bearing; the availability row is not. **Blocking change:** require a command-level RED case that causes the overlay boundary itself to receive `OSError(errno.ENOENT, secret)` at a named parent/file operation, expects exactly `error: overlay.file: unavailable` (or the deliberately selected parent field) and exit 4, proves exit is not 3, proves the runner is never called, and proves the path/message/endpoint/identity canaries are absent. Retain the domain-exception row only as a separate rendering unit test if useful.

2. **[MAJOR] The launch matrix cannot prove its normative claim that exit 127 is selected by errno only.** The amendment says “127 only for `ENOENT`” and 126 for every other pre-child `OSError` (`docs/plans/2026-07-16-issue-3549-amendment.md:54-57`), but its rows pair `FileNotFoundError` only with `ENOENT` and `PermissionError` only with `EACCES` (`:47-50`). An implementation can continue dispatching on exception subclass, as the current `_launch` does (`src/workspace_hub/workstations/connection_command.py:123-130`), and pass all four proposed rows while violating the rule for explicitly constructed mismatches such as `FileNotFoundError(errno.EACCES, secret)` or `PermissionError(errno.ENOENT, secret)`. This is the exact negative control needed to distinguish the promised errno inspection from the known-bad subclass inspection; generic `OSError(ENOEXEC/E2BIG)` does not exercise it. **Blocking change:** add at least one crossed subclass/errno RED control (preferably both directions) with exact exit/stderr, secret non-disclosure, and exactly-one runner call. Alternatively narrow the normative rule to explicit exception-class dispatch, but that would not satisfy round 2's “127 only for ENOENT” correction.

## Additional finding

3. **[MINOR] The human-facing TDD sequence still promises a failing direct-executable test even though the canonical amendment correctly classifies it as already-green regression coverage.** The amendment says direct executable mode is already green and will not be a promised RED (`docs/plans/2026-07-16-issue-3549-amendment.md:74-79`), but the HTML tells the user to “Write failing review-driven tests” for direct executable mode (`docs/reports/2026-07-16-issue-3549-registry-connection-helpers-plan.html:238-246`). The tracked script already has a shebang and executable mode. Because the HTML is the default human-facing approval artifact, this contradiction can cause false TDD evidence at resume. Remove direct executable mode from the HTML's failing-test list and label it regression/characterization evidence there as the amendment does.

## Checks performed

- Verified the focused command includes both `tests/workstations/test_connection_cli.py` and `tests/workstations/test_connection_resolver.py` plus wrapper and endpoint-enforcement suites (`docs/plans/2026-07-16-issue-3549-amendment.md:163-165`).
- Verified the exact launch rows cover errno-bearing `ENOENT`, `EACCES`, `ENOEXEC`, and `E2BIG`; child `-SIGINT`; and unchanged child status, with exception-row redaction and exactly-one-call requirements. Finding 2 is the missing crossed negative control, not an omission of those ordinary rows.
- Verified the overlay matrix assigns exact exit/stderr values for availability (4), raw EIO (5), and digest mismatch (5), forbids endpoint/identity/secret/registry-class disclosure, and requires zero launches. Finding 1 is the absence of an actual availability errno at the overlay translation boundary.
- Verified `connection_command.py` and `test_connection_cli.py` are explicit candidate paths and are explicitly required in the governed manifest (`docs/plans/2026-07-16-issue-3549-amendment.md:107,121,145-148`); base acceptance also requires staged/commit coverage and TOCTOU controls (`docs/plans/2026-07-16-issue-3549-registry-connection-helpers.md:289-296`).
- Verified the amendment preserves hostname-first routing, fixed strict host-key checking, canonical `HostKeyAlias`, a single shell-free launch, and no retry; no new caller-supplied SSH-option surface is authorized.
- Verified the line-gate disposition is executable in principle: the current candidate files are at most 400 lines except `registry.yaml` at 405, and the amendment requires removing at least five non-semantic lines before acceptance. The base plan, amendment, and HTML are 387, 170, and 298 lines respectively.
- Verified the candidate path authority includes the user-created revision-bound marker and all three round-3 artifact paths. The marker must name this exact reviewed amendment commit and the final artifacts before implementation resumes (`docs/plans/2026-07-16-issue-3549-amendment.md:134-143,151-161`).

## Publication readiness

**NOT READY (external pre-push gate).** No remote branch contains `d28dc9b7e3957e4e2a18b83921108b710c17f945`, and this round-3 artifact is newly local. This publication state is separate from the content verdict above; after the content blockers are corrected and re-reviewed, the exact reviewed amendment revision plus final review artifacts must be pushed and cited before renewed approval is requested.

## Required disposition

Keep implementation paused. Add the actual overlay-ENOENT boundary test and the crossed subclass/errno launch negative control, correct the HTML TDD classification, then rerun round-3 review against the new exact revision. Do not request renewed approval or create the approval marker for this MAJOR revision.
