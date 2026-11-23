#!/usr/bin/env python3
"""Scan all Excel workbooks across workspace-hub and /mnt/ace/digitalmodel.

Catalogs every .xlsx/.xls/.xlsm with sheet names, row counts, header detection,
formula detection, and VBA macro flag. Outputs JSONL inventory + summary.

Usage:
    uv run scripts/knowledge/excel-inventory-scan.py [--limit N]
"""

import json
import os
import sys
import csv
import time
import zipfile
import re
from pathlib import Path
from collections import Counter

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

# Scan roots
SCAN_ROOTS = [
    "/mnt/ace/digitalmodel/docs",
    "/mnt/ace/digitalmodel/projects",
    "/mnt/local-analysis/workspace-hub/digitalmodel/docs",
    "/mnt/local-analysis/workspace-hub/digitalmodel/tests",
]

SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".venv", "venv"}
EXCEL_EXTENSIONS = {".xlsx", ".xls", ".xlsm", ".xlsb", ".xlt", ".xltx", ".xltm"}
HEADER_SAMPLE_COLS = 20
HEADER_SAMPLE_ROWS = 3


def find_excel_files(roots, max_files=None):
    files = []
    seen = set()
    for root in roots:
        root_path = Path(root)
        if not root_path.exists():
            print(f"[WARN] Root not found: {root}")
            continue
        for dirpath, dirnames, filenames in os.walk(root_path):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            for fname in filenames:
                ext = Path(fname).suffix.lower()
                if ext in EXCEL_EXTENSIONS:
                    full = os.path.join(dirpath, fname)
                    if full not in seen:
                        seen.add(full)
                        files.append(full)
    files.sort()
    if max_files:
        files = files[:max_files]
    return files


def is_ole2_binary(filepath):
    """Check if file starts with OLE2 magic bytes."""
    try:
        with open(filepath, "rb") as f:
            return f.read(4) == b"\xd0\xcf\x11\xe0"
    except Exception:
        return False


def detect_vba_in_zip(filepath):
    """Check zip-based Excel for VBA macros."""
    try:
        with zipfile.ZipFile(filepath, "r") as z:
            return any("vbaProject" in n for n in z.namelist())
    except (zipfile.BadZipFile, RuntimeError, IsADirectoryError):
        return False


def scan_xlsx(filepath):
    """Scan .xlsx/.xlsm workbook using openpyxl."""
    result = {
        "sheets": [],
        "total_sheets": 0,
        "has_vba": False,
        "file_size_bytes": 0,
        "status": "ok",
    }
    try:
        result["file_size_bytes"] = os.path.getsize(filepath)
        result["has_vba"] = filepath.lower().endswith(".xlsm") or detect_vba_in_zip(filepath)

        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            sheet_type = type(ws).__name__

            if sheet_type == "Chartsheet":
                s_info = {
                    "name": sheet_name,
                    "dimensions": "chart sheet",
                    "row_count": 0,
                    "column_count": 0,
                    "headers": [],
                    "has_formulas": False,
                    "sheet_type": "Chartsheet",
                }
            else:
                s_info = {
                    "name": sheet_name,
                    "dimensions": str(getattr(ws, "dimensions", None) or "empty"),
                    "row_count": ws.max_row or 0,
                    "column_count": ws.max_column or 0,
                    "headers": [],
                    "has_formulas": False,
                    "sheet_type": "Worksheet",
                }

                # Read header rows
                header_rows = []
                max_r = min(HEADER_SAMPLE_ROWS, ws.max_row or 0)
                max_c = min(HEADER_SAMPLE_COLS, ws.max_column or 0)
                for row_idx in range(1, max_r + 1):
                    row_data = []
                    for col_idx in range(1, max_c + 1):
                        cell = ws.cell(row=row_idx, column=col_idx)
                        if cell.value is not None:
                            val = str(cell.value)
                            if val.startswith("="):
                                s_info["has_formulas"] = True
                            row_data.append(val[:100])
                        else:
                            row_data.append("")
                    if any(row_data):
                        header_rows.append(row_data)
                s_info["headers"] = header_rows

            result["sheets"].append(s_info)

        result["total_sheets"] = len(result["sheets"])
        wb.close()

    except zipfile.BadZipFile:
        result["status"] = "error: BadZipFile (corrupt or not a zip-based Excel)"
        result["total_sheets"] = 0
    except Exception as e:
        result["status"] = f"error: {type(e).__name__}: {str(e)[:200]}"
        result["total_sheets"] = 0

    return result


def scan_xls_fallback(filepath):
    """Scan .xls without xlrd: binary detection + basic metadata."""
    result = {
        "sheets": [],
        "total_sheets": 0,
        "has_vba": False,
        "file_size_bytes": 0,
        "status": "ok",
    }
    try:
        result["file_size_bytes"] = os.path.getsize(filepath)
        if is_ole2_binary(filepath):
            result["status"] = "ok (BIFF binary, xlrd needed for sheet details)"
            result["_note"] = "Valid .xls binary — install xlrd for full scan"
        else:
            # Might be CSV or XML renamed as .xls
            result["status"] = "ok (not BIFF binary, may be CSV/XML renamed)"
            result["_note"] = "Not a binary .xls — possibly CSV with .xls extension"
    except Exception as e:
        result["status"] = f"error: {type(e).__name__}: {str(e)[:200]}"
    return result


def scan_workbook(filepath):
    ext = Path(filepath).suffix.lower()
    if ext in {".xlsx", ".xlsm"} and HAS_OPENPYXL:
        return scan_xlsx(filepath)
    elif ext == ".xls":
        return scan_xls_fallback(filepath)
    else:
        return {
            "sheets": [],
            "total_sheets": 0,
            "has_vba": False,
            "file_size_bytes": os.path.getsize(filepath) if os.path.exists(filepath) else 0,
            "status": f"skipped (no scanner for {ext})",
        }


def classify_domain(filepath):
    p = filepath.lower()
    parts = p.split(os.sep)
    name = os.path.basename(p)

    for keyword, domain in [
        ("jumper", "jumper"),
        ("freespan", "freespan"),
        ("riser", "riser"),
        ("mooring", "mooring"),
        ("orcaflex", "orcaflex"),
        ("orcawave", "orcawave"),
        ("pipeline", "pipeline"),
        ("pipe", "pipe"),
        ("fatigue", "fatigue"),
        ("buckling", "buckling"),
        ("platecap", "platecapacity"),
        ("cathodic", "cathodic_protection"),
        ("installation", "installation"),
        ("ship-design", "ship_design"),
        ("cp", "cathodic_protection"),
    ]:
        if keyword in p:
            return domain

    # Check parent directory name
    for i in range(len(parts) - 1, -1, -1):
        d = parts[i]
        if d in {"data", "docs"} and i < len(parts) - 1:
            return parts[i - 1] if i > 0 else "other"
    return "other"


def extract_project_number(filepath):
    name = Path(filepath).stem
    m = re.match(r"^(\d{4})", name)
    if m:
        return m.group(1)
    m = re.search(r"[/_](\d{4})[-_]", filepath)
    if m:
        return m.group(1)
    return None


def progress_bar(current, total, elapsed):
    pct = (current / total * 100) if total > 0 else 0
    rate = current / elapsed if elapsed > 0 else 0
    eta = (total - current) / rate if rate > 0 else 0
    bar_len = 40
    filled = int(bar_len * current // total) if total > 0 else 0
    bar = "=" * filled + "-" * (bar_len - filled)
    return f"\r[{bar}] {current}/{total} ({pct:.0f}%) --- {rate:.1f} files/s, ETA: {eta:.0f}s"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scan Excel workbooks across all mounts")
    parser.add_argument("--limit", type=int, default=None, help="Scan only first N files")
    parser.add_argument("--roots", nargs="*", default=None, help="Override scan roots")
    parser.add_argument("--summary-only", action="store_true", help="Only print summary, no output files")
    args = parser.parse_args()

    roots = args.roots if args.roots else SCAN_ROOTS
    print(f"Scanning Excel workbooks in: {roots}")
    files = find_excel_files(roots, max_files=args.limit)
    print(f"Found {len(files)} Excel files\n")

    results = []
    start = time.time()
    errors = 0

    for i, filepath in enumerate(files):
        scan = scan_workbook(filepath)
        record = {
            "path": filepath,
            "file_size_bytes": scan["file_size_bytes"],
            "status": scan["status"],
            "total_sheets": scan["total_sheets"],
            "has_vba": scan["has_vba"],
            "domain": classify_domain(filepath),
            "project_number": extract_project_number(filepath),
        }

        # Sheet summaries
        sheet_summaries = []
        for sheet in scan["sheets"]:
            s = {
                "name": sheet["name"],
                "type": sheet.get("sheet_type", "Worksheet"),
                "rows": sheet["row_count"],
                "cols": sheet["column_count"],
                "has_formulas": sheet["has_formulas"],
            }
            if sheet.get("headers"):
                s["header_sample"] = sheet["headers"][0][:10]
            sheet_summaries.append(s)
        record["sheets"] = sheet_summaries
        results.append(record)

        if "error" in scan.get("status", ""):
            errors += 1

        if i % 100 == 0 and i > 0:
            sys.stdout.write(progress_bar(i, len(files), time.time() - start))
            sys.stdout.flush()

    elapsed = time.time() - start
    sys.stdout.write(progress_bar(len(files), len(files), elapsed) + "\n")

    # Summary stats
    total_sheets = sum(r["total_sheets"] for r in results)
    total_size = sum(r["file_size_bytes"] for r in results)
    statuses = Counter()
    domain_counts = Counter()
    project_counts = Counter()
    ext_counts = Counter()
    formula_sheets = 0
    vba_files = 0
    sheets_with_formulas = 0
    binary_xls_count = 0
    nonbinary_xls_count = 0

    for r in results:
        stats = r["status"]
        statuses[stats] += 1
        domain_counts[r["domain"]] += 1
        project_counts[r["project_number"]] += 1
        vba_files += 1 if r["has_vba"] else 0
        ext_counts[Path(r["path"]).suffix.lower()] += 1
        if "BIFF" in stats:
            binary_xls_count += 1
        if "not BIFF" in stats:
            nonbinary_xls_count += 1
        for s in r["sheets"]:
            if s.get("has_formulas"):
                formula_sheets += 1
                sheets_with_formulas += 1

    print(f"\n{'='*60}")
    print(f"EXCEL INVENTORY SUMMARY")
    print(f"{'='*60}")
    print(f"Files scanned:     {len(results)}")
    print(f"Total file size:   {total_size / 1024 / 1024:.1f} MB")
    print(f"VBA macro files:   {vba_files}")
    print(f"Sheets with data:  {total_sheets}")
    print(f"Sheets w/formulas: {sheets_with_formulas}")
    print()
    print(f"  .xlsx/.xlsm fully scanned: {len(results) - binary_xls_count - nonbinary_xls_count}")
    print(f"  .xls binary (xlrd needed): {binary_xls_count}")
    print(f"  .xls non-binary (CSV/XML): {nonbinary_xls_count}")
    print(f"  Other formats ({', '.join(k for k in ext_counts if k not in ('.xls', '.xlsx', '.xlsm'))}): {sum(c for k,c in ext_counts.items() if k not in ('.xls', '.xlsx', '.xlsm'))}")
    print(f"  Errors: {errors}")
    print(f"  Time: {elapsed:.1f}s")

    print(f"\n--- FILE TYPES ---")
    for ext, count in ext_counts.most_common():
        print(f"  {ext:10s}: {count}")

    print(f"\n--- BY DOMAIN ---")
    for domain, count in domain_counts.most_common():
        print(f"  {domain:25s}: {count}")

    print(f"\n--- TOP PROJECTS ---")
    for proj, count in project_counts.most_common(25):
        proj_label = proj if proj else "(no project number)"
        print(f"  {proj_label:10s}: {count}")

    if args.summary_only:
        return

    # Write outputs
    output_dir = Path("/mnt/local-analysis/workspace-hub/data/inventory")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Main JSONL
    jsonl_path = output_dir / "excel-inventory.jsonl"
    with open(jsonl_path, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nWrote: {jsonl_path}")

    # Sheet detail JSONL
    sheet_path = output_dir / "excel-sheet-detail.jsonl"
    with open(sheet_path, "w") as f:
        for r in results:
            for s in r["sheets"]:
                f.write(json.dumps({
                    "workbook": r["path"],
                    "workbook_domain": r["domain"],
                    "workbook_project": r["project_number"],
                    "workbook_vba": r["has_vba"],
                    "status": r["status"],
                    **s,
                }, ensure_ascii=False) + "\n")
    print(f"Wrote: {sheet_path}")

    # Markdown report
    md_path = output_dir / "excel-inventory-report.md"
    with open(md_path, "w") as f:
        f.write("# Excel Workbook Inventory\n\n")
        f.write(f"- **Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **Files**: {len(results)}\n")
        f.write(f"- **Size**: {total_size / 1024 / 1024:.1f} MB\n")
        f.write(f"- **Sheets with data**: {total_sheets}\n")
        f.write(f"- **Sheets with formulas**: {sheets_with_formulas}\n")
        f.write(f"- **VBA macros**: {vba_files}\n")
        f.write(f"- **.xls binary (need xlrd)**: {binary_xls_count}\n")
        f.write(f"- **.xls non-binary (CSV/XML)**: {nonbinary_xls_count}\n\n")

        f.write("## By Domain\n\n| Domain | Files |\n|--------|-------|\n")
        for d, c in domain_counts.most_common():
            f.write(f"| {d} | {c} |\n")

        f.write(f"\n## By Project Number\n\n| Project | Files |\n|---------|-------|\n")
        for p, c in project_counts.most_common():
            f.write(f"| {p or '(none)'} | {c} |\n")

        f.write(f"\n## Fully Scanned Workbooks (xlsx/xlsm with sheet data)\n\n")
        f.write("| Path | Sheets | Domain | Project | VBA |\n|------|--------|--------|---------|-----|\n")
        for r in results:
            if r["total_sheets"] > 0:
                f.write(f"| {r['path']} | {r['total_sheets']} | {r['domain']} | {r['project_number'] or '-'} | {'yes' if r['has_vba'] else 'no'} |\n")

    print(f"Wrote: {md_path}")
    print(f"\nDone.")


if __name__ == "__main__":
    main()
