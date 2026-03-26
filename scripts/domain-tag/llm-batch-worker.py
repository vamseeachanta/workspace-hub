#!/usr/bin/env python3
"""
WRK-1412: LLM batch worker for classifying riser-eng-job unknown documents.

Usage:
    python scripts/domain-tag/llm-batch-worker.py --shard 0 --total 10
"""

import argparse
import hashlib
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import importlib.util

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [shard-%(shard)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[1]

# Load classify_riser_eng_job.py dynamically
spec = importlib.util.spec_from_file_location("classify_riser", SCRIPT_DIR / "classify-riser-eng-job.py")
classify_riser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classify_riser)

SOURCE_DIR = "/mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job"
RESULTS_DIR = Path(SOURCE_DIR) / "llm-classifications"

CLAUDE_TIMEOUT = 90

DOC_TYPES = list(classify_riser.DOC_TYPE_MAP.values())
DOMAINS = list(classify_riser.DOMAIN_KEYWORDS.keys())

PROMPT = (
    "You are classifying a subsea engineering document. "
    "Reply with JSON only — no markdown fences, no extra text:\n"
    '{"doc_type":"one of [' + ",".join(DOC_TYPES) + ']",'
    '"domains":["one to three of [' + ",".join(DOMAINS) + ']"]}\n'
    "Use the text provided to classify accurately. If you are unsure, pick the closest match."
)

def extract_pdf_text(path: str, max_pages: int = 2) -> str:
    try:
        r = subprocess.run(
            ["pdftotext", "-f", "1", "-l", str(max_pages), "-q", path, "-"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout[:6000]
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        logging.debug(f"Failed to read PDF {path}: {e}")
    except Exception as e:
        logging.debug(f"Failed to read PDF {path}: {e}")
    return ""

def claude_classify(text: str, filename: str) -> dict:
    if not text.strip():
        return {}
    
    context = f"Filename: {filename}\n\nDocument text:\n{text}"
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)
    
    try:
        r = subprocess.run(
            [
                "claude", "-p", PROMPT,
                "--output-format", "json",
                "--model", "haiku",
                "--no-session-persistence",
                "--dangerously-skip-permissions",
                "--tools", "",
                "--max-turns", "1",
            ],
            input=context,
            capture_output=True,
            text=True,
            timeout=CLAUDE_TIMEOUT,
            env=env,
        )
        if r.returncode != 0:
            logging.warning("claude non-zero: %s", r.stderr[:200])
            return {}
        
        outer = json.loads(r.stdout)
        raw = outer.get("result", "")
        if raw.startswith("```"):
            lines = raw.strip().split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
        return json.loads(raw.strip())
    except Exception as e:
        logging.warning("claude error: %s", e)
    return {}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--total", type=int, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Inject shard into log format
    old_factory = logging.getLogRecordFactory()
    shard_val = args.shard
    def record_factory(*a, **kw):
        rec = old_factory(*a, **kw)
        rec.shard = shard_val
        return rec
    logging.setLogRecordFactory(record_factory)
    logger = logging.getLogger()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Scanning %s...", SOURCE_DIR)
    all_results = classify_riser.scan_and_classify(SOURCE_DIR)
    
    # Filter for unknown PDFs
    unknowns = [
        r for r in all_results 
        if r["doc_type"] == "unknown" and r["path"].lower().endswith(".pdf")
    ]
    
    # Sort for deterministic sharding
    unknowns.sort(key=lambda x: x["path"])
    my_shard = [r for i, r in enumerate(unknowns) if i % args.total == args.shard]
    
    logger.info("Total unknowns: %d (PDFs only). My shard: %d files.", len(unknowns), len(my_shard))

    done = skipped = errors = 0

    for r in my_shard:
        path = r["path"]
        sha = hashlib.sha256(path.encode('utf-8')).hexdigest()
        out_file = RESULTS_DIR / f"{sha}.json"
        
        if out_file.exists():
            skipped += 1
            continue
            
        if args.dry_run:
            logger.info("[DRY] Would classify: %s", path)
            done += 1
            continue

        text = extract_pdf_text(path)
        if not text:
            # Save empty result to avoid retrying
            out_file.write_text(json.dumps({
                "path": path,
                "error": "no_text_extracted",
                "llm_at": datetime.now(timezone.utc).isoformat()
            }))
            errors += 1
            continue
            
        filename = os.path.basename(path)
        classification = claude_classify(text, filename)
        
        if classification:
            classification["path"] = path
            classification["llm_at"] = datetime.now(timezone.utc).isoformat()
            out_file.write_text(json.dumps(classification, indent=2))
            done += 1
        else:
            errors += 1
            
        if (done + skipped + errors) % 10 == 0:
            logger.info("Progress: done=%d skipped=%d errors=%d", done, skipped, errors)

    logger.info("COMPLETE: done=%d skipped=%d errors=%d", done, skipped, errors)
    return 0

if __name__ == "__main__":
    sys.exit(main())