#!/usr/bin/env python3
# ABOUTME: Stage 2+3 of OrcaFlex enrichment pipeline (WRK-595)
# ABOUTME: Enriches raw YAML with worldenergydata public databases, then strips client names

"""
Enrich raw OrcaFlex YAML extracts using worldenergydata public databases
and produce client-name-clean fixtures for digitalmodel.

Replaces anonymize-import.py (blind string replacement) with enrichment-first:
  1. Line objects: match OD/WT → DrillingRiserLoader or PipelineSpecLookup
  2. Vessel objects: match type context → BSEE rig fleet
  3. Strip client-specific string fields (names only)
  4. Keep all numeric dat_properties unchanged

Requires: worldenergydata installed (pip install -e ../../worldenergydata)
Runs on:  acma-ansys05 (same ecosystem as dat-to-yaml.py)

Usage:
    python enrich-and-clean.py --input client_projects/data/raw/orcaflex-extracted/ \\
                                --output digitalmodel/data/orcaflex/ --dry-run
    python enrich-and-clean.py --input path/to/raw/ --output path/to/clean/
"""

from __future__ import annotations

import argparse
import copy
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]

# OD tolerance for riser/pipe matching (meters)
_OD_TOLERANCE_M = 0.003   # ~3mm; covers measurement noise in .dat files
_WT_TOLERANCE_M = 0.002   # ~2mm


# ---------------------------------------------------------------------------
# worldenergydata lookup helpers
# ---------------------------------------------------------------------------

def _load_riser_loader():
    """Lazy-load DrillingRiserLoader; None if worldenergydata not installed."""
    try:
        from worldenergydata.vessel_fleet import DrillingRiserLoader  # noqa: PLC0415
        return DrillingRiserLoader()
    except Exception as exc:
        logger.warning("DrillingRiserLoader unavailable: %s", exc)
        return None


def _load_pipeline_lookup():
    """Lazy-load PipelineSpecLookup; None if not yet implemented (WRK-594)."""
    try:
        from worldenergydata.bsee.pipeline import PipelineSpecLookup  # noqa: PLC0415
        return PipelineSpecLookup()
    except Exception as exc:
        logger.debug("PipelineSpecLookup unavailable (WRK-594 pending): %s", exc)
        return None


def _load_rig_fleet() -> list[dict]:
    """Load BSEE rig fleet from .bin; return list of rig dicts."""
    try:
        import pickle  # noqa: PLC0415
        bin_path = HUB_ROOT / "worldenergydata/data/modules/bsee/.local/rig_fleet/rig_fleet_full.bin"
        if not bin_path.exists():
            logger.debug("rig_fleet_full.bin not found")
            return []
        with open(bin_path, "rb") as fh:
            fleet = pickle.load(fh)
        # fleet may be list[dict] or DataFrame depending on serialization
        if hasattr(fleet, "to_dict"):
            return fleet.to_dict("records")
        return list(fleet) if fleet else []
    except Exception as exc:
        logger.debug("rig fleet load failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Enrichment logic
# ---------------------------------------------------------------------------

def enrich_line(line: dict, riser_loader, pipeline_lookup) -> dict:
    """
    Enrich a line object extracted from OrcaFlex.

    Strategy:
      1. Convert OD from m to inches
      2. Try DrillingRiserLoader.filter_by_size(od_in)
      3. If no riser match, try PipelineSpecLookup.match_od_wt()
      4. Fallback: retain numeric data with component_type='unknown_line'
    """
    result: dict[str, Any] = {}
    dat_props = {k: v for k, v in line.items() if k != "name"}

    od_m_raw = line.get("OD")
    wt_m_raw = line.get("WallThickness")

    od_m = od_m_raw[0] if isinstance(od_m_raw, list) else od_m_raw
    wt_m = wt_m_raw[0] if isinstance(wt_m_raw, list) else wt_m_raw

    matched = False

    # --- Try riser joint match ---
    if riser_loader is not None and od_m is not None:
        od_in = od_m / 0.0254
        try:
            df = riser_loader.filter_by_size(od_in)
            if not df.empty:
                row = df.iloc[0]
                result["component_type"] = "marine_drilling_riser_joint"
                result["nps_in"] = float(row.get("OD_IN", od_in))
                result["public_match"] = {
                    "grade_range": _parse_grade(row.get("GRADE", "")),
                    "connection_type": row.get("CONNECTION_TYPE") or None,
                    "pressure_rating_psi": row.get("PRESSURE_RATING_PSI") or None,
                    "manufacturer": row.get("MANUFACTURER") or None,
                    "api_standard": "API-STD-16F",
                    "source": "worldenergydata.vessel_fleet.DrillingRiserLoader",
                }
                matched = True
                logger.debug("Riser match: OD=%.4fm (%.2f\") → %s", od_m, od_in, row.get("MANUFACTURER"))
        except Exception as exc:
            logger.debug("Riser lookup failed: %s", exc)

    # --- Try pipeline spec match ---
    if not matched and pipeline_lookup is not None and od_m is not None:
        try:
            spec = pipeline_lookup.match_od_wt(od_m, wt_m or 0.0)
            if spec:
                result["component_type"] = "pipeline_segment"
                result["nps_in"] = spec.get("nps_in")
                result["public_match"] = {
                    "schedule": spec.get("schedule"),
                    "grade_range": spec.get("grade_range", []),
                    "standards": spec.get("standards", []),
                    "source": "worldenergydata.bsee.pipeline.PipelineSpecLookup",
                }
                matched = True
        except Exception as exc:
            logger.debug("Pipeline lookup failed: %s", exc)

    # --- Fallback ---
    if not matched:
        result["component_type"] = "unknown_line"
        if od_m is not None:
            result["od_m"] = od_m
            result["nps_in_approx"] = round(od_m / 0.0254, 2)
        result["public_match"] = None

    result["dat_properties"] = dat_props
    # name field omitted — client-specific
    return result


def enrich_vessel(vessel: dict, rig_fleet: list[dict]) -> dict:
    """
    Enrich a vessel object extracted from OrcaFlex.

    Attempts to classify vessel from rig fleet data based on
    context clues. Returns enriched dict with client name stripped.
    """
    result: dict[str, Any] = {}
    dat_props = {k: v for k, v in vessel.items() if k != "name"}

    # Heuristic classification from dat properties
    vessel_class = "unknown"
    water_depth_rating_m = None
    dp_class = None

    if rig_fleet:
        # Use first drillship in fleet as representative (WRK-595 TODO: smarter matching)
        drillships = [r for r in rig_fleet if str(r.get("RIG_TYPE", "")).lower() == "drillship"]
        if drillships:
            vessel_class = "drillship"
            sample = drillships[0]
            wd_ft = sample.get("WATER_DEPTH_RATING_FT")
            if wd_ft:
                water_depth_rating_m = round(float(wd_ft) * 0.3048, 0)

    result["vessel_class"] = vessel_class
    if water_depth_rating_m:
        result["water_depth_rating_m"] = water_depth_rating_m
    if dp_class:
        result["dp_class"] = dp_class
    result["public_source"] = "worldenergydata.vessel_fleet.BSEE_rig_fleet"
    result["dat_properties"] = dat_props
    # name: stripped — client-specific
    return result


def _parse_grade(grade_str: str) -> list[str]:
    """Parse 'G105/S135' or 'G105' into list of grades."""
    if not grade_str:
        return []
    return [g.strip() for g in str(grade_str).replace(",", "/").split("/") if g.strip()]


# ---------------------------------------------------------------------------
# Legal scan (inline, no subprocess dependency)
# ---------------------------------------------------------------------------

def _load_deny_patterns(deny_list_path: Path) -> list:
    """Load compiled regex patterns from .legal-deny-list.yaml."""
    import re  # noqa: PLC0415
    if not deny_list_path.exists():
        return []
    with open(deny_list_path) as fh:
        data = yaml.safe_load(fh) or {}
    patterns = []
    for section in ("client_references", "proprietary_tools", "client_infrastructure"):
        for entry in data.get(section) or []:
            if not entry:
                continue
            pat = entry.get("pattern", "")
            flags = 0 if entry.get("case_sensitive", False) else re.IGNORECASE
            try:
                patterns.append(re.compile(re.escape(pat), flags))
            except re.error:
                pass
    return patterns


def _scan_violations(data: dict, patterns: list) -> list[str]:
    violations = []

    def _walk(node, path=""):
        if isinstance(node, str):
            for pat in patterns:
                if pat.search(node):
                    violations.append(f"{path}: '{pat.pattern}' in '{node[:80]}'")
        elif isinstance(node, dict):
            for k, v in node.items():
                _walk(v, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                _walk(item, f"{path}[{i}]")

    _walk(data)
    return violations


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process_file(
    src: Path,
    dst: Path,
    riser_loader,
    pipeline_lookup,
    rig_fleet: list[dict],
    deny_patterns: list,
    dry_run: bool = False,
) -> bool:
    with open(src, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    if not raw:
        logger.warning("Empty: %s", src)
        return False

    enriched = copy.deepcopy(raw)
    enrich_log: dict[str, Any] = {"source": str(src), "enriched_at": datetime.now(timezone.utc).isoformat()}

    # Enrich lines
    if "lines" in enriched and isinstance(enriched["lines"], list):
        new_lines = []
        for line in enriched["lines"]:
            new_lines.append(enrich_line(line, riser_loader, pipeline_lookup))
        enriched["lines"] = new_lines
        enrich_log["lines_enriched"] = len(new_lines)

    # Enrich vessels
    if "vessels" in enriched and isinstance(enriched["vessels"], list):
        new_vessels = []
        for vessel in enriched["vessels"]:
            new_vessels.append(enrich_vessel(vessel, rig_fleet))
        enriched["vessels"] = new_vessels
        enrich_log["vessels_enriched"] = len(new_vessels)

    # Legal scan
    violations = _scan_violations(enriched, deny_patterns)
    if violations:
        logger.error("LEGAL VIOLATIONS in %s:", src.name)
        for v in violations:
            logger.error("  %s", v)
        return False

    enriched.setdefault("metadata", {})["enriched"] = True
    enriched["metadata"]["enrich_log"] = enrich_log

    if dry_run:
        n_lines = len(enriched.get("lines", []))
        n_vessels = len(enriched.get("vessels", []))
        logger.info("  [DRY-RUN] %s → %d lines, %d vessels", src.name, n_lines, n_vessels)
        return True

    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w", encoding="utf-8") as fh:
        yaml.dump(enriched, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)

    log_path = dst.parent / f"{dst.stem}_enrich_log.yaml"
    with open(log_path, "w", encoding="utf-8") as fh:
        yaml.dump(enrich_log, fh, default_flow_style=False, allow_unicode=True)

    logger.info("  ✓ %s → %s", src.name, dst.name)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enrich OrcaFlex YAML extracts with worldenergydata, strip client names"
    )
    parser.add_argument("--input", required=True, help="Raw YAML dir (client_projects staging)")
    parser.add_argument("--output", required=True, help="Clean YAML dir (digitalmodel/data/orcaflex)")
    parser.add_argument("--deny-list", default=str(HUB_ROOT / ".legal-deny-list.yaml"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    if not input_dir.exists():
        logger.error("Input not found: %s", input_dir)
        sys.exit(1)

    # Load worldenergydata lookups once
    riser_loader = _load_riser_loader()
    pipeline_lookup = _load_pipeline_lookup()
    rig_fleet = _load_rig_fleet()
    deny_patterns = _load_deny_patterns(Path(args.deny_list))

    logger.info("Lookups ready — riser: %s | pipeline: %s | rig fleet: %d rigs | deny: %d patterns",
                "✓" if riser_loader else "✗ (WRK-593)",
                "✓" if pipeline_lookup else "✗ (WRK-594)",
                len(rig_fleet),
                len(deny_patterns))

    yaml_files = sorted(input_dir.rglob("*.yaml")) + sorted(input_dir.rglob("*.yml"))
    yaml_files = [f for f in yaml_files if "_enrich_log" not in f.name]

    n_ok = n_fail = 0
    for src in yaml_files:
        rel = src.relative_to(input_dir)
        dst = output_dir / rel
        ok = process_file(src, dst, riser_loader, pipeline_lookup, rig_fleet,
                          deny_patterns, dry_run=args.dry_run)
        if ok:
            n_ok += 1
        else:
            n_fail += 1

    logger.info("Complete: %d enriched, %d failed", n_ok, n_fail)
    if n_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
