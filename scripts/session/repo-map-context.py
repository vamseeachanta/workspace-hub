#!/usr/bin/env python3
"""repo-map-context.py — Print repo-map entries for a WRK item's target_repos."""
import re
import sys
from pathlib import Path

def main() -> int:
    wrk_path = Path(sys.argv[1])
    repo_map_path = Path(sys.argv[2])

    if not wrk_path.exists() or not repo_map_path.exists():
        return 0

    # --- Parse target_repos from WRK frontmatter ---
    wrk_text = wrk_path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'^target_repos:\s*\n((?:[ \t]+-[^\n]+\n?)+)', wrk_text, re.MULTILINE)
    if not m:
        return 0

    target_repos = [
        re.sub(r'^\s*-\s*', '', line).strip()
        for line in m.group(1).splitlines()
        if line.strip().startswith('-')
    ]
    if not target_repos:
        return 0

    # --- Parse repo-map.yaml (minimal, no PyYAML dependency) ---
    repo_map_text = repo_map_path.read_text(encoding="utf-8", errors="replace")
    repos: dict[str, dict] = {}
    current: dict = {}
    for line in repo_map_text.splitlines():
        stripped = line.strip()
        if stripped.startswith('- name:'):
            if current.get('name'):
                repos[current['name']] = current
            current = {'name': stripped.split(':', 1)[1].strip()}
        elif ':' in stripped and current:
            key, _, val = stripped.partition(':')
            current[key.strip()] = val.strip().strip('"')
    if current.get('name'):
        repos[current['name']] = current

    HUB_REPOS = {'workspace-hub'}

    for repo_name in target_repos:
        if repo_name in HUB_REPOS:
            continue  # expected absence, not an error
        entry = repos.get(repo_name)
        if entry:
            purpose = entry.get('purpose', '').strip('"')
            print(f"  {entry['name']}: {purpose}")
            tc = entry.get('test_command', '')
            if tc:
                print(f"    test: {tc}")
        else:
            print(f"  NOTE: '{repo_name}' not found in repo-map.yaml")

    return 0


if __name__ == "__main__":
    sys.exit(main())
