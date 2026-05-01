#!/usr/bin/env python3
"""Validate the B1528 SIROCCO source pack artifacts."""
from __future__ import annotations
from pathlib import Path
import math
import sys
import yaml
ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "docs/projects/acma/B1528/sirocco-rudder-source-pack.md"
BENCH = ROOT / "docs/projects/acma/B1528/sirocco-turning-benchmark.yaml"
def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
def main() -> int:
    text = PACK.read_text()
    data = yaml.safe_load(BENCH.read_text())
    required_strings = ["44.939563193699 m²", "225.5 m", "135.300000 m", "legacy yaw lever", "not automatically equivalent to CG-to-rudder arm", "workbook-regression mode should reproduce the evaluated workbook", "Ft = F * sin", "Fn = F * sin", "+1°", "-1°", "narrative benchmark"]
    for needle in required_strings:
        require(needle in text, f"missing required source-pack text: {needle}")
    require(data["data_quality"]["classification"] == "narrative_benchmark_not_instrumented_validation_dataset", "benchmark classification drifted")
    vdr = data["vdr_timeline_points"]
    require(len(vdr) >= 82, "expected at least 82 VDR timeline points")
    require(len(data["rosepoint_salvage_video_points"]) >= 20, "expected at least 20 Rosepoint points")
    times = {point["time_utc"] for point in vdr}
    for expected in ["071630", "071830", "071930", "072030", "072230", "075711"]:
        require(expected in times, f"missing VDR sentinel timestamp {expected}")
    first = vdr[0]
    require(first["time_utc"] == "071630", "unexpected first VDR timestamp")
    require(math.isclose(first["heading_deg"], 253.2, rel_tol=0, abs_tol=1e-9), "unexpected first VDR heading")
    require(all(point.get("source_line_basis") == "docx paragraph index including empty paragraphs" for point in vdr), "VDR source-line basis not documented per point")
    return 0
if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"B1528 source-pack validation failed: {exc}", file=sys.stderr)
        raise
