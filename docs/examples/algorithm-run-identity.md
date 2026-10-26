# Offline algorithm run identity example

The [worked module](../../examples/algorithm_runs/identity_example.py) demonstrates
deterministic version and run identities using fabricated data. It is a pure,
non-production example, not a complete run-admission implementation.

The current [contract](../architecture/algorithm-run-dataset-contract.yaml),
particularly `identity.canonicalization`, `identity.algorithm_version_id` and
`identity.run_id`, governs this example. The
[identity plan](../plans/2026-07-11-issue-3428-deterministic-run-identity-contract.md)
explains immutable bindings, opaque input-set injection and the boundary between
execution controls and replay data. Where the older plan describes embedding a
scheme-version field in each object, the current contract specifies the domain
prefix below; this example follows that contract.

## Byte profile

Only plain dictionaries with ASCII string keys, ordered lists, strings and
unitless integers are accepted. String values are normalized to NFC, then encoded
as UTF-8. Keys are sorted and JSON uses compact separators without insignificant
whitespace. ASCII key order agrees with the contract's UTF-16 key order within
this restricted domain. Quotes, backslashes and control characters use JSON
escaping. Lists retain their declared order, including empty lists; empty objects
and empty string values remain explicit.

Booleans, null, floats, non-finite numbers, Decimal values, tuples, sets, bytes,
non-ASCII keys and unsupported types are rejected. Lone Unicode surrogates are
rejected during UTF-8 encoding. Integers are declared dimensionless by the caller;
the example does not infer units, support dimensional quantities or convert units.
It does not implement decimal normalization or claim full JCS conformance.
Integer serialization uses exact decimal digits without a float conversion.
Raw JSON parsing and duplicate-key detection are outside this object-based API.

Each digest hashes these bytes, in order:

```text
UTF8(identity_type + "\n" + "identity-jcs-1" + "\n") + canonical_json_bytes
```

`identity-jcs-1` comes from `identity.canonicalization.version`, not the document's
`contract_version`. `identity_type` is either `algorithm_version_id` or `run_id`.
The result is `sha256:` followed by the lowercase hexadecimal SHA-256 digest.
The digest algorithm, scheme identifier and prefix are specified by the contract;
the full hexadecimal Git revision shape is specified by the identity plan.

## Explicit field selection

| Identity | Selected fields |
| --- | --- |
| Algorithm version | `algorithm_id`, `semantic_version`, `clean_git_commit`, `input_schema_version`, `output_schema_version`, `environment_digest` |
| Run | Derived `algorithm_version_id`, supplied `input_set_id`, `execution_parameters`, explicit `seed` |

The input-set digest is an opaque stand-in for already pinned replay input
membership. This example does not construct input-record or input-set identities.
Execution parameters hold declared run controls; replay data belongs in the input
set, as the plan requires. Missing fields are rejected. An explicit empty controls
object is permitted; an omitted controls object is rejected. The seed is a
unitless integer or the plan's explicit `deterministic:no-seed` sentinel.

Observation timestamps, outputs and other annotations are excluded by selecting
only the listed fields. No broad metadata object is hashed. Extra fields are
ignored, not checked for publication eligibility; a timestamp placed inside
`execution_parameters` would be a declared control and would affect identity.
Output equality is a separate contract concern and cannot change a run identity.

## Synthetic worked fixture and independent oracle

All values below are illustrative choices, not measured engineering constants.
The algorithm is `synthetic:counter`. Semantic, input-schema and output-schema
versions are `1.0.0`. The fabricated revision repeats `a` forty times; the
fabricated environment digest repeats `b` sixty-four times after `sha256:`.
These lengths are the full Git revision and SHA-256 hexadecimal shapes referenced
above; the fabricated values do not assert the existence of a commit or environment.
The input-set stand-in repeats `d` sixty-four times after `sha256:`. Controls are
`{"iterations":3,"label":"café"}` and the seed is `7`; changing them to `4`,
`tea` or `8` respectively provides independent single-field mutation cases.
An observation at `2026-01-01T00:00:00Z` changed to `2026-01-02T00:00:00Z`
provides the observation-only comparison.

The version's canonical JSON is the following single line, encoded as UTF-8:

```json
{"algorithm_id":"synthetic:counter","clean_git_commit":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","environment_digest":"sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","input_schema_version":"1.0.0","output_schema_version":"1.0.0","semantic_version":"1.0.0"}
```

For an independently supplied version-digest stand-in repeating `c` sixty-four
times, the run's canonical JSON is:

```json
{"algorithm_version_id":"sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","execution_parameters":{"iterations":3,"label":"café"},"input_set_id":"sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed":7}
```

The [tests](../../tests/architecture/test_run_identity_example.py) transcribe these
lines as byte literals, including the UTF-8 encoding of `é`, and compare canonical
bytes before hashing. Expected identities use these literal bytes and the literal
prefix directly through the standard hash library, without the serializer under
test. The end-to-end run oracle substitutes the independently calculated version
digest into the literal run bytes. Reordering keys preserves identity; each
selected field is changed independently to demonstrate sensitivity.

Additional synthetic edge fixtures use zero, a negative integer, ordered integers,
`NA`, empty containers and JSON escape characters. Unsupported numeric forms,
an incomplete revision and non-hexadecimal revisions are rejection fixtures.
Alternative version fields use `2.0.0`, `synthetic:other` and repeated `e` pins.
These values are chosen test cases rather than claims about real inputs.

## Offline execution and limits

From the repository root, using an existing Python interpreter:

```sh
python examples/algorithm_runs/identity_example.py
```

The command uses only the standard library, reads no repository or machine state,
accesses no network and prints only the fabricated algorithm-version and run
identities. Importing the module does not execute the example.

Digest and revision syntax checks do not verify that a revision exists, that a
source tree is clean, that a schema is pinned or that an environment is available.
The example does not validate semantic versions, redistribution rights, public
replay access, hidden defaults, failure admission, output equality or publication.
Matching identifiers alone therefore establish neither admission nor eligibility.
No normative contract, production check or real run record is changed.
