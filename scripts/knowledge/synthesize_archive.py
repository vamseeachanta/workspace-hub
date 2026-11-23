#!/usr/bin/env python3
"""synthesize-archive.py — Parse archived WRKs, backfill knowledge base,
generate synthesis report.

Usage:
    synthesize-archive.py [--backfill-only | --report-only | --all] [--dry-run]
"""
import argparse
import fcntl
import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

def _repo_root():
    try:
        return Path(subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL, text=True).strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()

def _load_yaml(path):
    """Load YAML; regex fallback if PyYAML unavailable."""
    if HAS_YAML:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    data = {}
    for m in re.finditer(r'^(\w[\w_]*):\s*(.+)$', Path(path).read_text(), re.MULTILINE):
        data[m.group(1)] = m.group(2).strip().strip('"')
    return data

def parse_frontmatter(path):
    """Extract YAML frontmatter from a WRK .md file."""
    text = Path(path).read_text(errors="replace")
    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    defaults = {"id": Path(path).stem, "category": "uncategorized",
                "subcategory": "", "title": "", "complexity": ""}
    if not m:
        return defaults
    if HAS_YAML:
        try:
            data = yaml.safe_load(m.group(1)) or {}
        except Exception:
            data = {}
    else:
        data = {}
        for line in m.group(1).split("\n"):
            km = re.match(r'^(\w[\w_]*):\s*(.+)$', line)
            if km:
                data[km.group(1)] = km.group(2).strip().strip('"')
    for k, v in defaults.items():
        data.setdefault(k, v)
    repos = data.get("target_repos", [])
    data["target_repos"] = [repos] if isinstance(repos, str) else (repos or [])
    return data

def parse_wrk_body(path, max_chars=500):
    """First N chars of body after frontmatter."""
    text = Path(path).read_text(errors="replace")
    m = re.match(r'^---\n.*?\n---\n?', text, re.DOTALL)
    body = text[m.end():] if m else text
    return re.sub(r'\s+', ' ', body).strip()[:max_chars]

def scan_archived_wrks(archive_dir):
    """Find all WRK-*.md under archive (flat + YYYY-MM sharded)."""
    archive = Path(archive_dir)
    if not archive.is_dir():
        return []
    files = list(archive.glob("WRK-*.md"))
    files.extend(archive.glob("*/WRK-*.md"))
    return sorted(set(files))

def load_existing_ids(jsonl_path):
    """Load set of WRK IDs already in the JSONL file."""
    p = Path(jsonl_path)
    if not p.exists():
        return set()
    ids = set()
    for line in p.read_text().splitlines():
        if not line.strip():
            continue
        try:
            ids.add(json.loads(line).get("id", ""))
        except json.JSONDecodeError:
            continue
    return ids

def _evi(assets_dir, wrk_id, name):
    return Path(assets_dir) / wrk_id / "evidence" / name

def _load_future_work(assets_dir, wrk_id, limit=5):
    fw = _evi(assets_dir, wrk_id, "future-work.yaml")
    if not fw.is_file():
        return []
    try:
        recs = (_load_yaml(fw).get("recommendations", []) or [])
        return [r.get("id", "") for r in recs if r.get("id")][:limit]
    except Exception:
        return []

def _load_resource_gaps(assets_dir, wrk_id, limit=5):
    ri = _evi(assets_dir, wrk_id, "resource-intelligence.yaml")
    if not ri.is_file():
        return []
    try:
        d = _load_yaml(ri)
        items = (d.get("top_p2_gaps", []) or []) + (d.get("constraints", []) or [])
        return [str(g) for g in items][:limit]
    except Exception:
        return []

def _load_cost(assets_dir, wrk_id):
    cs = _evi(assets_dir, wrk_id, "cost-summary.yaml")
    if not cs.is_file():
        return None
    try:
        d = _load_yaml(cs)
        return {"input_tokens": int(d.get("total_input_tokens", 0) or 0),
                "output_tokens": int(d.get("total_output_tokens", 0) or 0)}
    except Exception:
        return None

def _count_unaddressed(assets_dir, wrk_id):
    fw = _evi(assets_dir, wrk_id, "future-work.yaml")
    if not fw.is_file():
        return 0, []
    try:
        recs = _load_yaml(fw).get("recommendations", []) or []
        un = [r for r in recs if r.get("status") == "pending" and not r.get("captured")]
        return len(un), [r.get("title", "") for r in un]
    except Exception:
        return 0, []

def _total_follow_ons(assets_dir, wrk_id):
    fw = _evi(assets_dir, wrk_id, "future-work.yaml")
    if not fw.is_file():
        return 0
    try:
        return len(_load_yaml(fw).get("recommendations", []) or [])
    except Exception:
        return 0

def backfill_knowledge(archive_dir, assets_dir, jsonl_path, dry_run=False):
    """Backfill missing WRK entries into wrk-completions.jsonl."""
    wrk_files = scan_archived_wrks(archive_dir)
    existing = load_existing_ids(jsonl_path)
    entries, already = [], 0
    for wf in wrk_files:
        fm = parse_frontmatter(wf)
        if fm["id"] in existing:
            already += 1
            continue
        entries.append({
            "id": fm["id"], "type": "wrk",
            "category": fm["category"], "subcategory": fm["subcategory"],
            "title": fm["title"],
            "archived_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": "synthesize-archive",
            "mission": parse_wrk_body(wf, max_chars=500),
            "patterns": _load_resource_gaps(assets_dir, fm["id"]),
            "follow_ons": _load_future_work(assets_dir, fm["id"]),
        })
    if not dry_run and entries:
        p = Path(jsonl_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(str(p) + ".lock", "w") as lf:
            try:
                fcntl.flock(lf, fcntl.LOCK_EX)
                with open(p, "a") as f:
                    for e in entries:
                        f.write(json.dumps(e) + "\n")
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)
    total = len(wrk_files)
    print(f"Backfilled {len(entries)} of {total} archived WRKs ({already} already existed)")
    return {"backfilled": len(entries), "already_existed": already, "total": total}

def _build_wrk_index(archive_dir):
    """Map WRK ID -> frontmatter for all archived WRKs."""
    return {fm["id"]: fm for wf in scan_archived_wrks(archive_dir)
            for fm in [parse_frontmatter(wf)]}

def _build_category_data(records, wrk_index, assets_dir):
    """Group records by category; compute subcats, follow-ons, spawners, cost."""
    by_cat = defaultdict(list)
    for r in records:
        by_cat[r.get("category", "uncategorized")].append(r)
    categories, total_tokens, cost_by_cat = {}, 0, defaultdict(int)
    for cat, recs in sorted(by_cat.items()):
        subs = defaultdict(lambda: {"count": 0, "repos": set()})
        unaddressed, spawners = [], []
        for r in recs:
            wid = r["id"]
            sc = r.get("subcategory", "") or "other"
            subs[sc]["count"] += 1
            for repo in wrk_index.get(wid, {}).get("target_repos", []):
                if isinstance(repo, str):
                    subs[sc]["repos"].add(repo)
            n_un, titles = _count_unaddressed(assets_dir, wid)
            if n_un > 0:
                unaddressed.append({"wrk": wid, "title": r.get("title", ""),
                                    "follow_on_count": n_un, "follow_ons": titles[:3]})
            n_total = _total_follow_ons(assets_dir, wid)
            if n_total >= 3:
                spawners.append({"wrk": wid, "follow_on_count": n_total,
                                 "pattern": titles[0] if titles else ""})
            cost = _load_cost(assets_dir, wid)
            if cost:
                t = cost["input_tokens"] + cost["output_tokens"]
                total_tokens += t
                cost_by_cat[cat] += t
        sub_dict = {sc: {"count": d["count"], "repos": sorted(d["repos"])}
                    for sc, d in sorted(subs.items())}
        categories[cat] = {"count": len(recs), "subcategories": sub_dict,
                           "unaddressed_follow_ons": unaddressed,
                           "repeat_spawners": spawners}
    return categories, total_tokens, dict(cost_by_cat)

def _load_jsonl_records(jsonl_path):
    """Load all JSON records from a JSONL file."""
    p = Path(jsonl_path)
    if not p.exists():
        return []
    records = []
    for line in p.read_text().splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records

def generate_synthesis_report(jsonl_path, archive_dir, assets_dir,
                              output_path, dry_run=False):
    """Generate archive-synthesis-report.yaml from JSONL + evidence."""
    records = _load_jsonl_records(jsonl_path)
    wrk_index = _build_wrk_index(archive_dir)
    categories, total_tokens, cost_by_cat = _build_category_data(
        records, wrk_index, assets_dir)
    heat_map = sorted([
        {"category": cat, "unaddressed_count": (n := len(info["unaddressed_follow_ons"])),
         "density": round(n / info["count"], 2) if info["count"] else 0}
        for cat, info in categories.items()
    ], key=lambda x: x["density"], reverse=True)
    report = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_archived": sum(c["count"] for c in categories.values()),
        "total_backfilled": len(records),
        "categories": categories,
        "cost_summary": {"total_tokens": total_tokens, "by_category": cost_by_cat},
        "heat_map": heat_map,
    }
    if not dry_run:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        writer = (lambda f: yaml.dump(report, f, default_flow_style=False, sort_keys=False)
                  ) if HAS_YAML else (lambda f: json.dump(report, f, indent=2))
        with open(out, "w") as f:
            writer(f)
        print(f"Synthesis report written to {out}")
    return report

def main():
    ap = argparse.ArgumentParser(description="Synthesize archived WRK items")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--backfill-only", action="store_true")
    g.add_argument("--report-only", action="store_true")
    g.add_argument("--all", action="store_true", default=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = _repo_root()
    archive = root / ".claude" / "work-queue" / "archive"
    assets = root / ".claude" / "work-queue" / "assets"
    jsonl = root / "knowledge-base" / "wrk-completions.jsonl"
    report = root / "docs" / "archive-synthesis-report.yaml"
    if not args.report_only:
        backfill_knowledge(archive, assets, jsonl, dry_run=args.dry_run)
    if not args.backfill_only:
        generate_synthesis_report(jsonl, archive, assets, report, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
