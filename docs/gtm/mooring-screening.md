# Demo 6 supplied-envelope screening

## Summary

The first slice compares supplied maximum line tension and radial offset with
referenced, supplied allowable values. It records arithmetic comparisons for
review and makes no physical response or design-acceptance claim. It does not
produce the parametric run requested by issue #2115.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-19 | Define an evidence-preserving scalar input boundary before physical analysis is available. |

## Scope and sources

- Issue #2115 defines the requested tension, offset and fatigue screening.
- `docs/gtm/capability-map.md`, Mooring Design, records the existing capability
  and demo gap.
- `scripts/animations/mooring_math.py`, `max_utilisation`, already reports
  tension divided by minimum breaking load for visualisation. This slice does
  not import that module or reuse its illustrative physical assumptions.
- `docs/field-development/mooring-preliminary-inventory.md` identifies unresolved
  factor provenance and duplicate property libraries. No material properties,
  standard factors or solver response approximations are copied from them.

DNV-OS-E301 and API RP 2SK are requested future qualification bases, not implemented
criteria. No qualified edition or clause is selected here. The public report
*The IEA Wind Task 49 Reference Floating Wind Array Design Basis* (2024),
<https://www.nrel.gov/docs/fy24osti/89709.pdf>, could not be retrieved during
preparation. No equation or value is attributed to its unread contents.

There are no physical equations, empirical coefficients or numerical code
acceptance limits in this slice. The comparisons are definitions of this input
contract: supplied demand less than or equal to supplied limit means
`WITHIN_SUPPLIED_LIMIT`; greater demand means `EXCEEDS_SUPPLIED_LIMIT`. Equality
is included without rounding or tolerance. These definitions do not reproduce a
standard clause. Zero is the mathematical lower bound of magnitude inputs;
allowable inputs must be strictly positive. Both units and sign conventions are
part of the contract below, not inferred from a solver.

## Input contract

`scripts/gtm/demo_06_mooring_screening.py` reads a JSON object containing only a
nonempty `cases` array. Each case has these fields:

| Field | Meaning |
|---|---|
| `case_id` | Required, unique, nonblank string identifying an envelope and condition. |
| `response_source` | Reference identifying the supplied response evidence and its units, condition and maximum-extraction method. |
| `max_tension_kn` | Nonnegative finite total maximum line tension magnitude in kN. |
| `allowable_tension_kn` | Positive finite allowable tension in kN, derived outside this script. |
| `tension_limit_source` | Limit derivation reference: document title, edition, clause or table, condition, applicable factors and strength basis. |
| `max_offset_m` | Nonnegative finite maximum radial horizontal displacement in m from the declared reference position. |
| `allowable_offset_m` | Positive finite radial displacement allowance in m, established outside this script. |
| `offset_limit_source` | Allowance reference: document title, revision, criterion and reference position. |

References are caller assertions retained verbatim for review; this script does
not open, authenticate or qualify them. Keep references suitable for the intended
audience. Do not supply private locators or confidential response data to a public
record. A response record should identify the upstream revision, content digest
and extraction method so a later analysis can reproduce its envelopes.

All fields except `case_id` may be omitted or null. A comparison requires its
demand, allowance, limit reference and `response_source`. Missing evidence yields
`NOT_EVALUATED`, with the missing field names. Missing offset evidence does not
prevent a complete tension comparison, or vice versa. Empty strings, booleans,
nonfinite values, negative magnitudes, zero allowances, unknown fields, duplicate
case identities and duplicate JSON keys are errors. Numeric strings are rejected.
Malformed input rejects the entire batch before any result is written.

Supply a total maximum envelope for the applicable line and condition, not a
mean or a tension component. Use separate cases for separately governed lines
or conditions. Minimum breaking load alone must not be used as allowable tension:
factor and condition selection require external engineering qualification. The
script does not know whether a claimed envelope covers the governing case.

## Running and interpreting the record

```sh
python scripts/gtm/demo_06_mooring_screening.py envelopes.json > record.json
```

The standard-library script writes a deterministic JSON record with the original
input fields, separate tension and offset statuses, and explanatory reasons.
Identical input yields byte-identical output; case order is preserved and no
timestamp or local path is added automatically. No file is written by the script.

Fatigue, DNV-OS-E301 compliance and API RP 2SK compliance are always
`NOT_EVALUATED`. No overall pass is emitted. A `WITHIN_SUPPLIED_LIMIT` result is
only a comparison against a caller assertion, never a standards-compliance or
whole-system conclusion. A successful command exit means that a record was
produced; it can contain exceedances and unevaluated checks. Invalid input yields
a nonzero exit and a diagnostic without echoing input contents or local paths.

## Verification basis

`scripts/gtm/tests/test_demo_06_mooring_screening.py` uses independent hand
comparisons documented in its fixture and test docstrings. For example, the
invented tension demand is 120 kN against an invented 150 kN limit and the
invented radial offset is 6 m against an invented 8 m limit: both demands are
strictly less than their respective limits. Equality and exceedance examples
are written out separately. These values test arithmetic only; they are not
published response values, material properties or engineering acceptance limits.

Tests also exercise missing evidence, malformed magnitudes and references,
duplicate identities and JSON keys, case independence, deterministic CLI output
and error handling. No test starts, imports or queries a licensed solver.

## Later slices

- Qualify the standards editions, conditions, line-strength basis and allowable
  derivations, with clause-level citations and independently checked examples.
- Connect qualified response extraction and a reproducible parametric matrix to
  the existing engineering modules. Keep load generation outside this adapter.
- Add fatigue only with cycle/exposure evidence, a qualified fatigue curve and
  an applicable acceptance criterion.
- Produce a computed run record and draft website integration with website
  tests. The current scalar record cannot replace that deliverable.
