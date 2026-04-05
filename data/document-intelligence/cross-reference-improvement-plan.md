# Cross-Reference Improvement Plan

> **Generated:** 2026-04-05
> **Task:** #1658 - Cross-reference improvement plan

---

## 1. Objective

The workspace contains several key registries for managing documents and resources:

-   **`mounted-source-registry.yaml`**: Defines the high-level physical and logical storage locations (e.g., `/mnt/ace`, remote DDE drive).
-   **`online-resource-registry.yaml`**: Catalogs external online resources like GitHub repositories, APIs, and academic papers.
-   **`standards-transfer-ledger.yaml`**: Tracks the processing status of individual industry standards (e.g., API RP 1111).
-   **`index.jsonl`**: The master file index containing over a million entries with paths and metadata.

Currently, these registries are largely disconnected. The goal is to establish robust cross-referencing between them to create a cohesive, navigable knowledge graph. This will enable us to answer questions like "Which files in the index correspond to this standard in the ledger?" or "Where is the local backup of this online resource?".

## 2. Cross-Referencing Strategies

### Strategy 1: URL & Domain Matching (Online Resources ↔ Master Index)

This strategy connects entries in the `online-resource-registry.yaml` to their locally downloaded counterparts in the `index.jsonl`.

-   **Mechanism:** Match the URL from the online registry with file paths in the master index.
-   **Process:**
    1.  For each entry in `online-resource-registry.yaml`, extract the primary URL (e.g., `https://github.com/CadQuery/cadquery`).
    2.  Create a search pattern to find corresponding local paths in `index.jsonl`. The pattern should be flexible enough to handle different cloning conventions. For a GitHub URL, the pattern could look for paths containing `CadQuery/cadquery`.
    3.  For each match found in `index.jsonl`, inject a `cross_reference_id` field into the JSONL entry, pointing back to the `id` in the online registry (e.g., `cross_reference_id: cadquery`).
    4.  Conversely, update the `local_backup_path` field in the `online-resource-registry.yaml` entry with the path found in the index.
-   **Example:**
    -   **Online Registry Entry:** `{id: cadquery_repo, url: https://github.com/CadQuery/cadquery}`
    -   **Index Search:** Find paths containing `cadquery`.
    -   **Index Entry Found:** `{"path": "/mnt/ace/open-source/cadquery/README.md", ...}`
    -   **Result:** Update the `online-resource-registry.yaml` entry with `local_backup_path: /mnt/ace/open-source/cadquery/` and add `"cross_reference_id": "cadquery_repo"` to the relevant entries in `index.jsonl`.

### Strategy 2: Organization & Document Number Matching (Standards Ledger ↔ Master Index)

This strategy links the conceptual standards in the `standards-transfer-ledger.yaml` to their actual PDF files on disk.

-   **Mechanism:** Use the standard's organization (`org`) and document identifier (`id` or `title`) to find the corresponding file paths.
-   **Process:**
    1.  For each entry in `standards-transfer-ledger.yaml` (e.g., `{id: API-RP-1111, org: API, title: API RP 1111 ...}`).
    2.  Construct a search regex based on the `org` and `id/title`. For `API RP 1111`, patterns could be `*API*1111*` or `*RP*1111*`.
    3.  Search the `path` field in `index.jsonl` using this pattern.
    4.  Update the `doc_paths` field in the `standards-transfer-ledger.yaml` with all the file paths that match. This is crucial as multiple versions or copies of a standard may exist.
    5.  For each matched entry in `index.jsonl`, add a `cross_reference_id` pointing back to the ledger entry (e.g., `cross_reference_id: std-API-RP-1111`).
-   **Example:**
    -   The ledger entry for `API RP 1111` currently has several paths. This process would be used to automatically discover and populate those paths if they were missing.

## 3. Implementation Plan

A new script, `scripts/data/document-index/cross_reference_linker.py`, will be created to implement these strategies.

1.  **Script Structure:**
    *   The script will have two main functions, one for each strategy described above.
    *   `link_online_resources()`: Implements Strategy 1.
    *   `link_standards_to_files()`: Implements Strategy 2.

2.  **Data Handling:**
    *   The script will load `online-resource-registry.yaml` and `standards-transfer-ledger.yaml` into memory.
    *   It will read `index.jsonl` line by line to avoid loading the entire large file into memory.
    *   It will write updates to a *new* version of the YAML files and a *new* `index.crossreferenced.jsonl` file to avoid in-place corruption. The old files will be backed up and replaced upon successful completion.

3.  **Fuzzy Matching & Heuristics:**
    *   The script will employ fuzzy matching logic. For example, when matching `API RP 1111`, it should correctly identify files named `API_RP_1111.pdf`, `API-RP-1111-4th-Ed.pdf`, etc.
    *   For GitHub URLs, it should be able to break down the URL (`https://github.com/user/repo`) and search for paths containing `user/repo`.

4.  **Reporting:**
    *   The script will generate a `cross-reference-report.md`.
    *   This report will summarize the linking process, including:
        -   Number of online resources linked to local files.
        -   Number of standards in the ledger linked to file paths.
        -   Lists of entries that could not be linked, highlighting gaps in our local mirrors or standards collection.

## 4. Next Steps

-   Develop the `cross_reference_linker.py` script and its corresponding tests.
-   Run the script to perform the initial cross-referencing and generate the first report.
-   Review the report to identify and address any failed linkages.
-   Integrate the script into the regular document intelligence pipeline to ensure cross-references are kept up-to-date as new documents and resources are added.
