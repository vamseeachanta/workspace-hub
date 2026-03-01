# Source Registry

Current document-intelligence assets:

- `data/document-index/registry.yaml`
- `data/document-index/index.jsonl`
- `data/document-index/shards/`
- `data/document-index/summaries/`
- `data/document-index/standards-transfer-ledger.yaml`

Mounted-source registry:

- `data/document-index/mounted-source-registry.yaml`

Use the mounted-source registry to map:

- source bucket
- mount root
- local vs remote
- index artifact
- storage policy
- availability check

Do not invent a new source bucket when an existing one already covers the same root.
Prefer extending the registry with better metadata over duplicating entries elsewhere.
