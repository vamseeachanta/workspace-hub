# feat(report): build report artifact index by output residency

Parent: #2729

Create a report artifact index that tracks report-layer artifacts by issue, source IDs, artifact type, output residency, and promotion state.

The index should cover:

- raw outputs
- evidence bundles
- internal reports
- client-facing HTML
- limited PDFs
- chatbot/query surfaces
- public pages
- report-derived learning

Acceptance criteria:

- artifact index schema includes source IDs, issue reference, artifact type, output residency, and promotion gates
- index generation has tests or validator coverage
- raw outputs are not marked deliverable by default
- public/client-facing entries require evidence bundle references and legal/sanitization gate status
