#!/usr/bin/env python3
"""Verify report sidecars against exact checkout bytes and pinned Git blobs.

Method: SHA-256 over unmodified bytes (RFC 6234, 2011, sections 6 and 8.5).
Git cat-file <type> <object> returns object content without checkout filters;
see https://git-scm.com/docs/git-cat-file, OPTIONS. Checkout conversion is
specified by https://git-scm.com/docs/gitattributes, text and eol attributes.
A PASS checks content and declared continuity, never engineering acceptance,
publication, source rights or the authority of a prerequisite disposition.
"""

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


class ProvenanceError(ValueError):
    """A provenance claim cannot be established from the supplied evidence."""


# RFC 6234 (2011), section 6.2: SHA-256 has a 256-bit digest, 64 hex digits.
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_SCOPES = {"checkout-bytes", "git-blob-bytes"}


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ProvenanceError(f"invalid {label}")
    return value


def _git(root, *args):
    # Caller Git bindings must never redirect a read into another checkout.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    try:
        return subprocess.run(
            ["git", "--literal-pathspecs", "-C", str(root), *args],
            check=True, capture_output=True, env=env,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        # Git stderr may contain restricted locators. Do not relay it.
        raise ProvenanceError("Git source unavailable") from exc


def _path(value):
    value = _text(value, "source path")
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise ProvenanceError("invalid source path") from exc
    path = PurePosixPath(value)
    if (path.is_absolute() or path.as_posix() != value or ".." in path.parts
            or not path.parts or "\\" in value or ":" in value or "\x00" in value):
        raise ProvenanceError("invalid source path")
    return value


def _repository_url(value):
    value = _text(value, "repository URL")
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise ProvenanceError("invalid repository URL") from exc
    parts = parsed.path.split("/")
    if (parsed.scheme != "https" or parsed.netloc != "github.com"
            or parsed.query or parsed.fragment or len(parts) != 3
            or any(not re.fullmatch(r"[A-Za-z0-9_.-]+", part) for part in parts[1:])
            or any(part in {".", ".."} for part in parts[1:])):
        raise ProvenanceError("invalid repository URL")
    return parsed.path


def _reader_link(url, repository_url, revision, path, scope):
    if scope == "checkout-bytes":
        if url is not None:
            raise ProvenanceError("reader link cannot identify checkout bytes")
        return
    repository_path = _repository_url(repository_url)
    url = _text(url, "reader link")
    try:
        parsed = urlsplit(url)
        decoded_path = unquote(parsed.path, encoding="utf-8", errors="strict")
    except (ValueError, UnicodeError) as exc:
        raise ProvenanceError("invalid reader link") from exc
    expected = {
        "github.com": f"{repository_path}/blob/{revision}/{path}",
        "raw.githubusercontent.com": f"{repository_path}/{revision}/{path}",
    }
    if (parsed.scheme != "https" or parsed.query or parsed.fragment
            or parsed.netloc not in expected
            or decoded_path != expected[parsed.netloc]):
        raise ProvenanceError("reader link does not match pinned source")


def capture_source(repository, *, source_id, path, revision, byte_scope,
                   repository_url, reader_url=None):
    """Capture a raw digest and its immutable source identity without mutation.

    Checkout bytes may differ from the pinned baseline. A checkout record has
    no published reader URL. Record a second git-blob-bytes entry for that link.
    Only regular files are supported; no symlinks, gitlinks or LFS retrieval.
    """
    source_id = _text(source_id, "source identifier")
    path = _path(path)
    _repository_url(repository_url)
    if byte_scope not in _SCOPES:
        raise ProvenanceError("invalid byte scope")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]+", revision):
        raise ProvenanceError("revision must be a full commit identifier")
    root = Path(repository).resolve()
    resolved_root = Path(os.fsdecode(_git(root, "rev-parse", "--show-toplevel")).strip()).resolve()
    if resolved_root != root:
        raise ProvenanceError("repository must identify the checkout root")
    try:
        resolved = _git(root, "rev-parse", "--verify", f"{revision}^{{commit}}").decode().strip()
    except ProvenanceError as exc:
        raise ProvenanceError("source revision unavailable") from exc
    if resolved != revision:
        raise ProvenanceError("revision must be a full commit identifier")
    entry = _git(root, "ls-tree", "-z", revision, "--", path)
    try:
        info, name = entry.rstrip(b"\0").split(b"\t", 1)
        mode, kind, oid = info.split()
    except ValueError as exc:
        raise ProvenanceError("source is not a regular file at revision") from exc
    # Git gitformat-index, Index entry (online edition consulted 2026-10-22):
    # regular type bits 1000 and permissions 0644/0755 give modes 100644/100755.
    if (mode not in {b"100644", b"100755"} or kind != b"blob"
            or os.fsdecode(name) != path):
        raise ProvenanceError("source is not a regular file at revision")
    _reader_link(reader_url, repository_url, revision, path, byte_scope)
    if byte_scope == "git-blob-bytes":
        payload = _git(root, "cat-file", "blob", oid.decode())
    else:
        candidate = root / path
        try:
            # Reject links at every component, even ones pointing inside root.
            current = root
            for component in PurePosixPath(path).parts:
                current /= component
                if (current.is_symlink()
                        or getattr(current.lstat(), "st_file_attributes", 0)
                        & stat.FILE_ATTRIBUTE_REPARSE_POINT):
                    raise ProvenanceError("checkout source must be a regular file")
            if not stat.S_ISREG(candidate.stat().st_mode):
                raise ProvenanceError("checkout source must be a regular file")
            payload = candidate.read_bytes()
        except OSError as exc:
            raise ProvenanceError("checkout source unavailable") from exc
    result = {
        "source_id": source_id, "path": path, "revision": revision,
        "byte_scope": byte_scope, "sha256": hashlib.sha256(payload).hexdigest(),
        "git_blob_oid": oid.decode(),
    }
    if reader_url is not None:
        result["reader_url"] = reader_url
    return result


def load_manifest(raw):
    """Parse JSON without silently discarding duplicate keys or NaN values."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ProvenanceError("duplicate JSON field")
            result[key] = value
        return result

    def invalid_constant(_value):
        raise ProvenanceError("non-finite JSON value")

    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)
    except (ValueError, UnicodeError) as exc:
        raise ProvenanceError("invalid or ambiguous JSON manifest") from exc


def _indexed(items, key, label):
    if not isinstance(items, list):
        raise ProvenanceError(f"invalid {label} list")
    result = {}
    for item in items:
        if not isinstance(item, dict):
            raise ProvenanceError(f"invalid {label} entry")
        identifier = _text(item.get(key), f"{label} identifier")
        if identifier in result:
            raise ProvenanceError(f"duplicate {label} identifier")
        result[identifier] = item
    return result


def _header(manifest):
    if not isinstance(manifest, dict) or manifest.get("schema") != "report-provenance-v1":
        raise ProvenanceError("unsupported manifest schema")
    _text(manifest.get("report_id"), "report identifier")
    _text(manifest.get("revision"), "report revision")
    _repository_url(manifest.get("repository_url"))
    sources = _indexed(manifest.get("sources"), "source_id", "source")
    if not sources:
        raise ProvenanceError("sources must not be empty")
    prerequisites = _indexed(manifest.get("prerequisites"), "id", "prerequisite")
    for item in prerequisites.values():
        if item.get("status") not in {"met", "unmet"}:
            raise ProvenanceError("invalid prerequisite status")
    return sources, prerequisites


def _supersession(manifest, prerequisites, sources, previous_bytes):
    dispositions = _indexed(manifest.get("dispositions", []), "id", "disposition")
    pointer = manifest.get("supersedes")
    if pointer is None:
        if previous_bytes is not None or dispositions:
            raise ProvenanceError("supersession pointer required")
        return "NOT_APPLICABLE"
    if not isinstance(pointer, dict) or previous_bytes is None:
        raise ProvenanceError("exact predecessor bytes required")
    previous = load_manifest(previous_bytes)
    _, old_prerequisites = _header(previous)
    if (pointer.get("sha256") != hashlib.sha256(previous_bytes).hexdigest()
            or pointer.get("report_id") != previous["report_id"]
            or pointer.get("revision") != previous["revision"]
            or manifest["report_id"] != previous["report_id"]
            or manifest["revision"] == previous["revision"]):
        raise ProvenanceError("predecessor identity or digest mismatch")
    unmet = {key for key, item in old_prerequisites.items() if item["status"] == "unmet"}
    if dispositions.keys() - unmet:
        raise ProvenanceError("disposition does not identify an unmet predecessor prerequisite")
    for identifier in unmet:
        current = prerequisites.get(identifier)
        disposition = dispositions.get(identifier)
        if disposition is None:
            if current is None or current["status"] != "unmet":
                raise ProvenanceError("unmet prerequisite requires carry-forward or disposition")
            continue
        _text(disposition.get("reason"), "disposition reason")
        evidence = sources.get(disposition.get("evidence_source_id"))
        if evidence is None or evidence.get("byte_scope") != "git-blob-bytes":
            raise ProvenanceError("disposition requires pinned evidence source")
        action = disposition.get("action")
        if action == "satisfied" and current and current["status"] == "met":
            continue
        if action == "withdrawn" and current is None:
            continue
        raise ProvenanceError("disposition action conflicts with current prerequisite")
    return "PASS"


def check_manifest(manifest, repository, *, previous_bytes=None):
    """Check all sources and continuity; retain diagnostics after any failure."""
    result = {"status": "FAIL", "sources": [], "supersession": {"status": "FAIL"}}
    try:
        sources, prerequisites = _header(manifest)
    except (ProvenanceError, TypeError) as exc:
        result["reason"] = str(exc) if isinstance(exc, ProvenanceError) else "invalid manifest type"
        return result
    for identifier, entry in sources.items():
        observation = {"source_id": identifier, "status": "FAIL"}
        try:
            if not isinstance(entry.get("sha256"), str) or not _DIGEST.fullmatch(entry["sha256"]):
                raise ProvenanceError("invalid SHA-256 digest")
            captured = capture_source(
                repository, source_id=identifier, path=entry.get("path"),
                revision=entry.get("revision"), byte_scope=entry.get("byte_scope"),
                repository_url=manifest["repository_url"], reader_url=entry.get("reader_url"),
            )
            if captured["sha256"] != entry["sha256"]:
                raise ProvenanceError("digest mismatch")
            if "git_blob_oid" in entry and captured["git_blob_oid"] != entry["git_blob_oid"]:
                raise ProvenanceError("Git blob identifier mismatch")
            observation["status"] = "PASS"
        except (ProvenanceError, TypeError) as exc:
            # Do not include raw malformed values or filesystem error messages.
            observation["reason"] = str(exc) if isinstance(exc, ProvenanceError) else "invalid source type"
        result["sources"].append(observation)
    try:
        status = _supersession(manifest, prerequisites, sources, previous_bytes)
        result["supersession"] = {"status": status}
    except (ProvenanceError, TypeError) as exc:
        result["supersession"]["reason"] = (
            str(exc) if isinstance(exc, ProvenanceError) else "invalid supersession type"
        )
    if (all(item["status"] == "PASS" for item in result["sources"])
            and result["supersession"]["status"] != "FAIL"):
        result["status"] = ("PASS" if any(item.get("reader_url") for item in sources.values())
                            else "NOT_EVALUATED")
    result["limits"] = [
        "Reader content is checked against local Git objects; remote publication is not checked.",
        "Disposition evidence and authority require independent engineering review.",
    ]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--previous", type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.manifest.read_bytes())
        previous = args.previous.read_bytes() if args.previous else None
        result = check_manifest(manifest, args.repository, previous_bytes=previous)
    except (OSError, ProvenanceError):
        result = {"status": "FAIL", "reason": "manifest input unavailable or invalid"}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
