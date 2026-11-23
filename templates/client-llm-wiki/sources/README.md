# Source inventory conventions

Use this folder for source manifests and readable-source pointers, not bulk raw drops.

Each source manifest should include:

- source_id
- source_path, an authorized absolute path only after the private registry records a raw root; otherwise absent
- source_class: raw-data | readable-raw-data | private-wiki | public-derivative
- client/project identifier
- extraction method
- privacy classification
- citation fields
- current promotion status

Large binaries, solver archives, PDFs, spreadsheets, and client files remain in authorized external storage unless explicitly approved for private repo storage.
