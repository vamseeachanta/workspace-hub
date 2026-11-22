# Portability guidance health input contract

The on-demand comparison in `scripts/memory/portability_guidance_health.py`
reports whether portability guidance declares support for an explicit audit
model. Memory size, file age and audit corpus counts cannot establish that
compatibility. The primitive reads supplied evidence and prints a JSON report;
it makes no provider or network call and writes no file.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-26 | Define explicit compatibility evidence to avoid count-based staleness alerts. |

## Explicit inputs

Both input files are UTF-8 JSON objects. The audit evidence declares
`audit_model`; the guidance document declares `supported_audit_model`.
Each model object contains exactly `shape` and `schema_version`. Both values
are nonempty ASCII tokens beginning with a letter or digit, followed by letters,
digits, periods, underscores or hyphens. Versions are opaque strings compared
exactly; there is no version ordering, range, coercion or implicit compatibility.
Changing either field requires a matching guidance support declaration.
For example, changing `schema-a` to `schema-b`, or `event-log` to `message-log`,
requires guidance review until the supported pair matches the new audit pair.

The following examples are synthetic contract fixtures, not observations.
The count example is an independent hand calculation: adding one record to ten
records yields eleven records and leaves both model fields unchanged.

Audit evidence:

```json
{
  "audit_model": {"shape": "event-log", "schema_version": "schema-a"},
  "counts": {"records": 10}
}
```

Guidance document (other fields may carry guidance content):

```json
{
  "supported_audit_model": {
    "shape": "event-log",
    "schema_version": "schema-a"
  },
  "guidance": "Describe the supported portability model here."
}
```

Extra top-level fields are ignored for compatibility. Extra model fields are
unknown evidence because their compatibility meaning has not been defined.
JSON duplicate keys, invalid encoding, malformed JSON, non-finite constants and
non-object documents are invalid evidence. A JSON `null` document is invalid,
distinct from an absent file. Missing model declarations are unknown evidence.
The object API uses `None` to represent absent documents.

`--canonical-locator` is required and is supplied separately from the input file
paths. It names the canonical guidance destination for remediation. It must be a
repository-relative POSIX locator with nonempty slash-separated components made
of ASCII letters, digits, periods, underscores or hyphens. Absolute paths,
backslashes, drive prefixes, query strings, control characters and dot or parent
components are invalid. The primitive never discovers, opens or authenticates
this locator. A supplied guidance file may be a temporary copy; matching evidence
does not prove that the copy is installed at the canonical destination.

Existing unversioned audit exports and Markdown guidance are not implicitly
adapted or migrated. A caller must supply an explicit structured declaration
based on reviewed model evidence. An unversioned export yields unknown evidence;
neither its counts nor its apparent field layout is a substitute for a declared
model. Producing declarations for existing sources remains follow-up work.

## Invocation and output

```bash
uv run --no-project python scripts/memory/portability_guidance_health.py \
  --audit audit-evidence.json --guidance guidance-evidence.json \
  --canonical-locator docs/guides/portability.md
```

The report always contains `status`, `reason_code`, `canonical_locator` and
`diagnostic`. Diagnostics are fixed messages: no input values, input paths,
exception text, timestamps, counts or version strings are echoed. The validated
caller-supplied canonical locator is the sole locator in the output; it is `null`
when invalid. Both current and non-current reports retain a valid locator.

| Condition | Status | Stable reason code |
| --- | --- | --- |
| Exact shape and schema-version match | `current` | `GUIDANCE_CURRENT` |
| Guidance absent | `missing_guidance` | `GUIDANCE_MISSING` |
| Shape or schema version differs | `incompatible_model` | `GUIDANCE_REVIEW_REQUIRED` |
| Invalid canonical locator | `unknown_evidence` | `CANONICAL_LOCATOR_INVALID` |
| Audit absent | `unknown_evidence` | `AUDIT_MISSING` |
| Input cannot be read | `unknown_evidence` | `AUDIT_UNREADABLE` or `GUIDANCE_UNREADABLE` |
| Invalid document | `unknown_evidence` | `AUDIT_DOCUMENT_INVALID` or `GUIDANCE_DOCUMENT_INVALID` |
| Model not declared | `unknown_evidence` | `AUDIT_MODEL_MISSING` or `GUIDANCE_MODEL_MISSING` |
| Invalid model declaration | `unknown_evidence` | `AUDIT_MODEL_INVALID` or `GUIDANCE_MODEL_INVALID` |

Precedence is locator validity, guidance existence/readability/declaration, audit
existence/readability/declaration, then pair comparison. Only the first reason
is reported. A missing guidance document therefore remains actionable even
without audit evidence; a directory or permission error is unreadable evidence,
not missing guidance. Review remediation means checking the guidance content
against the changed model before updating the declaration.

The CLI contract defines exit status `0` for current, `1` for a non-current
report, and `2` for invalid CLI arguments. Argument errors emit the fixed code
`ARGUMENTS_INVALID` to stderr without echoing supplied arguments. Normal reports
are emitted to stdout. These exit codes are contract constants used by the tests.

## Verification and limits

The focused suite is `tests/memory/test_portability_guidance_health.py`:

```bash
uv run --no-project --with pytest python -m pytest \
  tests/memory/test_portability_guidance_health.py -q -rA -p no:cacheprovider
```

Fixtures are synthetic, offline and temporary. They cover count-only refreshes,
shape and schema-version changes, absent and malformed evidence, locator
validation, fixed diagnostics, CLI results and preservation of source bytes and
modification times. Equal synthetic epoch timestamps are used only to demonstrate
that age is irrelevant; they do not enter the compatibility computation.

Current means declared compatibility only. It does not assess guidance quality,
verify declared model truth, authenticate source provenance or establish that
guidance is installed. Scheduled scripts, shared rules, personal memory and real
reports remain unchanged. Scheduler integration and historical migration remain
open. The reusable lesson is to separate compatibility revisions from changing
audit counts and generation timestamps.
