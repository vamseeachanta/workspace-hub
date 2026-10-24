# Private machine ecosystem maps

The map separates private inventory from public equality metadata. It implements
the collector, private matrix tooling and public pointer requested by
issue #3498, within the
dispatch architecture in issue #3497.
No operational inventory is included in this repository.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Define private records and public metadata so inventory detail stays private. |

## Boundary and destination

Set `MACHINE_MAP_ADMIN_ROOT` to an authorized local clone of the private admin
repository. Inside it, initialize `machine-ecosystem/private.json` with
`{"visibility":"private"}`. This explicit acknowledgement prevents accidental
default output into this public checkout. It does **not** authenticate repository
visibility or authorize publication: maintainers must verify the destination.
The collector rejects overlap with this public checkout and symlinked output
components. Inputs to the command line interface must also be inside the private
`machine-ecosystem/` directory.

The private layout is:

```text
machine-ecosystem/
  private.json
  probes.json
  active.json
  machines/
    <label>.yaml
  matrix.html
```

The tooling requires Python 3.11 or newer, matching the repository runtime.
Records use JSON syntax, which is a YAML subset, so the collector needs only the
Python standard library. Arbitrary YAML syntax is not accepted. Files are written
atomically with restrictive permissions. Input duplicate keys, duplicate names,
unknown record fields and invalid timestamps are rejected. A private directory
must be trusted against concurrent mutation; this is not an adversarial filesystem
sandbox. No Git staging, commits or network publication are performed. Review and
commit private changes in the private repository separately.

## Record contract

Schema version `1` is a protocol tag defined here, not a measurement. Exact fields:

| Field | Contract |
| --- | --- |
| `schema_version` | Integer protocol tag; booleans rejected |
| `machine` | Lowercase alphanumeric label with internal hyphens or underscores |
| `role` | `producer`, `executor`, `portable`, or `other`; explicitly configured |
| `source` | `self-report` or `seeded-manual` |
| `updated_at` | Offset-aware date and time; RFC 3339 format, excluding leap seconds |
| `data_sources` | Unique named rows: `{name, reachable}`; boolean or `not_evaluated` |
| `services` | Unique named rows: `{name, kind, state}` |
| `auth_surfaces` | CLI-presence booleans keyed by `gh`, `claude`, `codex`, `gemini`, `hermes` |

Service kinds are `unit`, `timer`, `cron`, and `agent`. States are `active`,
`inactive`, `failed`, `present`, `absent`, or `not_evaluated`. Inventory names use
the same syntax as labels. Paths, remote addresses, command lines and credential
values are never copied into records. The private names and role remain private.

Data probes call filesystem metadata lookup on explicitly configured absolute
local paths. A visible mounted share can be checked this way; no remote connection
or mount command is attempted. `true` means metadata lookup succeeded, not that
contents are readable, current, licensed or suitable for an application.
Permission and other lookup errors remain `not_evaluated`.

Unit and timer probes query `systemctl is-active`; they never start units. A cron
entry is identified only by its trailing `# machine-map:<configured-target>`
marker on an uncommented line. Crontab contents are discarded. An unavailable
command, unrecognized response or timeout produces `not_evaluated`. Agent probes
check a configured local path; presence does not mean a running process.
Authentication surfaces check executable presence only. Provider programs and
authentication commands are never invoked; login and entitlement are not inferred.
`probe_timeout_seconds` is a required positive finite input, not a built-in limit.
Filesystem metadata lookup itself is subject to operating-system filesystem
behavior and may block on an unresponsive mount.

Example private probe configuration, with paths supplied locally at run time:

```json
{
  "role": "executor",
  "probe_timeout_seconds": 1,
  "data_sources": [],
  "services": [],
  "auth_surfaces": ["gh", "codex"]
}
```

The timeout above is synthetic example input, not an operational recommendation.
A data source row adds `name` and `path`. An agent row adds `name`, `kind: agent`
and `path`. Other service rows add `name`, `kind` and `target`; unit targets are
unit identifiers and cron targets are marker names. There is no shell evaluation.

```bash
bash scripts/readiness/collect-machine-map.sh collect --machine compute \
  --input "$MACHINE_MAP_ADMIN_ROOT/machine-ecosystem/probes.json"
```

For machines unable to self-report, prepare a complete record in the private
inventory directory, with `source: seeded-manual` and its actual assertion time:

```bash
bash scripts/readiness/collect-machine-map.sh seed \
  --input "$MACHINE_MAP_ADMIN_ROOT/machine-ecosystem/seed.json"
```

A seed never probes the target or claims self-report evidence. Identical payloads
ignore a newly supplied timestamp and leave bytes and modification time unchanged;
the original observation time is retained. A changed observation rewrites the
record. Thus freshness measures time since the last **changed inventory**, not
proof of periodic successful collection. A separate heartbeat would be needed to
make that latter claim. Collection order is normalized before comparison.

## Private matrix

Provide the complete active roster as a private JSON array of labels in
`active.json`; it is an input, not inferred from available reports:

```bash
bash scripts/readiness/collect-machine-map.sh build \
  --input "$MACHINE_MAP_ADMIN_ROOT/machine-ecosystem/active.json"
```

This writes `machine-ecosystem/matrix.html` in the same private destination.
Columns cover the union of named data sources and services in valid active
records. Rows retain provenance, role, timestamp and content hash. A missing or
invalid record is `MISSING-EVIDENCE`; an unobserved cell is `not_evaluated`, never
inferred absent. Inactive or unlisted files do not silently expand the roster.
HTML is deterministic and escaped. Do not copy the generated private HTML here.

## Public equality integration

`collect-equality.sh` reads the configured private record and emits exactly:

```json
{"present": false, "updated_at": null, "content_hash": null}
```

For a valid record, `present` is true, the timestamp is retained and `content_hash`
is a lowercase SHA-256 digest of the exact stored bytes. No private file path,
source name, service name, role or authentication surface crosses this boundary.
Missing, unreadable or invalid inventory yields the absent tuple. A record label
must match the requested label. The pointer participates in equality report
change detection. Existing reports without a pointer remain valid but have
`MISSING-EVIDENCE` for this row. The Windows-specific collector is unchanged.

`build-equality-matrix.py` renders `machine_map` as an independent freshness row.
Declare `machine_map_max_age_seconds` in each applicable workstation entry in
`harness-config.yaml`. The limit must be a positive finite number. No default
acceptance limit is supplied because issue #3498 gives none:

- Missing or malformed metadata, or a future timestamp: `MISSING-EVIDENCE`.
- Valid metadata without a valid limit: `NOT_EVALUATED`.
- `age = build_time - updated_at`, in seconds, with `age <= limit`: `MAP-FRESH`.
- Greater age: `MAP-STALE`.

Existing unreachable and stale-checkout precedence still applies. Freshness does
not compare hashes between machines: distinct private records should differ.
A valid pointer is an observation reference, not an authorization or readiness
qualification. The public renderer cannot independently read private bytes.

## Worked example and verification

Run the executable example with an explicitly supplied disposable output directory
outside the public checkout:

```bash
uv run --no-project python examples/readiness/machine_map_example.py \
  --output-dir "$EXAMPLE_OUTPUT_DIR"
```

It creates only synthetic local fixtures: one visible directory, one absent path,
and a manually seeded portable record. The self-report therefore contains
`reachable: true` and `reachable: false`, respectively. The manual row stays
`seeded-manual`; a third requested row remains `MISSING-EVIDENCE`. It writes a
private matrix and prints only a metadata pointer. Repeating the same inventory
preserves its stored bytes.

The freshness test supplies midnight on consecutive dates. Independent hand
calculation: one day is `24 * 60 * 60 = 86400` seconds. A synthetic limit of
`86400` therefore passes at equality; `86399` is stale. These are test inputs and
arithmetic, not operational acceptance values. Tests also cover malformed
pointers, private destination overlap, symlink escapes, exact projection fields,
idempotency, manual seeding and unavailable probes.

Sources for the method:

- Issue #3498, Security posture and Scope (2026): private inventory and exact public field allowlist.
- [RFC 3339 (2002), sections 5.6 and 5.7](https://www.rfc-editor.org/rfc/rfc3339): dated observations with explicit offsets; timestamp subtraction supplies elapsed time.
- [FIPS 180-4 (2015), section 6.2](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf): SHA-256 content identity. A digest has `256 / 4 = 64` hexadecimal digits.

## Remaining private deployment

No real inventory has been collected, seeded or published by this change.
Maintainers must verify the private destination, supply the actual active roster
and probe definitions, review manual assertions, choose freshness limits, and
review and commit private records and the built matrix. Automatic private Git
commits and native Windows collection are not implemented. Independent provider
review remains required before merge; no additional provider was invoked here.
