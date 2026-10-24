# Offline field results audit

The audit checks a local copy of the existing field results projection against
an independently supplied bundle digest and its declared source bytes. It
reports exported coverage without establishing global completeness or permission
to publish. The authoritative field registry remains in the data repository.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Add an offline consistency audit so consumers can detect changed bytes and broken joins before using an export. |

## Scope and sources

This is a bounded contribution to initiative #3602. Its three slices are source
integrity, relational consistency, and a reproducible coverage report with a
worked example. It consumes existing outputs; it does not replace the global
registry, implement a website, collect regional data, or calculate engineering
and economic results.

The inspected upstream revision is
`a814fe13149465d1daeb8a06ca2f024b60a335a1` in `worldenergydata`:

- `scripts/hf_export/build_explorer_results_bundle.py`, `build_bundle()`:
  schema `1.0.0`, projection `field_explorer_results`, source roles and paths,
  raw-byte hashes and sizes, nested tables, provenance, and record counts.
- `packages/worldenergydata-core/src/worldenergydata/common/fields_registry.py`:
  `config/fields.yml` remains the identity authority; aliases are resolved there.
  The consumer creates no alternate mappings and never joins by display name.
- `reports/lower_tertiary/lifecycle/_explorer.json`: detail fields are keyed by
  `id`; wells carry `api` and `field_id`; the optional `wellsCount` is checked
  against the exported well rows when present.
- `reports/field-atlas/_atlas_feed.json`: countries and catalog rows have their
  own identity space. The strict consumer requires unique `catalog_id` values
  and existing country references, without equating these IDs to detail IDs.
- Upstream program issue #939 (2026): `rich`, `sample`, and `roadmap` are the
  declared density tiers. These labels are counted, without requalifying them.
- [Python standard-library hashing documentation](https://docs.python.org/3/library/hashlib.html),
  inspected 2026-10-22: `sha256`, `digest_size`, and `hexdigest`. The implementation
  derives digest width from the library rather than introducing a numeric limit.
- Local [data-handling contract](../architecture/agent-data-handling-contract.md):
  source identity, rights, qualification and publication are separate evidence.

Upstream issue #3559 additionally requires immutable, complete snapshots and
fail-closed joins. This audit supplies local consistency evidence only; it
cannot establish that a remote snapshot was atomically published at a particular
revision. The generic `scripts/hf/save_results_to_hf.py` remains a table publisher
and is unchanged.

## Inputs and method

Run from the repository root, using a local bundle and source root:

```sh
uv run --no-project python scripts/hf/audit_field_explorer.py \
  --bundle "$BUNDLE" --source-root "$SOURCE_ROOT" \
  --expected-sha256 "$EXPECTED_SHA256"
```

The expected digest is lowercase hexadecimal and must come from an independently
trusted record. Computing it
from the same untrusted bundle demonstrates repeatability, not authenticity.
This tool performs no network requests and writes no files.

For each declared source, the method checks exact byte count and SHA-256 equality.
Paths must be normalized relative paths, contain only portable filename
characters, remain under the selected root, and contain no symlink or directory
junction component.
Inputs must be regular files. Concurrent modification of the source directory is
outside the local-input trust model; use an isolated snapshot directory.

The parsed bundle must match the source projections, including values and JSON
types. Duplicate JSON keys, non-finite numbers and invalid encodings fail closed.
Fractional numbers must retain their exact decimal value when parsed and
serialized by the float-based comparator; underflow and excess precision are
rejected with `strict_json`, even when both inputs contain the same value.
Equivalent decimal spellings such as `1.2500` and `1.25` remain supported.
Each detail field's embedded ID must equal its map key. Each well must have a
unique nonempty `api` and one existing `field_id`. Roll-up keys must refer to
detail fields. Atlas catalog IDs and country names must be unique in their
respective tables, and each atlas row must reference a declared country.

Counts are direct enumeration, not an engineering correlation:
`wells_per_field[f] = count(well.field_id == f)`; total counts are table lengths.
The expected values follow from literal input rows in the test docstring.
No engineering coefficient, acceptance tolerance, currency conversion or
physical equation is introduced.

`integrity_status: PASS` means that these local checks passed. Six checks remain
`NOT_EVALUATED`: canonical registry membership, source freshness, redistribution
rights, engineering readiness, economics basis, and global completeness.
Missing evidence is never converted into readiness. Empty tables can be locally
consistent; they provide no evidence of worldwide coverage.

On a data failure the command returns a nonzero exit status and a JSON object
containing only `integrity_status: FAIL` and the violated rule identifier.
Input values, source contents and local paths are not echoed in audit errors.
Successful output contains source IDs as data; consumers remain responsible for
handling and escaping those values. The output is not a browser-safe snapshot
validator or a publication authorization.

## Worked example: inputs, method and answer

The example constructs synthetic rows, writes them to a new directory, and runs
the same audit. Existing output directories are refused to preserve their data.
The digest is computed locally solely for this synthetic demonstration.

```sh
uv run --no-project python examples/field_explorer_audit.py --out "$EXAMPLE_DIR"
```

Inputs: `field_a` and `field_b`; wells `well_x` and `well_y`, both parented to
`field_a`; atlas rows `a` and `b` in country `AA`, and `c` in country `BB`.
Atlas rows declare one `rich`, one `sample`, and one `roadmap` tier. All values
are synthetic labels and row counts, not measured asset properties.

Independent enumeration gives the answer:

| Quantity | Derivation | Expected answer |
| --- | --- | --- |
| Detail fields | a and b | 2 |
| Wells | x and y | 2 |
| Wells per detail field | x and y belong to a; none belong to b | a: 2; b: 0 |
| Zero-well detail fields | b only | 1 |
| Atlas fields | a, b and c | 3 |
| Countries | AA and BB | 2 |
| Atlas density | one row of each declared tier | rich: 1; sample: 1; roadmap: 1 |

The report gives `integrity_status: PASS` and
`eligibility_status: NOT_EVALUATED`. The example saves `detail.json`,
`atlas.json`, `bundle.json`, and `bundle.sha256`; the report goes to standard
output. The test suite independently checks these answers and confirms that
re-running the example does not overwrite its inputs.

## Current upstream observation and later slices

A local bundle built with the inspected upstream exporter and saved source
bytes was rejected at `atlas_identity`: enumeration found 2,032 atlas rows
but 505 repeated-ID rows beyond the first occurrence of each `catalog_id`.
This is evidence of an ambiguous catalog identity for this strict consumer,
not a claim that every repeated row represents a distinct field. Resolving
catalog identity and registry federation belongs in the authoritative data
repository; the consumer does not deduplicate or invent replacements.

Later work remains regional ingest, cite-or-null play backfill, canonical
registry federation, immutable publisher/readback, site selectors and panels,
lifecycle/architecture/cost planes, and qualified commercial/engineering feeds.
These span other repositories and are not completed by this audit. The linked
hub issue #1842 could not be resolved through the issue API during discovery.
Independent provider review remains required before merge.
