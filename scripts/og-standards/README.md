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
