"""Exact-byte provenance and prerequisite retention regressions.

Digest oracles: RFC 6234 (2011), section 8.5, SHA256 test 1 gives
SHA256(b"abc") = ba7816bf...15ad. The newline variants were independently
calculated with sha256sum over printf 'abc\\n' and printf 'abc\\r\\n'.
No result from the production checker is used to construct these oracles.
Prerequisite outcomes follow the explicit truth table in the reporting guide.
"""

import copy
import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from report_provenance import (
    ProvenanceError,
    capture_source,
    check_manifest,
    load_manifest,
)

ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
LF = "edeaaff3f1774ad2888673770c6d64097e391bc362d7d6fb34982ddf0efd18cb"
CRLF = "552bab6864c7a7b69a502ed1854b9245c0e1a30f008aaa0b281da62585fdb025"
REPOSITORY_URL = "https://github.com/example/reference"
SCRIPT = Path(__file__).resolve().parents[2] / "scripts/reporting/report_provenance.py"


def git(repo, *args, data=None):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return subprocess.run(
        ["git", "-C", str(repo), *args], input=data, capture_output=True,
        check=True, env=env,
    ).stdout


@pytest.fixture
def source_repo(tmp_path):
    """Create disposable Git objects without configuring an identity or hooks.

    Git mktree accepts mode/type/object/tab/path records (Git mktree manual).
    The commit object's tree is built from literal fixture bytes. Its identity
    is synthetic and has no deliverable meaning; no branch is committed.
    """
    repo = tmp_path / "source"
    repo.mkdir()
    git(repo, "init")
    blob = git(repo, "hash-object", "-w", "--stdin", data=b"abc\n").strip()
    tree = git(repo, "mktree", data=b"100644 blob " + blob + b"\tevidence.txt\n").strip()
    commit = (
        b"tree " + tree + b"\nauthor Fixture <fixture> 0 +0000\n"
        b"committer Fixture <fixture> 0 +0000\n\nSynthetic evidence\n"
    )
    revision = git(repo, "hash-object", "-t", "commit", "-w", "--stdin", data=commit)
    (repo / "evidence.txt").write_bytes(b"abc\r\n")
    return repo, revision.decode().strip()


def source(source_repo, scope="git-blob-bytes", **kwargs):
    repo, revision = source_repo
    args = {
        "source_id": "input", "path": "evidence.txt", "revision": revision,
        "byte_scope": scope,
        "reader_url": f"{REPOSITORY_URL}/blob/{revision}/evidence.txt"
        if scope == "git-blob-bytes" else None,
        "repository_url": REPOSITORY_URL,
    }
    args.update(kwargs)
    return capture_source(repo, **args)


def manifest(source_repo):
    return {
        "schema": "report-provenance-v1", "report_id": "example",
        "revision": "initial", "repository_url": REPOSITORY_URL,
        "sources": [source(source_repo)],
        "prerequisites": [{"id": "qualified-quantity", "status": "unmet"}],
    }


def successor(old):
    raw = json.dumps(old).encode()
    new = copy.deepcopy(old)
    new["revision"] = "corrected"
    new["supersedes"] = {
        "report_id": old["report_id"], "revision": old["revision"],
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    return new, raw


def test_checkout_and_blob_are_distinct_exact_bytes(source_repo):
    repo, _ = source_repo
    before = (repo / "evidence.txt").read_bytes()
    assert source(source_repo)["sha256"] == LF
    assert source(source_repo, "checkout-bytes")["sha256"] == CRLF
    assert (repo / "evidence.txt").read_bytes() == before


def test_rfc_sha256_vector(source_repo):
    repo, _ = source_repo
    (repo / "evidence.txt").write_bytes(b"abc")
    assert source(source_repo, "checkout-bytes")["sha256"] == ABC


def test_blob_verifies_when_checkout_is_changed_or_missing(source_repo):
    repo, _ = source_repo
    record = manifest(source_repo)
    (repo / "evidence.txt").unlink()
    assert check_manifest(record, repo)["status"] == "PASS"


def test_checkout_digest_cannot_verify_reader_blob(source_repo):
    repo, _ = source_repo
    record = manifest(source_repo)
    record["sources"][0]["sha256"] = CRLF
    result = check_manifest(record, repo)
    assert result["status"] == "FAIL"
    assert result["sources"][0]["reason"] == "digest mismatch"


@pytest.mark.parametrize("scope", ["normalized-text", "", None])
def test_unknown_scope_rejected(source_repo, scope):
    with pytest.raises(ProvenanceError, match="byte scope"):
        source(source_repo, scope)


@pytest.mark.parametrize("revision", ["HEAD", "main", "-h", "abc123"])
def test_mutable_or_abbreviated_revision_rejected(source_repo, revision):
    with pytest.raises(ProvenanceError, match="revision"):
        source(source_repo, revision=revision)


@pytest.mark.parametrize("path", ["../evidence.txt", "/evidence.txt", "a/../evidence.txt",
                                  "./evidence.txt", "a\\evidence.txt", ":(glob)*", ""])
def test_unsafe_or_noncanonical_paths_rejected(source_repo, path):
    with pytest.raises(ProvenanceError):
        source(source_repo, path=path)


@pytest.mark.parametrize("url", [
    "https://github.com/example/reference/blob/main/evidence.txt",
    "https://github.com/example/other/blob/{revision}/evidence.txt",
    "https://github.com/example/reference/blob/{revision}/other.txt",
    "https://github.com/example/reference/blob/{revision}/evidence.txt?raw=1",
    "https://github.com/example/reference/blob/{revision}/evidence.txt#L1",
    "http://github.com/example/reference/blob/{revision}/evidence.txt",
    "https://github.com.evil.invalid/example/reference/blob/{revision}/evidence.txt",
])
def test_reader_link_must_match_scope_repository_revision_and_path(source_repo, url):
    with pytest.raises(ProvenanceError, match="reader link"):
        source(source_repo, reader_url=url.format(revision=source_repo[1]))


def test_raw_reader_url_supported(source_repo):
    record = source(source_repo, reader_url=(
        f"https://raw.githubusercontent.com/example/reference/{source_repo[1]}/evidence.txt"
    ))
    assert record["sha256"] == LF


def test_checkout_cannot_claim_published_blob_link(source_repo):
    with pytest.raises(ProvenanceError, match="reader link"):
        source(source_repo, "checkout-bytes", reader_url="https://github.com/example/reference")


def test_inherited_git_binding_does_not_redirect_source_read(source_repo, monkeypatch, tmp_path):
    alien = tmp_path / "alien"
    alien.mkdir()
    git(alien, "init")
    monkeypatch.setenv("GIT_DIR", str(alien / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(alien))
    monkeypatch.setenv("GIT_COMMON_DIR", str(alien / ".git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(alien / "index"))
    assert source(source_repo)["sha256"] == LF
    assert not (alien / "index").exists()


def test_checkout_symlink_rejected(source_repo, tmp_path):
    repo, _ = source_repo
    outside = tmp_path / "outside"
    outside.write_bytes(b"abc")
    (repo / "evidence.txt").unlink()
    (repo / "evidence.txt").symlink_to(outside)
    with pytest.raises(ProvenanceError, match="regular file"):
        source(source_repo, "checkout-bytes")


def test_checkout_only_has_no_reader_verification(source_repo):
    repo, _ = source_repo
    data = manifest(source_repo)
    data["sources"] = [source(source_repo, "checkout-bytes")]
    result = check_manifest(data, repo)
    assert result["status"] == "NOT_EVALUATED"
    assert result["sources"][0]["status"] == "PASS"


def test_unmet_prerequisite_must_carry_forward(source_repo):
    repo, _ = source_repo
    old = manifest(source_repo)
    new, raw = successor(old)
    assert check_manifest(new, repo, previous_bytes=raw)["status"] == "PASS"
    new["prerequisites"] = []
    assert check_manifest(new, repo, previous_bytes=raw)["status"] == "FAIL"


def test_relabeling_unmet_as_met_requires_disposition(source_repo):
    repo, _ = source_repo
    new, raw = successor(manifest(source_repo))
    new["prerequisites"][0]["status"] = "met"
    assert check_manifest(new, repo, previous_bytes=raw)["status"] == "FAIL"


@pytest.mark.parametrize("action", ["satisfied", "withdrawn"])
def test_explicit_evidenced_disposition(source_repo, action):
    repo, _ = source_repo
    new, raw = successor(manifest(source_repo))
    new["prerequisites"] = ([{"id": "qualified-quantity", "status": "met"}]
                            if action == "satisfied" else [])
    new["dispositions"] = [{
        "id": "qualified-quantity", "action": action,
        "reason": "Explicit technical disposition", "evidence_source_id": "input",
    }]
    assert check_manifest(new, repo, previous_bytes=raw)["status"] == "PASS"
    new["dispositions"][0]["evidence_source_id"] = "absent"
    assert check_manifest(new, repo, previous_bytes=raw)["status"] == "FAIL"


@pytest.mark.parametrize("mutation", ["missing", "digest", "identity", "same-revision"])
def test_supersession_binds_exact_predecessor(source_repo, mutation):
    repo, _ = source_repo
    new, raw = successor(manifest(source_repo))
    if mutation == "missing":
        raw = None
    elif mutation == "digest":
        raw += b"\n"
    elif mutation == "identity":
        new["supersedes"]["report_id"] = "other"
    else:
        new["revision"] = "initial"
    assert check_manifest(new, repo, previous_bytes=raw)["status"] == "FAIL"


@pytest.mark.parametrize("field", ["sources", "prerequisites"])
def test_duplicate_identifiers_fail_closed(source_repo, field):
    repo, _ = source_repo
    data = manifest(source_repo)
    data[field].append(copy.deepcopy(data[field][0]))
    assert check_manifest(data, repo)["status"] == "FAIL"


@pytest.mark.parametrize("raw", [b'{"sources": [], "sources": []}', b'{"value": NaN}'])
def test_ambiguous_json_rejected(raw):
    with pytest.raises(ProvenanceError):
        load_manifest(raw)


def test_cli_pass_and_failure_exit_codes(source_repo, tmp_path):
    repo, _ = source_repo
    path = tmp_path / "manifest.json"
    data = manifest(source_repo)
    for expected_code, digest in [(0, LF), (1, CRLF)]:
        data["sources"][0]["sha256"] = digest
        path.write_text(json.dumps(data), encoding="utf-8", newline="\n")
        result = subprocess.run(
            [os.sys.executable, str(SCRIPT), str(path), "--repository", str(repo)],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        assert result.returncode == expected_code
        assert json.loads(result.stdout)["status"] == ("PASS" if expected_code == 0 else "FAIL")


@pytest.mark.parametrize("field,value", [
    ("repository_url", "https://[invalid"),
    ("sources", None),
    ("prerequisites", {"id": "quantity"}),
])
def test_malformed_manifest_fails_without_traceback(source_repo, field, value):
    data = manifest(source_repo)
    data[field] = value
    assert check_manifest(data, source_repo[0])["status"] == "FAIL"


@pytest.mark.parametrize("field,value", [
    ("reader_url", "https://[invalid"),
    ("reader_url", []),
    ("byte_scope", {}),
    ("sha256", ABC.upper()),
    ("git_blob_oid", LF),
])
def test_malformed_source_claims_fail_closed(source_repo, field, value):
    data = manifest(source_repo)
    data["sources"][0][field] = value
    assert check_manifest(data, source_repo[0])["status"] == "FAIL"


def test_failed_supersession_keeps_all_source_diagnostics(source_repo):
    repo, _ = source_repo
    new, raw = successor(manifest(source_repo))
    new["prerequisites"] = []
    checkout = source(source_repo, "checkout-bytes", source_id="executed")
    checkout["sha256"] = ABC
    new["sources"].append(checkout)
    result = check_manifest(new, repo, previous_bytes=raw)
    assert result["status"] == "FAIL"
    assert [entry["status"] for entry in result["sources"]] == ["PASS", "FAIL"]
    assert result["supersession"]["status"] == "FAIL"


@pytest.mark.parametrize("mutation", ["empty-reason", "unknown-action", "duplicate", "checkout-evidence"])
def test_invalid_dispositions_do_not_clear_prerequisite(source_repo, mutation):
    repo, _ = source_repo
    new, raw = successor(manifest(source_repo))
    new["prerequisites"] = []
    disposition = {
        "id": "qualified-quantity", "action": "withdrawn",
        "reason": "Changed technical basis", "evidence_source_id": "input",
    }
    new["dispositions"] = [disposition]
    if mutation == "empty-reason":
        disposition["reason"] = " "
    elif mutation == "unknown-action":
        disposition["action"] = "ignore"
    elif mutation == "duplicate":
        new["dispositions"].append(copy.deepcopy(disposition))
    else:
        new["sources"] = [source(source_repo, "checkout-bytes")]
    assert check_manifest(new, repo, previous_bytes=raw)["status"] == "FAIL"


def test_previous_argument_cannot_be_ignored(source_repo):
    data = manifest(source_repo)
    assert check_manifest(data, source_repo[0], previous_bytes=b"{}")["status"] == "FAIL"


def test_nonempty_sources_required(source_repo):
    data = manifest(source_repo)
    data["sources"] = []
    assert check_manifest(data, source_repo[0])["status"] == "FAIL"


def test_documented_worked_sidecar(source_repo):
    """Published example has LF bytes; the independently hashed checkout has CRLF.

    The expected PASS follows exact LF == LF and CRLF == CRLF comparisons.
    Setting the published digest to CRLF instead gives LF != CRLF, hence FAIL.
    An unmet engineering prerequisite remains unmet under both outcomes.
    """
    example = SCRIPT.parents[2] / "examples/reporting/provenance-sidecar.json"
    data = load_manifest(example.read_bytes())
    assert data["sources"][0]["revision"] == source_repo[1]
    assert check_manifest(data, source_repo[0])["status"] == "PASS"
    data["sources"][0]["sha256"] = CRLF
    assert check_manifest(data, source_repo[0])["status"] == "FAIL"
    assert data["prerequisites"][0]["status"] == "unmet"


@pytest.mark.parametrize("prefix", [
    "https://github.com/example/reference/blob/",
    "https://raw.githubusercontent.com/example/reference/",
])
@pytest.mark.parametrize("encoded,valid", [("%FF", False), ("%EF%BF%BD", True)])
def test_reader_path_requires_exact_utf8(source_repo, prefix, encoded, valid):
    repo, _ = source_repo
    blob = git(repo, "hash-object", "-w", "--stdin", data=b"abc\n").strip()
    tree = git(repo, "mktree", data=(
        b"100644 blob " + blob + b"\t" + "\ufffd.txt".encode("utf-8") + b"\n"
    )).strip()
    commit = (b"tree " + tree + b"\nauthor Fixture <fixture> 0 +0000\n"
              b"committer Fixture <fixture> 0 +0000\n\nUnicode evidence\n")
    revision = git(repo, "hash-object", "-t", "commit", "-w", "--stdin", data=commit)
    revision = revision.decode("ascii").strip()
    data = manifest(source_repo)
    data["sources"][0].update(
        path="\ufffd.txt", revision=revision,
        reader_url=f"{prefix}{revision}/{encoded}.txt",
    )
    data["sources"][0].pop("git_blob_oid")
    result = check_manifest(data, repo)
    assert result["status"] == ("PASS" if valid else "FAIL")
    if not valid:
        assert result["sources"][0]["reason"] == "invalid reader link"


@pytest.mark.parametrize("path", [chr(0xD800) + ".txt", chr(0xDFFF) + ".txt",
                                  "a" + chr(0xDFFF) + chr(0xD800) + ".txt"])
def test_surrogate_source_path_rejected_before_git(source_repo, monkeypatch, path):
    def unexpected_git(*args):
        pytest.fail("invalid source path reached Git")

    monkeypatch.setattr("report_provenance._git", unexpected_git)
    with pytest.raises(ProvenanceError, match="^invalid source path$"):
        source(source_repo, path=path)


@pytest.mark.parametrize("path", [chr(0xD800) + ".txt", chr(0xDFFF) + ".txt",
                                  "a" + chr(0xDFFF) + chr(0xD800) + ".txt"])
def test_surrogate_source_path_cli_json_failure(source_repo, tmp_path, path):
    data = manifest(source_repo)
    data["sources"][0]["path"] = path
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(data), encoding="utf-8", newline="\n")
    result = subprocess.run(
        [os.sys.executable, str(SCRIPT), str(manifest_path),
         "--repository", str(source_repo[0])],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    assert result.returncode == 1
    assert result.stderr == ""
    observed = json.loads(result.stdout)
    assert observed["status"] == "FAIL"
    assert observed["sources"][0]["reason"] == "invalid source path"


def test_checkout_junction_rejected(source_repo, monkeypatch):
    repo, _ = source_repo
    original_lstat = Path.lstat

    def junction_lstat(self, **kwargs):
        observed = original_lstat(self, **kwargs)
        if self == repo / "evidence.txt":
            return SimpleNamespace(st_mode=observed.st_mode,
                                   st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)
        return observed

    monkeypatch.setattr(Path, "lstat", junction_lstat)
    with pytest.raises(ProvenanceError, match="regular file"):
        source(source_repo, "checkout-bytes")
