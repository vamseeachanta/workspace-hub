# Unified Document Intelligence CLI Design

## 1. Overview

This document proposes a unified Command Line Interface (CLI) tool named `doc-intel` to streamline all document intelligence tasks. This replaces the current collection of disparate scripts with a single, consistent, and extensible tool.

## 2. Command Structure

The `doc-intel` CLI will be built using a subcommand structure to organize its various functions.

```bash
doc-intel <subcommand> [options]
```

### 2.1. Subcommands

-   **`scan`**: Scan a directory for new or updated documents. This will be the entry point for the pipeline, identifying files to be processed.
    -   `doc-intel scan <directory>`
    -   `--recursive, -r`: Scan subdirectories.
    -   `--since <date>`: Scan for files modified since a given date.

-   **`index`**: Create or update a document index. The index will be a central registry of all known documents and their metadata.
    -   `doc-intel index --source <scan_result.json>`
    -   `--index-path <path/to/index.json>`: Path to the master index file.

-   **`extract`**: Extract text and metadata (e.g., tables, images) from documents. This will support various file types (PDF, DOCX, etc.).
    -   `doc-intel extract --file <path/to/file>`
    -   `--index <path/to/index.json>`: Process all new files in the index.
    -   `--output-dir <path/to/output>`: Directory to save extracted content.

-   **`classify`**: Classify documents into predefined categories (e.g., by engineering discipline, document type).
    -   `doc-intel classify --file <path/to/file>`
    -   `--index <path/to/index.json>`: Classify all unclassified documents in the index.
    -   `--model <model_name>`: Specify the classification model to use.

-   **`summarize`**: Generate summaries of documents. This can create both brief overviews and more detailed technical summaries.
    -   `doc-intel summarize --file <path/to/file>`
    -   `--length <short|medium|long>`: Control the length of the summary.

-   **`audit`**: Audit the document intelligence pipeline for completeness and consistency.
    -   `doc-intel audit --index <path/to/index.json>`
    -   Checks for missing extractions, classifications, or summaries.

## 3. Benefits

-   **Consistency:** A single, well-defined interface for all document-related tasks.
-   **Discoverability:** Subcommands and help messages make it easy to understand the available functionality.
-   **Extensibility:** New features can be added as new subcommands without breaking existing workflows.
-   **Orchestration:** Simplifies the process of building automated document processing workflows.
