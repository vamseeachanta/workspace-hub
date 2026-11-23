# Evidence Sidecar Redaction Safety

Use this when verifying readiness scripts, dashboards, generated reports, or remote-host probes that consume JSON/YAML evidence from another command or machine.

## Durable lesson

Evidence existence is not enough. A sidecar can be present but malformed, partial, stale, or redacted in ways that hide diagnostic codes. Readiness gates must fail closed on both missing and malformed evidence.

## Verification pattern

1. Validate the top-level evidence identity before reading nested fields:
   - expected `type`
   - expected `producer`
   - expected host/machine identifier when applicable
2. Validate nested structure:
   - `checks` exists and is a mapping/object
   - required check names are present
   - each required check has `status`, `message`, and `details` or the local equivalent contract
3. Return separate blockers for:
   - evidence missing
   - evidence malformed
   - evidence present but check status blocking
4. Run the full artifact through the same redaction function used in production, then assert the machine-readable fields still support triage.
5. Prefer renaming diagnostic codes over weakening redaction.

## Redaction-safe code naming

Avoid these substrings in machine-readable blocker/status codes because broad redactors and secret scanners may redact them even when they are not secrets:

- `token`
- `secret`
- `api_key` / `apikey`
- `password`
- `credential`

Prefer neutral codes:

- `repo_placement_missing`
- `repo_placement_malformed`
- `repo_placement_blocking`
- `tool_contract_missing`
- `workspace_contract_malformed`

Avoid codes like:

- `repo_placement_evidence_malformed` if the redactor pattern treats `credential`-like or evidence-related substrings too broadly
- `missing_credentials` unless the value is intentionally redacted and not used for machine dispatch

## Test matrix

Minimum tests for evidence-consuming readiness code:

- valid evidence -> readiness can proceed
- missing evidence -> readiness fails closed with missing blocker
- malformed top-level evidence -> readiness fails closed with malformed blocker
- missing required nested check -> readiness fails closed with malformed blocker
- production redaction path does not destroy blocker `code` values needed by downstream tools

## Closeout rule

Do not close a readiness/evidence issue until the malformed-evidence path has been covered by tests and adversarial review has specifically checked fail-closed behavior.