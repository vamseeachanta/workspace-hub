# feat(execution): implement execution manifest validator for #2728

Parent: #2728

Build a validator for `docs/architecture/execution-manifest.schema.yaml` that fails closed on:

- missing `source_ids`, `source_registry_kind`, or `source_registry_ref`
- missing command/replay/regeneration metadata
- missing tests, checksums, legal scan evidence, or review artifacts
- inline raw/private payload keys such as `raw_data`, `data_dump`, `client_payload`, or `source_text`
- public or more-public output routing without `provenance`, `license`, `legal`, `sanitization`, and `owner-review` gates

Acceptance criteria:

- validator has TDD coverage for valid and invalid manifests
- validator is wired to architecture validation or pre-publication checks
- validation output identifies the failing field and issue reference
