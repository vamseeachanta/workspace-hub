# Verification evidence composition

The offline checker compares complete **declared** domain data, applicable
settings, byte bindings and an explicit result criterion. It reports content
agreement only. Whole-model readiness remains `NOT_EVALUATED`, including when
all content checks pass. It neither loads a solver nor authenticates execution.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-22 | Added bounded composition checks and negative cases to prevent sub-check promotion. |
| 2 | 2026-10-24 | Preserved decimal evidence in content comparisons to prevent rounding from hiding changed coordinates or out-of-range results. |

## Basis and scope

Issue #3849 (2026) records two counterexamples: a correct loaded
boundary with a wrong complete domain, and an earlier default-settings statement
superseded by modified settings before a result. The checker addresses their
composition pattern, rather than implementing a geometry verifier or parsing
native solver logs. The related parser audit is issue #3847 (2026);
solver-specific corrections remain in the originating engineering repository.

Slice 1 compares the entire supplied domain mapping and frozen source bytes.
Slice 2 selects the governing complete settings snapshot in an ordered history.
Slice 3 applies a sourced result-specific interval, retains all diagnostics and
provides the worked example below. These are standalone, offline checks; no
existing queue consumer is changed or enrolled automatically.

## Inputs and method

Run from the repository root:

```sh
uv run --no-project python scripts/solver/verification_composition.py \
  docs/solver/examples/verification-composition/requirements.json \
  docs/solver/examples/verification-composition/input.txt \
  docs/solver/examples/verification-composition/evidence.json
```

The three arguments are the independently reviewed requirements JSON, the exact
input bytes and an extracted evidence JSON. Keep original evidence immutable;
requirements bind the exact bytes of the extracted record with `evidence_sha256`.
A native adapter must separately retain original artifacts and prove extraction
lineage. Editing or reformatting the evidence requires a new digest and review.

| Check | Required contract | Failure or unknown |
|---|---|---|
| `binding` | Requirements input SHA-256 equals the actual input digest and the evidence input digest; requirements evidence SHA-256 equals the actual evidence digest; evidence kinds agree exactly. | A stale digest or mixed kind fails; absent binding fields are not evaluated. |
| `domain` | Nonempty expected and observed full-domain mappings agree recursively with numeric types preserved. | Every changed, missing or extra field fails; an absent domain is not evaluated. |
| `settings` | Complete nonempty snapshots have unique, strictly increasing nonnegative integer events and source references. The result binds the latest snapshot strictly before its event, whose full settings agree with requirements. | A superseding modification or stale snapshot reference fails; absent history/applicable snapshot is not evaluated. |
| `criterion` | Explicit result identifier, quantity and unit agree. Finite numeric value is inside the supplied inclusive minimum/maximum interval, with a nonempty criterion source. | Wrong labels, inverted bounds and boolean/string values fail; absent bounds or fields are not evaluated. |

Domain mappings must describe the full intended geometry, topology, boundaries,
units and relevant regions for the model family. The checker compares everything
provided, including extra regions and connectivity; it cannot establish that an
adapter actually extracted the entire model. Bounds, area, a pressure resultant
or a loaded-edge subset alone are insufficient descriptors. Ordering of arrays
is significant. Object key order is immaterial. Numeric representations remain
exact: integer and decimal types are distinct; JSON decimal tokens are preserved
through domain, settings and interval comparisons without binary-float rounding.
Equal decimal values such as `2.0` and `2.000` compare equally. No tolerance or
unit conversion is inferred. The existing finite binary-float magnitude range
remains a validation restriction. Direct Python API floats are interpreted using
their round-trip decimal spelling; precision lost before the call cannot be
recovered. Use `read_record` for requirements supplied as JSON bytes. Unknown
completeness requires separate `NOT_EVALUATED` qualification.

Settings snapshots contain **all applicable settings**, not deltas. Never fill
omitted fields from assumed defaults. A snapshot after the result cannot govern
it; a snapshot at the same event is ambiguous and fails. Event order and source
references are adapter assertions requiring independent review against original
artifacts. An omitted contradictory later snapshot cannot be detected from an
incomplete history. A default statement found anywhere in a log is insufficient.

SHA-256 follows [FIPS PUB 180-4 (2015), section 6.2](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf).
Its hexadecimal representation uses 64 digits (256 bits divided by four bits per
hexadecimal digit). Hash agreement establishes byte identity, not authenticity.
JSON rejects duplicate keys at every nesting depth, non-finite numbers and
non-object records. Normalization of native field names belongs in the adapter;
the composition checker never merges aliases or silently replaces duplicates.

For the supplied criterion, `minimum <= value <= maximum`. These limits and their
source are required inputs; no engineering coefficient or acceptance limit is
built in. The overall content status is a conjunction: any `FAIL` yields `FAIL`;
otherwise any `NOT_EVALUATED` yields `NOT_EVALUATED`; otherwise it is `PASS`.
Every sub-check runs even after a failure. A criterion pass alongside a binding
failure is an unbound diagnostic, not reusable evidence.

The JSON report always includes `whole_model_readiness: NOT_EVALUATED` and
`provenance: independently_unverified`. `synthetic` and `native` are retained as
caller declarations, never inferred from file names or promoted by a content
pass. CLI exit codes are zero for content pass, one for failed/incomplete content
and two for invalid/unreadable JSON. Parse errors omit payloads and paths.

## Worked example: inputs, method and answer

The committed [requirements](examples/verification-composition/requirements.json),
[input](examples/verification-composition/input.txt) and
[evidence](examples/verification-composition/evidence.json) are synthetic, not
solver output. Every number below is a constructed test input, not a design limit.
The same independent calculation is written in the test module docstring.

The domain has four nodes `(0,0), (2,0), (2,3), (0,3)` and one cell with connectivity
`[0,1,2,3]`, in arbitrary units. The observed domain is identical. The complete
settings snapshot at event 1 says `shape_check=default`, `limit=specified`.
The result at event 3 references settings event 1. Its result identifier and
quantity are `sum`, unit is `arbitrary`, and value is 5. The explicit synthetic
criterion is `[4,6]` with the independent hand calculation `2 + 3 = 5`.

Method: verify byte digests, compare the full domain, select event 1 as the latest
snapshot before event 3, compare settings, and evaluate `4 <= 5 <= 6`.
Answer: all four content checks and `content_status` are `PASS`;
whole-model readiness is `NOT_EVALUATED` and provenance is independently unverified.
No stress, equilibrium, mesh convergence or engineering acceptance follows.

Negative cases in `tests/solver/test_verification_composition.py` move a domain
boundary, reverse connectivity, add a region, insert modified settings at event 2,
retain a stale settings reference, change artifact bytes, mix evidence kinds and
change result units. These fail their respective checks. Missing evidence stays
not evaluated; physical zero remains valid. The independent interval endpoints
4 and 6 pass; 0 and 7 fail for this particular synthetic criterion.

## Review and later slices

Adversarial design checks require rejecting wrong full-domain descriptors,
superseding settings, stale byte bindings and mixed evidence kinds. The regression
suite exercises these cases without treating any synthetic pass as native proof.
Second-provider code review remains required before merge.

A later, separately scoped adapter must establish extraction completeness,
authoritative settings chronology, original-result provenance, physical quantity
semantics and independent result criteria. Native execution, authorization,
engineering qualification and whole-model readiness remain outside this checker.
