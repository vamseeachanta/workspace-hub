#!/usr/bin/env python3
"""check-wiki-sibling-frontmatter.py — workspace-hub #2778 enforcement.

Validates YAML frontmatter on staged (pre-commit) or committed (CI) wiki content
inside `llm-wiki` (generic) and `llm-wiki-<client>` (per-client) sibling repos.

Contract reference: .claude/rules/wiki-sibling-routing.md (Rules A-E).
Plan: docs/plans/2026-05-22-issue-2778-wiki-sibling-routing-contract.md.

Repo-scope: bails early via `git rev-parse --show-toplevel` + basename match
against `llm-wiki` / `llm-wiki-*`. Workspace-hub paths are out-of-scope by
construction.

Modes (auto-detected via $CI):
    pre-commit (default): git diff --cached --name-only --diff-filter=ACM
    CI         (CI=true): git diff --name-only --diff-filter=ACM ${BASE_REF}..HEAD
                          with --depth=1 fetch fallback for shallow clones.

Bypass: WIKI_FRONTMATTER_ALLOW=1 (logged). Matches ALLOW_ABS_PATHS=1 shape.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("[wiki-frontmatter] PyYAML not installed — cannot validate", file=sys.stderr)
    sys.exit(0)  # degrade open; install path is documented in the rule


ALLOWED_VISIBILITY = {
    "private-llm-wiki",
    "private-client-llm-wiki",
    "public-federal-data",
}

PROJECT_README_BASENAME = "README.md"  # r2-F4: excluded from project validation


def _git(args: list[str], cwd: Path | None = None, check: bool = True) -> str:
    """Run a git command and return stdout (stripped)."""
    r = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
    )
    return r.stdout.strip()


def _git_safe(args: list[str], cwd: Path | None = None) -> str | None:
    """Run a git command; return stdout or None on failure."""
    try:
        return _git(args, cwd=cwd, check=True)
    except subprocess.CalledProcessError:
        return None


def _parse_frontmatter(path: Path) -> dict[str, Any] | None:
    """Parse the YAML frontmatter block (between leading --- markers). Returns None if absent."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    block = text[4:end]
    try:
        data = yaml.safe_load(block)
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def _load_registry(repo_root: Path) -> dict[str, dict[str, Any]] | None:
    """Resolve and load client-wikis.yml registry.

    Precedence:
        1. $WIKI_SIBLING_REGISTRY_PATH if set
        2. $repo_root/.workspace-hub/client-wikis.yml
        3. None (warn-only mode for registry-dependent rules)
    """
    explicit = os.environ.get("WIKI_SIBLING_REGISTRY_PATH")
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.append(repo_root / ".workspace-hub" / "client-wikis.yml")
    for path in candidates:
        if path.is_file():
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except yaml.YAMLError:
                return None
            if not isinstance(data, dict):
                return None
            wikis = data.get("wikis", [])
            if not isinstance(wikis, list):
                return None
            return {w.get("short_name"): w for w in wikis if isinstance(w, dict) and w.get("short_name")}
    return None


def _gather_files(mode: str, base_ref: str, repo_root: Path) -> list[str]:
    """Gather candidate files based on mode."""
    if mode == "ci":
        # r2-F5: shallow-clone safety — try fetch first, degrade open on failure.
        subprocess.run(
            ["git", "fetch", "--depth=1", "origin", base_ref],
            cwd=repo_root,
            capture_output=True,
            check=False,
        )
        out = _git_safe(
            ["diff", "--name-only", "--diff-filter=ACM", f"{base_ref}..HEAD"],
            cwd=repo_root,
        )
        if out is None:
            print(
                f"[wiki-frontmatter] base ref '{base_ref}' unreachable in CI clone — "
                f"skipping check (degrades open; set fetch-depth: 0 to enforce)",
                file=sys.stderr,
            )
            return []
        return [line for line in out.splitlines() if line]
    # pre-commit
    out = _git(
        ["diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=repo_root,
    )
    return [line for line in out.splitlines() if line]


def _is_wiki_path(path: str, is_client_wiki: bool) -> bool:
    """Filter to wiki content paths. r2-F3: pages/ included. r2-F4: README.md excluded under projects/."""
    if fnmatch.fnmatch(path, "wikis/*.md") or fnmatch.fnmatch(path, "wikis/**/*.md"):
        return True
    if fnmatch.fnmatch(path, "pages/*.md") or fnmatch.fnmatch(path, "pages/**/*.md"):
        return True
    if is_client_wiki and (fnmatch.fnmatch(path, "projects/*.md") or fnmatch.fnmatch(path, "projects/**/*.md")):
        if os.path.basename(path) == PROJECT_README_BASENAME:
            return False
        return True
    return False


def _validate(
    file_rel: str,
    repo_root: Path,
    is_client_wiki: bool,
    expected_client_slug: str | None,
    registry: dict[str, dict[str, Any]] | None,
) -> list[str]:
    """Apply Rules A-E to a single file. Returns list of error strings."""
    errors: list[str] = []
    abs_path = repo_root / file_rel
    fm = _parse_frontmatter(abs_path)
    if fm is None:
        errors.append(f"{file_rel}: missing or unparseable YAML frontmatter")
        return errors

    visibility = fm.get("visibility")
    client = fm.get("client")
    project = fm.get("project")

    # Rule A
    if visibility not in ALLOWED_VISIBILITY:
        errors.append(
            f"{file_rel}: visibility='{visibility}' not in {sorted(ALLOWED_VISIBILITY)}"
        )
        return errors  # downstream rules assume valid visibility

    # Rule B
    if visibility == "private-client-llm-wiki" and not client:
        errors.append(f"{file_rel}: visibility=private-client-llm-wiki requires client:")

    # Rule C
    if client:
        if is_client_wiki and client != expected_client_slug:
            errors.append(
                f"{file_rel}: client='{client}' but repo identity is '{expected_client_slug}'"
            )
        elif not is_client_wiki:
            errors.append(f"{file_rel}: client='{client}' set but repo is generic llm-wiki")
        if registry is not None and client not in registry:
            errors.append(f"{file_rel}: client='{client}' not in client-wikis registry")

    # Rule D
    if project and visibility != "private-client-llm-wiki":
        errors.append(
            f"{file_rel}: project='{project}' set but visibility is not private-client-llm-wiki"
        )

    # Rule E (forward-compatible — warn-only when projects list is absent)
    if project and client and registry is not None:
        entry = registry.get(client)
        if entry:
            projects_list = entry.get("projects")
            if projects_list and project not in projects_list:
                errors.append(
                    f"{file_rel}: project='{project}' not in registry.projects for client='{client}'"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Override base ref for CI mode")
    parser.add_argument("--mode", choices=["pre-commit", "ci"], help="Force mode (otherwise auto-detect)")
    args = parser.parse_args()

    # r2-F6: explicit bypass at top, logged to stderr.
    if os.environ.get("WIKI_FRONTMATTER_ALLOW") == "1":
        print(
            "[wiki-frontmatter] bypass via WIKI_FRONTMATTER_ALLOW=1",
            file=sys.stderr,
        )
        return 0

    # 1. Repo identity (r2-F1 fix).
    repo_root_str = _git_safe(["rev-parse", "--show-toplevel"])
    if repo_root_str is None:
        print("[wiki-frontmatter] not inside a git repo — skipping", file=sys.stderr)
        return 0
    repo_root = Path(repo_root_str)
    repo_name = repo_root.name

    if repo_name != "llm-wiki" and not repo_name.startswith("llm-wiki-"):
        # Not a wiki repo — bail early. Workspace-hub and other repos are out-of-scope.
        return 0

    is_client_wiki = repo_name.startswith("llm-wiki-")
    expected_client_slug = repo_name[len("llm-wiki-"):] if is_client_wiki else None

    # 2. Mode + base_ref resolution.
    if args.mode:
        mode = args.mode
    elif os.environ.get("CI") == "true":
        mode = "ci"
    else:
        mode = "pre-commit"
    base_ref = args.base or os.environ.get("WIKI_FRONTMATTER_BASE_REF") or "origin/main"

    # 3. Gather files.
    changed_files = _gather_files(mode, base_ref, repo_root)
    if not changed_files:
        return 0

    # 4. Filter to wiki content paths.
    wiki_files = [p for p in changed_files if _is_wiki_path(p, is_client_wiki)]
    if not wiki_files:
        return 0

    # 5. Load registry (warn-only if absent).
    registry = _load_registry(repo_root)
    if registry is None:
        print(
            "[wiki-frontmatter] client-wikis.yml registry not found — "
            "Rules C/E degrade to warn-only (vendor via install-pre-commit-hook-cross-repo.sh)",
            file=sys.stderr,
        )

    # 6. Validate.
    all_errors: list[str] = []
    for file_rel in wiki_files:
        all_errors.extend(
            _validate(file_rel, repo_root, is_client_wiki, expected_client_slug, registry)
        )

    if all_errors:
        for e in all_errors:
            print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
