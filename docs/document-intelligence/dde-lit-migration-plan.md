# DDE Remote Literature Migration Plan

This document outlines the plan for migrating the 14.6 GB / 5,456 PDFs of DDE remote literature.

## Storage Requirements

- **Current Size:** 14.6 GB
- **Estimated Growth:** 2-3 GB/year
- **Recommendation:** Allocate 25 GB of storage to accommodate future growth.

## Bandwidth Estimate

- **Total Size:** 14.6 GB
- **Estimated Transfer Time (100 Mbps):** ~20 minutes

## Priority Ordering by Domain

1. **Risers & Moorings:** Highest priority due to direct relevance to current projects.
2. **Pipelines & Subsea:** High priority.
3. **Naval Architecture & Marine Engineering:** Medium priority.
4. **General Engineering & Reference:** Low priority.

## Indexing Strategy Post-Migration

1. **OCR:** Perform OCR on all scanned documents to make them text-searchable.
2. **Metadata Extraction:** Extract key metadata such as title, author, publication date, and keywords.
3. **Semantic Indexing:** Use a pre-trained language model to create vector embeddings for each document, enabling semantic search.
4. **Search Interface:** Implement a user-friendly search interface that allows for both keyword and semantic search.
