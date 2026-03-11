#!/usr/bin/env python3
# ABOUTME: WRK-1085 — Build AST-based symbol index for all tier-1 Python repos.
# ABOUTME: Walks src roots, extracts classes/functions/constants, writes JSONL.
# ABOUTME: Usage: uv run --no-project python scripts/search/build-symbol-index.py [--quiet]

import ast
import json
import os
import sys
import warnings

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_FILE = os.path.join(REPO_ROOT, "config", "search", "symbol-index.jsonl")

TIER1_REPOS = {
    "assethold": "assethold/src",
    "assetutilities": "assetutilities/src",
    "digitalmodel": "digitalmodel/src",
    "OGManufacturing": "OGManufacturing/src",
    "worldenergydata": "worldenergydata/src",
}

CONSTANT_RE = __import__("re").compile(r"^[A-Z][A-Z0-9_]{2,}$")


def emit_symbol(symbol, kind, repo, filepath, line):
    rel_file = os.path.relpath(filepath, REPO_ROOT).replace(os.sep, "/")
    return {"symbol": symbol, "kind": kind, "repo": repo, "file": rel_file, "line": line}


def walk_ast(tree, repo, filepath, records):
    for node in ast.walk(tree):
        if isinstance(node, ast.Module):
            for child in node.body:
                _process_top_level(child, repo, filepath, records)
            break


def _process_top_level(node, repo, filepath, records):
    if isinstance(node, ast.ClassDef):
        records.append(emit_symbol(node.name, "class", repo, filepath, node.lineno))
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                records.append(
                    emit_symbol(child.name, "method", repo, filepath, child.lineno)
                )
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        records.append(emit_symbol(node.name, "function", repo, filepath, node.lineno))
    elif isinstance(node, ast.Assign):
        if len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and CONSTANT_RE.match(target.id):
                records.append(
                    emit_symbol(target.id, "constant", repo, filepath, node.lineno)
                )


def index_repo(repo_name, src_rel, quiet):
    src_root = os.path.join(REPO_ROOT, src_rel)
    if not os.path.isdir(src_root):
        if not quiet:
            print(f"  SKIP {repo_name}: src root not found at {src_rel}", file=sys.stderr)
        return [], 0

    records = []
    file_count = 0
    for dirpath, dirnames, filenames in os.walk(src_root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__" and not d.startswith(".")]
        for fname in sorted(filenames):
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fname)
            file_count += 1
            try:
                with open(fpath, encoding="utf-8", errors="replace") as fh:
                    source = fh.read()
                tree = ast.parse(source, filename=fpath)
            except SyntaxError as exc:
                warnings.warn(f"SyntaxError in {fpath}: {exc}", stacklevel=2)
                continue
            except OSError as exc:
                warnings.warn(f"OSError reading {fpath}: {exc}", stacklevel=2)
                continue
            walk_ast(tree, repo_name, fpath, records)
    return records, file_count


def main():
    quiet = "--quiet" in sys.argv

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    all_records = []
    total_files = 0
    active_repos = 0

    for repo_name, src_rel in TIER1_REPOS.items():
        records, file_count = index_repo(repo_name, src_rel, quiet)
        if file_count > 0:
            active_repos += 1
        all_records.extend(records)
        total_files += file_count
        if not quiet:
            print(f"  {repo_name}: {len(records)} symbols from {file_count} files")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        for rec in all_records:
            fh.write(json.dumps(rec) + "\n")

    print(
        f"Indexed {len(all_records)} symbols from {total_files} files "
        f"across {active_repos} repos"
    )


if __name__ == "__main__":
    main()
