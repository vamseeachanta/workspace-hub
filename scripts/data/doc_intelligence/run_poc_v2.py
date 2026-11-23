"""Orchestrate POC v2 pipeline: pattern detection → code generation.

Reads v1 formulas.yaml per workbook, runs pattern detection,
generates Python modules + tests + calc reports.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml

# Ensure sibling imports work
sys.path.insert(0, os.path.dirname(__file__))
from pattern_detector import (
    compute_compression_stats,
    detect_row_patterns,
)
from module_assembler import assemble_module
from test_generator_v2 import generate_test_module
from calc_report_from_patterns import generate_calc_report_yaml

try:
    from formula_chain_builder import build_dependency_graph, classify_cells
    HAS_NX = True
except ImportError:
    HAS_NX = False

REPO_ROOT = Path(__file__).resolve().parents[3]
POC_LIST = REPO_ROOT / "knowledge/dark-intelligence/xlsx-poc/poc-file-list.yaml"
V1_DIR = REPO_ROOT / "knowledge/dark-intelligence/xlsx-poc"
V2_DIR = REPO_ROOT / "knowledge/dark-intelligence/xlsx-poc-v2"


MAX_FORMULAS_MB = 50  # Skip YAML files larger than this


def _load_formulas(path: str) -> dict:
    """Load a formulas.yaml file. Skip if too large."""
    size_mb = os.path.getsize(path) / (1024 * 1024)
    if size_mb > MAX_FORMULAS_MB:
        print(f"  WARNING: formulas.yaml is {size_mb:.0f}MB "
              f"(>{MAX_FORMULAS_MB}MB) — loading first 50K formulas")
        return _load_formulas_partial(path, max_formulas=50000)
    with open(path) as f:
        return yaml.safe_load(f) or {"formulas": []}


def _load_formulas_partial(path: str, max_formulas: int) -> dict:
    """Load first N formulas from a large YAML file via line scanning."""
    formulas = []
    current = {}
    in_formulas = False
    count = 0

    with open(path) as f:
        for line in f:
            if line.startswith("formulas:"):
                in_formulas = True
                continue
            if in_formulas and line.startswith("- cell_ref:"):
                if current:
                    formulas.append(current)
                    count += 1
                    if count >= max_formulas:
                        break
                current = {"cell_ref": line.split(": ", 1)[1].strip()}
                continue
            if in_formulas and current and ": " in line:
                key = line.strip().split(": ", 1)[0].lstrip("- ")
                val = line.strip().split(": ", 1)[1] if ": " in line.strip() else ""
                if key == "references":
                    current["references"] = []
                elif key.startswith("- ") or line.strip().startswith("- "):
                    ref_val = line.strip().lstrip("- ").strip()
                    if "references" in current and isinstance(
                        current["references"], list
                    ):
                        current["references"].append(ref_val)
                else:
                    # Try numeric conversion
                    try:
                        current[key] = float(val)
                    except (ValueError, TypeError):
                        current[key] = val.strip("'\"")
            if not in_formulas and line.strip() and not line.startswith(" "):
                if line.startswith("named_ranges:"):
                    in_formulas = False

    if current and count < max_formulas:
        formulas.append(current)

    return {"formulas": formulas, "named_ranges": [],
            "partial_load": True, "loaded_count": len(formulas)}


def _classify_from_formulas(formulas: list[dict]) -> dict:
    """Build classification from formula list."""
    if HAS_NX and formulas:
        try:
            g = build_dependency_graph(formulas)
            return classify_cells(g)
        except Exception:
            pass
    # Fallback: all refs without formulas are inputs
    formula_refs = {f["cell_ref"] for f in formulas}
    all_refs = set()
    for f in formulas:
        for r in f.get("references", []):
            all_refs.add(r.replace("$", ""))
    inputs = sorted(all_refs - formula_refs)
    outputs = sorted(
        formula_refs
        - {r.replace("$", "") for f in formulas for r in f.get("references", [])}
    )
    return {"inputs": inputs, "outputs": outputs, "chain": []}


def process_single_file(
    formulas_path: str,
    output_dir: str,
    stem: str,
    domain: str,
) -> dict:
    """Process one formulas.yaml through the v2 pipeline.

    Writes to output_dir:
      - patterns.yaml
      - calculations.py
      - test_calculations.py
      - calc-report.yaml

    Returns result dict with status and metrics.
    """
    os.makedirs(output_dir, exist_ok=True)

    data = _load_formulas(formulas_path)
    formulas = data.get("formulas", [])

    # Step 1: Detect patterns
    patterns = detect_row_patterns(formulas)
    stats = compute_compression_stats(patterns)

    # Step 2: Classify cells
    classification = _classify_from_formulas(formulas)

    # Step 3: Write patterns.yaml
    patterns_out = {
        "stem": stem,
        "domain": domain,
        "compression_stats": stats,
        "patterns": {
            k: {"canonical": k, "cell_count": len(v),
                 "cells": [c["cell_ref"] for c in v]}
            for k, v in patterns.items()
        },
    }
    with open(os.path.join(output_dir, "patterns.yaml"), "w") as f:
        yaml.dump(patterns_out, f, default_flow_style=False)

    # Step 4: Assemble Python module
    code = assemble_module(
        stem=stem,
        patterns=patterns,
        classification=classification,
        named_ranges=data.get("named_ranges", []),
        domain=domain,
    )
    with open(os.path.join(output_dir, "calculations.py"), "w") as f:
        f.write(code)

    # Step 5: Generate tests
    test_code = generate_test_module(
        stem=stem,
        patterns=patterns,
        classification=classification,
        formulas=data,
    )
    with open(os.path.join(output_dir, "test_calculations.py"), "w") as f:
        f.write(test_code)

    # Step 6: Generate calc report
    report = generate_calc_report_yaml(
        stem=stem,
        patterns=patterns,
        classification=classification,
        formulas=data,
        domain=domain,
        stats=stats,
    )
    with open(os.path.join(output_dir, "calc-report.yaml"), "w") as f:
        yaml.dump(report, f, default_flow_style=False)

    # Count loops (patterns with 6+ cells)
    n_loops = sum(1 for cells in patterns.values() if len(cells) >= 6)

    return {
        "stem": stem,
        "status": "success",
        "total_cells": stats["total_cells"],
        "unique_patterns": stats["unique_patterns"],
        "compression_ratio": stats["compression_ratio"],
        "functions": len(patterns),
        "loops": n_loops,
    }


def generate_compression_report(results: list[dict]) -> dict:
    """Generate cross-file compression summary."""
    success = [r for r in results if r["status"] == "success"]
    return {
        "total_files": len(success),
        "total_cells": sum(r["total_cells"] for r in success),
        "total_unique_patterns": sum(
            r["unique_patterns"] for r in success
        ),
        "total_functions": sum(r["functions"] for r in success),
        "total_loops": sum(r["loops"] for r in success),
        "per_file": results,
    }


def main():
    """Run the full v2 pipeline across all processable files."""
    if not POC_LIST.exists():
        print(f"POC file list not found: {POC_LIST}")
        return

    with open(POC_LIST) as f:
        poc = yaml.safe_load(f)

    results = []
    for entry in poc.get("selected_files", []):
        filename = entry["filename"]
        stem = _sanitize_stem(filename)
        domain = entry.get("domain", "unknown")

        # Check if v1 output exists
        v1_dir = V1_DIR / stem
        formulas_path = v1_dir / "formulas.yaml"
        if not formulas_path.exists():
            print(f"SKIP: {stem} — no v1 formulas.yaml")
            results.append({"stem": stem, "status": "skipped"})
            continue

        print(f"Processing: {stem}")
        out_dir = V2_DIR / stem
        try:
            result = process_single_file(
                formulas_path=str(formulas_path),
                output_dir=str(out_dir),
                stem=stem,
                domain=domain,
            )
            print(
                f"  → {result['unique_patterns']} patterns, "
                f"{result['functions']} functions, "
                f"{result['loops']} loops, "
                f"{result['compression_ratio']}x compression"
            )
            results.append(result)
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"stem": stem, "status": "error", "error": str(e)})

    # Write compression report
    report = generate_compression_report(results)
    os.makedirs(V2_DIR, exist_ok=True)
    with open(V2_DIR / "compression-report.yaml", "w") as f:
        yaml.dump(report, f, default_flow_style=False)

    print(f"\nCompression report: {V2_DIR / 'compression-report.yaml'}")
    print(f"Total: {report['total_files']} files, "
          f"{report['total_unique_patterns']} patterns, "
          f"{report['total_functions']} functions, "
          f"{report['total_loops']} loops")


def _sanitize_stem(filename: str) -> str:
    """Create safe directory name matching v1 run_poc_extraction.py."""
    stem = Path(filename).stem
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in stem)
    return safe[:60].strip("-").lower()


if __name__ == "__main__":
    main()
