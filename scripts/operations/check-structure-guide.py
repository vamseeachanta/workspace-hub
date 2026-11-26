"""Check a repository's folder inventory and render its structure guide."""

import argparse
import html
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import yaml


def git(repo, *args, stdin=None, allowed=(0,)):
    env = {k: v for k, v in os.environ.items() if k.upper() not in {
        "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"
    }}
    result = subprocess.run(
        ["git", "-C", repo, *args], input=stdin, capture_output=True, env=env,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if result.returncode not in allowed:
        raise ValueError(result.stderr.decode("utf-8", "replace").strip() or "Git failed")
    return result.stdout


def strings(value):
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def load_guide(path):
    guide = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(guide, dict) or type(guide.get("version")) is not int or guide["version"] != 1:
        raise ValueError("expected guide version 1")
    if type(guide.get("depth")) is not int or guide["depth"] < 1:
        raise ValueError("depth must be a positive integer")
    ignore = guide.get("ignore", [])
    if not strings(ignore) or not isinstance(guide.get("entries"), list):
        raise ValueError("expected lists for ignore and entries")
    entries = {}
    for row in guide["entries"]:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise ValueError("each entry needs a relative directory path")
        name = row["path"].removesuffix("/")
        if ("\\" in name or ":" in name or "\0" in name
                or any(part in ("", ".", "..") for part in name.split("/"))):
            raise ValueError(f"invalid entry path {name!r}")
        if name in entries:
            raise ValueError(f"duplicate entry for {name}")
        if not isinstance(row.get("owner", ""), str) or not strings(row.get("rules", [])):
            raise ValueError(f"invalid owner or rules for {name}")
        entries[name] = row
    return guide["depth"], set(ignore) | {".git"}, entries


def inventory(repo, depth, ignore):
    if git(repo, "rev-parse", "--show-prefix").strip():
        raise ValueError("REPO must be the repository root")
    tracked = set()
    gitlinks = set()
    for record in git(repo, "ls-files", "--stage", "-z").split(b"\0"):
        if not record:
            continue
        header, raw = record.split(b"\t", 1)
        parts = os.fsdecode(raw).split("/")
        if header.startswith(b"160000 "):
            gitlinks.add("/".join(parts))
        else:
            parts.pop()
        for i, part in enumerate(parts, 1):
            if part in ignore:
                break
            tracked.add("/".join(parts[:i]))

    folders = {name for name in tracked if len(name.split("/")) <= depth}
    parents = [repo]
    for _ in range(depth):
        candidates = {}
        for parent in parents:
            for child in parent.iterdir():
                if (child.name in ignore or child.is_symlink()
                        or getattr(child, "is_junction", lambda: False)() or not child.is_dir()):
                    continue
                name = child.relative_to(repo).as_posix()
                candidates[name] = child
        if not candidates:
            break
        names = [name for name in candidates if name not in gitlinks]
        ignored = set()
        if names:
            data = b"".join(os.fsencode(name + "/") + b"\0" for name in names)
            output = git(repo, "check-ignore", "-z", "--stdin", stdin=data, allowed=(0, 1))
            ignored = {os.fsdecode(item).rstrip("/") for item in output.split(b"\0") if item}
        parents = []
        for name, child in candidates.items():
            if name in ignored:
                continue
            folders.add(name)
            if name not in gitlinks and not (child / ".git").exists():
                parents.append(child)
    return folders


def table_cell(value):
    return "<br>".join(html.escape(value, quote=False).replace("\\", "\\\\")
                        .replace("|", "\\|").splitlines())


def render(repo, entries):
    lines = ["# Repository structure", "", "| Path | Purpose | Owner | Rules |",
             "| --- | --- | --- | --- |"]
    for name, row in sorted(entries.items()):
        cells = [table_cell(name + "/"), table_cell(row["purpose"]), table_cell(row.get("owner", "")),
                 "<br>".join(table_cell(rule) for rule in row.get("rules", []))]
        lines.append("| " + " | ".join(cells) + " |")
    docs = repo / "docs"
    if docs.resolve() != docs:
        raise ValueError("docs must be a repository-local directory")
    docs.mkdir(exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=docs, encoding="utf-8",
                                     newline="\n", delete=False) as handle:
        temp = Path(handle.name)
        try:
            handle.write("\n".join(lines) + "\n")
            handle.close()
            temp.replace(docs / "STRUCTURE.md")
        finally:
            temp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("--guide", type=Path, help="alternate YAML file (relative to current directory)")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    guide = args.guide or repo / "docs" / "structure.yaml"
    findings = []

    def finding(kind, path, **details):
        findings.append(dict(kind=kind, path=path, **details))

    try:
        depth, ignore, entries = load_guide(guide)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        finding("unreadable guide", str(guide), detail=str(exc))
    else:
        try:
            folders = inventory(repo, depth, ignore)
            for name in sorted(folders - entries.keys()):
                finding("undocumented", name + "/")
            for name, row in entries.items():
                if not (repo / name).is_dir():
                    finding("stale entry", name + "/")
                if not isinstance(row.get("purpose"), str) or not row["purpose"].strip():
                    finding("missing purpose", name + "/")
            if args.render and not findings:
                render(repo, entries)
        except (OSError, ValueError) as exc:
            finding("operation failed", str(repo), detail=str(exc))
    if args.json:
        print(json.dumps({"findings": findings}))
    else:
        for item in findings:
            print(f"{item['kind']}: {item['path']}", item.get("detail", ""))
    return int(bool(findings))


if __name__ == "__main__":
    sys.exit(main())
