"""Qualify literal local HTML/manifest composition, not a publishing service.

The literals below independently define paths, byte lengths (len of literal
bytes), SHA-256 inputs and HTML edges. No production digest helper supplies an
oracle. The manifest schema is the local bundle_manifest v1 interface; SHA-256
is computed with the standard library. Duplicate references are edges, not
additional payloads. Arbitrary Markdown parsing and operational publication
services are outside this suite.
"""

import builtins
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil

import pytest

from bundle_manifest import (
    ManifestError, compare_manifests, inventory, load_manifest, read_manifest,
    serialize_manifest,
)
from publication_navigation import NavigationIssue, check_bundle


LITERALS = {
    "index.html": (
        b'<h1 id="summary">Summary</h1>'
        b'<a href="runs/review.html#details">Review</a>'
        b'<a href="evidence/result.txt">Evidence</a>'
        b'<img src="assets/plot.svg">'
    ),
    "runs/review.html": (
        b'<h2 id="details">Details</h2>'
        b'<a href="../index.html#summary">Summary</a>'
        b'<a href="../evidence/result.txt">Evidence</a>'
    ),
    "assets/plot.svg": b'<svg xmlns="http://www.w3.org/2000/svg"></svg>',
    "evidence/result.txt": b"abc\n",
}
# Explicit fixture membership and lexical order, independent of tree traversal.
EXPECTED_PATHS = [
    "assets/plot.svg", "evidence/result.txt", "index.html", "runs/review.html",
]
MANIFEST = "bundle-manifest.json"
NO_DIFF = {"added": [], "removed": [], "changed": []}


def expected_row(path, payload):
    return {"path": path, "size": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest()}


def expected_manifest():
    return {"schema": "bundle-manifest-v1", "files": [
        expected_row(path, LITERALS[path]) for path in EXPECTED_PATHS
    ]}


def current_manifest(root):
    return inventory(root, exclude_output=root / MANIFEST)


@pytest.fixture
def assembled(tmp_path):
    root = tmp_path / "assembled"
    for name, payload in LITERALS.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    # Use the actual builder and reader; the manifest excludes itself only.
    (root / MANIFEST).write_bytes(serialize_manifest(current_manifest(root)))
    return root


def test_bundle_manifest_and_navigation_agree(assembled):
    stored = read_manifest(assembled / MANIFEST)
    assert stored == current_manifest(assembled) == expected_manifest()
    assert [row["path"] for row in stored["files"]] == EXPECTED_PATHS
    assert compare_manifests(stored, current_manifest(assembled)) == NO_DIFF
    assert check_bundle(assembled) == []


def test_relocated_fixture_has_same_integrity(assembled, tmp_path):
    relocated = tmp_path / "another" / "root"
    shutil.copytree(assembled, relocated)
    for root in (assembled, relocated):
        assert read_manifest(root / MANIFEST) == expected_manifest()
        assert current_manifest(root) == expected_manifest()
        assert compare_manifests(read_manifest(root / MANIFEST),
                                 current_manifest(root)) == NO_DIFF
        assert check_bundle(root) == []
    assert (relocated / MANIFEST).read_bytes() == (assembled / MANIFEST).read_bytes()


def test_content_tamper_fails_manifest_even_with_valid_links(assembled, tmp_path):
    root = tmp_path / "tampered"
    shutil.copytree(assembled, root)
    replacement = b"abd\n"  # Same hand-counted ASCII length as abc plus newline.
    assert len(replacement) == len(LITERALS["evidence/result.txt"])
    (root / "evidence/result.txt").write_bytes(replacement)
    actual = current_manifest(root)
    wanted = expected_manifest()
    wanted["files"] = [
        expected_row("evidence/result.txt", replacement)
        if row["path"] == "evidence/result.txt" else row
        for row in wanted["files"]
    ]
    assert actual == wanted
    assert actual != read_manifest(root / MANIFEST)
    assert compare_manifests(read_manifest(root / MANIFEST), actual) == {
        "added": [], "removed": [], "changed": ["evidence/result.txt"],
    }
    assert check_bundle(root) == []


@pytest.mark.parametrize("fault", ["missing", "extra", "stale"])
def test_missing_extra_and_stale_members_are_distinct(assembled, tmp_path, fault):
    root = tmp_path / fault
    shutil.copytree(assembled, root)
    stored = read_manifest(root / MANIFEST)
    if fault == "missing":
        # Delete only disposable fixture data; retain the recorded manifest row.
        (root / "assets/plot.svg").unlink()
        wanted = {"added": [], "removed": ["assets/plot.svg"], "changed": []}
        issues = [NavigationIssue("index.html", "assets/plot.svg", "missing-target")]
    elif fault == "extra":
        (root / "evidence/unlisted.txt").write_bytes(b"unlisted\n")
        wanted = {"added": ["evidence/unlisted.txt"], "removed": [], "changed": []}
        issues = []  # An unlinked retained file affects inventory, not navigation.
    else:
        stale = copy.deepcopy(stored)
        stale["files"].append(expected_row("evidence/retired.txt", b"retired\n"))
        (root / MANIFEST).write_text(json.dumps(stale), encoding="utf-8")
        wanted = {"added": [], "removed": ["evidence/retired.txt"], "changed": []}
        issues = []  # A stale row alone does not introduce an HTML edge.
    assert compare_manifests(read_manifest(root / MANIFEST),
                             current_manifest(root)) == wanted
    assert check_bundle(root) == issues
    # Each fault is confined to its copy, including the stored baseline manifest.
    assert read_manifest(assembled / MANIFEST) == expected_manifest()
    assert current_manifest(assembled) == expected_manifest()
    assert check_bundle(assembled) == []


def test_shared_asset_is_one_inventory_member(assembled, tmp_path):
    # The two literal pages each contain one reference to the same evidence file.
    assert b'href="evidence/result.txt"' in LITERALS["index.html"]
    assert b'href="../evidence/result.txt"' in LITERALS["runs/review.html"]
    evidence = [row for row in current_manifest(assembled)["files"]
                if row["path"] == "evidence/result.txt"]
    assert evidence == [expected_row("evidence/result.txt", b"abc\n")]
    assert current_manifest(assembled) == expected_manifest()
    assert check_bundle(assembled) == []
    # Removing the single payload breaks both edges, but removes one member.
    missing = tmp_path / "shared-missing"
    shutil.copytree(assembled, missing)
    (missing / "evidence/result.txt").unlink()
    assert compare_manifests(read_manifest(missing / MANIFEST),
                             current_manifest(missing)) == {
        "added": [], "removed": ["evidence/result.txt"], "changed": [],
    }
    assert check_bundle(missing) == [
        NavigationIssue("index.html", "evidence/result.txt", "missing-target"),
        NavigationIssue("runs/review.html", "../evidence/result.txt", "missing-target"),
    ]


def test_fragment_change_breaks_navigation_and_manifest(assembled, tmp_path):
    root = tmp_path / "fragment"
    shutil.copytree(assembled, root)
    (root / "runs/review.html").write_bytes(
        LITERALS["runs/review.html"].replace(b'id="details"', b'id="absent"'))
    assert compare_manifests(read_manifest(root / MANIFEST), current_manifest(root)) == {
        "added": [], "removed": [], "changed": ["runs/review.html"],
    }
    assert check_bundle(root) == [NavigationIssue(
        "index.html", "runs/review.html#details", "missing-fragment")]


@pytest.mark.parametrize("kind, reason", [
    ("parent", "escaped-target"), ("absolute", "absolute-target"),
    ("symlink", "symlinked-target"),
])
def test_unsafe_reference_does_not_read_external_payload(
        assembled, tmp_path, monkeypatch, kind, reason):
    root = tmp_path / kind
    shutil.copytree(assembled, root)
    sentinel = tmp_path / "external-sentinel.html"
    payload = b'<h1 id="external">Sentinel must remain unread</h1>'
    sentinel.write_bytes(payload)
    before = sentinel.stat()
    alias = root / "external-alias.html"
    if kind == "parent":
        target = "../external-sentinel.html#external"
        unsafe_path = "../external-sentinel.html"
    elif kind == "absolute":
        unsafe_path = str(sentinel)  # Runtime temporary path, never operational data.
        target = unsafe_path + "#external"
    else:
        try:
            alias.symlink_to(sentinel)
        except (NotImplementedError, OSError) as exc:
            pytest.skip(f"Temporary filesystem cannot create symlinks: {type(exc).__name__}")
        target = "external-alias.html#external"
    (root / "index.html").write_bytes(
        LITERALS["index.html"] + f'<a href="{target}">Outside</a>'.encode("utf-8"))

    def guard(opener):
        def checked(file, *args, **kwargs):
            if isinstance(file, (str, bytes, os.PathLike)):
                candidate = Path(os.fsdecode(file))
                # Basename checks cover descriptor-relative opens used by inventory;
                # resolution covers absolute opens and the symlink alias.
                assert candidate.name not in {sentinel.name, alias.name}, "External open attempted"
                assert candidate.resolve() != sentinel, "External open attempted"
            return opener(file, *args, **kwargs)
        return checked

    with monkeypatch.context() as boundary:
        boundary.setattr(builtins, "open", guard(builtins.open))
        boundary.setattr(io, "open", guard(io.open))
        boundary.setattr(os, "open", guard(os.open))
        issues = [NavigationIssue("index.html", target, reason)]
        if kind == "symlink":
            # HTML inventory also rejects the alias as an HTML source.
            issues.append(NavigationIssue(alias.name, "", "symlinked-target"))
            with pytest.raises(ManifestError):
                current_manifest(root)
        else:
            # Inventory hashes the changed HTML, but does not interpret its edges.
            assert compare_manifests(read_manifest(root / MANIFEST),
                                     current_manifest(root)) == {
                "added": [], "removed": [], "changed": ["index.html"],
            }
            invalid = expected_manifest()
            invalid["files"].append(expected_row(unsafe_path, payload))
            with pytest.raises(ManifestError):
                load_manifest(json.dumps(invalid))
        assert check_bundle(root) == sorted(
            issues, key=lambda issue: (issue.source, issue.target, issue.reason))
    assert sentinel.read_bytes() == payload
    after = sentinel.stat()
    assert (after.st_mode, after.st_size, after.st_mtime_ns, after.st_ctime_ns) == (
        before.st_mode, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
