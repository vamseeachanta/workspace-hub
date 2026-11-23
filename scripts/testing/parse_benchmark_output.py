#!/usr/bin/env python3
"""parse_benchmark_output.py — Baseline save/compare helper for run-benchmarks.sh.

Reads pytest-benchmark JSON output files, compares against a saved baseline,
and prints a regression table.  Exits 1 when any benchmark regresses >20%.

Usage:
    # Save baseline from raw JSON files (name:path pairs):
    python parse_benchmark_output.py --mode save-baseline --output baseline.json \
        assetutilities:/path/to/assetutilities-raw.json \
        digitalmodel:/path/to/digitalmodel-raw.json

    # Compare current run against baseline:
    python parse_benchmark_output.py --mode compare --baseline baseline.json \
        --output aggregate.json \
        assetutilities:/path/to/assetutilities-raw.json

Exit codes:
    0  All benchmarks within threshold (or save-baseline mode).
    1  At least one benchmark regressed >20% in mean execution time.
    2  Usage / file error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REGRESSION_THRESHOLD = 0.20  # 20 % slower = regression


# ── Parsing ────────────────────────────────────────────────────────────────────

def _parse_file(repo_name: str, json_path: str) -> Dict[str, float]:
    """Return {baseline_key: mean_seconds} from a pytest-benchmark JSON file."""
    path = Path(json_path)
    if not path.is_file():
        print(f"ERROR: benchmark file not found: {json_path}", file=sys.stderr)
        sys.exit(2)
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {json_path}: {exc}", file=sys.stderr)
        sys.exit(2)

    benchmarks = data.get("benchmarks", [])
    results: Dict[str, float] = {}
    for b in benchmarks:
        name = b.get("name") or b.get("fullname", "unknown")
        mean = b.get("stats", {}).get("mean")
        if mean is None:
            continue
        key = f"{repo_name}::{name}"
        results[key] = float(mean)
    return results


def _load_all(name_path_pairs: List[str]) -> Dict[str, float]:
    """Parse all 'name:path' pairs and merge into one dict."""
    combined: Dict[str, float] = {}
    for pair in name_path_pairs:
        if ":" not in pair:
            print(f"ERROR: expected 'name:path', got: {pair!r}", file=sys.stderr)
            sys.exit(2)
        repo, _, json_path = pair.partition(":")
        combined.update(_parse_file(repo, json_path))
    return combined


# ── Modes ──────────────────────────────────────────────────────────────────────

def save_baseline(output_path: str, name_path_pairs: List[str]) -> None:
    """Aggregate all benchmark means and write to baseline JSON."""
    results = _load_all(name_path_pairs)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"Baseline saved ({len(results)} benchmarks): {output_path}")


def compare(
    baseline_path: str,
    output_path: str,
    name_path_pairs: List[str],
) -> int:
    """Compare current results against baseline.  Returns exit code."""
    bl_file = Path(baseline_path)
    if not bl_file.is_file():
        print(f"ERROR: baseline not found: {baseline_path}", file=sys.stderr)
        return 2

    baseline: Dict[str, float] = json.loads(bl_file.read_text())
    current: Dict[str, float] = _load_all(name_path_pairs)

    regressions: List[Tuple[str, float, float, float]] = []
    new_benchmarks: List[str] = []
    ok_benchmarks: List[str] = []

    for key, cur_mean in current.items():
        if key not in baseline:
            new_benchmarks.append(key)
            continue
        base_mean = baseline[key]
        if base_mean <= 0:
            continue
        ratio = (cur_mean - base_mean) / base_mean  # positive = slower
        if ratio > REGRESSION_THRESHOLD:
            regressions.append((key, base_mean, cur_mean, ratio))
        else:
            ok_benchmarks.append(key)

    # ── Print table ──────────────────────────────────────────────────────────
    col_w = 60
    print(f"\n{'Benchmark':<{col_w}}  {'Baseline':>12}  {'Current':>12}  {'Delta':>8}")
    print("-" * (col_w + 38))

    for key in sorted(ok_benchmarks):
        b = baseline[key]
        c = current[key]
        ratio = (c - b) / b
        sign = "+" if ratio >= 0 else ""
        print(f"  {key:<{col_w - 2}}  {b * 1e6:>10.1f}µs  {c * 1e6:>10.1f}µs  {sign}{ratio * 100:>6.1f}%")

    for key, b, c, ratio in sorted(regressions, key=lambda x: -x[3]):
        print(
            f"  REGRESS {key:<{col_w - 8}}  {b * 1e6:>10.1f}µs  {c * 1e6:>10.1f}µs  "
            f"+{ratio * 100:>6.1f}%"
        )

    for key in sorted(new_benchmarks):
        c = current[key]
        print(f"  NEW     {key:<{col_w - 8}}  {'n/a':>12}  {c * 1e6:>10.1f}µs  {'':>8}")

    print()
    if regressions:
        print(f"REGRESSION: {len(regressions)} benchmark(s) exceeded +{REGRESSION_THRESHOLD * 100:.0f}% threshold.")
    else:
        print(f"OK: all {len(ok_benchmarks)} benchmark(s) within threshold.")
    if new_benchmarks:
        print(f"NOTE: {len(new_benchmarks)} new benchmark(s) not in baseline (add with --save-baseline).")

    # ── Write aggregate JSON ─────────────────────────────────────────────────
    aggregate = {
        "baseline": baseline_path,
        "results": current,
        "regressions": [
            {"key": k, "baseline_s": b, "current_s": c, "delta_pct": r * 100}
            for k, b, c, r in regressions
        ],
        "new_benchmarks": new_benchmarks,
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(aggregate, indent=2, sort_keys=True))

    return 1 if regressions else 0


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["save-baseline", "compare"], required=True)
    parser.add_argument("--baseline", help="Path to baseline JSON (compare mode)")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument(
        "name_path_pairs",
        nargs="+",
        metavar="NAME:PATH",
        help="repo-name:path-to-pytest-benchmark-json pairs",
    )
    args = parser.parse_args()

    if args.mode == "save-baseline":
        save_baseline(args.output, args.name_path_pairs)
        sys.exit(0)

    if args.mode == "compare":
        if not args.baseline:
            print("ERROR: --baseline required for compare mode", file=sys.stderr)
            sys.exit(2)
        sys.exit(compare(args.baseline, args.output, args.name_path_pairs))


if __name__ == "__main__":
    main()
