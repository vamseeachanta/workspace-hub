"""Select 10 XLSX/XLSM files for the WRK-1247 formula extraction POC."""

import json
import os
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = REPO_ROOT / "data" / "document-index" / "index.jsonl"
OUTPUT_PATH = REPO_ROOT / "knowledge" / "dark-intelligence" / "xlsx-poc" / "poc-file-list.yaml"

CALC_KEYWORDS = re.compile(
    r"(calc|design|analysis|check|sizing|capacity|fatigue|stability|load|stress)",
    re.IGNORECASE,
)

TARGET_EXTENSIONS = {"xlsx", "xlsm"}
MIN_SIZE_MB = 0.01  # 10KB
MAX_FILES = 10
MIN_XLSM = 2


def scan_index() -> list[dict]:
    """Scan index.jsonl for XLSX/XLSM files matching calculation keywords."""
    candidates = []
    with open(INDEX_PATH, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            ext = rec.get("ext", "").lower()
            if ext not in TARGET_EXTENSIONS:
                continue
            size_mb = rec.get("size_mb", 0) or 0
            if size_mb < MIN_SIZE_MB:
                continue
            path = rec.get("path", "")
            filename = Path(path).name
            if not CALC_KEYWORDS.search(filename):
                continue
            candidates.append({
                "path": path,
                "filename": filename,
                "extension": f".{ext}",
                "size_mb": round(size_mb, 3),
                "source": rec.get("source", "unknown"),
                "domain": rec.get("domain", "unknown"),
            })
    return candidates


def select_diverse(candidates: list[dict]) -> list[dict]:
    """Select up to MAX_FILES with domain diversity and XLSM preference."""
    # Sort: .xlsm first, then by size descending (bigger files more likely to have formulas)
    candidates.sort(key=lambda c: (c["extension"] != ".xlsm", -c["size_mb"]))

    selected = []
    domains_seen = set()
    xlsm_count = 0

    # First pass: pick diverse domains, prefer .xlsm
    for c in candidates:
        if len(selected) >= MAX_FILES:
            break
        domain = c["domain"]
        is_xlsm = c["extension"] == ".xlsm"

        # Prefer new domains
        if domain not in domains_seen or is_xlsm and xlsm_count < MIN_XLSM:
            selected.append(c)
            domains_seen.add(domain)
            if is_xlsm:
                xlsm_count += 1

    # Fill remaining slots if needed
    if len(selected) < MAX_FILES:
        for c in candidates:
            if len(selected) >= MAX_FILES:
                break
            if c not in selected:
                selected.append(c)

    return selected[:MAX_FILES]


def main():
    print(f"Scanning {INDEX_PATH} ...")
    candidates = scan_index()
    print(f"Found {len(candidates)} calc-related XLSX/XLSM files")

    if not candidates:
        print("No candidates found. Check index path and keywords.")
        return

    selected = select_diverse(candidates)
    print(f"\nSelected {len(selected)} files:")
    xlsm_count = sum(1 for s in selected if s["extension"] == ".xlsm")
    print(f"  .xlsx: {len(selected) - xlsm_count}, .xlsm: {xlsm_count}")
    print(f"  Domains: {sorted(set(s['domain'] for s in selected))}")

    for i, s in enumerate(selected, 1):
        print(f"  {i:2d}. [{s['extension']}] {s['domain']:20s} {s['filename'][:60]}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        yaml.dump(
            {"wrk_id": "WRK-1247", "selected_files": selected},
            f,
            default_flow_style=False,
            sort_keys=False,
        )
    print(f"\nWritten to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
