# Explicit integer bounds before canonical JSON

## Summary

Integer validation must establish the application domain before decimal JSON
encoding or hashing. A generic `ValueError` assertion can pass because the
interpreter rejected conversion, while the application has no effective bound
when that interpreter guard is disabled. The bounded discovery for issue #3840
confirmed this ordering gap in the rule-authority codec. Its existing unsigned
generation ceiling now supplies a pre-encoding and parse-token safety bound.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Record the bounded inventory, codec correction and guard-independent regression pattern. |

## Bounded discovery

The inventory covers the following reusable entry points and their direct tests.
It is a source inspection, not an assertion of repository-wide coverage. The issue
contains no linked issues. Search scope and terms:

```sh
rg -n 'canonical_bytes|json.dumps|sha256|type\(.*int|isinstance\(.*int' \
  scripts/governance/workflow_receipt.py \
  scripts/governance/publication_eligibility.py \
  scripts/legal/rule_authority/codec.py \
  scripts/legal/rule_authority/authority.py \
  scripts/legal/verify_rule_authority_genesis_approval.py \
  scripts/operations/storage/repository_size_guard.py
rg -n 'raises\(ValueError|AuthorityError|int_max_str_digits' \
  tests/governance/test_workflow_receipt.py \
  tests/governance/test_publication_eligibility.py \
  scripts/legal/tests/test_rule_authority_codec.py \
  scripts/legal/tests/test_rule_authority_genesis_approval.py \
  tests/operations/storage/test_repository_size_guard.py
```

| Entry point | Observed validation and test boundary | Disposition |
| --- | --- | --- |
| `rule_authority.codec.canonical_bytes`, `parse_canonical` | Field validators already bound generations, but only after canonical encoding. Old tests checked `AuthorityError` without disabling the interpreter guard or proving validation order. | Confirmed local defect tracked by #3840; corrected in this change. |
| `rule_authority.authority._sha`, `build_manifest`, ledger helpers | Hashing and sealing consume codec bytes. An excessive integer could reach decimal encoding first. | Covered by the codec correction and a test that forbids hashing invalid input. |
| `workflow_receipt.canonical_bytes`, `load_json` | Traversal, depth, node and encoded-byte limits exist; integer magnitude is not a declared domain criterion. Generic `ValueError` tests concern those separate limits. | No domain defect established. An integer ceiling requires a consumer contract; no new ceiling is inferred. |
| `publication_eligibility.bundle_digest`, `load_json` | Payload integers remain exact; decimal round-trip checks concern floats. No payload integer ceiling is declared. | No domain defect established; preserve caller payload semantics. |
| `verify_rule_authority_genesis_approval.parse_canonical_approval` | Typed fields and byte limits reject malformed approvals; generic `ValueError` assertions do not prove integer validation order. | Integer-specific hardening needs separate bounded review; no new limit is inferred here. |
| `repository_size_guard.load_policy`, `evaluate` | Byte budgets are required inputs, not fixed domain maxima. The parsing-resource test explicitly exercises interpreter exhaustion and skips when its guard is disabled. | Interpreter-resource test, not evidence of an application integer bound. No fixed storage cap is inferred. |

Only the confirmed local defect is changed. No external owning repository was
found in this bounded scope. Additional issue creation and external review remain
with the maintainers; there is no claim that uninspected tooling is defect-free.

## Method and source basis

The repository's [normative rule-authority contract](../plans/evidence/2026-07-13-issue-3522-rule-authority-contract.md),
sections 1 and 2 (2026), specifies unsigned 64-bit generations and smaller caps
for other integer fields. Hence the largest permitted integer magnitude in an
authority document is:

```text
M = sum(2**k, k = 0 through 63) = 2**64 - 1 = 18446744073709551615
```

The codec checks `-M <= value <= M` for integer leaves, including integer object
keys that Python JSON can coerce to strings. This is a wire safety ceiling, not
full schema validation. Negative values and zero remain invalid generations;
Booleans remain invalid integer fields. Existing field-specific validators retain
their narrower limits. Generic serializers outside this closed contract must not
inherit this ceiling without their own domain basis.

The preflight traverses dictionaries, lists and tuples before encoding. Repeated
containers are visited once; JSON still rejects actual cycles. Accepted values
retain the same ordering, escaping, separators and trailing newline.

For raw JSON, reject an integer token whose decimal magnitude has more digits
than `M` before calling `int`. For equal-width tokens, convert the short token
and compare its value with `M`; width alone cannot distinguish `M` from `M + 1`.
Neither path depends on the configurable interpreter digit guard. Errors use the
existing `AuthorityError("schema")` without embedding input values.

[Python 3.11, Integer string conversion length limitation](https://docs.python.org/3.11/library/stdtypes.html#integer-string-conversion-length-limitation)
describes the interpreter safeguard and its configuration. Setting the limit to
zero disables it. [Python 3.11, `sys.int_info`](https://docs.python.org/3.11/library/sys.html#sys.int_info)
provides the default and minimum limits; tests read the default rather than
assuming a particular configured digit count. Neither runtime limit defines an
application's acceptance criterion.

## Worked example

Input at the boundary:

```python
value = {"generation": 18446744073709551615}
expected = b'{"generation":18446744073709551615}\n'
```

Method: the geometric sum above gives `M`; the input equals `M`, so the safety
check accepts it. The generation field also satisfies its positive-integer domain.
Canonical encoding returns exactly `expected`. The existing SHA-256 algorithm
receives these unchanged bytes; tests compare the codec digest with SHA-256 of
the independently written byte literal.

Input just outside the boundary:

```python
value = {"generation": 18446744073709551616}
```

Method: subtracting `M` gives one, so the input exceeds the domain ceiling. Answer:
`AuthorityError("schema")` before JSON encoding or hashing. The same result holds
for a raw JSON token at that value and for its negative counterpart. These
expected outcomes come from integer arithmetic, not from the implementation.

## Regression pattern

- Test the largest valid value and the adjacent invalid value from the cited
  application contract. Include wrong types, signs and nested containers.
- Require the application exception class and exact error category. A generic
  `ValueError` assertion alone cannot distinguish interpreter conversion failure.
- Exercise the interpreter's default guard and disabled guard. Save and restore
  the prior setting in `finally`, including when the test fails. These tests run
  serially within their process because the setting is process-wide.
- Construct hostile input as a digit string or with integer exponentiation;
  avoid converting it to decimal while constructing test parameters or IDs.
- For pre-encoding rejection, replace the encoder with a failing sentinel.
  For hash rejection, replace the hash constructor with a failing sentinel.
- Preserve a literal valid byte vector. Do not calculate expected boundaries,
  serialization bytes or rejection categories using the function under test.

The executable example is
[`test_rule_authority_integer_bounds.py`](../../scripts/legal/tests/test_rule_authority_integer_bounds.py).
Existing authority codec and manifest golden vectors supply compatibility checks.

## Limits and follow-up

The correction does not introduce depth, node or total-size policy for in-memory
codec inputs. It does not claim general denial-of-service protection or change
floating-point handling. Wider discovery and consumers with no documented
integer domain require separate specifications. Independent provider review
remains required before merge.
