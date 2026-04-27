import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# Sentinel comment that protects a hand-curated leading region (raw-inventory banner)
# from being clobbered when this generator regenerates docs/CONTENT_INDEX.md.
# Locked by docs/plans/2026-04-22-issue-2464-workspace-hub-routing-split.md.
RAW_INVENTORY_SENTINEL = (
    "<!-- tier1-raw-inventory-banner: preserve; "
    "see docs/plans/2026-04-22-issue-2464 -->"
)
# Sentinel scan window: how many leading lines we'll search for the sentinel
# before deciding the file has no preserved prelude.
_PRELUDE_SCAN_LINES = 200


def is_repo_root(path: Path) -> bool:
    return (path / ".git").is_dir()


def scan_repository(repo_path: Path):
    """Scan a repository for disciplines, project files, and key docs."""
    results = {
        "disciplines": [],
        "project_files": [],
        "key_docs": []
    }

    # We will walk through the repository but ignore some common large/binary directories
    ignore_dirs = {".git", "node_modules", ".venv", "__pycache__", "dist", "build", "htmlcov", ".tox", ".pytest_cache", ".ruff_cache"}

    for root, dirs, files in os.walk(repo_path):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        current_dir = Path(root)

        for file in files:
            file_path = current_dir / file

            # Avoid overly deep or huge paths (optional safety)
            try:
                rel_path = file_path.relative_to(repo_path)
            except ValueError:
                continue

            path_str = str(rel_path)
            lower_path = path_str.lower()

            # 1. Disciplines
            # Match anything with 'discipline' in path or file name
            if 'discipline' in lower_path:
                results["disciplines"].append(path_str)

            # 2. Project Files
            project_file_names = {'project.md', 'roadmap.md', 'pyproject.toml', 'package.json', 'project.json', 'harness-config.yaml'}
            if file.lower() in project_file_names or 'projects/' in lower_path:
                # Do not duplicate if it also matched disciplines
                if path_str not in results["disciplines"]:
                    results["project_files"].append(path_str)

            # 3. Key Docs
            key_doc_names = {'readme.md', 'architecture.md', 'vision.md', 'index.md'}
            if file.lower() in key_doc_names or 'docs/' in lower_path or '.planning/' in lower_path:
                if file_path.suffix.lower() in {'.md', '.txt', '.pdf', '.rst'}:
                    if path_str not in results["disciplines"] and path_str not in results["project_files"]:
                        results["key_docs"].append(path_str)

    return results


def _read_preserved_prelude(output_path: Path) -> str:
    """Return the leading region of an existing CONTENT_INDEX-style file, up to
    (but not including) the body heading `# Content Index`, when the sentinel
    is present in that region. Returns "" when no preserved prelude is found.

    The sentinel guards the banner: if the user has not opted in by adding the
    sentinel, the generator owns the whole file as before.
    """
    output_path = Path(output_path)
    if not output_path.exists():
        return ""
    try:
        with open(output_path, "r", encoding="utf-8") as fh:
            head_lines: list[str] = []
            sentinel_seen = False
            body_start = -1
            for i, line in enumerate(fh):
                if i >= _PRELUDE_SCAN_LINES:
                    return ""
                head_lines.append(line)
                if RAW_INVENTORY_SENTINEL in line:
                    sentinel_seen = True
                if line.startswith("# Content Index"):
                    body_start = i
                    break
            if not sentinel_seen or body_start <= 0:
                return ""
            return "".join(head_lines[:body_start])
    except OSError:
        return ""


def write_markdown(output_path, index_data) -> None:
    """Render CONTENT_INDEX-style markdown to output_path, preserving any
    sentinel-guarded leading region from the existing file (idempotent).

    Exposed as a function (not just an inline block in main()) so that the
    sentinel-preservation contract can be exercised by `tests/docs/test_tier1_routing_hygiene.py::test_content_index_generator_preserves_sentinel`.
    """
    output_path = Path(output_path)
    preserved = _read_preserved_prelude(output_path)

    if output_path.parent and not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        if preserved:
            f.write(preserved)
            if not preserved.endswith("\n"):
                f.write("\n")

        f.write("# Content Index\n\n")
        f.write(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("This index catalogs disciplines, project files, and key docs across all repositories.\n\n")

        for repo_path, data in index_data.items():
            repo_name = Path(repo_path).name
            if not any(data.values()):
                continue  # Skip empty repos

            f.write(f"## Repository: `{repo_name}`\n")
            f.write(f"**Path**: `{repo_path}`\n\n")

            if data["disciplines"]:
                f.write("### Disciplines\n")
                for item in sorted(data["disciplines"]):
                    f.write(f"- `{item}`\n")
                f.write("\n")

            if data["project_files"]:
                f.write("### Project Files\n")
                for item in sorted(data["project_files"]):
                    f.write(f"- `{item}`\n")
                f.write("\n")

            if data["key_docs"]:
                f.write("### Key Docs\n")
                for item in sorted(data["key_docs"]):
                    f.write(f"- `{item}`\n")
                f.write("\n")

            f.write("---\n\n")


def main():
    parser = argparse.ArgumentParser(description="Build a searchable content index across repositories.")
    parser.add_argument("--root", default="/mnt/local-analysis/", help="Root directory to scan for repositories")
    parser.add_argument("--output-json", default="data/content_index.json", help="Output JSON file")
    parser.add_argument("--output-md", default="docs/CONTENT_INDEX.md", help="Output Markdown file")
    args = parser.parse_args()

    root_dir = Path(args.root)
    repos = []

    # Find all git repos up to 3 levels deep
    for root, dirs, files in os.walk(root_dir):
        # Limit depth to avoid scanning the whole drive
        depth = root.replace(str(root_dir), "").count(os.sep)
        if depth >= 3:
            dirs[:] = []
            continue

        current_path = Path(root)
        if is_repo_root(current_path):
            repos.append(current_path)
            # Do not traverse into subdirectories of a repo to find other repos,
            # wait, workspace-hub HAS sub-repos. So we MUST traverse into subdirectories!
            # But we shouldn't traverse into .git

        if ".git" in dirs:
            dirs.remove(".git")

    print(f"Found {len(repos)} repositories in {root_dir}")

    index_data = {}

    for repo in repos:
        print(f"Scanning repository: {repo.name}")
        repo_data = scan_repository(repo)
        # Store using the full path as key to handle sub-repos properly
        index_data[str(repo)] = repo_data

    # Write JSON
    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
    with open(args.output_json, 'w') as f:
        json.dump(index_data, f, indent=2)
    print(f"Wrote JSON index to {args.output_json}")

    # Write Markdown (sentinel-preserving)
    write_markdown(args.output_md, index_data)

    print(f"Wrote Markdown index to {args.output_md}")


if __name__ == "__main__":
    main()
