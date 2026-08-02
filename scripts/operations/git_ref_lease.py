#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""git_ref_lease.py — real-git adapter for the dispatch lease (#2970, F3).

Provides the injected git interface that `dispatch_lease.py` expects
(`read_ref` / `create_ref` / `cas_update_ref`) backed by actual git refs, so the
versioned-CAS + fencing lease runs against a real repository.

Atomic primitive: `git update-ref <ref> <new> <old>` — git performs this as an
atomic compare-and-swap (it fails iff the ref's current value != <old>). Creation
uses the empty old-value (`''`) which git treats as "must not already exist". The
lease JSON is stored as the MESSAGE of a commit over the empty tree, and the ref
points at that commit — because `refs/heads/*` must point to commits (git rejects a
bare blob there) and GitHub only accepts pushes to `refs/heads/*`.

LOCAL refs arbitrate processes on one host. CROSS-MACHINE arbitration is the same
refs moved by `dispatch_pull._fetch_lease_refs` / `_push_lease_refs`; a lease that
never leaves the host arbitrates nothing, because every host then CASes against
refs only it can see and wins every claim (#3772).

The lease NAMESPACE is owned by `dispatch_lease.REF_PREFIX` and imported here
rather than restated. It used to be a second string literal that happened to
agree — and a third, in the pull loop's refspecs, that did not.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


#: Single source of truth for the lease namespace (scripts/ is not a package, so
#: the sibling core is loaded by path — same shape as dispatch_pull does it).
_dl = _load("dispatch_lease", _HERE / "dispatch_lease.py")
REF_PREFIX = _dl.REF_PREFIX


def lease_ref(name: str) -> str:
    return _dl.lease_ref(name)


class GitRefLease:
    def __init__(self, repo: str | Path):
        self.repo = str(repo)

    def _git(self, *args: str, input_text: str | None = None, check: bool = True):
        return subprocess.run(["git", "-C", self.repo, *args],
                              input=input_text, capture_output=True, text=True,
                              check=check)

    # ── injected interface expected by dispatch_lease ────────────────────────
    # NOTE: dispatch_lease owns the lease namespace and passes the FULL ref string
    # (it calls its own lease_ref()). This adapter treats the argument as the exact
    # ref and never re-namespaces it (double-prefix bug otherwise).
    def read_ref(self, ref: str):
        r = self._git("rev-parse", "--verify", "--quiet", ref, check=False)
        sha = r.stdout.strip()
        if r.returncode != 0 or not sha:
            return None
        msg = self._git("show", "-s", "--format=%B", sha).stdout
        return (sha, json.loads(msg))

    def _write_lease_commit(self, blob_dict: dict, parent: str | None = None) -> str:
        # JSON-in-commit-message over the empty tree → a commit object that a
        # refs/heads/* ref can point at (and that GitHub will accept on push).
        # Parenting each update on the PRIOR lease commit guarantees a UNIQUE sha
        # every CAS (the parent always differs), so the ref strictly advances even
        # for identical content in the same second (#2970 code-review MINOR #1 —
        # commit-tree is deterministic per tree+msg+ident+timestamp otherwise).
        empty_tree = self._git("hash-object", "-t", "tree", "-w", "/dev/null").stdout.strip()
        text = json.dumps(blob_dict, sort_keys=True)
        args = ["commit-tree", empty_tree, "-m", text]
        if parent:
            args += ["-p", parent]
        return self._git(*args).stdout.strip()

    def create_ref(self, ref: str, blob_dict: dict):
        csha = self._write_lease_commit(blob_dict)
        # empty old-value ⇒ git fails if the ref already exists (creation arbiter)
        r = self._git("update-ref", ref, csha, "", check=False)
        return csha if r.returncode == 0 else None

    def cas_update_ref(self, ref: str, expected_sha: str, blob_dict: dict):
        # parent on expected_sha → the new commit can never collide with the old
        csha = self._write_lease_commit(blob_dict, parent=expected_sha)
        # update-ref with an explicit old-value is an atomic compare-and-swap
        r = self._git("update-ref", ref, csha, expected_sha, check=False)
        return csha if r.returncode == 0 else None
