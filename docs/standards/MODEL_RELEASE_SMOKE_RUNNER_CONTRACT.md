# Model-Release Smoke Runner Contract

> Scope: battery schema and future runner interface only; no runner implementation.
> Read budget: opening block identifies scope; requirements precede rationale.
> Format: `schema_version: 1`, declared under Battery format.
> Parent: [readiness contract](MODEL_RELEASE_READINESS_CONTRACT.md).

## Summary

The battery describes fixture-backed checks through a named adapter interface.
Structural validation does not establish execution or readiness. Missing or invalid
evidence is **incomplete**, never **pass**. This slice supplies documentation, a
strict input schema and a synthetic example; it supplies no runner implementation,
adapter, command invocation, scoring integration or golden-task corpus.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-25 | Declare battery inputs and the future evidence boundary so structural validation can precede runner implementation. |

## Battery format

The normative structure is
[`model-release-smoke-battery.schema.json`](../../config/ai/model-release-smoke-battery.schema.json).
The documented synthetic instance is
[`model-release-smoke-battery.example.yaml`](../../config/ai/model-release-smoke-battery.example.yaml).
Validate the parsed YAML instance against the committed JSON Schema with local
references only. Unknown fields are rejected at every object level.

| Required field | Meaning |
|---|---|
| `schema_version` | Integer format identifier, fixed to `1` for this declaration. |
| `battery_id` | Stable identity for the battery definition. |
| `fixture_root` | Directory relative to the trusted repository root, independent of the battery file's directory and current working directory. |
| `execution.interface` | Fixed interface identifier `adapter-v1`; this format carries no shell command. |
| `execution.adapter_id` | Identity selected from a separately trusted adapter registry. The battery cannot define the registry or executable. |
| `cases` | Nonempty array; each object requires `case_id`, `input_ref` and `expected_result_ref`. |
| `cases[].case_id` | Identity unique within the battery. |
| `cases[].input_ref` | Input file relative to `fixture_root`. |
| `cases[].expected_result_ref` | Expected-result file relative to `fixture_root`; its content format and deterministic comparison rule belong to the trusted adapter. |

Identities use lowercase ASCII words or digits separated by single hyphens and
start with a letter. Schema version `1` and the suffix in `adapter-v1` are declared
format choices, not measured values, scoring weights, release numbers or
performance thresholds. The schema's `const: 1` and `minItems: 1` encode this
identifier and the nonempty-array rule respectively. JSON Schema integer
semantics accept a numeric value with no fractional part, including `1.0`; the
quoted string `"1"` and a Boolean are invalid. Undeclared versions/interfaces
require an explicit future contract revision; they must not be coerced.

Exact duplicate case objects are rejected by the schema. Case identities must
also be checked for uniqueness by the future consumer: JSON Schema's
`uniqueItems` cannot enforce uniqueness of a property across differing objects.
The future YAML reader must reject duplicate mapping keys before parsing loses
them and accept only the JSON data model, without custom object construction.

## Path boundary

All path references are literal, portable, slash-separated relative paths.
Each segment starts and ends with an ASCII letter, digit, underscore or hyphen;
internal dots are permitted. The schema rejects empty paths, absolute paths,
drive-qualified paths, backslashes, URI schemes, percent encoding, whitespace,
control characters, empty segments, trailing slashes and the segments `.` or
`..`. No URL decoding, environment-variable substitution, tilde expansion or
shell expansion is permitted. The pattern anchors reject trailing newlines too.

Before any execution, the future consumer must resolve the repository root,
resolve `fixture_root` beneath it, and resolve each input and expected-result
reference beneath that fixture root. Both lexical and resolved containment are
required: symlinks must not escape either root. Referenced inputs/expectations
must exist as readable regular files, and platform-specific aliases or special
files must be rejected. Files must remain contained when opened, not merely at
a prior check. The schema checks syntax only; it cannot establish existence,
symlink containment, identity uniqueness or evidence integrity.

The synthetic example's fixture directory, files and adapter are intentionally
not provided. Its validation is structural only. Attempting to run it without
those dependencies would be incomplete. No external fixture, model or executable
is needed to validate it.

## Future execution interface

This section specifies a boundary, not an installed API or CLI. The conceptual
runner inputs are a battery file, a trusted repository root, a writable evidence
root selected by the caller, a trusted adapter registry, and a target descriptor
carrying provider, model and adapter implementation versions. The caller supplies
a run identity that distinguishes repeated attempts. Reusing evidence from an
unrelated target, battery revision or attempt is invalid.

The runner must parse and validate the entire battery, check unique identities,
resolve dependencies and enforce containment before invoking any adapter. An
invalid battery or missing dependency yields an incomplete record with diagnostics
and no dispatch. An unavailable target or unsupported adapter/interface is
incomplete, never an implicit skip or pass.

For `adapter-v1`, a trusted adapter receives the resolved input file and target
descriptor and writes an actual-result artifact under the caller's evidence root.
It returns the artifact reference and execution diagnostics to the future runner.
The runner uses the adapter's declared comparison rule to compare that artifact
with the resolved expected-result file. An absent or unsupported comparison rule
is incomplete. The battery cannot supply code, arguments or a comparison rule.
Adapters must preserve the input and expected-result files.

No invocation spelling, executable lookup, scheduling, retry, concurrency or
provider-routing mechanism is implemented or selected here. A successful process
exit or a structurally valid battery cannot substitute for comparison evidence.

## Future output record

The future runner must return and persist a JSON record, even when validation or
execution fails. The caller chooses the output destination outside fixture inputs.
If persistence fails, expose that operational error; never report a pass without
the required persisted evidence. This table is a prose output contract, not an
implemented output validator.

| Required field | Meaning |
|---|---|
| `schema_version` | Output format identifier `1`, a declared choice for this contract, independent of the input version. |
| `run_id` | Caller-supplied attempt identity. |
| `battery_id`, `battery_schema_version` | Validated input identity/version; use JSON `null` if invalid or unreadable, and retain diagnostics. |
| `battery_revision` | Content digest of the exact battery and referenced fixture bytes used; `null` if unavailable. The digest algorithm and encoding remain a runner-integration decision. |
| `target` | Observed provider, model and adapter implementation versions; unavailable values are `null` and deny a pass. |
| `adapter_id` | Validated adapter identity, or `null` if unavailable. |
| `state`, `reason` | Aggregate normalized state and nonempty diagnostic explanation. |
| `case_results` | Array of case records with `case_id`, `state`, nonempty `reason` and `evidence_refs`. No omitted or duplicate case can contribute to a pass. |

Each `evidence_refs` array contains literal references beneath the caller's
evidence root to actual outputs, comparison outcomes and execution diagnostics.
Apply the same path syntax and resolved-containment checks as for fixtures.
Every pass/fail comparison must retain the actual output and comparison evidence
bound to the expected fixture, target and attempt. Empty evidence is permitted
only for incomplete records explaining what is absent. Unreadable, stale,
mismatched or malformed evidence denies a pass. Invalid input with no reliable
case identities may produce an empty `case_results` array and must be incomplete.

| State | Required interpretation |
|---|---|
| `pass` | Execution completed and valid retained evidence demonstrates agreement with the expected result under the declared comparison rule. |
| `fail` | Execution and comparison completed with valid retained evidence demonstrating disagreement with the expected result. |
| `incomplete` | Required definition, dependency, case coverage, target metadata, comparison rule or evidence is missing, invalid, unsupported or unverified. A skipped, timed-out or interrupted case without complete evidence is incomplete. |
| `error` | A known operational execution/comparison failure has a valid retained diagnostic artifact; it is not an expected-result mismatch. Missing/invalid diagnostic evidence makes this incomplete instead. |

Aggregate precedence is `incomplete`, then `error`, then `fail`, then `pass`.
First apply record-level completeness checks, including case coverage and valid
evidence. Thereafter, any incomplete case makes the battery incomplete; otherwise
any error makes it error; otherwise any fail makes it fail. Pass requires every
declared case to pass with complete evidence and metadata. An empty result set
cannot pass. Keep all case states and reasons even when another state takes
aggregate precedence; do not hide a failed comparison behind missing evidence.

## Validation and integration limits

`tests/docs/test_model_release_smoke_schema.py` uses jsonschema and PyYAML to
validate the example and reject missing fields, wrong types, unknown keys,
undeclared identifiers and escaping/nonportable paths. It validates structure
only and never executes a command from the battery. All schema references are
local. With test dependencies already available, the named checks run offline:

```sh
python -m pytest tests/docs/test_model_release_smoke_schema.py tests/docs/test_workspace_hub_model_release_readiness.py -q -rA
```

Runner execution, semantic containment and duplicate-key checks, output-schema
enforcement, fixture content qualification, trusted adapter registration and
comparison implementation remain future integration work. No scoring weights,
performance thresholds or aggregate readiness score are defined. Structural
acceptance alone does not establish model quality or release readiness.

The [upgrade playbook](MODEL_RELEASE_UPGRADE_PLAYBOOK.md) governs adoption steps;
the [control-plane contract](CONTROL_PLANE_CONTRACT.md) retains authority over
entry points and adapter topology. Routing policy and the golden-task corpus are
unchanged by this contract.
