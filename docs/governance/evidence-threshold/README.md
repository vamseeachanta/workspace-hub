# Evidence-threshold approval — evidence ledger (#3296)

Append-only audit records for the **shadow-mode** evidence-threshold eligibility
pilot. Each record makes one (shadow) eligibility decision reconstructable.

- **Policy:** [`../2026-06-28-evidence-threshold-approval-policy.md`](../2026-06-28-evidence-threshold-approval-policy.md)
- **Evaluator:** `scripts/governance/evidence_threshold_eligibility.py` (pure, fail-closed, shadow-mode only — it records, it never applies `status:plan-approved`).
- **Records land in:** `ledger/` (one append-only JSON object per shadow-eligible decision).

## Shared workflow assessment

The advisory CLI is `scripts/governance/workflow_decision.py`; the canonical
skill is [.claude/skills/coordination/shared-risk-workflow/SKILL.md](../../../.claude/skills/coordination/shared-risk-workflow/SKILL.md).
From the repository root, pipe one UTF-8 JSON request into:

```sh
uv run --no-project --with 'jsonschema[format-nongpl]==4.26.0' --with rfc3339-validator==0.1.4 --with referencing==0.37.0 python -B scripts/governance/workflow_decision.py
```

```json
{"schema_version":"1","provider":"codex","operation_kind":"edit","scope":{"repository_id":"fixture/repo","task_id":"issue:1","operation_id":"fix-typo","bounded":true},"changed_paths":["docs/example.md"],"effects":["local-reversible"],"authorization_reference":"session:user-message:1"}
```

`provider` is optional descriptive metadata. Claude and Codex use the same request
contract and receive identical assessments. This skill is explicitly loaded by
path during trials; native discovery or installation is not established.

Required fields are `schema_version` (exact string `1`), `operation_kind`, `scope`,
`changed_paths`, and `effects`. Scope contains exactly the three nonempty identity
strings in the example and `bounded: true`. Paths are owner-relative strings or
rename objects containing exactly `old_path` and `new_path`. Both rename endpoints
are included. Backslashes become slashes, then paths are sorted and deduplicated;
absolute paths, drive/UNC roots, traversal and ambiguous components are rejected.
The request asserts the complete change set; this pure helper cannot inspect a
repository or establish dependency completeness independently.

Operation kinds are `inspect`, `edit`, and `execute`. Inspection requires no changed
paths and exactly the `read-only` effect. Editing requires changed paths. Effect
values are `read-only`, `local-reversible`, `substantial-change`, `publication`,
`destruction`, `access-change`, and `engineering-basis-change`. Unknown or
inconsistent effects require context. Execution is never inferred routine from a
caller label. Protected paths remain substantial even when the effect is described
as reversible. Consequential effects require applicable approval independently of
the filename. A nonempty `authorization_reference` locates evidence for external
verification; booleans such as `approved` are rejected as unknown fields.

| Output field | Closed values |
|---|---|
| `risk_class` | read-only, routine-reversible, substantial, consequential, unknown |
| `authorization_assessment` | not-required-for-assessment, unverified-reference, missing |
| `action_boundary` | assessment-only, conditional-routine, approval-required, needs-context |
| `metric_advice` | not-requested, eligible-shadow, ineligible-shadow, unavailable |
| `reuse_assessment` | not-requested, invalid, candidate-pending-live-validation, needs-context |
| `reason_codes` | sorted unique codes from the list below |

Table 1. Advisory output vocabulary; no field represents verified permission.

Reason codes: `READ_ONLY_ASSESSMENT`, `ROUTINE_CONDITIONAL`, `PROTECTED_CHANGE`,
`CONSEQUENTIAL_EFFECT`, `UNKNOWN_EFFECT`, `MISSING_CONTEXT`, `UNVERIFIED_AUTHORITY`,
`APPROVAL_REQUIRED`, `METRIC_INELIGIBLE`, `METRIC_UNAVAILABLE`, `RECEIPT_INVALID`,
`KEY_CHANGED`, `EVIDENCE_DIGEST_MISMATCH`, `MUTABLE_VALIDATION_REQUIRED`,
`RESOURCE_UNVERIFIED`, `SCHEMA_UNAVAILABLE`.

The optional `metrics` object contains exactly `raw` (the existing evaluator's raw
metric dictionary) and `sample_count` (a nonnegative integer). A low or missing
metric produces shadow advice, never a change to session authorization. Omitted
metrics are `not-requested`.

This CLI uses path/effect assessment, not GitHub issue labels. Its optional metric
advice uses the historical proposed default thresholds; it does not expose the
older evaluator's configurable kill-switch or owner threshold overrides. The
historical `test-only-additive` class identifies test paths, not additive diff
semantics. The orchestrator must inspect the actual diff, issue context and scope;
path classification alone cannot establish that assertions were only added.

The CLI reads at most 1 MiB and rejects duplicate JSON keys, non-finite numbers,
excessive nesting, unknown fields and versions. It emits one JSON result; exit 2
means malformed input or an unknown risk class, while exit 0 means an assessment
was produced, **not permission to act**. Optional evidence invalidity is reported
in `reuse_assessment`; callers must inspect fields rather than treating exit 0 as
acceptance. No command, network request, persistence, label or cleanup is performed.
An otherwise classified routine request with missing authority can therefore
return exit 0 and `needs-context`; its action boundary still prevents progression.

### Verification receipts are separate from ledger records

The optional request `reuse` object contains `previous`, `current`, `as_of`
(RFC3339 current assessment time), `source_ids` (provided catalog membership),
and `evidence_artifacts` (opaque locator to UTF-8 content). Resource-bearing
comparisons also require explicit `resource_operation` and `destination`; code-only
comparisons may omit them because no resource rights are being assessed.
Locators are never opened as files. Supplied catalog membership, time, content and
resource metadata remain unverified assertions requiring independent checks.

[workflow-receipt-v1.schema.json](../../../config/schemas/workflow-receipt-v1.schema.json)
owns receipt fields and references the resource descriptor schema. Each receipt
validator is bound to the reviewed v1 schemas by canonical SHA-256 pins; altered
or substituted schemas fail validation. Changing a versioned schema therefore
requires a reviewed pin update and conformance checks, not a permissive fallback.
The resource pin includes its conformance vectors. Fixture edits therefore require
the same coordinated update; the 1 MiB schema bound also applies to that document.
Each receipt
contains `schema_version`, `observed_at`, `key`, `key_sha256`, `resources`, and
`evidence` (`locator` plus `evidence_artifact_sha256`). Each resource wrapper holds
`resource_descriptor_schema`, `resource_descriptor_sha256`,
`resource_stable_sha256`, and `descriptor`. Hashes are lowercase 64-digit SHA-256.

The key contains exactly `repository_id`, `task_id`, `operation_id`, `changed_paths`,
`code_revision`, `dirty_diff_sha256`, `resource_stable_sha256s`,
`environment_sha256`, `criteria_revision`, and `verification_procedure_version`.
Its hash uses canonical JSON of the entire object. Paths and resource digest sets
are sorted unique. Code-only tasks explicitly carry `resources: []` and
`resource_stable_sha256s: []`; resource-bearing tasks require the published resource
schema. The current key's repository, task, operation and paths must match the
assessment request. Inputs, code, dirty diff, environment, criteria or verifier
changes invalidate the candidate. Observation timestamps and artifact locators
are outside the key, so refreshing metadata or moving identical evidence does
not alone force expensive recomputation. Artifact bytes are hashed independently.
Different keys are rejected before expensive resource validation; `KEY_CHANGED`
does not imply that either rejected receipt was otherwise valid. Unknown path
classes require context; routine assessment requires a recognized eligible class.

The single production canonicalizer in `workflow_receipt.py` consumes the resource
schema's literal conformance vectors. It does not redefine source ownership,
rights, units or readiness. Schema-valid input alone does not establish access,
rights, freshness, complete dependency closure, evidence issuer or current
authorization. Equal valid receipts yield only `candidate-pending-live-validation`;
the orchestrator must independently revalidate those mutable conditions before
using prior results. Missing or invalid evidence never silently becomes reuse.
The receipt does not record pass/fail. The evidence artifact's content carries the
verification outcome and must be read against the governing criterion; a digest
match or candidate result does not mean the prior verification succeeded. The
independent temporal check must use a trusted current clock, not merely `as_of`.
`EVIDENCE_DIGEST_MISMATCH` covers unavailable, oversized or invalid UTF-8 content
as well as different bytes; it is an integrity-check refusal, not a tampering claim.
Receipt persistence and any live hook integration remain outside this slice.

### Reproduce acceptance

Run from the repository root. These commands register the resource marker at
invocation and include the RFC3339 format dependency required for validation.
The first intentionally deselects resource-dependent cases; the second is full
acceptance and permits no missing-predecessor skips.

```sh
uv run --no-project --with pytest==9.1.1 --with pyyaml==6.0.3 --with 'jsonschema[format-nongpl]==4.26.0' --with rfc3339-validator==0.1.4 --with referencing==0.37.0 python -B -m pytest -p no:cacheprovider --import-mode=importlib -o markers=resource_schema tests/governance/test_evidence_threshold_eligibility.py tests/governance/test_workflow_receipt.py tests/governance/test_workflow_decision.py -m 'not resource_schema' -q
uv run --no-project --with pytest==9.1.1 --with pyyaml==6.0.3 --with 'jsonschema[format-nongpl]==4.26.0' --with rfc3339-validator==0.1.4 --with referencing==0.37.0 python -B -m pytest -p no:cacheprovider --import-mode=importlib -o markers=resource_schema tests/governance/test_evidence_threshold_eligibility.py tests/governance/test_workflow_receipt.py tests/governance/test_workflow_decision.py tests/architecture/test_resource_authority_contract.py -q
```

## Record schema (unchanged historical ledger)

Produced by `build_ledger_record(...)`:

| Field | Meaning |
|---|---|
| `reviewed_commit_sha` | commit the decision was computed against |
| `plan_path` | the plan file under review |
| `review_artifact_paths` | the adversarial-review artifacts the metrics were read from |
| `issue_class` | the DERIVED class (`classify()` output) — never caller-supplied |
| `raw_metric_snapshot` | raw metric values as gathered |
| `normalized_metric_snapshot` | metrics after normalization to higher-is-better [0,1] |
| `thresholds` | the normalized thresholds in force at decision time |
| `window_bounds` | the trailing window the metrics were computed over |
| `sample_size` | number of eligible-class issues in the window |
| `decision` | `ELIGIBLE_SHADOW` (shadow-eligible) |
| `decided_at_utc` | ISO-8601 UTC timestamp |
| `mode` | always `"shadow"` — there is no `auto_apply` mode |

## Scope boundary (D6)

This is **governance-internal audit only**. It does NOT define the
envelope-determinism fields (`input_hash`, `result_hash`,
`provenance.code_version`) owned by #3282/#3283, nor the deckhand routing /
`result:` registry descriptor owned by #3282/#3295.

## Reconstruction

To audit a shadow decision: read the JSON record, confirm `reviewed_commit_sha`,
re-read the `review_artifact_paths` at that SHA, and re-run the evaluator with the
recorded `raw_metric_snapshot` + thresholds — the verdict must reproduce.
