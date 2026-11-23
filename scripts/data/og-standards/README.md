# O&G Standards Knowledge System

> AI-powered knowledge management for 27,000+ Oil & Gas technical standards

## Overview

This system provides semantic search and AI-powered Q&A for O&G industry standards including API, DNV, ASTM, ISO, Norsok, BSI, and more.

**Features:**
- 📚 27,000+ PDF documents indexed
- 🔍 Full-text keyword search (FTS5)
- 🧠 Semantic search with vector embeddings
- 🤖 AI-powered answers using Claude or OpenAI
- 📊 Interactive CLI tools

## Quick Start

```bash
# Setup
./setup.sh

# Check status
./og-status

# Quick search
./og "API riser design"

# AI-powered Q&A (requires API key)
./og-rag "What are DNV requirements for pipeline fatigue assessment?"
```

## Installation

### Prerequisites

- Python 3.8+
- pip
- SQLite3
- 8GB+ RAM (for embedding generation)

### Setup

```bash
# Run setup script
./setup.sh

# Set API key for AI answers
export ANTHROPIC_API_KEY='your-key-here'

# Add to ~/.bashrc for persistence
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.bashrc
```

## Commands

| Command | Description |
|---------|-------------|
| `og <query>` | Quick keyword search |
| `og -i` | Interactive search mode |
| `og-rag <question>` | AI-powered Q&A |
| `og-rag -i` | Interactive AI assistant |
| `og-status` | System status dashboard |
| `og-service <cmd>` | Service management |
| `og-ingest <cmd>` | Document ingestion |

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    O&G Standards System                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │   PDF    │   │   Text   │   │  Vector  │   │   RAG    │ │
│  │ Library  │──▶│ Extract  │──▶│ Embeddings│──▶│  Query   │ │
│  │ 27K docs │   │  fitz    │   │ sentence-│   │ Claude   │ │
│  └──────────┘   └──────────┘   │transformers│  └──────────┘ │
│                                 └──────────┘                 │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    SQLite Database                       ││
│  │  • documents (27K records)                               ││
│  │  • text_chunks (60K+ chunks with embeddings)             ││
│  │  • FTS5 full-text search index                           ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
og-standards/
├── config.yaml          # Configuration
├── setup.sh             # Installation script
├── README.md            # This file
│
├── inventory.py         # Document inventory builder
├── rename.py            # Rename/remap mode for renamed files and moved roots
├── extract.py           # PDF text extraction
├── embed.py             # Vector embedding generation
├── search.py            # CLI search interface
├── rag.py               # RAG query engine
│
├── og                   # Quick search wrapper
├── og-rag               # AI Q&A wrapper
├── og-status            # Status dashboard
├── og-service           # Service manager
└── og-ingest            # Document ingestion
```

## Usage Examples

### Keyword Search

```bash
# Search for API standards about risers
./og "API riser"

# Search for fatigue requirements
./og "fatigue assessment -org DNV"

# Interactive mode
./og -i
```

### AI-Powered Q&A

```bash
# Ask technical questions
./og-rag "What are the safety factors for offshore pipelines in DNV-OS-F101?"

# Compare standards
./og-rag "How do API and DNV requirements for riser design differ?"

# Interactive session
./og-rag -i
```

### Service Management

```bash
# Check system status
./og-status

# Start background processing
./og-service start-all

# Stop processing
./og-service stop-all

# View logs
./og-service logs
```

### Adding New Documents

```bash
# Add single PDF
./og-ingest add /path/to/new_standard.pdf

# Add directory of PDFs
./og-ingest add /path/to/standards/

# Process new documents
./og-ingest process

# Full refresh
./og-ingest refresh
```

### Renamed Files and Moved Roots

A rename on disk leaves the inventory DB, the FTS index and the catalog pointing at
the old name. A full rebuild (`inventory.py --force`) discards extracted text, chunks
and embeddings, so carry renames through with `rename.py` instead. It updates rows in
place by id, so text, chunks and embeddings stay attached.

The rename log is a Markdown table at the library root (`RENAME-LOG.md`):

```markdown
| Old path | New path | SHA-256 |
|---|---|---|
| `API/API RP 2RD (2013).pdf` | `API/API RP 2RD (2013 draft).pdf` | 3f5a…(64 hex) |
```

Relative paths resolve against `target_directory`. Every entry is checked before any
write: the new file must exist and hash to the logged SHA-256, the old path must be a
catalogued `target_path`, and the new path must not belong to another row. One bad
entry rejects the whole log. Re-running an applied log is a no-op.

The log is append-only. Entries replay in order, so a file renamed twice is two
rows (`A → B`, then `B → C`); only the end of each chain must exist on disk and
match its SHA-256. A direct swap (`A → B`, `B → A`) is rejected; swap through a
temporary name (`A → T`, `B → A`, `T → B`). A row whose recorded SHA-256 differs
from an entry's is a different document and is never moved by that entry, which
keeps re-runs of such logs no-ops.

```bash
python rename.py --dry-run     # validate and print the plan
python rename.py               # update rows (target_path, filename, title, sha256,
                               # organization/doc_type/doc_number), rebuild FTS,
                               # regenerate the catalog (--no-catalog to skip)
```

Then refresh the document index through its normal chain, starting with
`scripts/data/document-index/remap_og_standards_paths.py --dry-run`.

Source roots moved under `raw/`. The inventory keys rows on `file_path`, so a scan
over a moved root would insert every file again; `inventory.py` refuses to scan while
rows sit under unconfigured roots. Remap each old root first (dry-run, then apply):

```bash
python rename.py --remap-root "/old/source/root" "/mnt/ace/O&G-Standards/raw/<dir>" --dry-run
```

## Configuration

Edit `config.yaml` to customize:

```yaml
# Standards library location
standards_directory: /mnt/ace/O&G-Standards

# Database path
database_path: /mnt/ace/O&G-Standards/_inventory.db

# Embedding model
embedding:
  model: all-MiniLM-L6-v2
  dimensions: 384

# Text chunking
chunking:
  size: 1000
  overlap: 200
```

## API Keys

For AI-powered answers, set one of:

```bash
# Claude (recommended)
export ANTHROPIC_API_KEY='sk-ant-...'

# OpenAI (alternative)
export OPENAI_API_KEY='sk-...'
```

## Performance

| Metric | Value |
|--------|-------|
| Total Documents | 27,000+ |
| Text Chunks | 60,000+ |
| Embedding Dimensions | 384 |
| Query Time (semantic) | ~100ms |
| Query Time (AI answer) | ~2-3s |

## Troubleshooting

### GPU/CUDA Errors

If you see CUDA compatibility errors:
```bash
# Force CPU mode (automatic in og-rag)
export CUDA_VISIBLE_DEVICES=""
```

### Missing API Key

```
[ANTHROPIC_API_KEY not set]
```

Set the API key:
```bash
export ANTHROPIC_API_KEY='your-key'
```

### Slow Embedding Generation

Embedding 60K+ chunks takes several hours on CPU. Use the service manager:
```bash
./og-service start-embed  # Run in background
./og-service logs         # Monitor progress
```

## License

Internal tool - Not for distribution

## Support

Contact: workspace-hub/scripts/og-standards
