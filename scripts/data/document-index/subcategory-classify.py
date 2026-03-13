#!/usr/bin/env python3
# ABOUTME: Add subcategory classification to the document index
# ABOUTME: Hierarchical domain → subcategory taxonomy with path rules and keyword scoring

"""
Usage:
    python subcategory-classify.py --domain naval-architecture --batch-size 10 [--offset 0] [--apply]
    python subcategory-classify.py --domain marine --batch-size 10 [--apply]
    python subcategory-classify.py --all --batch-size 100 [--apply]
    python subcategory-classify.py --report
    python subcategory-classify.py --taxonomy  # print full taxonomy
"""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
INDEX_PATH = HUB_ROOT / "data" / "document-index" / "index.jsonl"
SUMMARIES_DIR = HUB_ROOT / "data" / "document-index" / "summaries"

# ── Subcategory Taxonomy ──────────────────────────────────────────────
# Each domain maps to subcategories, each with (keywords, weight) pairs
# and optional path rules

TAXONOMY = {
    "naval-architecture": {
        "ship-plans": {
            "path_rules": [r"/ship-plans/"],
            "keywords": [("ship plan", 4), ("lines plan", 4), ("general arrangement", 4)],
        },
        "hydrostatics-stability": {
            "path_rules": [r"/hydrostatics"],
            "keywords": [
                ("hydrostatic", 5), ("stability", 3), ("gz curve", 5),
                ("metacentric", 5), ("buoyancy", 3), ("trim", 2),
                ("intact stability", 5), ("damage stability", 5),
                ("freeboard", 3), ("displacement", 2),
            ],
        },
        "hydrodynamics": {
            "keywords": [
                ("hydrodynamic", 4), ("resistance", 3), ("propulsion", 3),
                ("wave resistance", 5), ("ship resistance", 5), ("drag", 3),
                ("wake", 3), ("flow", 2), ("boundary layer", 4),
                ("holtrop", 5), ("ittc", 5), ("froude", 4),
                ("fluid dynamic", 4), ("marine hydrodynamic", 5),
                ("hydromechanic", 4),
            ],
        },
        "ship-structures": {
            "keywords": [
                ("ship structural", 5), ("scantling", 5), ("hull girder", 5),
                ("ship construction", 5), ("midship section", 5), ("hull strength", 4),
                ("longitudinal strength", 4), ("ship steel", 3),
                ("ship-construction", 5), ("structural-analysis-design", 5),
            ],
        },
        "motions-seakeeping": {
            "keywords": [
                ("seakeeping", 5), ("ship motion", 5), ("roll", 2), ("pitch", 2),
                ("heave", 3), ("added mass", 4), ("strip theory", 5),
                ("controllability", 4), ("maneuvering", 4), ("rudder", 3),
                ("motions", 3), ("ship-performance", 4),
            ],
        },
        "ship-design": {
            "keywords": [
                ("ship design", 5), ("hull form", 4), ("preliminary design", 4),
                ("design spiral", 5), ("concept design", 4), ("hybrid hull", 4),
                ("hybrid-ship-hull", 5), ("design-principles", 4),
                ("ship-theory", 5), ("naval-architecture", 3),
                ("engineering-mathematics-ship", 5),
            ],
        },
        "classification-rules": {
            "keywords": [
                ("abs rule", 5), ("dnv rule", 5), ("lloyd's register", 5),
                ("bureau veritas", 4), ("classification society", 4),
                ("class rule", 4), ("survey", 2),
                ("abs-intro", 5), ("rules-and-guides", 5),
            ],
        },
        "naval-reference": {
            "keywords": [
                ("jane's", 5), ("warship", 4), ("fighting ship", 5),
                ("naval vessel", 3), ("naval history", 3),
                ("janes-fighting", 5), ("naval-submarine", 4),
            ],
        },
        "regulatory": {
            "keywords": [
                ("solas", 5), ("marpol", 5), ("imo", 3), ("mca", 4),
                ("flag state", 4), ("port state", 4), ("convention", 2),
            ],
        },
        "offshore-engineering": {
            "keywords": [
                ("offshore", 3), ("offshore engineering", 5), ("ocean engineering", 4),
                ("platform", 2), ("deepwater", 3),
                ("offshore-engineering", 5), ("offshore-hydromechanic", 5),
            ],
        },
    },
    "marine": {
        "mooring-analysis": {
            "keywords": [
                ("mooring", 5), ("anchor", 3), ("turret", 4), ("hawser", 4),
                ("chain", 2), ("api rp 2sk", 5), ("calm buoy", 5),
                ("spread mooring", 5), ("single point", 4),
            ],
        },
        "hydrodynamics-diffraction": {
            "keywords": [
                ("diffraction", 5), ("rao", 4), ("orcawave", 5), ("wamit", 5),
                ("panel method", 5), ("radiation", 3), ("added mass", 4),
                ("drift force", 5), ("wave excitation", 4), ("qft", 4),
            ],
        },
        "riser-analysis": {
            "keywords": [
                ("riser", 4), ("drilling riser", 5), ("production riser", 5),
                ("top tension", 4), ("flex joint", 5), ("stress joint", 5),
                ("riser connector", 4), ("viv", 3),
            ],
        },
        "viv-fatigue": {
            "keywords": [
                ("vortex-induced", 5), ("viv", 4), ("strouhal", 5),
                ("lock-in", 4), ("vibration suppression", 5), ("helical strake", 5),
                ("shear7", 5), ("vivana", 5),
            ],
        },
        "vessel-motions": {
            "keywords": [
                ("vessel motion", 5), ("fpso", 4), ("semi-submersible", 4),
                ("spar", 2), ("tlp", 3), ("hull motion", 4),
                ("offloading", 3), ("weathervane", 4),
            ],
        },
        "wave-environment": {
            "keywords": [
                ("wave statistics", 5), ("wave kinematics", 5), ("sea state", 4),
                ("significant wave", 4), ("wave spectrum", 5), ("jonswap", 5),
                ("pierson-moskowitz", 5), ("wave height", 3), ("wave period", 3),
                ("current profile", 4), ("metocean", 5),
            ],
        },
        "offshore-structures": {
            "keywords": [
                ("offshore platform", 5), ("jacket", 3), ("wellhead platform", 4),
                ("deck", 2), ("offshore structure", 4),
            ],
        },
        "marine-operations": {
            "keywords": [
                ("marine operation", 5), ("tow", 3), ("heavy lift", 4),
                ("float-over", 5), ("launch", 2), ("upending", 4),
                ("weather window", 4), ("dnv-rp-h103", 5),
            ],
        },
        "orcaflex-models": {
            "path_rules": [r"\.dat$", r"/[Oo]rcaflex/"],
            "keywords": [
                ("orcaflex", 5), (".dat", 2),
            ],
        },
    },
    "pipeline": {
        "design-code": {
            "keywords": [
                ("dnv-st-f101", 5), ("api rp 1111", 5), ("dnv-os-f101", 5),
                ("wall thickness", 4), ("pressure containment", 4),
                ("hoop stress", 4), ("collapse", 3),
            ],
        },
        "on-bottom-stability": {
            "keywords": [
                ("on-bottom stability", 5), ("dnv-rp-f109", 5), ("lateral stability", 4),
                ("pipe-soil", 4), ("hydrodynamic load", 3),
            ],
        },
        "free-span": {
            "keywords": [
                ("free span", 5), ("dnv-rp-f105", 5), ("spanning", 3),
                ("span assessment", 5), ("viv", 3), ("natural frequency", 3),
            ],
        },
        "installation": {
            "keywords": [
                ("j-lay", 5), ("s-lay", 5), ("reel-lay", 5), ("pipelay", 5),
                ("lay analysis", 4), ("overbend", 4), ("sagbend", 4),
                ("tensioner", 3), ("stinger", 4),
            ],
        },
        "umbilical-flowline": {
            "keywords": [
                ("umbilical", 4), ("flowline", 4), ("flexible pipe", 5),
                ("dynamic riser", 4), ("lazy wave", 5), ("steep wave", 5),
            ],
        },
        "subsea": {
            "keywords": [
                ("subsea", 4), ("manifold", 3), ("jumper", 3), ("spool", 3),
                ("tie-in", 4), ("subsea tree", 5), ("wellhead", 3),
            ],
        },
        "integrity": {
            "keywords": [
                ("pipeline integrity", 5), ("pig", 3), ("inline inspection", 5),
                ("corrosion", 3), ("anomaly", 3), ("fitness for service", 4),
                ("api 579", 4), ("remaining life", 4),
            ],
        },
    },
    "structural": {
        "fatigue-analysis": {
            "keywords": [
                ("fatigue", 4), ("s-n curve", 5), ("scf", 4), ("hot spot stress", 5),
                ("fatigue life", 4), ("cumulative damage", 5), ("miner", 4),
                ("rainflow", 5), ("fatigue crack", 4),
            ],
        },
        "tubular-joints": {
            "keywords": [
                ("tubular joint", 5), ("brace", 3), ("chord", 2),
                ("joint can", 4), ("punching shear", 5),
                ("api rp 2a", 3), ("efthymiou", 5),
            ],
        },
        "fea": {
            "keywords": [
                ("finite element", 5), ("fea", 4), ("ansys", 4), ("abaqus", 5),
                ("mesh", 3), ("element type", 3), ("von mises", 4),
                ("buckling", 3), ("eigenvalue", 3),
            ],
        },
        "weld-ndt": {
            "keywords": [
                ("weld", 3), ("welding procedure", 5), ("ndt", 4),
                ("radiograph", 4), ("ultrasonic", 3), ("wps", 4),
                ("pqr", 4), ("asme ix", 5),
            ],
        },
        "in-place-analysis": {
            "keywords": [
                ("in-place", 5), ("topside", 3), ("jacket", 3),
                ("unity check", 5), ("member check", 4), ("iso 19902", 4),
            ],
        },
        "transportation-lifting": {
            "keywords": [
                ("transportation", 3), ("sea transport", 5), ("barge", 3),
                ("lifting", 3), ("sling", 4), ("pad eye", 5),
                ("crane", 2), ("rigging", 3),
            ],
        },
    },
    "cathodic-protection": {
        "design": {
            "keywords": [
                ("cp design", 5), ("anode design", 5), ("current demand", 5),
                ("dnv-rp-b401", 5), ("protective potential", 4),
                ("anode mass", 4), ("utilization factor", 4),
            ],
        },
        "monitoring": {
            "keywords": [
                ("cp survey", 5), ("reference electrode", 5), ("potential measurement", 5),
                ("cp monitoring", 5), ("rov survey", 4),
            ],
        },
        "materials": {
            "keywords": [
                ("anode alloy", 5), ("zinc", 3), ("aluminium anode", 4),
                ("bracelet anode", 5), ("sacrificial anode", 4),
            ],
        },
        "coatings": {
            "keywords": [
                ("coating", 4), ("fbe", 5), ("3lpe", 5), ("paint", 2),
                ("coating breakdown", 5), ("coating resistance", 4),
            ],
        },
    },
    "materials": {
        "astm-standards": {
            "path_rules": [r"/ASTM/"],
            "keywords": [("astm", 4)],
        },
        "british-standards": {
            "path_rules": [r"/BS/"],
            "keywords": [("bs ", 3), ("british standard", 4)],
        },
        "metallurgy": {
            "keywords": [
                ("metallurgy", 5), ("microstructure", 5), ("heat treatment", 4),
                ("tensile", 3), ("charpy", 4), ("hardness", 3),
            ],
        },
        "composites": {
            "keywords": [
                ("composite", 4), ("laminate", 4), ("fibre", 3), ("fiber", 3),
                ("cfrp", 5), ("gfrp", 5), ("clt", 4),
            ],
        },
    },
    "cad": {
        "2d-drawings": {
            "keywords": [("dwg", 3), ("dxf", 3), ("autocad", 4), ("2d", 2)],
        },
        "3d-models": {
            "keywords": [
                ("step", 3), ("iges", 3), ("solidworks", 5), ("3d model", 4),
                ("parasolid", 5), ("sat", 2),
            ],
        },
    },
    "installation": {
        "pipelay": {
            "keywords": [
                ("j-lay", 5), ("s-lay", 5), ("reel-lay", 5), ("pipelay", 5),
            ],
        },
        "heavy-lift": {
            "keywords": [
                ("heavy lift", 5), ("crane", 3), ("derrick", 4),
                ("float-over", 5),
            ],
        },
        "umbilical-cable": {
            "keywords": [
                ("umbilical", 4), ("cable lay", 5), ("cable route", 4),
            ],
        },
    },
    "energy-economics": {
        "production-data": {
            "keywords": [("bsee", 5), ("production", 3), ("well data", 4)],
        },
        "market-analysis": {
            "keywords": [("eia", 4), ("price forecast", 4), ("economics", 3)],
        },
        "field-development": {
            "keywords": [("field development", 5), ("fpd", 4), ("reserves", 3)],
        },
    },
    "portfolio": {
        "equity-analysis": {
            "keywords": [("stock", 3), ("equity", 3), ("fundamental", 4)],
        },
        "options-derivatives": {
            "keywords": [("option", 3), ("covered call", 5), ("black-scholes", 5)],
        },
        "portfolio-management": {
            "keywords": [("portfolio", 3), ("sharpe", 5), ("allocation", 3)],
        },
    },
}


def get_summary(content_hash: str) -> Optional[Dict]:
    """Load summary by content hash."""
    if not content_hash:
        return None
    sha = content_hash.replace("sha256:", "")
    sfile = SUMMARIES_DIR / f"{sha}.json"
    if sfile.exists():
        try:
            with open(sfile) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return None


def classify_subcategory(
    record: Dict, domain: str, summary: Optional[Dict] = None,
    multi_threshold: float = 0.6,
) -> Tuple[List[str], float, str]:
    """Classify subcategory within a domain. Returns ([subcategories], confidence, reason).

    Multi-topic: if a second subcategory scores >= multi_threshold * best score,
    both are returned. This handles textbooks covering multiple disciplines.
    """
    if domain not in TAXONOMY:
        return ["general"], 0.1, "no_taxonomy_for_domain"

    subcats = TAXONOMY[domain]
    path = record.get("path", "").lower()

    # 1. Path rules (deterministic — single subcategory)
    for subcat_name, subcat_def in subcats.items():
        for pattern in subcat_def.get("path_rules", []):
            if re.search(pattern, path, re.IGNORECASE):
                return [subcat_name], 1.0, f"path_rule:{pattern}"

    # 2. Build searchable text
    parts = [path, str(record.get("org", "") or ""), str(record.get("doc_number", "") or "")]
    if summary:
        parts.extend([
            str(summary.get("title", "") or ""),
            str(summary.get("summary", "") or "")[:500],
            str(summary.get("text_preview", "") or "")[:500],
            str(summary.get("discipline", "") or ""),
        ])
    searchable = " ".join(parts).lower()

    # 3. Weighted keyword scoring
    scores: Dict[str, float] = {}
    for subcat_name, subcat_def in subcats.items():
        score = 0.0
        for kw, weight in subcat_def.get("keywords", []):
            if kw in searchable:
                score += weight
        if score > 0:
            scores[subcat_name] = score

    if not scores:
        return ["general"], 0.1, "no_keywords_matched"

    ranked = sorted(scores.items(), key=lambda x: -x[1])
    best_subcat, best_score = ranked[0]
    total = sum(scores.values())
    confidence = best_score / total if total > 0 else 0.0

    # Multi-topic: include subcategories scoring >= threshold * best
    result_subcats = [best_subcat]
    for subcat, score in ranked[1:]:
        if score >= multi_threshold * best_score:
            result_subcats.append(subcat)

    detail = "+".join(f"{s}={scores[s]:.0f}" for s in result_subcats)
    return result_subcats, confidence, f"keyword:{detail}"


def load_index() -> List[Dict]:
    records = []
    with open(INDEX_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def run_batch(records: List[Dict], args) -> List[Dict]:
    """Classify subcategories for a batch."""
    filtered = records
    if args.domain:
        filtered = [r for r in filtered if r.get("domain") == args.domain]
    if args.no_subcategory:
        filtered = [r for r in filtered if not r.get("subcategory")]

    start = args.offset
    end = start + args.batch_size
    batch = filtered[start:end]

    if not batch:
        print(f"No records (filtered={len(filtered)}, offset={start})")
        return []

    print(f"Batch: {len(batch)} records (of {len(filtered):,} filtered, offset {start})")
    print(f"{'='*100}")

    changes = []
    for i, rec in enumerate(batch):
        domain = rec.get("domain", "other")
        old_subcat = rec.get("subcategory")
        summary = get_summary(rec.get("content_hash", ""))

        new_subcats, confidence, reason = classify_subcategory(rec, domain, summary)
        new_val = new_subcats if len(new_subcats) > 1 else new_subcats[0]

        changed = new_val != old_subcat
        marker = "NEW" if old_subcat is None else ("CHANGE" if changed else "same")

        short_path = "/".join(rec["path"].split("/")[-3:])
        title = ""
        if summary:
            title = (summary.get("title") or "")[:50]

        subcat_display = ", ".join(new_subcats) if len(new_subcats) > 1 else new_subcats[0]

        print(f"\n[{i+1}/{len(batch)}] {marker}")
        print(f"  Path:        {short_path}")
        if title:
            print(f"  Title:       {title}")
        print(f"  Domain:      {domain}")
        print(f"  Subcategory: {old_subcat or 'NONE'} → {subcat_display} (conf={confidence:.2f}, {reason})")

        if changed:
            rec["subcategory"] = new_val
            changes.append(rec)

    print(f"\n{'='*100}")
    print(f"Changes: {len(changes)} / {len(batch)}")
    return changes


def apply_changes(records: List[Dict], changes: List[Dict]) -> None:
    change_map = {r["path"]: r for r in changes}
    updated = 0
    with open(INDEX_PATH, "w") as f:
        for rec in records:
            if rec["path"] in change_map:
                rec["subcategory"] = change_map[rec["path"]]["subcategory"]
                updated += 1
            f.write(json.dumps(rec) + "\n")
    print(f"Applied {updated} subcategory changes to {INDEX_PATH}")


def print_taxonomy():
    for domain, subcats in sorted(TAXONOMY.items()):
        print(f"\n{domain}:")
        for subcat, defn in subcats.items():
            kw_count = len(defn.get("keywords", []))
            pr_count = len(defn.get("path_rules", []))
            print(f"  {subcat:30s} ({kw_count} keywords, {pr_count} path rules)")


def print_report(records: List[Dict]):
    domain_subcat = defaultdict(Counter)
    has_subcat = 0
    for r in records:
        d = r.get("domain", "other")
        sc = r.get("subcategory")
        if sc:
            has_subcat += 1
            domain_subcat[d][sc] += 1
        else:
            domain_subcat[d]["(none)"] += 1

    print(f"Total records: {len(records):,}")
    print(f"With subcategory: {has_subcat:,} ({100*has_subcat/len(records):.1f}%)")
    print()
    for domain in sorted(domain_subcat.keys()):
        total = sum(domain_subcat[domain].values())
        print(f"{domain} ({total:,}):")
        for sc, count in domain_subcat[domain].most_common():
            print(f"  {sc:30s} {count:>8,}")
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", type=str)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--no-subcategory", action="store_true", help="Only records without subcategory")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--taxonomy", action="store_true")
    args = parser.parse_args()

    if args.taxonomy:
        print_taxonomy()
        return

    records = load_index()

    if args.report:
        print_report(records)
        return

    if args.all:
        args.no_subcategory = True
        # Process all domains that have taxonomy
        total_changes = []
        for domain in TAXONOMY:
            args.domain = domain
            domain_recs = [r for r in records if r.get("domain") == domain and not r.get("subcategory")]
            if not domain_recs:
                continue
            print(f"\n{'#'*100}")
            print(f"# Domain: {domain} ({len(domain_recs):,} records without subcategory)")
            print(f"{'#'*100}")
            batch = domain_recs[:args.batch_size]
            for i, rec in enumerate(batch):
                summary = get_summary(rec.get("content_hash", ""))
                subcats, conf, reason = classify_subcategory(rec, domain, summary)
                val = subcats if len(subcats) > 1 else subcats[0]
                rec["subcategory"] = val
                total_changes.append(rec)
                short_path = "/".join(rec["path"].split("/")[-3:])
                display = ", ".join(subcats)
                print(f"  [{i+1}] {short_path} → {display} ({conf:.2f})")
        if args.apply and total_changes:
            apply_changes(records, total_changes)
        return

    changes = run_batch(records, args)

    if args.apply and changes:
        confirm = input(f"Apply {len(changes)} subcategory changes? [y/N] ")
        if confirm.lower() == "y":
            apply_changes(records, changes)
    elif changes:
        print("\nDry run. Use --apply to commit.")


if __name__ == "__main__":
    main()
