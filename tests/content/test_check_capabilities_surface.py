"""Structural contract from issue #3494 and the merged redirect source pages.

Expected outcomes are independent inspections: each accepted page has one
canonical URL, one immediate refresh to it, a readable matching link, and no
technical overview. The zero delay is the literal refresh in the published
repository stubs, rather than an engineering acceptance coefficient.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "scripts/content/check_capabilities_surface.py"
)
TARGET = "https://www.aceengineer.com/capabilities/"
# Source: issue #3494, merged repository redirect stubs (July 2026).
STUB = f"""<!doctype html><html lang="en"><head>
<title>Capabilities have moved</title>
<link rel="canonical" href="{TARGET}">
<meta name="robots" content="noindex, follow">
<meta http-equiv="refresh" content="0; url={TARGET}">
</head><body><main><p>Capabilities now live at
<a href="{TARGET}">aceengineer.com/capabilities</a>.</p>
</main></body></html>"""


@pytest.fixture
def checker():
    spec = importlib.util.spec_from_file_location("capabilities_surface", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_redirect_contract(checker):
    assert checker.check_redirect(STUB) == []


@pytest.mark.parametrize(
    ("old", "new", "rule"),
    [
        ('rel="canonical"', 'rel="alternate"', "canonical"),
        (f'href="{TARGET}"', 'href="https://example.org/"', "canonical"),
        ('content="0; url=', 'content="5; url=', "refresh"),
        ('http-equiv="refresh"', 'http-equiv="other"', "refresh"),
        (f'url={TARGET}', 'url=https://example.org/', "refresh"),
        ('content="noindex, follow"', 'content="index, follow"', "robots"),
        ('content="noindex, follow"', 'content="noindex, nofollow"', "robots"),
        ("aceengineer.com/capabilities</a>", "</a>", "visible-link"),
        ("<a href=", "<a hidden href=", "visible-link"),
        ("<main>", '<main aria-hidden="true">', "visible-link"),
        ("<main>", '<main style="display: none">', "visible-link"),
        ("<main>", '<main style="visibility:hidden">', "visible-link"),
        ("<main>", "<main><h1>Engineering portfolio</h1>", "landing-content"),
        ("<main>", "<main><table><tr><td>Results</td></tr></table>", "landing-content"),
        ("</head>", '<script src="copy.js"></script></head>', "landing-content"),
        ("</head>", f'<link rel="canonical" href="{TARGET}"></head>', "canonical"),
        ("</head>", f'<meta http-equiv="refresh" content="0; url={TARGET}"></head>', "refresh"),
        ("</head>", '<meta name="robots" content="index"></head>', "robots"),
    ],
)
def test_contract_mutations(checker, old, new, rule):
    assert rule in checker.check_redirect(STUB.replace(old, new))


def test_comment_cannot_supply_contract(checker):
    assert set(checker.check_redirect(f"<!-- {STUB} -->")) >= {
        "canonical", "refresh", "robots", "visible-link"
    }


@pytest.mark.parametrize("old,new", [
    ('rel="canonical"', 'rel="alternate" rel="canonical"'),
    ('content="0; url=', 'content="bad" content="0; url='),
    ('<a href=', '<a href="https://example.org/" href='),
])
def test_ambiguous_duplicate_attributes_are_rejected(checker, old, new):
    # Hand inspection: duplicate attributes provide conflicting routing evidence.
    # Decline qualification rather than choosing a parser-specific winner.
    assert "markup" in checker.check_redirect(STUB.replace(old, new))


def test_head_link_is_not_visible_fallback(checker):
    source = STUB.replace("<main>", "<main hidden>")
    source = source.replace("</head>", f'<a href="{TARGET}">Moved</a></head>')
    assert "visible-link" in checker.check_redirect(source)


def test_metadata_requires_head(checker):
    source = STUB.replace("<head>", "<body>").replace("</head><body>", "")
    assert set(checker.check_redirect(source)) >= {"canonical", "refresh", "robots"}


def test_metadata_case_and_whitespace(checker):
    source = STUB.replace('rel="canonical"', 'rel="CANONICAL"')
    source = source.replace('http-equiv="refresh"', 'HTTP-EQUIV="Refresh"')
    source = source.replace("0; url=", "0 ; URL = ")
    source = source.replace("noindex, follow", "NOINDEX, FOLLOW")
    assert checker.check_redirect(source) == []


def test_css_and_comments_are_not_visible_text(checker):
    source = STUB.replace("aceengineer.com/capabilities</a>", "<!-- moved --></a>")
    source = source.replace("</head>", "<style>a::after {content:'Moved'}</style></head>")
    assert "visible-link" in checker.check_redirect(source)


@pytest.mark.parametrize("repo", ["digitalmodel", "worldenergydata"])
@pytest.mark.parametrize("suffix", ["", "/", "/index.html", "/?source=nav", "/#overview"])
def test_old_landing_links(checker, repo, suffix):
    # Synthetic public URL: expected by path inspection, independent of parser.
    url = f"https://example.github.io/{repo}/capabilities{suffix}"
    assert checker.old_landing_links(f'[Capabilities]({url})') == [url]


@pytest.mark.parametrize("suffix", ["/insights.html", "/pdf/brief.pdf", "/api/", "/explorer/"])
def test_preserve_deep_technical_links(checker, suffix):
    url = f"https://example.github.io/worldenergydata/capabilities{suffix}"
    assert checker.old_landing_links(f'<a href="{url}">Technical report</a>') == []


def test_unrelated_and_canonical_links(checker):
    text = f"{TARGET} https://example.org/digitalmodel/capabilities/"
    text += " https://example.github.io/another-repository/capabilities/"
    assert checker.old_landing_links(text) == []


def test_landing_link_with_html_entity_query(checker):
    url = "https://example.github.io/digitalmodel/capabilities/?a=x&amp;b=y"
    assert checker.old_landing_links(f'<a href="{url}">Capabilities</a>') == [
        url.replace("&amp;", "&")
    ]


def make_sources(root):
    for repo, relative in {
        "digitalmodel": "docs/api/capabilities/index.html",
        "worldenergydata": "reports/capabilities/index.html",
    }.items():
        path = root / repo / relative
        path.parent.mkdir(parents=True)
        path.write_text(STUB, encoding="utf-8")


def run_cli(root, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--digitalmodel-root", str(root / "digitalmodel"),
         "--worldenergydata-root", str(root / "worldenergydata"), *args],
        capture_output=True, text=True, check=False,
    )


def test_cli_worked_example_and_read_only(tmp_path):
    """Hand inspection: two valid stubs => two PASS entries and exit success.

    A deep report remains present and byte-identical. No source rewriting,
    generation, checkout discovery or network request is needed for this result.
    """
    make_sources(tmp_path)
    deep = tmp_path / "worldenergydata/reports/capabilities/insights.html"
    deep.write_text("<h1>Technical analysis</h1>", encoding="utf-8")
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    result = run_cli(tmp_path)
    assert result.returncode == 0
    rows = json.loads(result.stdout)
    assert [(r["surface"], r["status"]) for r in rows] == [
        ("digitalmodel", "PASS"), ("worldenergydata", "PASS")
    ]
    assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before
    assert str(tmp_path) not in result.stdout


def test_cli_missing_source_is_not_evaluated(tmp_path):
    result = run_cli(tmp_path)
    assert result.returncode != 0
    assert {r["status"] for r in json.loads(result.stdout)} == {"NOT_EVALUATED"}
    assert str(tmp_path) not in result.stdout + result.stderr


def test_cli_drift_and_missing_link_input(tmp_path):
    make_sources(tmp_path)
    path = tmp_path / "digitalmodel/docs/api/capabilities/index.html"
    path.write_text("<h1>Old capabilities</h1>", encoding="utf-8")
    result = run_cli(tmp_path, "--links", str(tmp_path / "missing.md"))
    assert result.returncode != 0
    rows = json.loads(result.stdout)
    assert rows[0]["status"] == "FAIL"
    assert rows[-1]["status"] == "NOT_EVALUATED"
    assert str(tmp_path) not in result.stdout + result.stderr


def test_cli_link_file_reports_line_without_content(tmp_path):
    make_sources(tmp_path)
    path = tmp_path / "links.md"
    path.write_text("Navigation\n[Capabilities](https://example.github.io/digitalmodel/capabilities/)\n")
    result = run_cli(tmp_path, "--links", str(path))
    assert result.returncode != 0
    row = json.loads(result.stdout)[-1]
    assert row["status"] == "FAIL"
    assert row["lines"] == [2]  # Independent line count in the literal above.
    assert "github.io" not in result.stdout


def test_cli_decoding_failure_is_not_evaluated(tmp_path):
    make_sources(tmp_path)
    path = tmp_path / "worldenergydata/reports/capabilities/index.html"
    path.write_bytes(b"\xff")
    result = run_cli(tmp_path)
    assert result.returncode != 0
    assert json.loads(result.stdout)[1]["status"] == "NOT_EVALUATED"
    assert "Traceback" not in result.stderr


def test_published_worklog_links_to_canonical_surface(checker):
    path = SCRIPT.parents[2] / "docs/reports/casing-design-worklog.html"
    source = path.read_text(encoding="utf-8")
    assert checker.old_landing_links(source) == []
    assert source.count(f'href="{TARGET}"') == 2
    # The deep technical explorer remains at its existing destination.
    assert "/digitalmodel/well/casing-design-explorer.html" in source
