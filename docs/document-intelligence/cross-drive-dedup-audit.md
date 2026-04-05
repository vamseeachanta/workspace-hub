# Cross-Drive Deduplication Audit

This document outlines the deduplication strategy for the /mnt/ace and DDE drives.

## Existing Reports

- `src/utilities/deduplication.py`: Contains existing deduplication logic.
- Various analysis and report files suggest that deduplication has been considered before.

## Drive Comparison

| Drive | File Count | Notes |
|---|---|---|
| /mnt/ace | TBD | TBD |
| DDE | TBD | TBD |

## Deduplication Strategy

1. **File Hashing:** Use a cryptographic hash (e.g., SHA-256) to identify duplicate files.
2. **Metadata Comparison:** Compare file size, and modification dates as a first pass.
3. **Content-Based Deduplication:** For text-based files, use a tool like `fdupes` to find files with identical content, even if metadata differs.

## Tool Recommendations

- **fdupes:** A command-line tool for identifying and deleting duplicate files.
- **jdupes:** A more performant alternative to `fdupes`.
- **Custom Python Script:** Utilize `src/utilities/deduplication.py` and expand upon it to handle the specific needs of these drives.
