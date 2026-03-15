# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Validate extraction manifests by computing a confidence score.

Filters manifests by extraction quality heuristics. Assigns a 0.0–1.0
confidence score and a pass/fail verdict based on a configurable threshold.
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Scoring weights
# ---------------------------------------------------------------------------
_WEIGHT_HAS_SECTIONS = 0.30
_WEIGHT_HAS_TABLES = 0.20
_WEIGHT_NO_ERRORS = 0.20
_WEIGHT_AVG_TEXT_LENGTH = 0.15
_WEIGHT_HAS_FIGURE_REFS = 0.15

_AVG_TEXT_LENGTH_THRESHOLD = 100  # characters
_DEFAULT_PASS_THRESHOLD = 0.5


def compute_confidence(manifest_dict: dict[str, Any]) -> dict[str, Any]:
    """Compute a 0.0–1.0 confidence score for a single manifest.

    Args:
        manifest_dict: Parsed manifest as a Python dict.

    Returns:
        Dict with keys: ``score`` (float), ``factors`` (dict[str, float]),
        ``verdict`` ("pass" | "fail").
    """
    sections = manifest_dict.get("sections") or []
    tables = manifest_dict.get("tables") or []
    figure_refs = manifest_dict.get("figure_refs") or []
    errors = manifest_dict.get("errors") or []

    # --- individual factor scores ---
    has_sections = _WEIGHT_HAS_SECTIONS if _has_nonempty_section(sections) else 0.0
    has_tables = _WEIGHT_HAS_TABLES if len(tables) >= 1 else 0.0
    no_errors = _WEIGHT_NO_ERRORS if len(errors) == 0 else 0.0
    avg_text_length = (
        _WEIGHT_AVG_TEXT_LENGTH
        if _avg_section_text_length(sections) > _AVG_TEXT_LENGTH_THRESHOLD
        else 0.0
    )
    has_figure_refs = _WEIGHT_HAS_FIGURE_REFS if len(figure_refs) >= 1 else 0.0

    factors = {
        "has_sections": has_sections,
        "has_tables": has_tables,
        "no_errors": no_errors,
        "avg_text_length": avg_text_length,
        "has_figure_refs": has_figure_refs,
    }

    score = round(sum(factors.values()), 10)
    # clamp to [0.0, 1.0] to avoid float artefacts
    score = max(0.0, min(1.0, score))

    verdict = "pass" if score >= _DEFAULT_PASS_THRESHOLD else "fail"
    return {"score": score, "factors": factors, "verdict": verdict}


def validate_manifest(
    manifest_dict: dict[str, Any], min_score: float = _DEFAULT_PASS_THRESHOLD
) -> dict[str, Any]:
    """Run confidence check on a single manifest dict.

    Args:
        manifest_dict: Parsed manifest.
        min_score: Minimum score to receive a "pass" verdict.

    Returns:
        Dict with keys: ``filename``, ``score``, ``verdict``, ``factors``.
    """
    result = compute_confidence(manifest_dict)
    verdict = "pass" if result["score"] >= min_score else "fail"
    filename = (manifest_dict.get("metadata") or {}).get("filename", "")
    return {
        "filename": filename,
        "score": result["score"],
        "verdict": verdict,
        "factors": result["factors"],
    }


def validate_directory(
    directory: str, min_score: float = _DEFAULT_PASS_THRESHOLD
) -> dict[str, Any]:
    """Scan ``*.manifest.yaml`` files in *directory* and validate each.

    Args:
        directory: Path to directory containing manifest YAML files.
        min_score: Pass threshold forwarded to :func:`validate_manifest`.

    Returns:
        Dict with keys: ``total``, ``passed``, ``failed``, ``results`` (list).
    """
    pattern = os.path.join(directory, "*.manifest.yaml")
    manifest_files = sorted(glob.glob(pattern))

    results: list[dict[str, Any]] = []
    for path in manifest_files:
        with open(path, encoding="utf-8") as fh:
            manifest_dict = yaml.safe_load(fh) or {}
        entry = validate_manifest(manifest_dict, min_score=min_score)
        results.append(entry)

    passed = sum(1 for r in results if r["verdict"] == "pass")
    failed = len(results) - passed
    return {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "results": results,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    """Entry-point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Validate manifest extraction confidence."
    )
    parser.add_argument(
        "--input", required=True, metavar="FILE_OR_DIR",
        help="Path to a single *.manifest.yaml file or a directory of manifests.",
    )
    parser.add_argument(
        "--min-score", type=float, default=_DEFAULT_PASS_THRESHOLD, metavar="FLOAT",
        help="Minimum confidence score to pass (default: 0.5).",
    )
    parser.add_argument(
        "--output", metavar="FILE.yaml",
        help="Write YAML report to this file instead of stdout.",
    )
    parser.add_argument(
        "--failed-only", action="store_true",
        help="Include only failed manifests in the report.",
    )
    args = parser.parse_args(argv)

    if os.path.isdir(args.input):
        report = validate_directory(args.input, min_score=args.min_score)
    else:
        with open(args.input, encoding="utf-8") as fh:
            manifest_dict = yaml.safe_load(fh) or {}
        entry = validate_manifest(manifest_dict, min_score=args.min_score)
        report = {
            "total": 1,
            "passed": 1 if entry["verdict"] == "pass" else 0,
            "failed": 0 if entry["verdict"] == "pass" else 1,
            "results": [entry],
        }

    if args.failed_only:
        report["results"] = [r for r in report["results"] if r["verdict"] == "fail"]

    output_yaml = yaml.dump(report, sort_keys=False, allow_unicode=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output_yaml)
        print(f"Report written to {args.output}")
    else:
        sys.stdout.write(output_yaml)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _has_nonempty_section(sections: list[dict[str, Any]]) -> bool:
    """Return True if any section has non-empty text."""
    for section in sections:
        text = section.get("text") or ""
        if text.strip():
            return True
    return False


def _avg_section_text_length(sections: list[dict[str, Any]]) -> float:
    """Return average character length of section text fields."""
    if not sections:
        return 0.0
    lengths = [len(section.get("text") or "") for section in sections]
    return sum(lengths) / len(lengths)


if __name__ == "__main__":
    main()
