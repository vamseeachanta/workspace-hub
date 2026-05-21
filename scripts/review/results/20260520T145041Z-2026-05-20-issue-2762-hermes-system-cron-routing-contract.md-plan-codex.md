### Verdict: MAJOR

### Summary
The plan is directionally sound and correctly separates Hermes runtime flow from repo observability, but it still has specification gaps that would make implementation ambiguous. The main blocker is that the contract model mixes scheduler planes with runtime classes, while the validator is supposed to report those as separate dimensions.

### Issues Found
- [P1] Critical: The Contract Model table incorrectly lists `native-provider-ai` and `bridge-export-audit` under `Plane`, even though the deliverable and pseudocode define scheduler plane and runtime class as separate axes. This can produce invalid `scheduler_plane` values and recreate the ambiguity the plan is trying to eliminate.
- [P2] Important: The plan does not define where documented exceptions or migration links live. Acceptance requires native-provider AI bypasses to warn or violate unless a documented exception exists, but there is no schema, file, YAML field, or contract section for exception metadata beyond the hardcoded `#2763` example.
- [P2] Important: The test list does not cover CLI/report behavior that the pseudocode promises: JSON vs Markdown output, selected non-zero exit modes, and fail-soft parsing when Hermes CLI output drifts. That leaves the validator’s operational contract under-specified.
- [P3] Minor: The plan references `scripts/cron/setup-cron.sh --dry-run`, but the attestation only verifies `setup-cron.sh` as missing and does not verify `scripts/cron/setup-cron.sh`. This is not a contradiction against the cited path, but the evidence block does not independently support the dry-run script existence claim.

### Suggestions
- Split the model into explicit enums: `scheduler_plane = system-cron | hermes-gateway-cron | unknown/unavailable` and `runtime_class = deterministic | native-provider-ai | hermes-managed-ai | hermes-managed-no-agent | bridge-export-audit` or similar.
- Add an exception/migration metadata source to the contract, such as fields in `config/scheduled-tasks/schedule-tasks.yaml` or a small registry section in `SCHEDULER_ROUTING_CONTRACT.md`, then test it.
- Add tests for CLI exit behavior, output schema stability, and Hermes parser drift/unrecognized columns.
- Add implementation verification commands, including the repo-required legal sanity scan.

### Questions for Author
- Should native-provider AI exceptions be declared in the schedule YAML, in the contract document, or in a separate registry?
- Is `bridge-export-audit` intended to be a runtime class, an evidence kind, or both?
