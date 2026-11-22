# Review evidence and capability receipts

## Summary

The packet builder freezes the review target; its verifier detects changes to
the target or the packet. The portable preflight consumer checks recorded
capabilities against explicit requirements and a caller-supplied lifetime.
Neither artifact establishes authorization, reviewer acknowledgement or live
access. This guide extends the tools and shared workflow introduced for #3973.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-22 | Document packet validation and receipt consumption with an executable example so recorded evidence can be checked before reuse. |

## Existing workflow requirements

The [shared contract](../../config/agents/SHARED_SOUL.md#must-fire-rules-per-message-reinforcement)
remains authoritative. The following is an operating checklist, not a new
controller or an installed enforcement claim.

- Record why work stopped: policy restriction, diagnosis required or failed
  cases. Continue unaffected authorized cases after an isolated failure. Recheck
  authority and state after a quota reset; a persistent scheduler requires its
  own authorization.
- Report attempted and completed native runs, qualified results and report
  freshness before test counts. Advancing output establishes progress; a live
  process or successful process exit alone does not establish completion.
- Freeze review inputs before sending them. Verify the packet and target after
  review and before acting on the verdict. Changed bytes require renewed review.
  After three MAJOR rounds, propose a simpler design to the maintainer; the review
  requirement remains. This threshold comes from the shared contract's frozen
  packet rule, not a measured reliability limit.
- Carry revisions, capability probe time, responsibility and acknowledgement
  state in a handoff. Reprobe capability claims before relying on them. Queueing
  a message does not establish receipt or transfer responsibility.
- Rotate at a milestone, three compactions or 48 hours, whichever comes first,
  under the shared contract's rotation rule. Retain inputs, arrays, metrics and
  manifests against a versioned criterion before starting a campaign. Read PDFs
  as text first and render the pages needed for figures or tables.

Controller integration, automatic resumption and handoff persistence remain
separate work. This change does not modify shared instructions or their generated
runtimes, which already contain these requirements.

## Freeze and verify a review target

Run from the checkout root. Set `REVIEW_SCRATCH` to an existing approved output
directory outside the checkout and `REVIEW_PACKET_BUDGET_BYTES` to the transport's
usable byte budget. The budget is an input, not an acceptance value inferred from
a provider's advertised context size.

```sh
python scripts/review/build-review-packet.py build \
  --out "$REVIEW_SCRATCH/packet.md" \
  --manifest "$REVIEW_SCRATCH/manifest.json" \
  --max-bytes "$REVIEW_PACKET_BUDGET_BYTES" \
  scripts/windows/validate-agent-preflight.py
python scripts/review/build-review-packet.py verify \
  --manifest "$REVIEW_SCRATCH/manifest.json" \
  --packet "$REVIEW_SCRATCH/packet.md"
```

Send the packet on standard input using the established review transport. Retain
the manifest and the exact packet sent, and repeat `verify` after review. Use
`--packet` when the sent copy differs in location from the recorded packet path.

The digest is SHA-256 over the stored bytes, including line endings; the numbered
display is a reading aid. Duplicate resolved input paths, including symlink
aliases, are refused before publication. Malformed manifests, ambiguous JSON
object keys, invalid byte counts and unreadable paths are input errors. Packet
verification has these process results:

| Exit code | Meaning | Disposition |
|---|---|---|
| `0` | Packet and reviewed files are unchanged | The existing review may be considered with its other prerequisites. |
| `1` | Invalid or unreadable input | Correct the evidence before considering the verdict. |
| `2` | Build exceeds the supplied budget | Split the review; do not truncate its target. |
| `3` | Target or packet changed or is missing | Rebuild and obtain review of the affected scope. |

These codes and the raw-byte domain are defined by
[`build-review-packet.py`](../../scripts/review/build-review-packet.py),
`review-packet/1`. A hash pins bytes; it does not authenticate a reviewer or protect
against replacement of both the packet and its manifest. Preserve a trusted copy.

## Consume recorded capability evidence

[`agent-preflight.ps1`](../../scripts/windows/agent-preflight.ps1) remains the
Windows collector. The new
[`validate-agent-preflight.py`](../../scripts/windows/validate-agent-preflight.py)
reads its `agent-preflight/1` receipt without starting probes, querying another
assistant or making network requests. Run it with each required capability and
the receipt lifetime selected for the intended use:

```sh
python scripts/windows/validate-agent-preflight.py \
  "$REVIEW_SCRATCH/receipt.json" \
  --max-age-seconds "$CAPABILITY_LIFETIME_SECONDS" \
  --require python --require gh
```

`--as-of` supplies a comparison instant for reproducible checking; otherwise the
current UTC time is used. Timestamp syntax follows
[RFC 3339, section 5.6 (2002)](https://www.rfc-editor.org/rfc/rfc3339#section-5.6).
Leap-second timestamps are not evaluated by this consumer. Fractional seconds
are retained for comparisons, including the collector's round-trip format.

The method is `age = comparison instant - probe instant`. Eligibility requires
`0 <= age < supplied lifetime`. The strict expiry comparison follows
the [data handling contract](../architecture/agent-data-handling-contract.md#descriptor-v1-and-qualification)
(`valid_until > as_of`). There is no default operational lifetime. Capability
criteria come from the existing collector fields:

| Required capability | Evidence required |
|---|---|
| `python` | Selected executable exists, a nonempty version is recorded, virtual environment configuration is present or inapplicable, and preferred encoding is UTF-8. |
| `git` | Executable and nonempty version are recorded. |
| `gh` | Executable and nonempty version are recorded; the authenticated API probe result is boolean true. |

All error-severity findings block eligibility. Warnings and informational findings
are retained in the original receipt for assessment; they do not establish an
error. A failed stored-account status probe alone does not invalidate successful
active authentication. Missing fields required by the selected capability deny
eligibility. This consumer checks that subset of evidence, not every collector
field or CLI version. It does not evaluate shell selection or task-specific
software requirements.

JSON object names must be unique, and non-finite number literals are refused,
following [RFC 8259, sections 4 and 6 (2017)](https://www.rfc-editor.org/rfc/rfc8259).
Printed summaries contain static failure codes, requirements and age; raw
diagnostics, recorded paths and environment-derived values are not echoed.
Receipt-check exits are `0` for ready evidence, `1` for invalid input, `2` for
command usage errors and `3` for evidence that is not ready. Ready evidence still
requires live revalidation when the operation needs current access.

## Worked example: current evidence and expiry

The following input is synthetic and contains only the fields consumed by this
check. The interpreter version and capability outcomes are exercise inputs, not
claims about an installation. Save the JSON as `receipt.json` in the output
directory. The example's lifetime of 600 seconds is supplied for this exercise;
it is not an operating recommendation.

```json
{
  "schema": "agent-preflight/1",
  "generated_at": "2026-10-22T12:00:00.0000000Z",
  "python": {
    "selected": "python.exe",
    "selected_exists": true,
    "version": "3.12.0",
    "preferred_encoding": "UTF-8",
    "venv_cfg_present": null
  },
  "gh": {
    "path": "gh.exe",
    "version": "gh version synthetic",
    "auth_ok": true,
    "auth_status_ok": false
  },
  "findings": []
}
```

```sh
python scripts/windows/validate-agent-preflight.py \
  "$REVIEW_SCRATCH/receipt.json" --as-of 2026-10-22T12:05:00Z \
  --max-age-seconds 600 --require python --require gh
```

Hand calculation: 12:05 minus 12:00 is five minutes, or 300 seconds. Since
`0 <= 300 < 600` and both capabilities have positive recorded evidence, the
answer is `status: ready`, `age_seconds: 300.0`, no failures, exit `0`.

At `--as-of 2026-10-22T12:10:00Z`, the age is ten minutes, or 600 seconds.
Equality fails the strict expiry comparison: the answer is `status: not-ready`,
`age_seconds: 600.0`, failure `RECEIPT_EXPIRED`, exit `3`. Obtain new evidence
before reuse. The automated example test reads this JSON block and checks both
answers, rather than deriving its expected result from the validator.

## Verification and limits

Run the packet and receipt tests with `python -m pytest
tests/review/test_build_review_packet.py
tests/preflight/test_validate_agent_preflight.py`. Their expected dispositions
come from the tool contracts; the expected ages come from the hand calculation
above. File contents and existing outputs are checked for preservation when
input validation fails.

The portable tests do not establish live Windows probe behavior or cross-provider
review. They do not measure engineering progress or qualify solver outputs. Those
claims still require their native evidence and the applicable criterion.
