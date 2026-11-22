# Plan review transport and authentication diagnostics

The review wrapper sends the complete Codex prompt through a finite private file
on stdin. Plan content does not contribute to the process argument length.
Authentication probes distinguish a confirmed login requirement from an unknown
state. An unavailable provider contributes no review signal.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Describe finite stdin delivery and bounded authentication diagnostics to address large arguments and ambiguous failures. |

## Invocation contract

Run `bash scripts/review/plan-review-fanout.sh <plan-file> --output-dir=<results>`.
The plan filename must retain the existing date and issue-number convention.
Use `--providers=codex`, `--providers=claude`, or the existing provider list to
select reviews. The `gemini` token continues to select the existing `agy`
adapter; it does not select a separate Gemini CLI.

Codex receives `exec -`, with the shared prompt, framing and original plan bytes
on stdin. The private file reaches EOF without depending on an inherited pipe.
`CLAUDECODE` is removed for Codex probes and execution. The existing version
regression guard remains in force; its documented version range is not widened.

Claude retains its prompt and plan path references. Its authentication probe
uses `claude auth status` JSON. Only a boolean `loggedIn` combined with the
expected exit status establishes authenticated or logged-out state. Codex uses
`codex login status`; its diagnostic text is inspected privately and never copied
into the artifact. Neither probe initiates login or reads credential files.

The `agy` adapter has no documented authentication-status command in the existing
repository contract. Its authentication preflight is `NOT_EVALUATED`; the
existing bounded headless invocation remains available. Recognized login failures
become `AUTH_REQUIRED`, and unknown failures remain `RUNTIME_FAILURE`.
Credential-file presence and environment-variable presence are not proof of auth.

Each version and auth probe is bounded by
`PLAN_REVIEW_PREFLIGHT_TIMEOUT_SEC`, which defaults to the existing
`PLAN_REVIEW_PROVIDER_TIMEOUT_SEC`. Review execution retains its existing timeout.
These bounds apply separately, so total elapsed time can include multiple probes.
The exact recognized version line, delivery mode, auth state and diagnostic
category are appended under `## Invocation` in every provider artifact.
Unrecognized or failed version output becomes `VERSION_CHECK_FAILED`, with
`CLI version: NOT_REPORTED`; arbitrary diagnostic text is not published.

## Failure semantics and temporary data

| Observation | Diagnostic | Review verdict |
| --- | --- | --- |
| Confirmed logged-out auth response | `AUTH_REQUIRED` with login command | `UNAVAILABLE` |
| Auth probe timeout, malformed output or runtime error | `AUTH_CHECK_FAILED` | `UNAVAILABLE` |
| Known incompatible Codex version | `INCOMPATIBLE` | `UNAVAILABLE` |
| Review timeout, including partial output | `TIMEOUT` | `UNAVAILABLE` |
| Other unsuccessful review invocation | `RUNTIME_FAILURE` | `UNAVAILABLE` |
| Empty or malformed successful review | `INVALID_OUTPUT` | `UNAVAILABLE` |
| Adapter reports structured local delivery failure | `INVALID_OUTPUT` | Existing `INVALID_OUTPUT` |

Raw stdout and stderr stay in a private temporary directory until normalization.
Successful structured stderr reviews remain supported. Failed or unstructured
output is replaced by fixed diagnostics; it is not excerpted into artifacts.
Temporary files use restrictive permissions and are removed when the provider
subprocess exits. Adapter diagnostic logs are redirected into the same temporary
directory. The caller controls its temporary root through `TMPDIR`.
A forced process termination or power loss can prevent cleanup; use a protected
temporary root. Successful review text is retained as provider-authored content,
not certified as free of sensitive material.

## Worked example

Input plan `2026-07-11-issue-3462-example.md` contains `Example plan` and a final
newline. Let `P` be the exact bytes of `scripts/review/plan-review-prompt.md`,
and let `F` be the supplied plan filename. The independent expected input is:

```text
P + "\n\n--- PLAN (" + F + ") ---\n" + "Example plan\n"
```

The method writes those byte sequences to a private file, then redirects that
file to `codex exec -`. The answer is an argument vector containing only `exec`
and `-`, with the complete composed input on stdin. Serializing the illustrative
command `codex exec -` gives 12 ASCII code units: 5 for `codex`, 4 for `exec`,
1 for `-`, and 2 separating spaces. This hand calculation excludes the executable
path and terminating NUL; neither the prompt nor the plan affects that length.

For the logged-out Claude response from issue #3462, input JSON is
`{"loggedIn": false, "authMethod": "none"}` with unsuccessful auth status.
The result remains `UNAVAILABLE`, with `AUTH_REQUIRED`, a `claude auth login`
remedy, and no review invocation. A failing auth probe without that evidence is
`AUTH_CHECK_FAILED`, not a claim that credentials are absent.

## Validation and limits

The offline tests independently compose expected payloads and compare every byte,
including Unicode and final newlines. Synthetic plan sizes bracket the observed
32,089-character case in issue #3462 and the documented Windows command-line
size of 32,767 characters including NUL. The Windows figure comes from Microsoft's
`CreateProcessW` documentation, parameter `lpCommandLine`; it is not a universal
shell or executable-specific limit. No length threshold is used in production:
all Codex payloads use stdin.

Tests cover authenticated and unauthenticated probes, unknown auth state,
known incompatible versions, failed version probes, partial timeouts, invalid
output, metadata and temporary-file cleanup. Existing mock tests also exercise
parallel fanout, stderr promotion and adapter receipt handling.
Native Windows execution and live provider authentication are not established by
these Unix tests. An independent provider review remains required before merge;
no other assistant executable was invoked during this change.

## Sources

- [Codex CLI reference](https://developers.openai.com/codex/cli/reference/),
  `codex exec` stdin prompt and `codex login status`, retrieved 2026-10-22.
- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference),
  `claude auth status` JSON and exit-status contract, retrieved 2026-10-22.
- [Microsoft CreateProcessW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw),
  `lpCommandLine` size, retrieved 2026-10-22.
- Issue #3462: observed plan length and CLI versions; issues #2479, #2661,
  #2684 and #3294: prior version regression, EOF and environment handling.
- `scripts/review/lib/codex-version-guard.sh`: existing compatibility policy.
- `scripts/review/submit-to-agy.sh`: existing file delivery and receipt contract.
