"""
Generate config/onboarding/repo-map.yaml from AGENTS.md frontmatter + pyproject.toml.

Usage:
    uv run --no-project python scripts/onboarding/generate-repo-map.py

Re-run after any structural change to an AGENTS.md or pyproject.toml.
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required — run: uv add pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = REPO_ROOT / "config" / "onboarding" / "repo-map.yaml"

TIER1_REPOS = [
    "assetutilities",
    "digitalmodel",
    "worldenergydata",
    "assethold",
    "OGManufacturing",
]


def parse_frontmatter(path: Path) -> dict:
    """Extract YAML frontmatter from a Markdown file (between --- delimiters)."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return {}
    block = "\n".join(lines[1:end])
    try:
        return yaml.safe_load(block) or {}
    except yaml.YAMLError as exc:
        print(f"WARN: YAML parse error in {path}: {exc}", file=sys.stderr)
        return {}


def parse_pyproject(path: Path) -> dict:
    """Extract name/description from pyproject.toml (simple regex, no TOML dep)."""
    import re
    result: dict = {}
    if not path.exists():
        return result
    text = path.read_text(encoding="utf-8")
    for key in ("name", "description", "version"):
        m = re.search(rf'^{key}\s*=\s*"([^"]+)"', text, re.MULTILINE)
        if m:
            result[key] = m.group(1)
    return result


def build_repo_entry(repo_name: str) -> dict | None:
    repo_path = REPO_ROOT / repo_name
    agents_md = repo_path / "AGENTS.md"
    pyproject = repo_path / "pyproject.toml"

    if not repo_path.exists():
        print(f"WARN: repo path missing, skipping: {repo_path}", file=sys.stderr)
        return None

    if not agents_md.exists():
        print(f"WARN: AGENTS.md missing for {repo_name}, skipping", file=sys.stderr)
        return None

    front = parse_frontmatter(agents_md)
    proj = parse_pyproject(pyproject)

    purpose = front.get("purpose") or proj.get("description") or "(undocumented)"
    test_command = front.get("test_command") or "(unknown)"
    entry_points = front.get("entry_points") or []
    depends_on = front.get("depends_on") or []
    maturity = front.get("maturity") or "unknown"

    if isinstance(entry_points, str):
        entry_points = [entry_points]
    if isinstance(depends_on, str):
        depends_on = [depends_on]

    return {
        "name": repo_name,
        "path": repo_name,
        "purpose": purpose,
        "test_command": test_command,
        "primary_modules": entry_points,
        "depends_on": depends_on,
        "maturity": maturity,
    }


def main() -> int:
    entries = []
    for repo in TIER1_REPOS:
        entry = build_repo_entry(repo)
        if entry:
            entries.append(entry)

    if not entries:
        print("ERROR: no repos processed", file=sys.stderr)
        return 1

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "generated_by": "scripts/onboarding/generate-repo-map.py",
        "note": "Re-run after any structural change to AGENTS.md or pyproject.toml",
        "repos": entries,
    }
    OUTPUT.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False), encoding="utf-8")
    print(f"Written: {OUTPUT.relative_to(REPO_ROOT)} ({len(entries)} repos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
