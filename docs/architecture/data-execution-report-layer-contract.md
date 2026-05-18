# Data, Execution, Report, and Curated-Learning Layer Contract

This contract defines the workspace-hub ecosystem lifecycle requested in [#2726](https://github.com/vamseeachanta/workspace-hub/issues/2726):

```text
inputs -> execution -> reports/chatbots -> curated output learnings -> corpus tier
```

It is a parent architecture contract. Child plans #2727, #2728, and #2729 may refine their own layer details only when they consume this cross-layer contract instead of redefining upstream/downstream interfaces.

## Architecture-surface codes

These architecture-surface codes are not replacements for document-intelligence L-levels. Existing document-intelligence L-levels remain governed by `docs/document-intelligence/README.md` and related maps.

| Code | Boundary | Owns | Does not own |
|---|---|---|---|
| A-DATA | Source truth and residency | raw/public/private source IDs, curated reference data, provenance, source residence | execution routing, report publication, chatbot exposure |
| A-EXEC | Execution manifests and compute evidence | `source_id` references, `input_residency`, tools, code execution, machines/compute, checksums, validation logs | raw source truth, public promotion decisions |
| A-REPORT | Audience-facing and internal output surfaces | raw internal output, client HTML, limited PDFs, chatbot/index configs, evidence bundles, `output_residency` | automatic promotion into public/private llm-wiki |
| A-CURATED-LEARNING | Reviewed learnings extracted from report/chatbot outputs | public llm-wiki pages, private/domain corpus entries, client-private corpus entries after promotion gate | raw report dumps, private data laundering |

## Lifecycle rules

1. Data starts in A-DATA with a source owner, source posture, and canonical `source_id` or redacted source ID.
2. A-EXEC consumes data by reference through `source_id`, `input_residency`, and gate evidence. Execution must not duplicate raw data ownership.
3. A-REPORT consumes execution evidence and data classification to produce raw internal outputs, client-facing HTML, limited PDFs, and chatbot surfaces.
4. A-CURATED-LEARNING receives only reviewed report-derived learnings after a promotion gate. Report output is not automatically knowledge.
5. Each transition must name a promotion gate when the destination is more public, more durable, or broader-audience than the source.

## Required gates by transition

| Transition | Required gate |
|---|---|
| A-DATA -> A-EXEC | source registry lookup, provenance, `source_id`, `input_residency`, license/legal constraints, validation readiness |
| A-EXEC -> A-REPORT | tool/run evidence, checksums where applicable, `output_residency`, redaction, audience classification |
| A-REPORT -> A-CURATED-LEARNING | promotion gate with provenance, license, legal, sanitization, citation/source separation, owner review |
| Any private/restricted source -> public llm-wiki/public chatbot/public report | explicit legal and sanitization gate; fail closed by default |

## Residency and publication rules

- Raw/private/client data cannot route directly into public llm-wiki or public chatbot indexes.
- Private or raw-like llm-wiki staging remains local/private until a registry identifies its owner and allowed destination.
- Public llm-wiki content must be sanitized, source-cited, and public-safe.
- Client-facing HTML and limited PDFs are A-REPORT outputs and require audience-specific evidence gates.
- Chatbots inherit the most restrictive posture of their source corpus and report evidence.

## Canonical source matrix

The structured source matrix is `tests/fixtures/architecture/layer_boundary_matrix.yaml`. The reviewable markdown rendering is `docs/architecture/source-layer-classification-matrix.md`.

## Sequencing boundaries

- #2726 owns this parent cross-layer contract and classification crosswalk.
- #2727 owns data-layer refinements and promotion rules after consuming this contract.
- #2728 owns execution-layer manifests, tools, compute, and routing after consuming this contract.
- #2729 owns report-layer outputs and evidence boundaries after consuming this contract.
- #2731/#2732 own mount/source-registry normalization and must not be silently absorbed into this parent issue.
