# Delivery evidence snapshots

A local evaluator checks a supplied snapshot for capability input gaps,
geometry-to-report traceability and recorded pursuit outcomes. It produces JSON
or an inert HTML report. It reads no external registers, changes no source data
and sends no messages. `RECORDED` describes bookkeeping completeness only;
engineering suitability always remains `NOT_EVALUATED`.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| 1 | 2026-10-22 | Define evidence snapshot checks and a synthetic example so missing records and broken dependencies remain visible. |

## Scope and basis

This is a bounded contribution to initiative #3605, covering three slices:

1. Inventory each supplied capability's workflow, criteria and input evidence;
   retain an acquisition reference for unavailable or unknown inputs.
2. Check a supplied geometry → case → results → report chain and render the
   same findings as JSON or HTML.
3. Distinguish active pursuits from recorded terminal outcomes, requiring an
   evidence locator for each terminal outcome.

The existing inventory validator,
`scripts/knowledge/validate_inventory_readiness.py`, already distinguishes
implemented evidence from plans. This evaluator applies that distinction to a
caller-supplied delivery snapshot without creating another authoritative registry.
The prospect adapter and demo dispatch are unchanged.

The source basis is repository documentation, read directly:

- `docs/architecture/agent-data-handling-contract.md` (2026), **Original retention,
  rights and publication** and **Descriptor v1 and qualification**: a locator or
  digest is an assertion; permission, available bytes, units, qualification and
  current access require separate evidence.
- The same contract, **Foundational solver-result ownership and consumption**:
  preserve pinned revision/digest links; changed source evidence invalidates
  affected reuse. The snapshot tests only immediate digest equality.
- `docs/gtm/prospect-demo-sop.md` (2026), **Dual-Delivery State Machine**: recorded
  delivery status and external delivery actions have distinct responsibilities.
- `docs/gtm/intake/IMPLEMENTATION-STATUS.md` (2026), **Explicit non-promise**:
  intake scaffolding does not establish report generation or delivery.

No physical equations, design coefficients or acceptance limits are introduced.
The vocabulary below is a local bookkeeping contract, version 1, rather than a
standard-derived engineering criterion. No inaccessible source is replaced by a
remembered value. Engineering checks are `NOT_EVALUATED` until the responsible
analysis workflow supplies qualified inputs, methods and criteria.

## Contract v1

Input is one JSON object containing exactly `schema_version`, `capabilities`,
`artifacts` and `pursuits`. `schema_version` is the integer `1`. Unexpected or
missing keys, duplicate object keys, non-finite JSON, duplicate record identities
and invalid field types are errors. Each capability has its own input identities.
Capability and pursuit arrays, and each capability's inputs, are nonempty;
an empty artifact array is valid and records missing delivery evidence.

IDs use lowercase letters, digits, underscores and hyphens, starting with a
letter. References are logical relative locators using letters, digits, periods,
underscores and hyphens within slash-separated segments. Absolute paths, URLs,
backslashes, empty segments and dot traversal segments are rejected. Null means
unrecorded. Locators are never opened, resolved or turned into links. Use opaque
IDs and authorized evidence references; the evaluator cannot detect confidential
names embedded in otherwise valid text. Input and output belong with the owning
private evidence unless separately cleared for publication.

| Record | Required fields | Interpretation |
|---|---|---|
| Capability | `id`, `workflow_ref`, `criteria_ref`, `inputs` | Null workflow or criteria reference is unevaluated. References do not authenticate engineering approval. |
| Input | `id`, `state`, `evidence_ref`, `acquisition_ref` | States are `available`, `missing`, `unknown`. Missing means a known gap; unknown or available without evidence means unevaluated. An acquisition reference identifies the request to pursue; a null value exposes an unassigned action. |
| Artifact | `stage`, `ref`, `revision`, `sha256`, `upstream_sha256` | Stages are `geometry`, `case`, `results`, `report`, each at most once. Null reference, revision or digest is unevaluated. Missing stages are gaps. |
| Pursuit | `id`, `state`, `evidence_ref`, `next_action_ref` | `active` remains open even with evidence. `won`, `lost`, `declined`, `withdrawn` are terminal only for this snapshot, with evidence required. No external pursuit is closed by this tool. |

Digest syntax follows the data handling contract: exactly 64 lowercase
hexadecimal characters, without the algorithm prefix in these explicitly named
`sha256` fields. For geometry, `upstream_sha256` must be null. Each later stage's
upstream digest is compared with the immediately preceding stage's recorded
content digest. Missing digests remain unevaluated; unequal known digests are a
gap. Array ordering has no effect on this fixed stage order. Geometry bytes,
coordinate transforms, solver identity and native outputs remain the owning
workflow's responsibility; the snapshot is not a replacement run manifest.

The aggregation rules and counts are definitions, not empirical thresholds:

- A group is `GAPS` if any finding is a known gap; otherwise it is
  `NOT_EVALUATED` if any finding is uncertain; otherwise it is `RECORDED`.
- Overall status applies that same rule across all findings. Unknown evidence is
  never converted to a successful engineering check.
- `inputs = sum(number of inputs in each capability)`.
- `findings = number of emitted missing, unknown or mismatched records`.
  Several missing fields in one record can produce several findings.

A structurally valid snapshot always produces a report. CLI exit codes, defined
here for automation, are `0` for `RECORDED`, `1` for `GAPS` or `NOT_EVALUATED`, and
`2` for invalid or unreadable input. Exit `0` does not authorize engineering use,
publication, outreach or delivery. Validation errors identify fields without
printing submitted values or local input paths.

## Worked example: inputs, method and answer

`docs/gtm/examples/delivery-readiness.json` is entirely synthetic. Its repeated
hexadecimal digest strings are illustrative labels, not hashes of real artifacts.
The relative evidence references do not point to real analysis data.

Inputs: one screening capability with two required inputs; geometry is recorded
as available and conditions as missing, with acquisition reference
`requests/conditions`. All four artifacts carry revision labels, digest labels
and matching upstream labels. One pursuit is active, with next action
`actions/request-conditions`.

Method: enumerate the input gaps; compare case-to-geometry, results-to-case and
report-to-results digest labels; then test whether the pursuit has a terminal
state and evidence. This is an independent hand calculation:

| Check | Hand calculation | Answer |
|---|---|---|
| Capability inventory | Geometry has evidence; conditions are missing | One known input gap |
| Delivery chain | Three immediate digest pairs agree | `RECORDED` traceability assertions |
| Pursuit | Active state still requires action | One open pursuit |
| Findings | One missing input + one open pursuit | Two findings; overall `GAPS` |
| Engineering | No artifact bytes, criteria or physical results qualified | `NOT_EVALUATED` |

Run from the repository root, directing reports to an authorized output folder:

```bash
uv run --no-project python scripts/gtm/delivery_readiness.py \
  docs/gtm/examples/delivery-readiness.json
uv run --no-project python scripts/gtm/delivery_readiness.py \
  docs/gtm/examples/delivery-readiness.json --format html > "$TMPDIR/delivery.html"
```

Both commands intentionally return `1` because the example contains gaps.
The JSON output reports counts of one capability, two inputs, four artifacts,
one pursuit and two findings. Changing conditions to `available` with evidence,
and recording a terminal pursuit outcome with evidence, removes those two
findings. It still leaves engineering suitability `NOT_EVALUATED`.

Tests are in `scripts/gtm/tests/test_delivery_readiness.py`. Expected counts are
written out in test docstrings; fixtures are synthetic. Cases cover missing and
unknown inputs, absent workflow/criteria evidence, every missing artifact stage,
each broken dependency, all terminal outcomes without evidence, active pursuits,
status precedence, duplicate identities, malformed JSON, relative references,
CLI behavior and the worked example.

## Limits and later slices

This implements local evidence bookkeeping, not the entire initiative. It cannot
close business pursuits, acquire missing data, qualify engineering capabilities,
execute solvers or produce a qualified engineering report. It does not assert
that the supplied capability list includes every required discipline, nor that
each declared input checklist is complete for its intended use.

Later work belongs with the authoritative workflows and private evidence:
verify actual bytes and revision availability; bind each capability input and
criterion to the appropriate case; enforce rights, freshness, units and
applicability; preserve native result provenance; obtain independent engineering
review; integrate authorized register snapshots; and perform separately
authorized delivery and pursuit actions. A complete local snapshot cannot close
the initiative. No private issue content or derived engineering values are
included in this example.
