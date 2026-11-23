# WRK-1132: Multi-Code Standards Semantic Search — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CLI tool (`scripts/standards/query-standards.sh`) that searches engineering standards PDFs (DNV/API/ABS/BS/ISO) by natural-language query and returns ranked results with doc name + page number citations.

**Architecture:** Ingest PDFs from `docs/domains/` using PyMuPDF (same library as existing `scripts/data/og-standards/extract.py`), extract page-level text chunks into `data/standards-index/chunks.jsonl`, pre-build a BM25 index (`data/standards-index/bm25.pkl`), and serve queries via a bash wrapper that loads the pre-built index for sub-second lookup.

**Tech Stack:** Python 3.11, PyMuPDF (`fitz`), `rank_bm25` (BM25Okapi), `uv run --no-project --with pymupdf --with rank_bm25 python`

---

## Context

DNV launched RuleAgent on 2026-03-11 (Veracity portal) — AI Q&A over DNV standards only. ACE differentiator is multi-code independence. `scripts/data/og-standards/` already has extract.py (PyMuPDF, page-by-page) and search.py (SQLite FTS5 at `/mnt/ace/O&G-Standards/_inventory.db`). That DB is remote-mount-only and file-level (no page citations). This WRK adds a local, page-level, multi-code search tool that works without the remote mount.

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `scripts/standards/ingest_standards.py` | Create | PDF ingestion: extract page chunks → chunks.jsonl + bm25.pkl |
| `scripts/standards/query-standards.sh` | Create | CLI bash wrapper → python heredoc BM25 query |
| `tests/standards/__init__.py` | Create | pytest package marker |
| `tests/standards/test_ingest_standards.py` | Create | TDD: ingestion + index build |
| `tests/standards/test_query_logic.py` | Create | TDD: query + filter logic |
| `tests/standards/fixtures/mini.pdf` | Create | Tiny 2-page PDF for testing (generated in test setup) |
| `docs/domains/.gitkeep` | Create | Staging dir for curated standards PDFs |
| `.gitignore` | Modify | Add `data/standards-index/` patterns |

## Chunk Record Schema

Each line in `chunks.jsonl`:
```json
{"chunk_id": "doc_name::p3::0", "doc_name": "DNV-OS-F101.pdf", "page": 3, "code_family": "DNV", "text": "...section text...", "source_path": "/abs/path/to/pdf"}
```

---

## Task 1: Setup — dirs, .gitignore, packages

**Files:**
- Modify: `.gitignore`
- Create: `docs/domains/.gitkeep`
- Create: `scripts/standards/` (directory)
- Create: `tests/standards/__init__.py`

- [ ] **Step 1: Create staging dir and package marker**
```bash
mkdir -p docs/domains scripts/standards tests/standards
touch docs/domains/.gitkeep tests/standards/__init__.py
```

- [ ] **Step 2: Add to .gitignore**

Add these lines to `.gitignore`:
```
# Standards search index (built locally, not committed)
data/standards-index/chunks.jsonl
data/standards-index/bm25.pkl
```

- [ ] **Step 3: Create data dir**
```bash
mkdir -p data/standards-index
touch data/standards-index/.gitkeep
```

- [ ] **Step 4: Verify uv packages available**
```bash
uv run --no-project --with pymupdf --with rank_bm25 python -c "import fitz; from rank_bm25 import BM25Okapi; print('OK')"
```
Expected: `OK`

- [ ] **Step 5: Commit**
```bash
git add docs/domains/.gitkeep data/standards-index/.gitkeep tests/standards/__init__.py .gitignore
git commit -m "chore(standards): scaffold dirs and gitignore for standards search (WRK-1132)"
```

---

## Task 2: TDD — PDF page extraction

**Files:**
- Create: `tests/standards/test_ingest_standards.py`
- Create: `scripts/standards/ingest_standards.py` (partial)
- Create: `tests/standards/conftest.py`

- [ ] **Step 1: Write failing tests for extract_pages()**

Create `tests/standards/conftest.py`:
```python
import io, pytest
from pathlib import Path

@pytest.fixture(scope="session")
def mini_pdf(tmp_path_factory):
    """Create a minimal 2-page PDF for testing without requiring an actual PDF file."""
    import fitz
    tmp = tmp_path_factory.mktemp("fixtures")
    pdf_path = tmp / "mini.pdf"
    doc = fitz.open()
    for i in range(2):
        page = doc.new_page()
        page.insert_text((50, 72), f"Page {i+1} content about cathodic protection design per DNV-RP-B401.")
    doc.save(str(pdf_path))
    return pdf_path
```

Create `tests/standards/test_ingest_standards.py`:
```python
import json
import pytest
from pathlib import Path


def test_extract_pages_returns_list(mini_pdf):
    from scripts.standards.ingest_standards import extract_pages
    chunks = extract_pages(str(mini_pdf))
    assert isinstance(chunks, list)


def test_extract_pages_has_correct_fields(mini_pdf):
    from scripts.standards.ingest_standards import extract_pages
    chunks = extract_pages(str(mini_pdf))
    assert len(chunks) >= 1
    chunk = chunks[0]
    assert "page" in chunk
    assert "text" in chunk
    assert "doc_name" in chunk
    assert chunk["doc_name"] == "mini.pdf"


def test_extract_pages_page_numbers_start_at_one(mini_pdf):
    from scripts.standards.ingest_standards import extract_pages
    chunks = extract_pages(str(mini_pdf))
    pages = [c["page"] for c in chunks]
    assert 1 in pages


def test_extract_pages_skips_empty_text(tmp_path):
    """Scanned / image PDFs yield empty text — should be skipped."""
    import fitz
    pdf_path = tmp_path / "blank.pdf"
    doc = fitz.open()
    doc.new_page()  # blank page, no text
    doc.save(str(pdf_path))
    from scripts.standards.ingest_standards import extract_pages
    chunks = extract_pages(str(pdf_path))
    assert chunks == []


def test_detect_code_family_from_path():
    from scripts.standards.ingest_standards import detect_code_family
    assert detect_code_family("DNV-RP-C203.pdf") == "DNV"
    assert detect_code_family("API_RP_2RD_3rd.pdf") == "API"
    assert detect_code_family("ABS_offshore_structures.pdf") == "ABS"
    assert detect_code_family("ISO_13628-4.pdf") == "ISO"
    assert detect_code_family("BS_EN_ISO_19902.pdf") == "BS"
    assert detect_code_family("unknown_doc.pdf") == "UNKNOWN"
```

- [ ] **Step 2: Run tests — verify FAIL**
```bash
uv run --no-project --with pymupdf --with rank_bm25 python -m pytest tests/standards/test_ingest_standards.py -v 2>&1 | head -40
```
Expected: ImportError or ModuleNotFoundError (ingest_standards.py doesn't exist yet)

- [ ] **Step 3: Implement extract_pages() and detect_code_family()**

Create `scripts/standards/ingest_standards.py`:
```python
#!/usr/bin/env python3
"""
ABOUTME: Standards PDF ingestion pipeline for WRK-1132.
ABOUTME: Extracts page-level chunks from PDFs in docs/domains/ into
ABOUTME: data/standards-index/chunks.jsonl and builds a BM25 index.

Usage:
    python ingest_standards.py ingest [--source docs/domains/] [--out data/standards-index/]
    python ingest_standards.py build-index [--out data/standards-index/]
"""

import argparse
import hashlib
import json
import pickle
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Page extraction
# ---------------------------------------------------------------------------

CODE_FAMILY_PATTERNS = [
    ("DNV", r"\bdnv\b"),
    ("API", r"\bapi\b"),
    ("ABS", r"\babs\b"),
    ("ISO", r"\biso\b"),
    ("BS",  r"\bbs[_\-\s]"),
    ("NORSOK", r"\bnorsok\b"),
    ("ASTM", r"\bastm\b"),
]


def detect_code_family(filename: str) -> str:
    """Detect code family from filename using regex patterns."""
    lower = filename.lower()
    for family, pattern in CODE_FAMILY_PATTERNS:
        if re.search(pattern, lower):
            return family
    return "UNKNOWN"


def extract_pages(pdf_path: str) -> list:
    """
    Extract page-level text chunks from a PDF using PyMuPDF.

    Args:
        pdf_path: Absolute or relative path to a PDF file.

    Returns:
        List of dicts with keys: chunk_id, doc_name, page, code_family, text, source_path.
        Pages with no extractable text are silently skipped.
    """
    try:
        import fitz
    except ImportError:
        print("ERROR: pymupdf not installed. Run: uv run --no-project --with pymupdf python", file=sys.stderr)
        return []

    path = Path(pdf_path)
    doc_name = path.name
    code_family = detect_code_family(doc_name)
    chunks = []

    try:
        doc = fitz.open(str(path))
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if not text.strip():
                continue
            chunk_id = f"{doc_name}::p{page_num}::0"
            chunks.append({
                "chunk_id": chunk_id,
                "doc_name": doc_name,
                "page": page_num,
                "code_family": code_family,
                "text": text.strip(),
                "source_path": str(path.resolve()),
            })
        doc.close()
    except Exception as exc:
        print(f"WARNING: could not extract {pdf_path}: {exc}", file=sys.stderr)

    return chunks
```

- [ ] **Step 4: Run tests — verify PASS**
```bash
uv run --no-project --with pymupdf --with rank_bm25 python -m pytest tests/standards/test_ingest_standards.py::test_extract_pages_returns_list tests/standards/test_ingest_standards.py::test_extract_pages_has_correct_fields tests/standards/test_ingest_standards.py::test_extract_pages_page_numbers_start_at_one tests/standards/test_ingest_standards.py::test_extract_pages_skips_empty_text tests/standards/test_ingest_standards.py::test_detect_code_family_from_path -v
```
Expected: 5 PASS

- [ ] **Step 5: Commit**
```bash
git add scripts/standards/ingest_standards.py tests/standards/test_ingest_standards.py tests/standards/conftest.py
git commit -m "feat(standards): page extraction + code family detection (WRK-1132)"
```

---

## Task 3: TDD — JSONL persistence and ingest command

**Files:**
- Modify: `tests/standards/test_ingest_standards.py` (add tests)
- Modify: `scripts/standards/ingest_standards.py` (add ingest_directory + main)

- [ ] **Step 1: Write failing tests for ingest_directory()**

Append to `tests/standards/test_ingest_standards.py`:
```python
def test_ingest_directory_writes_chunks_jsonl(mini_pdf, tmp_path):
    from scripts.standards.ingest_standards import ingest_directory
    out_dir = tmp_path / "standards-index"
    ingest_directory(str(mini_pdf.parent), str(out_dir))
    chunks_path = out_dir / "chunks.jsonl"
    assert chunks_path.exists()
    with open(chunks_path) as f:
        lines = [json.loads(l) for l in f if l.strip()]
    assert len(lines) >= 1
    assert lines[0]["doc_name"] == "mini.pdf"
    assert lines[0]["page"] >= 1


def test_ingest_directory_skips_non_pdf(tmp_path):
    from scripts.standards.ingest_standards import ingest_directory
    (tmp_path / "notes.txt").write_text("ignore me")
    out_dir = tmp_path / "out"
    ingest_directory(str(tmp_path), str(out_dir))
    chunks_path = out_dir / "chunks.jsonl"
    if chunks_path.exists():
        with open(chunks_path) as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) == 0
```

- [ ] **Step 2: Run tests — verify FAIL**
```bash
uv run --no-project --with pymupdf --with rank_bm25 python -m pytest tests/standards/test_ingest_standards.py::test_ingest_directory_writes_chunks_jsonl tests/standards/test_ingest_standards.py::test_ingest_directory_skips_non_pdf -v 2>&1 | tail -10
```
Expected: FAIL (function not defined)

- [ ] **Step 3: Implement ingest_directory()**

Append to `scripts/standards/ingest_standards.py`:
```python
# ---------------------------------------------------------------------------
# JSONL persistence
# ---------------------------------------------------------------------------

def ingest_directory(source_dir: str, out_dir: str) -> int:
    """
    Walk source_dir for PDFs, extract page chunks, write to out_dir/chunks.jsonl.

    Args:
        source_dir: Directory containing PDF files.
        out_dir: Output directory; chunks.jsonl written here.

    Returns:
        Number of chunks written.
    """
    source = Path(source_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    chunks_path = out / "chunks.jsonl"
    count = 0

    with open(chunks_path, "w") as fh:
        for pdf_file in sorted(source.glob("*.pdf")):
            chunks = extract_pages(str(pdf_file))
            for chunk in chunks:
                fh.write(json.dumps(chunk) + "\n")
                count += 1

    return count
```

- [ ] **Step 4: Run tests — verify PASS**
```bash
uv run --no-project --with pymupdf --with rank_bm25 python -m pytest tests/standards/test_ingest_standards.py -v
```
Expected: all PASS

- [ ] **Step 5: Commit**
```bash
git add scripts/standards/ingest_standards.py tests/standards/test_ingest_standards.py
git commit -m "feat(standards): ingest_directory writes chunks.jsonl (WRK-1132)"
```

---

## Task 4: TDD — BM25 index build

**Files:**
- Modify: `tests/standards/test_ingest_standards.py` (add BM25 tests)
- Modify: `scripts/standards/ingest_standards.py` (add build_index)

- [ ] **Step 1: Write failing BM25 tests**

Append to `tests/standards/test_ingest_standards.py`:
```python
def test_build_index_writes_pickle(tmp_path):
    from scripts.standards.ingest_standards import build_index
    chunks = [
        {"chunk_id": "a::p1::0", "doc_name": "a.pdf", "page": 1,
         "code_family": "DNV", "text": "cathodic protection design requirements", "source_path": "/a.pdf"},
        {"chunk_id": "b::p1::0", "doc_name": "b.pdf", "page": 1,
         "code_family": "API", "text": "riser design fatigue analysis", "source_path": "/b.pdf"},
    ]
    chunks_path = tmp_path / "chunks.jsonl"
    with open(chunks_path, "w") as f:
        for c in chunks:
            f.write(json.dumps(c) + "\n")
    build_index(str(tmp_path))
    assert (tmp_path / "bm25.pkl").exists()


def test_build_index_pickle_loads_correctly(tmp_path):
    from scripts.standards.ingest_standards import build_index
    chunks = [
        {"chunk_id": "x::p1::0", "doc_name": "x.pdf", "page": 1,
         "code_family": "DNV", "text": "wall thickness pressure containment", "source_path": "/x.pdf"},
    ]
    chunks_path = tmp_path / "chunks.jsonl"
    with open(chunks_path, "w") as f:
        f.write(json.dumps(chunks[0]) + "\n")
    build_index(str(tmp_path))
    with open(tmp_path / "bm25.pkl", "rb") as f:
        data = pickle.load(f)
    assert "bm25" in data
    assert "chunks" in data
    assert len(data["chunks"]) == 1
```

- [ ] **Step 2: Run tests — verify FAIL**
```bash
uv run --no-project --with pymupdf --with rank_bm25 python -m pytest tests/standards/test_ingest_standards.py::test_build_index_writes_pickle tests/standards/test_ingest_standards.py::test_build_index_pickle_loads_correctly -v 2>&1 | tail -10
```
Expected: FAIL

- [ ] **Step 3: Implement build_index()**

Append to `scripts/standards/ingest_standards.py`:
```python
# ---------------------------------------------------------------------------
# BM25 index
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list:
    """Simple whitespace+punctuation tokenizer."""
    return re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()


def build_index(out_dir: str) -> None:
    """
    Build BM25 index from chunks.jsonl and serialize to bm25.pkl.

    Args:
        out_dir: Directory containing chunks.jsonl; bm25.pkl written here.
    """
    from rank_bm25 import BM25Okapi

    out = Path(out_dir)
    chunks_path = out / "chunks.jsonl"
    if not chunks_path.exists():
        raise FileNotFoundError(f"chunks.jsonl not found in {out_dir}. Run ingest first.")

    chunks = []
    with open(chunks_path) as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))

    if not chunks:
        raise ValueError("No chunks found in chunks.jsonl — nothing to index.")

    tokenized = [_tokenize(c["text"]) for c in chunks]
    bm25 = BM25Okapi(tokenized)

    with open(out / "bm25.pkl", "wb") as f:
        pickle.dump({"bm25": bm25, "chunks": chunks}, f)

    print(f"Built BM25 index over {len(chunks)} chunks → {out}/bm25.pkl")
```

- [ ] **Step 4: Run all tests — verify PASS**
```bash
uv run --no-project --with pymupdf --with rank_bm25 python -m pytest tests/standards/test_ingest_standards.py -v
```
Expected: all PASS

- [ ] **Step 5: Commit**
```bash
git add scripts/standards/ingest_standards.py tests/standards/test_ingest_standards.py
git commit -m "feat(standards): BM25 index build + pickle serialization (WRK-1132)"
```

---

## Task 5: TDD — Query logic

**Files:**
- Create: `tests/standards/test_query_logic.py`
- Modify: `scripts/standards/ingest_standards.py` (add query_standards)

- [ ] **Step 1: Write failing query tests**

Create `tests/standards/test_query_logic.py`:
```python
import json
import pickle
import pytest
from pathlib import Path


@pytest.fixture
def built_index(tmp_path):
    """Fixture: pre-built index with 3 known chunks."""
    from scripts.standards.ingest_standards import build_index
    chunks = [
        {"chunk_id": "DNV::p1::0", "doc_name": "DNV-RP-C203.pdf", "page": 1,
         "code_family": "DNV", "text": "fatigue design criteria S-N curves DNV offshore structures", "source_path": "/dnv.pdf"},
        {"chunk_id": "API::p2::0", "doc_name": "API-RP-2RD.pdf", "page": 2,
         "code_family": "API", "text": "riser design wall thickness pressure containment API offshore", "source_path": "/api.pdf"},
        {"chunk_id": "ABS::p1::0", "doc_name": "ABS-offshore-structures.pdf", "page": 1,
         "code_family": "ABS", "text": "cathodic protection impressed current design ABS rules", "source_path": "/abs.pdf"},
    ]
    with open(tmp_path / "chunks.jsonl", "w") as f:
        for c in chunks:
            f.write(json.dumps(c) + "\n")
    build_index(str(tmp_path))
    return tmp_path


def test_query_returns_results(built_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("fatigue S-N", str(built_index))
    assert len(results) >= 1


def test_query_ranks_best_match_first(built_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("fatigue S-N curves", str(built_index))
    assert results[0]["doc_name"] == "DNV-RP-C203.pdf"


def test_query_filters_by_code_family(built_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("design", str(built_index), code_family="API")
    assert all(r["code_family"] == "API" for r in results)


def test_query_returns_page_citation(built_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("cathodic protection", str(built_index))
    assert "page" in results[0]
    assert isinstance(results[0]["page"], int)
    assert results[0]["page"] >= 1


def test_query_no_results_returns_empty_list(built_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("xyzzy_nonexistent_term", str(built_index))
    assert isinstance(results, list)
    assert len(results) == 0
```

- [ ] **Step 2: Run tests — verify FAIL**
```bash
uv run --no-project --with pymupdf --with rank_bm25 python -m pytest tests/standards/test_query_logic.py -v 2>&1 | tail -15
```
Expected: FAIL (query_standards not defined)

- [ ] **Step 3: Implement query_standards()**

Append to `scripts/standards/ingest_standards.py`:
```python
# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

def query_standards(
    query: str,
    index_dir: str,
    code_family: str = None,
    limit: int = 10,
) -> list:
    """
    Query the BM25 index and return ranked chunks with page citations.

    Args:
        query: Natural-language search query.
        index_dir: Directory containing bm25.pkl.
        code_family: Optional code filter (DNV, API, ABS, BS, ISO, NORSOK, ASTM).
        limit: Maximum results to return.

    Returns:
        List of chunk dicts sorted by relevance, filtered by code_family if provided.
        Returns [] if index not found or no matches.
    """
    pkl_path = Path(index_dir) / "bm25.pkl"
    if not pkl_path.exists():
        return []

    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    bm25 = data["bm25"]
    chunks = data["chunks"]

    tokens = _tokenize(query)
    if not tokens:
        return []

    scores = bm25.get_scores(tokens)

    # Pair scores with chunks, apply code_family filter, sort
    ranked = sorted(
        [(score, chunk) for score, chunk in zip(scores, chunks)
         if score > 0 and (code_family is None or chunk.get("code_family") == code_family.upper())],
        key=lambda x: x[0],
        reverse=True,
    )

    return [chunk for _, chunk in ranked[:limit]]
```

- [ ] **Step 4: Run all tests — verify PASS**
```bash
uv run --no-project --with pymupdf --with rank_bm25 python -m pytest tests/standards/ -v
```
Expected: all PASS

- [ ] **Step 5: Add CLI entry point to ingest_standards.py**

Append to `scripts/standards/ingest_standards.py`:
```python
# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Standards ingestion and index build")
    sub = parser.add_subparsers(dest="cmd")

    p_ingest = sub.add_parser("ingest", help="Extract page chunks from PDFs")
    p_ingest.add_argument("--source", default="docs/domains/", help="Source PDF directory")
    p_ingest.add_argument("--out", default="data/standards-index/", help="Output directory")

    p_build = sub.add_parser("build-index", help="Build BM25 index from chunks.jsonl")
    p_build.add_argument("--out", default="data/standards-index/", help="Index directory")

    args = parser.parse_args()

    if args.cmd == "ingest":
        n = ingest_directory(args.source, args.out)
        print(f"Ingested {n} chunks from {args.source} → {args.out}/chunks.jsonl")
    elif args.cmd == "build-index":
        build_index(args.out)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Commit**
```bash
git add scripts/standards/ingest_standards.py tests/standards/test_query_logic.py
git commit -m "feat(standards): query_standards BM25 + code family filter (WRK-1132)"
```

---

## Task 6: CLI bash wrapper — query-standards.sh

**Files:**
- Create: `scripts/standards/query-standards.sh`

- [ ] **Step 1: Create CLI bash wrapper**

Create `scripts/standards/query-standards.sh`:
```bash
#!/usr/bin/env bash
# query-standards.sh — Search engineering standards by natural-language query
# Usage: query-standards.sh "query" [--code DNV|API|ABS|BS|ISO] [--topic CP|fatigue|...] [--limit N]
# Returns: Ranked standard sections with doc name + page number citations
# Requires: data/standards-index/bm25.pkl (run ingest_standards.py ingest + build-index first)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
INDEX_DIR="${REPO_ROOT}/data/standards-index"

QUERY=""
CODE=""
TOPIC=""
LIMIT=10

while [[ $# -gt 0 ]]; do
    case "$1" in
        --code)    CODE="$2";    shift 2 ;;
        --topic)   TOPIC="$2";   shift 2 ;;
        --limit)   LIMIT="$2";   shift 2 ;;
        --index)   INDEX_DIR="$2"; shift 2 ;;
        -*)        echo "Unknown flag: $1" >&2; exit 1 ;;
        *)         QUERY="$1";   shift ;;
    esac
done

if [[ -z "$QUERY" && -z "$TOPIC" ]]; then
    echo "Usage: query-standards.sh \"query\" [--code DNV|API|ABS|BS|ISO] [--topic TOPIC] [--limit N]" >&2
    exit 1
fi

# Combine query + topic if both provided
FULL_QUERY="${QUERY}"
if [[ -n "$TOPIC" ]]; then
    FULL_QUERY="${FULL_QUERY} ${TOPIC}"
fi

uv run --no-project --with pymupdf --with rank_bm25 python3 - <<PYEOF
import sys
sys.path.insert(0, "${REPO_ROOT}")
from scripts.standards.ingest_standards import query_standards

query = "${FULL_QUERY}".strip()
code = "${CODE}" or None
limit = ${LIMIT}
index_dir = "${INDEX_DIR}"

results = query_standards(query, index_dir, code_family=code, limit=limit)

if not results:
    print("No results found.")
    if code:
        print(f"(Filtered to code family: {code})")
    sys.exit(0)

print(f"\n## Standards Search: '{query}'" + (f" [code: {code}]" if code else "") + "\n")
for i, r in enumerate(results, 1):
    doc = r["doc_name"]
    page = r["page"]
    family = r.get("code_family", "")
    snippet = r["text"][:200].replace("\n", " ").strip()
    print(f"{i}. **{doc}** (p.{page}) [{family}]")
    print(f"   > {snippet}...")
    print()
PYEOF
```

- [ ] **Step 2: Make executable**
```bash
chmod +x scripts/standards/query-standards.sh
```

- [ ] **Step 3: Commit**
```bash
git add scripts/standards/query-standards.sh
git commit -m "feat(standards): query-standards.sh CLI bash wrapper (WRK-1132)"
```

---

## Task 7: Integration test — end-to-end

**Files:**
- Create: `tests/standards/test_integration.py`

- [ ] **Step 1: Write integration test**

Create `tests/standards/test_integration.py`:
```python
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def e2e_index(tmp_path_factory):
    """Build a real BM25 index from a generated multi-page PDF."""
    import fitz
    from scripts.standards.ingest_standards import ingest_directory, build_index

    tmp = tmp_path_factory.mktemp("e2e")
    src = tmp / "docs"
    src.mkdir()
    idx = tmp / "index"

    # Create realistic test PDF
    doc = fitz.open()
    pages = [
        "Cathodic protection system design per DNV-RP-B401 section 5. Impressed current ICCP.",
        "API RP 2RD riser wall thickness pressure containment design factor.",
        "S-N fatigue curves DNV-RP-C203 offshore structural steel details.",
    ]
    for text in pages:
        p = doc.new_page()
        p.insert_text((50, 72), text)
    doc.save(str(src / "DNV-test-standard.pdf"))

    ingest_directory(str(src), str(idx))
    build_index(str(idx))
    return idx


def test_e2e_query_returns_results(e2e_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("cathodic protection", str(e2e_index))
    assert len(results) >= 1


def test_e2e_query_with_code_filter(e2e_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("design", str(e2e_index), code_family="DNV")
    assert all(r["code_family"] == "DNV" for r in results)


def test_e2e_query_returns_page_citations(e2e_index):
    from scripts.standards.ingest_standards import query_standards
    results = query_standards("fatigue curves", str(e2e_index))
    assert results[0]["page"] >= 1
    assert results[0]["doc_name"].endswith(".pdf")


def test_e2e_speed(e2e_index):
    """Query must complete in under 5 seconds."""
    from scripts.standards.ingest_standards import query_standards
    start = time.time()
    query_standards("wall thickness pressure", str(e2e_index))
    elapsed = time.time() - start
    assert elapsed < 5.0, f"Query took {elapsed:.2f}s — must be < 5s"
```

- [ ] **Step 2: Run integration tests**
```bash
uv run --no-project --with pymupdf --with rank_bm25 python -m pytest tests/standards/test_integration.py -v
```
Expected: all PASS

- [ ] **Step 3: Run full test suite**
```bash
uv run --no-project --with pymupdf --with rank_bm25 python -m pytest tests/standards/ -v
```
Expected: all PASS, 0 FAIL

- [ ] **Step 4: Commit**
```bash
git add tests/standards/test_integration.py
git commit -m "test(standards): integration tests with speed gate (WRK-1132)"
```

---

## Verification

### Run all tests
```bash
uv run --no-project --with pymupdf --with rank_bm25 python -m pytest tests/standards/ -v
```
Expected: all PASS, 0 FAIL, < 30s

### Smoke test the CLI (if docs/domains/ has PDFs)
```bash
# If docs/domains/ has real PDFs:
uv run --no-project --with pymupdf --with rank_bm25 python scripts/standards/ingest_standards.py ingest
uv run --no-project --with pymupdf --with rank_bm25 python scripts/standards/ingest_standards.py build-index
bash scripts/standards/query-standards.sh "cathodic protection design" --code DNV
```

### Speed check
```bash
time bash scripts/standards/query-standards.sh "wall thickness pressure containment"
```
Expected: < 5s

### Acceptance Criteria checklist
- [ ] AC1: PDF ingestion pipeline for docs/domains/ — `ingest_standards.py ingest`
- [ ] AC2: Doc name + page number in results — `chunk["doc_name"]` + `chunk["page"]`
- [ ] AC3: Code family filter — `--code DNV` maps to `code_family="DNV"`
- [ ] AC4: CLI < 5s — verified by test_e2e_speed
- [ ] AC5: Codex cross-review — submit `scripts/review/cross-review.sh` post-implementation
