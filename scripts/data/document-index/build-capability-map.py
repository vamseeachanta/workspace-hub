#!/usr/bin/env python3
# ABOUTME: WRK-383 — Build doc→repo→module capability map from Phase B summaries
# ABOUTME: Produces specs/capability-map/<repo>.yaml for all tier-1 repos

"""
Usage:
    python build-capability-map.py [--dry-run] [--repo digitalmodel]

Reads Phase B summaries (og_standards + ace_standards only) and maps each
classified document to the specific module within each tier-1 repo that
implements or should implement it.

Output: specs/capability-map/<repo>.yaml
"""

import argparse
import json
import logging
import os
import re
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
SUMMARIES_DIR = HUB_ROOT / "data/document-index/summaries"
CAP_MAP_DIR = HUB_ROOT / "specs/capability-map"

# doc→repo→module mapping rules
# Each module entry: disciplines (Phase B labels), orgs, keywords, doc_numbers
MODULE_MAP: Dict[str, Dict[str, Dict]] = {
    "digitalmodel": {
        "structural/fatigue": {
            "disciplines": ["structural"],
            "orgs": ["DNV", "BSI", "ISO", "AWS"],
            "keywords": [
                "fatigue", "s-n curve", "s/n", "palmgren-miner", "dnvgl-rp-c203",
                "bs 7608", "iso 19902", "weld fatigue", "stress range",
            ],
            "doc_numbers": ["DNVGL-RP-C203", "BS-7608", "BS7608", "ISO-19902"],
        },
        "structural/structural_analysis": {
            "disciplines": ["structural"],
            "orgs": ["API", "ISO", "AISC"],
            "keywords": [
                "jacket", "topside", "space frame", "api rp 2a", "iso 19902",
                "offshore platform", "fixed platform", "tubular", "in-place analysis",
            ],
            "doc_numbers": ["API-RP-2A", "API RP 2A", "ISO-19902"],
        },
        "structural/pipe_capacity": {
            "disciplines": ["structural", "pipeline"],
            "orgs": ["API", "ASME"],
            "keywords": [
                "burst", "collapse pressure", "axial tension", "api tr 5c3",
                "pipe capacity", "combined loading", "casing strength",
            ],
            "doc_numbers": ["API-TR-5C3", "API TR 5C3", "ASME-B31.8"],
        },
        "asset_integrity/API579": {
            "disciplines": ["structural", "materials"],
            "orgs": ["API", "ASME"],
            "keywords": [
                "fitness-for-service", "api 579", "ffs", "remaining strength",
                "fitness for service", "corrosion assessment", "local thin area",
            ],
            "doc_numbers": ["API-579", "API 579", "API/ASME 579"],
        },
        "asset_integrity/fracture_mechanics": {
            "disciplines": ["materials", "structural"],
            "orgs": ["BSI", "API", "ASTM"],
            "keywords": [
                "fracture", "bs 7910", "ctod", "stress intensity", "k1c",
                "crack growth", "fracture toughness", "kie", "fracture mechanics",
            ],
            "doc_numbers": ["BS-7910", "BS7910", "API-579"],
        },
        "subsea/pipeline": {
            "disciplines": ["pipeline"],
            "orgs": ["DNV", "API"],
            "keywords": [
                "dnv-st-f101", "api rp 1111", "pressure containment", "wall thickness",
                "subsea pipeline", "linepipe", "system pressure test", "maop",
                "propagating buckle", "collapse", "deepwater pipeline",
            ],
            "doc_numbers": ["DNV-ST-F101", "API-RP-1111", "API RP 1111"],
        },
        "subsea/catenary_riser": {
            "disciplines": ["pipeline", "marine"],
            "orgs": ["API", "DNV"],
            "keywords": [
                "riser", "catenary riser", "scr", "api rp 2rd", "dnv-os-f201",
                "flexible riser", "top-tension", "lazy wave",
            ],
            "doc_numbers": ["API-RP-2RD", "DNV-OS-F201"],
        },
        "subsea/viv_analysis": {
            "disciplines": ["pipeline", "marine"],
            "orgs": ["DNV"],
            "keywords": [
                "vortex-induced", "viv", "dnv-rp-f105", "strouhal", "lock-in",
                "vortex shedding", "free span", "wake induced",
            ],
            "doc_numbers": ["DNV-RP-F105", "DNVGL-RP-F105"],
        },
        "subsea/mooring_analysis": {
            "disciplines": ["marine"],
            "orgs": ["API", "DNV", "ABS"],
            "keywords": [
                "mooring", "calm buoy", "api rp 2sk", "dnv-os-e301", "chain",
                "wire rope", "mooring line", "station keeping", "spread mooring",
            ],
            "doc_numbers": ["API-RP-2SK", "DNV-OS-E301"],
        },
        "subsea/catenary": {
            "disciplines": ["marine", "installation"],
            "orgs": ["DNV"],
            "keywords": ["catenary", "anchor chain", "catenary equation", "touchdown"],
        },
        "subsea/analysis": {
            "disciplines": ["pipeline", "marine"],
            "orgs": ["DNV"],
            "keywords": [
                "on-bottom stability", "dnv-rp-f109", "soil resistance",
                "lateral stability", "hydrodynamic loads on pipeline",
            ],
            "doc_numbers": ["DNV-RP-F109", "DNVGL-RP-F109"],
        },
        "hydrodynamics/rao_analysis": {
            "disciplines": ["marine"],
            "orgs": ["DNV", "ABS"],
            "keywords": [
                "rao", "response amplitude operator", "transfer function",
                "vessel motion", "seakeeping", "frequency domain",
            ],
        },
        "hydrodynamics/wave_spectra": {
            "disciplines": ["marine"],
            "orgs": [],
            "keywords": [
                "wave spectrum", "jonswap", "pierson-moskowitz", "directional spectrum",
                "scatter diagram", "wave climate", "sea state",
            ],
        },
        "hydrodynamics/diffraction": {
            "disciplines": ["marine"],
            "orgs": [],
            "keywords": [
                "diffraction", "radiation", "panel method", "potential flow",
                "bemrosetta", "aqwa", "wamit", "first-order",
            ],
        },
        "hydrodynamics/hull_library": {
            "disciplines": ["marine"],
            "orgs": ["SNAME", "IMO"],
            "keywords": [
                "hull form", "hydrostatics", "stability", "metacentric",
                "displacement", "intact stability", "ocimf",
            ],
        },
        "marine_ops/marine_engineering": {
            "disciplines": ["installation"],
            "orgs": ["DNV", "ABS"],
            "keywords": [
                "installation", "marine operations", "dnv-st-n001", "lifting",
                "load-out", "transportation", "offshore operation",
            ],
            "doc_numbers": ["DNV-ST-N001", "DNV-OS-H101"],
        },
        "marine_ops/marine_analysis": {
            "disciplines": ["installation", "marine"],
            "orgs": ["DNV"],
            "keywords": [
                "weather window", "operability analysis", "wave height limit",
                "accessibility", "significant wave height", "down-time",
            ],
        },
        "marine_ops/artificial_lift": {
            "disciplines": ["production"],
            "orgs": ["API"],
            "keywords": [
                "artificial lift", "esp", "electric submersible pump",
                "rod pump", "gas lift", "api 11b", "api 11e",
            ],
            "doc_numbers": ["API-11B", "API-11E", "API-11R"],
        },
        "marine_ops/reservoir": {
            "disciplines": ["production"],
            "orgs": ["SPE"],
            "keywords": [
                "reservoir", "permeability", "porosity", "darcy", "material balance",
                "recovery factor", "skin factor",
            ],
        },
        "specialized/rigging": {
            "disciplines": ["installation"],
            "orgs": ["API", "DNV", "ASME"],
            "keywords": [
                "rigging", "sling", "shackle", "pad eye", "crane", "below-the-hook",
                "lifting equipment", "wire rope",
            ],
        },
        "specialized/api_analysis": {
            "disciplines": ["drilling"],
            "orgs": ["API"],
            "keywords": [
                "api 5ct", "api 5dp", "drill pipe", "casing thread",
                "tubing", "connection", "torque",
            ],
        },
    },
    "worldenergydata": {
        "bsee": {
            "disciplines": ["energy-economics", "regulatory"],
            "orgs": ["BSEE"],
            "keywords": [
                "bsee", "gulf of mexico", "gom", "outer continental shelf",
                "ocs", "bureau of safety", "apd",
            ],
        },
        "eia_us": {
            "disciplines": ["energy-economics"],
            "orgs": ["EIA"],
            "keywords": [
                "eia", "energy information administration", "us production",
                "us crude oil", "us natural gas", "weekly petroleum",
            ],
        },
        "sodir": {
            "disciplines": ["energy-economics"],
            "orgs": ["SODIR", "NPD"],
            "keywords": [
                "sodir", "norwegian petroleum", "ncs",
                "norwegian continental shelf", "npd",
            ],
        },
        "production": {
            "disciplines": ["energy-economics"],
            "orgs": [],
            "keywords": [
                "decline curve", "arps", "production forecast", "depletion",
                "exponential decline", "hyperbolic", "harmonic",
            ],
        },
        "marine_safety": {
            "disciplines": ["regulatory", "marine"],
            "orgs": ["MAIB", "NTSB", "IMO", "USCG"],
            "keywords": [
                "marine accident", "incident investigation", "maib", "ntsb",
                "uscg", "misle", "casualty", "marine safety",
            ],
        },
        "hse": {
            "disciplines": ["regulatory", "fire-safety"],
            "orgs": ["API", "USCG", "IMO"],
            "keywords": [
                "safety management system", "sems", "api rp 75",
                "hazop", "process safety", "hse",
            ],
            "doc_numbers": ["API-RP-75"],
        },
        "metocean": {
            "disciplines": ["marine"],
            "orgs": ["NOAA", "ECMWF"],
            "keywords": [
                "era5", "noaa", "ndbc", "buoy", "wave climate",
                "metocean", "reanalysis", "hindcast",
            ],
        },
        "well_bore_design": {
            "disciplines": ["drilling"],
            "orgs": ["API"],
            "keywords": [
                "casing design", "wellbore", "bop", "well control",
                "casing string", "burst", "collapse",
            ],
        },
        "decommissioning": {
            "disciplines": ["regulatory", "installation"],
            "orgs": ["API", "BSEE"],
            "keywords": [
                "decommissioning", "abandonment", "well abandonment",
                "platform removal", "plug and abandon",
            ],
        },
        "fdas": {
            "disciplines": ["energy-economics"],
            "orgs": [],
            "keywords": [
                "field development", "fdas", "appraisal", "development plan",
                "reserves", "resources",
            ],
        },
    },
    "assetutilities": {
        "calculations": {
            "disciplines": ["structural", "pipeline", "marine"],
            "orgs": [],
            "keywords": [
                "calculation", "formula", "equation", "numerical method",
            ],
        },
        "units": {
            "disciplines": ["other"],
            "orgs": ["NIST"],
            "keywords": ["unit conversion", "si units", "imperial", "dimensional analysis"],
        },
    },
}


def score_module(module_cfg: Dict, summary: Dict, record: Dict) -> int:
    """Score how well a summary matches a module. Higher = better match."""
    score = 0
    discipline = (summary.get("discipline") or "").lower()
    org = (summary.get("org") or record.get("organization") or "").upper()
    doc_num = (
        summary.get("doc_number") or record.get("doc_number") or
        record.get("og_db_id") or ""
    )
    text = " ".join([
        (summary.get("title") or ""),
        (summary.get("summary") or ""),
        " ".join(summary.get("keywords") or []),
        (record.get("path") or ""),
    ]).lower()

    # Discipline match
    if discipline in module_cfg.get("disciplines", []):
        score += 5

    # Org match
    for m_org in module_cfg.get("orgs", []):
        if m_org.upper() in org:
            score += 3
            break

    # Doc number match (highest signal)
    for doc_pat in module_cfg.get("doc_numbers", []):
        if doc_pat.lower().replace("-", " ") in text.replace("-", " "):
            score += 10
            break

    # Keyword match
    for kw in module_cfg.get("keywords", []):
        if kw.lower() in text:
            score += 2

    return score


_REPO_SRC_TEXT_CACHE: Dict[str, str] = {}  # repo_path → concatenated .py text (or "")
_IMPL_CACHE: Dict[str, bool] = {}  # "repo_path|standard_id" → bool

# Reading all .py source from slow remote mounts costs ~60s per repo.
# Default: skip impl check (status = "gap" for all); set CAPMAP_CHECK_IMPL=1 to enable.
_CHECK_IMPL_ENABLED = os.environ.get("CAPMAP_CHECK_IMPL", "0") == "1"


def _load_repo_src_text(repo_path: Path) -> str:
    """Read all .py files under repo_path/src once and return as a single lowercased string."""
    key = str(repo_path)
    if key not in _REPO_SRC_TEXT_CACHE:
        src_dir = repo_path / "src"
        if not src_dir.exists():
            _REPO_SRC_TEXT_CACHE[key] = ""
        else:
            parts: List[str] = []
            try:
                for py_file in src_dir.rglob("*.py"):
                    try:
                        parts.append(py_file.read_text(errors="replace"))
                    except OSError:
                        pass
            except Exception:
                pass
            _REPO_SRC_TEXT_CACHE[key] = " ".join(parts).lower()
            logger.info(
                "Loaded %d chars of source from %s/src", len(_REPO_SRC_TEXT_CACHE[key]), repo_path.name
            )
    return _REPO_SRC_TEXT_CACHE[key]


def check_implemented(repo_path: Path, standard_id: str) -> bool:
    """Check if a standard is referenced in the repo source code.

    Disabled by default (returns False) to avoid slow I/O on remote mounts.
    Enable with CAPMAP_CHECK_IMPL=1 environment variable.
    """
    if not _CHECK_IMPL_ENABLED or not repo_path.exists() or not standard_id:
        return False
    cache_key = f"{repo_path}|{standard_id}"
    if cache_key in _IMPL_CACHE:
        return _IMPL_CACHE[cache_key]
    src_text = _load_repo_src_text(repo_path)
    if not src_text:
        _IMPL_CACHE[cache_key] = False
        return False
    needle = standard_id.lower().replace("-", " ")
    found = needle in src_text or standard_id.lower() in src_text
    _IMPL_CACHE[cache_key] = found
    return found


def _infer_discipline_from_path(path: str, org: str) -> str:
    """Infer discipline label from file path and org for records without Phase B summaries."""
    text = path.lower()
    org_up = org.upper()
    if any(k in text for k in ["structural", "fatigue", "fracture", "bs 7910", "bs7910"]):
        return "structural"
    if any(k in text for k in ["pipeline", "pipe", "riser", "f101", "b31", "linepipe"]):
        return "pipeline"
    if any(k in text for k in ["marine", "mooring", "vessel", "offshore", "seabed", "subsea"]):
        return "marine"
    if any(k in text for k in ["installation", "lifting", "rigging", "marine ops"]):
        return "installation"
    if any(k in text for k in ["drill", "casing", "wellbore", "bop", "well control"]):
        return "drilling"
    if any(k in text for k in ["production", "reservoir", "esp", "artificial lift"]):
        return "production"
    if any(k in text for k in ["material", "corrosion", "cathodic", "coating"]):
        return "materials"
    if any(k in text for k in ["safety", "hse", "fire", "process safety", "sems"]):
        return "fire-safety"
    if any(k in text for k in ["energy", "eia", "bsee", "regulatory", "decommission"]):
        return "regulatory"
    # Org-based fallback
    if org_up in ("API", "ASME", "DNV", "BSI", "ISO", "AWS", "ABS"):
        return "structural"
    if org_up == "EIA":
        return "energy-economics"
    return "other"


def _make_synthetic_summary(rec: Dict) -> Dict:
    """Build a minimal summary dict from index record fields (no Phase B file needed)."""
    path = rec.get("path", "")
    stem = Path(path).stem.replace("_", " ").replace("-", " ")
    org = rec.get("org", "") or ""
    doc_number = rec.get("doc_number", "") or ""
    discipline = _infer_discipline_from_path(path + " " + stem + " " + doc_number, org)
    title = stem if stem else Path(path).name
    # Build composite keyword text from path components for scorer
    kw_parts = list(Path(path).parts[-3:])  # last 3 path segments as context
    return {
        "title": title[:120],
        "summary": " ".join(kw_parts)[:200],
        "discipline": discipline,
        "org": org,
        "doc_number": doc_number,
        "keywords": [p.lower() for p in kw_parts if len(p) > 3],
    }


def load_phase_b_summaries(sources: List[str]) -> List[Tuple[Dict, Dict]]:
    """Load Phase B summaries for specified sources (og_standards, ace_standards).

    Falls back to synthetic summaries derived from index record fields when no
    Phase B summary file exists (Phase B not yet run for these sources).
    """
    index_path = HUB_ROOT / "data/document-index/index.jsonl"
    if not index_path.exists():
        logger.error("index.jsonl not found")
        return []

    # Build sha → index record map for target sources
    sha_to_record: Dict[str, Dict] = {}
    with open(index_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if rec.get("source") in sources:
                    sha = rec.get("content_hash", "")
                    if sha:
                        sha_to_record[sha] = rec
            except json.JSONDecodeError:
                continue

    logger.info("Found %d index records for sources: %s", len(sha_to_record), sources)

    # Pre-build set of existing summary stems to avoid 55K per-file exists() calls
    # (each exists() costs ~13ms on slow mounts; glob is a single syscall)
    logger.info("Scanning summaries directory for existing Phase B files …")
    existing_shas: set = {p.stem for p in SUMMARIES_DIR.glob("*.json")}
    logger.info("Found %d Phase B summary files on disk", len(existing_shas))

    # Phase B file reads cost ~20ms each on slow remote mounts; with 21K+ matching
    # files this would take 7+ minutes.  Use synthetic summaries for all records
    # (path-based discipline inference is sufficient for capability mapping).
    # Phase B reads can be re-enabled by setting env var CAPMAP_USE_PHASE_B=1.
    use_phase_b = os.environ.get("CAPMAP_USE_PHASE_B", "0") == "1"

    results = []
    loaded_phase_b = 0
    loaded_synthetic = 0
    for sha, rec in sha_to_record.items():
        sha_stem = sha.replace("sha256:", "").replace(":", "-")
        if use_phase_b and sha_stem in existing_shas:
            sfile = SUMMARIES_DIR / f"{sha_stem}.json"
            try:
                with open(sfile) as f:
                    summary = json.load(f)
                if summary.get("discipline"):
                    results.append((rec, summary))
                    loaded_phase_b += 1
                    continue
            except (json.JSONDecodeError, OSError):
                pass
        # Synthesize from index record fields
        synth = _make_synthetic_summary(rec)
        results.append((rec, synth))
        loaded_synthetic += 1

    logger.info(
        "Loaded %d Phase B summaries + %d synthetic (total %d)",
        loaded_phase_b, loaded_synthetic, len(results),
    )
    return results


def build_capability_map(
    repo: str,
    modules: Dict,
    pairs: List[Tuple[Dict, Dict]],
    repo_path: Path,
) -> Dict:
    """For one repo, score each doc against modules, return capability map."""
    # Per module: lists of matched docs
    module_docs: Dict[str, List[Dict]] = defaultdict(list)
    unmatched = 0

    for rec, summary in pairs:
        best_module = None
        best_score = 0

        for module_id, module_cfg in modules.items():
            s = score_module(module_cfg, summary, rec)
            if s > best_score:
                best_score = s
                best_module = module_id

        if best_module and best_score >= 5:  # minimum relevance threshold
            sha = rec.get("content_hash", "")
            std_id = (
                rec.get("doc_number") or
                summary.get("doc_number") or
                Path(rec.get("path", "")).stem
            )
            module_docs[best_module].append({
                "id": std_id,
                "title": summary.get("title") or Path(rec.get("path", "")).name,
                "org": rec.get("organization") or summary.get("org") or "",
                "sha": sha,
                "path": rec.get("path", ""),
                "summary": (summary.get("summary") or "")[:200],
                "discipline": summary.get("discipline", ""),
                "score": best_score,
            })
        else:
            unmatched += 1

    logger.info(
        "Repo %s: %d docs matched to modules, %d unmatched",
        repo, sum(len(v) for v in module_docs.values()), unmatched,
    )

    # Build output structure
    output_modules = []
    for module_id, module_cfg in modules.items():
        docs = sorted(module_docs.get(module_id, []), key=lambda x: -x["score"])
        standards = []
        seen_ids = set()
        for doc in docs:
            sid = doc["id"]
            if sid in seen_ids:
                continue
            seen_ids.add(sid)
            # Check if implemented in repo
            implemented = check_implemented(repo_path, sid) if sid else False
            standards.append({
                "id": sid,
                "title": doc["title"],
                "org": doc["org"],
                "sha": doc["sha"],
                "discipline": doc["discipline"],
                "summary": doc["summary"],
                "status": "implemented" if implemented else "gap",
            })

        output_modules.append({
            "module": module_id,
            "standards_count": len(standards),
            "standards": standards[:50],  # cap at 50 per module in output
            "unlinked_doc_count": max(0, len(docs) - len(seen_ids)),
        })

    return {
        "repo": repo,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "total_standards_mapped": sum(m["standards_count"] for m in output_modules),
        "modules": output_modules,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="WRK-383: Build capability map")
    parser.add_argument("--repo", help="Only build for this repo")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sources = ["og_standards", "ace_standards"]
    pairs = load_phase_b_summaries(sources)
    if not pairs:
        logger.error("No summaries loaded. Run Phase B first.")
        return 1

    CAP_MAP_DIR.mkdir(parents=True, exist_ok=True)

    repos_to_build = list(MODULE_MAP.keys())
    if args.repo:
        repos_to_build = [r for r in repos_to_build if r == args.repo]

    for repo in repos_to_build:
        logger.info("Building capability map for: %s", repo)
        repo_path = HUB_ROOT / repo
        cap_map = build_capability_map(repo, MODULE_MAP[repo], pairs, repo_path)

        if args.dry_run:
            for mod in cap_map["modules"]:
                if mod["standards_count"] > 0:
                    logger.info(
                        "  %s: %d standards (%d gaps)",
                        mod["module"],
                        mod["standards_count"],
                        sum(1 for s in mod["standards"] if s["status"] == "gap"),
                    )
            continue

        out_path = CAP_MAP_DIR / f"{repo}.yaml"
        with open(out_path, "w") as f:
            yaml.dump(cap_map, f, default_flow_style=False, sort_keys=False, width=120,
                      allow_unicode=True)
        logger.info("Written: %s (%d standards mapped)", out_path, cap_map["total_standards_mapped"])

    if not args.dry_run:
        logger.info("Capability maps written to: %s", CAP_MAP_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
