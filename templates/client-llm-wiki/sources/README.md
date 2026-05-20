# Source inventory conventions

Use this folder for source manifests and readable-source pointers, not bulk raw drops.

Each source manifest should include:

- source_id
- source_path, usually under `/mnt/ace/<CLIENT_RAW_ROOT>/`
- source_class: raw-data | readable-raw-data | private-wiki | public-derivative
- client/project identifier
- extraction method
- privacy classification
- citation fields
- current promotion status

Large binaries, solver archives, PDFs, spreadsheets, and client files remain in the local raw-data root unless explicitly approved for private repo storage.
