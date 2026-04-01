# Data Placement Conventions

> Where generated data, bulk artifacts, and lightweight metadata belong.

## Decision Rule

| Criterion | In git repo | On ace drive (`/mnt/ace/data/`) |
|---|---|---|
| Size | < 10 MB total | >= 10 MB or will grow past it |
| File count | < 1000 files | >= 1000 files |
| Content type | Configs, schemas, scripts, ledgers, indexes | Generated outputs, summaries, extracted content |
| Volatility | Changes with human intent | Changes with pipeline runs |
| Sensitivity | Public / non-client | Client document content |

**If a directory will exceed either threshold (10 MB or 1000 files), it belongs on the ace drive.**

## What belongs in the repo

- Configuration files (`config/`, `data/design-codes/`)
- Schema definitions and registries (`data/document-index/registry.yaml`)
- Lightweight JSON indexes and shard metadata (`data/document-index/shards/`)
- Seed data for knowledge bases (`knowledge/seeds/`)
- Extracted calculation code and tests (`knowledge/dark-intelligence/xlsx-poc-v2/`)
- Pipeline checkpoints (`data/document-index/checkpoints/`)
- `.gitkeep` placeholders for empty directories

## What belongs on the ace drive

Target location: `/mnt/ace/data/<project-or-pipeline>/`

- Generated summaries and extracted text
- Bulk document content (PDFs, DOCX source files)
- Large search indexes (BM25 pickles, JSONL indexes)
- Runtime JSONL logs and notification data
- Any pipeline output that can be regenerated from source

## Mount Points

| Mount | Path | Type | Capacity |
|---|---|---|---|
| ace local disk | `/mnt/ace/` | ext4 (7.3 TB, 67% used) | Primary bulk storage |
| ace-linux-2 remote | `/mnt/remote/ace-linux-2/local-analysis` | sshfs (automount) | Cross-machine access |
| ace-linux-2 dde | `/mnt/remote/ace-linux-2/dde` | sshfs (automount) | DDE data |

## Current Misplaced Data — Relocation Plan

Audit date: 2026-03-31. Items below exceed thresholds and should be relocated.

| Directory | Size | Files | Git-tracked? | Target on ace | Status |
|---|---|---|---|---|---|
| `data/document-index/summaries/` | ~1.5 GB | ~717K | No (gitignored) | `/mnt/ace/data/document-index/summaries/` | Relocate, symlink back |
| `data/doc-intelligence/` | 295 MB | ~9K | No (gitignored) | `/mnt/ace/data/doc-intelligence/` | Relocate, symlink back |
| `data/standards/promoted/` | 28 MB | varies | No (gitignored) | `/mnt/ace/data/standards/promoted/` | Relocate, symlink back |

### Already Correct

- `data/document-index/shards/` — 17 MB tracked, lightweight JSON indexes (within threshold)
- `knowledge/seeds/` — 144 KB, small seed files (correct in repo)
- `knowledge/dark-intelligence/xlsx-poc-v2/` — tracked code/tests, YAML data gitignored (correct split)
- `knowledge-base/` — 380 KB runtime JSONL, already gitignored

### Relocation Steps (follow-up, not done yet)

For each directory in the relocation plan:

```bash
# 1. Copy to ace drive
rsync -av data/<path>/ /mnt/ace/data/<path>/

# 2. Verify copy
diff <(find data/<path>/ -type f | wc -l) <(find /mnt/ace/data/<path>/ -type f | wc -l)

# 3. Remove local copy
rm -rf data/<path>/

# 4. Create symlink
ln -s /mnt/ace/data/<path> data/<path>

# 5. Verify pipeline still works
```

## Gitignore Coverage

All misplaced directories are already covered by `.gitignore` rules:
- `data/document-index/summaries/` — explicit ignore
- `data/doc-intelligence/` — explicit ignore
- `data/standards/promoted/*` with `!.gitkeep` — explicit ignore

No `.gitignore` changes needed.

## For AI Agents

Before writing output to `data/` or `knowledge/`:
1. Check if the target directory is gitignored (if not, it will bloat the repo)
2. If output will exceed 10 MB or 1000 files, write to `/mnt/ace/data/` instead
3. If the ace drive is not mounted, write to the gitignored local path and log a warning
