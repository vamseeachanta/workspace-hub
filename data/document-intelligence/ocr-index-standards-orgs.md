# OCR and Semantic Index Plan for Migrated Standards Organizations

## SNAME

- **Total Files:** 50+
- **File Types:** Scanned documents (PDF) and digital documents (PDF, PPTX, DOCX).
- **OCR Needs:** High for the scanned documents. Optical Character Recognition will be required to make the text searchable.
- **Estimated OCR Time:** Assuming an average of 1 minute per scanned document (estimated 25), the estimated processing time is 25 minutes.

## OnePetro

- **Total Files:** 0
- **File Types:** N/A
- **OCR Needs:** N/A
- **Estimated OCR Time:** N/A

## BSI

- **Total Files:** 50+
- **File Types:** Scanned documents (PDF) and digital documents (PDF, DOC).
- **OCR Needs:** High for the scanned documents. Optical Character Recognition will be required to make the text searchable.
- **Estimated OCR Time:** Assuming an average of 1 minute per scanned document (estimated 25), the estimated processing time is 25 minutes.

## NORSOK

- **Total Files:** 11
- **File Types:** Mostly digital documents (PDF).
- **OCR Needs:** Low.
- **Estimated OCR Time:** 5 minutes.

## API

- **Total Files:** 50+
- **File Types:** A mix of scanned documents (TXT from OCR) and digital documents (PDF).
- **OCR Needs:** Medium. Many files are already OCR'd, but the quality should be verified.
- **Estimated OCR Time:** 30 minutes.

## ASTM

- **Total Files:** 50+
- **File Types:** Scanned documents (PDF) and digital documents (PDF, DOC).
- **OCR Needs:** High for the scanned documents. Optical Character Recognition will be required to make the text searchable.
- **Estimated OCR Time:** Assuming an average of 1 minute per scanned document (estimated 25), the estimated processing time is 25 minutes.

## Index Structure for Semantic Search

- **Vector Embeddings:** Each document will be chunked and converted into vector embeddings using a sentence-transformer model.
- **Metadata:** The following metadata will be stored alongside the vectors: `organization`, `document_id`, `title`, `year`, `file_path`.
- **Search:** The index will support semantic search over the document content, as well as filtering by metadata.
