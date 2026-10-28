"""Check existing local HTML bundles without a renderer or network access.

Usage: python scripts/reporting/publication_navigation.py BUNDLE_ROOT
API: check_bundle(root) returns deterministic, root-relative NavigationIssue
records; an empty list means every inspected local reference is valid.

All HTML/HTM files below the explicit root are inspected. href and src targets
must be relative, contained, non-symlink files (directories use index.html).
Queries do not affect filesystem lookup; percent-decoded fragments must match
an HTML id or legacy anchor name exactly. HTTP(S), protocol-relative, mail and
telephone links are ignored, never fetched. Other schemes, absolute paths and
base elements fail the portable bundle contract. Missing optional sections are
valid unless a link points to them. No latest/history layout is imposed: those
edges are documented and checked by the synthetic examples in the test module.

Input is UTF-8 HTML. CSS URLs, srcset, script-generated navigation, non-HTML
fragment semantics and concurrent filesystem mutation are outside this check.
Files are read without content or modification-metadata writes; filesystem
access times may change. Keep the bundle stable throughout inspection.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html.parser import HTMLParser
import os
from pathlib import Path
import re
import stat
from urllib.parse import unquote, urlsplit


@dataclass(frozen=True)
class NavigationIssue:
    """A source relative to the bundle root, the literal target and a reason."""

    source: str
    target: str
    reason: str


class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors: set[str] = set()
        self.targets: list[str] = []
        self.has_base = False

    def handle_starttag(self, tag, attrs):
        if tag == "base":
            self.has_base = True
            return
        for key, value in attrs:
            if value is None:
                continue
            if key == "id" or (tag == "a" and key == "name"):
                self.anchors.add(value)
            if key in {"href", "src"}:
                self.targets.append(value)

    handle_startendtag = handle_starttag


def _has_control(value: str) -> bool:
    # str.isprintable excludes Unicode formatting controls as well as newlines.
    return any(not char.isprintable() for char in value)


def _is_link(path: Path) -> bool:
    """Reject symlinks, junctions and other Windows reparse points."""
    if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
        return True
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except FileNotFoundError:
        return False
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def _local_target(root: Path, source: Path, target: str):
    """Return (path, fragment, failure); None path means an ignored remote URL."""
    if _has_control(target) or "\\" in target:
        return None, "", "invalid-target"
    try:
        parts = urlsplit(target.strip())
        if parts.scheme.lower() in {"http", "https", "mailto", "tel"}:
            return None, "", ""
        if parts.scheme:
            return None, "", "unsupported-scheme"
        if parts.netloc or target.strip().startswith("//"):
            return None, "", ""
        if re.search(r"%(?![a-fA-F0-9]{2})", parts.path + parts.fragment):
            return None, "", "invalid-target"
        path = unquote(parts.path, errors="strict")
        fragment = unquote(parts.fragment, errors="strict")
    except (ValueError, UnicodeError):
        return None, "", "invalid-target"
    if _has_control(path + fragment) or "\\" in path:
        return None, "", "invalid-target"
    if path.startswith("/"):
        return None, "", "absolute-target"
    if not path:
        return source, fragment, ""

    current = source.parent
    # Inspect before normalizing: alias/../page still traverses the alias.
    components = path.split("/")
    for position, component in enumerate(components):
        if component in {"", "."}:
            continue
        current = current.parent if component == ".." else current / component
        if not current.is_relative_to(root):
            return None, "", "escaped-target"
        if _is_link(current):
            return None, "", "symlinked-target"
        # Every slash requires a directory, including before a parent component.
        if position < len(components) - 1 and not current.is_dir():
            return None, "", "missing-target"
    if current.is_dir():
        current = current / "index.html"
        if _is_link(current):
            return None, "", "symlinked-target"
    if not current.is_file():
        return None, "", "missing-target"
    return current, fragment, ""


def check_bundle(root: str | Path) -> list[NavigationIssue]:
    """Inspect a stable explicit root, without writes, subprocesses or fetching.

    Invalid roots, unreadable HTML and an empty HTML inventory fail closed.
    Symlinked HTML sources and directories are reported without following them,
    even when their destinations are inside the root. Symlinked assets are
    rejected when referenced. Diagnostics contain no absolute filesystem paths.
    """
    root = Path(root).absolute()
    if any(_is_link(p) for p in (root, *root.parents)):
        return [NavigationIssue(".", "", "symlinked-root")]
    if not root.is_dir():
        return [NavigationIssue(".", "", "invalid-root")]

    issues: list[NavigationIssue] = []
    pages: dict[Path, _Page] = {}

    def issue(path, target, reason):
        issues.append(NavigationIssue(path.relative_to(root).as_posix(), target, reason))

    def walk_error(error):
        # Do not include the OS error string: it may contain an absolute path.
        issues.append(NavigationIssue(".", "", "unreadable-directory"))

    for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        parent = Path(directory)
        for name in sorted(dirs):
            path = parent / name
            if _is_link(path):
                issue(path, "", "symlinked-target")
        dirs[:] = sorted(name for name in dirs if not _is_link(parent / name))
        for name in sorted(files):
            path = parent / name
            if path.suffix.lower() not in {".html", ".htm"}:
                continue
            if _is_link(path):
                issue(path, "", "symlinked-target")
                continue
            try:
                page = _Page()
                page.feed(path.read_text(encoding="utf-8"))
                page.close()
                pages[path] = page
            except (OSError, UnicodeError, ValueError):
                issue(path, "", "unreadable-html")
    if not pages and not issues:
        return [NavigationIssue(".", "", "no-html")]

    for source, page in pages.items():
        if page.has_base:
            issue(source, "", "base-element")
        for target in page.targets:
            try:
                destination, fragment, reason = _local_target(root, source, target)
            except OSError:
                destination, fragment, reason = None, "", "unreadable-target"
            if reason:
                issue(source, target, reason)
            elif destination is not None and fragment:
                if destination not in pages:
                    issue(source, target, "uncheckable-fragment")
                elif fragment not in pages[destination].anchors:
                    issue(source, target, "missing-fragment")
    return sorted(issues, key=lambda item: (item.source, item.target, item.reason))


def main(argv: list[str] | None = None) -> int:
    """CLI: exit zero for valid navigation, one for reported violations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="explicit local HTML bundle root")
    issues = check_bundle(parser.parse_args(argv).root)
    for issue in issues:
        print(f"{issue.source}: {issue.reason}")
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
