#!/usr/bin/env python3
# ABOUTME: Stage 2+3 of OrcaFlex dat-to-yaml pipeline (WRK-589)
# ABOUTME: Runs on ace-linux-1; anonymizes string fields, legal-scans, imports to digitalmodel

"""
Anonymize raw OrcaFlex YAML extracts and import clean versions to digitalmodel.

Stage 2: Pull from client_projects/data/raw/orcaflex-extracted/
          → replace all non-numeric string values with generic labels
          → run legal scan to verify no client identifiers remain
Stage 3: Write clean YAMLs to digitalmodel/data/orcaflex/

Usage:
    python3 anonymize-import.py --input client_projects/data/raw/orcaflex-extracted/ \\
                                 --output digitalmodel/data/orcaflex/ \\
                                 --deny-list .legal-deny-list.yaml \\
                                 --dry-run

    python3 anonymize-import.py --input client_projects/data/raw/orcaflex-extracted/ \\
                                 --output digitalmodel/data/orcaflex/
"""

import argparse
import copy
import logging
import re
import sys
from pathlib import Path

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_DENY_LIST = HUB_ROOT / ".legal-deny-list.yaml"

# Fields whose string values are anonymized (object names, vessel names, type names).
# Numeric fields are kept as-is.
ANONYMIZE_KEYS = {"name", "LineType", "EndAConnection", "EndBConnection", "VesselType"}

# Counters for generic label generation
_label_counters: dict[str, int] = {}


def _generic_label(prefix: str) -> str:
    _label_counters[prefix] = _label_counters.get(prefix, 0) + 1
    return f"{prefix}{_label_counters[prefix]}"


def _reset_counters() -> None:
    _label_counters.clear()


def load_deny_patterns(deny_list_path: Path) -> list[re.Pattern]:
    """Load deny list patterns as compiled regexes."""
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


def scan_for_violations(data: dict, patterns: list[re.Pattern]) -> list[str]:
    """Walk YAML structure, return list of violation descriptions."""
    violations = []

    def _walk(node, path=""):
        if isinstance(node, str):
            for pat in patterns:
                if pat.search(node):
                    violations.append(f"{path}: matched '{pat.pattern}' in '{node[:80]}'")
        elif isinstance(node, dict):
            for k, v in node.items():
                _walk(v, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                _walk(item, f"{path}[{i}]")

    _walk(data)
    return violations


def anonymize(data: dict) -> tuple[dict, dict]:
    """
    Return (anonymized_copy, substitution_log).

    Replaces string values in ANONYMIZE_KEYS with generic labels.
    All numeric fields are preserved unchanged.
    """
    _reset_counters()
    subs: dict[str, str] = {}

    def _anon_node(node, parent_key=""):
        if isinstance(node, dict):
            result = {}
            for k, v in node.items():
                result[k] = _anon_node(v, parent_key=k)
            return result
        elif isinstance(node, list):
            return [_anon_node(item, parent_key=parent_key) for item in node]
        elif isinstance(node, str) and parent_key in ANONYMIZE_KEYS:
            if node not in subs:
                # Choose prefix from key name
                prefix_map = {
                    "name": "Obj",
                    "LineType": "LineType",
                    "EndAConnection": "Connection",
                    "EndBConnection": "Connection",
                    "VesselType": "VesselType",
                }
                prefix = prefix_map.get(parent_key, "Item")
                subs[node] = _generic_label(prefix)
            return subs[node]
        else:
            return node

    anon_data = _anon_node(copy.deepcopy(data))
    return anon_data, subs


def process_file(
    src: Path,
    dst: Path,
    patterns: list[re.Pattern],
    dry_run: bool = False,
) -> bool:
    """Anonymize src YAML and write to dst. Return True on success."""
    with open(src, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    if not raw:
        logger.warning("Empty/invalid YAML: %s", src)
        return False

    # Anonymize string fields
    clean, subs = anonymize(raw)

    # Legal scan on clean output
    violations = scan_for_violations(clean, patterns)
    if violations:
        logger.error("LEGAL VIOLATIONS after anonymize in %s:", src.name)
        for v in violations:
            logger.error("  %s", v)
        return False

    # Build log entry
    clean.setdefault("metadata", {})
    clean["metadata"]["anonymized"] = True
    clean["metadata"]["substitution_count"] = len(subs)

    log_path = dst.parent / f"{dst.stem}_anonymize_log.yaml"

    if dry_run:
        logger.info("  [DRY-RUN] %s → %s (%d subs)", src.name, dst, len(subs))
        if subs:
            for orig, label in list(subs.items())[:5]:
                logger.info("    '%s' → '%s'", orig[:60], label)
        return True

    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w", encoding="utf-8") as fh:
        yaml.dump(clean, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)

    with open(log_path, "w", encoding="utf-8") as fh:
        yaml.dump(
            {"source": str(src), "destination": str(dst), "substitutions": subs},
            fh,
            default_flow_style=False,
            allow_unicode=True,
        )

    logger.info("  ✓ %s → %s (%d subs)", src.name, dst.name, len(subs))
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Anonymize OrcaFlex YAML extracts and import to digitalmodel"
    )
    parser.add_argument("--input", required=True, help="Source dir (client_projects staging)")
    parser.add_argument("--output", required=True, help="Destination dir (digitalmodel/data/orcaflex)")
    parser.add_argument(
        "--deny-list",
        default=str(DEFAULT_DENY_LIST),
        help="Path to .legal-deny-list.yaml",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no writes")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    deny_path = Path(args.deny_list)

    if not input_dir.exists():
        logger.error("Input dir not found: %s", input_dir)
        sys.exit(1)

    patterns = load_deny_patterns(deny_path)
    logger.info("Loaded %d deny-list patterns from %s", len(patterns), deny_path)

    yaml_files = sorted(input_dir.rglob("*.yaml")) + sorted(input_dir.rglob("*.yml"))
    # Exclude anonymize logs from previous runs
    yaml_files = [f for f in yaml_files if "_anonymize_log" not in f.name]

    if not yaml_files:
        logger.warning("No YAML files found in %s", input_dir)
        sys.exit(0)

    logger.info("Processing %d files from %s", len(yaml_files), input_dir)
    n_ok = n_fail = 0

    for src in yaml_files:
        rel = src.relative_to(input_dir)
        dst = output_dir / rel
        ok = process_file(src, dst, patterns, dry_run=args.dry_run)
        if ok:
            n_ok += 1
        else:
            n_fail += 1

    logger.info("Complete: %d OK, %d failed", n_ok, n_fail)
    if n_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
