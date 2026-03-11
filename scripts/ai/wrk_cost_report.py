#!/usr/bin/env python3
"""
wrk_cost_report.py — Aggregate AI token costs by WRK item.

Usage:
  uv run --no-project python scripts/ai/wrk_cost_report.py           # all WRKs
  uv run --no-project python scripts/ai/wrk_cost_report.py WRK-NNN  # single WRK
  uv run --no-project python scripts/ai/wrk_cost_report.py --csv     # CSV output

Data source: .claude/state/session-signals/cost-tracking.jsonl
Primary cost field: cost_usd (recorded at session time — do not recalculate unless missing)
"""
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
DEFAULT_DATA_FILE = REPO_ROOT / ".claude/state/session-signals/cost-tracking.jsonl"


def load_records(path: Path) -> tuple[list[dict], int]:
    """Load valid JSONL records, streaming line by line. Returns (records, skipped_count)."""
    records: list[dict] = []
    skipped = 0
    if not path.exists():
        return [], 0
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                skipped += 1
    return records, skipped


def aggregate_by_wrk(
    records: list[dict], wrk_filter: str | None = None
) -> dict[str, dict]:
    """Sum tokens and cost per WRK item. Missing wrk field -> 'unattributed'."""
    result: dict[str, dict] = {}
    for r in records:
        wrk = str(r.get("wrk", "")).strip() or "unattributed"
        if wrk_filter and wrk != wrk_filter:
            continue
        if wrk not in result:
            result[wrk] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost_usd": 0.0,
                "session_count": 0,
                "providers": set(),
            }
        try:
            result[wrk]["input_tokens"] += int(r.get("input_tokens", 0))
            result[wrk]["output_tokens"] += int(r.get("output_tokens", 0))
            result[wrk]["cost_usd"] += float(r.get("cost_usd", 0.0))
        except (ValueError, TypeError):
            print(f"[WARN] skipping record with non-numeric tokens/cost: {r}", file=sys.stderr)
            continue
        result[wrk]["session_count"] += 1
        result[wrk]["providers"].add(str(r.get("provider", "unknown")))
    return result


def format_cost_table(
    data: dict[str, dict], skipped: int = 0, csv_mode: bool = False
) -> str:
    """Render aggregated data as a table or CSV."""
    if not data:
        return "(no records)"
    rows = sorted(data.items(), key=lambda x: x[1]["cost_usd"], reverse=True)
    if csv_mode:
        lines = ["WRK-ID,INPUT,OUTPUT,COST_USD,SESSIONS,PROVIDERS"]
        for wrk, d in rows:
            providers = "|".join(sorted(d["providers"]))
            lines.append(
                f"{wrk},{d['input_tokens']},{d['output_tokens']},"
                f"{d['cost_usd']:.4f},{d['session_count']},{providers}"
            )
    else:
        lines = [
            f"{'WRK-ID':<12} {'INPUT':>10} {'OUTPUT':>10} {'COST_USD':>10} "
            f"{'SESSIONS':>9} PROVIDERS",
            "-" * 70,
        ]
        for wrk, d in rows:
            providers = "+".join(sorted(d["providers"]))
            lines.append(
                f"{wrk:<12} {d['input_tokens']:>10,} {d['output_tokens']:>10,} "
                f"${d['cost_usd']:>9.4f} {d['session_count']:>9} {providers}"
            )
        total = sum(d["cost_usd"] for d in data.values())
        lines += ["-" * 70, f"{'TOTAL':<12} {'':>10} {'':>10} ${total:>9.4f}"]
    if skipped:
        lines.append(f"\n({skipped} records skipped — malformed JSON)")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="WRK AI cost report")
    parser.add_argument("wrk_id", nargs="?", help="Filter to single WRK (e.g. WRK-100)")
    parser.add_argument("--csv", action="store_true", help="Output as CSV")
    parser.add_argument("--data-file", default=str(DEFAULT_DATA_FILE),
                        help="Path to cost-tracking.jsonl")
    args = parser.parse_args()

    records, skipped = load_records(Path(args.data_file))
    if not records and not skipped:
        print(f"ERROR: data file not found: {args.data_file}", file=sys.stderr)
        sys.exit(2)
    if not records:
        print("No valid cost records found.", file=sys.stderr)
        sys.exit(1)

    data = aggregate_by_wrk(records, wrk_filter=args.wrk_id)
    if not data:
        msg = f"No records for {args.wrk_id}" if args.wrk_id else "No records"
        print(msg, file=sys.stderr)
        sys.exit(1)

    print(format_cost_table(data, skipped=skipped, csv_mode=args.csv))


if __name__ == "__main__":
    main()
