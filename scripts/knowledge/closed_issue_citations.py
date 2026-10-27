#!/usr/bin/env python3
"""Offline, reporting-only FLOW-2 citation inspection.

Policy basis: docs/document-intelligence/pyramid-conformance-checks.md,
Information-Flow Checks (FLOW-2) and Anti-patterns (CF-3). No document is
rewritten and no state, promotion, authority or section meaning is inferred.

CLI example (all data is caller supplied)::

    python scripts/knowledge/closed_issue_citations.py --root . \
        --repository ORG/REPO --snapshot evidence.json \
        --domain-section Basis --operational-section Tracking docs/example.md

Snapshot JSON maps "#17" or a full GitHub issue URL to an object with optional
"state" ("closed", "open", "unknown") and "promoted_artifact" (relative link or
HTTP(S) URL). Missing entries/state remain unknown. Duplicate keys and ambiguous
aliases are errors. Bare numbers refer only to --repository, never another repo.

Section selectors are exact ATX heading text, inherited by subsections until a
peer/ancestor heading. Explicit operational selectors override inherited domain
scope and vice versa. Unselected text is reported as unscoped. Repeated headings
share scope. At least one supplied selector must match across the input files.

Supported citations: bare #number, GitHub issue URLs, inline Markdown links,
and full/collapsed reference links with single-line definitions. Fenced and
indented code, backtick spans and HTML comments are ignored. This is a bounded
Markdown scanner, not a full CommonMark parser: setext headings, raw HTML blocks,
list/blockquote-contained fences and multiline link definitions are unsupported.
Callers must normalize those forms before use; this report proves no compliance.

Output is deterministic JSON with relative file, first-line-is-one line, rule,
state, scope, status and suggested remediation per unique issue per source line.
A supplied promotion link is a suggestion, not proof of authoritative use.
Valid reports exit successfully even with warnings/unknowns; input errors use
argparse's usage-error exit. No network or external process is used.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

RULE = "FLOW-2"  # Policy identifier, from the document cited in the module docstring.
REPO = r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"
NUMBER = r"[1-9][0-9]*"  # GitHub issue identifiers are positive decimal integers.
URL = re.compile(rf"https://github\.com/({REPO})/issues/({NUMBER})(?![\w/])", re.I)
BARE = re.compile(rf"(?<![\w/#])#({NUMBER})\b")
# CommonMark ATX/fence grammar: up to three leading spaces; headings have one
# through six hashes; fences have at least three backticks or tildes.
HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?)|[ \t]*)$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
DEFINITION = re.compile(r'^ {0,3}\[([^\]]+)\]:\s*<?([^\s>]+)>?(?:\s+.*)?$')
INLINE_LINK = re.compile(r'\[([^\]\n]*)\]\(\s*<?([^\s)>]+)>?(?:\s+["\'][^\n]*?["\'])?\s*\)')
REFERENCE_LINK = re.compile(r"\[([^\]\n]+)\]\[([^\]\n]*)\]")


def _blank(text: str) -> str:
    return re.sub(r"[^\n]", " ", text)


def _visible_lines(text: str) -> list[str]:
    """Mask code/comments without moving physical source lines."""
    # Consume outer constructs first: a comment marker inside code is literal,
    # and code delimiters inside a comment cannot begin a new code block.
    tokens = re.compile(r"^ {0,3}(?:`{3,}|~{3,})[^\n]*|^(?: {4}|\t)[^\n]*|<!--|`+", re.M)
    masked = []
    position = 0  # Python string offsets begin at zero.
    while match := tokens.search(text, position):
        start, end = match.span()
        masked.append(text[position:start])
        token = match.group()
        opening = FENCE.fullmatch(token.rstrip("\r"))
        if opening and not (opening[1].startswith("`") and "`" in opening[2]):
            marker = re.escape(opening[1][0])
            closing = re.compile(rf"^ {{0,3}}{marker}{{{len(opening[1])},}}[ \t]*\r?$", re.M)
            close = closing.search(text, end)
            end = close.end() if close else len(text)
        elif token == "<!--":
            close = re.search(r"-->", text[end:])
            end = end + close.end() if close else len(text)
        elif re.fullmatch(r"`+", token):
            # Equal runs close a span; unmatched runs stay literal text.
            close = re.compile(rf"(?<!`){re.escape(token)}(?!`)").search(text, end)
            if close is None:
                masked.append(token)
                position = end
                continue
            end = close.end()
        elif not token.startswith(("    ", "\t")):
            masked.append(token)
            position = end
            continue
        masked.append(_blank(text[start:end]))
        position = end
    masked.append(text[position:])
    return "".join(masked).splitlines()


def _issue_url(repository: str, number: str) -> str:
    return f"https://github.com/{repository}/issues/{number}"


def _canonical_issue(value: str, repository: str) -> str:
    if re.fullmatch(rf"#{NUMBER}", value):
        return _issue_url(repository, value.removeprefix("#"))
    match = URL.fullmatch(value)
    if not match:
        raise ValueError("snapshot keys must be bare issue references or full issue URLs")
    return _issue_url(match[1], match[2])


def _promotion_link(value) -> bool:
    if not isinstance(value, str) or not value or re.search(r"[\s\\]", value):
        return False
    parts = urlsplit(value)
    if parts.scheme:
        return parts.scheme in {"http", "https"} and bool(parts.netloc) and not parts.username
    return not parts.netloc and not value.startswith("/")


def _snapshot(raw, repository: str) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("snapshot must be a JSON object")
    normalized = {}
    for key, evidence in raw.items():
        if not isinstance(key, str) or not isinstance(evidence, dict):
            raise ValueError("snapshot entries must map issue references to objects")
        canonical = _canonical_issue(key, repository).casefold()
        if canonical in normalized:
            raise ValueError("snapshot contains duplicate issue aliases")
        state = evidence.get("state", "unknown")
        if state not in ("closed", "open", "unknown"):
            raise ValueError("issue state must be closed, open or unknown")
        promoted = evidence.get("promoted_artifact")
        if "promoted_artifact" in evidence and not _promotion_link(promoted):
            raise ValueError("promoted_artifact must be a relative link or an HTTP(S) URL")
        normalized[canonical] = {"state": state, "promoted_artifact": promoted}
    return normalized


def _references(line: str, definitions: dict, repository: str) -> set[str]:
    issues = set()

    def destination(value):
        match = URL.match(value)
        if match:
            repo = repository if match[1].casefold() == repository.casefold() else match[1]
            issues.add(_issue_url(repo, match[2]))

    def inline(match):
        destination(match[2])
        return _blank(match.group())

    def reference(match):
        label = match[2] or match[1]
        target = definitions.get(" ".join(label.casefold().split()))
        if target is None:
            return match.group()
        destination(target)
        return _blank(match.group())

    line = INLINE_LINK.sub(inline, line)
    line = REFERENCE_LINK.sub(reference, line)
    for match in URL.finditer(line):
        destination(match.group())
    line = re.sub(r"https?://[^\s<>]+", lambda m: _blank(m.group()), line)
    for match in BARE.finditer(line):
        issues.add(_issue_url(repository, match[1]))
    return issues


def report(markdown_files, *, root, repository, snapshot, domain_sections,
           operational_sections=()) -> dict:
    """Inspect only explicit inputs; return evidence, never a conformance pass."""
    if not re.fullmatch(REPO, repository):
        raise ValueError("repository must have the form ORG/REPO")
    domain = set(domain_sections)
    operational = set(operational_sections)
    if not domain or any(not isinstance(s, str) or not s.strip() for s in domain | operational):
        raise ValueError("at least one nonempty domain section selector is required")
    if domain & operational:
        raise ValueError("a section cannot have conflicting explicit scopes")
    evidence = _snapshot(snapshot, repository)
    root = Path(root).resolve(strict=True)
    paths = sorted({(root / Path(p)).resolve(strict=True) for p in markdown_files})
    if not paths:
        raise ValueError("explicit Markdown inputs are required")
    references = []
    matched = False
    for path in paths:
        if not path.is_relative_to(root) or path.suffix.lower() != ".md":
            raise ValueError("inputs must be Markdown files within root")
        relative = path.relative_to(root).as_posix()
        lines = _visible_lines(path.read_text(encoding="utf-8"))
        definitions = {}
        for line in lines:
            definition = DEFINITION.match(line)
            if definition:
                label = " ".join(definition[1].casefold().split())
                definitions.setdefault(label, definition[2])
        sections = []
        # Source line numbers follow the first-line-is-one convention.
        for number, line in enumerate(lines, start=1):
            if DEFINITION.match(line):
                continue
            heading = HEADING.match(line)
            if heading:
                level = len(heading[1])
                title = re.sub(r"\s+#+\s*$", "", heading[2] or "").strip()
                while sections and sections[-1][0] >= level:
                    sections.pop()
                inherited = sections[-1][1] if sections else "unscoped"
                scope = ("domain-knowledge" if title in domain else
                         "operational-reference" if title in operational else inherited)
                matched |= title in domain | operational
                sections.append((level, scope))
            scope = sections[-1][1] if sections else "unscoped"
            for issue in sorted(_references(line, definitions, repository)):
                entry = evidence.get(issue.casefold(), {})
                state = entry.get("state", "unknown")
                promoted = entry.get("promoted_artifact")
                if state == "unknown":
                    status = "unknown-state"
                    remediation = "Supply issue-state evidence in the snapshot; no authority conclusion is available."
                elif scope == "unscoped":
                    status = "unscoped"
                    remediation = "Supply explicit section scope for human review."
                elif scope == "operational-reference":
                    status = "operational-reference"
                    remediation = "Retain as operational provenance; no domain-authority conclusion is made."
                elif state == "open":
                    status = "open-issue"
                    remediation = "Review domain authority separately; open state establishes no authority."
                else:
                    status = "warning"
                    remediation = ("Cite the promoted artifact and retain the issue as provenance if needed."
                                   if promoted else
                                   "Promote the knowledge to a durable artifact, then cite it; retain the issue as provenance if needed.")
                references.append(dict(file=relative, line=number, rule=RULE, issue=issue,
                                       state=state, scope=scope, status=status,
                                       remediation_link=promoted, remediation=remediation))
    if not matched:
        raise ValueError("no supplied section selector matched an ATX heading")
    return {"mode": "advisory", "rule": RULE, "references": references}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("snapshot contains duplicate JSON keys")
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--domain-section", action="append", required=True)
    parser.add_argument("--operational-section", action="append", default=[])
    parser.add_argument("markdown", nargs="+")
    args = parser.parse_args(argv)
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
        result = report(args.markdown, root=args.root, repository=args.repository, snapshot=snapshot,
                        domain_sections=args.domain_section, operational_sections=args.operational_section)
    except (OSError, UnicodeError):
        parser.error("input could not be read as UTF-8; verify the supplied files and root")
    except ValueError as error:
        # JSON decoder messages contain no input contents or absolute file paths.
        parser.error(str(error))
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    # Successful advisory emission is not a pass, even when every state is known.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
