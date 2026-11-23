# Execution Layer Contract (#2728)

The execution layer transforms classified data-layer inputs into report-eligible artifacts without becoming the canonical owner of raw data or bypassing publication gates.

## Levels

| Level | Working name | Contents | Boundary rule |
|---|---|---|---|
| E-L1 | Input contracts | YAML/JSON specs, issue plans, source manifests, fixture manifests, prompt bundles | References data sources by `source_id`, `source_registry_kind`, and `input_residency`; does not own raw data |
| E-L2 | Tools/code execution | ingestion scripts, parsers, report generators, validation harnesses, legal scanners, skills/prompts | Code is repo-backed; Python commands use `uv run`; outputs manifest evidence |
| E-L3 | Compute/runtime placement | registry machine IDs, local worktrees, background jobs, provider tools | References `config/workstations/registry.yaml` for machine truth; no duplicated machine capability policy |
| E-L4 | Validation/evidence | tests, legal scan outputs, adversarial review artifacts, checksums, run manifests, command logs | Required validation/evidence handoff before any report-layer handoff |

## Required manifest fields

Execution manifests must include: `source_ids`, `source_registry_kind`, `source_registry_ref`, `input_residency`, `output_residency`, `tool`, `machine`, `provider_tool`, `command_manifest`, `regeneration_command`, `replay_command`, `environment_pin`, `outputs`, `checksums`, `test_evidence`, `legal_scan_evidence`, `review_artifact_paths`, `promotion_gates`, and `report_eligible`.

## Boundary rules

1. Execution consumes data-layer source IDs and registry references; it does not copy source truth into execution artifacts.
2. Report eligibility requires validation/evidence, a declared `output_residency`, and a report-layer handoff path.
3. Outputs cannot become more public than inputs unless a promotion gate names provenance, license, legal, sanitization, and owner-review evidence.
4. Runtime orchestrators may enforce this later, but the contract fails closed through schema, fixtures, and TDD tests now.
5. Checksum evidence has two gates: the JSON Schema syntax gate requires `sha256:<64 hex chars>`, and the semantic checksum verifier computes exact file hashes for report-handoff outputs so fabricated digest-looking values fail closed.
6. Machine/provider routing is a view over `config/workstations/registry.yaml`; #2119, #1838, and #2089 remain open dependencies, not approved policy.
