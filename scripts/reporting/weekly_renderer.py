"""Pure Markdown/HTML publication layout for weekly reviews (issue #2154).

Internal normalized input, independent of any upstream artifact schema::

    metadata = {"title": "Weekly review", "run_reference": "sample"}
    sections = [{
        "key": "ecosystem_health", "status": "ok", "summary": "Checks passed",
        "items": [{"text": "Evidence", "artifact": "artifacts/checks.json"}],
    }]

Metadata values, summaries and item text are plain strings, never markup.
The run reference is display text, not a URL. Section keys are unique members
of SECTION_ORDER; status is ok, warning, error or unknown. Summary and items
are required but may be empty. Item artifact is optional. Input shape, keys,
uniqueness and status validation belong upstream; this module is not a validator.

Both renderers use the order in issue #2154, preserving item order. By default,
absent sections and empty ok/unknown sections are omitted. Warning/error sections
remain visible even without content. With include_empty=True all sections appear;
absent sections have unknown status, never an inferred healthy status.

Artifact links are checked at the rendering boundary: only nonempty relative
paths with ASCII letters, digits, dots, underscores, hyphens and slash separators
are accepted. Empty, dot and parent segments are rejected, as are absolute paths,
schemes, backslashes, percent escapes, query strings and fragments. Resolution,
existence, symlink containment and publication authorization belong to the caller.

render_markdown and render_html return strings suitable for summary.md and
summary.html. Neither reads nor writes files, mutates inputs or consults clocks.
Markdown text uses numeric character references for ASCII punctuation and line
breaks so supplied content cannot create Markdown constructs or raw HTML. HTML
text uses standard entity escaping. Generated headings, status labels and callout
markers are fixed presentation text. HTML is a standalone semantic document with
normal document flow, a viewport declaration and no scripts or remote assets.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from html import escape
import re
from string import punctuation
from typing import Literal, NotRequired, TypedDict


class Metadata(TypedDict):
    title: str
    run_reference: str


class Item(TypedDict):
    text: str
    artifact: NotRequired[str]


class Section(TypedDict):
    key: str
    status: Literal["ok", "warning", "error", "unknown"]
    summary: str
    items: Sequence[Item]


# Source: issue #2154, Scope, ordered publication section list.
SECTION_ORDER = (
    ("ecosystem_health", "Ecosystem health"),
    ("machine_readiness", "Machine readiness"),
    ("settings_routing", "Settings/routing"),
    ("freshness", "Freshness"),
    ("accessibility", "Accessibility"),
    ("follow_on_issues", "Follow-on issues"),
)
_STATUS_LABELS = {"ok": "OK", "warning": "Warning", "error": "Error", "unknown": "Unknown"}
_MARKDOWN_CALLOUTS = {"warning": "WARNING", "error": "CAUTION"}
_PATH_CHARACTERS = re.compile(r"[A-Za-z0-9._/-]+")


def _markdown_text(text: str) -> str:
    return "".join(
        f"&#{ord(char)};" if char in punctuation or char in "\r\n\t" else char
        for char in text
    )


def _artifact_link(path: str) -> str:
    if not _PATH_CHARACTERS.fullmatch(path) or any(
        segment in ("", ".", "..") for segment in path.split("/")
    ):
        raise ValueError("Expected a normalized relative artifact path")
    return path


def _ordered_sections(sections: Sequence[Section], include_empty: bool):
    by_key = {section["key"]: section for section in sections}
    for key, title in SECTION_ORDER:
        section = by_key.get(key)
        if section is None:
            if not include_empty:
                continue
            section = {"key": key, "status": "unknown", "summary": "", "items": []}
        if (
            include_empty
            or section["summary"]
            or section["items"]
            or section["status"] in _MARKDOWN_CALLOUTS
        ):
            yield key, title, section


def _summary(section: Section, escape_text: Callable[[str], str]) -> str:
    if section["summary"]:
        return escape_text(section["summary"])
    if not section["items"]:
        return "No entries."
    if section["status"] in _MARKDOWN_CALLOUTS:
        return "No summary provided."
    return ""


def render_markdown(
    metadata: Metadata, sections: Sequence[Section], *, include_empty: bool = False
) -> str:
    """Return escaped Markdown; invalid artifact paths raise ValueError."""
    blocks = [
        f"# {_markdown_text(metadata['title'])}",
        f"Run: {_markdown_text(metadata['run_reference'])}",
    ]
    for _, title, section in _ordered_sections(sections, include_empty):
        status = section["status"]
        blocks.extend((f"## {title}", f"Status: {_STATUS_LABELS[status]}"))
        summary = _summary(section, _markdown_text)
        if status in _MARKDOWN_CALLOUTS:
            blocks.append(f"> [!{_MARKDOWN_CALLOUTS[status]}]\n> {summary}")
        elif summary:
            blocks.append(summary)
        items = []
        for item in section["items"]:
            text = _markdown_text(item["text"])
            if "artifact" in item:
                text = f"[{text}]({_artifact_link(item['artifact'])})"
            items.append(f"- {text}")
        if items:
            blocks.append("\n".join(items))
    return "\n\n".join(blocks) + "\n"


def render_html(
    metadata: Metadata, sections: Sequence[Section], *, include_empty: bool = False
) -> str:
    """Return standalone escaped HTML; invalid artifact paths raise ValueError."""
    title = escape(metadata["title"])
    lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{title}</title>",
        "</head>",
        "<body>",
        "<header>",
        f"<h1>{title}</h1>",
        f"<p>Run: {escape(metadata['run_reference'])}</p>",
        "</header>",
        "<main>",
    ]
    for key, heading, section in _ordered_sections(sections, include_empty):
        status = section["status"]
        label = _STATUS_LABELS[status]
        lines.extend((
            f'<section id="{key}">',
            f"<h2>{heading}</h2>",
            f'<p class="status {status}">Status: {label}</p>',
        ))
        summary = _summary(section, escape)
        if status in _MARKDOWN_CALLOUTS:
            lines.append(
                f'<aside class="callout {status}" role="note">'
                f"<strong>{label}</strong>: {summary}</aside>"
            )
        elif summary:
            lines.append(f"<p>{summary}</p>")
        if section["items"]:
            lines.append("<ul>")
            for item in section["items"]:
                text = escape(item["text"])
                if "artifact" in item:
                    path = escape(_artifact_link(item["artifact"]))
                    text = f'<a href="{path}">{text}</a>'
                lines.append(f"<li>{text}</li>")
            lines.append("</ul>")
        lines.append("</section>")
    lines.extend(("</main>", "</body>", "</html>"))
    return "\n".join(lines) + "\n"
