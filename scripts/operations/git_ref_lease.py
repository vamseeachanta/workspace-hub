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

`GitRefLease` arbitrates local processes. `RemoteGitRefLease` publishes each
grant to origin before returning success, and reads origin for every fence.
Bulk synchronization after execution cannot arbitrate that execution (#3772).

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


class LeaseSyncError(RuntimeError):
    """Remote state could not be established; execution must be refused."""


class RemoteGitRefLease(GitRefLease):
    """Arbitrate against origin, without publishing pending local lease refs.

    Each candidate is a root (creation) or a child of the observed remote tip
    (update). Competing candidates are unrelated roots or siblings; a normal
    branch push rejects the loser. Source: git-push, NOTE ABOUT FAST-FORWARDS,
    https://git-scm.com/docs/git-push#_note_about_fast_forwards
    (Git 2.55.0 manual, accessed 2026-10-22).

    This protocol requires append-only remote lease history: no deletion,
    merging competing grants, or forced updates. A remote read failure raises;
    a rejected publication returns None. Neither grants execution authority.
    """

    def __init__(self, repo: str | Path):
        super().__init__(repo)
        self.fetch_rc = 0
        self.push_rc = 0

    def read_ref(self, ref: str):
        result = self._git("ls-remote", "--exit-code", "--refs", "origin", ref,
                           check=False)
        # git-ls-remote --exit-code: 2 means no matching refs; other failures
        # are not absence. Source: https://git-scm.com/docs/git-ls-remote (2026),
        # Git 2.48.0 manual, OPTIONS, --exit-code. Preserve failures in the summary.
        if result.returncode == 2:
            return None
        if result.returncode != 0:
            self.fetch_rc = result.returncode
            raise LeaseSyncError(f"lease remote read failed (exit {result.returncode})")
        # One exact ref, with SHA and refname: git-ls-remote OUTPUT (same source).
        matches = [line.split() for line in result.stdout.splitlines()]
        if len(matches) != 1 or len(matches[0]) != 2 or matches[0][1] != ref:
            raise LeaseSyncError("lease remote read returned an unexpected ref")
        sha = matches[0][0]
        # Fetch objects without advancing a local lease ref or FETCH_HEAD.
        # Read the advertised SHA, even if a newer descendant is fetched.
        result = self._git("fetch", "--no-tags", "--no-write-fetch-head", "origin", ref,
                           check=False)
        if result.returncode != 0:
            self.fetch_rc = result.returncode
            raise LeaseSyncError(f"lease object fetch failed (exit {result.returncode})")
        result = self._git("show", "-s", "--format=%B", sha, check=False)
        if result.returncode != 0:
            raise LeaseSyncError("advertised lease object is unavailable")
        return sha, json.loads(result.stdout)

    def _publish(self, ref: str, blob_dict: dict, parent: str | None = None):
        candidate = self._write_lease_commit(blob_dict, parent=parent)
        result = self._git("push", "--no-follow-tags", "origin", f"{candidate}:{ref}",
                           check=False)
        if result.returncode != 0:
            self.push_rc = result.returncode
            return None
        return candidate

    def create_ref(self, ref: str, blob_dict: dict):
        return self._publish(ref, blob_dict)

    def cas_update_ref(self, ref: str, expected_sha: str, blob_dict: dict):
        return self._publish(ref, blob_dict, parent=expected_sha)
