# Weekly review run artifact format

The [schema](../../config/reporting/weekly-review-run.schema.json) defines one
weekly review artifact at version `1.0.0`. It covers structure and declared
observations. Validator tooling, canonical output locations, history, report
generation, integration and publication authority remain outside this slice.

## Revision history

| Revision | Date | What changed and why |
| --- | --- | --- |
| Initial | 2026-10-26 | Defined the standalone contract and synthetic examples for consumers. |
| Editorial | 2026-10-27 | Added Plan-lite scope, acceptance criteria and validation commands to make the structural boundary explicit. |

## Plan-lite

The standalone slice will cover three paths:

- `config/reporting/weekly-review-run.schema.json` will define the versioned
  structural contract.
- `docs/examples/weekly-review-run-format.md` will document the contract,
  synthetic examples, compatibility and consumer responsibilities.
- `tests/reporting/test_weekly_review_run_schema.py` will exercise independent
  literal vectors and the documented example validator.

Structural acceptance will require the exact version `1.0.0`, closed objects,
required fields, declared types and enums, nonblank text, RFC3339 timestamps
with format assertions enabled, and rejection of identical duplicate records.
The examples will include valid minimal and degraded artifacts and targeted
invalid version and status cases. Evidence integrity, timestamp ordering,
identifier uniqueness, reference resolution and publication permission will
remain consumer responsibilities.

Validation will run from the repository root with cached dependencies; temporary
test output will use separate scratch directories through `--basetemp`:

```bash
uv run --offline --no-project --with pytest --with pyyaml --with 'jsonschema[format-nongpl]' python -m pytest tests/reporting/test_weekly_review_run_schema.py -q -rA -p no:cacheprovider --basetemp="$TMPDIR/weekly-review-focused"
uv run --offline --no-project --with pytest --with pyyaml --with 'jsonschema[format-nongpl]' python -m pytest tests/analysis/test_readiness_bundle_schema.py -q -rA -p no:cacheprovider --basetemp="$TMPDIR/weekly-review-readiness"
uv run --offline --no-project python scripts/enforcement/check-engineering-register.py docs/examples/weekly-review-run-format.md
bash scripts/enforcement/check-model-id-sourcing.sh config/reporting/weekly-review-run.schema.json
git diff --check
```

## Contract and numeric basis

The JSON Schema dialect is Draft 7, following the existing
[readiness evidence schema](../modules/ai/readiness-evidence-bundle.schema.yaml).
The initial version `1.0.0`, exact version equality and a minimum text length of
one character are choices of this contract, rather than measured quantities.
Text must also contain a non-whitespace character. All dates, fractional seconds,
offsets, versions and numeric values in the examples and
[tests](../../tests/reporting/test_weekly_review_run_schema.py) are synthetic
contract vectors. Invalid versions `2.0.0`, `1.0.1`, `1.0` and numeric `1` exercise
exact matching; numeric `0` and booleans exercise type rejection. Empty strings,
whitespace, nulls, empty arrays and objects exercise missing-content/type bounds.
The impossible February date, invalid hour, date-only and timezone-free timestamps
exercise RFC3339 format rejection. No value represents an infrastructure observation.

Every object rejects undeclared keys. Required fields cannot be null. Every
reference, identifier, summary, recommendation and provenance value is nonblank
text. References are opaque locators: schema validation does not resolve them or
assert URI syntax. They may identify authorized evidence without copying it.

| Section | Required fields | Optional fields | Types and allowed values |
| --- | --- | --- | --- |
| Root | `schema_version`, `metadata`, `readiness`, `settings_routing`, `freshness`, `accessibility`, `findings` | `follow_on_refs` | Version is the string `1.0.0`; sections are objects, findings and follow-on references are arrays. |
| `metadata` | `run_id`, `period_start`, `period_end`, `generated_at`, `provenance` | none | Identifier is text; timestamps are RFC3339 date-time strings with a timezone, accepting fractions and offsets; provenance is an object. |
| `metadata.provenance` | `source_ref`, `source_revision`, `producer` | none | Text locating the source, its revision and the producing tool or format. No personal identity is required. |
| `readiness` | `status` | `evidence_refs` | Status: `ready`, `degraded`, `blocked`, `unknown`. |
| `settings_routing` | `status`, `baseline_ref` | `evidence_refs` | Status: `consistent`, `drifted`, `unknown`; baseline reference is text. |
| `freshness` | `status`, `criteria_ref` | `evidence_refs` | Status: `current`, `stale`, `unknown`; criterion reference is text. |
| `accessibility` | `status` | `evidence_refs` | Status: `accessible`, `partial`, `inaccessible`, `unknown`. |
| Each finding | `id`, `category`, `severity`, `summary` | `recommendation`, `evidence_refs` | Identifier and summary are text. Category: `readiness`, `settings_routing`, `freshness`, `accessibility`. Severity: `info`, `warning`, `critical`. Recommendation is text. |
| Each follow-on reference | `finding_id`, `kind`, `ref` | none | Identifier and reference are text; kind: `issue`, `artifact`. |

All arrays may be empty. Evidence arrays contain unique nonblank strings. Findings
and follow-on arrays contain objects and reject identical duplicate records.
Omitting an evidence array means no evidence references were recorded; an empty
array explicitly records no references. Neither establishes that a review occurred.
Omitting `follow_on_refs` means no follow-on references were recorded. An empty
`findings` array records no findings; it does not imply readiness. Use `unknown`
when a status has not been established.

The readiness status summarizes externally owned evidence. Canonical check IDs,
probe definitions and evidence rules remain in the readiness schema and its
[validator](../../scripts/analysis/readiness_bundle_schema.py); this contract
neither embeds their payloads nor defines another check catalogue. Settings and
freshness reference their applicable baseline and criteria rather than hardcoding
routing choices or staleness thresholds.

## Consumer responsibilities and limits

Validation requires the declared dialect and enabled RFC3339 format assertions
(for example `FormatChecker` in the command below). It does not establish source
revision integrity, reference resolution, access rights, current readiness or
publication permission. Consumers must check timestamp ordering and period
coverage, unique finding IDs, follow-on `finding_id` resolution, and agreement
between summaries, findings and evidence. Identical-object uniqueness alone does
not enforce identifier uniqueness. Parsing duplicate JSON keys, authorization,
redaction and publication remain consumer responsibilities. Synthetic locators
below intentionally do not resolve. No network request is needed to validate them.

## Compatibility and evolution

Consumers select a supported schema by exact `schema_version` before validation;
unknown versions are rejected. The schema identifier is version-specific. This
file currently contains only the initial contract. Supporting a later version
requires preserving a retrievable copy of every supported released schema.

Adding an optional field without changing any existing meaning or accepted value
is additive and merits a minor version. Removing or renaming a field, making an
optional field required, changing a type, narrowing accepted values, adding an
enum member that an older reader cannot interpret, or changing a field's meaning
is breaking and merits a major version. Editorial corrections that leave the
accepted instances and meanings unchanged merit a patch version. Version examples
in the tests deliberately reject unselected versions even when the change would
otherwise be additive.

Because objects are closed and versions are exact, old readers reject newer
versions, including additive revisions. Additive means existing payload structure
can be retained with the new version after consumer support is added; it does not
promise old-reader forward compatibility. Preserve released contracts and add
migration examples and tests with any successor. This slice adds no migration or
version-dispatch implementation.

## Minimal valid synthetic artifact

```json
{
  "schema_version": "1.0.0",
  "metadata": {
    "run_id": "synthetic-weekly-review",
    "period_start": "2026-10-12T00:00:00Z",
    "period_end": "2026-10-19T00:00:00Z",
    "generated_at": "2026-10-19T00:00:00Z",
    "provenance": {
      "source_ref": "synthetic:review-input",
      "source_revision": "synthetic-revision",
      "producer": "synthetic-fixture"
    }
  },
  "readiness": {
    "status": "unknown"
  },
  "settings_routing": {
    "status": "unknown",
    "baseline_ref": "synthetic:settings-baseline"
  },
  "freshness": {
    "status": "unknown",
    "criteria_ref": "synthetic:freshness-policy"
  },
  "accessibility": {
    "status": "unknown"
  },
  "findings": []
}
```

## Valid synthetic artifact with degradation and follow-on reference

```json
{
  "schema_version": "1.0.0",
  "metadata": {
    "run_id": "synthetic-weekly-review",
    "period_start": "2026-10-12T00:00:00Z",
    "period_end": "2026-10-19T00:00:00Z",
    "generated_at": "2026-10-19T00:00:00Z",
    "provenance": {
      "source_ref": "synthetic:review-input",
      "source_revision": "synthetic-revision",
      "producer": "synthetic-fixture"
    }
  },
  "readiness": {
    "status": "degraded",
    "evidence_refs": [
      "synthetic:evidence"
    ]
  },
  "settings_routing": {
    "status": "drifted",
    "baseline_ref": "synthetic:settings-baseline",
    "evidence_refs": [
      "synthetic:evidence"
    ]
  },
  "freshness": {
    "status": "stale",
    "criteria_ref": "synthetic:freshness-policy",
    "evidence_refs": [
      "synthetic:evidence"
    ]
  },
  "accessibility": {
    "status": "partial",
    "evidence_refs": [
      "synthetic:evidence"
    ]
  },
  "findings": [
    {
      "id": "finding-alpha",
      "category": "accessibility",
      "severity": "warning",
      "summary": "Synthetic reference is unavailable.",
      "recommendation": "Inspect the synthetic reference.",
      "evidence_refs": [
        "synthetic:evidence"
      ]
    }
  ],
  "follow_on_refs": [
    {
      "finding_id": "finding-alpha",
      "kind": "issue",
      "ref": "synthetic:follow-on-issue"
    }
  ]
}
```

## Invalid synthetic artifact: unsupported version

Only the version differs from the minimal valid artifact.

```json
{
  "schema_version": "2.0.0",
  "metadata": {
    "run_id": "synthetic-weekly-review",
    "period_start": "2026-10-12T00:00:00Z",
    "period_end": "2026-10-19T00:00:00Z",
    "generated_at": "2026-10-19T00:00:00Z",
    "provenance": {
      "source_ref": "synthetic:review-input",
      "source_revision": "synthetic-revision",
      "producer": "synthetic-fixture"
    }
  },
  "readiness": {
    "status": "unknown"
  },
  "settings_routing": {
    "status": "unknown",
    "baseline_ref": "synthetic:settings-baseline"
  },
  "freshness": {
    "status": "unknown",
    "criteria_ref": "synthetic:freshness-policy"
  },
  "accessibility": {
    "status": "unknown"
  },
  "findings": []
}
```

## Invalid synthetic artifact: unsupported readiness status

Only the readiness status differs from the minimal valid artifact.

```json
{
  "schema_version": "1.0.0",
  "metadata": {
    "run_id": "synthetic-weekly-review",
    "period_start": "2026-10-12T00:00:00Z",
    "period_end": "2026-10-19T00:00:00Z",
    "generated_at": "2026-10-19T00:00:00Z",
    "provenance": {
      "source_ref": "synthetic:review-input",
      "source_revision": "synthetic-revision",
      "producer": "synthetic-fixture"
    }
  },
  "readiness": {
    "status": "unsupported"
  },
  "settings_routing": {
    "status": "unknown",
    "baseline_ref": "synthetic:settings-baseline"
  },
  "freshness": {
    "status": "unknown",
    "criteria_ref": "synthetic:freshness-policy"
  },
  "accessibility": {
    "status": "unknown"
  },
  "findings": []
}
```

## Offline example validation

From the repository root, run the command below with locally installed/cached
`jsonschema` format dependencies. Dependency resolution may need a network connection on first use;
validation itself uses only local files and the library's bundled Draft 7 schema.
The optional format dependencies are required: plain `jsonschema` can silently
ignore `date-time`. The command explicitly checks that support is present.
It validates both positive examples and checks rejection of both targeted invalid
examples. It introduces no validator CLI or integration.

```bash
uv run --offline --no-project --with 'jsonschema[format-nongpl]' python - <<'PY'
import json
from pathlib import Path
import re

from jsonschema import Draft7Validator, FormatChecker
from jsonschema.validators import validator_for

schema = json.loads(Path("config/reporting/weekly-review-run.schema.json").read_text(encoding="utf-8"))
assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
validator_class = validator_for(schema)
assert validator_class is Draft7Validator
validator_class.check_schema(schema)
checker = FormatChecker()
assert "date-time" in checker.checkers, "Date-time format support is required"
validator = validator_class(schema, format_checker=checker)
text = Path("docs/examples/weekly-review-run-format.md").read_text(encoding="utf-8")
blocks = re.findall(r"```json\n(.*?)\n```", text, re.S)
minimal, degraded, invalid_version, invalid_status = map(json.loads, blocks)
validator.validate(minimal)
validator.validate(degraded)
assert not validator.is_valid(invalid_version)
assert not validator.is_valid(invalid_status)
print("Synthetic examples: valid and invalid cases verified.")
PY
```
