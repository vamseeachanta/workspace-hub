# Report Evidence Bundle Schema

A report evidence bundle is the required sidecar for client-facing HTML, limited PDF, public pages, chatbot/query surfaces, and report-derived learning. It proves every published claim has source, command, validation, legal, checksum, review, residency, and promotion evidence.

Machine-readable schema: `report-evidence-bundle.schema.yaml`.

## Required bundle-level fields

Every durable report/output artifact must declare:

- `bundle_id` and `issue` — trace the output to the originating work item.
- `artifact_type` — one of the report taxonomy values (`client_facing_html`, `limited_pdf`, `chatbot_query_surface`, etc.).
- `output_residency` — where the artifact is allowed to live (`public_llm_wiki`, `registered_client_private_corpus`, etc.).
- `corpus_scope` — corpus ID/name, registry reference, and explicit scope statement.
- `audience_classification` — `internal-only`, `client-private`, or `public-safe`.
- `source_class_mix` — source residency classes consumed by the artifact.
- `freshness` — as-of date plus the disclosure text required on reports/query surfaces.
- `execution_metadata` — command, run ID, and generation timestamp.
- `artifact_derivation_chain` — ordered derivation trail from source contract to output artifact.
- `sources` — source-level evidence entries with IDs, `source_doc_key`, confidence/readiness, and gate status.
- `published_claims` — claim-level evidence bindings.
- `legal_scan` — canonical legal scan command/result.

## Source-level fail-closed rules

Each `sources[]` entry requires:

- `source_id`
- `source_doc_key` in the canonical `source-doc-key:<corpus>:<opaque-id>` form; raw filesystem paths and sensitive filenames are invalid.
- `source_class`
- `input_residency`
- `output_residency`
- `confidence.overall`
- `confidence.report_readiness`
- `confidence.evidence_completeness`
- `promotion.promotion_record` with durable evidence of the promotion decision
- `promotion.gates.private_release_clearance`
- `promotion.gates.public_release_clearance`
- `promotion.gates.sanitization_review`
- `promotion.gates.reviewer_clearance`

Client-private outputs require private release, sanitization, and reviewer clearance. Public outputs additionally require `audience_classification: public-safe`, public source/input/output residency, public-release clearance for every source, plus full public promotion gates on every published claim.

## Format policy

HTML remains the canonical client-facing deliverable where possible. PDF is a limited derived deliverable and must include `exception_reason` while carrying the same evidence bundle as HTML.
