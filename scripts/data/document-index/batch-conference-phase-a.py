#!/usr/bin/env python3
"""
Batch Conference Paper Metadata Extraction (Phase A)
GitHub Issue: #1862

Extracts basic metadata (title, year, page count, etc.) from PDF files
listed in the conference index batch. This is a non-LLM, high-speed
extraction pass.

Usage:
    python batch-conference-phase-a.py --conferences OTC OMAE --limit 500
    python batch-conference-phase-a.py --conferences DOT --batch-size 50
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import pypdf
except ImportError:
    print("ERROR: pypdf is required. Install with: pip install pypdf", file=sys.stderr)
    sys.exit(1)

# --- Configuration ---
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
BATCH_FILE = WORKSPACE_ROOT / "data" / "document-index" / "conference-index-batch.jsonl"
DEFAULT_OUTPUT = WORKSPACE_ROOT / "data" / "document-index" / "conference-phase-a-results.jsonl"
CHECKPOINT_FILE = WORKSPACE_ROOT / ".cache" / "conference-phase-a-checkpoint.json"

# --- Helper Functions ---

def parse_year_from_path(path_str: str):
    """Extracts a 4-digit year from a path, prioritizing later years."""
    matches = re.findall(r'\b(19[89]\d|20[0-2]\d)\b', path_str)
    return int(matches[-1]) if matches else None

def clean_text(text: str):
    """Basic cleaning for extracted PDF text."""
    return text.replace('\u0000', ' ').strip()

def extract_title_from_filename(filename: str):
    """Extracts a title from a filename, cleaning it up."""
    title = Path(filename).stem
    title = title.replace('_', ' ').replace('-', ' ')
    # Simple title case, but don't mess with acronyms
    return ' '.join(word.capitalize() if not word.isupper() else word for word in title.split())

def process_pdf(file_path: str, conference: str):
    """
    Extracts metadata from a single PDF file.
    Returns a dictionary of metadata or None on failure.
    """
    try:
        pdf_reader = pypdf.PdfReader(file_path)
        meta = pdf_reader.metadata
        page_count = len(pdf_reader.pages)
        file_size = os.path.getsize(file_path)

        # 1. Title Extraction
        title = None
        if meta and meta.title:
            title = clean_text(meta.title)
        
        # If no metadata title, try first page content
        if not title:
            try:
                # Look for the largest font text on the first page - a common heuristic
                # This is complex with pypdf, so we'll do a simpler text extraction for now
                first_page_text = pdf_reader.pages[0].extract_text(extraction_mode="layout", line_gap=0)
                # A simple heuristic: first non-empty line
                lines = [line.strip() for line in first_page_text.split('\\n') if line.strip()]
                if lines:
                    title = clean_text(lines[0])
            except Exception:
                pass # Text extraction can fail

        # Fallback to filename
        if not title:
            title = extract_title_from_filename(os.path.basename(file_path))

        # 2. Year Extraction
        year = parse_year_from_path(file_path)

        return {
            "conference": conference,
            "path": file_path,
            "title": title,
            "year": year,
            "page_count": page_count,
            "file_size_bytes": file_size,
            "extraction_status": "success"
        }

    except pypdf.errors.PdfReadError:
        return {
            "path": file_path, "extraction_status": "error_corrupt_pdf"
        }
    except Exception as e:
        return {
            "path": file_path, "extraction_status": f"error_unknown: {e}"
        }

def save_checkpoint(processed_paths, output_file):
    CHECKPOINT_FILE.parent.mkdir(exist_ok=True)
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({
            "processed_count": len(processed_paths),
            "processed_paths_set": list(processed_paths),
            "output_file": str(output_file)
        }, f)

def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r') as f:
            try:
                data = json.load(f)
                # returning a set for faster lookups
                return set(data.get("processed_paths_set", []))
            except json.JSONDecodeError:
                return set()
    return set()


# --- Main Logic ---

def main():
    parser = argparse.ArgumentParser(description="Batch Conference Paper Metadata Extraction (Phase A)")
    parser.add_argument(
        '--conferences',
        nargs='+',
        required=True,
        help="List of conference names to process (e.g., OTC OMAE)"
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help="Maximum number of PDFs to process"
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help="How many files to process before saving results"
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output JSONL file (default: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        '--force-rerun',
        action='store_true',
        help="Ignore checkpoint and rerun all files."
    )

    args = parser.parse_args()
    
    # --- File Loading ---
    print("Loading batch file...")
    with open(BATCH_FILE, 'r') as f:
        all_entries = [json.loads(line) for line in f]
    
    # --- Filtering ---
    print(f"Filtering for conferences: {', '.join(args.conferences)}")
    target_entries = [
        e for e in all_entries
        if e.get('conference') in args.conferences and e.get('extension') == '.pdf'
    ]
    
    if args.limit:
        target_entries = target_entries[:args.limit]
        
    total_to_process = len(target_entries)
    print(f"Found {total_to_process} PDFs to process.")

    # --- Checkpoint Handling ---
    processed_paths = set()
    if not args.force_rerun:
        processed_paths = load_checkpoint()
        print(f"Loaded checkpoint. {len(processed_paths)} files already processed. Resuming...")
        target_entries = [e for e in target_entries if e['path'] not in processed_paths]
        print(f"{len(target_entries)} remaining to process.")

    # --- Processing Loop ---
    results_batch = []
    processed_count = 0
    
    for entry in target_entries:
        file_path = entry['path']
        conference = entry['conference']
        
        result = process_pdf(file_path, conference)
        if result:
            results_batch.append(result)

        processed_count += 1
        processed_paths.add(file_path)

        if len(results_batch) >= args.batch_size:
            with open(args.output, 'a') as f:
                for res in results_batch:
                    f.write(json.dumps(res) + '\n')
            
            save_checkpoint(processed_paths, args.output)
            print(f"Processed {len(processed_paths)} / {total_to_process}... (checkpoint saved)")
            results_batch = []

    # Final write for any remaining results
    if results_batch:
        with open(args.output, 'a') as f:
            for res in results_batch:
                f.write(json.dumps(res) + '\n')
    
    save_checkpoint(processed_paths, args.output)
    print(f"Finished processing. Total processed: {len(processed_paths)} / {total_to_process}.")
    
    # Clean up checkpoint on full completion
    if len(processed_paths) >= total_to_process:
        print("All files processed. Removing checkpoint.")
        CHECKPOINT_FILE.unlink(missing_ok=True)

if __name__ == "__main__":
    main()
