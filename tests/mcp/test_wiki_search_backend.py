"""Synthetic lexical search contract; no corpus or service is consulted.

Hand calculations beside each case are the source for expected numbers. Limits
are fixture choices measured in results or escaped characters, not tuning values.
The proposed API searches allowed_root/<domain>/wiki/**/*.md. Ranking is distinct
case-folded query tokens present, then total occurrences, then POSIX page path.
Repeated query tokens count once. Excerpts start at the first matched token and
are HTML escaped without splitting entities; the escaped length obeys the limit.
"""

from __future__ import annotations

import importlib.util
import os
import stat
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import pytest


# tests/mcp/file has the repository at parents[2]. Import without an MCP package.
MODULE = Path(__file__).resolve().parents[2] / "scripts/mcp/doc_intel_server/wiki_search.py"
SPEC = importlib.util.spec_from_file_location("wiki_search_backend", MODULE)
BACKEND = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BACKEND)
wiki_search = BACKEND.wiki_search


def page(root, relative, content):
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
    return target


def search(root, query="tide", **options):
    # Fixture budget: ten results and eighty escaped characters unless overridden.
    return wiki_search(query, allowed_root=root, top_k=options.pop("top_k", 10),
                       excerpt_chars=options.pop("excerpt_chars", 80), **options)


def test_domain_filter_and_stable_ranking(tmp_path):
    # beta: two distinct terms, three occurrences; alpha/zeta: two and two;
    # partial: one and four. The excluded domain would otherwise rank first.
    for name, text in reversed([
        ("alpha", "Tide current"), ("beta", "tide tide current"),
        ("zeta", "tide current"), ("partial", "tide tide tide tide"),
    ]):
        page(tmp_path, f"ocean/wiki/{name}.md", text)
    page(tmp_path, "soil/wiki/other.md", "tide current tide current")
    results = search(tmp_path, "TIDE current tide", domain="ocean", top_k=3)
    assert [r["page"] for r in results] == [
        "ocean/wiki/beta.md", "ocean/wiki/alpha.md", "ocean/wiki/zeta.md"]
    assert [(r["matched_terms"], r["occurrences"]) for r in results] == [
        (2, 3), (2, 2), (2, 2)]
    assert {r["domain"] for r in results} == {"ocean"}
    assert results == search(tmp_path, "TIDE current tide", domain="ocean", top_k=3)


def test_missing_index_uses_lexical_search(tmp_path):
    # One token appearing once; no index, model, transport or registry is created.
    page(tmp_path, "ocean/wiki/current.md", "A tide observation.")
    assert search(tmp_path, top_k=1) == [{
        "page": "ocean/wiki/current.md", "domain": "ocean",
        "matched_terms": 1, "occurrences": 1, "excerpt": "tide observation.",
    }]
    assert sorted(p.name for p in tmp_path.iterdir()) == ["ocean"]


def test_nested_pages_all_domains_and_token_boundaries(tmp_path):
    page(tmp_path, "ocean/wiki/nested/one.md", "tideline is unrelated; tide!")
    page(tmp_path, "soil/wiki/two.MD", "TIDE")
    page(tmp_path, "ocean/notes.md", "tide tide")
    page(tmp_path, "ocean/wiki/ignored.txt", "tide tide")
    results = search(tmp_path)
    assert [r["page"] for r in results] == [
        "ocean/wiki/nested/one.md", "soil/wiki/two.MD"]
    # Whole-word matching counts tide once on each page, never tideline.
    assert [r["occurrences"] for r in results] == [1, 1]
    assert results[0]["excerpt"] == "tide!"


def test_unicode_casefold_keeps_original_excerpt_offsets(tmp_path):
    page(tmp_path, "ocean/wiki/unicode.md", "Straße before TIDE <tag>")
    assert search(tmp_path)[0]["excerpt"] == "TIDE &lt;tag&gt;"
    # The single original word Straße folds to strasse without losing its span.
    assert search(tmp_path, "STRASSE")[0]["excerpt"] == "Straße before TIDE &lt;tag&gt;"


def test_escaped_excerpt_is_bounded_without_broken_entities(tmp_path):
    page(tmp_path, "ocean/wiki/html.md", 'tide <b>&"\'\n\x1b[31m')
    # HTML encoding by hand: < -> &lt;, > -> &gt;, & -> &amp;,
    # double quote -> &quot;, apostrophe -> &#x27;. Control characters become spaces.
    assert search(tmp_path)[0]["excerpt"] == (
        "tide &lt;b&gt;&amp;&quot;&#x27;  [31m")
    # 'tide ' takes five characters, '&lt;' takes four: exactly nine.
    assert search(tmp_path, excerpt_chars=9)[0]["excerpt"] == "tide &lt;"
    assert search(tmp_path, excerpt_chars=8)[0]["excerpt"] == "tide "
    assert search(tmp_path, excerpt_chars=1)[0]["excerpt"] == "t"


@pytest.mark.parametrize("query", ["", " \n\t", "!!!", "absent"])
def test_empty_or_unmatched_query_returns_no_results(tmp_path, query):
    page(tmp_path, "ocean/wiki/one.md", "tide")
    assert search(tmp_path, query) == []


@pytest.mark.parametrize("limit,expected", [(0, []), (1, ["a"]), (2, ["a", "b"]),
                                           (20, ["a", "b"])])
def test_result_limit_is_supplied_by_caller(tmp_path, limit, expected):
    # Two tied pages, a before b; zero/one/two/twenty request none/one/both/both.
    for name in ("b", "a"):
        page(tmp_path, f"ocean/wiki/{name}.md", "tide")
    assert [Path(r["page"]).stem for r in search(tmp_path, top_k=limit)] == expected


@pytest.mark.parametrize("options", [
    {"top_k": -1}, {"top_k": True}, {"top_k": 1.5}, {"top_k": "1"},
    {"excerpt_chars": 0}, {"excerpt_chars": -1}, {"excerpt_chars": False},
    {"excerpt_chars": 1.5}, {"query": None}, {"query": ["tide"]},
    {"domain": ".."}, {"domain": "../ocean"}, {"domain": "ocean/wiki"},
    {"domain": "ocean\\wiki"}, {"domain": ".hidden"}, {"domain": ""},
    {"domain": ["ocean"]}, {"domain": "ocean\n"},
])
def test_invalid_arguments_are_rejected_before_page_reads(tmp_path, monkeypatch, options):
    def forbidden(*args, **kwargs):
        pytest.fail("invalid arguments must be rejected before traversal")
    monkeypatch.setattr(os, "listdir", forbidden)
    with pytest.raises(ValueError):
        search(tmp_path, **options)


def test_missing_domain_and_empty_root(tmp_path):
    assert search(tmp_path) == []
    page(tmp_path, "ocean/wiki/a.md", "tide")
    assert search(tmp_path, domain="missing") == []


def test_symlink_escape_not_read(tmp_path, monkeypatch):
    root = tmp_path / "allowed"
    good = page(root, "ocean/wiki/good.md", "tide")
    outside = page(tmp_path, "outside/private.md", "tide tide tide")
    (good.parent / "escape.md").symlink_to(outside)
    (good.parent / "escape-dir").symlink_to(outside.parent, target_is_directory=True)
    (root / "linked").symlink_to(root / "ocean", target_is_directory=True)
    (root / "ocean/wiki-link").symlink_to(good.parent, target_is_directory=True)
    inside_link = good.parent / "alias.md"
    inside_link.symlink_to(good)
    real_read = os.read
    forbidden_inode = outside.stat().st_ino

    def guarded_read(fd, *args):
        assert os.fstat(fd).st_ino != forbidden_inode, "escaped page was read"
        return real_read(fd, *args)

    monkeypatch.setattr(os, "read", guarded_read)
    assert [r["page"] for r in search(root)] == ["ocean/wiki/good.md"]


@pytest.mark.parametrize("kind", ["relative", "missing", "file", "link", "ancestor", "dotdot"])
def test_escaped_or_invalid_allowed_root_rejected(tmp_path, kind):
    root = tmp_path / "allowed"
    root.mkdir()
    file = page(root, "ocean/wiki/good.md", "tide")
    link = tmp_path / "alias"
    link.symlink_to(root, target_is_directory=True)
    choices = {"relative": Path("relative"), "missing": tmp_path / "missing",
               "file": file, "link": link, "ancestor": link / "ocean",
               "dotdot": root / ".." / "allowed"}
    with pytest.raises(ValueError):
        search(choices[kind])


def test_sensitive_paths_excluded_before_open(tmp_path, monkeypatch):
    page(tmp_path, "ocean/wiki/good.md", "tide")
    hidden = [".env", ".env.md", ".private/page.md", "secrets/page.md",
              "config/secrets/page.md", ".claude/state/page.md"]
    for name in hidden:
        page(tmp_path, f"ocean/wiki/{name}", "tide")
    page(tmp_path, ".hidden/wiki/page.md", "tide")
    real_open = os.open

    def guarded_open(path, *args, **kwargs):
        # Descriptor traversal opens one component at a time, never denied entries.
        assert Path(path).name not in {".env", ".env.md", ".private", "secrets",
                                       ".claude", ".hidden"}
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(os, "open", guarded_open)
    assert [r["page"] for r in search(tmp_path)] == ["ocean/wiki/good.md"]


def test_domain_filter_excludes_other_domains_before_open(tmp_path, monkeypatch):
    page(tmp_path, "ocean/wiki/a.md", "tide")
    page(tmp_path, "soil/wiki/b.md", "tide")
    real_open = os.open

    def guarded_open(path, *args, **kwargs):
        assert Path(path).name != "soil", "excluded domain was opened"
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(os, "open", guarded_open)
    assert [r["domain"] for r in search(tmp_path, domain="ocean")] == ["ocean"]


@pytest.mark.parametrize("entry", ["domain", "wiki", "directory", "page"])
def test_symlink_substitution_between_check_and_open(tmp_path, monkeypatch, entry):
    root = tmp_path / "allowed"
    good = page(root, "ocean/wiki/nested/page.md", "tide")
    outside = page(tmp_path, "external/wiki/nested/page.md", "tide tide")
    targets = {"domain": root / "ocean", "wiki": root / "ocean/wiki",
               "directory": good.parent, "page": good}
    # page -> nested -> wiki -> domain: domain/wiki are parents[2]/parents[1].
    replacements = {"domain": outside.parents[2], "wiki": outside.parents[1],
                    "directory": outside.parent, "page": outside}
    target = targets[entry]
    real_open = os.open
    substituted = False

    def racing_open(path, *args, **kwargs):
        nonlocal substituted
        if kwargs.get("dir_fd") is not None and path == target.name and not substituted:
            # Synthetic attacker preserves the original fixture under another name.
            substituted = True
            target.rename(target.with_name("saved"))
            target.symlink_to(replacements[entry], target_is_directory=entry != "page")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(os, "open", racing_open)
    assert search(root) == []
    assert substituted


@pytest.mark.parametrize("entry", ["directory", "page"])
def test_device_crossing_is_not_read(tmp_path, monkeypatch, entry):
    target = page(tmp_path, "ocean/wiki/nested/page.md", "tide")
    # A synthetic device identifier differs by one; no mount operation is needed.
    blocked_inode = (target.parent if entry == "directory" else target).stat().st_ino
    real_fstat, real_read, real_listdir = os.fstat, os.read, os.listdir

    def changed_device(fd):
        info = real_fstat(fd)
        if info.st_ino == blocked_inode:
            return SimpleNamespace(st_mode=info.st_mode, st_dev=info.st_dev + 1)
        return info

    def guarded_read(fd, *args):
        assert real_fstat(fd).st_ino != blocked_inode
        return real_read(fd, *args)

    def guarded_listdir(fd):
        assert real_fstat(fd).st_ino != blocked_inode
        return real_listdir(fd)

    monkeypatch.setattr(os, "fstat", changed_device)
    monkeypatch.setattr(os, "read", guarded_read)
    monkeypatch.setattr(os, "listdir", guarded_listdir)
    assert search(tmp_path) == []


def test_nonregular_and_unreadable_pages_are_skipped(tmp_path, monkeypatch):
    good = page(tmp_path, "ocean/wiki/good.md", "tide")
    unreadable = page(tmp_path, "ocean/wiki/unreadable.md", "tide")
    os.mkfifo(good.parent / "pipe.md")
    real_open = os.open

    def guarded_open(path, *args, **kwargs):
        assert Path(path).name != "pipe.md", "nonregular entry was opened"
        if path == unreadable.name:
            raise PermissionError("synthetic unreadable page")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(os, "open", guarded_open)
    assert [r["page"] for r in search(tmp_path)] == ["ocean/wiki/good.md"]


def test_no_atime_permission_failure_rejects_root(tmp_path, monkeypatch):
    real_open = os.open

    def guarded_open(path, flags, *args, **kwargs):
        if flags & os.O_NOATIME:
            raise PermissionError("synthetic no-atime permission failure")
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", guarded_open)
    with pytest.raises(ValueError):
        search(tmp_path)


def test_invalid_root_closes_ancestor_descriptors(tmp_path, monkeypatch):
    real_open, real_close = os.open, os.close
    opened, closed = [], []

    def track_open(*args, **kwargs):
        fd = real_open(*args, **kwargs)
        opened.append(fd)
        return fd

    def track_close(fd):
        closed.append(fd)
        return real_close(fd)

    monkeypatch.setattr(os, "open", track_open)
    monkeypatch.setattr(os, "close", track_close)
    with pytest.raises(ValueError):
        search(tmp_path / "invalid\x00name")
    # Every successfully opened descriptor must have been closed, including on error.
    assert Counter(opened) == Counter(closed)


def snapshot(root):
    """Observe bytes, entries, and metadata using reads that preserve access times."""
    entries = {}

    def visit(path):
        metadata = path.lstat()
        # Includes inode, size, modes, links, ownership, and all three timestamps.
        value = (tuple(metadata), metadata.st_atime_ns, metadata.st_mtime_ns,
                 metadata.st_ctime_ns)
        if path.is_symlink():
            payload = os.readlink(path)
        elif stat.S_ISDIR(metadata.st_mode):
            fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOATIME)
            try:
                payload = sorted(os.listdir(fd))
            finally:
                os.close(fd)
            for name in payload:
                visit(path / name)
        else:
            fd = os.open(path, os.O_RDONLY | os.O_NOATIME)
            try:
                # The fixture size is the exact independent read budget.
                payload = os.read(fd, metadata.st_size)
            finally:
                os.close(fd)
        entries[path.relative_to(root).as_posix()] = (value, payload)

    visit(root)
    return entries


def test_read_only_preserves_bytes_entries_and_metadata(tmp_path, monkeypatch):
    root = tmp_path / "allowed"
    target = page(root, "ocean/wiki/good.md", "tide <tag>")
    page(tmp_path, "caller.txt", "caller content")
    # Move access time one nanosecond before modification time to expose reads
    # even on relatime filesystems. Preserve every observed value from here on.
    for path in (root, root / "ocean", target.parent, target):
        metadata = path.stat()
        os.utime(path, ns=(metadata.st_mtime_ns - 1, metadata.st_mtime_ns))
    before = snapshot(tmp_path)
    real_open = os.open

    def read_only_open(path, flags, *args, **kwargs):
        assert not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
        return real_open(path, flags, *args, **kwargs)

    def forbidden(*args, **kwargs):
        pytest.fail("mutation syscall attempted")

    monkeypatch.setattr(os, "open", read_only_open)
    for name in ("write", "unlink", "rename", "replace", "mkdir", "rmdir", "utime",
                 "chmod", "chown", "truncate", "ftruncate", "link", "symlink"):
        monkeypatch.setattr(os, name, forbidden)
    assert search(root)
    assert search(root, "missing") == []
    assert search(root, top_k=0) == []
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("mode", ["search", "close", "error"])
def test_deep_tree_closes_descriptors(tmp_path, monkeypatch, mode):
    shallow = page(tmp_path, "ocean/wiki/shallow.md", "tide")
    # Exceed the interpreter limit without changing it; short names keep the
    # synthetic tree below the filesystem path-length limit.
    depth = sys.getrecursionlimit() + 10
    directories = [os.open(shallow.parent, os.O_RDONLY | os.O_DIRECTORY)]
    try:
        for _ in range(depth):
            os.mkdir("d", dir_fd=directories[-1])
            directories.append(os.open("d", os.O_RDONLY | os.O_DIRECTORY,
                                       dir_fd=directories[-1]))
        if mode == "close":
            os.link(shallow, "deep.md", dst_dir_fd=directories[-1])
        real_open, real_close = os.open, os.close
        opened, closed = [], []

        def track_open(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            opened.append(fd)
            return fd

        def track_close(fd):
            closed.append(fd)
            return real_close(fd)

        with monkeypatch.context() as patch:
            patch.setattr(os, "open", track_open)
            patch.setattr(os, "close", track_close)
            if mode == "search":
                # One shallow matching page remains available beyond deep descent.
                assert [row["page"] for row in search(tmp_path, top_k=1)] == [
                    "ocean/wiki/shallow.md"]
            else:
                deepest = os.fstat(directories[-1]).st_ino
                real_listdir = os.listdir

                def deepest_entries(fd):
                    if os.fstat(fd).st_ino == deepest and mode == "error":
                        raise RuntimeError("synthetic enumeration failure")
                    # Descend before yielding the shallow result.
                    return sorted(real_listdir(fd))

                patch.setattr(os, "listdir", deepest_entries)
                pages = BACKEND._pages(directories[0], "ocean/wiki",
                                       os.fstat(directories[0]).st_dev)
                if mode == "error":
                    with pytest.raises(RuntimeError, match="synthetic enumeration failure"):
                        list(pages)
                else:
                    assert next(pages)[0].endswith("/deep.md")
                    pages.close()
            assert Counter(opened) == Counter(closed)
    finally:
        # Iterative fixture teardown avoids recursion in temporary-tree cleanup.
        if mode == "close":
            os.unlink("deep.md", dir_fd=directories[-1])
        while len(directories) > 1:
            os.close(directories.pop())
            os.rmdir("d", dir_fd=directories[-1])
        os.close(directories.pop())
