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
import json
import pickle
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Page extraction
# ---------------------------------------------------------------------------

CODE_FAMILY_PATTERNS = [
    ("DNV", r"(?<![a-z])dnv(?![a-z])"),
    ("API", r"(?<![a-z])api(?![a-z])"),
    ("ABS", r"(?<![a-z])abs(?![a-z])"),
    ("BS",  r"(?<![a-z])bs[_\-\s]"),
    ("ISO", r"(?<![a-z])iso(?![a-z])"),
    ("NORSOK", r"norsok"),
    ("ASTM", r"(?<![a-z])astm(?![a-z])"),
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
