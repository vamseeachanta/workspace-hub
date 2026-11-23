#!/usr/bin/env python3
"""
tag_onet.py — Suggest O*NET occupation codes for a WRK item.

Reads WRK frontmatter (title + mission) and keyword-matches against
a lookup table of relevant O*NET SOC codes.

Usage:
  uv run --no-project python scripts/ai/tag_onet.py WRK-5003
  uv run --no-project python scripts/ai/tag_onet.py WRK-5003 --apply
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent.parent
QUEUE_ROOT = REPO_ROOT / ".claude/work-queue"
LOOKUP_PATH = REPO_ROOT / "config/ai-tools/onet-lookup.yaml"
ONET_CODE_PATTERN = re.compile(r"^\d{2}-\d{4}\.\d{2}$")


def _load_lookup(path: Path | None = None) -> dict[str, tuple[str, list[str]]]:
    """Load O*NET lookup from YAML. Returns {code: (label, keywords)}."""
    p = path or LOOKUP_PATH
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    return {
        code: (entry["label"], entry["keywords"])
        for code, entry in raw.items()
    }


ONET_LOOKUP = _load_lookup()


def is_valid_onet_code(code: str) -> bool:
    """Check if a string matches O*NET SOC format XX-XXXX.XX."""
    return bool(ONET_CODE_PATTERN.match(code))


def read_wrk_frontmatter(path: Path) -> dict:
    """Parse YAML frontmatter from a WRK markdown file."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def _extract_mission(path: Path) -> str:
    """Extract the mission section text from a WRK file."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    lines = parts[2].split("\n")
    in_mission = False
    mission_lines = []
    for line in lines:
        if line.strip().startswith("## Mission"):
            in_mission = True
            continue
        if in_mission and line.strip().startswith("## "):
            break
        if in_mission:
            mission_lines.append(line)
    return " ".join(mission_lines).strip()


def suggest_onet_codes(
    title: str, mission: str, top_n: int = 3,
) -> list[dict]:
    """Suggest top-N O*NET codes based on keyword matching."""
    text = f"{title} {mission}".lower()
    if not text.strip():
        return []
    scores: list[tuple[str, str, int]] = []
    for code, (label, keywords) in ONET_LOOKUP.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores.append((code, label, score))
    scores.sort(key=lambda x: x[2], reverse=True)
    return [
        {"code": c, "label": l, "score": s}
        for c, l, s in scores[:top_n]
    ]


def find_wrk_file(wrk_id: str, queue_root: Path | None = None) -> Path | None:
    """Locate a WRK file in pending/, working/, or archive/."""
    root = queue_root or QUEUE_ROOT
    for subdir in ["pending", "working"]:
        p = root / subdir / f"{wrk_id}.md"
        if p.exists():
            return p
    archive = root / "archive"
    if archive.exists():
        matches = list(archive.rglob(f"{wrk_id}.md"))
        if matches:
            return matches[0]
    return None


def _apply_onet(wrk_path: Path, onet_value: str) -> None:
    """Write onet_category into WRK frontmatter."""
    text = wrk_path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return
    fm_text = parts[1]
    if "onet_category:" not in fm_text:
        fm_text = fm_text.rstrip("\n") + f'\nonet_category: "{onet_value}"\n'
    else:
        lines = fm_text.split("\n")
        lines = [
            f'onet_category: "{onet_value}"'
            if l.startswith("onet_category:") else l
            for l in lines
        ]
        fm_text = "\n".join(lines)
    wrk_path.write_text(f"---{fm_text}---{parts[2]}")
    print(f"\nApplied: onet_category: \"{onet_value}\"")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Suggest O*NET codes for a WRK item"
    )
    parser.add_argument("wrk_id", help="WRK ID (e.g. WRK-5003)")
    parser.add_argument("--apply", action="store_true",
                        help="Write top code to WRK frontmatter")
    parser.add_argument("--queue-root", default=str(QUEUE_ROOT),
                        help="Path to work-queue root")
    args = parser.parse_args()

    wrk_path = find_wrk_file(args.wrk_id, Path(args.queue_root))
    if not wrk_path:
        print(f"WRK file not found: {args.wrk_id}", file=sys.stderr)
        sys.exit(1)

    fm = read_wrk_frontmatter(wrk_path)
    suggestions = suggest_onet_codes(fm.get("title", ""),
                                     _extract_mission(wrk_path))
    if not suggestions:
        print("No matching O*NET codes found.", file=sys.stderr)
        sys.exit(1)

    print(f"Top O*NET suggestions for {args.wrk_id}:")
    for i, s in enumerate(suggestions, 1):
        print(f"  {i}. {s['code']} — {s['label']} (score: {s['score']})")

    if args.apply:
        best = suggestions[0]
        _apply_onet(wrk_path, f"{best['code']} — {best['label']}")


if __name__ == "__main__":
    main()
