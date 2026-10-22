"""Source evidence and isolated static builds for initiative #3607.

The SHA-256 oracle is RFC 6234 (2011), section 8.5, SHA256 TEST1:
the three ASCII bytes ``abc`` with no newline. Output inventories below are
enumerated by hand from each fixture's explicit allowlist, never from a scan.
"""

import importlib.util
import json
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_pages.py"
# RFC 6234 (2011), section 8.5, SHA256 TEST1, concatenated hex words.
ABC_SHA256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


class Elements(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


@pytest.fixture
def builder(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("pages_evidence", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = tmp_path / "source"
    root.mkdir()
    (root / "guide.md").write_bytes(b"abc")
    (root / "standalone.html").write_bytes(b"<!doctype html><p>Frozen proof</p>\r\n")
    (root / "unlisted.md").write_text("Not approved for publication", encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", root)
    monkeypatch.setattr(module, "PAGES", {"guide": ("guide.md", "Guide")})
    monkeypatch.setattr(module, "HTML_PAGES", {"proof": ("standalone.html", "Proof")})
    monkeypatch.setattr(module, "SESSIONS_SRC", root / "reports")
    return module


def shell(builder, source=b"abc", path="guide.md"):
    return builder.shell(
        "Guide", "<h1>Guide</h1>", source_path=path, source_bytes=source
    )


def test_source_evidence_uses_published_digest(builder):
    """RFC 6234 section 8.5: SHA256(TEST1='abc') equals ABC_SHA256."""
    page = shell(builder)
    assert ABC_SHA256 in page
    assert "guide.md" in page
    assert "Source and data limits" in page
    assert "static documentation snapshot" in page
    assert "live algorithm results" in page


def test_digest_tracks_exact_source_bytes(builder):
    """A newline changes the input; the published abc digest must disappear."""
    assert ABC_SHA256 not in shell(builder, source=b"abc\n")
    assert ABC_SHA256 not in shell(builder, source=b"abc\r\n")


def test_source_label_is_escaped(builder):
    page = shell(builder, path='docs/<proof>&".md')
    assert 'docs/&lt;proof&gt;&amp;&quot;.md' in page
    assert "<proof>" not in page


def test_skip_link_precedes_navigation_and_targets_main(builder):
    """W3C WCAG 2.2 Technique G1: first focusable link skips to main."""
    tags = Elements(shell(builder)).tags
    links = [attrs for tag, attrs in tags if tag == "a"]
    assert links[0]["href"] == "#main-content"
    assert links[0]["class"] == "skip-link"
    assert ("main", {"id": "main-content", "tabindex": "-1"}) in tags
    assert any(tag == "nav" and attrs.get("aria-label") for tag, attrs in tags)
    assert sum(attrs.get("id") == "main-content" for _, attrs in tags) == 1


def test_skip_link_has_visible_focus_style(builder):
    """Technique G1 requires the link to be visible when it has focus."""
    assert ".skip-link:focus" in builder.STYLE
    assert ".source-evidence" in builder.STYLE
    assert "overflow-wrap:anywhere" in builder.STYLE


def test_build_writes_only_enumerated_outputs(builder, tmp_path):
    """Hand inventory: guide + proof + the shared stylesheet, no other files."""
    output = tmp_path / "output"
    builder.build(output_dir=output)
    actual = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()}
    assert actual == {"guide.html", "proof.html", "assets/style.css"}
    page = (output / "guide.html").read_text(encoding="utf-8")
    assert ABC_SHA256 in page
    assert "Not approved for publication" not in page
    assert not (builder.ROOT / "public").exists()


def test_build_preserves_standalone_bytes(builder, tmp_path):
    """Standalone HTML is frozen evidence, including its CRLF bytes."""
    output = tmp_path / "output"
    builder.build(output_dir=output)
    assert (output / "proof.html").read_bytes() == b"<!doctype html><p>Frozen proof</p>\r\n"


def test_build_routes_manifest_outputs_to_the_same_destination(builder, tmp_path):
    """Hand inventory: manifest index + named page; unlisted HTML stays private."""
    source = builder.SESSIONS_SRC
    source.mkdir()
    index = b"<!doctype html><p>Index</p>\r\n"
    proof = b"<!doctype html><p>Recorded proof</p>\r\n"
    (source / "index.html").write_bytes(index)
    (source / "proof.html").write_bytes(proof)
    (source / "unlisted.html").write_bytes(b"Not approved for publication")
    (source / "manifest.json").write_text(
        json.dumps([{"file": "proof.html"}]), encoding="utf-8"
    )
    output = tmp_path / "output"
    builder.build(output_dir=output)
    assert (output / "sessions" / "index.html").read_bytes() == index
    assert (output / "sessions" / "proof.html").read_bytes() == proof
    assert not (output / "sessions" / "unlisted.html").exists()


def test_build_is_repeatable_and_does_not_modify_sources(builder, tmp_path):
    before = {p: p.read_bytes() for p in builder.ROOT.rglob("*") if p.is_file()}
    outputs = [tmp_path / "first", tmp_path / "second"]
    for output in outputs:
        builder.build(output_dir=output)
    snapshots = [
        {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
        for output in outputs
    ]
    assert snapshots[0] == snapshots[1]
    assert {p: p.read_bytes() for p in builder.ROOT.rglob("*") if p.is_file()} == before


def test_default_output_remains_compatible(builder, tmp_path, monkeypatch):
    output = tmp_path / "default"
    monkeypatch.setattr(builder, "PUBLIC", output)
    monkeypatch.setattr(builder, "ASSETS", output / "assets")
    builder.build()
    assert (output / "guide.html").exists()
    assert (output / "assets/style.css").read_text(encoding="utf-8") == builder.STYLE


def test_cli_can_build_outside_the_source_tree(tmp_path):
    # Run a disposable copy: even a regression that ignores the CLI argument
    # must never write generated files into the real checkout.
    root = tmp_path / "repo"
    script = root / "scripts" / "build_pages.py"
    script.parent.mkdir(parents=True)
    script.write_bytes(SCRIPT.read_bytes())
    brand = root / "docs" / "assets" / "brand.css"
    brand.parent.mkdir(parents=True)
    brand.write_bytes((ROOT / "docs" / "assets" / "brand.css").read_bytes())
    (root / "README.md").write_bytes(b"abc")
    output = tmp_path / "isolated"
    result = subprocess.run(
        [sys.executable, str(script), "--output-dir", str(output)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (output / "index.html").exists()
    assert (output / "assets/style.css").read_bytes() == (
        ROOT / "docs" / "assets" / "brand.css"
    ).read_bytes()
    assert "README.md" in (output / "index.html").read_text(encoding="utf-8")
    assert not (root / "public").exists()
