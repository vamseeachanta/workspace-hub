# Cross-Drive Deduplication Audit: /mnt/ace and DDE Remote

## Findings

- The DDE remote storage at `/mnt/dde` is currently inaccessible. Therefore, a direct comparison of file contents is not possible.
- The analysis is based on the file listing of `/mnt/ace`.

## /mnt/ace File System Structure

- The `/mnt/ace` directory contains a mix of project data, standards, literature, and software.
- There are numerous directories with similar names, suggesting potential duplication (e.g., `O&G-Standards` and `O&G-Standards/raw`).
- File types are varied, including PDFs, Office documents, CAD files, and text files.

## Deduplication Strategy

- **Tool Recommendation:** `jdupes` or `fdupes` are recommended for identifying and removing duplicate files. `jdupes` is generally faster.
- **Strategy:**
    1. **Dry Run:** First, perform a dry run to identify duplicate files without deleting them. This will provide a clear picture of the extent of duplication.
    2. **Review and Exclude:** Review the list of duplicates. Exclude any directories or file types that should not be deduplicated (e.g., system files, certain project files where copies are intentional).
    3. **Hard Linking:** Instead of deleting duplicates, use hard links. This saves space while ensuring that all paths still point to the correct file.
    4. **Execution:** Run the deduplication tool with the appropriate flags to replace duplicates with hard links.

## Future Actions

- Once the DDE remote is accessible, this audit should be re-run to compare the two storage locations and perform a cross-drive deduplication.
