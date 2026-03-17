#!/usr/bin/env python3
"""
observed_exposure_report.py — Measure AI observed exposure per WRK category.

Scans WRK items, reads stage-evidence files, classifies each completed stage
as AI or human-gated, and reports observed automation rate by category.

Usage:
  uv run --no-project python scripts/ai/observed_exposure_report.py
  uv run --no-project python scripts/ai/observed_exposure_report.py --csv
"""
import argparse
import csv
import io
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent.parent
QUEUE_ROOT = REPO_ROOT / ".claude/work-queue"
HUMAN_GATE_STAGES = {1, 5, 7, 17}


def scan_wrk_files(queue_root: Path | None = None) -> list[dict]:
    """Glob pending/*.md, working/*.md, archive/**/*.md; parse frontmatter."""
    root = queue_root or QUEUE_ROOT
    results: list[dict] = []
    globs = [
        root / "pending" / "*.md",
        root / "working" / "*.md",
        root / "archive",
    ]
    md_files: list[Path] = []
    for g in globs[:2]:
        md_files.extend(g.parent.glob(g.name))
    archive_dir = root / "archive"
    if archive_dir.exists():
        md_files.extend(archive_dir.rglob("*.md"))

    for md_file in md_files:
        parsed = _parse_frontmatter(md_file)
        if parsed and parsed.get("id"):
            results.append({
                "id": parsed["id"],
                "category": parsed.get("category", "uncategorized"),
                "onet_category": parsed.get("onet_category"),
            })
    return results


def _parse_frontmatter(path: Path) -> dict | None:
    """Extract YAML frontmatter from a markdown file."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None


def load_stage_evidence(
    wrk_id: str, queue_root: Path | None = None
) -> list[dict]:
    """Read stage-evidence.yaml for a WRK. Returns stages list or []."""
    root = queue_root or QUEUE_ROOT
    evidence_path = root / "assets" / wrk_id / "evidence" / "stage-evidence.yaml"
    if not evidence_path.exists():
        return []
    try:
        data = yaml.safe_load(evidence_path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError):
        return []
    if not isinstance(data, dict):
        return []
    return data.get("stages", [])


def classify_stages(stages: list[dict]) -> tuple[int, int, int]:
    """Classify completed stages. Returns (total_done, ai_done, human_done)."""
    total = 0
    ai = 0
    human = 0
    for s in stages:
        if s.get("status") != "done":
            continue
        total += 1
        order = s.get("order", 0)
        if order in HUMAN_GATE_STAGES:
            human += 1
        else:
            ai += 1
    return total, ai, human


def aggregate_by_category(wrk_data: list[dict]) -> dict[str, dict]:
    """Group WRK data by category and sum stage counts."""
    result: dict[str, dict] = {}
    for wrk in wrk_data:
        cat = wrk.get("category", "uncategorized")
        if cat not in result:
            result[cat] = {
                "wrk_count": 0,
                "total_stages": 0,
                "ai_stages": 0,
                "human_stages": 0,
            }
        result[cat]["wrk_count"] += 1
        result[cat]["total_stages"] += wrk.get("total", 0)
        result[cat]["ai_stages"] += wrk.get("ai", 0)
        result[cat]["human_stages"] += wrk.get("human", 0)
    return result


def aggregate_by_onet(wrk_data: list[dict]) -> dict[str, dict]:
    """Group WRK data by onet_category. Items without it go to 'untagged'."""
    result: dict[str, dict] = {}
    for wrk in wrk_data:
        key = wrk.get("onet_category") or "untagged"
        if key not in result:
            result[key] = {
                "wrk_count": 0,
                "total_stages": 0,
                "ai_stages": 0,
                "human_stages": 0,
            }
        result[key]["wrk_count"] += 1
        result[key]["total_stages"] += wrk.get("total", 0)
        result[key]["ai_stages"] += wrk.get("ai", 0)
        result[key]["human_stages"] += wrk.get("human", 0)
    return result


def format_table(
    data: dict[str, dict],
    csv_mode: bool = False,
    include_theoretical: bool = True,
) -> str:
    """Render aggregated data as Markdown table or CSV."""
    if not data:
        return "(no data)"

    headers = [
        "Category", "WRKs", "Total Stages", "AI Stages",
        "Human Stages", "Observed Exposure %", "Theoretical Max %",
    ]
    rows = sorted(data.items(), key=lambda x: x[1]["wrk_count"], reverse=True)

    def _calc_pct(ai: int, total: int) -> float:
        return (ai / total * 100) if total > 0 else 0.0

    if csv_mode:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(headers)
        for cat, d in rows:
            observed = _calc_pct(d["ai_stages"], d["total_stages"])
            theoretical = _calc_pct(
                d["total_stages"] - d["human_stages"], d["total_stages"]
            )
            writer.writerow([
                cat, d["wrk_count"], d["total_stages"],
                d["ai_stages"], d["human_stages"],
                f"{observed:.1f}", f"{theoretical:.1f}",
            ])
        return buf.getvalue().rstrip("\r\n")

    # Markdown table
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for cat, d in rows:
        observed = _calc_pct(d["ai_stages"], d["total_stages"])
        theoretical = _calc_pct(
            d["total_stages"] - d["human_stages"], d["total_stages"]
        )
        lines.append(
            f"| {cat} | {d['wrk_count']} | {d['total_stages']} | "
            f"{d['ai_stages']} | {d['human_stages']} | "
            f"{observed:.1f} | {theoretical:.1f} |"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Observed AI exposure report by WRK category"
    )
    parser.add_argument("--csv", action="store_true", help="Output as CSV")
    parser.add_argument(
        "--by-onet", action="store_true",
        help="Group by onet_category instead of category",
    )
    parser.add_argument(
        "--queue-root", default=str(QUEUE_ROOT),
        help="Path to work-queue root",
    )
    args = parser.parse_args()

    queue_root = Path(args.queue_root)
    wrk_list = scan_wrk_files(queue_root)
    if not wrk_list:
        print("No WRK items found.", file=sys.stderr)
        sys.exit(1)

    for wrk in wrk_list:
        evidence = load_stage_evidence(wrk["id"], queue_root)
        total, ai, human = classify_stages(evidence)
        wrk["total"] = total
        wrk["ai"] = ai
        wrk["human"] = human

    if args.by_onet:
        agg = aggregate_by_onet(wrk_list)
    else:
        agg = aggregate_by_category(wrk_list)
    print(format_table(agg, csv_mode=args.csv))


if __name__ == "__main__":
    main()
