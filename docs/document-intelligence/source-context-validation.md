# Source context validation

## Summary

The REST document fetcher uses one side-effect-free validator for offline status,
URL construction and execution. A syntactically valid source context does not
establish network availability, authorization, endpoint support or response quality.
This implements the hub REST integration for issue #3445. It does not modify the
sibling package where the defect class was first reported.

## Revision history

| Revision | Date | What changed and why |
|---|---|---|
| Initial | 2026-10-22 | Shared syntax validation and deferred I/O status prevent false readiness. |

## Inventory and scope

| Surface | Existing behavior | Contract disposition |
|---|---|---|
| `scripts/data/doc_intelligence/fetch_from_api.py:get_api_registry` and `--list-sources` | Lists configured sources and example endpoints. | Configuration metadata only; no readiness claim. Returned nested metadata is copied so callers cannot mutate validation authority. |
| `build_api_url` | Checks source membership; endpoint and query types were not checked consistently. | Calls `validate_source_context` before URL construction. |
| `fetch_api_data` | Duplicated source membership, then read credentials and called the URL builder. | Calls the same validator before credential access or fetching. |
| Fetcher CLI, single and paginated requests | Required nonempty flags; malformed query members could be silently discarded. | Rejects malformed query members and calls the same validator before either request path. |
| Fetcher `source_status` and `--status` | No offline source preflight existed. | Added shared validation with explicit deferred I/O; no environment, filesystem or network reads. |
| `scripts/governance/workflow_receipt.py:validate_resource` | Validates descriptor schema, current supplied context and eligibility. | Already a shared pure resource validator; supplied access claims still need live validation. No changes. |
| `scripts/client_llm_wiki/bootstrap_contract_cli.py` | Classification and execution load the same bootstrap registry schema. | Separate disabled-ingestion contract; classification does not establish source access. No changes. |
| `scripts/data/drive-index-search/staleness.py` | Reports index age and prior refresh state. | Freshness observation only; no request syntax or execution readiness claim. No changes. |
| `scripts/readiness/provider_harness_parity.py` | Inspects installed runtime and configuration surfaces. | Runtime observations, not REST source request validation. No changes. |

The repository contains no pre-existing `requirements_satisfied` or `routable_now`
fields. The linked defect in the Landman package is sibling context, not evidence
that the same provider implementation exists in this repository. The inventory
covers the source-context and readiness surfaces inspected for this integration;
it does not establish parity for every consumer in other repositories.

## Pure contract

`validate_source_context(source, endpoint, params=None, api_key=None)` raises
`SourceContextError` with a fixed `code` and no supplied input in its message.
It does not read environment variables, open files, resolve DNS or make requests.

- The source must be an exact registry identifier; other values yield `UNKNOWN_SOURCE`.
- The endpoint must contain literal ASCII path segments made from letters, digits,
  underscores, hyphens or dots, separated by slashes. A single leading slash is
  accepted for existing callers. Empty segments, dot segments, URL authorities,
  query strings, fragments, percent escapes, backslashes and controls yield
  `INVALID_ENDPOINT`. Registry endpoint lists remain examples, not allowlists.
- Parameters must be absent or a dictionary with printable, nonblank string keys
  and printable strings, integers, booleans or finite floats as values. Empty
  string values are permitted. Nested containers, null values and values the
  runtime query encoder cannot represent yield `INVALID_PARAMS`.
- An explicitly supplied API key must be absent or printable, nonblank text;
  otherwise the code is `INVALID_API_KEY`. Status can validate a supplied key's
  syntax without reading credentials. It never returns the key or request URL.

The endpoint grammar is an application input contract, not a statement that all
valid HTTP endpoint paths use this subset. More expressive endpoints require a
reviewed contract extension. Existing query values continue to use `urlencode`.
These are software syntax rules; no physical coefficients or engineering
acceptance limits are introduced.

## Status and I/O boundary

Let `S` mean the shared source syntax/type validator passes. Status applies:

```text
requirements_satisfied = S
routable_now = false
io_validation = NOT_EVALUATED
```

These Boolean rules follow issue #3445's requirement to distinguish syntax from
deferred I/O. `requirements_satisfied` refers only to the documented syntax/type
preconditions; consumers must inspect `io_validation` before treating the context
as ready for external use. Failure reports the validator's exact reason code;
syntax success reports `IO_VALIDATION_DEFERRED`.

Execution resolves an environment-provided key after syntax validation and passes
it through the same validator during URL construction. Key presence, server-side
credential acceptance, connectivity, response parsing and output persistence are
execution-time checks. Status does not perform them. A successful fetch does not
establish freshness, data suitability, source rights or permission to publish.
A server failure propagates as an execution failure; an offline status observation
is never promoted to a successful network check. No status result is cached or
accepted as an execution authorization token.

The CLI rejects malformed comma-separated `key=value` members instead of silently
dropping them. Repeated keys retain the existing last-value behavior. `--status`
prints structured syntax results without fetching. Malformed query serialization
is a usage error in either mode. `--list-sources` remains a metadata operation.

## Worked example: input, method and answer

The existing registry supplies the source `bsee` and example endpoint `Production`.
The query `label=a b` is synthetic and makes no claim about a live API response.

```sh
uv run --no-project python scripts/data/doc_intelligence/fetch_from_api.py \
  --source bsee --endpoint Production --params 'label=a b' --status
```

Method: the registry contains the source, the endpoint is a literal segment and
the query is a string mapping. Therefore syntax passes. No I/O evidence is
collected. The expected answer, derived directly from the Boolean contract, is:

```json
{
  "syntax_validation": "PASSED",
  "requirements_satisfied": true,
  "routable_now": false,
  "io_validation": "NOT_EVALUATED",
  "reason_codes": ["IO_VALIDATION_DEFERRED"]
}
```

Replacing the endpoint with `../records` fails the literal-segment rule. Status
then returns `INVALID_ENDPOINT`, `syntax_validation=FAILED` and
`requirements_satisfied=false`. Both URL construction and execution raise the
same code before any fetch or output-directory creation. With a valid endpoint
but an unavailable test fetcher, status still defers I/O and execution raises the
fetcher's failure. The tests calculate these expectations independently from the
rules above and inject fetchers; they make no live API requests.

## Verification and limits

The existing fetcher tests and `test_source_context_parity.py` cover empty,
malformed, unavailable and valid source contexts, query encoding, credential type
errors, metadata isolation and both CLI request paths. The old unknown-source
assertion is updated only to expect the fixed error code. Other existing behavior
assertions are retained.

In-process adversarial review checks error parity, side effects before validation,
credential exposure, runtime query-encoding failures and metadata mutation. An
independent provider review remains required before merging. Sibling consumers,
live availability probing, source payload schema validation and persistence
permissions remain outside this integration.

## Sources

- Issue #3445, “Require status and readiness checks to validate the same source
  contract as execution”: validation parity and deferred I/O requirements.
- Linked Landman issue #924: defect context and existing sibling parity remediation;
  no sibling code is changed here.
- [Existing REST registry and fetcher](../../scripts/data/doc_intelligence/fetch_from_api.py):
  configured source identities, base URLs, endpoint examples and encoding behavior.
- [Agent data handling contract](../architecture/agent-data-handling-contract.md):
  readiness observations do not authenticate access, rights or intended-use eligibility.
