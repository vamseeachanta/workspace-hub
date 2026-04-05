# Mount Drive Resource Audit

## 1. Local vs. Remote Resources

Based on the `dde-lit-migration-plan.md`, there is a significant collection of 14.6 GB of literature (5,456 PDFs) that is currently remote and planned for migration.

**Local Resources:**

*   The local `workspace-hub` repository contains planning documents, schemas, and indexing artifacts. It does not appear to contain the primary source documents themselves.

**Remote Resources:**

*   A remote drive contains 14.6 GB of PDF documents, which are the primary target for the document intelligence pipeline.

## 2. Resource Gaps

*   **Centralized Document Store:** The primary gap is the lack of a centralized, locally accessible repository for the main corpus of 5,456 PDF documents. They are currently on a remote mount, which introduces access, performance, and pipeline complexities.
*   **Direct Database Access:** There is no direct access to a structured database containing document metadata, classifications, or extracted entities. All information appears to be stored in flat files (`.jsonl`, `.yaml`).

## 3. Legal Scan Status

A search for "legal" reveals several potentially relevant files:

*   `knowledge/seeds/maritime-law-cases.yaml`: Suggests some level of legal case data is available as seed knowledge.
*   `docs/governance/TRUST-ARCHITECTURE.md`: May contain high-level principles regarding data handling and legal constraints.
*   Various files under `assets/WRK-*`: These appear to be outputs from specific work items that may have involved legal considerations.

**Conclusion:** There is no evidence of a systematic, comprehensive legal scan across the entire 32,00 a document corpus. The existing legal-related files seem to be specific to certain datasets or high-level architectural documents. A dedicated legal review of the source documents is a major gap.

## 4. Bridging Recommendations

1.  **Prioritize Migration:** Execute the migration of the 14.6 GB of remote literature as outlined in `dde-lit-migration-plan.md`. This is the most critical step to enable a robust document intelligence pipeline.
2.  **Implement a Two-Tier Storage System:**
    *   **Tier 1 (Hot):** An indexed, searchable database (e.g., Elasticsearch, PostgreSQL with pgvector) for metadata, extracted text, and vector embeddings.
    *   **Tier 2 (Cold):** A file storage solution (like the planned migrated location) for the original PDF documents.
3.  **Initiate a Corpus-Wide Legal & Compliance Scan:** Before beginning large-scale processing, a systematic legal review of the 32,000 documents is necessary to identify IP, copyright, and data privacy constraints. This should be a formal, tracked process.
4.  **Develop a Centralized Schema:** Create a canonical JSON schema that defines the structure for all extracted metadata, including legal/compliance flags, document source, and classification details.
