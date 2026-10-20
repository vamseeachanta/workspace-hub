"""Read-only, literal sibling-contract audit; see docs/agents/hub-routing-audit.md."""

import argparse
import html
import json
import re
from pathlib import Path

# Acceptance marker: workspace-hub issue 3958, Acceptance criteria.
TARGET = "../workspace-hub/AGENTS.md"
CONTRACT = f"Contract: {TARGET}"
HUB_REFERENCE = re.compile(r"workspace-hub/(?:blob/[^/\s]+/)?AGENTS\.md\b")


def active_lines(text):
    """Yield numbered prose lines, excluding fenced blocks and HTML comments."""
    fence = None
    in_comment = False
    for number, line in enumerate(text.splitlines(), 1):
        visible = ""
        while line:
            if in_comment:
                _, end, line = line.partition("-->")
                if not end:
                    break
                in_comment = False
            else:
                before, start, line = line.partition("<!--")
                visible += before
                if not start:
                    break
                in_comment = True
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", visible)
        if fence:
            if (match and match[1][0] == fence[0]
                    and len(match[1]) >= len(fence) and not match[2].strip()):
                fence = None
            continue
        if match:
            fence = match[1]
            continue
        # Indented code examples are not routing instructions.
        if visible.startswith(("    ", "\t")):
            continue
        yield number, visible.strip()


def audit_file(repo, filename):
    """Return evidence for one file; never create or modify an input."""
    row = {"repository": repo.name, "file": filename, "present": False,
           "routes": "no", "missing": [CONTRACT], "lines": []}
    path = repo / filename
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return row
    except (OSError, UnicodeError):
        row["present"] = path.exists()
        row["missing"] = [CONTRACT, "unreadable UTF-8 file"]
        return row
    row["present"] = True
    lines = list(active_lines(text))
    exact = [n for n, line in lines if line == CONTRACT]
    evidence = [n for n, line in lines
                if "Contract:" in line or HUB_REFERENCE.search(line)]
    row["lines"] = exact or evidence
    if exact:
        row.update(routes="yes", missing=[])
    elif evidence:
        row["routes"] = "partial"
        row["missing"] = [f"exact line: {CONTRACT}"]
    return row


def audit_repository(repo):
    """Report both current and retired instruction filenames separately."""
    return [audit_file(Path(repo), name) for name in ("AGENTS.md", "CLAUDE.md")]


def cell(value):
    return html.escape(str(value)).replace("|", "&#124;").replace("\n", " ").replace("\r", " ")


def render_table(rows):
    lines = ["| repository | file present | routes to the hub contract | missing marker(s) | line numbers |",
             "| --- | --- | --- | --- | --- |"]
    for row in rows:
        values = (row["repository"], f'{row["file"]}: {"yes" if row["present"] else "no"}',
                  row["routes"], "; ".join(row["missing"]) or "none",
                  ", ".join(map(str, row["lines"])) or "none")
        lines.append("| " + " | ".join(cell(v) for v in values) + " |")
    return "\n".join(lines)


def repository_paths(args, parser):
    paths = list(args.repositories)
    if args.repos_json:
        try:
            config = Path(args.repos_json)
            entries = json.loads(config.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            parser.error("cannot read repository JSON list")
        if (not isinstance(entries, list) or not entries
                or any(not isinstance(p, str) or not p.strip() for p in entries)):
            parser.error("repository JSON must be a nonempty list of nonempty paths")
        paths.extend(str(config.parent / p) for p in entries)
    if not paths:
        parser.error("supply checkout paths or --repos-json")
    repositories = list(dict.fromkeys(Path(p).resolve() for p in paths))
    if any(not repo.is_dir() for repo in repositories):
        parser.error("each repository checkout must be an existing directory")
    if len({repo.name for repo in repositories}) != len(repositories):
        parser.error("checkout basenames must be unique for an unambiguous table")
    return repositories


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repositories", nargs="*", help="sibling checkout directories")
    parser.add_argument("--repos-json", help="JSON list; paths relative to this file")
    args = parser.parse_args()
    repositories = repository_paths(args, parser)
    print(render_table([row for repo in repositories for row in audit_repository(repo)]))
    # Gaps are report data, not a CI policy decision. Usage errors return 2.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
