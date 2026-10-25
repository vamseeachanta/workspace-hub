"""Synthetic bundle tests; expected paths are literal, never inventoried oracles.

Digest and byte-count basis: RFC 6234 section 8.5, SHA256 test 1 (ASCII abc,
three bytes): https://www.rfc-editor.org/rfc/rfc6234#section-8.5.
Protocol versions, exit statuses and JSON indentation below are local interface
choices, specified in bundle_manifest's docstring, rather than measured values.
"""

import copy
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/reporting/bundle_manifest.py"
SPEC = importlib.util.spec_from_file_location("bundle_manifest", SCRIPT)
bundle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bundle)

# RFC 6234 section 8.5, SHA256 test 1; normalized to lowercase hexadecimal.
ABC_SHA256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
ABC_SIZE = 3  # Hand count of ASCII bytes: a, b, c.
SCHEMA = "bundle-manifest-v1"


def expected(*paths):
    return {"schema": SCHEMA, "files": [
        {"path": path, "size": ABC_SIZE, "sha256": ABC_SHA256}
        for path in paths
    ]}


def tree(root, paths):
    root.mkdir()
    for path in paths:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"abc")
    return root


def cli(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )


def test_manifest_is_deterministic(tmp_path):
    root = tree(tmp_path / "bundle", ["z.txt", "sub/a.txt", "a.txt"])
    first = bundle.inventory(root)
    assert first == expected("a.txt", "sub/a.txt", "z.txt")
    (root / "z.txt").touch()
    assert bundle.serialize_manifest(bundle.inventory(root)) == bundle.serialize_manifest(first)
    other = tree(tmp_path / "other", ["a.txt", "sub/a.txt", "z.txt"])
    assert bundle.serialize_manifest(bundle.inventory(other)) == bundle.serialize_manifest(first)


def test_manifest_known_digest(tmp_path):
    root = tree(tmp_path / "bundle", ["abc.txt"])
    assert bundle.inventory(root) == expected("abc.txt")


def test_empty_manifest(tmp_path):
    assert bundle.inventory(tmp_path) == {"schema": SCHEMA, "files": []}


def test_manifest_filename_roundtrip(tmp_path):
    paths = ['a space.txt', 'colon:pipe|comma,.txt', 'quote".txt',
             'tab\tline\n.txt', '雪/é.txt', 'é.txt', 'e\u0301.txt', 'back\\slash.txt']
    root = tree(tmp_path / "bundle", paths)
    # Literal POSIX lexical order; Unicode is not normalized or case folded.
    wanted = expected('a space.txt', 'back\\slash.txt', 'colon:pipe|comma,.txt',
                      'e\u0301.txt', 'quote".txt', 'tab\tline\n.txt', 'é.txt', '雪/é.txt')
    assert bundle.inventory(root) == wanted
    assert bundle.load_manifest(bundle.serialize_manifest(wanted)) == wanted


def test_manifest_excludes_its_output(tmp_path):
    root = tree(tmp_path / "bundle", ["abc.txt"])
    output = root / "manifest.json"
    for _ in ("first", "repeat"):
        result = cli("inventory", root, "--destination", root, "--output", output.name)
        assert result.returncode == 0
        assert result.stderr == ""
        assert bundle.load_manifest(output.read_bytes()) == expected("abc.txt")
        assert (root / "abc.txt").read_bytes() == b"abc"
    assert bundle.inventory(root, exclude_output=output) == expected("abc.txt")


def test_inventory_never_changes_input_bytes(tmp_path):
    root = tree(tmp_path / "bundle", ["a.txt", "sub/b.txt"])
    before = {"a.txt": b"abc", "sub/b.txt": b"abc"}
    for _ in ("first", "repeat"):
        assert bundle.inventory(root) == expected("a.txt", "sub/b.txt")
        assert {path: (root / path).read_bytes() for path in before} == before
    assert sorted(path.relative_to(root).as_posix() for path in root.rglob("*")
                  if path.is_file()) == ["a.txt", "sub/b.txt"]


@pytest.mark.parametrize("kind", ["file-link", "directory-link", "broken-link", "hard-link",
                                 "fifo", "socket", "excluded-link", "excluded-fifo"])
def test_manifest_rejects_links_and_special_files(tmp_path, kind):
    root = tree(tmp_path / "bundle", ["abc.txt"])
    suspect = root / "suspect"
    sock = None
    if kind in {"file-link", "excluded-link"}:
        suspect.symlink_to(root / "abc.txt")
    elif kind == "directory-link":
        suspect.symlink_to(tmp_path, target_is_directory=True)
    elif kind == "broken-link":
        suspect.symlink_to(tmp_path / "absent")
    elif kind == "hard-link":
        os.link(root / "abc.txt", suspect)
    elif kind in {"fifo", "excluded-fifo"}:
        os.mkfifo(suspect)
    else:
        sock = socket.socket(socket.AF_UNIX)
        sock.bind(str(suspect))
    try:
        with pytest.raises(bundle.ManifestError):
            bundle.inventory(root, exclude_output=suspect if kind.startswith("excluded") else None)
    finally:
        if sock:
            sock.close()
    assert (root / "abc.txt").read_bytes() == b"abc"


def test_linked_root_and_ancestor_are_rejected(tmp_path):
    root = tree(tmp_path / "bundle", ["sub/abc.txt"])
    alias = tmp_path / "alias"
    alias.symlink_to(root, target_is_directory=True)
    for candidate in (alias, alias / "sub"):
        with pytest.raises(bundle.ManifestError):
            bundle.inventory(candidate)


def test_non_directory_root_is_rejected(tmp_path):
    file = tmp_path / "file"
    file.write_bytes(b"abc")
    for candidate in (file, tmp_path / "absent"):
        with pytest.raises(bundle.ManifestError):
            bundle.inventory(candidate)


def test_compare_added_removed_changed(tmp_path):
    before = tree(tmp_path / "before", ["removed.txt", "changed.txt", "unchanged.txt"])
    after = tree(tmp_path / "after", ["added.txt", "changed.txt", "unchanged.txt"])
    (after / "changed.txt").write_bytes(b"abd")  # Same hand-counted length, different bytes.
    assert bundle.compare_manifests(bundle.inventory(before), bundle.inventory(after)) == {
        "added": ["added.txt"], "removed": ["removed.txt"], "changed": ["changed.txt"],
    }


def test_identical_bundles_have_empty_diff(tmp_path):
    first = tree(tmp_path / "first", ["a.txt", "sub/b.txt"])
    second = tree(tmp_path / "second", ["sub/b.txt", "a.txt"])
    assert bundle.compare_manifests(bundle.inventory(first), bundle.inventory(second)) == {
        "added": [], "removed": [], "changed": [],
    }
    assert bundle.compare_manifests(expected(), expected()) == {
        "added": [], "removed": [], "changed": [],
    }


def test_compare_sorts_input_and_reports_size_change():
    before = expected("z", "b", "a")
    after = expected("z", "b", "a")
    # Four bytes = the three-byte vector plus one; intentionally inconsistent
    # digest checks metadata comparison independently of recomputing source bytes.
    after["files"][0]["size"] = ABC_SIZE + 1
    assert bundle.compare_manifests(before, after)["changed"] == ["z"]
    assert bundle.compare_manifests(expected(), before)["added"] == ["a", "b", "z"]
    assert bundle.compare_manifests(before, expected())["removed"] == ["a", "b", "z"]


@pytest.mark.parametrize("raw", [b"{", b"\xff", b"[]", b"null",
    b'{"schema":"bundle-manifest-v1","schema":"bundle-manifest-v1","files":[]}',
    b'{"schema":"bundle-manifest-v1","files":NaN}',
    b'{"schema":"bundle-manifest-v1","files":Infinity}'])
def test_malformed_json_is_rejected(raw):
    with pytest.raises(bundle.ManifestError):
        bundle.load_manifest(raw)


@pytest.mark.parametrize("field,value", [
    ("path", ""), ("path", "."), ("path", "../escape"), ("path", "/absolute"),
    ("path", "a/../b"), ("path", "a//b"), ("path", "a/./b"), ("path", "a/"),
    ("path", "nul\x00"), ("path", "\ud800"), ("path", None),
    ("size", -1), ("size", True), ("size", 3.0), ("size", "3"),
    ("sha256", "invalid"), ("sha256", ABC_SHA256.upper()), ("sha256", None),
])
def test_malformed_entries_are_rejected(field, value):
    data = expected("a.txt")
    data["files"][0][field] = value
    with pytest.raises(bundle.ManifestError):
        bundle.compare_manifests(expected(), data)


@pytest.mark.parametrize("kind", ["version", "extra-header", "missing-files", "files-object",
                                 "entry-scalar", "extra-field", "missing-field", "duplicate",
                                 "ancestor"])
def test_malformed_schema_is_rejected(kind):
    data = expected("a.txt")
    if kind == "version":
        data["schema"] = "unsupported"
    elif kind == "extra-header":
        data["timestamp"] = "unwanted"
    elif kind == "missing-files":
        del data["files"]
    elif kind == "files-object":
        data["files"] = {}
    elif kind == "entry-scalar":
        data["files"] = [None]
    elif kind == "extra-field":
        data["files"][0]["extra"] = "unwanted"
    elif kind == "missing-field":
        del data["files"][0]["size"]
    elif kind == "duplicate":
        data["files"].append(copy.deepcopy(data["files"][0]))
    else:
        data = expected("a", "a/b")
    with pytest.raises(bundle.ManifestError):
        bundle.load_manifest(json.dumps(data))


@pytest.mark.parametrize("output", ["../escaped.json", "/absolute.json", "sub/../../escape.json"])
def test_output_escape_is_rejected(tmp_path, output):
    root = tree(tmp_path / "bundle", ["abc.txt"])
    destination = tmp_path / "destination"
    destination.mkdir()
    result = cli("inventory", root, "--destination", destination, "--output", output)
    assert result.returncode == 2
    assert result.stdout == ""
    assert list(destination.iterdir()) == []
    assert (root / "abc.txt").read_bytes() == b"abc"


def test_output_link_and_payload_overwrite_are_rejected(tmp_path):
    root = tree(tmp_path / "bundle", ["abc.txt"])
    external = tree(tmp_path / "external", ["retained.txt"])
    (root / "linked").symlink_to(external, target_is_directory=True)
    (root / "linked.json").symlink_to(external / "retained.txt")
    for output in ("linked/manifest.json", "linked.json", "abc.txt"):
        result = cli("inventory", external, "--destination", root, "--output", output)
        assert result.returncode == 2
        assert result.stdout == ""
    assert (root / "abc.txt").read_bytes() == b"abc"
    assert (external / "retained.txt").read_bytes() == b"abc"
    assert not (external / "manifest.json").exists()


def test_cli_subcommands_and_exit_codes(tmp_path):
    root = tree(tmp_path / "bundle", ["a.txt"])
    result = cli("inventory", root)
    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout) == expected("a.txt")
    assert str(root) not in result.stdout
    before = tmp_path / "before.json"
    before.write_text(result.stdout, encoding="utf-8")
    after = tmp_path / "after.json"
    after.write_text(json.dumps(expected("b.txt")), encoding="utf-8")
    noop = cli("compare", before, before)
    assert noop.returncode == 0
    assert json.loads(noop.stdout) == {"added": [], "removed": [], "changed": []}
    changed = cli("compare", before, after)
    assert changed.returncode == 1
    assert json.loads(changed.stdout) == {
        "added": ["b.txt"], "removed": ["a.txt"], "changed": [],
    }
    after.write_bytes(b"not json")
    malformed = cli("compare", before, after)
    assert malformed.returncode == 2
    assert malformed.stdout == ""
    assert malformed.stderr == "error: manifest input is invalid\n"
    missing = cli("compare", before, tmp_path / "absent")
    assert missing.returncode == 2
    assert missing.stdout == ""
    assert missing.stderr == "error: filesystem input or output unavailable\n"


@pytest.mark.parametrize("kind", ["link", "fifo", "hard-link", "directory"])
def test_compare_rejects_non_regular_manifest_inputs(tmp_path, kind):
    good = tmp_path / "good.json"
    good.write_text(json.dumps(expected()), encoding="utf-8")
    suspect = tmp_path / "suspect.json"
    if kind == "link":
        suspect.symlink_to(good)
    elif kind == "fifo":
        os.mkfifo(suspect)
    elif kind == "hard-link":
        os.link(good, suspect)
    else:
        suspect.mkdir()
    # Reject the file type before opening a stream, including a blocking FIFO.
    with pytest.raises(bundle.ManifestError):
        bundle.read_manifest(suspect)
    for before, after in ((suspect, good), (good, suspect)):
        result = cli("compare", before, after)
        assert result.returncode == 2
        assert result.stdout == ""


def test_cli_output_requires_destination_and_rejects_empty_name(tmp_path):
    for arguments in (("--output", "manifest.json"),
                      ("--destination", tmp_path, "--output", "")):
        result = cli("inventory", tmp_path, *arguments)
        assert result.returncode == 2
        assert result.stdout == ""
        assert list(tmp_path.iterdir()) == []


def test_compare_delimiter_paths():
    assert bundle.compare_manifests(expected('tab\tline\n.txt', '雪.txt'),
                                    expected('quote".txt', '雪.txt')) == {
        "added": ['quote".txt'], "removed": ['tab\tline\n.txt'], "changed": [],
    }
