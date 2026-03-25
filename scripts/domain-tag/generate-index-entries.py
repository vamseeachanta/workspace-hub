#!/usr/bin/env python3
"""
Generate document-index JSONL entries from riser-eng-job domain classification.

Usage:
    python generate-index-entries.py [--output FILE] [--append-to FILE]
"""

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone

# Load the classifier module (dash in filename requires importlib)
_script_dir = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "classifier", os.path.join(_script_dir, "classify-riser-eng-job.py"))
_classifier = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_classifier)
classify_file = _classifier.classify_file

SOURCE_DIR = "/mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job"


def get_project(filepath):
    rel = os.path.relpath(filepath, SOURCE_DIR)
    return rel.split(os.sep)[0] if os.sep in rel else ""


def generate_entries():
    entries = []
    for root, _dirs, files in os.walk(SOURCE_DIR):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in {".pdf", ".doc", ".docx"}:
                continue

            fpath = os.path.join(root, fname)
            try:
                stat = os.stat(fpath)
                size_mb = round(stat.st_size / (1024 * 1024), 3)
                mtime = datetime.fromtimestamp(
                    stat.st_mtime, tz=timezone.utc
                ).strftime("%Y-%m-%dT%H:%M:%S")
            except OSError:
                size_mb = 0
                mtime = ""

            project = get_project(fpath)
            classification = classify_file(fpath, project)
            primary_domain = classification["domains"][0] if classification["domains"] else "risers"

            entries.append({
                "path": fpath,
                "host": "ace-linux-1",
                "source": "riser_eng_job",
                "ext": ext.lstrip("."),
                "size_mb": size_mb,
                "mtime": mtime,
                "content_hash": "",
                "is_cad": False,
                "domain": primary_domain,
                "domains": classification["domains"],
                "doc_type": classification["doc_type"],
                "project": project,
                "summary": None,
                "status": "indexed",
                "target_repos": ["digitalmodel"],
                "readability": "native",
                "path_category": "riser-engineering",
                "path_subcategory": project,
            })

    return entries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="-", help="Output file (- for stdout)")
    parser.add_argument("--append-to", help="Append to existing index.jsonl")
    args = parser.parse_args()

    print(f"Scanning {SOURCE_DIR}...", file=sys.stderr)
    entries = generate_entries()
    print(f"Generated {len(entries)} index entries", file=sys.stderr)

    if args.append_to:
        with open(args.append_to, "a") as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"Appended {len(entries)} entries to {args.append_to}", file=sys.stderr)
    elif args.output == "-":
        for entry in entries:
            print(json.dumps(entry, ensure_ascii=False))
    else:
        with open(args.output, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"Written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
