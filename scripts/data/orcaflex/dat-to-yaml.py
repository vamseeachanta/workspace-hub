#!/usr/bin/env python3
# ABOUTME: Stage 1 of OrcaFlex dat-to-yaml pipeline (WRK-589)
# ABOUTME: Runs on acma-ansys05 (Windows, OrcaFlex licensed); extracts model params to YAML

"""
Extract engineering parameters from OrcaFlex .dat files to YAML.

Requires OrcaFlex Python API (OrcFxAPI) installed on the machine.
Designed to run on acma-ansys05 (Windows) where OrcaFlex is licensed.

Usage:
    python dat-to-yaml.py --input "path/to/orcaflex/models" --output "path/to/staging"
    python dat-to-yaml.py --input "path/to/models" --output "path/to/out" --project my-project
    python dat-to-yaml.py --input "path/to/single.dat" --output "path/to/out"

Output:
    One YAML file per .dat file; structure mirrors input directory tree.
    Each YAML contains: general, environment, lines[], vessels[], metadata.
"""

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Properties to extract per object type.
# Use a list so we can try each name (OrcaFlex API property names vary by version).
LINE_PROPS = [
    "Length", "OD", "WallThickness", "MassPerUnitLength", "MassPerLength",
    "EIx", "EIy", "GJ", "EA", "E", "Poisson", "PoissonRatio",
    "CDt", "CDn", "CMt", "CMn", "AddedMassCoefficient",
    "LineType", "EndAConnection", "EndBConnection",
]
VESSEL_PROPS = [
    "InitialX", "InitialY", "InitialZ", "InitialHeel", "InitialTrim", "InitialHeading",
    "VesselType", "SurgeAmplitude", "SwayAmplitude", "HeaveAmplitude",
]
GENERAL_PROPS = [
    "StaticSimulationLength", "DynamicSimulationLength",
    "ImplicitConstantTimeStep", "ImplicitVariableMaxTimeStep",
    "StageDuration", "NumberOfStages", "LogSamplePeriod",
]
ENVIRONMENT_PROPS = [
    "WaterDepth", "SeaDensity", "WaveType", "WaveHs", "WaveTz", "WaveTp",
    "WaveDirection", "WaveGamma", "WaveSpectrumType",
    "CurrentSpeed", "CurrentDirection", "CurrentDepth",
    "Gravity", "KinematicViscosity",
]


def _try_get(obj, *prop_names):
    """Try property names in order; return first that succeeds, or None."""
    for name in prop_names:
        try:
            val = getattr(obj, name)
            if val is None:
                continue
            # Convert numpy/OrcaFlex array types to plain list
            if hasattr(val, "tolist"):
                val = val.tolist()
            elif hasattr(val, "__iter__") and not isinstance(val, str):
                try:
                    val = list(val)
                except Exception:
                    pass
            return val
        except Exception:
            continue
    return None


def _extract_obj(obj, prop_names):
    """Extract a dict of {prop: value} for a model object."""
    result = {}
    for name in prop_names:
        val = _try_get(obj, name)
        if val is not None:
            result[name] = val
    return result


def extract_model(dat_path: Path) -> dict:
    """Open a .dat file and extract key engineering parameters."""
    try:
        import OrcFxAPI as ofx  # noqa: PLC0415 — deferred; only on Windows
    except ImportError:
        logger.error("OrcFxAPI not installed. Run on acma-ansys05 with OrcaFlex.")
        sys.exit(1)

    logger.debug("Opening: %s", dat_path)
    try:
        model = ofx.Model(str(dat_path))
    except Exception as exc:
        logger.warning("Cannot open %s: %s", dat_path.name, exc)
        return {}

    # General
    try:
        general = _extract_obj(model.general, GENERAL_PROPS)
    except Exception as exc:
        logger.debug("general failed: %s", exc)
        general = {}

    # Environment
    try:
        env = _extract_obj(model.environment, ENVIRONMENT_PROPS)
    except Exception as exc:
        logger.debug("environment failed: %s", exc)
        env = {}

    # Lines
    lines = []
    try:
        for obj in model.objects:
            if obj.type == ofx.ObjectType.Line:
                d = {"name": obj.name}
                d.update(_extract_obj(obj, LINE_PROPS))
                lines.append(d)
    except Exception as exc:
        logger.debug("lines failed: %s", exc)

    # Vessels
    vessels = []
    try:
        for obj in model.objects:
            if obj.type == ofx.ObjectType.Vessel:
                d = {"name": obj.name}
                d.update(_extract_obj(obj, VESSEL_PROPS))
                vessels.append(d)
    except Exception as exc:
        logger.debug("vessels failed: %s", exc)

    # OrcaFlex version
    try:
        version = model.state  # noqa: F841
        version_str = str(ofx.__version__) if hasattr(ofx, "__version__") else "unknown"
    except Exception:
        version_str = "unknown"

    return {
        "metadata": {
            "source_file": dat_path.name,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "orcaflex_api_version": version_str,
            "object_counts": {
                "lines": len(lines),
                "vessels": len(vessels),
            },
        },
        "general": general,
        "environment": env,
        "lines": lines,
        "vessels": vessels,
    }


def process_directory(input_dir: Path, output_dir: Path, project: str = "") -> int:
    """Walk input_dir, extract each .dat, write YAML to output_dir."""
    dat_files = sorted(input_dir.rglob("*.dat"))
    if not dat_files:
        logger.warning("No .dat files found in %s", input_dir)
        return 0

    logger.info("Found %d .dat files in %s", len(dat_files), input_dir)
    n_ok = n_fail = 0

    for dat_path in dat_files:
        rel = dat_path.relative_to(input_dir)
        out_path = output_dir / rel.with_suffix(".yaml")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if out_path.exists():
            logger.debug("Skipping (already extracted): %s", rel)
            continue

        data = extract_model(dat_path)
        if not data:
            n_fail += 1
            continue

        if project:
            data["metadata"]["project"] = project

        with open(out_path, "w", encoding="utf-8") as fh:
            yaml.dump(data, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)

        logger.info("  ✓ %s → %s", rel, out_path.name)
        n_ok += 1

    logger.info("Done: %d extracted, %d failed", n_ok, n_fail)
    return n_ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract OrcaFlex .dat to YAML")
    parser.add_argument("--input", required=True, help="Input .dat file or directory")
    parser.add_argument("--output", required=True, help="Output directory for YAML files")
    parser.add_argument("--project", default="", help="Project label for metadata")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.is_file():
        output_dir.mkdir(parents=True, exist_ok=True)
        data = extract_model(input_path)
        if not data:
            logger.error("Extraction failed for %s", input_path)
            sys.exit(1)
        if args.project:
            data["metadata"]["project"] = args.project
        out = output_dir / input_path.with_suffix(".yaml").name
        with open(out, "w", encoding="utf-8") as fh:
            yaml.dump(data, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)
        logger.info("Written: %s", out)
    elif input_path.is_dir():
        process_directory(input_path, output_dir, project=args.project)
    else:
        logger.error("Input not found: %s", input_path)
        sys.exit(1)


if __name__ == "__main__":
    main()
