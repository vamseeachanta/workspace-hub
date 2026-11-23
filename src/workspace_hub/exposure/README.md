# Identity exposure library

`expose(record, surface)` projects a validated private registry record into plain
JSON-compatible values. No registry data is distributed with this package.

```python
from src.workspace_hub.exposure import Surface, expose, load_registry

registry = load_registry()  # DATA_REGISTRY_PATH points to a private JSON file
result = expose(registry["V-0107"], Surface.NEWSLETTER)
```

The CLI uses the same policy and checks output against forbidden names, secret
strings and contact strings throughout the loaded registry:

```sh
python -m src.workspace_hub.exposure --id V-0107 --surface newsletter
```

Set `DATA_REGISTRY_PATH` in the caller's environment, or pass `--registry` with the
private file location. There is no default path, directory search or fallback
dataset. Lookup uses an exact ID; name and semantic searches belong to the find
layer. Exit status is 0 for a complete JSON result and 2 for a refusal. Refusals
emit no partial JSON and do not disclose registry contents or filesystem paths.

## Registry contract (version 1)

The JSON envelope contains exactly `schema_version: 1` and `records`, an array of
records. Duplicate JSON keys, duplicate IDs, non-finite numbers and unknown keys
are rejected. Each record contains:

| Key | Meaning |
| --- | --- |
| `id` | Nonempty stable registry identity, such as `V-0107` |
| `client_id` | Optional owning client identity, such as `C-0004` |
| `fields` | Nonempty mapping of snake_case field identifiers to classified values |
| `singling_out` | Assessment with boolean `reviewed` and `combinations` arrays |

Table 1. The record contains identity, classified fields and assessment metadata.

Each field requires `value` (a JSON value) and `exposure_class` (`public`, `client`
or `internal`). Optional `kind` is `data` (default), `name`, `secret` or `contact`.
A `name` field requires a string real value and a nonempty, distinct descriptive
`codename`. A codename is a plain description, with no appended registry ID.
Optional field-level `client_id` overrides record ownership. Unknown exposure
classes or kinds are rejected rather than treated as public.

| Surface | Names | Fields |
| --- | --- | --- |
| `internal` | Real values | All fields, plus record and client IDs |
| `client` | Recipient's real names; others' codenames | Public and recipient-owned client fields |
| `public_website` | Codenames | Public fields |
| `newsletter` | Codenames | Public fields |
| `public_repository` | Codenames | Public fields |

Table 2. Secret and contact fields are excluded from every outward surface.

For a client projection pass `client_id="C-0004"` to the library, or
`--client-id C-0004` to the CLI. A missing recipient refuses the projection.
The caller authenticates the recipient and authorizes internal access; the
function and CLI do not authenticate users or establish access rights.

For a synthetic record with a public name value `Synthetic Hull Zephyr`, codename
`bulk carrier A`, public capacity `25000`, and an internal notes field, the query
above hits `V-0107` and returns:

```json
{"fields": {"name": "bulk carrier A", "capacity": 25000}}
```

The same lookup with `--surface client --client-id C-0004` returns the synthetic
real name when the record belongs to that recipient. Neither outward result
contains the registry ID, ownership metadata, assessment or internal notes.

## Identification refusal and limits

An outward projection requires `singling_out.reviewed` to be true. Each entry in
`combinations` lists field identifiers whose joint presence would identify a
client or asset, including identification through a codename. For example,
`[["region", "capacity"]]` refuses output when both fields survive filtering.
A one-field entry can prohibit an identifying description on its own. A
combination containing a removed field does not refuse. Refusal applies to every
outward surface, including the owning client's surface. Withhold an affected
field to release such a projection; audience-specific assessment exceptions
are not supported by this version.

The assessment is supplied by the private registry's codename review. This
library does not infer anonymity from population statistics, discover new
identifying combinations or assess multiple separately projected records as one
document. An empty combination list is an explicit assessment of no declared
risks, not proof of anonymity. Consumers remain responsible for the combined
document assessment.

Known forbidden strings are checked in field keys and nested values after
Unicode/case/separator normalization. This check cannot detect unknown aliases,
arbitrary encodings or numeric secret values copied into unrelated fields.
The library scans the supplied record; the CLI additionally scans all records
in the configured registry. Report/page builders must perform that wider scan
or an equivalent final-output check when combining records. No builder or
existing public-output guard is migrated by this package.

This version defines the exposure input contract because a private-registry
schema is not bundled in this repository. Registry consumers must validate or
adapt their schema explicitly; unsupported records fail closed.

## Checks

```sh
PYTHONDONTWRITEBYTECODE=1 uv run --no-project --with pytest python -m pytest tests/exposure -q -p no:cacheprovider
```

Tests construct synthetic records in memory and place temporary registry files
under the launch environment's configured temporary directory.
