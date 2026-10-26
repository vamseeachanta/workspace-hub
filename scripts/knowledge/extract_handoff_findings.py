"""Read-only candidate extraction from explicitly supplied UTF-8 handoff content.

Heading vocabulary and candidate status follow docs/plans/
2026-04-27-issue-2374-transient-promotion-candidate-queue.md, handoff design.
This bounded interface performs no discovery, Git access, scoring or writes.
``source_sha`` is a SHA-256 content digest, not a Git revision or blob ID.
Summaries retain the complete bullet payload, including continuation whitespace.

Supported Markdown syntax follows CommonMark sections 4.2, 4.5 and 5.2:
ATX headings, backtick/tilde fences and unordered/ordered list markers.
This is a selective line parser, not a general Markdown renderer.
"""

import hashlib
import re


FINDING_HEADINGS = (
    "finding", "lesson", "decision", "discover", "open item",
    "key technical", "pattern", "outcome", "what was completed",
)
HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?)(?:[ \t]+#+)?)?[ \t]*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
BULLET = re.compile(r"^( *)(?:[-+*]|[0-9]{1,9}[.)])(?:[ \t]+|$)(.*)$")
ISSUE = re.compile(r"(?<![\w#])#([1-9][0-9]*)\b")


def _validate_source(source_path):
    """Accept canonical relative POSIX identities without resolving any files."""
    if (
        not isinstance(source_path, str)
        or not source_path
        or any(part in ("", ".", "..") for part in source_path.split("/"))
        or any(char in source_path for char in ("\\", ":"))
        or any(ord(char) < ord(" ") for char in source_path)
    ):
        raise ValueError("source_path must be a canonical repo-relative identity")


def _finding_bullets(text):
    """Yield payload slices under matching headings, excluding fenced examples."""
    sections = []
    fence = None
    bullet = []
    indent = None
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        marker = FENCE.match(content)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                if not marker[2].strip():
                    fence = None
            continue
        if marker:
            if indent is None or len(content) - len(content.lstrip(" ")) <= indent:
                if bullet:
                    yield "".join(bullet).rstrip("\r\n")
                bullet, indent = [], None
            fence = marker[1]
            continue
        heading = HEADING.match(content)
        if heading:
            if bullet:
                yield "".join(bullet).rstrip("\r\n")
            bullet, indent = [], None
            level = len(heading[1])
            while sections and sections[-1][0] >= level:
                sections.pop()
            sections.append((level, any(word in (heading[2] or "").lower()
                                        for word in FINDING_HEADINGS)))
            continue
        if not any(finding for _, finding in sections):
            continue
        item = BULLET.match(content)
        if item and (indent is None or len(item[1]) <= indent):
            if bullet:
                yield "".join(bullet).rstrip("\r\n")
            indent = len(item[1])
            bullet = [line[item.start(2):]] if item[2].strip() else []
        elif indent is not None and content.strip() and len(content) - len(content.lstrip(" ")) > indent:
            bullet.append(line)
        elif bullet and not content.strip():
            bullet.append(line)
        elif indent is not None:
            if bullet:
                yield "".join(bullet).rstrip("\r\n")
            bullet, indent = [], None
    if bullet:
        yield "".join(bullet).rstrip("\r\n")


def extract_handoff_findings(text: str | bytes, source_path: str) -> list[dict]:
    """Return ordered candidate records without accessing the source identity.

    Bytes are decoded strictly as UTF-8; strings are hashed as UTF-8 without
    newline or Unicode normalization. Prefer bytes when byte provenance matters.
    Issue evidence is local to each bullet: exactly one distinct reference is
    ``present``; absent or competing references yield null with ``missing`` or
    ``ambiguous``. Document headings and filenames never supply inferred issues.
    No review or promotion decision is implied by ``candidate`` status.
    """
    _validate_source(source_path)
    if not isinstance(text, (str, bytes)):
        raise TypeError("text must be a UTF-8 string or bytes")
    raw = text if isinstance(text, bytes) else text.encode("utf-8")
    body = raw.decode("utf-8")
    digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    records = []
    for summary in _finding_bullets(body):
        refs = list(dict.fromkeys(ISSUE.findall(summary)))
        unique = len(refs) == 1  # Exactly one distinct reference: API contract above.
        records.append({
            "source_path": source_path,
            "source_kind": "handoff",
            "source_sha": digest,
            "issue_ref": refs[0] if unique else None,
            "issue_ref_status": "present" if unique else "ambiguous" if refs else "missing",
            "finding_summary": summary,
            "status": "candidate",
        })
    return records
