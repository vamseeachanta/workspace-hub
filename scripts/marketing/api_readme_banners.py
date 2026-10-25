#!/usr/bin/env python3
"""Read-only audit of the API README banner checklist in issue #3300.

Catalog availability is a required, externally inspected input. A successful
text audit does not establish API hosting, workflow counts or engineering scope.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

# Source: issue #3300, Checklist and Draft banner snippet (2026).
# This is the issue's five-repository set, not the full ecosystem registry.
REPOSITORIES = (
    "digitalmodel", "worldenergydata", "deckhand", "deckhand-sandbox",
    "aceengineer-website",
)
# Source: existing README banners and the catalog dependency in issue #3300.
CATALOG_URL = "https://aceengineer.com/api-catalog.html"
CATALOG_STATUSES = ("live", "historical", "unverified")


def _intro_quotes(markdown: str) -> list[str]:
    """Collect contiguous quote blocks before the first section, ignoring fences."""
    markdown = re.sub(r"<!--[\s\S]*?(?:-->|\Z)", "\n", markdown)
    blocks = []
    current = []
    fence = None
    fence_quoted = False
    for line in markdown.splitlines():
        stripped = line.lstrip()
        quoted = stripped.startswith(">") and not line.startswith(("    ", "\t"))
        # CommonMark 0.31.2, sections 5.1 and 4.5: a quoted fence ends
        # when its containing quote ends, even without a closing marker.
        if fence is not None and fence_quoted and not quoted:
            fence = None
        content = stripped[1:] if quoted else line
        if quoted and content.startswith(" "):
            content = content[1:]
        # CommonMark 0.31.2, section 4.4: four spaces mark indented code.
        if content.startswith(("    ", "\t")):
            if current:
                blocks.append(" ".join(current))
                current = []
            continue
        # CommonMark 0.31.2, section 4.5: fences have at least three markers.
        marker = re.match(r" {0,3}(`{3,}|~{3,})", content)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
                fence_quoted = quoted
            elif (quoted == fence_quoted and token[0] == fence[0]
                  and len(token) >= len(fence) and not content[marker.end():].strip()):
                fence = None
            if current:
                blocks.append(" ".join(current))
                current = []
            continue
        if fence is not None:
            continue
        # CommonMark 0.31.2, section 4.2: ATX headings have one to six markers.
        # Issue #3300 places the banner at the top, before any subsection.
        if re.match(r"#{2,6}\s", stripped):
            break
        if quoted:
            current.append(content.strip())
        elif current:
            blocks.append(" ".join(current))
            current = []
    if current:
        blocks.append(" ".join(current))
    return blocks


def _is_catalog_link(text: str) -> bool:
    # CommonMark 0.31.2, section 6.3: the destination, not the label,
    # determines a link's target. Images do not provide a catalog link.
    def destination(match: re.Match) -> str:
        if match.group(1):
            return " "
        target = match.group(2).strip()
        if target.startswith("<"):
            return " " + target[1:].split(">", 1)[0] + " "
        return " " + target.split(maxsplit=1)[0] + " " if target else " "

    text = re.sub(r"(!?)\[(?:\\.|[^\]\\])*\]\(([^)\n]*)\)", destination, text)
    # Unresolved/reference labels also cannot supply destination evidence.
    text = re.sub(r"\[(?:\\.|[^\]\\])*\]", " ", text)
    for candidate in re.findall(r"https?://[^\s<>()]+", text):
        try:
            parsed = urlsplit(candidate.rstrip(".,;]"))
        except ValueError:
            continue
        if (parsed.scheme == "https"
                and parsed.netloc in ("aceengineer.com", "www.aceengineer.com")
                and parsed.path == "/api-catalog.html"
                and not parsed.query):
            return True
    return False


def _missing(text: str) -> list[str]:
    # Source: issue #3300, Draft banner snippet. Markdown emphasis is presentation.
    plain = re.sub(r"[*_`]", "", text).casefold()
    checks = {
        "deckhand_api": bool(re.search(
            r"\bdeckhand(?:\s+(?:is|—|-))?\s+(?:the\s+)?api\b", plain)),
        "api_path": bool(re.search(r"\bapi paths?\b", plain)),
        "run_endpoint": bool(re.search(r"\bpost /api/run(?=$|[\s.,;:)\]])", plain)),
        "report_contract": "standards-traceable html report url" in plain,
        "determinism": bool(re.search(r"\bdeterministic\b", plain))
        or "same input, same output" in plain,
        "catalog_link": _is_catalog_link(text),
        "api_reference": bool(re.search(
            r"\bdocs/deckhand/api\.md(?=$|[\s,;:)\]#])", plain)),
    }
    return [name for name, passed in checks.items() if not passed]


def audit(readmes: dict[str, str | None], *, catalog_status: str) -> dict:
    """Audit explicit snapshots; never infer availability from a banner or HTTP 200.

    Missing/unreadable snapshots and non-live catalog inputs are NOT_EVALUATED.
    A known text defect is FAIL even when another repository is unavailable.
    The catalog gate takes precedence: historical evidence never permits rollout.
    """
    if catalog_status not in CATALOG_STATUSES:
        raise ValueError("Unknown catalog status")
    if set(readmes) - set(REPOSITORIES):
        raise ValueError("Unknown repository")
    rows = []
    for repo in REPOSITORIES:
        text = readmes.get(repo)
        if text is None:
            rows.append({"repository": repo, "status": "NOT_EVALUATED", "missing": ["readme"]})
            continue
        candidates = [_missing(block) for block in _intro_quotes(text)]
        missing = min(candidates, key=len) if candidates else _missing("")
        rows.append({"repository": repo, "status": "FAIL" if missing else "PASS",
                     "missing": missing})
    gate = "PASS" if catalog_status == "live" else "NOT_EVALUATED"
    statuses = {row["status"] for row in rows}
    if gate != "PASS":
        status = gate
    elif "FAIL" in statuses:
        status = "FAIL"
    elif "NOT_EVALUATED" in statuses:
        status = "NOT_EVALUATED"
    else:
        status = "PASS"
    return {"status": status,
            "catalog": {"url": CATALOG_URL, "declared_status": catalog_status, "status": gate},
            "repositories": rows}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-status", required=True, choices=CATALOG_STATUSES,
                        help="Status independently established from the catalog; never inferred")
    parser.add_argument("--readme", action="append", default=[], metavar="REPOSITORY=FILE",
                        help="Explicit local snapshot; repeat for each checklist member")
    args = parser.parse_args(argv)
    readmes = {}
    for entry in args.readme:
        repo, separator, filename = entry.partition("=")
        if not separator or repo not in REPOSITORIES or not filename:
            parser.error("--readme requires a checklist repository and a nonempty file")
        if repo in readmes:
            parser.error("--readme repeats a repository")
        try:
            readmes[repo] = Path(filename).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            # Do not expose local filesystem details in the report.
            readmes[repo] = None
    result = audit(readmes, catalog_status=args.catalog_status)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
