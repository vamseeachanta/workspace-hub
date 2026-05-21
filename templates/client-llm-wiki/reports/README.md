# Report and chatbot provenance

Use this folder for report-output manifests, not generated bulky deliverables unless intentionally small and approved.

Every client-facing HTML/PDF/chatbot pack must declare:

- input source IDs and `source_doc_key` references
- execution tool/code revision and command manifest
- compute environment or run context
- raw output path, if preserved
- final output path
- evidence bundle sidecar validated by `docs/architecture/report-evidence-bundle.schema.yaml`
- freshness and corpus-scope disclosure
- privacy/audience classification
- output-residency decision proving the artifact is not more public than its source corpus unless promotion gates are complete
- publishability/review decision

Do not commit private retrieval indexes, raw answer traces, literal private/client paths, sensitive source filenames, or raw project files into this template tree.

PDFs are limited derivatives of approved HTML/report sources, not the primary evidence store; each PDF requires an exception reason in the evidence bundle.
