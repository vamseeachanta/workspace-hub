from __future__ import annotations

import os
import base64
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "legal"))
from rule_authority import audit, authority, codec, coverage, private_io  # noqa: E402

REV = "12345678-1234-" + "4234-9234-123456789abc"


def git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=True
    ).stdout.strip()


def test_audit_tree_scans_raw_paths_blobs_and_commit_bytes(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "synthetic@example.invalid")
    git(repo, "config", "user.name", "Synthetic")
    (repo / "nested").mkdir()
    (repo / "nested" / "data.bin").write_bytes(b"prefix prohibited suffix")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "synthetic commit")
    oid = git(repo, "rev-parse", "HEAD")
    result = audit.audit_tree(
        repo / ".git",
        oid,
        "refs/heads/master",
        [b"prohibited"],
        {
            "max_blob_bytes": 1024,
            "max_entries": 20,
            "max_findings": 10,
            "max_request_bytes": 4096,
        },
    )
    assert result == {
        "coverage": "complete",
        "findings": 1,
        "warnings": 0,
        "objects_examined": 2,
    }


def test_audit_tree_rejects_subset_ref_and_caps(tmp_path):
    with pytest.raises(codec.AuthorityError, match="integrity"):
        audit.audit_tree(
            tmp_path,
            "bad",
            "HEAD",
            [b"x"],
            {
                "max_blob_bytes": 1,
                "max_entries": 1,
                "max_findings": 1,
                "max_request_bytes": 1,
            },
        )


def test_audit_tree_handles_real_repository_scale(monkeypatch, tmp_path):
    oid = "a" * 40
    blob = "b" * 40
    records = b"".join(
        f"100644 blob {blob}\tfile-{index:05}.txt".encode() + b"\0"
        for index in range(22931)
    )

    def fake_git(_repo, *args, binary=False, **_kwargs):
        if args[:1] == ("rev-parse",):
            return oid
        if args[:1] == ("ls-tree",):
            return records
        if args[:2] == ("cat-file", "commit"):
            return b"clean"
        if args[:2] == ("cat-file", "blob"):
            return b"clean"
        raise AssertionError(args)

    monkeypatch.setattr(audit, "_git", fake_git)
    result = audit.audit_tree(
        tmp_path,
        oid,
        "refs/heads/main",
        [],
        {
            "max_blob_bytes": 1024,
            "max_entries": 100000,
            "max_findings": 1000,
            "max_request_bytes": 104857600,
        },
    )
    assert result["objects_examined"] == 22932


def test_structural_public_marker_allowlist_is_exact_canonical_path(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "synthetic@example.invalid")
    git(repo, "config", "user.name", "Synthetic")
    canonical = repo / "config" / "legal-rule-registry.json"
    canonical.parent.mkdir()
    canonical.write_bytes(b"legal-rule-" + b"registry-v1")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "canonical")
    rule = {
        "allow_paths": [b"config/legal-rule-registry.json"],
        "match_mode": "exact-bytes",
        "pattern": b"legal-rule-" + b"registry-v1",
        "severity": "block",
        "target": "content",
    }
    limits = {
        "max_blob_bytes": 1024,
        "max_entries": 100,
        "max_findings": 10,
        "max_request_bytes": 4096,
    }
    oid = git(repo, "rev-parse", "HEAD")
    clean = audit.audit_tree(repo / ".git", oid, "refs/heads/main", [rule], limits)
    assert clean["findings"] == 0
    (repo / "copied.json").write_bytes(b"legal-rule-" + b"registry-v1")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "copied")
    oid = git(repo, "rev-parse", "HEAD")
    finding = audit.audit_tree(repo / ".git", oid, "refs/heads/main", [rule], limits)
    assert finding["findings"] == 1


def test_public_tree_marker_occurrences_are_only_at_canonical_allowlisted_paths(
    tmp_path,
):
    def hits(marker):
        result = subprocess.run(
            ["git", "grep", "-l", "-z", "-F", "--", marker.decode("ascii")],
            cwd=ROOT,
            capture_output=True,
        )
        assert result.returncode in {0, 1}
        return set(result.stdout.split(b"\0")[:-1])

    for marker, allowed in authority.PUBLIC_MARKER_ALLOW_PATHS.items():
        assert hits(marker) == set(allowed)

    registry = codec.parse_registry(
        (ROOT / "config/legal-rule-registry.json").read_bytes()
    )
    policy = codec.parse_policy(
        (ROOT / "config/legal-rule-authority-policy.json").read_bytes()
    )
    private_map = {
        "authority_revision": registry["authority_revision"],
        "generation": registry["generation"],
        "rules": [
            {
                "pattern_b64": __import__("base64")
                .b64encode(b"synthetic-collision-probe")
                .decode(),
                "rule_id": registry["rules"][0]["rule_id"],
            }
        ],
        "schema_id": "legal-rule-" + "map-v1",
    }
    key = bytes(range(32))
    manifest = authority.build_manifest(registry, policy, private_map, key)
    preview = codec.parse_canonical(
        (
            ROOT
            / "docs/plans/evidence/2026-07-14-issue-3522-phase-a-protection-preview.json"
        ).read_bytes()
    )
    anchor = authority.make_anchor(manifest, preview["tool_sha"])
    ledger = authority.new_ledger("synthetic-key", manifest, key)
    unallowed = []
    for token in authority.structural_tokens(
        private_map, manifest, key, anchor=anchor, ledger=ledger
    ):
        allowed = authority.structural_allow_paths(token, manifest, anchor)
        if allowed:
            assert hits(token) == set(allowed)
        elif token and all(32 <= byte < 127 for byte in token.rstrip(b"\n")):
            unallowed.append(token.rstrip(b"\n"))
    patterns = tmp_path / "structural-patterns"
    patterns.write_bytes(b"\n".join(unallowed) + b"\n")
    residual = subprocess.run(
        ["git", "grep", "-l", "-z", "-F", "-f", str(patterns)],
        cwd=ROOT,
        capture_output=True,
    )
    assert residual.returncode == 1 and residual.stdout == b""


def test_rule_specs_honor_surface_ascii_fold_and_warning_severity():
    rules = [
        {
            "pattern": b"Secret.PDF",
            "match_mode": "ascii-fold",
            "severity": "block",
            "target": "path",
        },
        {
            "pattern": b"caution",
            "match_mode": "exact-bytes",
            "severity": "warn",
            "target": "content",
        },
    ]
    assert audit._matches(b"docs/SECRET.pdf", rules, "path") == (1, 0)
    assert audit._matches(b"caution", rules, "content") == (0, 1)
    assert audit._matches(b"secret.pdf caution", rules, "content") == (0, 1)


def test_scan_mirror_scans_raw_objects_and_retains_reverse_edges(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "synthetic@example.invalid")
    git(repo, "config", "user.name", "Synthetic")
    (repo / "Raw-Path.bin").write_bytes(b"content marker")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "commit marker")
    git(repo, "tag", "-a", "v1", "-m", "tag marker")
    mirror = tmp_path / "mirror.git"
    subprocess.run(
        ["git", "clone", "--mirror", str(repo), str(mirror)],
        check=True,
        capture_output=True,
    )
    refs = [
        (git(repo, "rev-parse", "HEAD").encode(), b"refs/heads/master"),
        (git(repo, "rev-parse", "v1").encode(), b"refs/tags/v1"),
    ]
    rules = [
        {
            "pattern": value,
            "match_mode": "exact-bytes",
            "severity": "block",
            "target": target,
        }
        for value, target in (
            (b"Raw-Path.bin", "path"),
            (b"content marker", "content"),
            (b"commit marker", "content"),
            (b"tag marker", "content"),
            (b"refs/tags/v1", "path"),
        )
    ]
    result = audit._scan_mirror(
        mirror,
        refs,
        rules,
        {
            "max_blob_bytes": 4096,
            "max_entries": 100,
            "max_findings": 20,
            "max_request_bytes": 65536,
        },
    )
    assert result["findings"] >= 5
    assert result["warnings"] == 0
    assert result["objects_examined"] >= 4
    assert result["edges_examined"] == len(result["reverse_edges"])
    edge_kinds = {edge["source_kind"] for edge in result["reverse_edges"]}
    assert edge_kinds == {"commit", "path", "ref"}
    assert any(
        edge.get("source_value") == base64.b64encode(b"Raw-Path.bin").decode()
        for edge in result["reverse_edges"]
    )


def test_scan_mirror_fails_closed_on_object_and_edge_caps(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "synthetic@example.invalid")
    git(repo, "config", "user.name", "Synthetic")
    (repo / "one").write_text("one")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "one")
    mirror = tmp_path / "mirror.git"
    subprocess.run(
        ["git", "clone", "--mirror", str(repo), str(mirror)],
        check=True,
        capture_output=True,
    )
    refs = [(git(repo, "rev-parse", "HEAD").encode(), b"refs/heads/master")]
    tiny = {
        "max_blob_bytes": 4096,
        "max_entries": 1,
        "max_findings": 20,
        "max_request_bytes": 65536,
    }
    with pytest.raises(codec.AuthorityError, match="integrity"):
        audit._scan_mirror(mirror, refs, [], tiny)


def test_remote_snapshot_includes_advertised_and_explicit_pull_refs(monkeypatch):
    oid = b"a" * 40
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        if len(calls) == 1:
            return SimpleNamespace(stdout=oid + b"\trefs/heads/main\n")
        return SimpleNamespace(stdout=oid + b"\trefs/pull/7/head\n")

    monkeypatch.setattr(audit.subprocess, "run", fake_run)
    snapshot = audit._snapshot_remote("https://example.invalid/o/r.git", {})
    assert snapshot == (
        (oid, b"refs/heads/main"),
        (oid, b"refs/pull/7/head"),
    )
    assert calls[0] == ["git", "ls-remote", "https://example.invalid/o/r.git"]
    assert calls[1][-2:] == ["refs/pull/*/head", "refs/pull/*/merge"]


def test_audit_history_fails_closed_on_snapshot_drift(monkeypatch, tmp_path):
    snapshots = [
        ((b"a" * 40, b"refs/heads/main"),),
        ((b"b" * 40, b"refs/heads/main"),),
    ]
    monkeypatch.setattr(audit, "_snapshot_remote", lambda *_args: snapshots.pop(0))
    monkeypatch.setattr(audit, "_fetch_snapshot", lambda *_args: None)
    with pytest.raises(codec.AuthorityError, match="integrity"):
        audit.audit_history(
            "https://example.invalid/o/r.git",
            tmp_path / "mirror.git",
            [],
            {
                "max_blob_bytes": 4096,
                "max_entries": 10,
                "max_findings": 10,
                "max_request_bytes": 65536,
            },
        )


def test_private_transaction_is_no_overwrite_complete_and_atomic(tmp_path):
    parent = tmp_path / "private"
    parent.mkdir()
    identity = {
        "authority_revision": REV,
        "generation": 1,
        "manifest_mac": "a" * 64,
    }
    result = private_io.write_complete_transaction(
        parent,
        REV,
        {"report.json": b"{}\n"},
        b"k" * 32,
        identity,
    )
    assert (result / "COMPLETE").is_file()
    with pytest.raises(codec.AuthorityError, match="filesystem"):
        private_io.write_complete_transaction(
            parent,
            REV,
            {"report.json": b"{}\n"},
            b"k" * 32,
            identity,
        )
    if os.name != "nt":
        assert (result.stat().st_mode & 0o077) == 0


def test_cleanup_only_removes_validated_incomplete_transaction(tmp_path):
    parent = tmp_path / "private"
    parent.mkdir()
    target = parent / f".incomplete.{REV}"
    target.mkdir()
    (target / "marker").write_bytes(b"incomplete\n")
    private_io.cleanup_incomplete(parent, REV)
    assert not target.exists()


def test_dual_slot_exact_head_and_coverage_matrix():
    current = {"slot": "current", "expected_head_oid": None}
    pending = {"slot": "pending", "expected_head_oid": "e" * 40}
    assert coverage.select_slot(current, pending, "e" * 40) is pending
    assert coverage.select_slot(current, pending, "d" * 40) is current
    scanned = {name: "scanned" for name in coverage.REQUIRED_SURFACES}
    assert coverage.classify_coverage(scanned) == "complete"
    scanned["actions"] = "unknown-residual"
    assert coverage.classify_coverage(scanned) == "residual"
    with pytest.raises(codec.AuthorityError):
        coverage.classify_coverage({"issues": "scanned"})


def test_github_residual_matrix_records_every_required_surface():
    matrix = coverage.github_residual_matrix("bounded-adapters-unavailable")
    assert set(matrix) == set(coverage.REQUIRED_SURFACES)
    assert all(
        item
        == {
            "bytes_examined": 0,
            "downloads_examined": 0,
            "pages_examined": 0,
            "permissions": "not-queried",
            "reason": "bounded-adapters-unavailable",
            "snapshot": "unavailable",
            "state": "unknown-residual",
        }
        for item in matrix.values()
    )
