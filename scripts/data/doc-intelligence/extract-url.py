#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml",
#     "pdfplumber",
#     "requests",
#     "beautifulsoup4",
# ]
# ///
"""CLI entry point for URL-based document extraction.

Usage:
    python extract-url.py --url <url> [--output <path>] [--domain <domain>]

Exit codes: 0=success, 1=fetch failed, 2=robots.txt blocked, 3=extraction failed
"""

import sys
from pathlib import Path

# Ensure repo root is on PYTHONPATH when run directly
_repo_root = str(Path(__file__).resolve().parents[3])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from scripts.data.doc_intelligence.extract_url import main

if __name__ == "__main__":
    sys.exit(main())
