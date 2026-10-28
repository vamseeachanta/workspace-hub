"""Synthetic navigation contract; no renderer, publication data or network.

The literal examples below are the source for every expected edge and outcome.
Dates are arbitrary labels for successive runs, not measured values. Hand checks:
first run: latest -> dated -> latest, both -> history, history -> both;
repeat run: latest -> newer -> older, older -> newer, history -> every page.
No optional findings/chart section is present in the first-run example, so no
link to either section is required. Negative controls each break a named edge.
"""

from pathlib import Path
import shutil
import socket
import stat
from types import SimpleNamespace

import pytest

from publication_navigation import check_bundle, main
from publication_navigation import _is_link


FIRST_RUN = {
    "latest.html": '''<!doctype html><html><body>
        <h1 id="summary">Latest</h1>
        <a href="runs/2026-01-01.html#summary">Dated run</a>
        <a href="history/index.html">History</a></body></html>''',
    "runs/2026-01-01.html": '''<html><body><h1 id="summary">Run</h1>
        <a href="../latest.html#summary">Latest</a>
        <a href="../history/index.html">History</a></body></html>''',
    "history/index.html": '''<html><body><h1>History</h1>
        <a href="../latest.html">Latest</a>
        <a href="../runs/2026-01-01.html#summary">Run</a></body></html>''',
}
REPEATED_RUN = {
    "latest.html": '''<html><body><h1 id="summary">Latest</h1>
        <a href="runs/2026-01-08.html#summary">Dated run</a>
        <a href="history/index.html">History</a></body></html>''',
    "runs/2026-01-01.html": '''<html><body><h1 id="summary">Older</h1>
        <a href="../latest.html#summary">Latest</a>
        <a href="2026-01-08.html#summary">Next</a>
        <a href="../history/index.html">History</a></body></html>''',
    "runs/2026-01-08.html": '''<html><body><h1 id="summary">Newer</h1>
        <a href="../latest.html#summary">Latest</a>
        <a href="2026-01-01.html#summary">Previous</a>
        <a href="../history/index.html">History</a></body></html>''',
    "history/index.html": '''<html><body><h1>History</h1>
        <a href="../latest.html">Latest</a>
        <a href="../runs/2026-01-08.html#summary">Newer</a>
        <a href="../runs/2026-01-01.html#summary">Older</a></body></html>''',
}


def write_bundle(root, pages):
    for name, content in pages.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
    return root


def test_first_run_navigation(tmp_path):
    """Hand check: all literal first-run edges resolve, no optional sections."""
    assert check_bundle(write_bundle(tmp_path, FIRST_RUN)) == []


def test_multiple_run_navigation(tmp_path):
    """Hand check: latest, both dated pages and history are mutually reachable."""
    assert check_bundle(write_bundle(tmp_path, REPEATED_RUN)) == []


@pytest.mark.parametrize("pages", [FIRST_RUN, REPEATED_RUN])
def test_relocated_bundle_has_same_result(tmp_path, pages):
    original = write_bundle(tmp_path / "original", pages)
    relocated = tmp_path / "nested" / "relocated"
    shutil.copytree(original, relocated)
    assert check_bundle(original) == check_bundle(relocated) == []


def test_broken_local_link_is_detected(tmp_path):
    root = write_bundle(tmp_path, FIRST_RUN)
    (root / "runs/2026-01-01.html").write_text(
        '<a href="../missing.html">Broken latest edge</a>', encoding="utf-8", newline="\n"
    )
    issues = check_bundle(root)
    assert any(i.source == "runs/2026-01-01.html" and
               i.target == "../missing.html" and i.reason == "missing-target"
               for i in issues)


@pytest.mark.parametrize("pages", [FIRST_RUN, REPEATED_RUN])
def test_each_navigation_edge_is_checked(tmp_path, pages):
    """Independent mutation: every literal href must yield its own diagnostic."""
    from html.parser import HTMLParser

    class Edges(HTMLParser):
        def __init__(self):
            super().__init__()
            self.targets = []

        def handle_starttag(self, tag, attrs):
            self.targets.extend(v for k, v in attrs if k == "href")

    for source, content in pages.items():
        parser = Edges()
        parser.feed(content)
        for target in parser.targets:
            broken = dict(pages)
            broken[source] = content.replace(target, "absent.html")
            root = write_bundle(tmp_path, broken)
            assert any(i.source == source and i.target == "absent.html" and
                       i.reason == "missing-target" for i in check_bundle(root))


@pytest.mark.parametrize("fragment, expected", [
    ("summary", []), ("Summary", ["missing-fragment"]),
    ("absent", ["missing-fragment"]), ("", []),
    ("r%C3%A9sum%C3%A9", []), ("old", []), ("a&amp;b", []),
])
def test_fragment_contract(tmp_path, fragment, expected):
    """Only summary, résumé, old (legacy name) and a&b exist; case matters."""
    root = write_bundle(tmp_path, {
        "index.html": f'<a href="page.HTML?view=brief#{fragment}">Page</a>',
        "page.HTML": '<h1 id="summary">S</h1><p id="résumé">R</p>'
                     '<a name="old"></a><p id="a&amp;b">A</p>',
    })
    assert [i.reason for i in check_bundle(root)] == expected


def test_self_directory_and_resource_links(tmp_path):
    """Self anchors, empty references, directory indexes and assets exist."""
    root = write_bundle(tmp_path, {
        "index.html": '<h1 id="summary">S</h1><a href="#summary">Self</a>'
                      '<a href="">Again</a><a href="history/">History</a>'
                      '<link href="style.css"><img src="plot.svg">',
        "history/index.html": '<a href="../index.html#summary">Latest</a>',
        "style.css": "body {}", "plot.svg": "<svg></svg>",
    })
    assert check_bundle(root) == []


@pytest.mark.parametrize("markup", [
    '<link href="absent.css">', '<img src="absent.svg">',
    '<iframe src="absent.html"></iframe>', '<area href="absent.html">',
])
def test_missing_resource_target(tmp_path, markup):
    assert [i.reason for i in check_bundle(write_bundle(
        tmp_path, {"index.html": markup}))] == ["missing-target"]


@pytest.mark.parametrize("attribute", ["href", "src"])
@pytest.mark.parametrize("target", [
    "page.html/", "page.html/#summary", "page.html%2F#summary",
    "page.html/?view=brief#summary", "page.html/.", "page.html/../page.html",
])
def test_regular_file_cannot_be_traversed_as_directory(tmp_path, attribute, target):
    """A file exists, but a slash after it requires a directory lookup."""
    root = write_bundle(tmp_path, {
        "index.html": f'<a {attribute}="{target}">Page</a>',
        "page.html": '<h1 id="summary">Page</h1>',
    })
    assert [i.reason for i in check_bundle(root)] == ["missing-target"]


@pytest.mark.parametrize("attribute", ["href", "src"])
def test_real_directory_with_fragment_is_valid(tmp_path, attribute):
    root = write_bundle(tmp_path, {
        "index.html": f'<a {attribute}="pages/?view=brief#summary">Page</a>',
        "pages/index.html": '<h1 id="summary">Page</h1>',
    })
    assert check_bundle(root) == []


@pytest.mark.parametrize("kind", ["root", "directory", "source", "target", "index"])
def test_junctions_are_rejected_without_reading(tmp_path, monkeypatch, kind):
    """Model the junction predicate without requiring a Windows filesystem."""
    root = write_bundle(tmp_path / "bundle", {
        "index.html": '<a href="pages/">Page</a>',
        "pages/index.html": '<h1>Page</h1>',
    })
    junction = {
        "root": root, "directory": root / "pages",
        "source": root / "index.html", "target": root / "asset",
        "index": root / "pages/index.html",
    }[kind]
    if kind == "target":
        write_bundle(root, {"index.html": '<a href="asset">Asset</a>', "asset": "data"})
    monkeypatch.setattr(Path, "is_junction", lambda path: path == junction, raising=False)
    read_text = Path.read_text

    def guarded_read(path, *args, **kwargs):
        assert path != junction, "Link was read"
        return read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded_read)
    assert any(i.reason in {"symlinked-root", "symlinked-target"}
               for i in check_bundle(root))


def test_reparse_point_is_rejected_without_junction_api(tmp_path, monkeypatch):
    """Older Python exposes Windows reparse attributes through lstat."""
    target = tmp_path / "alias"
    monkeypatch.delattr(Path, "is_junction", raising=False)
    monkeypatch.setattr(Path, "lstat", lambda path: SimpleNamespace(
        st_mode=stat.S_IFDIR, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT))
    assert _is_link(target)


@pytest.mark.parametrize("target, reason", [
    ("../outside.html", "escaped-target"),
    ("%2e%2e/outside.html", "escaped-target"),
    ("/outside.html", "absolute-target"),
    ("%2Foutside.html", "absolute-target"),
    ("file:outside.html", "unsupported-scheme"),
    ("javascript:void()", "unsupported-scheme"),
    ("data:text/html,hello", "unsupported-scheme"),
    ("C:/outside.html", "unsupported-scheme"),
    ("..\\outside.html", "invalid-target"),
    ("%00.html", "invalid-target"),
    ("pa%0Age.html", "invalid-target"),
])
def test_unsafe_target_is_rejected(tmp_path, target, reason):
    root = write_bundle(tmp_path / "bundle", {
        "index.html": f'<a href="{target}">Unsafe</a>',
    })
    (tmp_path / "outside.html").write_text("<h1>Outside</h1>", encoding="utf-8", newline="\n")
    assert [i.reason for i in check_bundle(root)] == [reason]


@pytest.mark.parametrize("external", [False, True])
@pytest.mark.parametrize("directory", [False, True])
def test_symlinked_targets_are_rejected(tmp_path, external, directory):
    root = write_bundle(tmp_path / "bundle", {"index.html": "<h1>Index</h1>"})
    dest = tmp_path / "outside" if external else root / "inside"
    write_bundle(dest, {"page.html": "<h1>Page</h1>"})
    link = root / "alias"
    link.symlink_to(dest if directory else dest / "page.html",
                    target_is_directory=directory)
    href = "alias/page.html" if directory else "alias"
    (root / "index.html").write_text(f'<a href="{href}">Alias</a>', encoding="utf-8", newline="\n")
    assert any(i.source == "index.html" and i.target == href and
               i.reason == "symlinked-target" for i in check_bundle(root))


def test_symlink_before_parent_component_is_rejected(tmp_path):
    root = write_bundle(tmp_path, {"index.html": '<a href="alias/../index.html">A</a>'})
    (root / "alias").symlink_to(root, target_is_directory=True)
    assert any(i.reason == "symlinked-target" and i.source == "index.html"
               for i in check_bundle(root))


def test_symlinked_html_source_is_not_read(tmp_path):
    root = write_bundle(tmp_path / "bundle", {"index.html": "<h1>Index</h1>"})
    outside = tmp_path / "outside.html"
    outside.write_text('<a href="missing.html">Outside</a>', encoding="utf-8", newline="\n")
    (root / "alias.html").symlink_to(outside)
    assert [i.reason for i in check_bundle(root)] == ["symlinked-target"]


@pytest.mark.parametrize("kind", ["absent", "file", "symlink", "empty"])
def test_invalid_bundle_root(tmp_path, kind):
    root = tmp_path / "bundle"
    if kind == "file":
        root.write_text("plain file", encoding="utf-8", newline="\n")
    elif kind == "symlink":
        real = write_bundle(tmp_path / "real", {"index.html": "<h1>Index</h1>"})
        root.symlink_to(real, target_is_directory=True)
    elif kind == "empty":
        root.mkdir()
    assert check_bundle(root)


def test_base_element_is_rejected(tmp_path):
    """A base element would change browser resolution; fail rather than guess."""
    root = write_bundle(tmp_path, {"index.html": '<base href="elsewhere/">'})
    assert [i.reason for i in check_bundle(root)] == ["base-element"]


def test_remote_links_are_never_fetched(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Network access attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    root = write_bundle(tmp_path, {"index.html":
        '<a href="https://example.invalid/missing#no">External</a>'
        '<a href="//example.invalid/missing">External</a>'
        '<a href="mailto:reader">Mail</a><a href="tel:help">Call</a>'})
    assert check_bundle(root) == []


def test_preserves_caller_files_and_metadata(tmp_path, monkeypatch):
    """Snapshot bytes, mode, size and modification time, including Git metadata.

    Access time is intentionally excluded: reading may update it on the caller's
    filesystem. The checker must not write content or modification metadata.
    """
    caller = write_bundle(tmp_path / "caller", {"notes.txt": "Keep", ".git/HEAD": "Keep"})
    root = write_bundle(tmp_path / "bundle", FIRST_RUN)
    monkeypatch.chdir(caller)
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        monkeypatch.setenv(key, str(caller))

    def snapshot():
        return {p.relative_to(tmp_path): (p.read_bytes(), p.stat().st_mode,
                                         p.stat().st_size, p.stat().st_mtime_ns)
                for p in tmp_path.rglob("*") if p.is_file()}

    before = snapshot()
    assert check_bundle(root) == []
    assert snapshot() == before


def test_invalid_html_encoding_is_reported(tmp_path):
    (tmp_path / "index.html").write_bytes(b"\xff")
    assert [i.reason for i in check_bundle(tmp_path)] == ["unreadable-html"]


def test_cli_reports_relative_diagnostics(tmp_path, capsys):
    root = write_bundle(tmp_path, {"index.html": '<a href="absent.html">A</a>'})
    # Exit conventions: success is zero; a detected violation is one.
    assert main([str(root)]) == 1
    output = capsys.readouterr().out
    assert "index.html" in output and "missing-target" in output
    assert str(root) not in output
    (root / "index.html").write_text("<h1>Valid</h1>", encoding="utf-8", newline="\n")
    assert main([str(root)]) == 0


def test_broken_result_is_relocatable(tmp_path):
    """A single missing history target gives the same relative diagnostic."""
    root = write_bundle(tmp_path / "original", {
        "index.html": '<a href="history/index.html">History</a>',
    })
    relocated = tmp_path / "relocated"
    shutil.copytree(root, relocated)
    original_issues = check_bundle(root)
    assert [i.reason for i in original_issues] == ["missing-target"]
    assert check_bundle(relocated) == original_issues


@pytest.mark.parametrize("target", ["page%xx.html", "page.html#%FF", "http://["])
def test_malformed_url_is_reported(tmp_path, target):
    root = write_bundle(tmp_path, {"index.html": f'<a href="{target}">A</a>'})
    assert [i.reason for i in check_bundle(root)] == ["invalid-target"]


def test_directory_index_fragment_and_htm_inventory(tmp_path):
    root = write_bundle(tmp_path, {
        "index.htm": '<a href="history/#summary">History</a>',
        "history/index.html": '<h1 id="summary">History</h1>',
    })
    assert check_bundle(root) == []
    (root / "history/index.html").write_text('<h1 id="other">History</h1>', encoding="utf-8", newline="\n")
    assert [i.reason for i in check_bundle(root)] == ["missing-fragment"]


def test_missing_directory_index_is_reported(tmp_path):
    root = write_bundle(tmp_path, {"index.html": '<a href="history/">History</a>'})
    (root / "history").mkdir()
    assert [i.reason for i in check_bundle(root)] == ["missing-target"]


def test_asset_fragment_is_not_silently_accepted(tmp_path):
    root = write_bundle(tmp_path, {
        "index.html": '<a href="plot.svg#missing">Plot</a>',
        "plot.svg": "<svg></svg>",
    })
    assert [i.reason for i in check_bundle(root)] == ["uncheckable-fragment"]


def test_symlinks_never_read_outside_bundle(tmp_path, monkeypatch):
    root = write_bundle(tmp_path / "bundle", {
        "index.html": '<a href="alias/page.html">Outside</a>',
    })
    outside = write_bundle(tmp_path / "outside", {
        "page.html": '<a href="missing.html">Do not inspect</a>',
    })
    (root / "alias").symlink_to(outside, target_is_directory=True)
    (root / "alias.html").symlink_to(outside / "page.html")
    read_text = Path.read_text

    def guarded_read(path, *args, **kwargs):
        assert path == root / "index.html", "Unexpected file read"
        return read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded_read)
    assert check_bundle(root)


def test_unreadable_html_is_reported(tmp_path, monkeypatch):
    root = write_bundle(tmp_path, {"index.html": "<h1>Index</h1>"})

    def denied(*args, **kwargs):
        raise PermissionError("Synthetic read denial")

    monkeypatch.setattr(Path, "read_text", denied)
    assert [i.reason for i in check_bundle(root)] == ["unreadable-html"]
