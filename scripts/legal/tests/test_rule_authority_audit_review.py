"""Adversarial regressions from the Phase A2 code review."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

LEGAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LEGAL))

from rule_authority import audit_git, audit_github, audit_output, report_transaction  # noqa: E402
from rule_authority.complete import create_complete  # noqa: E402
from rule_authority.structural import SensitiveArtifacts  # noqa: E402

KEY = b"k" * 32
PATTERN = b"synthetic-block-value"
SENSITIVE = SensitiveArtifacts(KEY, (PATTERN,), (), frozenset({"sealed.bin"}))
REVISION = "12345678-1234-4234-9234-123456789abc"


def _git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=repo, input=input_bytes, capture_output=True, check=True
    )
    return result.stdout


def _repo(tmp_path: Path, payload: bytes = b"safe") -> tuple[Path, str]:
    repo = tmp_path / "source"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Synthetic")
    _git(repo, "config", "user.email", "synthetic@example.invalid")
    (repo / "value.bin").write_bytes(payload)
    _git(repo, "add", "--", "value.bin")
    _git(repo, "commit", "-qm", "synthetic")
    return repo, _git(repo, "rev-parse", "HEAD").decode().strip()


def _replace_with_safe(repo: Path, original: str) -> None:
    (repo / "value.bin").write_bytes(b"safe")
    _git(repo, "add", "--", "value.bin")
    _git(repo, "commit", "-qm", "replacement")
    replacement = _git(repo, "rev-parse", "HEAD").decode().strip()
    _git(repo, "replace", original, replacement)


def test_tree_rejects_replace_and_scans_required_ref_raw_objects(tmp_path: Path) -> None:
    repo, original = _repo(tmp_path, PATTERN)
    _replace_with_safe(repo, original)
    with pytest.raises(audit_git.CoverageError):
        audit_git.audit_tree(
            repo, original, b"refs/heads/master", SENSITIVE,
            max_entries=20, max_blob_bytes=100,
        )


@pytest.mark.parametrize("artifact", ["info/grafts", "objects/info/http-alternates"])
def test_history_rejects_graft_and_all_alternate_sources(tmp_path: Path, artifact: str) -> None:
    source, _ = _repo(tmp_path)
    mirror = tmp_path / "mirror.git"
    _git(tmp_path, "init", "--bare", "-q", str(mirror))
    os.chmod(mirror, 0o700)
    target = mirror / artifact
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("synthetic\n")
    with pytest.raises(audit_git.CoverageError):
        audit_git.audit_history(
            mirror, str(source), SENSITIVE, api_discovered_oids=(),
            max_refs=20, max_entries=20, max_blob_bytes=100,
            max_objects=40, max_edges=80,
        )


@pytest.mark.parametrize("key", ["extensions.partialClone", "remote.origin.promisor"])
def test_history_rejects_every_partial_clone_marker(tmp_path: Path, key: str) -> None:
    source, _ = _repo(tmp_path)
    mirror = tmp_path / "mirror.git"
    _git(tmp_path, "init", "--bare", "-q", str(mirror))
    os.chmod(mirror, 0o700)
    _git(mirror, "config", key, "origin" if key.startswith("extensions") else "true")
    with pytest.raises(audit_git.CoverageError):
        audit_git.audit_history(
            mirror, str(source), SENSITIVE, api_discovered_oids=(),
            max_refs=20, max_entries=20, max_blob_bytes=100,
            max_objects=40, max_edges=80,
        )


def test_git_runner_rejects_symlinked_ancestor_and_ignores_global_config(tmp_path: Path) -> None:
    repo, oid = _repo(tmp_path)
    link = tmp_path / "link"
    link.symlink_to(repo.parent, target_is_directory=True)
    with pytest.raises(audit_git.CoverageError):
        audit_git.GitRunner(link / repo.name)
    home = tmp_path / "home"
    home.mkdir()
    (home / ".gitconfig").write_text("[alias]\nboom = !exit 77\n")
    runner = audit_git.GitRunner(repo)
    try:
        assert runner.run("cat-file", "-t", oid).strip() == b"commit"
        assert runner.environment["GIT_NO_REPLACE_OBJECTS"] == "1"
        assert runner.environment["GIT_CONFIG_GLOBAL"] == os.devnull
    finally:
        runner.close()


def test_tree_scans_tag_tree_gitlink_and_ref_path_bytes(tmp_path: Path) -> None:
    repo, commit = _repo(tmp_path)
    entry = b"160000 commit " + commit.encode() + b"\t" + PATTERN + b"\x00"
    tree = _git(repo, "mktree", "-z", input_bytes=entry).strip().decode()
    tagged_commit = _git(repo, "commit-tree", tree, "-m", "safe").strip().decode()
    _git(repo, "tag", "-a", "synthetic", tagged_commit, "-m", "safe")
    tag_oid = _git(repo, "rev-parse", "refs/tags/synthetic").decode().strip()
    result = audit_git.audit_tree(
        repo, tagged_commit, b"refs/tags/synthetic", SENSITIVE,
        max_entries=20, max_blob_bytes=100,
    )
    assert result.verdict == "blocked"
    assert tag_oid.encode() in {edge[1] for edge in result.edges}
    assert commit.encode() in {edge[1] for edge in result.edges}


def test_history_owns_snapshot_fetch_pull_refs_and_api_oid_graph(tmp_path: Path) -> None:
    source, oid = _repo(tmp_path)
    _git(source, "update-ref", "refs/pull/7/head", oid)
    mirror = tmp_path / "mirror.git"
    _git(tmp_path, "init", "--bare", "-q", str(mirror))
    os.chmod(mirror, 0o700)
    result = audit_git.audit_history(
        mirror, str(source), SENSITIVE, api_discovered_oids=(oid.encode(),),
        max_refs=20, max_entries=20, max_blob_bytes=100,
        max_objects=40, max_edges=80,
    )
    assert result.verdict == "clean"
    assert any(edge[0] == b"refs/pull/7/head" for edge in result.edges)
    assert (b"api-discovered", oid.encode()) in result.edges
    configured = subprocess.run(
        ["git", "config", "--get-regexp", "^remote\\."], cwd=mirror,
        capture_output=True, check=False,
    )
    assert configured.returncode == 1


class FixtureAdapter:
    def __init__(self, pages: dict[str, list[audit_github.ApiPage]]) -> None:
        self.pages = pages

    def snapshot(self) -> str:
        return "snapshot"

    def page(self, surface: str, cursor: str | None) -> audit_github.ApiPage:
        return self.pages[surface][int(cursor or "0")]


def _pages() -> dict[str, list[audit_github.ApiPage]]:
    return {
        name: [audit_github.ApiPage(b"safe", None, "etag", 0, permission="read")]
        for name in audit_github.REQUIRED_SURFACES
    }


def _inventory(pages: dict[str, list[audit_github.ApiPage]], **overrides):
    limits = {
        "max_pages": 40, "max_bytes": 1000, "max_edges": 20,
        "max_downloads": 10, "max_compressed_bytes": 1000,
        "max_expanded_bytes": 2000,
    }
    limits.update(overrides)
    return audit_github.inventory(FixtureAdapter(pages), SENSITIVE, **limits)


def test_github_inventory_scans_payloads_downloads_and_discovers_oids() -> None:
    pages = _pages()
    pages["issues"] = [audit_github.ApiPage(PATTERN, None, "etag", 1, permission="read")]
    result = _inventory(pages)
    assert result.coverage_class == "complete"
    assert result.private_findings == (b"issues",)
    oid = b"a" * 40
    pages["commits"] = [audit_github.ApiPage(
        b"safe", None, "etag", 1, permission="read", discovered_oids=(oid,),
        download_links=1,
        downloads=(audit_github.Download(b"asset", PATTERN, 5, len(PATTERN)),),
    )]
    result = _inventory(pages)
    assert result.discovered_oids == (oid,)
    assert b"commits:asset" in result.private_findings
    assert result.surfaces["commits"].permission == "read"
    assert result.surfaces["commits"].downloads == 1


@pytest.mark.parametrize("limit", ["max_edges", "max_downloads", "max_compressed_bytes", "max_expanded_bytes"])
def test_github_inventory_global_caps_fail_closed(limit: str) -> None:
    pages = _pages()
    pages["artifacts"] = [audit_github.ApiPage(
        b"safe", None, "etag", 2, permission="read", download_links=2,
        downloads=(audit_github.Download(b"asset", b"expanded", 4, 8),
                   audit_github.Download(b"asset-2", b"expanded", 4, 8)),
    )]
    with pytest.raises(audit_github.CoverageError):
        _inventory(pages, **{limit: 1})


def test_github_inventory_requires_download_evidence() -> None:
    pages = _pages()
    pages["artifacts"] = [audit_github.ApiPage(
        b"safe", None, "etag", 0, permission="read", download_links=1,
    )]
    with pytest.raises(audit_github.CoverageError):
        _inventory(pages)


def test_zip_rejects_backslash_and_scans_extracted_bytes() -> None:
    import io
    import zipfile

    raw = io.BytesIO()
    with zipfile.ZipFile(raw, "w") as archive:
        archive.writestr("bad\\name", PATTERN)
    with pytest.raises(audit_github.CoverageError):
        audit_github.scan_zip(
            raw.getvalue(), SENSITIVE, max_entries=2, max_compressed_bytes=1000,
            max_expanded_bytes=1000, max_ratio=20, max_depth=2,
        )


def _coverage(state: str = "scanned") -> dict[str, str]:
    return {name: state for name in ("git", *audit_github.REQUIRED_SURFACES)}


def _report_files() -> dict[str, bytes]:
    return {"coverage.json": b"{}\n", "findings.bin": b"", "reachability.json": b"{}\n"}


def _fields(transaction_id: str) -> dict:
    return {
        "api_snapshot_id": "api", "authority_revision": REVISION,
        "coverage_states": _coverage(), "generation": 1,
        "manifest_mac": "a" * 64, "ref_snapshot_id": "refs",
        "schema_id": "legal-rule-complete-v1", "transaction_id": transaction_id,
    }


def test_complete_rejects_incomplete_surface_or_file_contract() -> None:
    transaction_id = str(uuid.uuid4())
    unsigned = {**_fields(transaction_id), "files": []}
    with pytest.raises(ValueError):
        create_complete(unsigned, KEY)
    unsigned["files"] = [
        {"path": "coverage.json", "sha256": "a" * 64, "size": 1}
    ]
    unsigned["coverage_states"] = {"git": "scanned"}
    with pytest.raises(ValueError):
        create_complete(unsigned, KEY)


@pytest.mark.parametrize("rc,verdict,coverage", [
    (0, "clean", "partial"), (1, "clean", "complete"),
    (3, "blocked", "partial"), (4, "clean", "complete"),
])
def test_public_result_rejects_false_tuple(rc: int, verdict: str, coverage: str) -> None:
    with pytest.raises(audit_output.PublicOutputError):
        audit_output.public_result(
            command="audit-history", revision=REVISION, generation=1,
            objects_examined=1, coverage=coverage, verdict=verdict, rc=rc,
        )


def test_report_rejects_symlink_ancestor_and_atomic_overwrite(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir(mode=0o700)
    private = real / "private"
    private.mkdir(mode=0o700)
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    transaction_id = str(uuid.uuid4())
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.write_report(
            link / "private", transaction_id, _report_files(), _fields(transaction_id), KEY
        )
    final = private / transaction_id
    final.mkdir(mode=0o700)
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.write_report(
            private, transaction_id, _report_files(), _fields(transaction_id), KEY
        )
    assert list(final.iterdir()) == []


def test_report_post_publish_fsync_failure_is_not_final(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "private"
    root.mkdir(mode=0o700)
    transaction_id = str(uuid.uuid4())
    original = os.fsync
    calls = 0

    def fail_parent(descriptor: int) -> None:
        nonlocal calls
        calls += 1
        if calls >= 6:
            raise OSError("synthetic parent fsync failure")
        original(descriptor)

    monkeypatch.setattr(os, "fsync", fail_parent)
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.write_report(
            root, transaction_id, _report_files(), _fields(transaction_id), KEY
        )
    assert not (root / transaction_id).exists()


def test_report_verify_and_cleanup_are_descriptor_relative(tmp_path: Path) -> None:
    root = tmp_path / "private"
    root.mkdir(mode=0o700)
    transaction_id = str(uuid.uuid4())
    final = report_transaction.write_report(
        root, transaction_id, _report_files(), _fields(transaction_id), KEY
    )
    assert report_transaction.verify_report(final, KEY)["transaction_id"] == transaction_id
    incomplete_id = str(uuid.uuid4())
    incomplete = root / f".incomplete.{incomplete_id}"
    incomplete.mkdir(mode=0o700)
    (incomplete / "scratch").write_bytes(b"x")
    os.chmod(incomplete / "scratch", 0o600)
    report_transaction.cleanup_incomplete(root, incomplete_id)
    assert not incomplete.exists()
