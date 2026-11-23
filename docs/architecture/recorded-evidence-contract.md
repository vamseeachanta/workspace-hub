# Recorded evidence and independently verified conclusions

A caller-recorded class describes a claim about evidence. It cannot authenticate
its origin, strengthen engineering readiness or grant authorization. This
bounded contract and opt-in reference adapter implement the follow-up in issue
#3851 (2026); existing consumers retain their current behavior. The inventory
below identifies adoption candidates, not completed migrations.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Separate recorded claims from independently verified conclusions after a label-only status overclaim. |

## Scope and basis

The observed defect was a preparation bundle reporting a stronger status after
only its recorded artifact class changed. The linked correction is in
`digitalmodel`, issue #2094, commit `1b85a3e6`,
`tests/ansys/padeye_pressure_bundle.py:verify_pressure_bundle`. That source was
inspected at the pinned revision. It returns
`preparation_content_checks_passed`, preserves the recorded class and explicitly
leaves independent classification, capture and source-revision verification
false. Native qualification and stress-solve authorization remain false.
No solver or engineering result from that repository is imported here.

The local [data handling contract](agent-data-handling-contract.md), sections
“Descriptor v1 and qualification” and “Stable projection and shared conformance
contract”, distinguishes observation, content integrity, current eligibility and
live authorization. The [standards provenance contract](../document-intelligence/standards-codes-provenance-reuse-contract.md)
retains source identity and rights across derived artifacts. These existing
contracts and the linked correction supply the logical basis for this proposal;
no engineering equation, numerical coefficient or acceptance limit is introduced.

## Inventory of inspected boundaries

Coverage is limited to the available repository and the pinned linked source.
Searches covered evidence/class, provenance, verification and readiness fields in
`scripts/`, `tests/`, `config/schemas/` and the architecture contracts, followed by
inspection of the named functions. Other engineering repositories were not
inventoried. This is not a finding that all adapters have been identified.

| Surface | Observed transition | Interpretation and proposed adoption |
| --- | --- | --- |
| Linked `verify_pressure_bundle` above | Recorded class accompanies content-check success; independent flags remain false. | Corrected precedent; retain class-mutation regression tests. |
| [Calculation renderer](../../scripts/reporting/calc_report_html.py), `printable_status` and `printable_verification_status` | Supplied status and a printable dated role permit status display. | Rendering eligibility is not role authentication or verified approval. A future adapter should distinguish recorded status from verified approval in both HTML and Markdown. |
| [Report input validator](../../scripts/reporting/generate-calc-report.py), `load_and_validate` | Accepts draft/reviewed/approved metadata and checks structural input requirements. | Structural validity does not authenticate the supplied status, reviewer or approver. Keep validation separate from provenance qualification. |
| [Promotion ledger](../../scripts/client_llm_wiki/promotion_ledger.py), `classify_readiness` | Supplied confidence fields and release gates can derive `client-ready`. | A ledger assessment is conditional on supplied evidence. It cannot authenticate release gates. Independent gate resolution and wording require a separate adoption change. |
| [Report bundle schema](report-evidence-bundle.schema.yaml) and [schema guide](report-evidence-bundle-schema.md) | Source classes, confidence/readiness and promotion gates are required structural fields. | Schema acceptance cannot prove those assertions. The guide's proof wording requires reconciliation when this schema is adopted for verified conclusions. |
| [Readiness bundle validator](../../scripts/analysis/readiness_bundle_schema.py), `validate_bundle` | Returns structural/format errors from the supplied schema observation. | An empty error list establishes schema validity only. It does not verify provenance, access or readiness. |
| [Workflow receipts](../../scripts/governance/workflow_receipt.py), `validate_resource` and `compare_receipts` | Supplied resource status is a prerequisite; digest and context checks yield at most `candidate-pending-live-validation`. | Preserve this bound. Direct resource validation is not independent readiness authentication; consumers still need live evidence and rights validation. |

No listed production adapter is changed or automatically enrolled by this work.
Adoption must preserve source-specific engineering checks and independently
established authorization; a generic label hierarchy would repeat the defect.

## Shared recorded-versus-verified contract

An adapter shall keep the following conclusions distinct:

- **Recorded class:** inert caller metadata, retained without promoting its name
  into a status. Unknown nonempty labels remain recorded, not trusted.
- **Content assessment:** outcome of named checks on the supplied bytes. This
  says only what the selected procedure examined. A digest match establishes
  byte agreement, not execution history or correctness of the procedure.
- **Independent classification and provenance:** authenticated evidence of the
  asserted origin, linked to the exact artifact and relevant source revision.
  A caller Boolean, timestamp, role name, path, digest or receipt reference alone
  cannot supply that authentication.
- **Readiness:** a separate current intended-use assessment, including applicable
  engineering criteria, units, rights, access, freshness and limitations. Native
  origin alone does not establish this assessment.
- **Authorization:** a separately authenticated decision matching the action,
  destination and scope. Content success or readiness never supplies permission.

For fixed bytes, procedure and independent evidence, changing only the recorded
class shall leave content conclusions and all verification, readiness and
authorization conclusions unchanged. The same constraint applies to display
labels and report summaries. Invalid labels may be rejected by a domain-specific
schema, but cannot produce a stronger conclusion.

Before emitting a positive independent conclusion, a future consumer must
resolve evidence through its trusted authority boundary, verify the exact content
binding and source revision, check the verifier's identity and scope, and reject
stale, unavailable, contradictory or mismatched evidence. Rights and proposed
use remain separate. This proposal does not define a new authentication transport
or add a `verified=True` input. Such inputs would recreate self-authentication.

## Content assessment reference

[assess_content](../../scripts/governance/evidence_classification.py) is a pure,
opt-in adapter. It accepts immutable bytes, a nonempty recorded class and a
mapping of named callable predicates. Predicates are trusted application code,
not untrusted plugins. They receive only the bytes; the adapter never passes
them the class. They must be deterministic and free of side effects.

| Named check outcomes | Aggregate status |
| --- | --- |
| Nonempty set containing only literal `True` | `content_checks_passed` |
| Any literal `False` or `ERROR` | `content_checks_failed` |
| Empty set, or any `None` with no failure | `content_checks_not_evaluated` |

`True`, `False` and `None` become `PASS`, `FAIL` and `NOT_EVALUATED` respectively.
Other return types become `ERROR`; truthiness cannot turn a string into success.
Expected arithmetic, assertion, lookup, operating-system, runtime, type and value
errors become `ERROR` without diagnostic text. Other exceptions abort without a
verdict. Callers must keep their exception diagnostics private. Names and recorded
classes are caller text and still require normal output escaping and publication
review. The adapter itself performs no I/O or publication.

All returned observations explicitly set
`classification_independently_verified`, `provenance_independently_verified`,
`native_qualification`, `solve_authorized` and `publication_authorized` to false.
`readiness_status` remains `NOT_EVALUATED`. False means not established by this
adapter; it does not prove an artifact was never captured natively.

The adapter does not assess procedure completeness or select engineering checks.
Even an always-true predicate can pass its own content assessment, with no
stronger conclusion. A persistent consumer must bind its observations to retained
artifact digests, procedure/version, criteria and context under the existing data
handling contract. This transient reference does not issue reusable receipts.

## Worked example: inputs, method and answer

Run from the repository root:

```sh
uv run --no-project python -m examples.governance.recorded_evidence
```

The [executable example](../../examples/governance/recorded_evidence.py) uses only
synthetic bytes. Its first input is `b"result=synthetic\n"`. The named checks ask
whether it starts with `b"result="` and ends with a newline. Direct inspection
makes both answers true; no engineering acceptance threshold is involved.
The second input changes only the recorded class. The third removes the newline.

| Case | Recorded class | Record check | Newline check | Answer |
| --- | --- | --- | --- | --- |
| Original bytes | `format_reproduction` | PASS | PASS | `content_checks_passed` |
| Identical bytes | `native_capture` | PASS | PASS | `content_checks_passed` |
| Newline removed | `native_capture` | PASS | FAIL | `content_checks_failed` |

For every row, independent classification/provenance, native qualification and
authorizations remain false, and readiness is `NOT_EVALUATED`. Thus the example
answers the label-only defect without claiming a native capture or a solve.
The [tests](../../tests/governance/test_evidence_classification.py) write out this
hand derivation and also exercise missing checks, malformed results, predicate
errors, immutable inputs, caller-override rejection and deterministic ordering.

## Delivery slices and remaining adoption

The first slice supplies the tested reference adapter. The second supplies this
bounded inventory and recorded-versus-verified contract. The third supplies the
executable worked example and label-mutation regression tests.

Later adoption will need separate consumer changes, domain-specific verification
sources, failure handling and review. It includes report wording, authenticated
release-gate resolution and readiness qualification in the inventoried surfaces.
No ecosystem-wide coverage, native qualification, engineering acceptance,
publication permission or independent review completion is established here.
