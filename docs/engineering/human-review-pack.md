# Engineering human-review packs

The shared pack presents evidence beside a physical expectation, retains human
decisions and provides an explicit issue-eligibility check. It does not establish
engineering correctness, reviewer identity or publication authority. Results start
pending; a preparer's recommendation never sets acceptance.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| 1 | 2026-10-22 | Define the card interface, read-back and explicit gate so evidence and human decisions travel together. |

## Contract and sources

The authoritative structural interface is
[`human-review-pack-v1.schema.json`](../../config/schemas/human-review-pack-v1.schema.json).
The Python validator adds unique identity, finite numbers, image restrictions,
timestamp comparisons and surface conditions. The schema's `export` definition
describes browser decision exports; calculated record fields are outputs only.

The existing repository rules supply the engineering contract:

- [Reproducibility is not correctness](../../.claude/rules/reproducibility-is-not-correctness.md),
  clauses 1 and 4: independent comparator classes and criteria fixed before a run.
- [Report audience and surface](../../.claude/rules/report-audience-and-surface.md),
  surface table and clause 5: explicit audience, disclosure review and the
  `implausible`, `not_implausible`, `not_evaluated` vocabulary.
- [Mechanism before publication](../../.claude/rules/mechanism-before-publication.md),
  opening requirement and clauses 1–4: causal claims require evidence and an
  established mechanism; observations alone do not establish a cause.

No engineering constant, coefficient or default acceptance limit is built in.
The adapter supplies all observed and expected quantities in identical units,
the absolute tolerance, its source and pre-run timestamp, the run start, the
governing case, comparator independence and method qualification reference.
An unavailable expected value, observed value or tolerance is JSON `null`.
Unknown method qualification is `not_evaluated` with an explanatory reference.

The generic criterion is `abs(observed - expected) <= tolerance`; this is an
arithmetic interval comparison, not an engineering equation or design limit.
Relative limits, asymmetric bands, unit conversion and domain equations belong
in adapters and require their own sourced basis and qualification. An adapter
must preserve the underlying raw response; filtering, clipping or relabelling
a non-physical response to conceal it is not permitted.

An engineering result requires a card with evidence and a recorded human decision
before acceptance, issue or publication. A causal mechanism requires a
`not_implausible` check tied to its physical expectation, comparator, criterion
and governing case. Otherwise its cause remains not established. Plain
observations without a causal claim do not require a mechanism card.

## Three slices

1. **Cards and surface.** The adapter produces pack JSON and embeds evidence
   screenshots or plots as PNG/JPEG data URIs. Each card has a recommendation,
   rationale and at least one check. The tool builds one self-contained HTML
   page containing all cards, images, check tables and reviewer controls.
   Network resources and active image formats are refused. Evidence captions
   identify what was measured, its source and any limitations.
2. **Human decisions and read-back.** Browser controls default to `pending` and
   save locally under the complete pack digest. Export produces JSON with that
   digest, a reviewer record reference, review timestamp and every card decision
   and note. Ingest writes a new job record listing recommendation differences
   and every nonempty note as a potential instruction. It does not execute notes.
3. **Explicit acceptance gate.** The `gate` command checks the original pack
   against the export, including all card identities. It returns success only
   when every card is `accepted` or `accepted_with_note` and all its checks are
   `not_implausible`. The latter decision requires a note. Missing, duplicate,
   unknown or stale card decisions are refused. Rejected, queried and pending
   cards block issue. A human acceptance of a flagged check is retained in the
   read-back, but does not make that card issuable.

The comparator enums are `closed-form`, `measured`, `cross-solver`,
`conservation`, `archived-run` and `none`. The last two provide no independent
acceptance basis. An unqualified method, dependent comparator, unavailable value
or criterion fixed at or after the run start yields `not_evaluated`, never an
implicit favourable verdict. Qualification requires named cases where the
expectation must hold before applying the method to other cases. This generic
tool records the qualification assertion; the reviewer checks its evidence.

Review focus is `candidate` when all checks are `not_implausible`, `no value`
when every observed value is missing, and `check flagged` otherwise. Physics
verdicts and reviewer acceptance states remain separate.

## Surface and trust boundaries

The surface is explicit: `internal`, `client-deliverable` or `hosted`. The
default example is internal. A hosted build requires a `cleared` disclosure
record with a nonempty reference and every image marked `absent` or `redacted`
for identifiers. Evidence declared to contain an identifier is refused on that
surface. This checks declared review metadata; it is not image inspection,
OCR, a name blacklist or an authorization service. Reviewers must inspect all
text and image contents and verify rights for the destination before publication.
Private evidence stays in its owning private record. Only synthetic data and
general tooling belong in this public repository.

All displayed adapter text is escaped. The page has a content security policy
and no external resources. Local browser storage may be unavailable or shared;
export the decisions and retain them in the authorized job record. The SHA-256
digest binds every input, criterion, image and revision using sorted compact
UTF-8 JSON. Changed evidence requires a new review. It detects stale exports;
it does not authenticate a person, timestamp, independence claim or source.
The gate must re-read the original pack and export, not trust an edited
`issuable` field in a derived record. Exported acceptance is provisional until
the surrounding authorized workflow verifies reviewer identity and evidence.

## Worked example

[`equilibrium.json`](../../examples/review-pack/equilibrium.json) is an entirely
synthetic static-equilibrium adapter output. No solver is run or imported.
Inputs are an applied load of 10 N and support reactions of 4 N and 6 N.
The conservation expectation is reaction balance, per the conservation-check
requirement in the first source above. An independent hand calculation gives
`4 N + 6 N = 10 N` and discrepancy `abs(10 N - 10 N) = 0 N`.
The demonstration tolerance of 0.5 N is an illustrative input fixed before the
synthetic run, not a sourced engineering acceptance limit or advice for a design.
The same basis and independent calculation appear in the test module docstring.
Boundary probes give `abs(10.5 - 10) = 0.5 N` within the declared interval and
`abs(11 - 10) = 1 N` outside it. All numerical engineering values in this example
are invented demonstration inputs, not values from a standard or publication.

The embedded synthetic plot shows the applied load above the two reactions with
equal scale. It is labelled as illustrative evidence rather than a measured
screenshot. The answer is `not_implausible`, review focus `candidate`, acceptance
`pending` until the human decides. The method qualification reference names the
hand calculation and boundary probes; it does not qualify a solver.

With `jsonschema` available, use the following commands. `OUTPUT_DIR` must point
to an authorized output folder outside the repository. The Python environment
must already satisfy its dependencies, or be supplied through `uv run`.

```bash
python scripts/review/review_pack.py build \
  examples/review-pack/equilibrium.json "$OUTPUT_DIR/equilibrium.html"
# Open the local HTML, enter a reviewer record reference and export decisions.
python scripts/review/review_pack.py ingest \
  examples/review-pack/equilibrium.json "$OUTPUT_DIR/review-decisions.json" \
  "$OUTPUT_DIR/review-record.json"
python scripts/review/review_pack.py gate \
  examples/review-pack/equilibrium.json "$OUTPUT_DIR/review-decisions.json"
```

Exit status is zero for a successful build/ingest or an issuable gate, one for
invalid input/output, and two for a valid but non-issuable gate. Diagnostics omit
payload values and paths. Read-back preserves decisions even when issue is
blocked; the gate does not modify inputs or issue any deliverable.

## Verification and migration limits

Tests cover independent hand-calculated bounds, schema and enums, non-finite
values, qualification, pre-run criteria, hosted disclosure, embedded evidence,
HTML escaping, decision round-trip, stale digests, decision completeness,
recommendation differences, instruction notes and command-line behaviour.

Existing decision boards continue to work. On their next change, adapters can
map acceptance items onto this schema while keeping choices between options in
the boards. Automatic integration into report issuance, domain adapters and
causal-claim parsing are later work. This command is an explicit gate, not a
repository-wide publication hook. A plain decision board cannot substitute for
the evidence card. No existing shared rule file or board is changed here.
Second-provider review and a real study's human evidence review remain required
before merge and engineering use. The emitted JavaScript is exercised against a
DOM substitute and its export is ingested by Python, including storage failure.
Browser layout, downloads and persistence still require manual checking; no
browser is started by this test suite.
