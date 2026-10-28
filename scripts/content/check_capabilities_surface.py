"""Read-only structural audit of the single capabilities surface (issue #3494).

Inputs are explicit repository roots and optional maintained link files. No
network access, builds, directory discovery, or writes are performed. The
contract is the selected redirect design in issue #3494 and the merged source
stubs at digitalmodel:docs/api/capabilities/index.html and
worldenergydata:reports/capabilities/index.html (July 2026).
"""

from __future__ import annotations

import argparse
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

# Source: the merged redirect stubs referenced above use the www HTTPS endpoint.
CANONICAL = "https://www.aceengineer.com/capabilities/"
SURFACES = {
    "digitalmodel": Path("docs/api/capabilities/index.html"),
    "worldenergydata": Path("reports/capabilities/index.html"),
}
# Source: the same stubs use an immediate (zero-delay) refresh.
REFRESH = re.compile(r"0\s*;\s*url\s*=\s*(\S+)\s*", re.IGNORECASE)
# HTML void elements alone acknowledge a self-closing flag.
VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}
URL = re.compile(r"https?://[^\s<>\"'`\[\]()]+", re.IGNORECASE)


class RedirectParser(HTMLParser):
    """Collect contract evidence; comments never count as markup or link text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.canonicals: list[str | None] = []
        self.refreshes: list[str] = []
        self.robots: list[set[str]] = []
        self.visible_link = False
        self.rich_content = False
        self.invalid_markup = False
        self.anchor_target: str | None = None
        self.anchor_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if len(values) != len(attrs):
            self.invalid_markup = True
        in_head = (any(t == "head" for t, _ in self.stack)
                   and not any(t == "template" for t, _ in self.stack))
        if in_head and tag == "noscript":
            # Contents depend on scripting mode; never qualify that structure.
            self.invalid_markup = True
        in_body = any(t == "body" for t, _ in self.stack)
        style = re.sub(r"\s+", "", values.get("style") or "").lower()
        hidden = (
            any(h for _, h in self.stack)
            or "hidden" in values
            or (values.get("aria-hidden") or "").lower() == "true"
            or "display:none" in style
            or "visibility:hidden" in style
            or tag in {"script", "style", "template", "noscript"}
        )
        if (in_head and tag == "link"
                and "canonical" in (values.get("rel") or "").lower().split()):
            self.canonicals.append(values.get("href"))
        if in_head and tag == "meta":
            if (values.get("http-equiv") or "").lower() == "refresh":
                self.refreshes.append(values.get("content") or "")
            if (values.get("name") or "").lower() == "robots":
                self.robots.append(set(re.split(
                    r"[\s,]+", (values.get("content") or "").strip().lower()
                )))
        # A landing stub has prose and links, never an embedded capability report.
        # This is structural evidence, not a semantic equivalence test of prose.
        if tag in {"script", "iframe", "object", "embed"}:
            self.rich_content = True
        if in_body and tag not in {"main", "p", "a", "strong", "em", "span", "br"}:
            self.rich_content = True
        if tag == "a":
            self.anchor_target = values.get("href") if in_body and not hidden else None
            self.anchor_text = []
        if tag not in VOID_ELEMENTS:
            self.stack.append((tag, hidden))

    def handle_startendtag(self, tag, attrs):
        if tag not in VOID_ELEMENTS:
            self.invalid_markup = True
        # Non-void elements remain open, as in HTML parsing.
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == "a":
            if self.anchor_target == CANONICAL and "".join(self.anchor_text).strip():
                self.visible_link = True
            self.anchor_target = None
            self.anchor_text = []
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.anchor_target and not any(hidden for _, hidden in self.stack):
            self.anchor_text.append(data)


def check_redirect(markup: str) -> list[str]:
    """Return failed structural rules in stable order, without echoing input."""
    parser = RedirectParser()
    parser.feed(markup)
    parser.close()
    failures = []
    if parser.invalid_markup:
        failures.append("markup")
    if parser.canonicals != [CANONICAL]:
        failures.append("canonical")
    refresh = REFRESH.fullmatch(parser.refreshes[0]) if len(parser.refreshes) == 1 else None
    if refresh is None or refresh.group(1) != CANONICAL:
        failures.append("refresh")
    if len(parser.robots) != 1 or parser.robots[0] != {"noindex", "follow"}:
        failures.append("robots")
    if not parser.visible_link:
        failures.append("visible-link")
    if parser.rich_content:
        failures.append("landing-content")
    return failures


def old_landing_links(text: str) -> list[str]:
    """Find absolute Pages landing links, preserving technical subpage links.

    Only the exact landing path or its index.html spelling is selected. Query
    strings and old landing anchors do not change the destination's role. The
    Pages account is deliberately not hardcoded. Relative links are ambiguous
    without a publishing base and are outside this check's scope.
    """
    found = []
    for match in URL.finditer(html.unescape(text)):
        url = match.group().rstrip(".,;:!?")
        try:
            parts = urlsplit(url)
            host = parts.hostname or ""
        except ValueError:
            continue
        if not host.endswith(".github.io"):
            continue
        paths = {
            f"/{repo}/capabilities{suffix}"
            for repo in SURFACES for suffix in ("", "/", "/index.html")
        }
        if parts.path in paths:
            found.append(url)
    return found


def audit(roots: dict[str, Path], link_files: list[Path]) -> list[dict]:
    """Read the declared files only; missing or unreadable input denies PASS."""
    results = []
    for surface, relative in SURFACES.items():
        row = {"surface": surface, "source": relative.as_posix()}
        try:
            failures = check_redirect((roots[surface] / relative).read_text(encoding="utf-8"))
        except (OSError, UnicodeError):
            row.update(status="NOT_EVALUATED", rules=["source-unreadable"])
        else:
            row.update(status="FAIL" if failures else "PASS", rules=failures)
        results.append(row)
    for index, path in enumerate(link_files, start=1):
        # Stable input ordinal avoids exposing caller paths or arbitrary contents.
        row = {"surface": f"links-{index}"}
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            row.update(status="NOT_EVALUATED", rules=["source-unreadable"])
        else:
            lines = [n for n, line in enumerate(text.splitlines(), start=1)
                     if old_landing_links(line)]
            row.update(status="FAIL" if lines else "PASS", lines=lines,
                       rules=["old-landing-link"] if lines else [])
        results.append(row)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for surface in SURFACES:
        parser.add_argument(f"--{surface}-root", required=True, type=Path)
    parser.add_argument("--links", action="append", default=[], type=Path,
                        help="Explicit UTF-8 navigation file; may be repeated")
    args = parser.parse_args(argv)
    roots = {surface: getattr(args, f"{surface}_root") for surface in SURFACES}
    results = audit(roots, args.links)
    print(json.dumps(results, indent=2))
    return int(any(row["status"] != "PASS" for row in results))


if __name__ == "__main__":
    raise SystemExit(main())
