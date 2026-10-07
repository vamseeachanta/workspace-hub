# Final-report verification

Owner decision, 2026-10-03: [issue 3936](https://github.com/vamseeachanta/workspace-hub/issues/3936).

`legal-sanity-scan` and automatic repository identifier gates are retired.
Identifiers may flow through authorized repository workflows. Do not reinstall
these gates, require a legal-scan PASS, or treat an old scanner result as evidence.
Optional redaction libraries remain available for preparing a particular audience's
deliverable; their existence does not make them commit, CI or ingestion gates.

Verification moves to the final report and its actual outgoing bundle. This is
a manual review requirement, not a new script or automatic receipt gate.
Secret scanning, access controls, source-specific rights and engineering
qualification remain independent requirements. Repository/publication permissions
are not expanded by retiring identifier checks.

## Review the outgoing bundle

Before issuing a final report, the reviewing agent or operator records:

1. **Audience and destination:** internal, owning client, or public/hosted.
2. **Exact artifact set:** report, attachments, embedded data, plots and source
   exports; identify their revision or SHA-256 so later changes invalidate review.
3. **Identifier decision:** retain necessary names/project references for the
   authorized audience; redact only where that destination requires it.
4. **Rights and qualification:** source provenance, reuse limitations, technical
   basis and unresolved restrictions. Naming a public source is not itself a leak.
5. **Secret evidence:** the independent applicable secret checks and their results.
6. **Reviewer, date and verdict:** `verified`, `needs-review`, or `not-applicable`,
   with reasons and known limitations. Never label an unreviewed bundle verified.

The report's disclosure review covers machine-readable attachments as well as
visible prose. An altered bundle requires renewed review. Automated publishers
retain their independent secrets/access safeguards; this policy adds no invented
receipt-based CI gate. Source-specific publication authority still applies before
public release, including a public repository push.

## Examples for manual review

- A client report retains the client's own project identifier when authorized.
- A report reviewed as HTML but accompanied by an unreviewed CSV is `needs-review`.
- A reviewed report modified after its recorded digest is `needs-review` until
  reviewed again; the old receipt does not cover new bytes.
- A code-only change with no outgoing report records `not-applicable: no report`,
  and reports its actual code/test checks separately. It does not invent a report
  or claim blanket legal clearance.

## Migration limits

Historical plans and reports remain historical records. Live instructions that
still demand the retired scanner are superseded by this decision and should be
corrected when found. Track per-repository deployed revisions; a local or branch
change alone does not prove all machines have adopted retirement.
