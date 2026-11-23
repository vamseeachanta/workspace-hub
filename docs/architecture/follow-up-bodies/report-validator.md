# feat(report): implement report evidence bundle validator for #2729

Parent: #2729

Validate `docs/architecture/report-evidence-bundle.schema.yaml` and report evidence bundles before publication.

The validator must fail closed on:

- missing published claim bindings
- missing source manifest, command manifest, validation result, legal scan, checksum, review verdict, output residency, or promotion decision
- public or client-facing publication without sanitization and promotion gate evidence
- unknown artifact types or output residency values

Acceptance criteria:

- validator has TDD coverage for valid and invalid evidence bundles
- validator reports the exact failing claim/field
- publication workflows can call the validator before publishing HTML/PDF/chatbot/query surfaces
