"""
Research Literature Index Scanner
GitHub Issue #1623

Scans /mnt/ace-data/digitalmodel/docs/domains/ and produces:
  - JSONL index: one record per file
  - Markdown summary report
"""

import os
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

SOURCE_DIR = Path("/mnt/ace-data/digitalmodel/docs/domains")
OUT_DIR = Path("/mnt/local-analysis/workspace-hub/data/document-index")
JSONL_PATH = OUT_DIR / "research-literature-index.jsonl"
REPORT_PATH = OUT_DIR / "research-literature-report.md"

OUT_DIR.mkdir(parents=True, exist_ok=True)


def human_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} TB"


# ── Scan ──────────────────────────────────────────────────────────────────────
records = []
domain_stats = defaultdict(lambda: {
    "file_count": 0,
    "total_bytes": 0,
    "by_ext": defaultdict(int),
    "files": [],
})

for domain_path in sorted(SOURCE_DIR.iterdir()):
    if not domain_path.is_dir():
        continue
    domain = domain_path.name

    for root, dirs, files in os.walk(domain_path):
        dirs.sort()
        for fname in sorted(files):
            fpath = Path(root) / fname
            try:
                size = fpath.stat().st_size
            except OSError:
                size = 0

            ext = fpath.suffix.lower() if fpath.suffix else "(none)"
            rel_path = str(fpath)

            rec = {
                "domain": domain,
                "filename": fname,
                "path": rel_path,
                "extension": ext,
                "size_bytes": size,
            }
            records.append(rec)

            ds = domain_stats[domain]
            ds["file_count"] += 1
            ds["total_bytes"] += size
            ds["by_ext"][ext] += 1
            ds["files"].append(fname)

print(f"Total records collected: {len(records)}")

# ── Write JSONL ───────────────────────────────────────────────────────────────
with open(JSONL_PATH, "w", encoding="utf-8") as fh:
    for rec in records:
        fh.write(json.dumps(rec) + "\n")

print(f"JSONL written: {JSONL_PATH}")

# ── Write Markdown Report ─────────────────────────────────────────────────────
now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
total_files = len(records)
total_bytes = sum(r["size_bytes"] for r in records)

# Global extension breakdown
global_ext: dict[str, int] = defaultdict(int)
for r in records:
    global_ext[r["extension"]] += 1

lines = []
lines.append("# Research Literature Index — Domain Document Catalog")
lines.append("")
lines.append(f"> Generated: {now_utc}  ")
lines.append(f"> Source: `{SOURCE_DIR}`  ")
lines.append(f"> Issue: GitHub #1623  ")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## Executive Summary")
lines.append("")
lines.append(f"| Metric | Value |")
lines.append(f"|--------|-------|")
lines.append(f"| Total domains scanned | {len(domain_stats)} |")
lines.append(f"| Total files indexed   | {total_files} |")
lines.append(f"| Total corpus size     | {human_size(total_bytes)} |")
lines.append(f"| Primary file type     | PDF ({global_ext.get('.pdf', 0)} files) |")
lines.append("")
lines.append("### File Types Across All Domains")
lines.append("")
lines.append("| Extension | Count |")
lines.append("|-----------|-------|")
for ext, cnt in sorted(global_ext.items(), key=lambda x: -x[1]):
    lines.append(f"| `{ext}` | {cnt} |")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## Domain-by-Domain Breakdown")
lines.append("")

for domain in sorted(domain_stats.keys()):
    ds = domain_stats[domain]
    lines.append(f"### {domain}")
    lines.append("")
    lines.append(f"- **Files:** {ds['file_count']}")
    lines.append(f"- **Total size:** {human_size(ds['total_bytes'])}")
    lines.append("")

    # Extension breakdown for this domain
    lines.append("**File types:**")
    lines.append("")
    lines.append("| Extension | Count |")
    lines.append("|-----------|-------|")
    for ext, cnt in sorted(ds["by_ext"].items(), key=lambda x: -x[1]):
        lines.append(f"| `{ext}` | {cnt} |")
    lines.append("")

    # Full file listing
    lines.append("**Files:**")
    lines.append("")
    # Get records for this domain to show size
    domain_records = [r for r in records if r["domain"] == domain]
    lines.append("| # | Filename | Extension | Size |")
    lines.append("|---|----------|-----------|------|")
    for i, r in enumerate(domain_records, 1):
        lines.append(f"| {i} | `{r['filename']}` | `{r['extension']}` | {human_size(r['size_bytes'])} |")
    lines.append("")
    lines.append("---")
    lines.append("")

# Footer
lines.append("## Output Files")
lines.append("")
lines.append(f"- **JSONL index:** `{JSONL_PATH}`")
lines.append(f"- **This report:** `{REPORT_PATH}`")
lines.append("")
lines.append("Each JSONL record has keys: `domain`, `filename`, `path`, `extension`, `size_bytes`.")
lines.append("")

with open(REPORT_PATH, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")

print(f"Report written: {REPORT_PATH}")
print(f"\nDomain summary:")
for domain in sorted(domain_stats.keys()):
    ds = domain_stats[domain]
    print(f"  {domain:25s} {ds['file_count']:3d} files  {human_size(ds['total_bytes']):>10s}")
print(f"\n  {'TOTAL':25s} {total_files:3d} files  {human_size(total_bytes):>10s}")
