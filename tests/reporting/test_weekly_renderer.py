"""Literal publication examples and adversarial checks for issue #2154.

Expected strings are hand-authored layout examples, never renderer output.
"""

from copy import deepcopy
from html.parser import HTMLParser
import builtins
import io
import os

import pytest

import weekly_renderer as renderer


# Independent source: issue #2154, Scope, in the listed publication order.
SECTION_TABLE = (
    ("ecosystem_health", "Ecosystem health"),
    ("machine_readiness", "Machine readiness"),
    ("settings_routing", "Settings/routing"),
    ("freshness", "Freshness"),
    ("accessibility", "Accessibility"),
    ("follow_on_issues", "Follow-on issues"),
)
METADATA = {"title": "Weekly review", "run_reference": "sample"}
EXAMPLE = [
    {
        "key": "ecosystem_health",
        "status": "ok",
        "summary": "Checks passed",
        "items": [{"text": "Evidence", "artifact": "artifacts/checks.json"}],
    },
    {
        "key": "freshness",
        "status": "warning",
        "summary": "Refresh required",
        "items": [],
    },
]

# Independently specified examples: only supplied, nonempty sections appear.
GOLDEN_MARKDOWN = """# Weekly review

Run: sample

## Ecosystem health

Status: OK

Checks passed

- [Evidence](artifacts/checks.json)

## Freshness

Status: Warning

> [!WARNING]
> Refresh required
"""
GOLDEN_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Weekly review</title>
</head>
<body>
<header>
<h1>Weekly review</h1>
<p>Run: sample</p>
</header>
<main>
<section id="ecosystem_health">
<h2>Ecosystem health</h2>
<p class="status ok">Status: OK</p>
<p>Checks passed</p>
<ul>
<li><a href="artifacts/checks.json">Evidence</a></li>
</ul>
</section>
<section id="freshness">
<h2>Freshness</h2>
<p class="status warning">Status: Warning</p>
<aside class="callout warning" role="note"><strong>Warning</strong>: Refresh required</aside>
</section>
</main>
</body>
</html>
"""


class Structure(HTMLParser):
    """Inspect elements without opening a browser or resolving links."""

    def __init__(self, page):
        super().__init__()
        self.elements = []
        self.text = []
        self.feed(page)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


def test_section_order_and_status_callouts():
    statuses = ("ok", "warning", "error", "unknown", "ok", "warning")
    sections = [
        {"key": key, "status": status, "summary": heading, "items": []}
        for (key, heading), status in zip(SECTION_TABLE, statuses, strict=True)
    ]
    markdown = renderer.render_markdown(METADATA, list(reversed(sections)))
    page = renderer.render_html(METADATA, list(reversed(sections)))
    assert [line for line in markdown.splitlines() if line.startswith("## ")] == [
        f"## {heading}" for _, heading in SECTION_TABLE
    ]
    structure = Structure(page)
    assert [attrs["id"] for tag, attrs in structure.elements if tag == "section"] == [
        key for key, _ in SECTION_TABLE
    ]
    assert [attrs for tag, attrs in structure.elements if tag == "aside"] == [
        {"class": "callout warning", "role": "note"},
        {"class": "callout error", "role": "note"},
        {"class": "callout warning", "role": "note"},
    ]
    assert "> [!WARNING]\n> Machine readiness" in markdown
    assert "> [!CAUTION]\n> Settings&#47;routing" in markdown
    for label in ("OK", "Warning", "Error", "Unknown"):
        assert f"Status: {label}" in markdown
        assert f"Status: {label}" in page


def test_markdown_and_html_golden_outputs():
    assert renderer.render_markdown(METADATA, EXAMPLE) == GOLDEN_MARKDOWN
    assert renderer.render_html(METADATA, EXAMPLE) == GOLDEN_HTML


def test_hostile_text_is_escaped():
    hostile = (
        '<script>bad()</script> & "quoted" [open](javascript:bad) '
        '![image](x) `code` *bold* _under_ \\escape\n## injected\r\n- bullet'
    )
    metadata = {"title": hostile, "run_reference": hostile}
    sections = [{
        "key": "ecosystem_health", "status": "warning", "summary": hostile,
        "items": [{"text": hostile, "artifact": "artifacts/checks.json"}],
    }]
    markdown = renderer.render_markdown(metadata, sections)
    page = renderer.render_html(metadata, sections)
    structure = Structure(page)
    assert not {"script", "img", "iframe", "style"}.intersection(
        tag for tag, _ in structure.elements
    )
    assert [attrs for tag, attrs in structure.elements if tag == "a"] == [
        {"href": "artifacts/checks.json"}
    ]
    assert hostile in "".join(structure.text)
    assert "&lt;script&gt;bad()&lt;/script&gt; &amp; &quot;quoted&quot;" in page
    for literal in (
        "&#60;script&#62;", "&#38;", "&#34;quoted&#34;", "&#91;open&#93;",
        "&#96;code&#96;", "&#42;bold&#42;", "&#95;under&#95;", "&#92;escape",
        "&#10;&#35;&#35; injected&#13;&#10;&#45; bullet",
    ):
        assert literal in markdown
    assert "<script>" not in markdown
    assert "[open](javascript:" not in markdown
    assert "\n## injected" not in markdown


@pytest.mark.parametrize("render", [renderer.render_markdown, renderer.render_html])
@pytest.mark.parametrize("link", [
    "", "/absolute.json", "//example.invalid/asset", "../escape.json",
    "artifacts/../../escape.json", "artifacts/../escape.json", ".", "..",
    "artifacts/.", "artifacts/..", "./checks.json", "artifacts//checks.json",
    "artifacts/", "C:/checks.json", "C:\\checks.json", "\\\\server\\checks.json",
    "https://example.invalid/checks.json", "javascript:bad()", "data:text/html,bad",
    "%2e%2e/escape.json", "artifacts/%252e%252e/checks.json", "artifacts%2fchecks.json",
    "artifacts/%5cchecks.json", "checks.json?next=../escape", "checks.json#anchor",
    'checks".json', "checks).json", "checks<.json", "checks&.json",
    "checks\n.json", "checks\x00.json", " checks.json", "checks .json",
])
def test_absolute_or_traversing_links_are_rejected(render, link):
    sections = deepcopy(EXAMPLE)
    sections[0]["items"][0]["artifact"] = link
    with pytest.raises(ValueError, match="relative artifact"):
        render(METADATA, sections)


@pytest.mark.parametrize("render", [renderer.render_markdown, renderer.render_html])
def test_runtime_absolute_path_is_rejected(render, tmp_path):
    sections = deepcopy(EXAMPLE)
    sections[0]["items"][0]["artifact"] = str(tmp_path / "checks.json")
    with pytest.raises(ValueError, match="relative artifact"):
        render(METADATA, sections)


@pytest.mark.parametrize("link", ["checks.json", "artifacts/checks-v_next.json", "a/b.txt"])
def test_relative_artifacts_and_plain_items_preserve_order(link):
    sections = [{
        "key": "accessibility", "status": "ok", "summary": "",
        "items": [{"text": "Linked", "artifact": link}, {"text": "Plain"}],
    }]
    assert f"- [Linked]({link})\n- Plain\n" in renderer.render_markdown(METADATA, sections)
    page = renderer.render_html(METADATA, sections)
    assert f'<li><a href="{link}">Linked</a></li>\n<li>Plain</li>' in page


def test_optional_empty_sections_and_missing_status():
    sections = [{"key": "freshness", "status": "ok", "summary": "", "items": []}]
    assert "## " not in renderer.render_markdown(METADATA, sections)
    assert "<section " not in renderer.render_html(METADATA, sections)
    markdown = renderer.render_markdown(METADATA, sections, include_empty=True)
    page = renderer.render_html(METADATA, sections, include_empty=True)
    assert "## Freshness\n\nStatus: OK\n\nNo entries." in markdown
    assert "## Ecosystem health\n\nStatus: Unknown\n\nNo entries." in markdown
    assert [attrs["id"] for tag, attrs in Structure(page).elements if tag == "section"] == [
        key for key, _ in SECTION_TABLE
    ]
    assert '<p class="status unknown">Status: Unknown</p>\n<p>No entries.</p>' in page


@pytest.mark.parametrize("status, marker", [("warning", "WARNING"), ("error", "CAUTION")])
def test_empty_problem_sections_keep_their_callout(status, marker):
    sections = [{"key": "accessibility", "status": status, "summary": "", "items": []}]
    assert f"> [!{marker}]\n> No entries." in renderer.render_markdown(METADATA, sections)
    assert f'<aside class="callout {status}" role="note">' in renderer.render_html(
        METADATA, sections
    )


def test_repeated_rendering_is_pure_and_writes_no_files(monkeypatch, tmp_path):
    metadata, sections = deepcopy(METADATA), deepcopy(EXAMPLE)
    original = deepcopy((metadata, sections))
    monkeypatch.chdir(tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("Rendering attempted file access")

    with monkeypatch.context() as no_files:
        no_files.setattr(builtins, "open", forbidden)
        no_files.setattr(io, "open", forbidden)
        no_files.setattr(os, "open", forbidden)
        assert renderer.render_markdown(metadata, sections) == GOLDEN_MARKDOWN
        assert renderer.render_markdown(metadata, sections) == GOLDEN_MARKDOWN
        assert renderer.render_html(metadata, sections) == GOLDEN_HTML
        assert renderer.render_html(metadata, sections) == GOLDEN_HTML
    assert (metadata, sections) == original
    assert not list(tmp_path.iterdir())
