# Offline readiness follow-up proposals

## Summary

This worked example maps explicit readiness gaps to deterministic draft-only
proposals using a caller-provided policy table and in-memory existing proposals.
It does not implement issue creation or change approval authority. It never
queries GitHub, runs a model, evaluates readiness gates or edits entrypoints.

## Revision history

| Revision | Date | What changed and why |
|---|---|---|
| Initial | 2026-10-26 | Add a pure fixture example to explain draft deduplication without publication. |

## Scope and basis

The [readiness contract](../standards/MODEL_RELEASE_READINESS_CONTRACT.md#readiness-dimensions)
provides dimension names. This example supplies no approved threshold input and
sets no normative threshold. The literal fixtures below are the sole source of
example policy values; they are invented to exercise branches, not measured
release evidence. Broader follow-up issue creation remains outside this slice.

The implementation is [followup_policy.py](../../examples/readiness/followup_policy.py);
the executable cases are [the focused tests](../../tests/docs/test_readiness_followup_policy_example.py).

## Fixture policy

| Dimension | Illustrative threshold | Ordered severity labels |
|---|---|---|
| context-budget | high | low < medium < high < critical |
| truncation-safety | medium | low < medium < high < critical |

Table: literal fixture policy, supplied explicitly to every call.

A gap meets its fixture threshold when its severity is equal to or above the
listed label. `threshold_met` is informational: both sides produce drafts.
Unknown severities and dimensions without a caller-supplied threshold are errors.
The caller must supply `policy`; there is no default approved policy. No numeric
risk score, probability, severity weighting or release qualification is implied.

## Fixture gaps

| Field | Shared literal value |
|---|---|
| repository | example-repository |
| release | example-release |
| dimension | context-budget |
| surface | adapter-guide |
| summary | Read budget is absent |
| evidence | fixture:missing-budget |
| responsible_role | documentation-maintainer |
| accountable_role | release-maintainer |
| action | Document the intended read budget |
| acceptance | The guide states its intended read budget |

Table: synthetic shared fields; role labels are responsibilities, not identities or authority evidence.

| Case | gap_id | severity | Expected result |
|---|---|---|---|
| A | missing-budget | medium | Draft; threshold not met |
| A repeated unchanged | missing-budget | medium | Same key; collapse into the draft for A |
| B | missing-budget-note | high | Distinct draft; threshold met |
| A with responsible_role absent, null, empty or blank | missing-budget | medium | Reject input |
| A with accountable_role absent, null, empty or blank | missing-budget | medium | Reject input |
| A at critical severity, considered separately | missing-budget | critical | Draft; threshold met |

Table: literal illustrative cases, including below-threshold behavior and missing ownership.

All shared fields plus `gap_id` and `severity` are required. Every field must be
nonempty trimmed single-line text; unknown fields are rejected. Missing evidence,
action, acceptance or either responsibility rejects the entire call. The example
does not resolve roles, verify evidence or authenticate approval. A caller cannot
supply `create_now` or `publication_authorized` as a gap field.

## Duplicate identity and idempotence

The duplicate key is compact JSON containing this ordered array:

```text
["readiness-followup", repository, release, dimension, surface, gap_id]
```

JSON uses unescaped Unicode and no delimiter whitespace. Strings retain exact
case and Unicode spelling; outer whitespace is rejected, not normalized. JSON
escaping keeps delimiters inside fields unambiguous. Callers must assign stable
repository, release, surface and gap identifiers; aliases are not reconciled.

The independently enumerated fixture keys are:

```json
["readiness-followup","example-repository","example-release","context-budget","adapter-guide","missing-budget"]
```

```json
["readiness-followup","example-repository","example-release","context-budget","adapter-guide","missing-budget-note"]
```

| In-memory case | Behavior |
|---|---|
| Identical gaps in the same call | Return a single draft for that key |
| Identical draft already in `existing` | Return no new draft for that key |
| Same identity with changed evidence, severity, responsibilities or other content | Reject conflicting proposals; do not overwrite |
| Different repository, release, dimension, surface or gap_id | Distinct key |
| Existing draft with a forged key, changed content or non-draft status | Reject inconsistent existing metadata |
| Input order changes | Return drafts sorted by duplicate key |

Table: deterministic local duplicate rules.

`existing` contains complete proposal dictionaries previously returned by
`propose`, not issue identifiers or just keys. They are checked against the
current supplied policy. Changed policy that changes a stored draft also rejects
that draft. Conflicts require caller reconciliation; the example does not merge,
update or reopen records. Outputs contain copies of gap metadata and do not mutate
inputs. Feeding returned drafts back as `existing` makes a repeat return an empty
list. No persistence, remote duplicate search, cross-process locking, atomic issue
creation or update idempotence is claimed.

## Proposal minimums

Every returned dictionary contains `duplicate_key`, `status: draft`,
`threshold_met`, `title`, `body` and the complete validated `gap`. The threshold
flag is a JSON boolean; numeric substitutes are rejected in existing proposals.
The title for A
is `Readiness follow-up: Read budget is absent`. Its body is:

```text
Dimension: context-budget
Surface: adapter-guide
Evidence: fixture:missing-budget
Responsible role: documentation-maintainer
Accountable role: release-maintainer
Action: Document the intended read budget
Acceptance: The guide states its intended read budget
```

The identity remains in `gap` and `duplicate_key`; body text is an illustrative
minimum for human review. Role strings and a threshold result grant no authority.

## Publication boundary

| Future case | Example result | Separate authority or work needed before publication |
|---|---|---|
| Below the illustrative threshold | Draft only | Maintainer disposition plus explicit publication authority for the action, destination and content |
| At or above the illustrative threshold | Draft only | Approved real policy, reviewed evidence and explicit publication authority for the action, destination and content |
| Identical existing proposal | No new draft | Any remote lookup or update requires its own implementation and applicable authority |
| Conflicting duplicate or missing responsibility | Rejection | Resolve input conflict or responsibility before reconsideration; publication authority remains separate |
| Request to create immediately | Unsupported | Separately specified creation integration, duplicate protection and explicit publication authority |

Table: literal future-case policy; no row enables create-now behavior.

The example changes neither the canonical contract nor approval authority.
Production gates, model execution, provider configuration, canonical entrypoints
and automated issue creation are outside this example.

## Run offline

From the repository root:

```bash
uv run --no-project python examples/readiness/followup_policy.py
```

The command prints deterministic proposal JSON for A, its unchanged duplicate and
B; the duplicate collapses. There are no network calls, credentials, filesystem
writes or command execution inside the example. The Python runner may resolve its
own environment separately. To repeat the local deduplication operation:

```python
from examples.readiness.followup_policy import FIXTURE_GAP, FIXTURE_POLICY, propose

drafts = propose([FIXTURE_GAP], FIXTURE_POLICY, existing=[])
assert propose([FIXTURE_GAP], FIXTURE_POLICY, existing=drafts) == []
```

Run the focused tests:

```bash
uv run --no-project --with pytest --with pyyaml --with jsonschema python -m pytest tests/docs/test_readiness_followup_policy_example.py -q -rA -p no:cacheprovider
```
