#!/usr/bin/env python3
"""Post-process completed solver job results.

ABOUTME: Extracts key metrics from completed job YAML files and appends
summary entries to data/solver-results-log.jsonl.  Called by watch-results.sh
for each newly completed job.

Usage:
    python scripts/solver/post-process-hook.py <result.yaml>
    python scripts/solver/post-process-hook.py queue/completed/20260401T120000Z-test01/result.yaml
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_PATH = REPO_ROOT / "data" / "solver-results-log.jsonl"


def parse_yaml_simple(path: Path) -> dict:
    """Parse YAML file, falling back to simple parser if pyyaml unavailable."""
    if yaml is not None:
        with open(path) as f:
            return yaml.safe_load(f) or {}

    data = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                data[key] = value
    return data


def extract_metrics(result_data: dict) -> dict:
    """Extract key metrics from a completed job result YAML."""
    metrics = {
        "status": result_data.get("status", "unknown"),
        "solver": result_data.get("solver", ""),
        "input_file": str(result_data.get("input_file", "")),
        "description": str(result_data.get("description", "")),
        "processed_at": str(result_data.get("processed_at", "")),
        "elapsed_seconds": result_data.get("elapsed_seconds", 0.0),
    }
    if "output_files" in result_data:
        metrics["output_file_count"] = len(result_data["output_files"])
        metrics["output_files"] = result_data["output_files"]
    if "error" in result_data:
        metrics["error"] = str(result_data["error"])
    return metrics


def append_to_jsonl(log_path: Path, entry: dict) -> None:
    """Append a single JSON object as a line to a JSONL file."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: post-process-hook.py <result.yaml>", file=sys.stderr)
        return 1

    result_path = Path(sys.argv[1])
    if not result_path.exists():
        print(f"ERROR: File not found: {result_path}", file=sys.stderr)
        return 1

    data = parse_yaml_simple(result_path)
    metrics = extract_metrics(data)
    metrics["job_dir"] = result_path.parent.name
    metrics["result_path"] = str(result_path)

    append_to_jsonl(LOG_PATH, metrics)

    status = metrics["status"]
    solver = metrics["solver"]
    elapsed = metrics["elapsed_seconds"]
    print(f"Logged: {status} | {solver} | {elapsed}s → {LOG_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
