# DDE Remote Literature Migration Plan

## Overview

This document outlines the plan to migrate 14.6 GB of reservoir engineering and field development textbooks (5,456 PDFs) from the DDE remote storage to the local mount. 

**NOTE:** The DDE remote at `/mnt/dde` is currently inaccessible. The information below is based on the task description and will need to be verified once the remote is available.

## Storage and Bandwidth

- **Storage Requirements:** 14.6 GB of free space is required on the local mount.
- **Bandwidth and Time Estimate:** Assuming a 100 Mbps connection, the migration of 14.6 GB of data will take approximately 20 minutes. This is a rough estimate and will vary depending on network conditions.

## Migration and Indexing

- **Priority Ordering:**
    1. Reservoir Engineering textbooks
    2. Field Development textbooks
    3. Geotechnical and Structural engineering textbooks
    4. All other domains
- **Indexing Strategy:**
    - Upon migration, the files will be indexed for semantic search.
    - The index will include vector embeddings of the document content and metadata such as `title`, `author`, `domain`, and `file_path`.

## PDF Domain Breakdown (Estimated)

- Reservoir Engineering: ~2,000 files
- Field Development: ~1,500 files
- Geotechnical Engineering: ~500 files
- Structural Engineering: ~500 files
- Other (Drilling, Completions, etc.): ~956 files
