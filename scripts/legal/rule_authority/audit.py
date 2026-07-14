"""Fail-closed raw-object Git scanning with private reverse-edge evidence."""

from __future__ import annotations

import base64
import os
import re
import subprocess
from pathlib import Path

from .codec import AuthorityError


OID = re.compile(rb"[0-9a-f]{40,64}")
OBJECT_TYPES = {b"blob", b"commit", b"tag", b"tree"}


def _git(git_dir, *args, binary=False):
    try:
        result = subprocess.run(
            ["git", f"--git-dir={git_dir}", *args], capture_output=True, check=True
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise AuthorityError("integrity") from exc
    return result.stdout if binary else result.stdout.decode("ascii").strip()


def _ascii_fold(value):
    return value.translate(
        bytes.maketrans(b"ABCDEFGHIJKLMNOPQRSTUVWXYZ", b"abcdefghijklmnopqrstuvwxyz")
    )


def _matches(data, rules, surface):
    """Return block/warn rule counts without decoding attacker-controlled bytes."""
    block = warn = 0
    for rule in rules:
        if isinstance(rule, bytes):
            rule = {
                "pattern": rule,
                "match_mode": "exact-bytes",
                "severity": "block",
                "target": "both",
            }
        if not isinstance(rule, dict):
            raise AuthorityError("integrity")
        target = rule.get("target")
        if target not in {surface, "both"}:
            continue
        pattern = rule.get("pattern")
        mode = rule.get("match_mode")
        severity = rule.get("severity")
        if not isinstance(pattern, bytes) or not pattern:
            raise AuthorityError("integrity")
        if mode == "ascii-fold":
            matched = _ascii_fold(pattern) in _ascii_fold(data)
        elif mode == "exact-bytes":
            matched = pattern in data
        else:
            raise AuthorityError("integrity")
        if severity not in {"block", "warn"}:
            raise AuthorityError("integrity")
        if matched:
            if severity == "block":
                block += 1
            else:
                warn += 1
    return block, warn


def _add_counts(counts, addition, limits):
    counts[0] += addition[0]
    counts[1] += addition[1]
    if sum(counts) > limits["max_findings"]:
        raise AuthorityError("integrity")


def audit_tree(git_dir, commit_oid, required_ref, rules, limits):
    git_dir = Path(git_dir)
    try:
        oid_bytes = commit_oid.encode("ascii")
    except (AttributeError, UnicodeError):
        raise AuthorityError("integrity") from None
    if not OID.fullmatch(oid_bytes) or not required_ref.startswith("refs/"):
        raise AuthorityError("integrity")
    if _git(git_dir, "rev-parse", required_ref) != commit_oid:
        raise AuthorityError("integrity")
    records = _git(
        git_dir, "ls-tree", "-rz", "-r", "--full-tree", commit_oid, binary=True
    ).split(b"\0")[:-1]
    if len(records) > limits["max_entries"]:
        raise AuthorityError("integrity")
    counts = [0, 0]
    _add_counts(
        counts,
        _matches(
            _git(git_dir, "cat-file", "commit", commit_oid, binary=True),
            rules,
            "content",
        ),
        limits,
    )
    _add_counts(counts, _matches(required_ref.encode(), rules, "path"), limits)
    examined = 1
    for record in records:
        metadata, path = record.split(b"\t", 1)
        _add_counts(counts, _matches(path, rules, "path"), limits)
        oid = metadata.split()[2].decode("ascii")
        blob = _git(git_dir, "cat-file", "blob", oid, binary=True)
        if len(blob) > limits["max_blob_bytes"]:
            raise AuthorityError("integrity")
        _add_counts(counts, _matches(blob, rules, "content"), limits)
        examined += 1
    return {
        "coverage": "complete",
        "findings": counts[0],
        "warnings": counts[1],
        "objects_examined": examined,
    }


def _parse_snapshot(raw):
    refs = set()
    for line in raw.splitlines():
        try:
            oid, ref = line.split(b"\t", 1)
        except ValueError:
            raise AuthorityError("integrity") from None
        if (
            not OID.fullmatch(oid)
            or (ref != b"HEAD" and not ref.startswith(b"refs/"))
            or b"\0" in ref
        ):
            raise AuthorityError("integrity")
        refs.add((oid, ref))
    return refs


def _snapshot_remote(remote_url, environment):
    snapshots = []
    for patterns in ((), ("refs/pull/*/head", "refs/pull/*/merge")):
        try:
            snapshots.append(
                subprocess.run(
                    ["git", "ls-remote", remote_url, *patterns],
                    capture_output=True,
                    check=True,
                    env=environment,
                ).stdout
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise AuthorityError("integrity") from exc
    return tuple(sorted(_parse_snapshot(b"".join(snapshots))))


def _fetch_snapshot(remote_url, mirror_dir, refs, environment):
    mirror_dir = Path(mirror_dir)
    if mirror_dir.exists():
        raise AuthorityError("integrity")
    try:
        subprocess.run(
            ["git", "init", "--bare", str(mirror_dir)],
            capture_output=True,
            check=True,
            env=environment,
        )
        for index, (oid, _ref) in enumerate(refs):
            subprocess.run(
                [
                    "git",
                    f"--git-dir={mirror_dir}",
                    "-c",
                    "credential.helper=",
                    "-c",
                    "core.hooksPath=/dev/null",
                    "fetch",
                    "--no-tags",
                    remote_url,
                    f"{oid.decode('ascii')}:refs/audit/{index}",
                ],
                capture_output=True,
                check=True,
                env=environment,
            )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise AuthorityError("integrity") from exc


def _edge(oid, kind, value, commit=None):
    edge = {"object_oid": oid, "source_kind": kind, "source_value": value}
    if commit is not None:
        edge["source_commit"] = commit
    return tuple(sorted(edge.items()))


def _scan_mirror(git_dir, refs, rules, limits):
    """Scan each unique raw object once while retaining all reverse edges."""
    if len(refs) > limits["max_entries"]:
        raise AuthorityError("integrity")
    object_oids = set()
    edges = set()
    counts = [0, 0]
    max_entries = limits["max_entries"]

    def add_object(value):
        object_oids.add(value)
        if len(object_oids) > max_entries:
            raise AuthorityError("integrity")

    def add_edge(value):
        edges.add(value)
        if len(edges) > max_entries:
            raise AuthorityError("integrity")

    def bounded_lines(*git_args):
        raw = _git(git_dir, *git_args, binary=True)
        if len(raw) > limits["max_request_bytes"]:
            raise AuthorityError("integrity")
        lines = raw.splitlines()
        if len(lines) > max_entries:
            raise AuthorityError("integrity")
        return lines

    for oid_raw, ref_raw in refs:
        if not OID.fullmatch(oid_raw) or (
            ref_raw != b"HEAD" and not ref_raw.startswith(b"refs/")
        ):
            raise AuthorityError("integrity")
        oid = oid_raw.decode("ascii")
        _add_counts(counts, _matches(ref_raw, rules, "path"), limits)
        reachable = bounded_lines("rev-list", "--objects", "--no-object-names", oid)
        commits = bounded_lines("rev-list", oid)
        for object_raw in reachable:
            if not OID.fullmatch(object_raw):
                raise AuthorityError("integrity")
            object_oid = object_raw.decode("ascii")
            add_object(object_oid)
            add_edge(
                _edge(object_oid, "ref", base64.b64encode(ref_raw).decode("ascii"))
            )
        for commit_raw in commits:
            if not OID.fullmatch(commit_raw):
                raise AuthorityError("integrity")
            commit = commit_raw.decode("ascii")
            commit_reachable = bounded_lines(
                "rev-list", "--objects", "--no-object-names", commit
            )
            for object_raw in commit_reachable:
                if not OID.fullmatch(object_raw):
                    raise AuthorityError("integrity")
                object_oid = object_raw.decode("ascii")
                add_edge(_edge(object_oid, "commit", commit))
            tree_raw = _git(
                git_dir,
                "ls-tree",
                "-rz",
                "-r",
                "-t",
                "--full-tree",
                commit,
                binary=True,
            )
            if len(tree_raw) > limits["max_request_bytes"]:
                raise AuthorityError("integrity")
            tree_records = tree_raw.split(b"\0")[:-1]
            if len(tree_records) > max_entries:
                raise AuthorityError("integrity")
            for record in tree_records:
                try:
                    metadata, path = record.split(b"\t", 1)
                    path_oid = metadata.split()[2].decode("ascii")
                except (ValueError, IndexError, UnicodeError):
                    raise AuthorityError("integrity") from None
                if not OID.fullmatch(path_oid.encode("ascii")):
                    raise AuthorityError("integrity")
                _add_counts(counts, _matches(path, rules, "path"), limits)
                add_edge(
                    _edge(
                        path_oid,
                        "path",
                        base64.b64encode(path).decode("ascii"),
                        commit,
                    )
                )
    raw_bytes = 0
    for oid in sorted(object_oids):
        object_type = _git(git_dir, "cat-file", "-t", oid, binary=True).strip()
        if object_type not in OBJECT_TYPES:
            raise AuthorityError("integrity")
        raw = _git(git_dir, "cat-file", object_type.decode("ascii"), oid, binary=True)
        if len(raw) > limits["max_blob_bytes"]:
            raise AuthorityError("integrity")
        raw_bytes += len(raw)
        if raw_bytes > limits["max_request_bytes"]:
            raise AuthorityError("integrity")
        _add_counts(counts, _matches(raw, rules, "content"), limits)

    reverse_edges = [dict(edge) for edge in sorted(edges)]
    return {
        "coverage": "git-complete-api-residual",
        "findings": counts[0],
        "warnings": counts[1],
        "objects_examined": len(object_oids),
        "refs_examined": len(refs),
        "edges_examined": len(reverse_edges),
        "reverse_edges": reverse_edges,
    }


def audit_history(remote_url, mirror_dir, rules, limits):
    if (
        not remote_url.startswith("https://")
        or "@" in remote_url.split("//", 1)[1].split("/", 1)[0]
    ):
        raise AuthorityError("integrity")
    environment = {
        "PATH": os.environ.get("PATH", ""),
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
    }
    before = _snapshot_remote(remote_url, environment)
    if len(before) > limits["max_entries"]:
        raise AuthorityError("integrity")
    _fetch_snapshot(remote_url, mirror_dir, before, environment)
    after = _snapshot_remote(remote_url, environment)
    if before != after:
        raise AuthorityError("integrity")
    return _scan_mirror(mirror_dir, before, rules, limits)
