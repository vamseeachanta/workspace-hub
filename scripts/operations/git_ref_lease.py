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

LOCAL refs (default) arbitrate processes on one host. For CROSS-MACHINE arbitration
the same semantics map to `git push --force-with-lease=<ref>:<old-sha>` (CAS) and a
non-forced push (create); the remote binding is wired at the operator-cutover step.
This module is the local/single-repo adapter, fully testable with real git.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def lease_ref(name: str) -> str:
    return f"refs/heads/dispatch/leases/{name}"


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

    def _write_lease_commit(self, blob_dict: dict) -> str:
        # JSON-in-commit-message over the empty tree → a commit object that a
        # refs/heads/* ref can point at (and that GitHub will accept on push).
        empty_tree = self._git("hash-object", "-t", "tree", "-w", "/dev/null").stdout.strip()
        text = json.dumps(blob_dict, sort_keys=True)
        return self._git("commit-tree", empty_tree, "-m", text).stdout.strip()

    def create_ref(self, ref: str, blob_dict: dict):
        csha = self._write_lease_commit(blob_dict)
        # empty old-value ⇒ git fails if the ref already exists (creation arbiter)
        r = self._git("update-ref", ref, csha, "", check=False)
        return csha if r.returncode == 0 else None

    def cas_update_ref(self, ref: str, expected_sha: str, blob_dict: dict):
        csha = self._write_lease_commit(blob_dict)
        # update-ref with an explicit old-value is an atomic compare-and-swap
        r = self._git("update-ref", ref, csha, expected_sha, check=False)
        return csha if r.returncode == 0 else None
