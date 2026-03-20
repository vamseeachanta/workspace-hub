#!/usr/bin/env bash
# gemini-crosscheck-naval.sh — Gemini spot-check of extracted numerical values
# Samples 20% of worked examples and asks Gemini to verify values.
# Part of multi-provider extraction pipeline (WRK-1339).
#
# Usage:
#   bash scripts/data/doc-intelligence/gemini-crosscheck-naval.sh [--sample-pct 20]
#
# Prerequisites:
#   - worked_examples.jsonl must exist with deep extraction records
#   - gemini CLI must be available (echo content | gemini -p "prompt" -y)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
JSONL="${REPO_ROOT}/data/doc-intelligence/worked_examples.jsonl"
REPORT="${REPO_ROOT}/data/doc-intelligence/extraction-reports/naval-architecture/crosscheck-report.yaml"
SAMPLE_PCT="${2:-20}"

if [[ ! -f "${JSONL}" ]]; then
    echo "ERROR: ${JSONL} not found."
    exit 1
fi

# Sample records using Python
uv run --no-project python - "${JSONL}" "${REPORT}" "${SAMPLE_PCT}" <<'PYEOF'
import json
import random
import sys
import subprocess
from pathlib import Path

jsonl_path = sys.argv[1]
report_path = sys.argv[2]
sample_pct = int(sys.argv[3])

# Load all deep-extraction examples with use_as_test=true
examples = []
with open(jsonl_path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("use_as_test") and rec.get("expected_value") is not None:
            examples.append(rec)

if not examples:
    print("No testable examples found in JSONL.")
    sys.exit(0)

# Sample
n_sample = max(1, len(examples) * sample_pct // 100)
sample = random.sample(examples, min(n_sample, len(examples)))
print(f"Sampled {len(sample)} of {len(examples)} testable examples ({sample_pct}%)")

results = []
for ex in sample:
    book = ex.get("source_book", "unknown")
    page = ex.get("page", "?")
    number = ex.get("number", "?")
    expected = ex.get("expected_value")
    unit = ex.get("output_unit", "")

    prompt = (
        f"Verify this extraction from '{book}' page {page}, Example {number}. "
        f"The extracted expected value is {expected} {unit}. "
        f"Is this value correct based on the textbook? "
        f"Reply with JSON: {{\"correct\": true/false, \"reason\": \"...\"}}"
    )

    result = {
        "book": book,
        "page": page,
        "number": number,
        "extracted_value": expected,
        "unit": unit,
        "gemini_verified": None,
        "reason": "gemini not available",
    }

    try:
        proc = subprocess.run(
            ["gemini", "-p", prompt, "-y", "--output-format", "json"],
            input="",
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            resp = json.loads(proc.stdout.strip())
            result["gemini_verified"] = resp.get("correct")
            result["reason"] = resp.get("reason", "")
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        result["reason"] = "gemini unavailable or timed out"

    results.append(result)
    status = "AGREE" if result["gemini_verified"] else "SKIP"
    print(f"  {status}: {book} p.{page} Ex.{number} = {expected} {unit}")

# Write report
agreed = sum(1 for r in results if r["gemini_verified"] is True)
disagreed = sum(1 for r in results if r["gemini_verified"] is False)
skipped = sum(1 for r in results if r["gemini_verified"] is None)

report_data = {
    "summary": {
        "total_sampled": len(results),
        "agreed": agreed,
        "disagreed": disagreed,
        "skipped": skipped,
        "agreement_rate": f"{agreed / max(len(results), 1) * 100:.1f}%",
    },
    "results": results,
}

Path(report_path).parent.mkdir(parents=True, exist_ok=True)
import yaml
with open(report_path, "w") as f:
    yaml.dump(report_data, f, default_flow_style=False, sort_keys=False)

print(f"\nReport: {report_path}")
print(f"Agreement: {agreed}/{len(results)} ({agreed / max(len(results), 1) * 100:.1f}%)")
PYEOF
