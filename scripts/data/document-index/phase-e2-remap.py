#!/usr/bin/env python3
# ABOUTME: Phase E2 targeted remap — reclassify domain=other and fill target_repos gaps (WRK-309)
# ABOUTME: Applies path rules, filename-prefix rules, and script-extension rules in priority order

"""
Targeted remap pass on index.jsonl to resolve the 725K records with empty target_repos
and the 249K records stuck at domain=other.

Three rule tiers (first match wins per record):
  1. Path rules   — directory context is decisive (ASTM/, ri/, disciplines/, etc.)
  2. Filename rules — standards body prefix in filename (API, DNV, ASTM, SPE, ...)
  3. Script rules  — file extension (.m, .inp, .dat, .py) + path context

Also maps workspace-spec → workspace-hub and fills target_repos for all remaining
correctly-classified records that still have an empty repo list.

Usage:
    uv run --no-project python scripts/data/document-index/phase-e2-remap.py
    uv run --no-project python scripts/data/document-index/phase-e2-remap.py --dry-run
    uv run --no-project python scripts/data/document-index/phase-e2-remap.py --limit 5000 --dry-run

Results:
    Rewrites index.jsonl in-place (atomic rename).
    Backs up original to index.jsonl.bak (overwritten each run).
    Updates registry.yaml domain counts.
    Prints per-rule change counts.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Optional

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_CONFIG = SCRIPT_DIR / "config.yaml"

# ---------------------------------------------------------------------------
# Rule tables
# ---------------------------------------------------------------------------

# Path rules: (path_substring, ext_set_or_None, new_domain, new_repos, rule_name)
# Checked against the full path (case-sensitive substring match).
# ext_set: set of lowercase extensions without dot, or None for any extension.
# Ordered — first match wins.
PATH_RULES: list[tuple[str, Optional[set[str]], str, list[str], str]] = [
    # ── ace/docs/_standards/raw sub-directories (WRK-605) ────────────────
    # Most-specific first within the raw bucket.
    # 0000 Codes & Standards — per-org mappings
    ("_standards/raw/0000 Codes & Standards/ABS",       None, "structural",           ["digitalmodel"],                       "raw_cs_abs"),
    ("_standards/raw/0000 Codes & Standards/AISC",      None, "structural",           ["digitalmodel"],                       "raw_cs_aisc"),
    ("_standards/raw/0000 Codes & Standards/AMJIG",     None, "structural",           ["assetutilities"],                     "raw_cs_amjig"),
    ("_standards/raw/0000 Codes & Standards/AMS",       None, "structural",           ["digitalmodel"],                       "raw_cs_ams"),
    ("_standards/raw/0000 Codes & Standards/ANSI",      None, "structural",           ["digitalmodel"],                       "raw_cs_ansi"),
    ("_standards/raw/0000 Codes & Standards/AS/",       None, "structural",           ["digitalmodel"],                       "raw_cs_as"),
    ("_standards/raw/0000 Codes & Standards/ASCE",      None, "structural",           ["digitalmodel"],                       "raw_cs_asce"),
    ("_standards/raw/0000 Codes & Standards/ASME",      None, "structural",           ["digitalmodel"],                       "raw_cs_asme"),
    ("_standards/raw/0000 Codes & Standards/ASNT",      None, "structural",           ["digitalmodel"],                       "raw_cs_asnt"),
    ("_standards/raw/0000 Codes & Standards/ASTM",      None, "structural",           ["digitalmodel"],                       "raw_cs_astm"),
    ("_standards/raw/0000 Codes & Standards/AWHEM",     None, "structural",           ["digitalmodel"],                       "raw_cs_awhem"),
    ("_standards/raw/0000 Codes & Standards/AWS",       None, "structural",           ["digitalmodel"],                       "raw_cs_aws"),
    ("_standards/raw/0000 Codes & Standards/BSI",       None, "structural",           ["digitalmodel"],                       "raw_cs_bsi"),
    ("_standards/raw/0000 Codes & Standards/CFR",       None, "structural",           ["digitalmodel"],                       "raw_cs_cfr"),
    ("_standards/raw/0000 Codes & Standards/DNV",       None, "pipeline",             ["digitalmodel"],                       "raw_cs_dnv"),
    ("_standards/raw/0000 Codes & Standards/FAA",       None, "structural",           ["digitalmodel"],                       "raw_cs_faa"),
    ("_standards/raw/0000 Codes & Standards/GLND",      None, "structural",           ["digitalmodel"],                       "raw_cs_glnd"),
    ("_standards/raw/0000 Codes & Standards/HSE",       None, "structural",           ["digitalmodel"],                       "raw_cs_hse"),
    ("_standards/raw/0000 Codes & Standards/IADC-TPC",  None, "pipeline",             ["digitalmodel"],                       "raw_cs_iadc"),
    ("_standards/raw/0000 Codes & Standards/IEC",       None, "structural",           ["digitalmodel"],                       "raw_cs_iec"),
    ("_standards/raw/0000 Codes & Standards/ISO",       None, "pipeline",             ["digitalmodel"],                       "raw_cs_iso"),
    ("_standards/raw/0000 Codes & Standards/MIL",       None, "structural",           ["digitalmodel"],                       "raw_cs_mil"),
    ("_standards/raw/0000 Codes & Standards/NACE",      None, "cathodic-protection",  ["digitalmodel"],                       "raw_cs_nace"),
    ("_standards/raw/0000 Codes & Standards/_Needs Filing_", None, "pipeline",        ["digitalmodel"],                       "raw_cs_needs_filing"),
    ("_standards/raw/0000 Codes & Standards/NEMA",      None, "structural",           ["digitalmodel"],                       "raw_cs_nema"),
    ("_standards/raw/0000 Codes & Standards/NFPA",      None, "structural",           ["digitalmodel"],                       "raw_cs_nfpa"),
    ("_standards/raw/0000 Codes & Standards/Norsok",    None, "pipeline",             ["digitalmodel"],                       "raw_cs_norsok"),
    ("_standards/raw/0000 Codes & Standards/OnePetro",  None, "pipeline",             ["digitalmodel"],                       "raw_cs_onepetro"),
    ("_standards/raw/0000 Codes & Standards/SNAME",     None, "marine",               ["digitalmodel"],                       "raw_cs_sname"),
    ("_standards/raw/0000 Codes & Standards/Spare",     None, "pipeline",             ["digitalmodel"],                       "raw_cs_spare"),
    ("_standards/raw/0000 Codes & Standards/unsorted",  None, "pipeline",             ["digitalmodel"],                       "raw_cs_unsorted"),
    # Catch-all for any remaining 0000 Codes & Standards subdirs
    ("_standards/raw/0000 Codes & Standards",           None, "pipeline",             ["digitalmodel"],                       "raw_cs_fallback"),
    # Oil and Gas Codes — per-org mappings
    ("_standards/raw/Oil and Gas Codes/API Standards",  None, "pipeline",             ["digitalmodel"],                       "raw_ogc_api_standards"),
    ("_standards/raw/Oil and Gas Codes/API Stds",       None, "pipeline",             ["digitalmodel"],                       "raw_ogc_api_stds"),
    ("_standards/raw/Oil and Gas Codes/ASTM Standards", None, "structural",           ["digitalmodel"],                       "raw_ogc_astm"),
    ("_standards/raw/Oil and Gas Codes/British Library", None, "pipeline",            ["digitalmodel"],                       "raw_ogc_british_library"),
    ("_standards/raw/Oil and Gas Codes/BSI Standards",  None, "structural",           ["digitalmodel"],                       "raw_ogc_bsi"),
    ("_standards/raw/Oil and Gas Codes/DNV Standards",  None, "pipeline",             ["digitalmodel"],                       "raw_ogc_dnv"),
    ("_standards/raw/Oil and Gas Codes/ISO Standards",  None, "pipeline",             ["digitalmodel"],                       "raw_ogc_iso"),
    ("_standards/raw/Oil and Gas Codes/MIL Standards",  None, "structural",           ["digitalmodel"],                       "raw_ogc_mil"),
    ("_standards/raw/Oil and Gas Codes/Norsok",         None, "pipeline",             ["digitalmodel"],                       "raw_ogc_norsok"),
    ("_standards/raw/Oil and Gas Codes/Papers",         None, "pipeline",             ["digitalmodel"],                       "raw_ogc_papers"),
    # Catch-all for any remaining Oil and Gas Codes subdirs/files
    ("_standards/raw/Oil and Gas Codes",                None, "pipeline",             ["digitalmodel"],                       "raw_ogc_fallback"),
    # Ultimate catch-all for _standards/raw/
    ("_standards/raw",                                  None, "pipeline",             ["digitalmodel"],                       "raw_fallback"),
    # ── ace/docs/_standards sub-directories ──────────────────────────────
    ("_standards/ASTM",     None,               "materials",            ["digitalmodel", "OGManufacturing"],    "ace_astm"),
    ("_standards/NACE",     None,               "cathodic-protection",  ["digitalmodel"],                       "ace_nace"),
    ("_standards/API",      None,               "pipeline",             ["digitalmodel", "doris"],              "ace_api"),
    ("_standards/ISO",      None,               "structural",           ["digitalmodel", "OGManufacturing"],    "ace_iso"),
    ("_standards/BS",       None,               "structural",           ["digitalmodel", "OGManufacturing"],    "ace_bs"),
    ("_standards/ASME",     None,               "structural",           ["digitalmodel", "OGManufacturing"],    "ace_asme"),
    ("_standards/SNAME",    None,               "marine",               ["digitalmodel"],                       "ace_sname"),
    ("_standards/Norsok",   None,               "structural",           ["digitalmodel", "OGManufacturing"],    "ace_norsok"),
    # ── O&G Standards DB sub-directories ────────────────────────────────
    ("Codes & Standards/ASTM",   None,          "materials",            ["digitalmodel", "OGManufacturing"],    "og_astm"),
    ("Codes & Standards/API",    None,          "pipeline",             ["digitalmodel", "doris"],              "og_api"),
    ("Codes & Standards/ISO",    None,          "structural",           ["digitalmodel", "OGManufacturing"],    "og_iso"),
    ("Codes & Standards/ASCE",   None,          "structural",           ["digitalmodel", "OGManufacturing"],    "og_asce"),
    ("Codes & Standards/AS",     None,          "structural",           ["digitalmodel", "OGManufacturing"],    "og_as"),
    ("Oil and Gas Codes/API",    None,          "pipeline",             ["digitalmodel", "doris"],              "og_api_stds"),
    # ── dde/documents sub-directories (most specific first) ─────────────
    ("dde/documents/ri/",               None,   "marine",               ["digitalmodel"],                       "dde_ri_riser"),
    ("dde/documents/614 Sewol",         None,   "marine",               [],                                     "dde_sewol"),
    ("dde/documents/simulation",        None,   "structural",           ["digitalmodel"],                       "dde_simulation"),
    ("dde/documents/0168_Python",       None,   "project-management",   ["acma-projects"],                      "dde_0168_python"),
    ("dde/documents/0163 FDAS",         None,   "energy-economics",     ["worldenergydata"],                    "dde_0163_fdas"),
    # All remaining numbered ACMA project folders (0NNN prefix handled below by regex in apply_path_rules)
    # Fallback: any remaining dde/documents/ → acma-projects
    ("dde/documents/",                  None,   "project-management",   ["acma-projects"],                      "dde_acma_projects"),
    # ── ace/docs/disciplines sub-directories ────────────────────────────
    ("disciplines/production",   {"py", "csv"},         "energy-economics",  ["worldenergydata"],               "disciplines_production_scripts"),
    ("disciplines/production",   None,                  "energy-economics",  ["worldenergydata", "digitalmodel"],"disciplines_production_docs"),
    ("disciplines/completion",   {"inp", "dat", "m"},   "structural",        ["digitalmodel", "OGManufacturing"],"disciplines_completion_scripts"),
    ("disciplines/completion",   None,                  "structural",        ["digitalmodel", "OGManufacturing"],"disciplines_completion_docs"),
    ("disciplines/drilling",     {"m", "py", "dat"},    "installation",      ["digitalmodel"],                  "disciplines_drilling_scripts"),
    ("disciplines/drilling",     None,                  "installation",      ["digitalmodel"],                  "disciplines_drilling_docs"),
    ("disciplines/misc",         {"m", "bas", "mac"},   "structural",        ["digitalmodel", "OGManufacturing"],"disciplines_misc_scripts"),
    ("disciplines/misc",         None,                  "other",             [],                                 "disciplines_misc_docs"),
    ("disciplines/knowledge",    None,                  "other",             [],                                 "disciplines_knowledge"),
    # ── workspace specs ──────────────────────────────────────────────────
    ("workspace-hub/specs",      None,                  "workspace-spec",    ["workspace-hub"],                  "workspace_specs"),
]

# Filename rules: (prefixes_tuple, new_domain, new_repos)
# Checked against UPPERCASE filename (without extension).
# Applied only when no path rule matched.
FILENAME_RULES: list[tuple[tuple[str, ...], str, list[str]]] = [
    (("API RP ", "API-RP-", "API STD ", "API-STD-", "API SPEC ", "API-SPEC-",
      "API TR ", "API-TR-", "API BULL", "API MPMS"),
     "pipeline",            ["digitalmodel", "doris"]),
    (("SPE-", "SPE "),
     "energy-economics",    ["worldenergydata"]),
    (("DNV-", "DNV ", "DNVGL-", "DNVGL ", "DNV GL"),
     "marine",              ["digitalmodel"]),
    (("ABS ", "ABS-", "ABS_"),
     "marine",              ["digitalmodel"]),
    (("SNAME ", "SNAME-"),
     "marine",              ["digitalmodel"]),
    (("ISO ", "ISO-", "ISO_"),
     "structural",          ["digitalmodel", "OGManufacturing"]),
    (("ASME ", "ASME-"),
     "structural",          ["digitalmodel", "OGManufacturing"]),
    (("ASCE ", "ASCE-"),
     "structural",          ["digitalmodel", "OGManufacturing"]),
    (("NORSOK ", "NORSOK-"),
     "structural",          ["digitalmodel", "OGManufacturing"]),
    (("AISC ", "AISC-"),
     "structural",          ["digitalmodel", "OGManufacturing"]),
    (("BS ", "BS-"),
     "structural",          ["digitalmodel", "OGManufacturing"]),
    (("ASTM ", "ASTM-", "ASTM_"),
     "materials",           ["digitalmodel", "OGManufacturing"]),
    (("AWS A", "AWS D", "AWS B", "AWS C"),
     "materials",           ["digitalmodel", "OGManufacturing"]),
    (("NACE ", "NACE-", "NACE_", "NACE TM", "NACE MR"),
     "cathodic-protection", ["digitalmodel"]),
    (("IEC ", "IEC-"),
     "regulatory",          ["digitalmodel"]),
    (("IOGP ", "IOGP-", "OGP "),
     "regulatory",          ["digitalmodel"]),
    (("API 579", "API 578", "API 570", "API 580"),
     "structural",          ["digitalmodel", "OGManufacturing"]),
]

# Script extension rules: (ext_set, path_contains_any, new_domain, new_repos, rule_name)
# Applied only when no path or filename rule matched.
SCRIPT_RULES: list[tuple[set[str], list[str], str, list[str], str]] = [
    ({"dat"},  ["Orcaflex", "orcaflex", "drilling riser", "riser"],
               "installation",      ["digitalmodel"],                       "orcaflex_dat"),
    ({"dat"},  [],                   "installation",      ["digitalmodel"],  "dat_generic"),
    ({"inp"},  [],                   "structural",        ["digitalmodel", "OGManufacturing"], "ansys_inp"),
    ({"m"},    ["API", "VIV", "SCF", "fatigue", "riser"],
               "structural",        ["digitalmodel", "OGManufacturing"],    "matlab_structural"),
    ({"m"},    [],                   "structural",        ["digitalmodel", "OGManufacturing"], "matlab_generic"),
    ({"bas"},  [],                   "other",             [],                "vba_bas"),
    ({"mac"},  [],                   "structural",        ["digitalmodel"],  "apdl_mac"),
]

# Domains that are already well-classified — only fill repos if missing
WELL_CLASSIFIED_DOMAINS = {
    "structural", "cathodic-protection", "pipeline", "marine",
    "installation", "energy-economics", "portfolio", "materials",
    "regulatory",
}

# Skip path fragments — don't apply any rules to these
SKIP_PATH_FRAGMENTS = [
    "Information_Family",
    "Information_Friends",
    "Information_Important",
    "Personal/",
    # _standards/raw/ — reclassified in WRK-605 (no longer skipped)
    "Literature/",         # general reference, not repo-specific
    "TECH Animation",
    "TECH Writing",
    "2021-11-22-sd-HDD",   # legacy backup, too mixed to classify in bulk
    "va-hdd-2",            # legacy backup
    "dropbox_contents",    # legacy backup
]


# ---------------------------------------------------------------------------
# Rule application
# ---------------------------------------------------------------------------

def apply_path_rules(path: str, ext: str) -> Optional[tuple[str, list[str], str]]:
    """Return (new_domain, new_repos, rule_name) or None."""
    for rule in PATH_RULES:
        path_sub, ext_filter, new_domain, new_repos, rule_name = rule
        if path_sub not in path:
            continue
        if ext_filter is not None and ext not in ext_filter:
            continue
        return new_domain, list(new_repos), rule_name
    return None


def apply_filename_rules(filename: str) -> Optional[tuple[str, list[str], str]]:
    """Return (new_domain, new_repos, rule_name) or None."""
    fname_upper = filename.upper()
    for i, (prefixes, new_domain, new_repos) in enumerate(FILENAME_RULES):
        for prefix in prefixes:
            if fname_upper.startswith(prefix):
                return new_domain, list(new_repos), f"fname_{i}_{prefix.strip('-_ ').lower()}"
    return None


def apply_script_rules(ext: str, path: str) -> Optional[tuple[str, list[str], str]]:
    """Return (new_domain, new_repos, rule_name) or None for script file types."""
    for rule in SCRIPT_RULES:
        ext_set, path_hints, new_domain, new_repos, rule_name = rule
        if ext not in ext_set:
            continue
        if path_hints and not any(h.lower() in path.lower() for h in path_hints):
            continue
        return new_domain, list(new_repos), rule_name
    return None


def should_skip(path: str) -> bool:
    """Return True if this path should not be re-classified."""
    return any(frag in path for frag in SKIP_PATH_FRAGMENTS)


def remap(rec: dict, repo_domain_map: dict) -> Optional[tuple[str, list[str], str]]:
    """
    Determine new (domain, repos, rule_name) for a record, or None if no change needed.

    Rules applied in order:
      1. If path matches a skip fragment → no change
      2. Path rules (most specific)
      3. Filename prefix rules
      4. Script extension rules
      5. Workspace-spec fill-in
      6. Well-classified domain → fill repos from repo_domain_map if empty
    """
    path = rec.get("path", "")
    ext = rec.get("ext", "").lower()
    domain = rec.get("domain", "other")
    current_repos = rec.get("target_repos") or []
    filename = path.split("/")[-1]

    # Skip fragmented paths
    if should_skip(path):
        return None

    # Workspace-spec fill — domain already set, just need repos
    if domain == "workspace-spec" and not current_repos:
        return "workspace-spec", ["workspace-hub"], "workspace_spec_fill"

    # Only process domain=other records OR records missing repos
    needs_domain = (domain == "other")
    needs_repos = not current_repos

    if not needs_domain and not needs_repos:
        return None

    # --- Tier 1: path rules ---
    result = apply_path_rules(path, ext)
    if result:
        new_domain, new_repos, rule_name = result
        # For skip-intent rules (domain=other, repos=[]) — clear only if domain was other
        if new_domain == "other" and not new_repos:
            return None  # leave as-is
        if new_domain != domain or new_repos != current_repos:
            return new_domain, new_repos, rule_name
        return None

    # --- Tier 2: filename prefix rules ---
    if needs_domain:
        result = apply_filename_rules(filename)
        if result:
            new_domain, new_repos, rule_name = result
            return new_domain, new_repos, rule_name

    # --- Tier 3: script extension rules ---
    if ext in {"m", "inp", "dat", "bas", "mac"} and (needs_domain or needs_repos):
        result = apply_script_rules(ext, path)
        if result:
            new_domain, new_repos, rule_name = result
            if new_domain != domain or new_repos != current_repos:
                return new_domain, new_repos, rule_name

    # --- Tier 4: well-classified domain missing repos ---
    if not needs_domain and needs_repos and domain in WELL_CLASSIFIED_DOMAINS:
        repos = [
            repo for repo, domains in repo_domain_map.items()
            if domain in domains
        ]
        if repos:
            return domain, repos, "fill_repos_from_domain_map"

    return None


# ---------------------------------------------------------------------------
# Registry update
# ---------------------------------------------------------------------------

def update_registry(registry_path: Path, domain_counts: Counter) -> None:
    """Rewrite registry.yaml domain counts from fresh domain_counts."""
    if not registry_path.exists():
        logger.warning("registry.yaml not found, skipping registry update")
        return
    with open(registry_path) as f:
        reg = yaml.safe_load(f) or {}
    reg["by_domain"] = {k: v for k, v in sorted(domain_counts.items(), key=lambda x: -x[1])}
    reg["total_docs"] = sum(domain_counts.values())
    from datetime import datetime, timezone
    reg["generated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    with open(registry_path, "w") as f:
        yaml.dump(reg, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    logger.info("Updated registry.yaml (%d domains)", len(domain_counts))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_config(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase E2: targeted remap of domain=other and empty target_repos"
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--dry-run", action="store_true", help="Report changes, no writes")
    parser.add_argument("--limit", type=int, default=0, help="Process only N records (dev/test)")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    cfg = load_config(Path(args.config))
    index_path = HUB_ROOT / cfg["output"]["index_path"]
    registry_path = HUB_ROOT / cfg["output"]["registry_path"]
    repo_domain_map: dict = cfg.get("repo_domain_map", {})

    if not index_path.exists():
        logger.error("Index not found: %s", index_path)
        return 1

    logger.info("Phase E2 remap — %s (dry_run=%s)", index_path, args.dry_run)

    rule_counts: Counter = Counter()
    domain_counts: Counter = Counter()
    changed = 0
    skipped = 0
    total = 0

    if args.dry_run:
        with open(index_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                total += 1
                if args.limit and total > args.limit:
                    break

                result = remap(rec, repo_domain_map)
                if result:
                    new_domain, new_repos, rule_name = result
                    rule_counts[rule_name] += 1
                    domain_counts[new_domain] += 1
                    changed += 1
                    if args.debug:
                        logger.debug(
                            "  [%s] %s → domain=%s repos=%s",
                            rule_name, rec.get("path", "")[-60:], new_domain, new_repos,
                        )
                else:
                    domain_counts[rec.get("domain", "other")] += 1
                    skipped += 1

                if total % 200_000 == 0:
                    logger.info("  ... %d records scanned, %d would change", total, changed)

        logger.info("DRY-RUN summary: %d total, %d would change, %d unchanged",
                    total, changed, skipped)
        logger.info("Changes by rule:")
        for rule, count in rule_counts.most_common():
            logger.info("  %-45s %6d", rule, count)
        return 0

    # --- Live run ---
    backup_path = index_path.with_suffix(".jsonl.bak")
    shutil.copy2(index_path, backup_path)
    logger.info("Backup written to %s", backup_path)

    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=index_path.parent, prefix=".e2remap-", suffix=".jsonl"
    )
    try:
        with os.fdopen(tmp_fd, "w") as out_f, open(index_path) as in_f:
            for line in in_f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                total += 1
                if args.limit and total > args.limit:
                    out_f.write(line + "\n")
                    continue

                result = remap(rec, repo_domain_map)
                if result:
                    new_domain, new_repos, rule_name = result
                    rec["domain"] = new_domain
                    rec["target_repos"] = new_repos
                    rec["remapped_by"] = "phase-e2"
                    rule_counts[rule_name] += 1
                    domain_counts[new_domain] += 1
                    changed += 1
                else:
                    domain_counts[rec.get("domain", "other")] += 1

                out_f.write(json.dumps(rec) + "\n")

                if total % 200_000 == 0:
                    logger.info("  ... %d records, %d changed", total, changed)

        # Atomic replace
        os.replace(tmp_path, index_path)
        logger.info("index.jsonl updated (%d records, %d changed)", total, changed)

    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

    update_registry(registry_path, domain_counts)

    logger.info("Changes by rule:")
    for rule, count in rule_counts.most_common():
        logger.info("  %-45s %6d", rule, count)
    logger.info("Domain distribution after remap:")
    for domain, count in domain_counts.most_common():
        logger.info("  %-30s %8d", domain, count)
    logger.info("Done: %d total, %d changed, %d unchanged", total, changed, total - changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
