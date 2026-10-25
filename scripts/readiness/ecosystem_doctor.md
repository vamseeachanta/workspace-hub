# Ecosystem doctor snapshot adapter

This initial slice for issue #3819 reads an existing repository inventory JSON
snapshot. It does not import or execute the inventory producer or the installation
doctor. Collection, repair, subprocesses, network access and provider tools are
outside this adapter. The broader doctor issue remains open for other adapters.

## Schema

The result schema starts at `schema_version: 1`, defined by this document. A result
contains `status` and an ordered `probes` array. Each probe has exactly `group`,
`status`, `reason_code` and `counts`. Status is `healthy`, `degraded` or
`unavailable`. The fixed group order is repositories, providers, machines,
schedules, skills, memory, privacy and business_outcomes, following the groups
requested in issue #3819. Remaining groups have `adapter_not_implemented`, status
`unavailable` and empty counts. Overall status is always `unavailable` in this
slice, including when repository coverage is healthy. It does not imply whole
system health.

No timestamps, raw errors, paths, identifiers, repository records or arbitrary
input fields are emitted. JSON keys and human count labels are sorted; probe
order is fixed. Rendering introduces no observation time or other variable data.
Both formats carry identical status, reason and aggregate count values.

## Inventory input

Input version `1` and the summary fields come from
`scripts/repositories/work_surface_inventory.py`, function `join_inventory`.
The adapter consumes only the version and summary; repository rows are ignored.
It validates the producer's aggregate claims, not row consistency, provenance,
freshness, configuration membership or current filesystem state. It must not be
used as a live readiness or authorization check. An omitted row list is permitted.

All required counts are nonnegative JSON integers; booleans and floats are
rejected. Zero means no members in that category. The allowlisted output counts
are `declared`, `configured`, `present`, `missing`, `non_git`, `contract_complete`,
`contract_incomplete` and `unexpected_count`. The incomplete count comes from
`summary.adapter_coverage.incomplete`. Unknown summary fields are discarded.

The producer's required equalities are checked:

- declared = present + missing + non_git;
- observed_declared = present;
- unknown = unexpected_count;
- adapter_coverage.complete = contract_complete;
- adapter_coverage.complete + adapter_coverage.incomplete = declared.

Complete contracts cannot exceed present repositories. Configured counts can
exceed declared counts because the producer counts the configuration set
independently. That count alone does not establish correct membership.
A nonempty declared population with no missing, non-Git, incomplete or unexpected
repositories yields `healthy` / `inventory_complete`. Otherwise valid nonempty
coverage yields `degraded` / `inventory_incomplete`. An empty declared population
yields `unavailable` / `inventory_empty` with empty counts.

Unavailable reason codes are stable:

| Code | Meaning |
| --- | --- |
| `snapshot_missing` | No input, missing file, or JSON null |
| `snapshot_unreadable` | File access failed, including a directory input |
| `snapshot_malformed` | Invalid encoding, JSON, shape, count or count relationship |
| `snapshot_unsupported` | Missing or unsupported inventory schema version |
| `inventory_empty` | Valid summary with no declared population |
| `adapter_not_implemented` | No adapter implemented for this group |

Duplicate JSON keys and non-finite JSON constants are rejected. Parse and file
errors never include source text or exception details. No probe is executed, so
there is no timeout observation; a future executing adapter must distinguish
expired probes from missing evidence. Input file size is not bounded here;
consume trusted local snapshots rather than unbounded input streams.

## Invocation and exit status

```sh
python scripts/readiness/ecosystem_doctor.py --inventory inventory.json
python scripts/readiness/ecosystem_doctor.py --inventory inventory.json --json
```

Omitting `--inventory` reports missing evidence. No default discovery occurs.
Exit status is `0` for an overall healthy result, `1` for degraded or unavailable,
and `2` for invalid arguments, following the command's declared exit contract.
Consequently, valid snapshots still exit `1` in this initial slice. Invalid
argument diagnostics are fixed text and do not echo supplied values.

## Verification basis

`tests/readiness/test_ecosystem_doctor.py` uses independent hand tallies: a healthy
population of two present and complete repositories, and an incomplete population
of four declared repositories, comprising two present, one missing and one non-Git,
with one complete contract and one additional undeclared repository. These
examples supply expected counts directly, without running the producer or deriving
expectations from normalization. Tests cover malformed inputs, format agreement,
determinism, allowlisting and unchanged source bytes.
