#!/usr/bin/env python3
"""Build metadata-first LLM-wiki inventory for Elements-ingested buckets.

This script scans retained `_from_elements` staging paths to define the exact newly
introduced corpus, then maps each file to its parent `/mnt/ace` source-of-record
path. It writes full file inventory artifacts plus small per-wiki batch-ingest
records (bucket-level, not one page per file) to avoid exploding the wiki with
40k+ metadata pages.
"""
from __future__ import annotations

import csv
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / ".planning" / "intel" / "elements-to-llm-wiki"
BATCH = OUT / "batches"

BUCKETS = [
    {
        "order": 1,
        "bucket": "digitalmodel-suction-pile-sizing",
        "repo_bucket": "digitalmodel",
        "parent": "/mnt/ace/digitalmodel/references/suction-pile-sizing",
        "stage": "/mnt/ace/digitalmodel/references/suction-pile-sizing/_from_elements",
        "wiki": "marine-engineering",
        "content_type": "engineering-reference",
        "extract_priority": "high",
        "summary": "Suction pile sizing reference corpus from the Elements drive; small, high-value offshore foundation methodology candidate.",
        "tags": ["elements-ingest", "suction-pile", "offshore-foundations", "marine-engineering"],
    },
    {
        "order": 2,
        "bucket": "assethold-casa-grande-77017",
        "repo_bucket": "assethold",
        "parent": "/mnt/ace/assethold/casa-grande-77017",
        "stage": "/mnt/ace/assethold/casa-grande-77017/_from_elements",
        "wiki": "asset-management",
        "content_type": "asset-records",
        "extract_priority": "low",
        "summary": "Casa Grande assethold corpus from the Elements drive; metadata-only unless asset-management workflows need deeper synthesis.",
        "tags": ["elements-ingest", "asset-management", "casa-grande"],
    },
    {
        "order": 3,
        "bucket": "digitalmodel-qgis",
        "repo_bucket": "digitalmodel",
        "parent": "/mnt/ace/digitalmodel/tools/qgis",
        "stage": "/mnt/ace/digitalmodel/tools/qgis/_from_elements",
        "wiki": "engineering",
        "content_type": "engineering-tooling",
        "extract_priority": "high",
        "summary": "QGIS reusable engineering workflow/tooling data from the Elements drive.",
        "tags": ["elements-ingest", "qgis", "gis", "engineering-workflow"],
    },
    {
        "order": 4,
        "bucket": "digitalmodel-riser-toolbox",
        "repo_bucket": "digitalmodel",
        "parent": "/mnt/ace/digitalmodel/references/riser-toolbox",
        "stage": "/mnt/ace/digitalmodel/references/riser-toolbox/_from_elements",
        "wiki": "marine-engineering",
        "content_type": "engineering-reference",
        "extract_priority": "high",
        "summary": "Riser Toolbox reference corpus from the Elements drive; small, high-value riser/offshore methodology candidate.",
        "tags": ["elements-ingest", "riser", "offshore-engineering", "marine-engineering"],
    },
    {
        "order": 5,
        "bucket": "doris-62092-sesa",
        "repo_bucket": "doris",
        "parent": "/mnt/ace/doris/62092_sesa",
        "stage": "/mnt/ace/doris/62092_sesa/_from_elements",
        "wiki": "lng-projects",
        "content_type": "lng-project",
        "extract_priority": "medium",
        "summary": "SESA FLNG Terminal Project corpus staged from Elements and merged under Doris project data.",
        "tags": ["elements-ingest", "lng", "flng", "sesa", "doris"],
    },
    {
        "order": 6,
        "bucket": "doris-university",
        "repo_bucket": "doris",
        "parent": "/mnt/ace/doris/training",
        "stage": "/mnt/ace/doris/training/_from_elements",
        "wiki": "engineering",
        "content_type": "training",
        "extract_priority": "medium",
        "summary": "Doris University training corpus from the Elements drive; metadata-first training/source catalog.",
        "tags": ["elements-ingest", "training", "doris", "engineering"],
    },
    {
        "order": 7,
        "bucket": "doris-codes-specs",
        "repo_bucket": "doris",
        "parent": "/mnt/ace/doris/codes",
        "stage": "/mnt/ace/doris/codes/_from_elements/codes-doris",
        "wiki": "engineering-standards",
        "content_type": "codes-and-specifications",
        "extract_priority": "metadata-only",
        "summary": "Doris Codes and Specs corpus from Elements; large standards/specifications set requiring metadata-first handling before any legal/standards promotion.",
        "tags": ["elements-ingest", "codes", "specifications", "standards"],
    },
    {
        "order": 8,
        "bucket": "acma-projects-31522-woodfibre",
        "repo_bucket": "acma-projects",
        "parent": "/mnt/ace/acma-projects/31522-woodfibre-lng",
        "stage": "/mnt/ace/acma-projects/31522-woodfibre-lng/_from_elements",
        "wiki": "lng-projects",
        "content_type": "lng-project",
        "extract_priority": "metadata-only",
        "summary": "Woodfibre LNG project corpus for AceEngineer project 31522; very large corpus, metadata-first with curated extraction later.",
        "tags": ["elements-ingest", "lng", "woodfibre", "acma-projects", "project-31522"],
    },
]

EXTRACTABLE = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".csv", ".rtf", ".html", ".htm"}
SKIP_DIRS = {"_from_elements"}


def rel_for_parent(bucket: dict, rel: Path) -> Path:
    return Path(bucket["parent"]) / rel


def classify_ext(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {".pdf"}:
        return "pdf"
    if ext in {".doc", ".docx", ".rtf"}:
        return "document"
    if ext in {".xls", ".xlsx", ".xlsm", ".csv"}:
        return "tabular"
    if ext in {".ppt", ".pptx"}:
        return "presentation"
    if ext in {".txt", ".md", ".html", ".htm"}:
        return "text"
    if ext in {".zip", ".7z", ".rar", ".tar", ".gz"}:
        return "archive"
    if ext in {".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".bmp"}:
        return "image"
    if ext in {".dwg", ".dxf", ".step", ".stp", ".iges", ".igs"}:
        return "cad"
    if ext in {".dat", ".sim", ".yml", ".yaml", ".json"}:
        return "engineering-data"
    return "other"


def scan_bucket(bucket: dict) -> tuple[list[dict], dict]:
    stage = Path(bucket["stage"])
    parent = Path(bucket["parent"])
    records = []
    ext_counter = Counter()
    kind_counter = Counter()
    top_counter = Counter()
    missing = 0
    size_mismatch = 0
    not_hardlinked = 0
    total_bytes = 0

    for file_path in sorted(stage.rglob("*")):
        if not file_path.is_file():
            continue
        rel = file_path.relative_to(stage)
        parent_path = parent / rel
        try:
            st = file_path.stat()
        except FileNotFoundError:
            continue
        size = st.st_size
        total_bytes += size
        ext = file_path.suffix.lower() or "[no-ext]"
        kind = classify_ext(file_path)
        ext_counter[ext] += 1
        kind_counter[kind] += 1
        top = rel.parts[0] if rel.parts else "."
        top_counter[top] += 1

        parent_exists = parent_path.exists()
        same_size = False
        hardlinked = False
        if parent_exists:
            pst = parent_path.stat()
            same_size = pst.st_size == size
            hardlinked = pst.st_dev == st.st_dev and pst.st_ino == st.st_ino
            if not same_size:
                size_mismatch += 1
            if not hardlinked:
                not_hardlinked += 1
        else:
            missing += 1

        records.append({
            "source_issue": "workspace-hub#2526",
            "wiki_issue": "workspace-hub#2535",
            "cleanup_issue": "workspace-hub#2534",
            "repo_bucket": bucket["repo_bucket"],
            "bucket": bucket["bucket"],
            "wiki_domain_candidate": bucket["wiki"],
            "content_type_candidate": bucket["content_type"],
            "extract_priority": bucket["extract_priority"],
            "raw_source_policy": "link-only-parent-path-no-raw-copy-to-git",
            "parent_root": str(parent),
            "staging_root": str(stage),
            "absolute_path": str(parent_path),
            "staging_path": str(file_path),
            "relative_path": str(rel),
            "file_name": file_path.name,
            "extension": file_path.suffix.lower(),
            "content_kind": kind,
            "bytes": size,
            "mtime_ns": parent_path.stat().st_mtime_ns if parent_exists else st.st_mtime_ns,
            "parent_exists": parent_exists,
            "same_size": same_size,
            "hardlinked_to_staging": hardlinked,
        })

    summary = {
        **bucket,
        "files": len(records),
        "bytes": total_bytes,
        "missing": missing,
        "size_mismatch": size_mismatch,
        "not_hardlinked": not_hardlinked,
        "extensions": dict(ext_counter.most_common(25)),
        "content_kinds": dict(kind_counter.most_common()),
        "top_level_sample": dict(top_counter.most_common(25)),
    }
    return records, summary


def batch_record(summary: dict) -> dict:
    bucket = summary["bucket"]
    title = f"Elements ingest catalog — {bucket}"
    top = ", ".join(f"{k} ({v})" for k, v in list(summary["top_level_sample"].items())[:8]) or "n/a"
    kinds = ", ".join(f"{k}: {v}" for k, v in summary["content_kinds"].items())
    exts = ", ".join(f"{k}: {v}" for k, v in list(summary["extensions"].items())[:12])
    description = (
        f"Metadata-first catalog for the Elements-ingested `{bucket}` bucket. "
        f"The raw source of record remains `{summary['parent']}`; retained staging is `{summary['stage']}`. "
        f"This page represents {summary['files']:,} files / {summary['bytes']:,} bytes. "
        f"Top-level sample: {top}. Content kinds: {kinds}."
    )
    return {
        "id": f"elements-{bucket}",
        "slug": f"elements-{bucket}",
        "title": title,
        "summary": summary["summary"],
        "description": description,
        "tags": summary["tags"],
        "source_issue": "workspace-hub#2526",
        "wiki_issue": "workspace-hub#2535",
        "cleanup_issue": "workspace-hub#2534",
        "deep_extraction_issue": "workspace-hub#2536",
        "repo_bucket": summary["repo_bucket"],
        "bucket": bucket,
        "parent_root": summary["parent"],
        "retained_staging_root": summary["stage"],
        "files": summary["files"],
        "bytes": summary["bytes"],
        "content_type": summary["content_type"],
        "extract_priority": summary["extract_priority"],
        "raw_source_policy": "link-only; do not copy raw bulk data into git/wiki raw folders",
        "inventory_jsonl": ".planning/intel/elements-to-llm-wiki/elements-ingested-files.jsonl",
        "domain_summary": ".planning/intel/elements-to-llm-wiki/elements-wiki-domain-summary.md",
        "top_level_sample": top,
        "content_kinds": kinds,
        "extension_sample": exts,
        "verification": f"missing={summary['missing']}; size_mismatch={summary['size_mismatch']}; not_hardlinked={summary['not_hardlinked']}",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    BATCH.mkdir(parents=True, exist_ok=True)
    all_records: list[dict] = []
    summaries: list[dict] = []

    for bucket in BUCKETS:
        records, summary = scan_bucket(bucket)
        all_records.extend(records)
        summaries.append(summary)

    # Full inventory JSONL
    inv_path = OUT / "elements-ingested-files.jsonl"
    with inv_path.open("w", encoding="utf-8") as f:
        for rec in all_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Summary TSV
    summary_tsv = OUT / "elements-wiki-classification.tsv"
    with summary_tsv.open("w", newline="", encoding="utf-8") as f:
        fields = ["order", "bucket", "repo_bucket", "wiki", "content_type", "extract_priority", "parent", "stage", "files", "bytes", "missing", "size_mismatch", "not_hardlinked"]
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for s in summaries:
            writer.writerow({k: s.get(k, "") for k in fields})

    # Batch files by wiki, bucket-level source page records
    by_wiki = defaultdict(list)
    for s in summaries:
        by_wiki[s["wiki"]].append(batch_record(s))
    for wiki, rows in by_wiki.items():
        with (BATCH / f"{wiki}.jsonl").open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Deep extraction candidates: high/medium extractable files, cap not needed for TSV but prioritize small corpora first.
    candidates = [r for r in all_records if (r["extension"].lower() in EXTRACTABLE and r["extract_priority"] in {"high", "medium"})]
    candidates.sort(key=lambda r: ({"high": 0, "medium": 1}.get(r["extract_priority"], 9), r["bucket"], -int(r["bytes"])))
    cand_tsv = OUT / "deep-extraction-candidates.tsv"
    with cand_tsv.open("w", newline="", encoding="utf-8") as f:
        fields = ["extract_priority", "wiki_domain_candidate", "bucket", "content_kind", "extension", "bytes", "absolute_path", "relative_path"]
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for r in candidates:
            writer.writerow({k: r.get(k, "") for k in fields})

    # Markdown report
    total_files = sum(s["files"] for s in summaries)
    total_bytes = sum(s["bytes"] for s in summaries)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    report = OUT / "elements-wiki-domain-summary.md"
    lines = [
        "# Elements → LLM Wiki Metadata Index Summary",
        "",
        f"Generated: `{now}`",
        "",
        "## Policy",
        "",
        "- Raw bulk files remain in `/mnt/ace` parent targets.",
        "- Retained `_from_elements/` staging paths are provenance/retention artifacts only.",
        "- Wiki pages are metadata-first source/catalog pages; deep extraction is deferred to #2536.",
        "- Cleanup/deletion remains governed by #2534.",
        "",
        "## Totals",
        "",
        f"- Buckets: {len(summaries)}",
        f"- Files represented: {total_files:,}",
        f"- Bytes represented: {total_bytes:,}",
        "",
        "## Bucket summary",
        "",
        "| Order | Bucket | Wiki | Parent target | Files | Bytes | Priority | Verification |",
        "|---:|---|---|---|---:|---:|---|---|",
    ]
    for s in summaries:
        verification = f"missing={s['missing']}, size_mismatch={s['size_mismatch']}, not_hardlinked={s['not_hardlinked']}"
        lines.append(f"| {s['order']} | `{s['bucket']}` | `{s['wiki']}` | `{s['parent']}` | {s['files']:,} | {s['bytes']:,} | {s['extract_priority']} | {verification} |")
    lines.extend([
        "",
        "## Per-wiki batch files",
        "",
        "| Wiki | Batch file | Records |",
        "|---|---|---:|",
    ])
    for wiki, rows in sorted(by_wiki.items()):
        lines.append(f"| `{wiki}` | `.planning/intel/elements-to-llm-wiki/batches/{wiki}.jsonl` | {len(rows)} |")
    lines.extend([
        "",
        "## Deep extraction queue",
        "",
        f"Extractable high/medium-priority candidates written to `{cand_tsv.relative_to(ROOT)}`: {len(candidates):,} records.",
        "",
        "Recommended first pass: suction pile sizing, riser toolbox, QGIS, then SESA/Woodfibre selected LNG project files.",
    ])
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {inv_path}")
    print(f"Wrote {summary_tsv}")
    print(f"Wrote {cand_tsv}")
    print(f"Wrote {report}")
    for wiki in sorted(by_wiki):
        print(f"Wrote {BATCH / (wiki + '.jsonl')}")
    print(f"files={total_files} bytes={total_bytes}")
    failures = sum(s["missing"] + s["size_mismatch"] + s["not_hardlinked"] for s in summaries)
    print(f"verification_failures={failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
