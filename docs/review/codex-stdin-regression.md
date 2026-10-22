# Codex stdin regression handling

The submit wrapper detects the diagnostic reported for CLI 0.144.1 in issue
#3442 and returns `UNAVAILABLE` before spending the review deadline on a stalled
invocation. This is diagnostic handling, not evidence that a version always
fails. Compatibility without the diagnostic remains unverified.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| 1 | 2026-10-22 | Add bounded diagnostic handling and offline evidence because the reported stall could consume both review attempts. |

## Evidence and scope

The issue #3442 reproduction, dated 2026-07-10, reports
`submit-to-codex.sh --commit <sha> --prompt <prompt>` with CLI 0.144.1, followed
by `Reading additional input from stdin...` and timeout exit 124. Prompt size
and inherited input state were not recorded. This establishes one reported
failure; it establishes neither universal failure nor a size threshold.

Issue #2661, dated 2026-05-11, records successful basic probes with 0.130.0 and
requests representative-prompt validation. The existing
[version guard](../../scripts/review/lib/codex-version-guard.sh) records the
historical blocked band and verified-ceiling convention. The provider note also
records earlier periodic symptoms. These observations differ in context and do
not qualify later releases automatically.

| Evidence | Small prompt | Full implementation diff | Closed input | Held-open input |
| --- | --- | --- | --- | --- |
| Real CLI 0.144.1 | NOT_EVALUATED | One failure reported; size unknown | NOT_EVALUATED | NOT_EVALUATED |
| Injected executable, diagnostic emitted | Unavailable | Unavailable, synthetic diff | Unavailable | Unavailable |
| Injected executable, structured success | Success | Success, synthetic diff | Covered by input isolation | Success |

The offline tests vary content and input independently. They establish wrapper
behavior, not the upstream cause or real CLI compatibility. A live matrix must
record the exact version, prompt digest and byte count, input state, exit code,
diagnostic and elapsed time. Real CLI comparisons and independent provider review
remain pending because assistant invocation was outside the permitted checks.

## Method and contracts

- The canonical entry remains
  [submit-to-codex.sh](../../scripts/review/submit-to-codex.sh).
  It sends the prompt through argv and explicitly closes input.
- [codex-exec-watch.py](../../scripts/review/codex-exec-watch.py) supervises each
  attempt using Python's standard library and POSIX process groups. It discards
  stdout as the wrapper previously did and preserves stderr for classification.
- An exact diagnostic line, with optional ellipsis and carriage return, ends the
  attempt. Split writes, missing final newline and immediate exit are covered.
  Quoted mentions inside other lines are not diagnostics.
- The diagnostic returns exit 7, the existing unavailable contract in
  [cross-review.sh](../../scripts/review/cross-review.sh). The wrapper emits
  `CODEX_STDIN_REGRESSION` and `UNAVAILABLE`, skips the compact retry and does not
  render partial output as a review. Detection is independent of version.
- CLI 0.144.1 is recognized as a reported risk with `scope unverified`. Existing
  configured deny bands remain authoritative. No new failing version interval
  or prompt-size acceptance limit is inferred from one report.
- Other failures retain the existing compact retry, quota exit 3 and timeout
  exit 124. `CODEX_TIMEOUT_SECONDS` remains the caller's per-attempt deadline.
  Invalid, nonpositive or nonfinite deadlines are rejected.
- Supervisor design choices are a 0.1-second polling interval, a 1-second TERM
  grace and reads of at most 65,536 bytes. These are implementation resource
  bounds chosen here, not measured compatibility thresholds or sourced physical
  coefficients. Detection waits at most a polling interval under normal
  scheduling, then stops the process group; a process ignoring TERM receives
  KILL after the grace. Scheduler delays are not a real-time guarantee.
- Process cleanup also runs on interruption and after the leader exits, so a
  descendant cannot continue solely because its leader finished first.

## Worked example

Inputs: a synthetic commit identifier, the prompt `Find defects.`, a complete
synthetic diff with 2,000 added lines, and an inherited pipe whose writer remains
open. The injected executable prints the reported diagnostic and would otherwise
sleep for 30 seconds. The configured review deadline is 15 seconds; the outer
test deadline is 8 seconds. These are explicit test inputs, not service limits.

Method: invoke the actual submit wrapper with `--commit` and `--prompt`; provide
the synthetic diff through a strict Git test double; capture the executable's
argv, input bytes and call count. The supervisor closes input and recognizes the
diagnostic before either review deadline. Test doubles resolve no installed
assistant executable or service.

Expected answer, independently derived: closed input supplies zero bytes; one
diagnostic produces one attempt and exit 7; the captured prompt contains the
last diff line, `+value_1999 = 1999`. There is no second attempt and no review
verdict. For the control case, valid structured output without the diagnostic
produces one attempt, exit zero and the fixture's `APPROVE` verdict. An empty
first result followed by valid output produces two attempts. These expectations
come from the existing wrapper contracts and the stated inputs, not outputs of
the code under test.

Run the offline example and matrix from the repository root:

```bash
uv run --no-project --with pytest python -m pytest \
  tests/review/test_codex_stdin_regression.py -q -rA -p no:cacheprovider
```

## Limits and later checks

The monitor requires Python 3 and POSIX process-group support. Native Windows
execution is NOT_EVALUATED. The direct plan fanout has its own timeout path;
this change covers the structured submit path used by cross-review, not every
direct CLI caller. It detects the recorded stderr line, not silent stalls or a
diagnostic emitted only on stdout. Silent stalls retain the configured deadline.
No engineering equations or standards-derived constants apply to this harness.
Independent review and real-version small/full-diff comparisons remain required
before declaring the upstream regression resolved.
