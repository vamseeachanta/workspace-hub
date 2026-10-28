# Corpus evidence coverage audit

The read-only audit reports format observations, missing evidence references and
public-route privacy conflicts in an explicit catalog snapshot. It reads no
source payloads, follows no references and changes no files. Its output contains
fixed format labels and aggregate counts. It supports the knowledge-ingestion
initiative without claiming that a format has a proven extractor.

## Revision history

| Revision | Date | What changed and why |
| --- | --- | --- |
| Initial | 2026-10-22 | Added a synthetic snapshot audit to expose format and evidence gaps before ingestion. |

## Sources and scope

- [Agent data handling contract](../architecture/agent-data-handling-contract.md),
  “Existing authorities and discovery”, “Original retention, rights and
  publication”, and “Descriptor v1 and qualification”: existing catalogs retain
  authority; source identities are preserved; an observation is not permission.
  The existing processing states are preserved exactly.
- [Intelligence operating model](llm-wiki-resource-doc-intelligence-operating-model.md),
  sections “Single-Source-of-Truth Pyramid”, “Allowed Information Flows” and “Forbidden
  Information Flows”: provenance belongs to the registry layer; an audit shall
  not establish a second catalog or reparse raw sources.
- The linked per-format research and ingestion-wave epics of issue #3604 supply
  the format taxonomy and the route vocabulary
  `public_llm_wiki | private_sidecar | metadata_only | excluded_no_ingest`.
  Format labels describe observations, not supported extraction methods.

No engineering equation, empirical coefficient, percentage target, storage
migration trigger or acceptance threshold is introduced. Counts are exact
cardinalities of the supplied rows. The serialization revision is a local
protocol convention. Neither corpus-wide coverage nor computational readiness
can be inferred from these counts.

## Input contract

The JSON root has exactly `schema_version`, `format_families` and `sources`.
The schema revision is `1`. `format_families` is a nonempty, unique list defining
the denominator explicitly; `sources` may be empty. An omitted format is outside
the observation scope, not evidence that the corpus contains no such files.

Supported observation labels are `text`, `markdown`, `html`, `code`, `json`,
`csv`, `spreadsheet`, `pdf`, `scanned_document`, `word`, `presentation`, `email`,
`image`, `cad`, `solver_input`, `solver_output`, `database`, `geospatial`,
`archive`, `media` and `other`. Mixed-format sources require an explicitly chosen
family or upstream decomposition; this tool never inspects file extensions.

Each row contains exactly these fields:

| Field | Contract |
| --- | --- |
| `owner_repo`, `source_id`, `dataset_id` | Existing catalog identities, nonempty strings without surrounding whitespace. No prefix, namespace or normalization is added. The tuple is unique within a snapshot. Different datasets from the same source are allowed. |
| `format_family` | One declared observation label. |
| `route` | One of the four routing values above; supplied by the authoritative upstream process. |
| `privacy` | `public`, `restricted` or `unknown`; a snapshot assertion, never inferred from content or filename. |
| `processing_status` | `gap`, `indexed`, `summarized`, `extracted`, `promoted`, `superseded` or `unreachable`, as in the data handling contract. |
| `evidence` | Exactly `method_ref`, `fidelity_ref`, `citation_ref` and `rights_ref`; each a string or null. Empty or whitespace-only strings are missing evidence. References remain private input and are never resolved or emitted. |

Unknown fields, unknown choices, undeclared formats, duplicate identities,
duplicate JSON keys, nonfinite numbers and malformed UTF-8 are rejected.
The snapshot shall be produced from the existing authoritative catalog in the
appropriate authorized context. No catalog adapter or new allocation registry is
introduced. An upstream exporter shall preserve authoritative identities and
record snapshot vintage separately; this audit does not assess freshness.

## Method and interpretation

`record_count` counts dataset observation rows, not distinct source identities.
For each declared format, the audit counts all rows, processing states, routes,
missing evidence fields and route conflicts. A conflict is a `public_llm_wiki`
route whose privacy is `restricted` or `unknown`. Conflicts appear in the report;
they do not cause a validation error or silently change the supplied route.

A row has **complete evidence references** only when every reference is nonblank,
the processing state is `extracted` or `promoted`, the route is `public_llm_wiki`
or `private_sidecar`, and there is no public-route privacy conflict. This is a
local reporting predicate; it grants no extraction or publication authority.
`metadata_only` and `excluded_no_ingest` rows remain in the denominator and cannot
count as complete. Superseded and unreachable rows cannot count as complete.

The total is the sum of per-format counts; incomplete rows equal total rows
minus complete rows. Missing-evidence counts overlap: one row can lack several
references. A format with no rows is unobserved. A format with any complete row
counts in `formats_with_complete_evidence`, but that does not establish coverage
of its other rows or prove the extraction method.

`qualification` is always `NOT_EVALUATED`. Rights, access, retention, source
fidelity, citation correctness, freshness and intended-use eligibility require
independent live validation against the existing resource descriptor contract.
Aggregate output can itself reveal sensitive corpus sizes; its publication still
requires the applicable authorization. Only synthetic data is supplied here.

## Worked example: inputs, method and answer

The fixture [corpus-readiness.json](../../tests/knowledge/fixtures/corpus-readiness.json)
contains synthetic identities and evidence references. It declares markdown,
CSV and PDF. The expected values come from the following independent hand count,
also written in the test docstring:

| Observation | Method | Answer |
| --- | --- | --- |
| First markdown row | Extracted, public route, public privacy, all references present | Complete references |
| Second markdown row | Summarized, private route, fidelity and citation absent | Incomplete |
| CSV row | Promoted, all references present, restricted privacy on a public route | Incomplete; routing conflict |
| PDF | Declared but no observed row | Unobserved |

Thus the row count is `2 + 1 + 0 = 3`; complete rows are `1`; incomplete rows are
`3 - 1 = 2`; routing conflicts are `1`; unobserved formats are `1`; formats with
complete references are `1`. These are synthetic integer counts, not acceptance
criteria. Qualification is `NOT_EVALUATED`.

Run from the repository root:

```sh
python scripts/knowledge/corpus_readiness.py tests/knowledge/fixtures/corpus-readiness.json
```

The command writes deterministic, sorted JSON to standard output only. A valid
snapshot exits successfully even if gaps or conflicts exist: consumers shall
inspect the counts. Invalid or unreadable input exits with status `2` and a
redacted error. Input paths, source identities, reference strings and underlying
exception text are omitted from audit diagnostics.

Tests run with:

```sh
uv run --no-project --with pytest python -m pytest tests/knowledge/test_corpus_readiness.py -q -rA -p no:cacheprovider
uv run --no-project --with ruff ruff check scripts/knowledge/corpus_readiness.py tests/knowledge/test_corpus_readiness.py --no-cache
```

## Implementation slices and later work

The three delivered slices are strict snapshot validation and format counts;
processing, evidence and privacy-conflict observations; and the aggregate CLI,
synthetic worked example and documentation. Tests include deterministic ordering,
no input mutation, metadata redaction and malformed-input handling.

The broader initiative remains open. Later slices require catalog-owned export
adapters, per-format extraction and fidelity experiments, current rights and
access checks, cited retrieval evaluation, storage measurements and any separately
authorized migrations. This tool performs none of those operations. The existing
wiki ingest command remains unchanged and is not made safe by running this audit.
