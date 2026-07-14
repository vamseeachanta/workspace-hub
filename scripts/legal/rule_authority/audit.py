"""Raw-object Git scanning with fixed aggregate results."""

from __future__ import annotations

import re
import os
import subprocess
from pathlib import Path

from .codec import AuthorityError


OID = re.compile(r"[0-9a-f]{40,64}")


def _git(git_dir, *args, binary=False):
    try:
        result = subprocess.run(
            ["git", f"--git-dir={git_dir}", *args], capture_output=True, check=True
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise AuthorityError("integrity") from exc
    return result.stdout if binary else result.stdout.decode("ascii").strip()


def _matches(data, patterns):
    return sum(1 for pattern in patterns if pattern in data)


def audit_tree(git_dir, commit_oid, required_ref, patterns, limits):
    git_dir = Path(git_dir)
    if not OID.fullmatch(commit_oid) or not required_ref.startswith("refs/"):
        raise AuthorityError("integrity")
    if _git(git_dir, "rev-parse", required_ref) != commit_oid:
        raise AuthorityError("integrity")
    records = _git(
        git_dir, "ls-tree", "-rz", "-r", "--full-tree", commit_oid, binary=True
    ).split(b"\0")[:-1]
    if len(records) > limits["max_entries"]:
        raise AuthorityError("integrity")
    findings = _matches(
        _git(git_dir, "cat-file", "commit", commit_oid, binary=True), patterns
    )
    findings += _matches(required_ref.encode("utf-8"), patterns)
    examined = 1
    for record in records:
        metadata, path = record.split(b"\t", 1)
        findings += _matches(path, patterns)
        oid = metadata.split()[2].decode("ascii")
        blob = _git(git_dir, "cat-file", "blob", oid, binary=True)
        if len(blob) > limits["max_blob_bytes"]:
            raise AuthorityError("integrity")
        findings += _matches(blob, patterns)
        examined += 1
        if findings > limits["max_findings"]:
            raise AuthorityError("integrity")
    return {"coverage": "complete", "findings": findings, "objects_examined": examined}


def audit_history(remote_url, mirror_dir, patterns, limits):
    if (
        not remote_url.startswith("https://")
        or "@" in remote_url.split("//", 1)[1].split("/", 1)[0]
    ):
        raise AuthorityError("integrity")
    environment = {
        "PATH": os.environ.get("PATH", ""),
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_NOSYSTEM": "1",
    }
    try:
        before = subprocess.run(
            ["git", "ls-remote", remote_url],
            capture_output=True,
            check=True,
            env=environment,
        ).stdout
        subprocess.run(
            ["git", "clone", "--mirror", "--no-local", remote_url, str(mirror_dir)],
            capture_output=True,
            check=True,
            env=environment,
        )
        after = subprocess.run(
            ["git", "ls-remote", remote_url],
            capture_output=True,
            check=True,
            env=environment,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise AuthorityError("integrity") from exc
    if before != after:
        raise AuthorityError("integrity")
    refs = [line.split(b"\t", 1) for line in before.splitlines()]
    if len(refs) > limits["max_entries"]:
        raise AuthorityError("integrity")
    findings = sum(_matches(ref, patterns) for _oid, ref in refs)
    return {
        "coverage": "git-complete-api-residual",
        "findings": findings,
        "objects_examined": len(refs),
    }
