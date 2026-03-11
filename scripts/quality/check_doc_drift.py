#!/usr/bin/env python3
"""check_doc_drift.py — Documentation drift detector for workspace-hub (WRK-1093).

Detects symbols that exist in the symbol index but are not mentioned in docs,
and flags source files that have been modified without corresponding doc updates.

Usage:
    uv run --no-project python scripts/quality/check_doc_drift.py [OPTIONS]

Options:
    --repo <name>        Restrict to one repo (e.g. assethold)
    --update-baseline    Write current scores to config/quality/doc-drift-baseline.yaml
    --format json|text   Output format (default: text)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_SYMBOL_INDEX = Path("config/search/symbol-index.jsonl")
DEFAULT_BASELINE = Path("config/quality/doc-drift-baseline.yaml")

REPO_MAP: dict[str, str] = {
    "assetutilities": "assetutilities",
    "digitalmodel": "digitalmodel",
    "worldenergydata": "worldenergydata",
    "assethold": "assethold",
    "ogmanufacturing": "OGManufacturing",
}

# Cache: repo_path str -> set[str]
_modified_files_cache: dict[str, set[str]] = {}


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def load_symbol_index(path: Path) -> list[dict]:
    """Read JSONL symbol index; return [] with a warning if file is absent."""
    if not path.exists():
        print(f"WARNING: symbol index not found at {path}", file=sys.stderr)
        return []
    results: list[dict] = []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results


def build_doc_mention_set(repo_path: Path) -> set[str]:
    """Whole-word grep over docs/ + README.md; return set of mentioned symbol names."""
    mentions: set[str] = set()
    doc_files: list[Path] = []

    readme = repo_path / "README.md"
    if readme.exists():
        doc_files.append(readme)

    docs_dir = repo_path / "docs"
    if docs_dir.is_dir():
        doc_files.extend(docs_dir.rglob("*.md"))
        doc_files.extend(docs_dir.rglob("*.rst"))
        doc_files.extend(docs_dir.rglob("*.txt"))

    # Only count identifiers that look like Python names:
    # - At least 4 chars, or contain an underscore, or start with uppercase (class-like)
    # - Whole-word only (no substring matches)
    ident_pat = re.compile(r"(?<!\w)([A-Za-z_]\w*)(?!\w)")

    def _is_symbol_like(name: str) -> bool:
        return len(name) >= 4 or "_" in name or (name[0].isupper() and len(name) >= 2)

    for doc_file in doc_files:
        try:
            text = doc_file.read_text(errors="replace")
        except OSError:
            continue
        for match in ident_pat.finditer(text):
            name = match.group(1)
            if _is_symbol_like(name):
                mentions.add(name)

    return mentions


def compute_drift_score(
    symbols: list[dict], doc_mentions: set[str], repo: str
) -> float:
    """Return undocumented ratio: 0.0 = all documented, 1.0 = none documented."""
    repo_symbols = [s for s in symbols if s.get("repo") == repo]
    if not repo_symbols:
        return 0.0
    undocumented = sum(
        1 for s in repo_symbols if s.get("symbol") not in doc_mentions
    )
    return undocumented / len(repo_symbols)


def batch_git_modified_files(repo_path: Path) -> set[str]:
    """Return set of file paths modified in git history (single subprocess call, cached)."""
    key = str(repo_path.resolve())
    if key in _modified_files_cache:
        return _modified_files_cache[key]

    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--since=90.days",
                "--diff-filter=M",
                "--name-only",
                "--format=",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(
                f"WARNING: git log failed for {repo_path}: {result.stderr[:200]}",
                file=sys.stderr,
            )
            _modified_files_cache[key] = set()
            return set()
        files: set[str] = set()
        for line in result.stdout.splitlines():
            line = line.strip()
            if line:
                files.add(line)
        _modified_files_cache[key] = files
        return files
    except (subprocess.SubprocessError, OSError) as exc:
        print(f"WARNING: batch_git_modified_files error for {repo_path}: {exc}", file=sys.stderr)
        _modified_files_cache[key] = set()
        return set()


def detect_staleness(file_path: str, modified_files: set[str]) -> bool:
    """Return True if file_path appears in the recently-modified files set (last 90 days)."""
    return file_path in modified_files


def run_drift_check(
    repos: list[str],
    symbol_index_path: Path,
    repo_root: Path,
) -> dict:
    """Orchestrator: return {repo: {drift_score, stale_files, undocumented}}."""
    symbols = load_symbol_index(symbol_index_path)
    report: dict = {}

    for repo_name in repos:
        rel_path = REPO_MAP.get(repo_name, repo_name)
        repo_path = repo_root / rel_path

        if not repo_path.is_dir():
            continue

        doc_mentions = build_doc_mention_set(repo_path)
        drift_score = compute_drift_score(symbols, doc_mentions, repo=repo_name)

        modified = batch_git_modified_files(repo_path)
        stale_files = [
            f for f in modified
            if f.endswith(".py") and detect_staleness(f, modified_files=modified)
        ]

        repo_symbols = [s for s in symbols if s.get("repo") == repo_name]
        undocumented = [
            s.get("symbol", "")
            for s in repo_symbols
            if s.get("symbol") not in doc_mentions
        ]

        report[repo_name] = {
            "drift_score": round(drift_score, 4),
            "stale_files": stale_files[:20],
            "undocumented": undocumented[:50],
        }

    return report


def format_drift_candidates(report: dict, baseline: dict) -> list[str]:
    """Return human-readable strings for repos where drift increased vs baseline."""
    lines: list[str] = []
    for repo, data in report.items():
        current = data.get("drift_score", 0.0)
        prior = baseline.get(repo, {}).get("drift_score", 0.0)
        if current > prior:
            lines.append(
                f"WRK candidate: {repo} drift increased from {prior:.4f} to "
                f"{current:.4f} — run /work add 'fix doc drift in {repo}'"
            )
    return lines


# ---------------------------------------------------------------------------
# Baseline helpers
# ---------------------------------------------------------------------------


def _load_baseline(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open() as fh:
        return yaml.safe_load(fh) or {}


def _save_baseline(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {repo: {"drift_score": v["drift_score"]} for repo, v in report.items()}
    with path.open("w") as fh:
        yaml.dump(data, fh, default_flow_style=False, sort_keys=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Documentation drift detector (WRK-1093)"
    )
    parser.add_argument(
        "--repo",
        default="",
        help="Restrict check to one repo (lowercase name)",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Write current drift scores to baseline file",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--symbol-index",
        default=str(DEFAULT_SYMBOL_INDEX),
        help="Path to symbol-index.jsonl",
    )
    parser.add_argument(
        "--baseline",
        default=str(DEFAULT_BASELINE),
        help="Path to doc-drift-baseline.yaml",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[2]
    symbol_index_path = Path(args.symbol_index)
    if not symbol_index_path.is_absolute():
        symbol_index_path = repo_root / symbol_index_path

    baseline_path = Path(args.baseline)
    if not baseline_path.is_absolute():
        baseline_path = repo_root / baseline_path

    repos = list(REPO_MAP.keys())
    if args.repo:
        if args.repo not in REPO_MAP:
            print(f"ERROR: unknown repo '{args.repo}'", file=sys.stderr)
            return 1
        repos = [args.repo]

    report = run_drift_check(repos, symbol_index_path, repo_root)

    if args.update_baseline:
        _save_baseline(baseline_path, report)
        print(f"Baseline updated: {baseline_path}")

    baseline = _load_baseline(baseline_path)
    candidates = format_drift_candidates(report, baseline)

    if args.format == "json":
        output = {
            "report": report,
            "candidates": candidates,
        }
        print(json.dumps(output, indent=2))
    else:
        for repo, data in report.items():
            score = data["drift_score"]
            stale = len(data["stale_files"])
            undoc = len(data["undocumented"])
            prior = baseline.get(repo, {}).get("drift_score", 0.0)
            trend = "=" if score == prior else ("↑" if score > prior else "↓")
            print(
                f"[{repo:<20}] drift={score:.4f} {trend}"
                f"  stale_files={stale}  undocumented={undoc}"
            )
        if candidates:
            print("\nCandidates for doc-drift WRK items:")
            for line in candidates:
                print(f"  {line}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
