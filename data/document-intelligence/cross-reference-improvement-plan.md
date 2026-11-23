# Cross-Reference Improvement Plan

## 1. Objective

To enhance the connectivity and richness of the document index by systematically identifying and creating links between related documents. This will improve discoverability and provide a more comprehensive context for users and AI agents.

## 2. Cross-Referencing Strategies

### Strategy 1: URL Matching

*   **Concept:** Many documents, particularly academic papers and web-sourced articles, contain URLs that reference other resources. These URLs are explicit links that should be captured.
*   **Implementation:**
    1.  During the text extraction phase (Phase A), use a robust regex to identify all URLs within the body of each document.
    2.  For each extracted URL, search the existing document index (e.g., in the `url` or `source` field of the index records) to see if it corresponds to a known document.
    3.  If a match is found, create a bidirectional link in the index. This could be a `related_doc_id` field that stores an array of document IDs.
*   **Example:** A research paper on VIV that cites a DNV standard via its URL can be directly linked to the DNV standard's record in our index.

### Strategy 2: Organization Matching

*   **Concept:** Documents from the same organization (e.g., a specific company, university, or standards body) are often related. While not as direct as a URL, this provides a strong contextual link.
*   **Implementation:**
    1.  Ensure that the organization/author affiliation is consistently extracted during the metadata extraction phase.
    2.  Create a "fuzzy" matching algorithm to normalize organization names (e.g., "MIT" and "Massachusetts Institute of Technology" should resolve to the same entity).
    3.  Build a secondary index that maps organizations to the documents they have produced.
    4.  This can be used to provide a "More from this organization" feature in a user interface or to enrich the context provided to an AI agent.

### Strategy 3: Document Number / Identifier Matching

*   **Concept:** Many formal documents, especially standards and internal company reports, use a unique identifier (e.g., `DNV-RP-F105`, `OTC-25078-MS`). These identifiers are frequently mentioned in other documents.
*   **Implementation:**
    1.  Develop a library of regex patterns to recognize common document identifier formats from organizations like DNV, ISO, API, OTC, etc.
    2.  During text extraction, run these regexes to find all potential document identifiers mentioned in the text.
    3.  For each identifier found, perform a search against the `doc_number` or `title` field in the main document index.
    4.  If a match is found, create a bidirectional link.
*   **Example:** A pipeline design basis that refers to `API-RP-1111` for guidance can be automatically linked to the record for that standard.

## 3. Implementation Plan

1.  **Phase 1: Augment Extraction:**
    *   Update the Phase A (text/metadata extraction) scripts to include robust extraction for URLs and a pattern library for document identifiers.
    *   Store these extracted entities in a new field in the document index, such as `extracted_references`.

2.  **Phase 2: Asynchronous Linking:**
    *   Create a new, separate script (e.g., `scripts/document-intelligence/build-cross-references.py`).
    *   This script will run *after* the main indexing pipeline.
    *   It will iterate through the `extracted_references` for each document and perform the lookups against the main index as described above.
    *   It will then update the index records with the newly created links.

3.  **Phase 3: Schema Update:**
    *   Update the canonical document index schema to include fields for the new links, for example:
        *   `cross_references_url: [doc_id_1, doc_id_2, ...]`
        *   `cross_references_doc_id: [doc_id_3, doc_id_4, ...]`
    *   The `organization` field should also be leveraged to show related documents.

This multi-pronged approach will create a rich web of connections within the document corpus, turning a simple list of files into a true knowledge graph.
