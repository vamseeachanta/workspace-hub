#!/usr/bin/env python3
# ABOUTME: Build standards-transfer-ledger.yaml from enhancement-plan + data-sources + WRK items
# ABOUTME: Single source of truth for engineering code porting status (WRK-606)

"""
Merges three sources (in priority order, later wins):
  1. enhancement-plan.yaml     — seeds gap entries with doc_path + doc_number
  2. specs/data-sources/*.yaml — upgrades status for hand-curated entries
  3. WRK items (.claude/work-queue/) — upgrades status to wrk_captured / done

Output: data/document-index/standards-transfer-ledger.yaml

Usage:
    uv run --no-project python scripts/data/document-index/build-ledger.py
    uv run --no-project python scripts/data/document-index/build-ledger.py --dry-run
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]

ENHANCEMENT_PLAN = HUB_ROOT / "data/document-index/enhancement-plan.yaml"
DATA_SOURCES_DIR = HUB_ROOT / "specs/data-sources"
WRK_DIR = HUB_ROOT / ".claude/work-queue"
OUTPUT = HUB_ROOT / "data/document-index/standards-transfer-ledger.yaml"

# ---------------------------------------------------------------------------
# ID normalisation
# ---------------------------------------------------------------------------

ORG_PATTERNS = [
    (re.compile(r"^(DNV|DNVGL)[- ](OS|RP|ST)[- ]([A-Z][0-9]+)", re.I), "DNV", r"DNV-\2-\3"),
    (re.compile(r"^DNV[- ]?(OS|RP|ST)[- ]?([A-Z][0-9]+)", re.I),       "DNV", r"DNV-\1-\2"),
    (re.compile(r"^DNV[- ]?([A-Z][0-9]+)", re.I),                       "DNV", r"DNV-\1"),
    (re.compile(r"^API[- ]RP[- ]?([A-Z0-9]+)", re.I),                   "API", r"API-RP-\1"),
    (re.compile(r"^API[- ]STD[- ]?([A-Z0-9]+)", re.I),                  "API", r"API-STD-\1"),
    (re.compile(r"^API[- ]SPEC[- ]?([A-Z0-9]+)", re.I),                 "API", r"API-SPEC-\1"),
    (re.compile(r"^API[- ]([0-9]+[A-Z]*)", re.I),                       "API", r"API-RP-\1"),
    (re.compile(r"^ISO[- ]([0-9]+-[0-9]+)", re.I),                      "ISO", r"ISO-\1"),
    (re.compile(r"^ISO[- ]([0-9]+)", re.I),                              "ISO", r"ISO-\1"),
    (re.compile(r"^ASTM[- ]([A-Z][0-9]+)", re.I),                       "ASTM", r"ASTM-\1"),
    (re.compile(r"^NACE[- ]([A-Z0-9]+)", re.I),                         "NACE", r"NACE-\1"),
    (re.compile(r"^ABS[- ]([A-Z0-9]+)", re.I),                          "ABS", r"ABS-\1"),
    (re.compile(r"^ASME[- ]([A-Z0-9]+)", re.I),                         "ASME", r"ASME-\1"),
    (re.compile(r"^BS[- ]([0-9]+)", re.I),                              "BS", r"BS-\1"),
]


def normalize_id(raw_id: str, org_hint: str = "", domain_hint: str = "") -> str:
    """Normalise a raw standard ID to canonical form."""
    raw = raw_id.strip()
    for pattern, org, fmt in ORG_PATTERNS:
        m = pattern.match(raw)
        if m:
            result = pattern.sub(fmt, raw, count=1).upper()
            return result.replace(" ", "-")
    # Fallback: use as-is, uppercased, spaces→hyphens
    return raw.upper().replace(" ", "-")


def build_canonical_id(doc_num: str, org: str, title: str) -> str:
    """Build a canonical ID using title context when doc_num is a bare number."""
    # First: try to extract a full standard ID from the title
    title_pattern = re.compile(
        r"\b(DNV[-_ ]?(?:OS|RP|ST)[-_ ]?[A-Z][0-9]+|"
        r"DNV[-_ ]?[A-Z][0-9]+|"
        r"DNVGL[-_ ]?(?:OS|RP|ST)[-_ ]?[A-Z][0-9]+|"
        r"API[-_ ]?(?:RP|STD|SPEC)[-_ ]?[A-Z0-9]+|"
        r"API[-_ ]?[0-9]+[A-Z]*|"
        r"ISO[-_ ]?[0-9]+-[0-9]+|"
        r"ISO[-_ ]?[0-9]+|"
        r"ASTM[-_ ]?[A-Z][0-9]+|"
        r"NACE[-_ ]?(?:SP|MR|TM|RP)?[-_ ]?[0-9]+[A-Z]*)",
        re.I,
    )
    m = title_pattern.search(title)
    if m:
        return normalize_id(m.group(0))

    # Fallback: combine org + doc_num
    num = doc_num.strip().upper()
    t = title.upper()
    if org == "API":
        if "RP" in t:
            return f"API-RP-{num}"
        if "STD" in t:
            return f"API-STD-{num}"
        if "SPEC" in t:
            return f"API-SPEC-{num}"
        return f"API-RP-{num}"
    if org == "DNV":
        if "OS-" in t or " OS " in t:
            return f"DNV-OS-{num}"
        if "RP-" in t or " RP " in t:
            return f"DNV-RP-{num}"
        if "ST-" in t or " ST " in t:
            return f"DNV-ST-{num}"
        return f"DNV-{num}"
    if org == "ISO":
        return f"ISO-{num}"
    if org == "ASTM":
        return f"ASTM-{num}"
    if org == "NACE":
        return f"NACE-{num}"
    if org:
        return f"{org}-{num}"
    return num


def infer_org(raw_id: str, title: str, path: str) -> str:
    text = f"{raw_id} {title} {path}".upper()
    for kw, org in [("DNV", "DNV"), ("API", "API"), ("ISO", "ISO"),
                    ("ASTM", "ASTM"), ("NACE", "NACE"), ("ABS", "ABS"),
                    ("ASME", "ASME"), ("SNAME", "SNAME"), ("BS ", "BS"),
                    ("IEC", "IEC"), ("AISC", "AISC"), ("NORSOK", "NORSOK")]:
        if kw in text:
            return org
    return ""


# ---------------------------------------------------------------------------
# Source 1: enhancement-plan.yaml
# ---------------------------------------------------------------------------

def load_enhancement_plan() -> dict[str, dict]:
    """Return {norm_id: entry} for all items with a doc_number set."""
    entries: dict[str, dict] = {}

    with open(ENHANCEMENT_PLAN) as f:
        plan = yaml.safe_load(f)

    for domain, section in plan.get("by_domain", {}).items():
        for item in section.get("items", []):
            doc_num = (item.get("doc_number") or "").strip()
            if not doc_num:
                continue
            title = item.get("title", "").strip()
            path = item.get("path", "").strip()
            status = item.get("status", "gap")

            org = infer_org(doc_num, title, path)
            norm = build_canonical_id(doc_num, org, f"{title} {path}")
            if not norm:
                continue

            if norm in entries:
                # Keep the one with a better path
                existing = entries[norm]
                existing.setdefault("doc_paths", [])
                if path and path not in existing["doc_paths"]:
                    existing["doc_paths"].append(path)
                # Prefer more specific domain (not 'other')
                if existing.get("domain", "other") == "other" and domain != "other":
                    existing["domain"] = domain
            else:
                entries[norm] = {
                    "id": norm,
                    "title": title,
                    "org": org,
                    "domain": domain,
                    "doc_path": path,
                    "doc_paths": [path] if path else [],
                    "status": "gap" if status == "gap" else status,
                    "wrk_id": None,
                    "repo": None,
                    "modules": [],
                    "implemented_at": None,
                    "notes": "",
                }

    return entries


# ---------------------------------------------------------------------------
# Source 2: specs/data-sources/*.yaml
# ---------------------------------------------------------------------------

def merge_data_sources(entries: dict[str, dict]) -> None:
    """Upgrade status for standards in data-source YAMLs."""
    for yaml_path in sorted(glob.glob(str(DATA_SOURCES_DIR / "*.yaml"))):
        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        repo = data.get("repo", "")
        for s in data.get("standards", []):
            sid = (s.get("id") or "").strip()
            if not sid:
                continue
            org = infer_org(sid, s.get("title", ""), "")
            norm = normalize_id(sid, org_hint=org)
            ds_status = s.get("status", "")
            ds_domain = s.get("domain", "")

            if norm in entries:
                entry = entries[norm]
                # Upgrade status: implemented > reference > wrk_captured > gap
                STATUS_RANK = {"gap": 0, "wrk_captured": 1, "in_progress": 2,
                               "reference": 2, "done": 3, "deferred": 1}
                cur_rank = STATUS_RANK.get(entry.get("status", "gap"), 0)
                new_rank = STATUS_RANK.get(ds_status, 0)
                if new_rank > cur_rank:
                    entry["status"] = "done" if ds_status == "implemented" else ds_status
                if entry.get("repo") is None and repo:
                    entry["repo"] = repo
                if not entry.get("domain") or entry["domain"] == "other":
                    if ds_domain:
                        entry["domain"] = ds_domain
            else:
                # Not in enhancement plan — add from data-sources
                entries[norm] = {
                    "id": norm,
                    "title": s.get("title", sid),
                    "org": org,
                    "domain": ds_domain or "other",
                    "doc_path": "",
                    "doc_paths": [],
                    "status": "done" if ds_status == "implemented" else (ds_status or "reference"),
                    "wrk_id": None,
                    "repo": repo,
                    "modules": [],
                    "implemented_at": None,
                    "notes": s.get("summary", "")[:120] if s.get("summary") else "",
                }


# ---------------------------------------------------------------------------
# Source 3: WRK items
# ---------------------------------------------------------------------------

# Patterns to extract standard IDs from WRK body text
WRK_STD_RE = re.compile(
    r"\b(DNV[-_ ](?:OS|RP|ST)[-_ ][A-Z][0-9]+|"
    r"DNV[-_ ][A-Z][0-9]+|"
    r"API[-_ ](?:RP|STD|SPEC)[-_ ][A-Z0-9]+|"
    r"API[-_ ][0-9]+[A-Z]*|"
    r"ISO[-_ ][0-9]+-[0-9]+|"
    r"ISO[-_ ][0-9]+|"
    r"ASTM[-_ ][A-Z][0-9]+|"
    r"NACE[-_ ][A-Z0-9]+)",
    re.I,
)


def merge_wrk_items(entries: dict[str, dict]) -> None:
    """Link WRK items to standards; upgrade status to wrk_captured / done."""
    for folder in ["pending", "done"]:
        folder_path = WRK_DIR / folder
        if not folder_path.exists():
            continue
        for fname in sorted(folder_path.iterdir()):
            if not fname.name.startswith("WRK-"):
                continue
            wrk_id = fname.stem
            try:
                content = fname.read_text(errors="replace")
            except Exception:
                continue

            is_done = folder == "done"
            for m in WRK_STD_RE.finditer(content):
                raw = m.group(0)
                org = infer_org(raw, "", "")
                norm = normalize_id(raw, org_hint=org)
                if norm in entries:
                    entry = entries[norm]
                    cur_status = entry.get("status", "gap")
                    if cur_status in ("gap",):
                        entry["status"] = "done" if is_done else "wrk_captured"
                        entry["wrk_id"] = wrk_id
                    elif cur_status == "wrk_captured" and is_done:
                        entry["status"] = "done"
                    if entry.get("wrk_id") is None:
                        entry["wrk_id"] = wrk_id


# ---------------------------------------------------------------------------
# Write ledger
# ---------------------------------------------------------------------------

STATUS_ORDER = {"gap": 0, "wrk_captured": 1, "in_progress": 2,
                "reference": 3, "deferred": 4, "done": 5}
DOMAIN_ORDER = ["pipeline", "structural", "cathodic-protection", "marine",
                "installation", "materials", "energy-economics", "other"]


def write_ledger(entries: dict[str, dict], dry_run: bool) -> None:
    # Sort by domain order then ID
    def sort_key(e):
        d = e.get("domain", "other")
        di = DOMAIN_ORDER.index(d) if d in DOMAIN_ORDER else len(DOMAIN_ORDER)
        return (di, e["id"])

    standards_list = sorted(entries.values(), key=sort_key)

    # Summary counts
    counts: dict[str, int] = defaultdict(int)
    for e in standards_list:
        counts[e.get("status", "gap")] += 1

    ledger = {
        "generated": str(date.today()),
        "total": len(standards_list),
        "summary": dict(counts),
        "standards": standards_list,
    }

    # Print summary
    print(f"\nTotal standards: {len(standards_list)}")
    for k, v in sorted(counts.items(), key=lambda x: STATUS_ORDER.get(x[0], 99)):
        print(f"  {k:15} {v:>4}")

    # Domain breakdown for gap items
    gap_by_domain: dict[str, int] = defaultdict(int)
    for e in standards_list:
        if e.get("status") == "gap":
            gap_by_domain[e.get("domain", "other")] += 1
    if gap_by_domain:
        print("\nGaps by domain:")
        for d, c in sorted(gap_by_domain.items(), key=lambda x: -x[1]):
            print(f"  {d:25} {c:>4}")

    if dry_run:
        print("\n[dry-run] Not writing ledger.")
        return

    with open(OUTPUT, "w") as f:
        yaml.dump(ledger, f, default_flow_style=False, allow_unicode=True,
                  sort_keys=False, width=120)
    print(f"\nWrote {OUTPUT}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Build standards transfer ledger")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("Loading enhancement-plan.yaml…")
    entries = load_enhancement_plan()
    print(f"  {len(entries)} unique standards from enhancement-plan (with doc_number)")

    print("Merging data-sources/*.yaml…")
    merge_data_sources(entries)
    print(f"  {len(entries)} entries after merge")

    print("Linking WRK items…")
    merge_wrk_items(entries)

    write_ledger(entries, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
