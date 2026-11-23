# Reporting convention evidence contract

The [reporting convention](engineering-reporting-conventions-proposed.html) remains
a review draft. This companion consolidates its source relationships and defines
a reproducible audit of locally available adoption evidence. A successful audit
establishes byte and record consistency within an enumerated inventory. It does
not establish installation, receipt authenticity, engineering acceptance or use.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-22 | Source relationships and local evidence checks were documented to prevent storage and delivery from being counted as adoption. |

## Source precedence and reporting nuances

| Source and inspected scope | Preserved rule or boundary |
|---|---|
| [Convention, scope and precedence](engineering-reporting-conventions-proposed.html#scope), P6, 2026 | Applicable contractual requirements and explicit dated instructions retain precedence. File modification time alone does not establish acceptance. Private source records were not independently reinspected for this companion. |
| [Formal report structure](engineering-reporting-conventions-proposed.html#structure) and [presentation rules](engineering-reporting-conventions-proposed.html#presentation), P6, 2026 | The formal sequence, source tables, governing result and limitation placement remain intact. Later presentation rules govern conflicts within the draft. Operational evidence records retain their functional layout. |
| [Basis and traceability](engineering-reporting-conventions-proposed.html#basis), P6, 2026 | Supplied, measured, assumed and derived data remain distinct. Assumptions retain their confirmation evidence. Physical case identifiers and source-register table keys remain usable when defined. |
| [Claims and uncertainty](engineering-reporting-conventions-proposed.html#results) and [precision](engineering-reporting-conventions-proposed.html#visuals), P6, 2026 | Verification, validation, plausibility and acceptance remain separate. Display precision does not establish stored precision or accuracy; missing criteria are not invented. |
| [Human review](engineering-reporting-conventions-proposed.html#review), [document control](engineering-reporting-conventions-proposed.html#control) and [production checks](engineering-reporting-conventions-proposed.html#qa), P6, 2026 | Saved feedback, revision history, archived evidence, source rights, audience review and rendered-output checks remain required in their applicable workflows. This audit does not perform those checks. |
| [Adoption and reconciliation](engineering-reporting-conventions-proposed.html#adoption), P6, 2026 | Enumerate the inspected set and observation time; retain inaccessible targets. Storage, delivery, acknowledgement and adoption are separate claims. |
| [Final-report verification](FINAL_REPORT_VERIFICATION.md), 2026 | Review the actual outgoing bundle. This tool adds no identifier gate, publication permission or replacement for manual disclosure review. |
| [Existing exit record](../session-handoffs/2026-10-06-engineering-reporting-exit.html), 2026 | Publication was recorded; installed use was not established. Historical delivery records are not fresh observations. |

The linked proposals retain their distinct scopes:
rolling algorithm reports (issue 3431),
renderer selection (issue 3810) and
result precision (issue 3850).
This companion selects no renderer, changes no engineering criterion and starts
no proposed pilot. The existing reporting standard and shared instructions are
unchanged. Inaccessible original feedback and unobserved targets remain gaps.

## Local evidence format

The checker is `scripts/reporting/audit_reporting_adoption.py`. Its input is a
UTF-8 JSON object with exactly these fields:

- `standard`: `path`, `revision` and `sha256`. The path identifies the inspected
  standard bytes. The revision is a caller-supplied document label; the digest
  binds that label to the bytes being audited, without authenticating the label.
- `observed_at`: an inventory timestamp with timezone, no later than `--as-of`.
- `targets`: a nonempty array of uniquely aliased targets. The caller supplies
  the entire intended population; the checker cannot discover omitted targets.

Each target has `id` and `status`, and only the applicable optional fields below.
IDs use the neutral form `target-a`, with lowercase letters or digits after the
prefix. Keep the mapping to actual recipients in its authorized evidence store.
Every path is a normalized, root-relative POSIX file path. Absolute paths,
parent traversal and symlinks escaping the explicitly supplied root are rejected.
No current-directory inference, network discovery or remote writes occur.

| Reported status | Required evidence | What the audit establishes |
|---|---|---|
| `not inspected`, `unreachable` | Nonempty `reason`; no artifact or receipt | The gap remains visible; no evidence check is inferred. |
| `saved`, `revision-verified` | `artifact` | The supplied local snapshot matches the standard's SHA-256. This does not establish a deployed pointer or runtime installation. |
| `queued`, `acknowledged` | `receipt`; `artifact` is optional | The supplied receipt matches the target, reported state, revision and digest. A queue entry does not become an acknowledgement. |
| `adopted` | `artifact` and `receipt` | Both consistency checks passed for a reported adoption claim; actual use remains `NOT_EVALUATED`. |

A receipt is a JSON object with exactly `target`, `status`, `revision`, `sha256`
and `observed_at`. Its instant cannot follow the inventory observation. Equivalent
timezone offsets are compared as instants. An earlier receipt is historical
evidence, with no inferred freshness period. `reason` may also qualify an inspected
record, but is never repeated in the output. Unknown fields, duplicate JSON keys,
nonfinite numbers, unknown states and duplicate target aliases are errors.

SHA-256 is computed over exact file bytes with `hashlib.sha256`, without line-ending
normalization. Raw saved bytes and Git-normalized bytes are different digest scopes;
use the appropriate captured bytes throughout one inventory. A changed standard
requires a new digest, review and matching receipts. Relabelling an old receipt
does not authenticate it. Preserve original evidence; do not replace it in place.

## Invocation and interpretation

From the repository root:

```sh
uv run --no-project python scripts/reporting/audit_reporting_adoption.py \
  examples/reporting/adoption/manifest.json --root . \
  --as-of 2026-10-22T12:00:00Z
```

The command writes its JSON result to standard output and modifies no input.
Exit zero means that all supplied records are structurally valid and every
applicable consistency check passed. Exit one indicates invalid or unavailable
evidence; argument errors use the argument parser's usage exit. No exit status
means ecosystem adoption. Gaps remain visible in `reported_states` and each target
retains `reported_status`, `snapshot`, `receipt` and `adoption`. The latter and
`ecosystem_adoption` always remain `NOT_EVALUATED`: the tool cannot authenticate
acknowledgements, observe installed loaders or establish current use.

No engineering equations, numeric coefficients or acceptance limits are used.
Counts are exact enumerations of the supplied records, rather than a completeness
percentage. The [worked example](../reports/reporting-adoption-worked-example.html)
shows the inputs, method and hand-counted answer.

## Verification and remaining adoption work

Run the focused tests and Ruff without a project installation:

```sh
uv run --no-project --with pytest python -m pytest \
  tests/standards/test_reporting_adoption.py -q -rA -p no:cacheprovider
uv run --no-project --with ruff ruff check \
  scripts/reporting/audit_reporting_adoption.py \
  tests/standards/test_reporting_adoption.py
```

The tests exercise digest tampering, stale or mismatched receipts, future dates,
missing evidence, duplicate records, path escapes, invalid inputs, execution from
another directory and input preservation. Expected counts are independently
written out in the test module's docstring. The committed example is synthetic;
it is not evidence of distribution to an actual recipient.

For operational adoption, the maintainers will enumerate the authorized population,
record a dated source review and use the existing repository distribution tools.
An independent check will inspect each installed pointer and revision and obtain
revision-bound acknowledgement of use. Queued notices, unavailable recipients and
uninspected targets will remain separate until evidence changes their status.
No remote distribution or installation was performed by this change.
